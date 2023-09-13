"""Asynchronous Python client for Withings."""
from datetime import datetime, timezone

import aiohttp
from aresponses import ResponsesMockServer

from aiowithings import WithingsClient
from aiowithings.models import SleepDataFields, SleepSummaryDataFields
from syrupy import SnapshotAssertion

from . import load_fixture

WITHINGS_URL = "wbsapi.withings.net"


async def test_get_sleep(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving sleep."""
    aresponses.add(
        WITHINGS_URL,
        "/v2/sleep",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("sleep.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        response = await withings.get_sleep(
            datetime.fromtimestamp(0, tz=timezone.utc),
            datetime.now(tz=timezone.utc),
            [
                SleepDataFields.HEART_RATE,
                SleepDataFields.RESPIRATION_RATE,
                SleepDataFields.SNORING,
                SleepDataFields.HEART_RATE_VARIABILITY,
                SleepDataFields.HEART_RATE_VARIABILITY_2,
                SleepDataFields.MOVEMENT_SCORE,
            ],
        )
        assert response == snapshot
        await withings.close()


async def test_get_sleep_without_data_fields(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving sleep without datafields."""
    aresponses.add(
        WITHINGS_URL,
        "/v2/sleep",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("sleep_no_datafields.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        response = await withings.get_sleep(
            datetime.fromtimestamp(0, tz=timezone.utc),
            datetime.now(tz=timezone.utc),
        )
        assert response == snapshot
        await withings.close()


async def test_get_sleep_summary_in_period(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving sleep."""
    aresponses.add(
        WITHINGS_URL,
        "/v2/sleep",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("sleep_summary.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        response = await withings.get_sleep_summary_in_period(
            datetime.fromtimestamp(0, tz=timezone.utc).date(),
            datetime.now(tz=timezone.utc).date(),
            [
                SleepSummaryDataFields.REM_SLEEP_PHASE_COUNT,
                SleepSummaryDataFields.SLEEP_EFFICIENCY,
                SleepSummaryDataFields.SLEEP_LATENCY,
                SleepSummaryDataFields.TOTAL_SLEEP_TIME,
                SleepSummaryDataFields.TOTAL_TIME_IN_BED,
                SleepSummaryDataFields.WAKE_UP_LATENCY,
                SleepSummaryDataFields.TIME_AWAKE_DURING_SLEEP,
                SleepSummaryDataFields.APNEA_HYPOPNEA_INDEX,
                SleepSummaryDataFields.BREATHING_DISTURBANCES_INTENSITY,
                SleepSummaryDataFields.EXTERNAL_TOTAL_SLEEP_TIME,
                SleepSummaryDataFields.DEEP_SLEEP_DURATION,
                SleepSummaryDataFields.AVERAGE_HEART_RATE,
                SleepSummaryDataFields.MIN_HEART_RATE,
                SleepSummaryDataFields.MAX_HEART_RATE,
                SleepSummaryDataFields.LIGHT_SLEEP_DURATION,
                SleepSummaryDataFields.ACTIVE_MOVEMENT_DURATION,
                SleepSummaryDataFields.AVERAGE_MOVEMENT_SCORE,
                SleepSummaryDataFields.NIGHT_EVENTS,
                SleepSummaryDataFields.OUT_OF_BED_COUNT,
                SleepSummaryDataFields.REM_SLEEP_DURATION,
                SleepSummaryDataFields.AVERAGE_RESPIRATION_RATE,
                SleepSummaryDataFields.MIN_RESPIRATION_RATE,
                SleepSummaryDataFields.MAX_RESPIRATION_RATE,
                SleepSummaryDataFields.SLEEP_SCORE,
                SleepSummaryDataFields.SNORING,
                SleepSummaryDataFields.SNORING_COUNT,
                SleepSummaryDataFields.WAKE_UP_COUNT,
                SleepSummaryDataFields.TOTAL_TIME_AWAKE,
                SleepSummaryDataFields.WITHINGS_INDEX,
            ],
        )
        assert response == snapshot
        await withings.close()


async def test_get_sleep_summary_in_period_without_data_fields(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving sleep without datafields."""
    aresponses.add(
        WITHINGS_URL,
        "/v2/sleep",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("sleep_summary_no_datafields.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        response = await withings.get_sleep_summary_in_period(
            datetime.fromtimestamp(0, tz=timezone.utc).date(),
            datetime.now(tz=timezone.utc).date(),
        )
        assert response == snapshot
        await withings.close()


async def test_get_sleep_summary_since(
    aresponses: ResponsesMockServer,
) -> None:
    """Test retrieving sleep."""
    aresponses.add(
        WITHINGS_URL,
        "/v2/sleep",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("sleep_summary.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        response = await withings.get_sleep_summary_since(
            datetime.fromtimestamp(0, tz=timezone.utc),
            [
                SleepSummaryDataFields.REM_SLEEP_PHASE_COUNT,
                SleepSummaryDataFields.SLEEP_EFFICIENCY,
                SleepSummaryDataFields.SLEEP_LATENCY,
                SleepSummaryDataFields.TOTAL_SLEEP_TIME,
                SleepSummaryDataFields.TOTAL_TIME_IN_BED,
                SleepSummaryDataFields.WAKE_UP_LATENCY,
                SleepSummaryDataFields.TIME_AWAKE_DURING_SLEEP,
                SleepSummaryDataFields.APNEA_HYPOPNEA_INDEX,
                SleepSummaryDataFields.BREATHING_DISTURBANCES_INTENSITY,
                SleepSummaryDataFields.EXTERNAL_TOTAL_SLEEP_TIME,
                SleepSummaryDataFields.DEEP_SLEEP_DURATION,
                SleepSummaryDataFields.AVERAGE_HEART_RATE,
                SleepSummaryDataFields.MIN_HEART_RATE,
                SleepSummaryDataFields.MAX_HEART_RATE,
                SleepSummaryDataFields.LIGHT_SLEEP_DURATION,
                SleepSummaryDataFields.ACTIVE_MOVEMENT_DURATION,
                SleepSummaryDataFields.AVERAGE_MOVEMENT_SCORE,
                SleepSummaryDataFields.NIGHT_EVENTS,
                SleepSummaryDataFields.OUT_OF_BED_COUNT,
                SleepSummaryDataFields.REM_SLEEP_DURATION,
                SleepSummaryDataFields.AVERAGE_RESPIRATION_RATE,
                SleepSummaryDataFields.MIN_RESPIRATION_RATE,
                SleepSummaryDataFields.MAX_RESPIRATION_RATE,
                SleepSummaryDataFields.SLEEP_SCORE,
                SleepSummaryDataFields.SNORING,
                SleepSummaryDataFields.SNORING_COUNT,
                SleepSummaryDataFields.WAKE_UP_COUNT,
                SleepSummaryDataFields.TOTAL_TIME_AWAKE,
                SleepSummaryDataFields.WITHINGS_INDEX,
            ],
        )
        assert len(response) == 300
        await withings.close()


async def test_get_sleep_summary_since_without_data_fields(
    aresponses: ResponsesMockServer,
) -> None:
    """Test retrieving sleep without datafields."""
    aresponses.add(
        WITHINGS_URL,
        "/v2/sleep",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("sleep_summary_no_datafields.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        response = await withings.get_sleep_summary_since(
            datetime.fromtimestamp(0, tz=timezone.utc),
        )
        assert len(response) == 300
        await withings.close()
