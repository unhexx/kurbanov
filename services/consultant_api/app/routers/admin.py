from __future__ import annotations

import csv
import io
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db import get_db

from app.models import (
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
from app.security import AdminAuth
from app.services.fx_rates import fetch_cbr_daily_xml, parse_cbr_daily_xml
from app.settings import settings

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[AdminAuth])


@router.get("/health")
def health():
    return {"ok": True, "time": datetime.utcnow().isoformat() + "Z"}


@router.post("/fx_rates/refresh")
def refresh_fx_rates(db: Session = Depends(get_db)):
    xml = fetch_cbr_daily_xml(settings.cbr_daily_url)
    rate_date, items = parse_cbr_daily_xml(xml)
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
    return {"rate_date": str(rate_date), "upserted": upserted}


@router.get("/fx_rates")
def list_fx_rates(rate_date: str | None = None, db: Session = Depends(get_db)):
    q = db.query(FxRate).order_by(FxRate.rate_date.desc(), FxRate.char_code.asc())
    if rate_date:
        q = q.filter(FxRate.rate_date == rate_date)
    rows = q.limit(200).all()
    return [
        {
            "rate_date": str(r.rate_date),
            "char_code": r.char_code,
            "nominal": r.nominal,
            "rate_rub": str(r.rate_rub),
            "source": r.source,
            "fetched_at": r.fetched_at.isoformat() + "Z",
        }
        for r in rows
    ]


@router.post("/fx_rates/override")
def set_fx_override(payload: dict, db: Session = Depends(get_db)):
    char_code = (payload.get("char_code") or "").strip().upper()
    rate_rub = (payload.get("rate_rub") or "").strip()
    if not char_code or not rate_rub:
        raise HTTPException(status_code=400, detail="char_code and rate_rub are required")
    key = f"fx_override_{char_code}"
    st = db.query(Setting).filter(Setting.key == key).one_or_none()
    if not st:
        st = Setting(key=key, value=rate_rub)
        db.add(st)
    else:
        st.value = rate_rub
    db.commit()
    return {"ok": True, "char_code": char_code, "rate_rub": rate_rub}


@router.get("/fx_rates/overrides")
def list_fx_overrides(db: Session = Depends(get_db)):
    rows = db.query(Setting).filter(Setting.key.like("fx_override_%")).all()
    out = []
    for r in rows:
        out.append({"char_code": r.key.replace("fx_override_", "", 1), "rate_rub": r.value})
    return out


@router.post("/rates")
def upsert_rate(
    payload: dict,
    db: Session = Depends(get_db),
):
    code = (payload.get("code") or "").strip()
    title = (payload.get("title") or "").strip()
    if not code or not title:
        raise HTTPException(status_code=400, detail="code and title are required")
    item = db.query(RateItem).filter(RateItem.code == code).one_or_none()
    if not item:
        item = RateItem(code=code, title=title)
        db.add(item)
    item.title = title
    item.currency = (payload.get("currency") or "RUB").strip()
    item.amount = payload.get("amount")
    item.min_amount = payload.get("min_amount")
    item.max_amount = payload.get("max_amount")
    db.commit()
    return {"ok": True, "code": item.code}


@router.get("/rates")
def list_rates(db: Session = Depends(get_db)):
    rows = db.query(RateItem).order_by(RateItem.code.asc()).all()
    return [
        {
            "code": r.code,
            "title": r.title,
            "currency": r.currency,
            "amount": str(r.amount) if r.amount is not None else None,
            "min_amount": str(r.min_amount) if r.min_amount is not None else None,
            "max_amount": str(r.max_amount) if r.max_amount is not None else None,
        }
        for r in rows
    ]


@router.post("/estimates/preview")
def preview_estimate(payload: dict):
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
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"formula_version": settings.formula_version, "total_rub": str(total), "items": items}


@router.get("/leads/export.csv")
def export_leads_csv(db: Session = Depends(get_db)):
    rows = db.query(Lead).order_by(Lead.created_at.desc()).limit(5000).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "created_at", "chat_id", "customer_telegram_user_id", "status", "payload"])
    for r in rows:
        w.writerow(
            [
                str(r.id),
                r.created_at.isoformat() + "Z",
                r.chat_id,
                r.customer_telegram_user_id,
                r.status,
                r.payload,
            ]
        )
    return Response(content=buf.getvalue(), media_type="text/csv; charset=utf-8")


