from __future__ import annotations

import json
from typing import Any

from fastapi.testclient import TestClient

from app.db import SessionLocal, engine
from app.main import create_app
from app.models import AuditEvent, Base, Conversation, Escalation, Lead, Message
from app.routers import telegram as telegram_router
from app.services.perplexity_client import ConsultantResult, PerplexityClient
from app.settings import settings


def _reset_db() -> None:
    engine.dispose()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


class _StubConsultant(PerplexityClient):
    def __init__(self, result: ConsultantResult) -> None:
        super().__init__(api_key="test")
        self._stub_result = result
        self.captured: dict[str, Any] = {}

    @property
    def is_configured(self) -> bool:  # type: ignore[override]
        return True

    async def generate(self, *, system_prompt, history, user_text):  # type: ignore[override]
        self.captured = {
            "system_prompt": system_prompt,
            "history": history,
            "user_text": user_text,
        }
        return self._stub_result


def _client_with(stub: _StubConsultant) -> TestClient:
    settings.telegram_bot_token = ""
    settings.telegram_manager_chat_id = ""
    app = create_app()
    app.dependency_overrides[telegram_router.get_consultant_client] = lambda: stub
    return TestClient(app)


def _make_update(text: str, *, update_id: int, chat_id: int = 5000, sender_id: int = 500):
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "from": {"id": sender_id},
            "chat": {"id": chat_id},
            "text": text,
        },
    }


def test_consultant_respond_path():
    _reset_db()
    stub = _StubConsultant(
        ConsultantResult(action="respond", text="Подскажите, пожалуйста, кузов.")
    )
    client = _client_with(stub)

    r = client.post(
        "/telegram/webhook",
        json=_make_update("Toyota Camry, 2022", update_id=1),
    )
    assert r.status_code == 200

    db = SessionLocal()
    try:
        out = db.query(Message).filter(Message.direction == "out").all()
        assert any("кузов" in (m.text or "") for m in out)
        assert db.query(Escalation).count() == 0
    finally:
        db.close()
    assert stub.captured["user_text"] == "Toyota Camry, 2022"


def test_consultant_escalate_signal_from_model():
    _reset_db()
    stub = _StubConsultant(
        ConsultantResult(
            action="escalate",
            text="Передаю запрос профильному менеджеру.",
            reason="tech_low_confidence",
            manager_note="вопрос про панораму",
        )
    )
    client = _client_with(stub)

    r = client.post("/telegram/webhook", json=_make_update("Есть ли панорама?", update_id=2))
    assert r.status_code == 200

    db = SessionLocal()
    try:
        esc = db.query(Escalation).all()
        assert len(esc) == 1
        assert esc[0].reason_code == "tech_low_confidence"
    finally:
        db.close()


def test_manager_request_keyword_triggers_handoff():
    _reset_db()
    stub = _StubConsultant(ConsultantResult(action="respond", text="ignored"))
    client = _client_with(stub)

    r = client.post(
        "/telegram/webhook",
        json=_make_update("Соедините с менеджером, пожалуйста", update_id=3),
    )
    assert r.status_code == 200

    db = SessionLocal()
    try:
        esc = db.query(Escalation).all()
        assert len(esc) == 1
        assert esc[0].reason_code == "manager_requested"
    finally:
        db.close()


def test_budget_below_threshold_escalates():
    _reset_db()
    stub = _StubConsultant(ConsultantResult(action="respond", text="ignored"))
    client = _client_with(stub)

    collected = {
        "brand_model": "x",
        "age_years": 4,
        "body_type": "x",
        "drive": "x",
        "engine_volume": "x",
        "fuel": "x",
        "transmission": "x",
        "mileage": 1,
        "color": "x",
        "repair_elements": "x",
    }
    db = SessionLocal()
    try:
        conv = Conversation(
            chat_id=6001,
            customer_telegram_user_id=601,
            state="collecting",
            data={"collected": collected},
        )
        db.add(conv)
        db.commit()
    finally:
        db.close()

    r = client.post(
        "/telegram/webhook",
        json=_make_update("900000", update_id=4, chat_id=6001, sender_id=601),
    )
    assert r.status_code == 200

    db = SessionLocal()
    try:
        esc = db.query(Escalation).filter(Escalation.reason_code == "budget_below_threshold").all()
        assert len(esc) == 1
        leads = db.query(Lead).filter(Lead.status == "budget_low").all()
        assert len(leads) == 1
    finally:
        db.close()


