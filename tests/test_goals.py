"""Asynchronous Python client for Withings."""

import aiohttp
from aresponses import ResponsesMockServer
import pytest

from aiowithings import WithingsClient
from syrupy import SnapshotAssertion

from . import load_fixture

WITHINGS_URL = "wbsapi.withings.net"


@pytest.mark.parametrize(
    "fixture",
    [
        "goals",
        "goals_1",
        "goals_2",
        "no_goals",
    ],
)
async def test_get_goals(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    fixture: str,
) -> None:
    """Test retrieving devices."""
    aresponses.add(
        WITHINGS_URL,
        "/v2/user",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture(f"{fixture}.json"),
        ),
        body_pattern="action=getgoals",
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        response = await withings.get_goals()
        assert response == snapshot
        await withings.close()
