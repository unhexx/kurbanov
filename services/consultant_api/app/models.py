import uuid
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid


def _json_type():
    # JSONB в PostgreSQL, JSON в остальных СУБД (для тестов/локального запуска)
    return JSONB().with_variant(JSON(), "sqlite")


class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(128))

    users: Mapped[list["User"]] = relationship(back_populates="role")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str | None] = mapped_column(String(128), nullable=True)
    telegram_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    role_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("roles.id"), nullable=True)
    role: Mapped[Role | None] = relationship(back_populates="users")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    customer_telegram_user_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, index=True
    )

    state: Mapped[str] = mapped_column(String(64), default="collecting")
    data: Mapped[dict] = mapped_column(_json_type(), default=dict)
    bot_paused: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    messages: Mapped[list["Message"]] = relationship(back_populates="conversation")
    leads: Mapped[list["Lead"]] = relationship(back_populates="conversation")

    __table_args__ = (UniqueConstraint("chat_id", name="uq_conversations_chat_id"),)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"), index=True)

    direction: Mapped[str] = mapped_column(String(8))  # in/out
    telegram_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sender_telegram_user_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, index=True
    )
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw: Mapped[dict] = mapped_column(_json_type(), default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, index=True
    )

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"), index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    customer_telegram_user_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, index=True
    )

    status: Mapped[str] = mapped_column(String(32), default="new")
    payload: Mapped[dict] = mapped_column(_json_type(), default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    conversation: Mapped[Conversation] = relationship(back_populates="leads")


class Estimate(Base):
    __tablename__ = "estimates"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"), index=True)

    formula_version: Mapped[str] = mapped_column(String(32))
    fx_source: Mapped[str] = mapped_column(String(64))
    fx_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fx_rates: Mapped[dict] = mapped_column(_json_type(), default=dict)

    items: Mapped[list] = mapped_column(_json_type(), default=list)
    total_rub: Mapped[float] = mapped_column(Numeric(18, 2))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, index=True
    )


class Escalation(Base):
    __tablename__ = "escalations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"), index=True)

    reason_code: Mapped[str] = mapped_column(String(64), index=True)
    details: Mapped[dict] = mapped_column(_json_type(), default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, index=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_type: Mapped[str] = mapped_column(String(64), index=True)

    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("conversations.id"), nullable=True
    )

    payload: Mapped[dict] = mapped_column(_json_type(), default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, index=True
    )


class KnowledgeBaseSource(Base):
    __tablename__ = "kb_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(256))
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    format: Mapped[str | None] = mapped_column(String(64), nullable=True)
    owner: Mapped[str | None] = mapped_column(String(128), nullable=True)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)

    moderation_status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    docs: Mapped[list["KnowledgeBaseDoc"]] = relationship(back_populates="source")


class KnowledgeBaseDoc(Base):
    __tablename__ = "kb_docs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("kb_sources.id"), index=True)

    title: Mapped[str] = mapped_column(String(256))
    content: Mapped[str] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(_json_type(), default=list)
    moderation_status: Mapped[str] = mapped_column(String(32), default="draft", index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    source: Mapped[KnowledgeBaseSource] = relationship(back_populates="docs")


class RateItem(Base):
    __tablename__ = "rate_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(256))

    currency: Mapped[str] = mapped_column(String(8), default="RUB")
    amount: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    min_amount: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    max_amount: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class FxRate(Base):
    __tablename__ = "fx_rates"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rate_date: Mapped[date] = mapped_column(Date, index=True)
    char_code: Mapped[str] = mapped_column(String(8), index=True)
    nominal: Mapped[int] = mapped_column(Integer)
    rate_rub: Mapped[float] = mapped_column(Numeric(18, 6))
    source: Mapped[str] = mapped_column(String(32), default="CBR")

    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, index=True
    )

    __table_args__ = (
        UniqueConstraint("rate_date", "char_code", name="uq_fx_rates_date_code"),
        Index("ix_fx_rates_date_code", "rate_date", "char_code"),
    )


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