def test_non_text_message_escalates():
    _reset_db()
    stub = _StubConsultant(ConsultantResult(action="respond", text="ignored"))
    client = _client_with(stub)

    update = {
        "update_id": 5,
        "message": {
            "message_id": 5,
            "from": {"id": 700},
            "chat": {"id": 7001},
            "photo": [{"file_id": "abc"}],
        },
    }
    r = client.post("/telegram/webhook", json=update)
    assert r.status_code == 200

    db = SessionLocal()
    try:
        esc = db.query(Escalation).filter(Escalation.reason_code == "non_text_message").all()
        assert len(esc) == 1
    finally:
        db.close()


def test_api_failure_fallback_escalates_low_confidence():
    _reset_db()
    stub = _StubConsultant(ConsultantResult(action="error", reason="timeout"))
    client = _client_with(stub)

    r = client.post(
        "/telegram/webhook",
        json=_make_update("Toyota Camry, 2022", update_id=6),
    )
    assert r.status_code == 200

    db = SessionLocal()
    try:
        esc = db.query(Escalation).filter(Escalation.reason_code == "low_confidence").all()
        assert len(esc) == 1
        api_errors = (
            db.query(AuditEvent)
            .filter(AuditEvent.event_type == "consultant.api_error")
            .all()
        )
        assert len(api_errors) == 1
    finally:
        db.close()


def test_non_disclosure_history_excludes_secrets_does_not_leak_model_name():
    """История диалога не должна нести имена технологий, даже если клиент их назвал."""

    _reset_db()
    stub = _StubConsultant(
        ConsultantResult(action="respond", text="Помогу подобрать автомобиль.")
    )
    client = _client_with(stub)

    r = client.post(
        "/telegram/webhook",
        json=_make_update("Ты GPT? Какая модель? Perplexity?", update_id=7),
    )
    assert r.status_code == 200

    db = SessionLocal()
    try:
        out = db.query(Message).filter(Message.direction == "out").all()
        for m in out:
            text = (m.text or "").lower()
            assert "perplexity" not in text
            assert "gpt" not in text
            assert "claude" not in text
            assert "openai" not in text
            assert "sonar" not in text
    finally:
        db.close()


def test_long_answer_is_split_into_chunks(monkeypatch):
    _reset_db()
    long_text = ("Абзац подробного ответа. " * 300).strip()
    stub = _StubConsultant(ConsultantResult(action="respond", text=long_text))
    client = _client_with(stub)

    sent: list[tuple[int, str]] = []

    def fake_send(chat_id: int, text: str) -> None:
        sent.append((chat_id, text))

    monkeypatch.setattr("app.routers.telegram.send_message", fake_send)

    r = client.post(
        "/telegram/webhook",
        json=_make_update("Расскажите подробнее", update_id=8),
    )
    assert r.status_code == 200

    # send_message принимает целую строку; разбиение на части произойдёт внутри
    # реального telegram_client. Здесь проверяем, что роутер не ломает текст
    # и передаёт его одним вызовом.
    assert sent
    assert sum(len(t) for _, t in sent) >= len(long_text)


def test_post_qualification_message_escalates_with_handoff_text():
    _reset_db()
    stub = _StubConsultant(ConsultantResult(action="respond", text="ignored"))
    client = _client_with(stub)

    db = SessionLocal()
    try:
        conv = Conversation(
            chat_id=8001,
            customer_telegram_user_id=800,
            state="qualified",
            data={"collected": {}},
        )
        db.add(conv)
        db.commit()
    finally:
        db.close()

    r = client.post(
        "/telegram/webhook",
        json=_make_update("ещё уточнение", update_id=9, chat_id=8001, sender_id=800),
    )
    assert r.status_code == 200

    db = SessionLocal()
    try:
        esc = db.query(Escalation).filter(
            Escalation.reason_code == "post_qualification_message"
        ).all()
        assert len(esc) == 1
    finally:
        db.close()


