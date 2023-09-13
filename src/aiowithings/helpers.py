"""Asynchronous Python client for Withings."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiowithings import MeasurementGroup, MeasurementType


def aggregate_measurements(
    measurements: list[MeasurementGroup],
) -> dict[MeasurementType, float]:
    """Aggregate the measurements to return a list of the latest measurements."""
    result: dict[MeasurementType, float] = {}

    for measurement in measurements:
        for data_point in measurement.measurements:
            result[data_point.measurement_type] = data_point.value

    return result
