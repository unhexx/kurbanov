from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import quote, unquote

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.status import HTTP_303_SEE_OTHER

from app.db import get_db
from app.models import (
    Conversation,
    Escalation,
    FxRate,
    KnowledgeBaseDoc,
    KnowledgeBaseSource,
    Lead,
    RateItem,
    Role,
    Setting,
    User,
)
from app.services.calculator import (
    CalculatorInput,
    CalculatorScope,
    calculate_total_rub,
    validate_scope,
)
from app.services.fx_rates import fetch_cbr_daily_xml, parse_cbr_daily_xml
from app.settings import settings

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

ADMIN_COOKIE = "consultant_admin"
FLASH_COOKIE = "consultant_flash"


def _format_money(value: Decimal | str | int | float | None) -> str:
    if value is None or value == "":
        return "0,00"
    try:
        d = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return str(value)
    sign = "-" if d < 0 else ""
    d = abs(d)
    whole, frac = divmod(d, Decimal("1"))
    int_part = int(whole)
    int_str = f"{int_part:,}".replace(",", " ")
    cents = (frac * 100).quantize(Decimal("1"))
    return f"{sign}{int_str},{int(cents):02d}"


def _format_dt(value: datetime | None) -> str:
    if not value:
        return ""
    return value.strftime("%Y-%m-%d %H:%M")


templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["formula_version"] = settings.formula_version
templates.env.globals["get_flashes"] = lambda: []  # переопределяется в render()


def _push_flash(response: Response, kind: str, text: str) -> None:
    bag = [{"kind": kind, "text": text}]
    encoded = quote(json.dumps(bag, ensure_ascii=False), safe="")
    response.set_cookie(
        FLASH_COOKIE,
        encoded,
        max_age=20,
        httponly=True,
        samesite="lax",
        path="/",
    )


def _consume_flashes(request: Request) -> list[tuple[str, str]]:
    raw = request.cookies.get(FLASH_COOKIE)
    if not raw:
        return []
    try:
        decoded = unquote(raw)
        data = json.loads(decoded)
        return [(item.get("kind", "info"), item.get("text", "")) for item in data]
    except Exception:
        return []


def _flash_redirect(url: str, kind: str, text: str) -> RedirectResponse:
    resp = RedirectResponse(url=url, status_code=HTTP_303_SEE_OTHER)
    _push_flash(resp, kind, text)
    return resp


def _admin_authed(request: Request) -> bool:
    if not settings.admin_api_token:
        return True
    cookie = request.cookies.get(ADMIN_COOKIE)
    return bool(cookie and cookie == settings.admin_api_token)


def render(request: Request, template: str, context: dict | None = None) -> HTMLResponse:
    ctx = dict(context or {})
    flashes = _consume_flashes(request)

    def _flashes_callable() -> list[tuple[str, str]]:
        return flashes

    env = templates.env
    prev = env.globals.get("get_flashes")
    env.globals["get_flashes"] = _flashes_callable
    try:
        response = templates.TemplateResponse(request, template, ctx)
    finally:
        env.globals["get_flashes"] = prev
    if flashes:
        response.delete_cookie(FLASH_COOKIE, path="/")
    return response


router = APIRouter(include_in_schema=False)


def mount_web(app) -> None:
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="web_static")
    app.include_router(router)


# ----------------------------- Публичная часть -----------------------------


@router.get("/", response_class=HTMLResponse, name="public_index")
def public_index(request: Request):
    return render(request, "public_index.html")


@dataclass
class PublicField:
    key: str
    question: str
    type: str = "text"
    required: bool = False
    options: list[str] | None = None
    hint: str | None = None