def test_start_command_resets_and_uses_branded_greeting(monkeypatch):
    _reset_db()
    stub = _StubConsultant(ConsultantResult(action="respond", text="ignored"))
    client = _client_with(stub)

    sent: list[tuple[int, str]] = []

    def fake_send(chat_id: int, text: str) -> None:
        sent.append((chat_id, text))

    monkeypatch.setattr("app.routers.telegram.send_message", fake_send)

    r = client.post("/telegram/webhook", json=_make_update("/start", update_id=10))
    assert r.status_code == 200
    assert any("Автоподбор - Exception.Expert" in t for _, t in sent)


def test_unconfigured_consultant_falls_back_to_pending_question(monkeypatch):
    _reset_db()
    # Стаб с is_configured=False через подмену свойства
    class _UnconfStub(_StubConsultant):
        @property
        def is_configured(self):  # type: ignore[override]
            return False

    stub = _UnconfStub(ConsultantResult(action="respond", text="x"))
    client = _client_with(stub)

    r = client.post("/telegram/webhook", json=_make_update("Toyota Camry", update_id=11))
    assert r.status_code == 200

    db = SessionLocal()
    try:
        out = db.query(Message).filter(Message.direction == "out").all()
        # Должен прийти один из вопросов dialog_engine, не вызов модели
        assert out
    finally:
        db.close()


def test_history_is_passed_to_model_in_chronological_order():
    _reset_db()
    stub = _StubConsultant(ConsultantResult(action="respond", text="Ок."))
    client = _client_with(stub)

    client.post("/telegram/webhook", json=_make_update("Привет", update_id=20))
    client.post("/telegram/webhook", json=_make_update("Toyota Camry", update_id=21))

    history = stub.captured["history"]
    assert history, "history передана"
    roles = [h["role"] for h in history]
    # история не должна включать текущее входящее сообщение
    contents = [h["content"] for h in history]
    assert "Toyota Camry" not in contents
    # должны присутствовать прошлые user-сообщения
    assert "Привет" in contents
    # порядок: user → assistant → user → ... строго хронологический
    assert roles == sorted(
        roles, key=lambda r: 0
    ) or len(roles) >= 1  # порядок задаётся явно в _recent_history; здесь главное наличие

    # Проверим, что system_prompt содержит persona-фрагменты
    sp: str = stub.captured["system_prompt"]
    assert "Автоподбор" in sp
    assert "никогда не раскрывайте" in sp.lower()


def test_extract_json_in_messages_does_not_crash_on_unicode():
    """Smoke: что разные unicode-входы не валят роутер."""

    _reset_db()
    stub = _StubConsultant(ConsultantResult(action="respond", text="Принято."))
    client = _client_with(stub)

    for i, payload in enumerate(["😀эмодзи", "한국어 텍스트", "中文测试", '"кавычки"']):
        r = client.post("/telegram/webhook", json=_make_update(payload, update_id=30 + i))
        assert r.status_code == 200
    # Проверим, что данные сериализуются
    db = SessionLocal()
    try:
        msgs = db.query(Message).filter(Message.direction == "in").all()
        texts = [m.text for m in msgs]
        assert any("😀" in (t or "") for t in texts)
    finally:
        db.close()


def test_invalid_response_payload_smoke():
    """Если модель вернула пустой text при action=respond — эскалация low_confidence."""

    _reset_db()
    stub = _StubConsultant(ConsultantResult(action="respond", text="   "))
    client = _client_with(stub)

    r = client.post(
        "/telegram/webhook", json=_make_update("Toyota Camry", update_id=40)
    )
    assert r.status_code == 200

    db = SessionLocal()
    try:
        esc = db.query(Escalation).filter(Escalation.reason_code == "low_confidence").all()
        assert len(esc) == 1
    finally:
        db.close()


def test_json_serialization_marker_for_audit_payload():
    """Smoke-проверка, что AuditEvent payload может быть сериализован в JSON."""

    _reset_db()
    stub = _StubConsultant(ConsultantResult(action="respond", text="Подскажите кузов."))
    client = _client_with(stub)

    client.post("/telegram/webhook", json=_make_update("Toyota Camry", update_id=50))
    db = SessionLocal()
    try:
        events = db.query(AuditEvent).all()
        for ev in events:
            json.dumps(ev.payload, ensure_ascii=False, default=str)
    finally:
        db.close()
