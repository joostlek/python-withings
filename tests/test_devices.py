"""Asynchronous Python client for Withings."""

import aiohttp
from aresponses import ResponsesMockServer
import pytest

from aiowithings import WithingsClient
from syrupy import SnapshotAssertion

from . import load_fixture

WITHINGS_URL = "wbsapi.withings.net"


async def test_get_devices(
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
            text=load_fixture("device.json"),
        ),
        body_pattern="action=getdevice",
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        response = await withings.get_devices()
        assert response == snapshot
        await withings.close()


async def test_get_new_device(
    aresponses: ResponsesMockServer,
    caplog: pytest.LogCaptureFixture,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving devices that aren't known yet."""
    aresponses.add(
        WITHINGS_URL,
        "/v2/user",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("new_device.json"),
        ),
        body_pattern="action=getdevice",
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        response = await withings.get_devices()
        assert response == snapshot
        assert (
            "Futuristic device is an unsupported value for <enum 'DeviceType'>,"
            " please report this at https://github.com/joostlek/python-withings/issues"
            in caplog.text
        )
        assert (
            "696969 is an unsupported value for <enum 'DeviceModel'>, please report"
            " this at https://github.com/joostlek/python-withings/issues" in caplog.text
        )
        await withings.close()
