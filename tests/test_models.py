"""Asynchronous Python client for Withings."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from aiowithings import Device, MeasurementGroup

from . import load_fixture

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion


@pytest.mark.parametrize(
    ("device_type", "model_id", "model", "expected_model"),
    [
        ("Scale", 13, "", "Body+"),
        ("Scale", 13, "Sleep Analyzer", "Body+"),
        ("Scale", 13, "Body+", "Body+"),
        ("Scale", 13, "Body+S", "Body+S"),
        ("Sleep Monitor", 13, "", "Sleep Analyzer"),
        ("Sleep Monitor", 13, "Sleep Analyzer", "Sleep Analyzer"),
        ("Sleep Monitor", 13, "Aura Sensor V2", "Aura Sensor V2"),
        ("Scale", 5, "", ""),
        ("Scale", 5, "Body+", "Body+"),
        ("Scale", 5, "Sleep Analyzer", "Sleep Analyzer"),
    ],
)
def test_device_model_name(
    device_type: str, model_id: int, model: str, expected_model: str
) -> None:
    """Test model 13 scale names without changing other device names."""
    device_data = json.loads(load_fixture("device.json"))["body"]["devices"][0]
    device_data.update(type=device_type, model_id=model_id, model=model)

    device = Device.from_api(device_data)

    assert device.raw_model == expected_model
    assert device.device_type == device_type
    assert device.model == model_id


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
