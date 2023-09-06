"""Asynchronous Python client for Withings."""
from __future__ import annotations

import asyncio
import json

import aiohttp
from aiohttp.web_request import BaseRequest
from aresponses import Response, ResponsesMockServer
import pytest

from aiowithings import (
    WithingsAuthenticationFailedError,
    WithingsBadStateError,
    WithingsClient,
    WithingsConnectionError,
    WithingsError,
    WithingsErrorOccurredError,
    WithingsInvalidParamsError,
    WithingsTooManyRequestsError,
    WithingsUnauthorizedError,
    WithingsUnknownStatusError,
)

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


@pytest.mark.parametrize(
    ("status", "error"),
    [
        (100, WithingsAuthenticationFailedError),
        (201, WithingsInvalidParamsError),
        (214, WithingsUnauthorizedError),
        (215, WithingsErrorOccurredError),
        (522, WithingsConnectionError),
        (524, WithingsBadStateError),
        (601, WithingsTooManyRequestsError),
        (-1, WithingsUnknownStatusError),
        (None, WithingsUnknownStatusError),
    ],
)
async def test_error_codes(
    aresponses: ResponsesMockServer,
    status: int | None,
    error: type[Exception],
) -> None:
    """Test error codes from withings."""
    response_data = json.loads(load_fixture("device.json"))
    response_data["status"] = status

    aresponses.add(
        WITHINGS_URL,
        "/v2/user",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=json.dumps(response_data),
        ),
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        with pytest.raises(error):
            assert await withings.get_devices()
        await withings.close()
