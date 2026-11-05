"""Asynchronous Python client for Withings."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from aiowithings import MeasurementGroup, SleepSummary, aggregate_measurements
from aiowithings.helpers import aggregate_sleep_summary

from . import load_fixture

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion


def test_aggregate_measurements(snapshot: SnapshotAssertion) -> None:
    """Test aggregation."""
    json_file: list[dict[str, Any]] = json.loads(load_fixture("measurement_list.json"))

    measurements = [MeasurementGroup.from_api(measurement) for measurement in json_file]

    assert aggregate_measurements(measurements) == snapshot


def test_aggregate_positional_measurements(snapshot: SnapshotAssertion) -> None:
    """Test aggregation of positional measurements."""
    json_file: list[dict[str, Any]] = json.loads(
        load_fixture("measurement_positions.json")
    )

    measurements = [MeasurementGroup.from_api(measurement) for measurement in json_file]

    aggregation = aggregate_measurements(measurements)
    assert len(aggregation.items()) == 26
    assert aggregate_measurements(measurements) == snapshot


def test_aggregate_sleep_summary(snapshot: SnapshotAssertion) -> None:
    """Test aggregation."""
    json_file: list[dict[str, Any]] = json.loads(load_fixture("sleep_summary.json"))[
        "body"
    ]["series"]

    sleep_summaries = [
        SleepSummary.from_api(sleep_summary) for sleep_summary in json_file
    ]

    assert aggregate_sleep_summary(sleep_summaries) == snapshot


def test_aggregate_sleep_summary_with_missing_optional_metric() -> None:
    """Test aggregation when an optional metric is unavailable in every summary."""
    json_file: list[dict[str, Any]] = json.loads(load_fixture("sleep_summary.json"))[
        "body"
    ]["series"][:2]
    for sleep_summary in json_file:
        sleep_summary["data"].pop("breathing_disturbances_intensity")

    sleep_summaries = [
        SleepSummary.from_api(sleep_summary) for sleep_summary in json_file
    ]

    aggregated_summary = aggregate_sleep_summary(sleep_summaries)

    assert aggregated_summary is not None
    assert aggregated_summary.breathing_disturbances_intensity is None
    assert aggregated_summary.average_heart_rate == 96


def test_aggregate_single_sleep_summary(snapshot: SnapshotAssertion) -> None:
    """Test aggregation."""
    json_file: dict[str, Any] = json.loads(load_fixture("sleep_summary.json"))["body"][
        "series"
    ][0]

    sleep_summary = SleepSummary.from_api(json_file)

    assert aggregate_sleep_summary([sleep_summary]) == snapshot


def test_aggregate_no_sleep_summary(snapshot: SnapshotAssertion) -> None:
    """Test aggregation."""
    assert aggregate_sleep_summary([]) == snapshot
