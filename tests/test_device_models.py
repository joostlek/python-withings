"""Device models the API reports must not fall through to UNKNOWN."""

from __future__ import annotations

import pytest

from aiowithings import Device, DeviceModel


def _device(model_id: int, model: str) -> dict[str, object]:
    """Shape a getdevice entry, keeping only what Device.from_api reads."""
    return {
        "type": "Blood Pressure Monitor",
        "battery": "high",
        "model": model,
        "model_id": model_id,
        "first_session_date": None,
        "last_session_date": None,
        "deviceid": "d",
        "hash_deviceid": "d",
    }


@pytest.mark.parametrize(
    ("model_id", "raw_model", "expected"),
    [
        (48, "BPM Vision", DeviceModel.BPM_VISION),
        (71, "BeamO", DeviceModel.BEAMO),
    ],
)
def test_model_is_recognised(
    model_id: int,
    raw_model: str,
    expected: DeviceModel,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Both ids come from a live account; see issue #886."""
    device = Device.from_api(_device(model_id, raw_model))

    assert device.model is expected
    assert device.raw_model == raw_model
    assert "unsupported value" not in caplog.text


def test_an_actually_unknown_model_still_falls_back(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The fallback has to keep working, or this trades one gap for another."""
    device = Device.from_api(_device(696969, "Futuristic device A"))

    assert device.model is DeviceModel.UNKNOWN
    assert "unsupported value" in caplog.text
