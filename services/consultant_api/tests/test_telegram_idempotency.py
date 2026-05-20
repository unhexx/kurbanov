from __future__ import annotations

from fastapi.testclient import TestClient

from app.db import SessionLocal, engine
from app.main import create_app
from app.models import AuditEvent, Base, Conversation, Escalation, Lead, Message
from app.settings import settings


def _reset_db() -> None:
    engine.dispose()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _client() -> TestClient:
    settings.telegram_bot_token = ""
    settings.telegram_manager_chat_id = ""
    return TestClient(create_app())


def test_webhook_idempotency_by_update_id():
    _reset_db()
    client = _client()

    update = {
        "update_id": 100,
        "message": {
            "message_id": 1,
            "from": {"id": 111},
            "chat": {"id": 777},
            "text": "Toyota Camry",
        },
    }

    r1 = client.post("/telegram/webhook", json=update)
    assert r1.status_code == 200
    assert r1.json() == {"ok": True}

    r2 = client.post("/telegram/webhook", json=update)
    assert r2.status_code == 200
    assert r2.json() == {"ok": True}

    db = SessionLocal()
    try:
        assert db.query(Message).count() == 1
        assert db.query(Lead).count() == 0
        assert db.query(Escalation).count() == 0
        assert db.query(AuditEvent).filter(AuditEvent.event_type == "telegram.duplicate_ignored").count() == 1
    finally:
        db.close()


def test_webhook_idempotency_after_qualified_no_duplicate_escalation():
    _reset_db()
    client = _client()

    db = SessionLocal()
    try:
        conv = Conversation(chat_id=888, customer_telegram_user_id=222, state="qualified", data={"collected": {}})
        db.add(conv)
        db.commit()
    finally:
        db.close()

    update = {
        "update_id": 200,
        "message": {
            "message_id": 2,
            "from": {"id": 222},
            "chat": {"id": 888},
            "text": "уточнение после квалификации",
        },
    }

    r1 = client.post("/telegram/webhook", json=update)
    assert r1.status_code == 200

    r2 = client.post("/telegram/webhook", json=update)
    assert r2.status_code == 200

    db = SessionLocal()
    try:
        assert db.query(Escalation).filter(Escalation.reason_code == "post_qualification_message").count() == 1
        assert db.query(AuditEvent).filter(AuditEvent.event_type == "telegram.duplicate_ignored").count() == 1
    finally:
        db.close()


def test_webhook_idempotency_low_budget_no_duplicate_lead_escalation():
    _reset_db()
    client = _client()

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
            chat_id=999,
            customer_telegram_user_id=333,
            state="collecting",
            data={"collected": collected},
        )
        db.add(conv)
        db.commit()
    finally:
        db.close()

    update = {
        "update_id": 300,
        "message": {
            "message_id": 3,
            "from": {"id": 333},
            "chat": {"id": 999},
            "text": "1000000",
        },
    }

    r1 = client.post("/telegram/webhook", json=update)
    assert r1.status_code == 200

    r2 = client.post("/telegram/webhook", json=update)
    assert r2.status_code == 200

    db = SessionLocal()
    try:
        assert db.query(Escalation).filter(Escalation.reason_code == "budget_below_threshold").count() == 1
        assert db.query(Lead).filter(Lead.status == "budget_low").count() == 1
        assert db.query(AuditEvent).filter(AuditEvent.event_type == "telegram.duplicate_ignored").count() == 1
    finally:
        db.close()


def test_webhook_secret_token_still_enforced_when_enabled():
    _reset_db()
    client = _client()

    settings.telegram_webhook_secret_token = "secret"
    try:
        update = {
            "update_id": 400,
            "message": {
                "message_id": 4,
                "from": {"id": 444},
                "chat": {"id": 4444},
                "text": "/start",
            },
        }

        r1 = client.post("/telegram/webhook", json=update)
        assert r1.status_code == 401

        r2 = client.post(
            "/telegram/webhook",
            json=update,
            headers={"X-Telegram-Bot-Api-Secret-Token": "secret"},
        )
        assert r2.status_code == 200
        assert r2.json() == {"ok": True}
    finally:
        settings.telegram_webhook_secret_token = ""

