"""Asynchronous Python client for Withings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiowithings.models import (
    MeasurementAttribution,
    MeasurementPosition,
    MeasurementType,
    SleepSummary,
)

if TYPE_CHECKING:
    from aiowithings import MeasurementGroup


def aggregate_measurements(
    measurements: list[MeasurementGroup],
) -> dict[tuple[MeasurementType, MeasurementPosition | None], float]:
    """Aggregate the measurements to return a list of the latest measurements."""
    result: dict[tuple[MeasurementType, MeasurementPosition | None], float] = {}

    groups = sorted(measurements, key=lambda group: group.taken_at)

    for measurement in groups:
        if measurement.attribution not in (
            MeasurementAttribution.UNKNOWN,
            MeasurementAttribution.DEVICE_ENTRY_FOR_USER_AMBIGUOUS,
        ):
            for data_point in measurement.measurements:
                if data_point.position in (
                    MeasurementPosition.WHOLE_BODY,
                    MeasurementPosition.BETWEEN_LEGS,
                ):
                    data_point.position = None
                result[(data_point.measurement_type, data_point.position)] = (
                    data_point.value
                )

    return result


def aggregate_sleep_summary(
    sleep_summaries: list[SleepSummary],
) -> SleepSummary | None:
    """Aggregate the sleep summaries to return a combined report."""
    if len(sleep_summaries) == 0:
        return None
    if len(sleep_summaries) == 1:
        return sleep_summaries[0]
    sorted_sleep_summaries = sorted(
        sleep_summaries,
        key=lambda sleep_summary: sleep_summary.start_date,
    )

    def average(data: list[int]) -> int:
        return round(sum(data) / len(data))

    return SleepSummary(
        start_date=sorted_sleep_summaries[0].start_date,
        end_date=sorted_sleep_summaries[1].end_date,
        date=sorted_sleep_summaries[0].date,
        hashed_device_id=sorted_sleep_summaries[0].hashed_device_id,
        breathing_disturbances_intensity=average(
            [
                summary.breathing_disturbances_intensity
                for summary in sleep_summaries
                if summary.breathing_disturbances_intensity is not None
            ],
        ),
        deep_sleep_duration=sum(
            summary.deep_sleep_duration
            for summary in sleep_summaries
            if summary.deep_sleep_duration is not None
        ),
        sleep_latency=average(
            [
                summary.sleep_latency
                for summary in sleep_summaries
                if summary.sleep_latency is not None
            ],
        ),
        wake_up_latency=average(
            [
                summary.wake_up_latency
                for summary in sleep_summaries
                if summary.wake_up_latency is not None
            ],
        ),
        average_heart_rate=average(
            [
                summary.average_heart_rate
                for summary in sleep_summaries
                if summary.average_heart_rate is not None
            ],
        ),
        max_heart_rate=average(
            [
                summary.max_heart_rate
                for summary in sleep_summaries
                if summary.max_heart_rate is not None
            ],
        ),
        min_heart_rate=average(
            [
                summary.min_heart_rate
                for summary in sleep_summaries
                if summary.min_heart_rate is not None
            ],
        ),
        light_sleep_duration=sum(
            summary.light_sleep_duration
            for summary in sleep_summaries
            if summary.light_sleep_duration is not None
        ),
        rem_sleep_duration=sum(
            summary.rem_sleep_duration
            for summary in sleep_summaries
            if summary.rem_sleep_duration is not None
        ),
        average_respiration_rate=average(
            [
                summary.average_respiration_rate
                for summary in sleep_summaries
                if summary.average_respiration_rate is not None
            ],
        ),
        max_respiration_rate=average(
            [
                summary.max_respiration_rate
                for summary in sleep_summaries
                if summary.max_respiration_rate is not None
            ],
        ),
        min_respiration_rate=average(
            [
                summary.min_respiration_rate
                for summary in sleep_summaries
                if summary.min_respiration_rate is not None
            ],
        ),
        sleep_score=max(
            (
                summary.sleep_score
                for summary in sleep_summaries
                if summary.sleep_score is not None
            ),
            default=0,
        ),
        snoring=average(
            [
                summary.snoring
                for summary in sleep_summaries
                if summary.snoring is not None
            ],
        ),
        snoring_count=sum(
            summary.snoring_count
            for summary in sleep_summaries
            if summary.snoring_count is not None
        ),
        wake_up_count=sum(
            summary.wake_up_count
            for summary in sleep_summaries
            if summary.wake_up_count is not None
        ),
        total_time_awake=average(
            [
                summary.total_time_awake
                for summary in sleep_summaries
                if summary.total_time_awake is not None
            ],
        ),
        active_movement_duration=None,
        apnea_hypopnea_index=None,
        average_movement_score=None,
        external_time_asleep=None,
        out_of_bed_count=None,
        rem_sleep_phase_count=None,
        sleep_efficiency=None,
        time_awake_during_sleep=None,
        total_sleep_time=None,
        total_time_in_bed=None,
        withings_index=None,
    )
