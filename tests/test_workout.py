"""Asynchronous Python client for Withings."""
from datetime import datetime, timezone

import aiohttp
from aresponses import ResponsesMockServer

from aiowithings import WithingsClient
from aiowithings.models import WorkoutDataFields
from syrupy import SnapshotAssertion

from . import load_fixture

WITHINGS_URL = "wbsapi.withings.net"


async def test_get_workouts_since(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving workouts."""
    aresponses.add(
        WITHINGS_URL,
        "/v2/measure",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("workouts.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        response = await withings.get_workouts_since(
            datetime.now(tz=timezone.utc),
            workout_data_fields=[WorkoutDataFields.CALORIES],
        )
        assert response == snapshot
        await withings.close()


async def test_get_workouts_period(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving workouts."""
    aresponses.add(
        WITHINGS_URL,
        "/v2/measure",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("workouts.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        response = await withings.get_workouts_in_period(
            start_date=datetime.now(tz=timezone.utc),
            end_date=datetime.now(tz=timezone.utc),
        )
        assert response == snapshot
        await withings.close()
