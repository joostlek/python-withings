"""Asynchronous Python client for Withings."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from aiowithings import MeasurementGroup

from . import load_fixture

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion


def test_measurement_parsing(snapshot: SnapshotAssertion) -> None:
    """Test measurement parsing."""
    json_file: list[dict[str, Any]] = json.loads(load_fixture("measurement_list.json"))

    measurements = [MeasurementGroup.from_api(measurement) for measurement in json_file]

    assert measurements == snapshot
