from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import (
    AuditEvent,
    Conversation,
    Escalation,
    Lead,
    Message,
    TelegramUpdateDedup,
    User,
)
from app.services.consultant import (
    NEUTRAL_HANDOFF_TEXT,
    SERVICE_UNAVAILABLE_FALLBACK_TEXT,
    ConsultantDecision,
    build_calculator_hint,
    detect_non_standard_scope,
    detect_non_text,
    is_below_budget_threshold,
    is_manager_request,
    make_escalation,
)
from app.services.dialog_engine import build_summary, next_missing_field, normalize_field_value
from app.services.perplexity_client import (
    ConsultantResult,
    PerplexityClient,
    build_consultant_system_prompt,
)
from app.settings import settings
from app.telegram_client import send_message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["telegram"])


def get_consultant_client() -> PerplexityClient:
    """Фабрика клиента консультанта (легко переопределяется в тестах)."""

    return PerplexityClient()


def _get_or_create_conversation(db: Session, chat_id: int) -> Conversation:
    conv = db.query(Conversation).filter(Conversation.chat_id == chat_id).one_or_none()
    if conv:
        return conv
    conv = Conversation(chat_id=chat_id, data={})
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def _get_user_by_telegram_id(db: Session, telegram_user_id: int) -> User | None:
    return db.query(User).filter(User.telegram_user_id == telegram_user_id).one_or_none()


def _is_manager(user: User | None) -> bool:
    return bool(user and user.role and user.role.code == "manager")


def _build_dedup_key(update: dict, message: dict | None) -> tuple[str | None, dict]:
    update_id = update.get("update_id")
    if update_id is not None:
        try:
            update_id_int = int(update_id)
        except (TypeError, ValueError):
            update_id_int = None
        if update_id_int is not None:
            meta: dict = {"update_id": update_id_int}
            if message:
                try:
                    meta["chat_id"] = int(message["chat"]["id"])
                except (KeyError, TypeError, ValueError):
                    pass
                msg_id = message.get("message_id")
                try:
                    if msg_id is not None:
                        meta["message_id"] = int(msg_id)
                except (TypeError, ValueError):
                    pass
            return f"telegram:update_id:{update_id_int}", meta

    if message:
        try:
            chat_id = int(message["chat"]["id"])
        except (KeyError, TypeError, ValueError):
            chat_id = None
        msg_id = message.get("message_id")
        try:
            msg_id_int = int(msg_id) if msg_id is not None else None
        except (TypeError, ValueError):
            msg_id_int = None
        if chat_id is not None and msg_id_int is not None:
            return f"telegram:message:{chat_id}:{msg_id_int}", {
                "chat_id": chat_id,
                "message_id": msg_id_int,
            }

    return None, {}


def _try_register_dedup(db: Session, key: str, meta: dict) -> bool:
    row = TelegramUpdateDedup(
        key=key,
        update_id=meta.get("update_id"),
        chat_id=meta.get("chat_id"),
        message_id=meta.get("message_id"),
    )
    db.add(row)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return False
    return True


def _record_outgoing(db: Session, conv_id, chat_id: int, text: str) -> None:
    db.add(
        Message(
            conversation_id=conv_id,
            direction="out",
            text=text,
            raw={"chat_id": chat_id},
        )
    )


def _audit(db: Session, *, event_type: str, conv_id=None, payload: dict | None = None) -> None:
    db.add(
        AuditEvent(
            event_type=event_type,
            conversation_id=conv_id,
            payload=payload or {},
        )
    )


