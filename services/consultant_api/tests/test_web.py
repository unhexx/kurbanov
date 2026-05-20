import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def client(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("ADMIN_API_TOKEN", "")

    import importlib

    import app.settings as settings_module

    importlib.reload(settings_module)
    import app.db as db_module

    importlib.reload(db_module)

    import app.models as models_module
    import app.main as main_module
    import app.web.router as web_router

    importlib.reload(models_module)
    importlib.reload(web_router)
    importlib.reload(main_module)

    models_module.Base.metadata.create_all(bind=db_module.engine)

    # Точечное наполнение базовых данных
    SessionLocal = sessionmaker(bind=db_module.engine)
    db = SessionLocal()
    try:
        db.add(models_module.Role(code="manager", title="Менеджер"))
        db.add(
            models_module.KnowledgeBaseSource(
                code="KB-SRC-01", title="Источник", moderation_status="approved"
            )
        )
        db.commit()
    finally:
        db.close()

    return TestClient(main_module.app)


def test_public_index_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Подберём автомобиль" in resp.text


def test_public_calculator_get(client):
    resp = client.get("/calculator")
    assert resp.status_code == 200
    assert "Калькулятор итоговой стоимости" in resp.text


def test_public_calculator_post_ok(client):
    resp = client.post(
        "/calculator",
        data={
            "country": "РФ",
            "age_years": "4",
            "power_hp": "150",
            "car_price_rub": "1000000",
            "extra_costs_rub": "0",
            "export_cost_rub": "10000",
            "commission_rub": "50000",
            "broker_rub": "85000",
            "customs_rub": "300000",
            "logistics_rub": "200000",
        },
    )
    assert resp.status_code == 200
    assert "Итого" in resp.text
    # 1 645 000,00 рублей
    assert "1 645 000,00" in resp.text


def test_public_calculator_validation_error(client):
    resp = client.post(
        "/calculator",
        data={
            "country": "КЗ",
            "age_years": "4",
            "power_hp": "150",
            "car_price_rub": "1000000",
        },
    )
    assert resp.status_code == 200
    assert "Контур v1" in resp.text


def test_public_intake_submit_creates_lead(client):
    resp = client.post(
        "/intake",
        data={
            "brand_model": "Toyota Camry",
            "age_years": "4",
            "body_type": "седан",
            "drive": "передний",
            "engine_volume": "2.5",
            "fuel": "бензин",
            "transmission": "автомат",
            "mileage": "60000",
            "color": "белый",
            "budget_rub": "3000000",
            "power_hp": "180",
            "options": "CarPlay",
            "alternatives": "Honda Accord",
            "delivery_country": "РФ",
            "contact": "@example",
        },
    )
    assert resp.status_code == 200
    assert "Запрос принят" in resp.text


def test_public_intake_low_budget(client):
    resp = client.post(
        "/intake",
        data={
            "brand_model": "Lada Vesta",
            "age_years": "3",
            "budget_rub": "800000",
            "delivery_country": "РФ",
            "contact": "client@example.com",
        },
    )
    assert resp.status_code == 200
    assert "ниже 1 500 000" in resp.text


def test_public_intake_required_validation(client):
    resp = client.post("/intake", data={})
    assert resp.status_code == 200
    assert "Поле обязательно" in resp.text


def test_admin_dashboard_when_no_token_set(client):
    # При пустом ADMIN_API_TOKEN страница доступна без входа
    resp = client.get("/admin")
    assert resp.status_code == 200
    assert "Сводка" in resp.text


def test_admin_rates_save_and_list(client):
    resp = client.post(
        "/admin/rates",
        data={"code": "BROKER_BASE", "title": "Базовая ставка брокера", "currency": "RUB", "amount": "5000"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "BROKER_BASE" in resp.text


def test_admin_users_save_validation(client):
    resp = client.post(
        "/admin/users",
        data={"telegram_user_id": "999", "role_code": "manager", "username": "manager_one", "is_active": "1"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "999" in resp.text


def test_admin_login_with_token(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "auth.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("ADMIN_API_TOKEN", "secret-token")
    import importlib

    import app.settings as settings_module

    importlib.reload(settings_module)
    import app.db as db_module

    importlib.reload(db_module)

    import app.models as models_module
    import app.main as main_module
    import app.web.router as web_router

    importlib.reload(models_module)
    importlib.reload(web_router)
    importlib.reload(main_module)

    models_module.Base.metadata.create_all(bind=db_module.engine)

    client = TestClient(main_module.app)
    # Доступ к /admin без токена → редирект на /admin/login
    resp = client.get("/admin", follow_redirects=False)
    assert resp.status_code in (302, 303)
    assert resp.headers["location"].endswith("/admin/login")

    # Неверный токен
    bad = client.post("/admin/login", data={"token": "wrong"}, follow_redirects=False)
    assert bad.status_code in (302, 303)

    # Верный токен — кука выставляется, доступ к /admin открывается
    ok = client.post("/admin/login", data={"token": "secret-token"}, follow_redirects=False)
    assert ok.status_code in (302, 303)
    cookie_header = ok.headers.get("set-cookie", "")
    assert "consultant_admin=secret-token" in cookie_header

    resp = client.get("/admin")
    assert resp.status_code == 200
    assert "Сводка" in resp.text