PUBLIC_FIELDS: list[PublicField] = [
    PublicField("brand_model", "Какая марка и модель интересуют?", required=True),
    PublicField(
        "age_years",
        "Возраст автомобиля, лет",
        type="number",
        required=True,
        hint="например: 3, 4, 5",
    ),
    PublicField(
        "body_type",
        "Тип кузова",
        type="select",
        options=["седан", "хэтчбек", "лифтбек", "кроссовер", "внедорожник", "универсал", "купе"],
    ),
    PublicField(
        "drive",
        "Привод",
        type="select",
        options=["передний", "задний", "полный"],
    ),
    PublicField("engine_volume", "Объём двигателя, л", hint="например: 1.8 или 2.0"),
    PublicField(
        "fuel",
        "Топливо",
        type="select",
        options=["бензин", "дизель", "гибрид", "электро"],
    ),
    PublicField(
        "transmission",
        "Коробка передач",
        type="select",
        options=["автомат", "вариатор", "робот", "механика"],
    ),
    PublicField("mileage", "Желаемый пробег, км", type="number"),
    PublicField("color", "Цвет (если важен)"),
    PublicField(
        "budget_rub",
        "Бюджет, ₽",
        type="number",
        required=True,
        hint="ориентировочный целевой бюджет",
    ),
    PublicField("power_hp", "Мощность, л.с.", type="number"),
    PublicField("options", "Обязательные опции", hint="например: панорама, CarPlay"),
    PublicField("alternatives", "Рассматриваемые альтернативы"),
    PublicField(
        "delivery_country",
        "Страна доставки",
        type="select",
        options=["РФ", "РБ", "КЗ"],
        required=True,
    ),
]


def _serialize_field(f: PublicField) -> dict:
    return {
        "key": f.key,
        "question": f.question,
        "type": f.type,
        "required": f.required,
        "options": f.options,
        "hint": f.hint,
    }


@router.get("/intake", response_class=HTMLResponse, name="public_intake")
def public_intake_form(request: Request):
    return render(
        request,
        "public_intake.html",
        {
            "fields": [_serialize_field(f) for f in PUBLIC_FIELDS],
            "values": {},
            "errors": {},
        },
    )