def _recent_history(db: Session, conv_id, limit: int) -> list[dict[str, str]]:
    """Последние сообщения диалога в формате для модели (user/assistant)."""

    rows = (
        db.query(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
    history: list[dict[str, str]] = []
    for row in reversed(rows):
        role = "user" if row.direction == "in" else "assistant"
        text = (row.text or "").strip()
        if not text:
            continue
        history.append({"role": role, "content": text})
    return history


def _do_escalate(
    db: Session,
    *,
    conv: Conversation,
    chat_id: int,
    reason: str,
    text: str,
    manager_note: str = "",
    extra_payload: dict | None = None,
) -> None:
    details = {"text": text}
    if manager_note:
        details["manager_note"] = manager_note
    if extra_payload:
        details.update(extra_payload)

    db.add(
        Escalation(
            conversation_id=conv.id,
            reason_code=reason,
            details=details,
        )
    )
    _audit(
        db,
        event_type="escalation.created",
        conv_id=conv.id,
        payload={"reason_code": reason},
    )
    _record_outgoing(db, conv.id, chat_id, text)
    db.commit()

    send_message(chat_id, text)
    recent_msgs = extra_payload.get("recent_messages") if extra_payload else None
    _notify_manager(chat_id, conv, reason=reason, note=manager_note, recent_messages=recent_msgs)


def _do_respond(
    db: Session,
    *,
    conv: Conversation,
    chat_id: int,
    text: str,
) -> None:
    _record_outgoing(db, conv.id, chat_id, text)
    _audit(
        db,
        event_type="consultant.respond",
        conv_id=conv.id,
        payload={"chat_id": chat_id, "length": len(text)},
    )
    db.commit()
    send_message(chat_id, text)


def _rule_based_decision(
    *,
    collected: dict,
    text: str,
) -> ConsultantDecision | None:
    """Жёсткие правила, имеющие приоритет над сигналом модели."""

    if is_manager_request(text):
        return make_escalation("manager_requested", manager_note=text[:512])

    is_non_std, code = detect_non_standard_scope(collected, text)
    if is_non_std and code:
        return make_escalation(code, manager_note=text[:512])

    return None


async def _ask_consultant(
    client: PerplexityClient,
    *,
    system_prompt: str,
    history: list[dict[str, str]],
    user_text: str,
) -> ConsultantResult:
    return await client.generate(
        system_prompt=system_prompt,
        history=history,
        user_text=user_text,
    )


@router.post("/webhook")
def telegram_webhook(
    update: dict,
    db: Session = Depends(get_db),
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
    consultant_client: PerplexityClient = Depends(get_consultant_client),
):
    if settings.telegram_webhook_secret_token:
        if (
            not x_telegram_bot_api_secret_token
            or x_telegram_bot_api_secret_token != settings.telegram_webhook_secret_token
        ):
            raise HTTPException(status_code=401, detail="Unauthorized")

    message = update.get("message") or update.get("edited_message")
    key, meta = _build_dedup_key(update, message)

    db.add(AuditEvent(event_type="telegram.update", payload=update))
    db.commit()

    if key:
        registered = _try_register_dedup(db, key=key, meta=meta)
        if not registered:
            chat_id = meta.get("chat_id")
            conv_id = None
            if chat_id is not None:
                conv = (
                    db.query(Conversation)
                    .filter(Conversation.chat_id == int(chat_id))
                    .one_or_none()
                )
                conv_id = conv.id if conv else None
            db.add(
                AuditEvent(
                    event_type="telegram.duplicate_ignored",
                    conversation_id=conv_id,
                    payload={"key": key, **meta},
                )
            )
            db.commit()
            return {"ok": True}
        db.commit()

    if not message:
        return {"ok": True}

    chat_id = int(message["chat"]["id"])
    sender_id = int(message["from"]["id"])
    text = (message.get("text") or "").strip()

    sender_user = _get_user_by_telegram_id(db, telegram_user_id=sender_id)
    conv = _get_or_create_conversation(db, chat_id=chat_id)
    if not conv.customer_telegram_user_id and not _is_manager(sender_user):
        conv.customer_telegram_user_id = sender_id
        db.commit()

    db.add(
        Message(
            conversation_id=conv.id,
            direction="in",
            telegram_message_id=message.get("message_id"),
            sender_telegram_user_id=sender_id,
            text=text or None,
            raw=message,
        )
    )
    db.commit()

    # Правило takeover: если менеджер написал в чат — бот отключается до /resume_bot
    if _is_manager(sender_user):
        if text == "/resume_bot":
            conv.bot_paused = False
            db.add(
                AuditEvent(
                    event_type="bot.resume",
                    actor_user_id=sender_user.id,
                    conversation_id=conv.id,
                    payload={"chat_id": chat_id},
                )
            )
            db.commit()
            send_message(chat_id, "Бот снова активен.")
            return {"ok": True}
        conv.bot_paused = True
        db.add(
            AuditEvent(
                event_type="bot.pause",
                actor_user_id=sender_user.id,
                conversation_id=conv.id,
                payload={"chat_id": chat_id},
            )
        )
        db.commit()
        return {"ok": True}

    if conv.bot_paused:
        return {"ok": True}

    # Не-текстовые сообщения от клиента — сразу эскалация.
    if detect_non_text(message):
        _do_escalate(
            db,
            conv=conv,
            chat_id=chat_id,
            reason="non_text_message",
            text=NEUTRAL_HANDOFF_TEXT,
            manager_note="Клиент прислал нетекстовое сообщение.",
            extra_payload={"raw_keys": [k for k in message.keys() if k not in {"chat", "from"}]},
        )
        return {"ok": True}

    # После квалификации любые уточнения отдаём менеджеру.
    if conv.state == "qualified":
        _do_escalate(
            db,
            conv=conv,
            chat_id=chat_id,
            reason="post_qualification_message",
            text=NEUTRAL_HANDOFF_TEXT,
            manager_note=text[:512],
            extra_payload={"text": text},
        )
        return {"ok": True}

    # Команды клиента
    if text in {"/start", "/reset"}:
        conv.state = "collecting"
        conv.data = {"collected": {}}
        db.commit()
        greeting = (
            "Здравствуйте. Я консультант компании Автоподбор - Exception.Expert. "
            "Помогу подобрать автомобиль под ваши задачи и подготовить расчёт под ключ. "
            "Начнём с пары вопросов."
        )
        _do_respond(db, conv=conv, chat_id=chat_id, text=greeting)
        field = next_missing_field(conv.data.get("collected", {}))
        if field:
            _do_respond(db, conv=conv, chat_id=chat_id, text=field.question)
        return {"ok": True}

    collected = (conv.data or {}).get("collected") or {}
    pending = next_missing_field(collected)
    if pending:
        collected[pending.key] = normalize_field_value(pending.key, text)
        conv.data = {"collected": collected}
        db.commit()

    # Жёсткое правило: бюджет ниже порога — эскалация.
    if is_below_budget_threshold(collected):
        budget = collected.get("budget_rub")
        db.add(
            Lead(
                conversation_id=conv.id,
                chat_id=chat_id,
                customer_telegram_user_id=conv.customer_telegram_user_id,
                status="budget_low",
                payload={"collected": collected},
            )
        )
        _do_escalate(
            db,
            conv=conv,
            chat_id=chat_id,
            reason="budget_below_threshold",
            text=(
                "По бюджету ниже 1 500 000 ₽ самостоятельный подбор в нашем целевом контуре "
                "может быть недоступен. " + NEUTRAL_HANDOFF_TEXT
            ),
            manager_note=f"budget_rub={budget}",
            extra_payload={"budget_rub": budget},
        )
        return {"ok": True}

    rule_decision = _rule_based_decision(collected=collected, text=text)
    if rule_decision is not None and rule_decision.action == "escalate":
        _do_escalate(
            db,
            conv=conv,
            chat_id=chat_id,
            reason=rule_decision.reason,
            text=rule_decision.text,
            manager_note=rule_decision.manager_note,
            extra_payload={"text": text},
        )
        return {"ok": True}

    # Все параметры собраны → фиксируем лид и предлагаем следующий шаг.
    pending = next_missing_field(collected)
    if not pending:
        conv.state = "qualified"
        db.add(
            Lead(
                conversation_id=conv.id,
                chat_id=chat_id,
                customer_telegram_user_id=conv.customer_telegram_user_id,
                status="qualified",
                payload={"collected": collected},
            )
        )
        _audit(
            db,
            event_type="lead.qualified",
            conv_id=conv.id,
            payload={"chat_id": chat_id, "collected": collected},
        )
        ack = (
            "Спасибо. Параметры зафиксированы. Передаю менеджеру для подбора и расчёта."
        )
        _do_respond(db, conv=conv, chat_id=chat_id, text=ack)
        _notify_manager(chat_id, conv, collected_override=collected)
        return {"ok": True}

    # Сбор параметров идёт — формируем естественный ответ через внешний сервис.
    pending_question = pending.question if pending else None
    calc_hint = build_calculator_hint(collected)
    system_prompt = build_consultant_system_prompt(
        collected=collected,
        pending_field_question=pending_question,
        calc_hint=calc_hint,
    )

    if not consultant_client.is_configured:
        # Конфигурация внешнего сервиса не задана — используем rule-based вопрос,
        # чтобы не блокировать сбор параметров в локальной разработке.
        _do_respond(db, conv=conv, chat_id=chat_id, text=pending.question)
        return {"ok": True}

    history = _recent_history(db, conv.id, limit=settings.consultant_history_limit)
    # Последнее входящее уже сохранили — это и есть user_text.
    history = [h for h in history if not (h["role"] == "user" and h["content"] == text)]

    try:
        result = asyncio.run(
            _ask_consultant(
                consultant_client,
                system_prompt=system_prompt,
                history=history,
                user_text=text,
            )
        )
    except RuntimeError:
        # На случай вложенного event loop (вряд ли в Sync FastAPI route, но безопасно).
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                _ask_consultant(
                    consultant_client,
                    system_prompt=system_prompt,
                    history=history,
                    user_text=text,
                )
            )
        finally:
            loop.close()

    model_error_reasons = {
        "timeout",
        "unknown_error",
        "malformed_response",
        "invalid_json",
        "invalid_action",
    }
    is_model_problem = (
        result.action == "error"
        or (result.action == "escalate" and result.reason in model_error_reasons)
    )

    if is_model_problem:
        # Усиленная обработка проблем модели (B.2)
        logger.warning("Проблема с генерацией ответа консультанта: reason=%s", result.reason)

        recent_messages = _recent_history(db, conv.id, limit=8)
        _audit(
            db,
            event_type="consultant.api_error",
            conv_id=conv.id,
            payload={"reason": result.reason, "messages_count": len(recent_messages)},
        )
        _do_escalate(
            db,
            conv=conv,
            chat_id=chat_id,
            reason="low_confidence",
            text=SERVICE_UNAVAILABLE_FALLBACK_TEXT,
            manager_note=f"consultant_api_error: {result.reason}",
            extra_payload={
                "text": text,
                "api_reason": result.reason,
                "recent_messages": recent_messages,
                "collected": (conv.data or {}).get("collected", {}),
            },
        )
        return {"ok": True}

    if result.action == "escalate":
        reason = result.reason or "low_confidence"
        client_text = result.text.strip() or NEUTRAL_HANDOFF_TEXT
        _do_escalate(
            db,
            conv=conv,
            chat_id=chat_id,
            reason=reason,
            text=client_text,
            manager_note=result.manager_note or text[:512],
            extra_payload={"text": text, "citations": result.citations},
        )
        return {"ok": True}

    # action == "respond"
    answer = result.text.strip()
    if not answer:
        _do_escalate(
            db,
            conv=conv,
            chat_id=chat_id,
            reason="low_confidence",
            text=NEUTRAL_HANDOFF_TEXT,
            manager_note="empty answer from consultant service",
            extra_payload={"text": text},
        )
        return {"ok": True}

    _do_respond(db, conv=conv, chat_id=chat_id, text=answer)
    return {"ok": True}


def _notify_manager(
    chat_id: int,
    conv: Conversation,
    *,
    reason: str | None = None,
    note: str = "",
    collected_override: dict | None = None,
    recent_messages: list[dict[str, str]] | None = None,
) -> None:
    if not settings.telegram_manager_chat_id:
        return
    collected = collected_override
    if collected is None:
        collected = (conv.data or {}).get("collected") or {}
    summary = build_summary(collected) if collected else "(параметры не собраны)"
    header = f"Новый запрос (чат {chat_id})"
    if reason:
        header += f", причина: {reason}"
    body = header + ":\n" + summary

    if recent_messages:
        body += "\n\nПоследние сообщения:\n"
        for msg in recent_messages[-4:]:  # последние 4 для компактности
            role = "Клиент" if msg.get("role") == "user" else "Бот"
            body += f"- {role}: {msg.get('content', '')[:200]}\n"

    if note:
        body += f"\n---\n{note}"
    send_message(int(settings.telegram_manager_chat_id), body)
