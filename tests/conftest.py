"""Asynchronous Python client for Withings."""
import pytest

from syrupy import SnapshotAssertion

from .syrupy import WithingsSnapshotExtension


@pytest.fixture(name="snapshot")
def snapshot_assertion(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the Withings extension."""
    return snapshot.use_extension(WithingsSnapshotExtension)