@router.post("/intake", name="public_intake_submit")
async def public_intake_submit(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    values = {key: (form.get(key) or "").strip() for key in [f.key for f in PUBLIC_FIELDS]}
    contact = (form.get("contact") or "").strip()

    errors: dict[str, str] = {}
    for f in PUBLIC_FIELDS:
        if f.required and not values.get(f.key):
            errors[f.key] = "Поле обязательно."
    if not contact:
        errors["contact"] = "Укажите способ связи."

    collected: dict[str, object] = {}
    for f in PUBLIC_FIELDS:
        raw = values.get(f.key, "")
        if not raw:
            continue
        if f.type == "number":
            digits = "".join(ch for ch in raw if ch.isdigit())
            if not digits:
                errors[f.key] = "Введите число."
                continue
            collected[f.key] = int(digits)
        else:
            collected[f.key] = raw

    if errors:
        return render(
            request,
            "public_intake.html",
            {
                "fields": [_serialize_field(f) for f in PUBLIC_FIELDS],
                "values": values | {"contact": contact},
                "errors": errors,
            },
        )

    collected["contact"] = contact

    # Создаём «виртуальный» диалог для веб-канала. chat_id отрицательный,
    # чтобы исключить пересечение с реальными telegram-чатами.
    synthetic_chat_id = -int(uuid.uuid4().int % 1_000_000_000)
    conv = Conversation(chat_id=synthetic_chat_id, state="qualified", data={"collected": collected})
    db.add(conv)
    db.flush()

    budget = collected.get("budget_rub")
    if isinstance(budget, int) and budget < 1_500_000:
        status = "budget_low"
        db.add(
            Escalation(
                conversation_id=conv.id,
                reason_code="budget_below_threshold",
                details={"budget_rub": budget, "channel": "web"},
            )
        )
    else:
        status = "qualified"

    lead = Lead(
        conversation_id=conv.id,
        chat_id=synthetic_chat_id,
        customer_telegram_user_id=None,
        status=status,
        payload={"collected": collected, "channel": "web"},
    )
    db.add(lead)
    db.commit()

    summary = []
    label_by_key = {f.key: f.question for f in PUBLIC_FIELDS}
    label_by_key["contact"] = "Контакт"
    for key, value in collected.items():
        summary.append({"label": label_by_key.get(key, key), "value": value})

    return render(
        request,
        "public_intake_done.html",
        {"lead": {"status": status}, "summary": summary},
    )


@router.get("/calculator", response_class=HTMLResponse, name="public_calculator")
def public_calculator_form(request: Request):
    return render(request, "public_calculator.html", {"form": {}, "result": None, "error": None})


@router.post("/calculator", name="public_calculator_submit")
async def public_calculator_submit(request: Request):
    form = await request.form()
    payload = {k: (form.get(k) or "").strip() for k in [
        "country", "age_years", "power_hp",
        "car_price_rub", "extra_costs_rub", "export_cost_rub",
        "commission_rub", "broker_rub", "customs_rub", "logistics_rub",
    ]}
    result, error = _run_calculator(payload)
    return render(
        request,
        "public_calculator.html",
        {"form": payload, "result": result, "error": error},
    )


# ----------------------------- Админ-часть -----------------------------


@router.get("/admin/login", response_class=HTMLResponse, name="admin_login_form")
def admin_login_form(request: Request):
    if _admin_authed(request):
        return RedirectResponse(url="/admin", status_code=HTTP_303_SEE_OTHER)
    return render(request, "admin_login.html")


@router.post("/admin/login", name="admin_login")
def admin_login(token: str = Form(...)):
    if not settings.admin_api_token:
        # В dev-режиме без токена — сразу пускаем.
        resp = RedirectResponse(url="/admin", status_code=HTTP_303_SEE_OTHER)
        return resp
    if token != settings.admin_api_token:
        return _flash_redirect("/admin/login", "error", "Неверный токен.")
    resp = RedirectResponse(url="/admin", status_code=HTTP_303_SEE_OTHER)
    resp.set_cookie(ADMIN_COOKIE, token, httponly=True, samesite="lax", path="/", max_age=8 * 3600)
    return resp


@router.get("/admin/logout", name="admin_logout")
def admin_logout():
    resp = RedirectResponse(url="/admin/login", status_code=HTTP_303_SEE_OTHER)
    resp.delete_cookie(ADMIN_COOKIE, path="/")
    return resp


def _require_admin_or_redirect(request: Request) -> RedirectResponse | None:
    if not _admin_authed(request):
        return RedirectResponse(url="/admin/login", status_code=HTTP_303_SEE_OTHER)
    return None


@router.get("/admin", response_class=HTMLResponse, name="admin_dashboard")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    if r := _require_admin_or_redirect(request):
        return r

    leads_total = db.query(func.count(Lead.id)).scalar() or 0
    leads_qualified = (
        db.query(func.count(Lead.id)).filter(Lead.status == "qualified").scalar() or 0
    )
    conversations = db.query(func.count(Conversation.id)).scalar() or 0
    escalations = db.query(func.count(Escalation.id)).scalar() or 0
    kb_approved = (
        db.query(func.count(KnowledgeBaseSource.id))
        .filter(KnowledgeBaseSource.moderation_status == "approved")
        .scalar()
        or 0
    )
    kb_waiting = (
        db.query(func.count(KnowledgeBaseSource.id))
        .filter(KnowledgeBaseSource.moderation_status == "waiting_customer")
        .scalar()
        or 0
    )

    latest_fx_date = db.query(func.max(FxRate.rate_date)).scalar()
    latest_fx = None
    if latest_fx_date:
        rows = (
            db.query(FxRate)
            .filter(FxRate.rate_date == latest_fx_date)
            .order_by(FxRate.char_code.asc())
            .limit(8)
            .all()
        )
        latest_fx = {
            "rate_date": str(latest_fx_date),
            "rows": [
                {
                    "char_code": r.char_code,
                    "nominal": r.nominal,
                    "rate_rub": _format_money(r.rate_rub),
                }
                for r in rows
            ],
        }

    recent = db.query(Lead).order_by(Lead.created_at.desc()).limit(8).all()
    recent_leads = []
    for lead in recent:
        collected = (lead.payload or {}).get("collected") or {}
        summary_text = "; ".join(
            f"{k}={v}" for k, v in list(collected.items())[:5] if v not in (None, "")
        )
        recent_leads.append(
            {
                "created_at": _format_dt(lead.created_at),
                "chat_id": lead.chat_id,
                "status": lead.status,
                "summary": summary_text or "—",
            }
        )

    return render(
        request,
        "admin_dashboard.html",
        {
            "stats": {
                "leads_total": leads_total,
                "leads_qualified": leads_qualified,
                "conversations": conversations,
                "escalations": escalations,
                "kb_approved": kb_approved,
                "kb_waiting": kb_waiting,
            },
            "latest_fx": latest_fx,
            "recent_leads": recent_leads,
        },
    )


@router.get("/admin/leads", response_class=HTMLResponse, name="admin_leads")
def admin_leads(
    request: Request,
    status: str | None = None,
    q: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    if r := _require_admin_or_redirect(request):
        return r
    limit = max(10, min(int(limit or 50), 500))
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status)
    rows = query.order_by(Lead.created_at.desc()).limit(limit * 4).all()
    items = []
    for lead in rows:
        collected = (lead.payload or {}).get("collected") or {}
        haystack = json.dumps(collected, ensure_ascii=False).lower()
        if q and q.lower() not in haystack:
            continue
        pretty = json.dumps(collected, ensure_ascii=False, indent=2)
        items.append(
            {
                "created_at": _format_dt(lead.created_at),
                "chat_id": lead.chat_id,
                "status": lead.status,
                "pretty": pretty,
            }
        )
        if len(items) >= limit:
            break
    return render(
        request,
        "admin_leads.html",
        {"leads": items, "status": status or "", "q": q or "", "limit": limit},
    )


def _run_calculator(payload: dict) -> tuple[dict | None, str | None]:
    try:
        scope = CalculatorScope(
            country=str(payload.get("country") or ""),
            age_years=int(payload.get("age_years") or 0),
            power_hp=int(payload.get("power_hp") or 0),
        )
        validate_scope(scope)
        inp = CalculatorInput(
            car_price_rub=Decimal(str(payload.get("car_price_rub") or "0")),
            export_cost_rub=Decimal(str(payload.get("export_cost_rub") or "0")),
            commission_rub=Decimal(str(payload.get("commission_rub") or "0")),
            broker_rub=Decimal(str(payload.get("broker_rub") or "0")),
            logistics_rub=Decimal(str(payload.get("logistics_rub") or "0")),
            customs_rub=Decimal(str(payload.get("customs_rub") or "0")),
            extra_costs_rub=Decimal(str(payload.get("extra_costs_rub") or "0")),
        )
        total, items = calculate_total_rub(inp)
    except ValueError as e:
        return None, _calc_error_message(str(e))
    except (InvalidOperation, TypeError):
        return None, "Введены недопустимые числовые значения."
    decorated = [
        {**item, "amount_human": _format_money(item["amount_rub"])} for item in items
    ]
    return {
        "formula_version": settings.formula_version,
        "total_rub": str(total),
        "total_human": _format_money(total),
        "lines": decorated,
    }, None


def _calc_error_message(code: str) -> str:
    mapping = {
        "scope_country_out_of_v1": "Контур v1 поддерживает оформление в РФ.",
        "scope_age_out_of_v1": "Контур v1 поддерживает возраст 3–5 лет.",
        "scope_power_out_of_v1": "Контур v1 поддерживает мощность до 160 л.с.",
    }
    return mapping.get(code, f"Расчёт недоступен: {code}")


@router.get("/admin/calculator", response_class=HTMLResponse, name="admin_calculator")
def admin_calculator_form(request: Request):
    if r := _require_admin_or_redirect(request):
        return r
    return render(request, "admin_calculator.html", {"form": {}, "result": None, "error": None})


@router.post("/admin/calculator", name="admin_calculator_submit")
async def admin_calculator_submit(request: Request):
    if r := _require_admin_or_redirect(request):
        return r
    form = await request.form()
    payload = {k: (form.get(k) or "").strip() for k in [
        "country", "age_years", "power_hp",
        "car_price_rub", "extra_costs_rub", "export_cost_rub",
        "commission_rub", "broker_rub", "customs_rub", "logistics_rub",
    ]}
    result, error = _run_calculator(payload)
    return render(
        request,
        "admin_calculator.html",
        {"form": payload, "result": result, "error": error},
    )


@router.get("/admin/rates", response_class=HTMLResponse, name="admin_rates")
def admin_rates(request: Request, edit: str | None = None, db: Session = Depends(get_db)):
    if r := _require_admin_or_redirect(request):
        return r
    rows = db.query(RateItem).order_by(RateItem.code.asc()).all()
    items = [
        {
            "code": r.code,
            "title": r.title,
            "currency": r.currency,
            "amount": _format_money(r.amount) if r.amount is not None else None,
            "min_amount": _format_money(r.min_amount) if r.min_amount is not None else None,
            "max_amount": _format_money(r.max_amount) if r.max_amount is not None else None,
        }
        for r in rows
    ]
    edit_item = None
    if edit:
        for r in rows:
            if r.code == edit:
                edit_item = {
                    "code": r.code,
                    "title": r.title,
                    "currency": r.currency,
                    "amount": str(r.amount) if r.amount is not None else "",
                    "min_amount": str(r.min_amount) if r.min_amount is not None else "",
                    "max_amount": str(r.max_amount) if r.max_amount is not None else "",
                }
                break
    return render(request, "admin_rates.html", {"items": items, "edit_item": edit_item})


@router.post("/admin/rates", name="admin_rates_save")
async def admin_rates_save(request: Request, db: Session = Depends(get_db)):
    if r := _require_admin_or_redirect(request):
        return r
    form = await request.form()
    code = (form.get("code") or "").strip()
    title = (form.get("title") or "").strip()
    if not code or not title:
        return _flash_redirect("/admin/rates", "error", "Код и название обязательны.")
    item = db.query(RateItem).filter(RateItem.code == code).one_or_none()
    if not item:
        item = RateItem(code=code, title=title)
        db.add(item)
    item.title = title
    item.currency = (form.get("currency") or "RUB").strip()

    def _to_decimal(key: str):
        v = (form.get(key) or "").strip()
        if not v:
            return None
        try:
            return Decimal(v)
        except (InvalidOperation, ValueError):
            return None

    item.amount = _to_decimal("amount")
    item.min_amount = _to_decimal("min_amount")
    item.max_amount = _to_decimal("max_amount")
    db.commit()
    return _flash_redirect("/admin/rates", "success", f"Позиция «{code}» сохранена.")


@router.get("/admin/fx", response_class=HTMLResponse, name="admin_fx")
def admin_fx(request: Request, db: Session = Depends(get_db)):
    if r := _require_admin_or_redirect(request):
        return r
    rates_q = db.query(FxRate).order_by(FxRate.rate_date.desc(), FxRate.char_code.asc()).limit(40)
    rates = [
        {
            "rate_date": str(r.rate_date),
            "char_code": r.char_code,
            "nominal": r.nominal,
            "rate_rub": _format_money(r.rate_rub),
        }
        for r in rates_q.all()
    ]
    overrides_q = db.query(Setting).filter(Setting.key.like("fx_override_%")).all()
    overrides = [
        {"char_code": s.key.replace("fx_override_", "", 1), "rate_rub": s.value}
        for s in overrides_q
    ]
    return render(request, "admin_fx.html", {"rates": rates, "overrides": overrides})


@router.post("/admin/fx/refresh", name="admin_fx_refresh")
def admin_fx_refresh(request: Request, db: Session = Depends(get_db)):
    if r := _require_admin_or_redirect(request):
        return r
    try:
        xml = fetch_cbr_daily_xml(settings.cbr_daily_url)
        rate_date, items = parse_cbr_daily_xml(xml)
    except Exception as exc:  # noqa: BLE001 — обработка отказа сети целиком
        return _flash_redirect("/admin/fx", "error", f"Не удалось получить курсы ЦБ: {exc}")
    upserted = 0
    for item in items:
        existing = (
            db.query(FxRate)
            .filter(FxRate.rate_date == rate_date, FxRate.char_code == item.char_code)
            .one_or_none()
        )
        if existing:
            existing.nominal = item.nominal
            existing.rate_rub = item.rate_rub
        else:
            db.add(
                FxRate(
                    rate_date=rate_date,
                    char_code=item.char_code,
                    nominal=item.nominal,
                    rate_rub=item.rate_rub,
                    source="CBR",
                )
            )
        upserted += 1
    db.commit()
    return _flash_redirect(
        "/admin/fx", "success", f"Курсы обновлены на {rate_date}: {upserted} записей."
    )


@router.post("/admin/fx/override", name="admin_fx_override")
async def admin_fx_override(request: Request, db: Session = Depends(get_db)):
    if r := _require_admin_or_redirect(request):
        return r
    form = await request.form()
    char_code = (form.get("char_code") or "").strip().upper()
    rate_rub = (form.get("rate_rub") or "").strip()
    if not char_code or not rate_rub:
        return _flash_redirect("/admin/fx", "error", "Укажите код валюты и значение курса.")
    key = f"fx_override_{char_code}"
    setting = db.query(Setting).filter(Setting.key == key).one_or_none()
    if not setting:
        setting = Setting(key=key, value=rate_rub)
        db.add(setting)
    else:
        setting.value = rate_rub
    db.commit()
    return _flash_redirect("/admin/fx", "success", f"Курс {char_code} зафиксирован.")


@router.get("/admin/kb", response_class=HTMLResponse, name="admin_kb")
def admin_kb(request: Request, db: Session = Depends(get_db)):
    if r := _require_admin_or_redirect(request):
        return r
    sources = db.query(KnowledgeBaseSource).order_by(KnowledgeBaseSource.code.asc()).all()
    docs_rows = (
        db.query(KnowledgeBaseDoc, KnowledgeBaseSource)
        .join(KnowledgeBaseSource, KnowledgeBaseDoc.source_id == KnowledgeBaseSource.id)
        .order_by(KnowledgeBaseDoc.updated_at.desc())
        .limit(40)
        .all()
    )
    return render(
        request,
        "admin_kb.html",
        {
            "sources": [
                {
                    "code": s.code,
                    "title": s.title,
                    "url": s.url,
                    "moderation_status": s.moderation_status,
                }
                for s in sources
            ],
            "docs": [
                {
                    "source_code": src.code,
                    "title": doc.title,
                    "moderation_status": doc.moderation_status,
                    "updated_at": _format_dt(doc.updated_at),
                }
                for doc, src in docs_rows
            ],
        },
    )


@router.post("/admin/kb/docs", name="admin_kb_create_doc")
async def admin_kb_create_doc(request: Request, db: Session = Depends(get_db)):
    if r := _require_admin_or_redirect(request):
        return r
    form = await request.form()
    source_code = (form.get("source_code") or "").strip()
    title = (form.get("title") or "").strip()
    content = (form.get("content") or "").strip()
    if not source_code or not title or not content:
        return _flash_redirect("/admin/kb", "error", "Заполните все поля документа.")
    src = (
        db.query(KnowledgeBaseSource)
        .filter(KnowledgeBaseSource.code == source_code)
        .one_or_none()
    )
    if not src:
        return _flash_redirect("/admin/kb", "error", "Источник не найден.")
    doc = KnowledgeBaseDoc(
        source_id=src.id,
        title=title,
        content=content,
        tags=[],
        moderation_status=(form.get("moderation_status") or "draft").strip(),
    )
    db.add(doc)
    db.commit()
    return _flash_redirect("/admin/kb", "success", f"Документ «{title}» добавлен.")


@router.get("/admin/users", response_class=HTMLResponse, name="admin_users")
def admin_users(request: Request, db: Session = Depends(get_db)):
    if r := _require_admin_or_redirect(request):
        return r
    roles = [
        {"code": r.code, "title": r.title}
        for r in db.query(Role).order_by(Role.code.asc()).all()
    ]
    user_rows = (
        db.query(User, Role)
        .outerjoin(Role, User.role_id == Role.id)
        .order_by(User.telegram_user_id.asc().nullsfirst())
        .limit(200)
        .all()
    )
    users = [
        {
            "telegram_user_id": u.telegram_user_id,
            "username": u.username,
            "role_code": r.code if r else None,
            "is_active": u.is_active,
        }
        for u, r in user_rows
    ]
    return render(request, "admin_users.html", {"roles": roles, "users": users})


@router.post("/admin/users", name="admin_users_save")
async def admin_users_save(request: Request, db: Session = Depends(get_db)):
    if r := _require_admin_or_redirect(request):
        return r
    form = await request.form()
    try:
        telegram_user_id = int((form.get("telegram_user_id") or "").strip())
    except ValueError:
        return _flash_redirect("/admin/users", "error", "Telegram ID должен быть числом.")
    role_code = (form.get("role_code") or "").strip()
    role = db.query(Role).filter(Role.code == role_code).one_or_none()
    if not role:
        return _flash_redirect("/admin/users", "error", "Роль не найдена.")
    user = db.query(User).filter(User.telegram_user_id == telegram_user_id).one_or_none()
    if not user:
        user = User(telegram_user_id=telegram_user_id)
        db.add(user)
    user.username = (form.get("username") or "").strip() or None
    user.role_id = role.id
    user.is_active = bool(form.get("is_active"))
    db.commit()
    return _flash_redirect("/admin/users", "success", "Пользователь сохранён.")


@router.get("/admin/leads/export.csv", name="admin_leads_export")
def admin_leads_export(request: Request, db: Session = Depends(get_db)):
    if r := _require_admin_or_redirect(request):
        return r
    import csv
    import io

    rows = db.query(Lead).order_by(Lead.created_at.desc()).limit(5000).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "created_at", "chat_id", "status", "payload"])
    for lead in rows:
        writer.writerow(
            [
                str(lead.id),
                lead.created_at.isoformat() + "Z",
                lead.chat_id,
                lead.status,
                json.dumps(lead.payload or {}, ensure_ascii=False),
            ]
        )
    return Response(content=buf.getvalue(), media_type="text/csv; charset=utf-8")


