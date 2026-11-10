"""Tests for paginated activity and workout retrieval."""

from __future__ import annotations

from datetime import UTC, date, datetime
import json
from urllib.parse import parse_qs

from aiohttp.hdrs import METH_POST
from aiointercept import aiointercept
import pytest
from yarl import URL

from aiowithings import (
    ActivityDataFields,
    WithingsClient,
    WithingsTooManyRequestsError,
    WorkoutDataFields,
)

from . import load_fixture
from .const import HEADERS, WITHINGS_URL


async def test_get_activities_since_paginated(
    responses: aiointercept,
    authenticated_client: WithingsClient,
) -> None:
    """Retrieve later activity pages with the original update and field filters."""
    activities = json.loads(load_fixture("activity.json"))["body"]["activities"]
    responses.post(
        f"{WITHINGS_URL}/v2/measure",
        payload={
            "status": 0,
            "body": {"activities": activities[:1], "more": True, "offset": 123},
        },
    )
    responses.post(
        f"{WITHINGS_URL}/v2/measure",
        payload={"status": 0, "body": {"activities": activities[1:], "more": False}},
    )

    response = await authenticated_client.get_activities_since(
        datetime.fromtimestamp(1609459200, tz=UTC),
        activity_data_fields=[ActivityDataFields.DISTANCE],
    )

    assert [activity.date for activity in response] == [
        date(2023, 10, 20),
        date(2023, 10, 21),
    ]
    assert responses.call_count == 2
    responses.assert_called_with(
        f"{WITHINGS_URL}/v2/measure",
        METH_POST,
        headers=HEADERS,
        data={
            "action": "getactivity",
            "lastupdate": 1609459200,
            "data_fields": "distance",
            "offset": 123,
        },
    )


async def test_get_activities_period_paginated(
    responses: aiointercept,
    authenticated_client: WithingsClient,
) -> None:
    """Preserve the requested activity date range across pages."""
    activities = json.loads(load_fixture("activity.json"))["body"]["activities"]
    responses.post(
        f"{WITHINGS_URL}/v2/measure",
        payload={
            "status": 0,
            "body": {"activities": activities[:1], "more": True, "offset": 123},
        },
    )
    responses.post(
        f"{WITHINGS_URL}/v2/measure",
        payload={"status": 0, "body": {"activities": activities[1:], "more": False}},
    )

    response = await authenticated_client.get_activities_in_period(
        start_date=date(2023, 10, 20),
        end_date=date(2023, 10, 21),
    )

    assert [activity.date for activity in response] == [
        date(2023, 10, 20),
        date(2023, 10, 21),
    ]
    assert responses.call_count == 2
    responses.assert_called_with(
        f"{WITHINGS_URL}/v2/measure",
        METH_POST,
        headers=HEADERS,
        data={
            "action": "getactivity",
            "startdateymd": "2023-10-20",
            "enddateymd": "2023-10-21",
            "offset": 123,
        },
    )


async def test_get_workouts_since_paginated(
    responses: aiointercept,
    authenticated_client: WithingsClient,
) -> None:
    """Follow successive workout offsets while preserving the original filters."""
    workouts = json.loads(load_fixture("workouts.json"))["body"]["series"][:3]
    for page, more, offset in (
        (workouts[:1], True, 123),
        (workouts[1:2], True, 456),
        (workouts[2:], False, 0),
    ):
        responses.post(
            f"{WITHINGS_URL}/v2/measure",
            payload={
                "status": 0,
                "body": {"series": page, "more": more, "offset": offset},
            },
        )

    response = await authenticated_client.get_workouts_since(
        datetime.fromtimestamp(1609459200, tz=UTC),
        workout_data_fields=[WorkoutDataFields.CALORIES],
    )

    assert [workout.workout_id for workout in response] == [
        3661300277,
        3661300290,
        3661300269,
    ]
    assert responses.call_count == 3
    filters = {
        "action": ["getworkouts"],
        "lastupdate": ["1609459200"],
        "data_fields": ["calories"],
    }
    for request, expected_data in zip(
        responses.requests[(METH_POST, URL(f"{WITHINGS_URL}/v2/measure"))],
        [filters, {**filters, "offset": ["123"]}, {**filters, "offset": ["456"]}],
        strict=True,
    ):
        assert request.captured_body is not None
        assert parse_qs(request.captured_body.decode()) == expected_data


async def test_get_workouts_period_paginated(
    responses: aiointercept,
    authenticated_client: WithingsClient,
) -> None:
    """Preserve the requested workout date range across pages."""
    workouts = json.loads(load_fixture("workouts.json"))["body"]["series"][:2]
    responses.post(
        f"{WITHINGS_URL}/v2/measure",
        payload={
            "status": 0,
            "body": {"series": workouts[:1], "more": True, "offset": 123},
        },
    )
    responses.post(
        f"{WITHINGS_URL}/v2/measure",
        payload={"status": 0, "body": {"series": workouts[1:], "more": False}},
    )

    response = await authenticated_client.get_workouts_in_period(
        start_date=date(2023, 8, 1),
        end_date=date(2023, 8, 31),
    )

    assert [workout.workout_id for workout in response] == [3661300277, 3661300290]
    assert responses.call_count == 2
    responses.assert_called_with(
        f"{WITHINGS_URL}/v2/measure",
        METH_POST,
        headers=HEADERS,
        data={
            "action": "getworkouts",
            "startdateymd": "2023-08-01",
            "enddateymd": "2023-08-31",
            "offset": 123,
        },
    )


@pytest.mark.parametrize(
    ("method", "fixture", "key"),
    [
        ("get_activities_since", "activity.json", "activities"),
        ("get_workouts_since", "workouts.json", "series"),
    ],
)
async def test_pagination_error(
    responses: aiointercept,
    authenticated_client: WithingsClient,
    method: str,
    fixture: str,
    key: str,
) -> None:
    """Raise later-page API errors instead of returning incomplete results."""
    entries = json.loads(load_fixture(fixture))["body"][key][:1]
    responses.post(
        f"{WITHINGS_URL}/v2/measure",
        payload={"status": 0, "body": {key: entries, "more": True, "offset": 123}},
    )
    responses.post(
        f"{WITHINGS_URL}/v2/measure",
        payload={"status": 601, "error": "Too many requests"},
    )

    with pytest.raises(WithingsTooManyRequestsError):
        await getattr(authenticated_client, method)(
            datetime.fromtimestamp(1609459200, tz=UTC),
        )

    assert responses.call_count == 2
