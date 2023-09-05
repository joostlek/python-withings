"""Asynchronous Python client for Withings."""
import asyncio

import aiohttp
import pytest
from aiohttp.web_request import BaseRequest
from aresponses import Response, ResponsesMockServer

from aiowithings import WithingsClient, WithingsConnectionError, WithingsError

from . import load_fixture

WITHINGS_URL = "wbsapi.withings.net"


async def test_own_session(
    aresponses: ResponsesMockServer,
) -> None:
    """Test creating own session."""
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
    async with WithingsClient() as withings:
        withings.authenticate("test")
        await withings.get_devices()
        assert withings.session is not None


async def test_unexpected_server_response(
    aresponses: ResponsesMockServer,
) -> None:
    """Test handling unexpected response."""
    aresponses.add(
        WITHINGS_URL,
        "/v2/user",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "plain/text"},
            text="Yes",
        ),
    )
    async with WithingsClient() as withings:
        withings.authenticate("test")
        with pytest.raises(WithingsError):
            assert await withings.get_devices()


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout."""

    # Faking a timeout by sleeping
    async def response_handler(_: BaseRequest) -> Response:
        """Response handler for this test."""
        await asyncio.sleep(2)
        return aresponses.Response(body="Goodmorning!")

    aresponses.add(
        WITHINGS_URL,
        "/v2/user",
        "POST",
        response_handler,
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session, request_timeout=1)
        withings.authenticate("test")
        with pytest.raises(WithingsConnectionError):
            assert await withings.get_devices()
        await withings.close()
