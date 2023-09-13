"""Asynchronous Python client for Withings."""
from datetime import datetime, timezone

import aiohttp
from aresponses import ResponsesMockServer
from syrupy import SnapshotAssertion

from aiowithings import WithingsClient
from aiowithings.models import SleepDataFields

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
