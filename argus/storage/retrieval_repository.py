from collections.abc import Mapping

from sqlalchemy.orm import Session

from argus.acquisition import (
    RetrievalOutcome,
    RetrievalResult,
)
from argus.models import (
    CollectionEndpoint,
    RawArtifact,
    RetrievalAttempt,
)
from argus.storage.base_repository import BaseRepository


class RetrievalProvenanceConflict(ValueError):
    """Raised when retrieval data conflicts with its endpoint."""


class RetrievalAttemptRepository(
    BaseRepository[RetrievalAttempt]
):
    def __init__(self, session: Session) -> None:
        super().__init__(
            session=session,
            model_type=RetrievalAttempt,
        )

    def record_result(
        self,
        *,
        endpoint: CollectionEndpoint,
        result: RetrievalResult,
        article_id: int | None = None,
        raw_artifact: RawArtifact | None = None,
        request_metadata: Mapping[str, object] | None = None,
    ) -> RetrievalAttempt:
        if endpoint.id is None:
            raise ValueError(
                "endpoint must be persisted before retrieval is recorded."
            )

        candidate = result.candidate

        if candidate.connector_id != endpoint.connector_id:
            raise RetrievalProvenanceConflict(
                "Candidate connector does not match the collection "
                "endpoint connector."
            )

        content_hash = result.content_hash

        self._validate_raw_artifact(
            result=result,
            raw_artifact=raw_artifact,
        )

        attempt = RetrievalAttempt(
            endpoint_id=endpoint.id,
            article_id=article_id,
            raw_artifact_id=(
                raw_artifact.id
                if raw_artifact is not None
                else None
            ),
            connector_id=candidate.connector_id,
            connector_version=candidate.connector_version,
            requested_location=candidate.location,
            external_identifier=candidate.external_identifier,
            discovered_at=candidate.discovered_at,
            retrieved_at=result.retrieved_at,
            outcome=result.outcome,
            resolved_location=result.resolved_location,
            response_status=result.response_status,
            content_type=result.content_type,
            content_hash=content_hash,
            hash_algorithm=(
                "sha256"
                if content_hash is not None
                else None
            ),
            error=result.error,
            warnings=list(result.warnings),
            request_metadata=(
                dict(request_metadata)
                if request_metadata is not None
                else None
            ),
        )

        self.add(attempt)
        self.flush()

        return attempt

    @staticmethod
    def _validate_raw_artifact(
        *,
        result: RetrievalResult,
        raw_artifact: RawArtifact | None,
    ) -> None:
        if result.outcome is RetrievalOutcome.SUCCEEDED:
            if raw_artifact is None or raw_artifact.id is None:
                raise RetrievalProvenanceConflict(
                    "Successful retrieval requires a persisted "
                    "raw artifact."
                )

            if (
                raw_artifact.hash_algorithm != "sha256"
                or raw_artifact.content_hash
                != result.content_hash
                or raw_artifact.byte_size
                != len(result.content or b"")
            ):
                raise RetrievalProvenanceConflict(
                    "Raw artifact does not match retrieved content."
                )

        elif raw_artifact is not None:
            raise RetrievalProvenanceConflict(
                "Unsuccessful retrieval must not reference a raw "
                "artifact."
            )