@router.post("/kb_sources")
def upsert_kb_source(payload: dict, db: Session = Depends(get_db)):
    code = (payload.get("code") or "").strip()
    title = (payload.get("title") or "").strip()
    if not code or not title:
        raise HTTPException(status_code=400, detail="code and title are required")
    src = db.query(KnowledgeBaseSource).filter(KnowledgeBaseSource.code == code).one_or_none()
    if not src:
        src = KnowledgeBaseSource(code=code, title=title)
        db.add(src)
    src.title = title
    src.url = payload.get("url")
    src.format = payload.get("format")
    src.owner = payload.get("owner")
    src.moderation_status = payload.get("moderation_status") or src.moderation_status
    src.notes = payload.get("notes")
    db.commit()
    return {"ok": True, "code": src.code}


@router.get("/kb_sources")
def list_kb_sources(db: Session = Depends(get_db)):
    rows = db.query(KnowledgeBaseSource).order_by(KnowledgeBaseSource.code.asc()).all()
    return [
        {
            "code": s.code,
            "title": s.title,
            "url": s.url,
            "format": s.format,
            "owner": s.owner,
            "moderation_status": s.moderation_status,
            "updated_at": s.updated_at.isoformat() + "Z",
        }
        for s in rows
    ]


@router.post("/kb_docs")
def create_kb_doc(payload: dict, db: Session = Depends(get_db)):
    source_code = (payload.get("source_code") or "").strip()
    title = (payload.get("title") or "").strip()
    content = (payload.get("content") or "").strip()
    if not source_code or not title or not content:
        raise HTTPException(status_code=400, detail="source_code, title, content are required")
    src = (
        db.query(KnowledgeBaseSource)
        .filter(KnowledgeBaseSource.code == source_code)
        .one_or_none()
    )
    if not src:
        raise HTTPException(status_code=404, detail="kb source not found")
    doc = KnowledgeBaseDoc(
        source_id=src.id,
        title=title,
        content=content,
        tags=payload.get("tags") or [],
        moderation_status=payload.get("moderation_status") or "draft",
    )
    db.add(doc)
    db.commit()
    return {"ok": True, "id": str(doc.id)}


@router.get("/kb_docs")
def list_kb_docs(source_code: str | None = None, db: Session = Depends(get_db)):
    q = db.query(KnowledgeBaseDoc, KnowledgeBaseSource).join(
        KnowledgeBaseSource, KnowledgeBaseDoc.source_id == KnowledgeBaseSource.id
    )
    if source_code:
        q = q.filter(KnowledgeBaseSource.code == source_code)
    rows = q.order_by(KnowledgeBaseDoc.updated_at.desc()).limit(200).all()
    return [
        {
            "id": str(doc.id),
            "source_code": src.code,
            "title": doc.title,
            "moderation_status": doc.moderation_status,
            "updated_at": doc.updated_at.isoformat() + "Z",
        }
        for doc, src in rows
    ]


@router.post("/roles")
def upsert_role(payload: dict, db: Session = Depends(get_db)):
    code = (payload.get("code") or "").strip()
    title = (payload.get("title") or "").strip()
    if not code or not title:
        raise HTTPException(status_code=400, detail="code and title are required")
    role = db.query(Role).filter(Role.code == code).one_or_none()
    if not role:
        role = Role(code=code, title=title)
        db.add(role)
    role.title = title
    db.commit()
    return {"ok": True, "code": role.code}


@router.get("/roles")
def list_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).order_by(Role.code.asc()).all()
    return [{"code": r.code, "title": r.title} for r in roles]


@router.post("/users")
def upsert_user(payload: dict, db: Session = Depends(get_db)):
    telegram_user_id = payload.get("telegram_user_id")
    role_code = (payload.get("role_code") or "").strip()
    if not telegram_user_id or not role_code:
        raise HTTPException(status_code=400, detail="telegram_user_id and role_code are required")
    role = db.query(Role).filter(Role.code == role_code).one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="role not found")
    user = db.query(User).filter(User.telegram_user_id == int(telegram_user_id)).one_or_none()
    if not user:
        user = User(telegram_user_id=int(telegram_user_id))
        db.add(user)
    user.username = payload.get("username")
    user.role_id = role.id
    user.is_active = bool(payload.get("is_active", True))
    db.commit()
    return {"ok": True, "telegram_user_id": user.telegram_user_id}


@router.get("/users")
def list_users(db: Session = Depends(get_db)):
    q = (
        db.query(User, Role)
        .outerjoin(Role, User.role_id == Role.id)
        .order_by(User.telegram_user_id.asc())
    )
    rows = q.limit(200).all()
    return [
        {
            "id": str(u.id),
            "username": u.username,
            "telegram_user_id": u.telegram_user_id,
            "role_code": r.code if r else None,
            "is_active": u.is_active,
        }
        for u, r in rows
    ]
