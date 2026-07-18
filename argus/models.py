from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLAlchemyEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import Mapped, mapped_column

from argus.database import Base
from argus.endpoints import EndpointType

from argus.processing import (
    ProcessingStage,
    ProcessingStatus,
)

from argus.sources import SourceType

def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""

    return datetime.now(timezone.utc)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    identifier: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_type: Mapped[SourceType] = mapped_column(
        SQLAlchemyEnum(
            SourceType,
            name="source_type",
            native_enum=False,
            values_callable=lambda enum_type: [
                member.value
                for member in enum_type
            ],
            validate_strings=True,
            length=50,
        ),
        nullable=False,
        default=SourceType.NEWS_MEDIA,
        index=True,
    )

    primary_jurisdiction: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    default_language: Mapped[str | None] = mapped_column(
        String(35),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )


class CollectionEndpoint(Base):
    __tablename__ = "collection_endpoints"
    __table_args__ = (
        UniqueConstraint(
            "connector_id",
            "url",
            name="uq_collection_endpoint_connector_url",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    identifier: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    source_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "sources.id",
            name=(
                "fk_collection_endpoints_source_id_sources"
            ),
        ),
        nullable=True,
        index=True,
    )

    endpoint_type: Mapped[EndpointType] = mapped_column(
        SQLAlchemyEnum(
            EndpointType,
            name="endpoint_type",
            native_enum=False,
            values_callable=lambda enum_type: [
                member.value
                for member in enum_type
            ],
            validate_strings=True,
            length=50,
        ),
        nullable=False,
        index=True,
    )

    connector_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    language: Mapped[str | None] = mapped_column(
        String(35),
        nullable=True,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    source_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "sources.id",
            name="fk_articles_source_id_sources",
        ),
        nullable=True,
        index=True,
    )

    url: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str | None] = mapped_column(String, nullable=True)

    author: Mapped[str | None] = mapped_column(String, nullable=True)
    language: Mapped[str | None] = mapped_column(String, nullable=True)

    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)

    content_hash: Mapped[str | None] = mapped_column(String, nullable=True, index=True)


class ProcessingState(Base):
    __tablename__ = "processing_states"
    __table_args__ = (
        UniqueConstraint(
            "article_id",
            "stage",
            "method_version",
            name="uq_processing_article_stage_method",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id"),
        nullable=False,
        index=True,
    )

    stage: Mapped[ProcessingStage] = mapped_column(
        SQLAlchemyEnum(
            ProcessingStage,
            name="processing_stage",
            native_enum=False,
            values_callable=lambda enum_type: [
                member.value
                for member in enum_type
            ],
            validate_strings=True,
            length=50,
        ),
        nullable=False,
        index=True,
    )

    method_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="default",
    )

    status: Mapped[ProcessingStatus] = mapped_column(
        SQLAlchemyEnum(
            ProcessingStatus,
            name="processing_status",
            native_enum=False,
            values_callable=lambda enum_type: [
                member.value
                for member in enum_type
            ],
            validate_strings=True,
            length=20,
        ),
        nullable=False,
        default=ProcessingStatus.PENDING,
        index=True,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class DiscourseAnalysisResult(Base):
    __tablename__ = "discourse_analysis_results"
    __table_args__ = (
        UniqueConstraint(
            "article_id",
            "method_version",
            name="uq_discourse_article_method",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id"),
        nullable=False,
        index=True,
    )

    method_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    word_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    sentence_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    average_sentence_length: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    question_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    exclamation_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    first_person_plural_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    third_person_plural_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    certainty_marker_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    uncertainty_marker_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    fear_marker_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    threat_marker_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class AnalysisEvidence(Base):
    __tablename__ = "analysis_evidence"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    analysis_result_id: Mapped[int] = mapped_column(
        ForeignKey("discourse_analysis_results.id"),
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    sentence: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    matched_terms: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
