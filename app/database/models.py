import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class PipelineStatus(str, enum.Enum):
    NEW = "NEW"
    QUALIFIED = "QUALIFIED"
    CONTACTED = "CONTACTED"
    REPLIED = "REPLIED"
    MEETING = "MEETING"
    PROPOSAL_SENT = "PROPOSAL_SENT"
    NEGOTIATION = "NEGOTIATION"
    WON = "WON"
    LOST = "LOST"
    DO_NOT_CONTACT = "DO_NOT_CONTACT"
    ARCHIVED = "ARCHIVED"


class ContactType(str, enum.Enum):
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    WEBSITE = "WEBSITE"
    INSTAGRAM = "INSTAGRAM"


class DuplicateLevel(str, enum.Enum):
    EXACT = "EXACT"
    PROBABLE = "PROBABLE"
    POSSIBLE = "POSSIBLE"
    DISTINCT = "DISTINCT"


class DuplicateStatus(str, enum.Enum):
    OPEN = "OPEN"
    DISTINCT = "DISTINCT"
    CONFIRMED_DUPLICATE = "CONFIRMED_DUPLICATE"
    MERGE_REQUESTED = "MERGE_REQUESTED"
    CLOSED = "CLOSED"


class WebsiteAuditStatus(str, enum.Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_normalized: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status", native_enum=True), default=UserStatus.ACTIVE, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    name_normalized: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(40), nullable=False)
    collection_method: Mapped[str] = mapped_column(String(40), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    legal_or_trade_name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_normalized: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    tax_id_normalized: Mapped[str | None] = mapped_column(String(14), unique=True)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    state_code: Mapped[str] = mapped_column(String(2), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), default="BR", nullable=False)
    pipeline_status: Mapped[PipelineStatus] = mapped_column(
        Enum(PipelineStatus, name="pipeline_status", native_enum=True), default=PipelineStatus.NEW, nullable=False
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    updated_by_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    merged_into_company_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"))


class CompanySourceRef(Base):
    __tablename__ = "company_source_refs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    data_source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False
    )
    external_id: Mapped[str | None] = mapped_column(String(300))
    source_url: Mapped[str | None] = mapped_column(Text)
    raw_name: Mapped[str | None] = mapped_column(String(300))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint("company_id", "contact_type", "value_normalized"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    contact_type: Mapped[ContactType] = mapped_column(
        Enum(ContactType, name="contact_type", native_enum=True), nullable=False
    )
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    value_normalized: Mapped[str] = mapped_column(String(500), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    person_name: Mapped[str | None] = mapped_column(String(120))
    job_title: Mapped[str | None] = mapped_column(String(120))
    source_ref_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("company_source_refs.id", ondelete="SET NULL"))
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DuplicateCandidate(Base):
    __tablename__ = "duplicate_candidates"
    __table_args__ = (UniqueConstraint("company_a_id", "company_b_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_a_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    company_b_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    level: Mapped[DuplicateLevel] = mapped_column(
        Enum(DuplicateLevel, name="duplicate_level", native_enum=True), nullable=False
    )
    status: Mapped[DuplicateStatus] = mapped_column(
        Enum(DuplicateStatus, name="duplicate_status", native_enum=True), default=DuplicateStatus.OPEN, nullable=False
    )
    signals: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    decision_reason: Mapped[str | None] = mapped_column(String(500))


class CompanyMergeAudit(Base):
    __tablename__ = "company_merge_audits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    survivor_company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False
    )
    merged_company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False
    )
    performed_by_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class OpportunityScore(Base):
    __tablename__ = "opportunity_scores"
    __table_args__ = (CheckConstraint("total IS NULL OR (total >= 0 AND total <= 100)"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    total: Mapped[int | None] = mapped_column(Integer)
    formula_version: Mapped[str] = mapped_column(String(40), nullable=False)
    components: Mapped[dict] = mapped_column(JSONB, nullable=False)
    explanation: Mapped[str] = mapped_column(String(1000), nullable=False)
    calculated_by_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CommercialActivity(Base):
    __tablename__ = "commercial_activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    previous_status: Mapped[str | None] = mapped_column(String(40))
    new_status: Mapped[str | None] = mapped_column(String(40))
    outcome: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str] = mapped_column(String(1000), nullable=False)
    next_action_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    performed_by_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class WebsiteAudit(Base):
    __tablename__ = "website_audits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    contact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contacts.id", ondelete="RESTRICT"), nullable=False)
    requested_url: Mapped[str] = mapped_column(Text, nullable=False)
    final_url: Mapped[str | None] = mapped_column(Text)
    status: Mapped[WebsiteAuditStatus] = mapped_column(
        Enum(WebsiteAuditStatus, name="website_audit_status", native_enum=True), nullable=False
    )
    http_status: Mapped[int | None] = mapped_column(Integer)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    findings: Mapped[dict] = mapped_column(JSONB, nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(60))
    performed_by_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
