"""Asynchronous Python client for Withings."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from aiowithings import MeasurementGroup

from . import load_fixture

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion


@pytest.mark.parametrize(
    "file",
    [
        "measurement_list.json",
        "measurement_list_2.json",
    ],
)
def test_measurement_parsing(snapshot: SnapshotAssertion, file: str) -> None:
    """Test measurement parsing."""
    json_file: list[dict[str, Any]] = json.loads(load_fixture(file))

    measurements = [MeasurementGroup.from_api(measurement) for measurement in json_file]

    assert measurements == snapshot(name=file)
