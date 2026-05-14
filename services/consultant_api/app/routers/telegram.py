from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import AuditEvent, Conversation, Escalation, Lead, Message, User
from app.services.dialog_engine import build_summary, next_missing_field, normalize_field_value
from app.settings import settings
from app.telegram_client import send_message

router = APIRouter(prefix="/telegram", tags=["telegram"])


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


@router.post("/webhook")
def telegram_webhook(
    update: dict,
    db: Session = Depends(get_db),
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if settings.telegram_webhook_secret_token:
        if (
            not x_telegram_bot_api_secret_token
            or x_telegram_bot_api_secret_token != settings.telegram_webhook_secret_token
        ):
            raise HTTPException(status_code=401, detail="Unauthorized")

    db.add(AuditEvent(event_type="telegram.update", payload=update))
    db.commit()

    message = update.get("message") or update.get("edited_message")
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
            text=text,
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

    # После квалификации любые уточнения отдаём менеджеру (правило качества)
    if conv.state == "qualified":
        db.add(
            Escalation(
                conversation_id=conv.id,
                reason_code="post_qualification_message",
                details={"text": text},
            )
        )
        db.add(
            AuditEvent(
                event_type="escalation.created",
                conversation_id=conv.id,
                payload={"reason_code": "post_qualification_message"},
            )
        )
        db.commit()
        send_message(chat_id, "Передаю уточнение менеджеру.")
        _notify_manager(chat_id, {"message": text})
        return {"ok": True}

    # Команды клиента
    if text in {"/start", "/reset"}:
        conv.state = "collecting"
        conv.data = {"collected": {}}
        db.commit()
        send_message(chat_id, "Здравствуйте! Начнем с пары вопросов для подбора.")
        field = next_missing_field(conv.data.get("collected", {}))
        if field:
            send_message(chat_id, field.question)
        return {"ok": True}

    collected = (conv.data or {}).get("collected") or {}
    pending = next_missing_field(collected)
    if pending:
        collected[pending.key] = normalize_field_value(pending.key, text)
        conv.data = {"collected": collected}
        db.commit()

    pending = next_missing_field(collected)
    if pending:
        # Бюджетный порог: если уже есть budget_rub < 1_500_000,
        # то не обещаем подбор в целевом контуре.
        budget = collected.get("budget_rub")
        if isinstance(budget, int) and budget < 1_500_000:
            db.add(
                Escalation(
                    conversation_id=conv.id,
                    reason_code="budget_below_threshold",
                    details={"budget_rub": budget},
                )
            )
            db.add(
                AuditEvent(
                    event_type="escalation.created",
                    conversation_id=conv.id,
                    payload={"reason_code": "budget_below_threshold", "budget_rub": budget},
                )
            )
            db.add(
                Lead(
                    conversation_id=conv.id,
                    chat_id=chat_id,
                    customer_telegram_user_id=conv.customer_telegram_user_id,
                    status="budget_low",
                    payload={"collected": collected},
                )
            )
            db.commit()
            send_message(
                chat_id,
                (
                    "Бюджет ниже 1 500 000 ₽. В целевом контуре подбор может быть недоступен — "
                    "передаю запрос менеджеру для уточнения вариантов."
                ),
            )
            _notify_manager(chat_id, collected)
            return {"ok": True}
        send_message(chat_id, pending.question)
        return {"ok": True}

    # Все параметры собраны → фиксируем лид и предлагаем следующий шаг
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
    db.add(
        AuditEvent(
            event_type="lead.qualified",
            conversation_id=conv.id,
            payload={"chat_id": chat_id, "collected": collected},
        )
    )
    db.commit()

    send_message(
        chat_id,
        "Спасибо. Параметры зафиксированы. Передаю менеджеру для подбора и расчета.",
    )
    _notify_manager(chat_id, collected)
    return {"ok": True}


def _notify_manager(chat_id: int, collected: dict) -> None:
    if not settings.telegram_manager_chat_id:
        return
    summary = build_summary(collected)
    send_message(
        int(settings.telegram_manager_chat_id),
        f"Новый запрос (чат {chat_id}):\n{summary}",
    )
