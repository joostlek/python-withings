"""Asynchronous Python client for Withings."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
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

    device = Device.from_dict(device_data)

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

    measurements = [
        MeasurementGroup.from_dict(measurement) for measurement in json_file
    ]

    assert measurements == snapshot(name=file)


def test_measurement_group_parsing_under_frozen_time() -> None:
    """Test the first parse of a measurement group while time is frozen.

    The test runs in a new process because mashumaro can build a ``from_dict``
    on its first call. That build must not see the fake ``datetime`` class.
    """
    code = """
import json
from datetime import UTC
from pathlib import Path

import freezegun

from aiowithings import MeasurementGroup

data = json.loads(Path("tests/fixtures/measurement.json").read_text())
with freezegun.freeze_time("2023-10-21"):
    group = MeasurementGroup.from_dict(data["body"]["measuregrps"][0])
assert group.taken_at.tzinfo is UTC, group.taken_at
assert group.taken_at.timestamp() == 1693651151, group.taken_at
"""
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code],
        capture_output=True,
        check=False,
        cwd=Path(__file__).parent.parent,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_from_dict_built_at_import() -> None:
    """Test that mashumaro builds every model's ``from_dict`` at import time.

    A ``from_dict`` that mashumaro could not build yet, for example because of a
    forward reference, is a stub that calls ``CodeBuilder`` on its first call.
    The test runs in a new process because that first call replaces the stub.
    """
    code = """
from aiowithings.models import _WithingsModel

def subclasses(cls):
    for sub in cls.__subclasses__():
        yield sub
        yield from subclasses(sub)

models = list(subclasses(_WithingsModel))
assert models
lazy = [
    model.__name__
    for model in models
    if "CodeBuilder" in model.from_dict.__func__.__code__.co_names
]
assert not lazy, lazy
"""
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code],
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0, result.stderr
