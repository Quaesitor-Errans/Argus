from enum import Enum


class DocumentType(str, Enum):
    """High-level kind of an attributable information object."""

    ARTICLE = "article"
    REPORT = "report"
    LAW = "law"
    SPEECH = "speech"
    SCIENTIFIC_WORK = "scientific_work"
    DATASET = "dataset"
    HISTORICAL_RECORD = "historical_record"
    OTHER = "other"


class DocumentIdentityConflict(ValueError):
    """Raised when a stable document identity conflicts with stored data."""


class DocumentVersionConflict(ValueError):
    """Raised when version metadata conflicts with immutable content."""


class DocumentIngestionConflict(ValueError):
    """Raised when retrieval provenance cannot form a document version."""
