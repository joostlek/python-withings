"""Asynchronous Python client for Withings."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

import aiohttp
from aiohttp.hdrs import METH_POST
from aioresponses import aioresponses, CallbackResult
import pytest
from syrupy import SnapshotAssertion

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
    WithingsUnknownStatusError, ActivityDataFields,
)

from . import load_fixture
from .const import HEADERS, WITHINGS_URL


async def test_putting_in_own_session(
    responses: aioresponses,
) -> None:
    """Test putting in own session."""
    responses.post(
        f"{WITHINGS_URL}/v2/user",
        status=200,
        body=load_fixture("device.json"),
    )
    async with aiohttp.ClientSession() as session:
        withings = WithingsClient(session=session)
        withings.authenticate("test")
        await withings.get_devices()
        assert withings.session is not None
        assert not withings.session.closed
        await withings.close()
        assert not withings.session.closed


async def test_creating_own_session(
    responses: aioresponses,
) -> None:
    """Test creating own session."""
    responses.post(
        f"{WITHINGS_URL}/v2/user",
        status=200,
        body=load_fixture("device.json"),
    )
    withings = WithingsClient()
    withings.authenticate("test")
    await withings.get_devices()
    assert withings.session is not None
    assert not withings.session.closed
    await withings.close()
    assert withings.session.closed


async def test_refresh_token() -> None:
    """Test refreshing token."""

    async def _get_token() -> str:
        return "token"

    async with WithingsClient() as withings:
        assert withings._token is None  # pylint: disable=protected-access
        await withings.refresh_token()
        assert withings._token is None  # pylint: disable=protected-access

        withings.refresh_token_function = _get_token
        await withings.refresh_token()

        assert withings._token == "token"  # pylint: disable=protected-access




async def test_unexpected_server_response(
    responses: aioresponses,
    authenticated_client: WithingsClient,
) -> None:
    """Test handling unexpected response."""
    responses.post(
        f"{WITHINGS_URL}/v2/user",
        status=200,
        headers={"Content-Type": "plain/text"},
        body="Yes",
    )
    with pytest.raises(WithingsError):
        assert await authenticated_client.get_devices()


async def test_timeout(
    responses: aioresponses,
) -> None:
    """Test request timeout."""

    # Faking a timeout by sleeping
    async def response_handler(_: str, **_kwargs: Any) -> CallbackResult:
        """Response handler for this test."""
        await asyncio.sleep(2)
        return CallbackResult(body="Goodmorning!")

    responses.post(
        f"{WITHINGS_URL}/v2/user",
        callback=response_handler,
    )
    async with WithingsClient(request_timeout=1) as withings:
        with pytest.raises(WithingsConnectionError):
            assert await withings.get_devices()


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
    responses: aioresponses,
    authenticated_client: WithingsClient,
    status: int | None,
    error: type[Exception],
) -> None:
    """Test error codes from withings."""
    response_data = json.loads(load_fixture("device.json"))
    response_data["status"] = status

    responses.post(
        f"{WITHINGS_URL}/v2/user",
        status=200,
        body=json.dumps(response_data),
    )
    with pytest.raises(error):
        assert await authenticated_client.get_devices()



async def test_get_activities_since(
    responses: aioresponses,
    snapshot: SnapshotAssertion,
    authenticated_client: WithingsClient,
) -> None:
    """Test retrieving activities."""
    responses.post(
        f"{WITHINGS_URL}/v2/measure",
        status=200,
        body=load_fixture("activity.json"),
    )
    response = await authenticated_client.get_activities_since(
        datetime.fromtimestamp(1609559200, tz=timezone.utc),
        activity_data_fields=[ActivityDataFields.DISTANCE],
    )
    assert response == snapshot
    responses.assert_called_once_with(
        f"{WITHINGS_URL}/v2/measure",
        METH_POST,
        headers=HEADERS,
        data={"lastupdate": 1609559200, "action": "getactivity", "data_fields": "distance"},
    )


async def test_get_activities_period(
    responses: aioresponses,
    snapshot: SnapshotAssertion,
    authenticated_client: WithingsClient,
) -> None:
    """Test retrieving activities."""
    responses.post(
        f"{WITHINGS_URL}/v2/measure",
        status=200,
        body=load_fixture("activity.json"),
    )
    response = await authenticated_client.get_activities_in_period(
        start_date=datetime.fromtimestamp(1609459200, tz=timezone.utc),
        end_date=datetime.fromtimestamp(1609559200, tz=timezone.utc),
    )
    assert response == snapshot
    responses.assert_called_once_with(
        f"{WITHINGS_URL}/v2/measure",
        METH_POST,
        headers=HEADERS,
        data={"action": "getactivity", "startdateymd": "2021-01-01 00:00:00+00:00", "enddateymd": "2021-01-02 03:46:40+00:00"},
    )
