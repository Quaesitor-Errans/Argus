from dataclasses import dataclass

from sqlalchemy.orm import Session

from argus.acquisition import RetrievalOutcome
from argus.documents import (
    DocumentIngestionConflict,
    DocumentType,
)
from argus.models import (
    AcquisitionCandidate,
    CollectionEndpoint,
    Document,
    DocumentVersion,
    RawArtifact,
    RetrievalAttempt,
)
from argus.storage.document_repository import (
    DocumentRepository,
    DocumentVersionRepository,
)


@dataclass(frozen=True, slots=True)
class DocumentIngestionResult:
    """Document objects produced from one successful retrieval."""

    document: Document
    version: DocumentVersion
    retrieval_attempt: RetrievalAttempt


class DocumentIngestionService:
    """Turn successful retrieval provenance into a document version.

    The service never commits. The caller owns the transaction containing
    the document, version and retrieval-attempt link.
    """

    def __init__(self, session: Session) -> None:
        self._session = session
        self._document_repository = DocumentRepository(session)
        self._version_repository = DocumentVersionRepository(session)

    def ingest_retrieval(
            self,
            *,
            attempt: RetrievalAttempt,
            candidate: AcquisitionCandidate,
            document_type: DocumentType,
    ) -> DocumentIngestionResult:
        endpoint, raw_artifact = self._validate_and_load(
            attempt=attempt,
            candidate=candidate,
        )
        identifier_scheme, identifier_value = (
            self._document_identity(candidate)
        )
        document = self._document_repository.get_or_create(
            identifier_scheme=identifier_scheme,
            identifier_value=identifier_value,
            document_type=document_type,
            source_id=endpoint.source_id,
            title=candidate.title,
            language=candidate.language,
        )
        version = self._version_repository.register(
            document=document,
            raw_artifact=raw_artifact,
            media_type=(
                attempt.content_type or candidate.media_type
            ),
            published_at=candidate.published_at,
        )

        if (
                attempt.document_version_id is not None
                and attempt.document_version_id != version.id
        ):
            raise DocumentIngestionConflict(
                "Retrieval attempt is already linked to another "
                "document version."
            )

        attempt.document_version_id = version.id
        self._session.flush()

        return DocumentIngestionResult(
            document=document,
            version=version,
            retrieval_attempt=attempt,
        )

    def _validate_and_load(
            self,
            *,
            attempt: RetrievalAttempt,
            candidate: AcquisitionCandidate,
    ) -> tuple[CollectionEndpoint, RawArtifact]:
        if attempt.id is None:
            raise ValueError(
                "attempt must be persisted before document ingestion."
            )

        if candidate.id is None:
            raise ValueError(
                "candidate must be persisted before document ingestion."
            )

        if attempt.outcome is not RetrievalOutcome.SUCCEEDED:
            raise DocumentIngestionConflict(
                "Only successful retrieval attempts can create document "
                "versions."
            )

        if attempt.candidate_id != candidate.id:
            raise DocumentIngestionConflict(
                "Retrieval attempt does not reference the supplied "
                "candidate."
            )

        if attempt.endpoint_id != candidate.endpoint_id:
            raise DocumentIngestionConflict(
                "Retrieval attempt and candidate belong to different "
                "endpoints."
            )

        if attempt.raw_artifact_id is None:
            raise DocumentIngestionConflict(
                "Successful retrieval attempt has no raw artifact."
            )

        endpoint = self._session.get(
            CollectionEndpoint,
            attempt.endpoint_id,
        )
        raw_artifact = self._session.get(
            RawArtifact,
            attempt.raw_artifact_id,
        )

        if endpoint is None:
            raise DocumentIngestionConflict(
                "Retrieval endpoint does not exist."
            )

        if raw_artifact is None:
            raise DocumentIngestionConflict(
                "Retrieval raw artifact does not exist."
            )

        if (
                attempt.hash_algorithm != raw_artifact.hash_algorithm
                or attempt.content_hash != raw_artifact.content_hash
        ):
            raise DocumentIngestionConflict(
                "Retrieval attempt does not match its raw artifact."
            )

        return endpoint, raw_artifact

    @staticmethod
    def _document_identity(
            candidate: AcquisitionCandidate,
    ) -> tuple[str, str]:
        if candidate.external_identifier is not None:
            return (
                f"{candidate.connector_id}:external",
                candidate.external_identifier,
            )

        return "uri", candidate.location
