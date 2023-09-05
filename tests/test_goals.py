"""Asynchronous Python client for Withings."""

import aiohttp
from aresponses import ResponsesMockServer
from syrupy import SnapshotAssertion

from aiowithings import (
    WithingsClient,
)

from . import load_fixture

WITHINGS_URL = "wbsapi.withings.net"


async def test_get_goals(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving devices."""
    aresponses.add(
        WITHINGS_URL,
        "/v2/user",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("goals.json"),
        ),
        body_pattern="action=getgoals",
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        response = await withings.get_goals()
        assert response == snapshot
        await withings.close()
