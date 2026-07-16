"""Protocol-independent acquisition contracts."""

from argus.acquisition.connector import Connector
from argus.acquisition.contracts import (
    AcquisitionMode,
    CandidateRecord,
    DiscoveryRequest,
    RetrievalOutcome,
    RetrievalResult,
)

__all__ = [
    "AcquisitionMode",
    "CandidateRecord",
    "Connector",
    "DiscoveryRequest",
    "RetrievalOutcome",
    "RetrievalResult",
]
