from argus.services.processing import (
    DONE,
    FAILED,
    PENDING,
    RUNNING,
)


def test_processing_constants():
    assert PENDING == "pending"
    assert RUNNING == "running"
    assert DONE == "done"
    assert FAILED == "failed"