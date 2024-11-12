"""Asynchronous Python client for Withings."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from importlib import metadata
from typing import TYPE_CHECKING, Any, Awaitable, Callable, cast

from aiohttp import ClientSession
from aiohttp.hdrs import METH_POST
from yarl import URL

from .const import (
    STATUS_AUTH_FAILED,
    STATUS_BAD_STATE,
    STATUS_ERROR_OCCURRED,
    STATUS_INVALID_PARAMS,
    STATUS_SUCCESS,
    STATUS_TIMEOUT,
    STATUS_TOO_MANY_REQUESTS,
    STATUS_UNAUTHORIZED,
)
from .exceptions import (
    WithingsAuthenticationFailedError,
    WithingsBadStateError,
    WithingsConnectionError,
    WithingsError,
    WithingsErrorOccurredError,
    WithingsInvalidParamsError,
    WithingsTooManyRequestsError,
    WithingsUnauthorizedError,
    WithingsUnknownStatusError,
)
from .models import (
    Activity,
    ActivityDataFields,
    Device,
    Goals,
    MeasurementGroup,
    MeasurementType,
    NotificationCategory,
    NotificationConfiguration,
    SleepDataFields,
    SleepSeries,
    SleepSummary,
    SleepSummaryDataFields,
    Workout,
    WorkoutDataFields,
)

if TYPE_CHECKING:
    from datetime import date, datetime

    from typing_extensions import Self


VERSION = metadata.version(__package__)


@dataclass
class WithingsClient:
    """Main class for handling connections with Withings."""

    session: ClientSession | None = None
    request_timeout: int = 10
    api_host: str = "wbsapi.withings.net"
    _token: str | None = None
    _close_session: bool = False
    refresh_token_function: Callable[[], Awaitable[str]] | None = None

    async def refresh_token(self) -> None:
        """Refresh token with provided function."""
        if self.refresh_token_function:
            self._token = await self.refresh_token_function()

    def authenticate(self, token: str) -> None:
        """Authenticate the user with a token."""
        self._token = token

    async def _request(
        self,
        uri: str,
        *,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Handle a request to Withings."""
        url = URL.build(
            scheme="https",
            host=self.api_host,
            port=443,
        ).joinpath(uri)

        await self.refresh_token()

        headers = {
            "User-Agent": f"AioWithings/{VERSION}",
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {self._token}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    METH_POST,
                    url,
                    headers=headers,
                    data=data,
                )
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to Withings"
            raise WithingsConnectionError(msg) from exception

        content_type = response.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            text = await response.text()
            msg = "Unexpected response from Withings"
            raise WithingsError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        response_data = cast(dict[str, Any], await response.json())
        response_status = response_data.get("status", -1)
        if response_status in STATUS_SUCCESS:
            return cast(dict[str, Any], response_data.get("body"))
        error = response_data.get("error")
        if response_status in STATUS_AUTH_FAILED:
            raise WithingsAuthenticationFailedError(error)
        if response_status in STATUS_INVALID_PARAMS:
            raise WithingsInvalidParamsError(error)
        if response_status in STATUS_UNAUTHORIZED:
            raise WithingsUnauthorizedError(error)
        if response_status in STATUS_ERROR_OCCURRED:
            raise WithingsErrorOccurredError(error)
        if response_status in STATUS_TIMEOUT:
            raise WithingsConnectionError(error)
        if response_status in STATUS_BAD_STATE:
            raise WithingsBadStateError(error)
        if response_status in STATUS_TOO_MANY_REQUESTS:
            raise WithingsTooManyRequestsError(error)
        raise WithingsUnknownStatusError(error)

    async def get_devices(self) -> list[Device]:
        """Get devices."""
        response = await self._request("v2/user", data={"action": "getdevice"})
        return [
            Device.from_api(device)
            for device in response["devices"]
            if device["model"] != "Aura Sensor V2"
        ]

    async def get_goals(self) -> Goals:
        """Get goals."""
        response = await self._request("v2/user", data={"action": "getgoals"})
        return Goals.from_api(response["goals"])

    async def _get_measurements(
        self,
        measurement_types: list[MeasurementType] | None,
        base_data: dict[str, Any],
    ) -> list[MeasurementGroup]:
        data = {**base_data, "action": "getmeas"}
        if measurement_types is not None:
            data["meastypes"] = ",".join(
                [str(measurement_type) for measurement_type in measurement_types],
            )
        response = await self._request("measure", data=data)
        return [
            MeasurementGroup.from_api(measurement_group)
            for measurement_group in response["measuregrps"]
        ]

    async def get_measurement_since(
        self,
        measurement_since: datetime,
        measurement_types: list[MeasurementType] | None = None,
    ) -> list[MeasurementGroup]:
        """Get all measurements since measurement_since."""
        return await self._get_measurements(
            measurement_types,
            {"lastupdate": int(measurement_since.timestamp())},
        )

    async def get_measurement_in_period(
        self,
        start_date: datetime,
        end_date: datetime,
        measurement_types: list[MeasurementType] | None = None,
    ) -> list[MeasurementGroup]:
        """Get all measurements measured since start date and until end date."""
        return await self._get_measurements(
            measurement_types,
            {
                "startdate": int(start_date.timestamp()),
                "enddate": int(end_date.timestamp()),
            },
        )

    async def get_sleep(
        self,
        start_date: datetime,
        end_date: datetime,
        data_fields: list[SleepDataFields] | None = None,
    ) -> list[SleepSeries]:
        """Get sleep."""
        data = {
            "action": "get",
            "startdate": int(start_date.timestamp()),
            "enddate": int(end_date.timestamp()),
        }
        if data_fields is not None:
            data["data_fields"] = ",".join(
                [str(sleep_data_field) for sleep_data_field in data_fields],
            )
        response = await self._request(
            "v2/sleep",
            data=data,
        )
        return [SleepSeries.from_api(sleep) for sleep in response["series"]]

    async def _get_sleep_summary(
        self,
        sleep_summary_data_fields: list[SleepSummaryDataFields] | None,
        base_data: dict[str, Any],
    ) -> list[SleepSummary]:
        data = {**base_data, "action": "getsummary"}
        if sleep_summary_data_fields is not None:
            data["data_fields"] = ",".join(
                [
                    str(sleep_data_field)
                    for sleep_data_field in sleep_summary_data_fields
                ],
            )
        response = await self._request(
            "v2/sleep",
            data=data,
        )
        return [SleepSummary.from_api(sleep) for sleep in response["series"]]

    async def get_sleep_summary_since(
        self,
        sleep_summary_since: datetime,
        sleep_summary_data_fields: list[SleepSummaryDataFields] | None = None,
    ) -> list[SleepSummary]:
        """Get all sleep summaries since sleep_summary_since."""
        return await self._get_sleep_summary(
            sleep_summary_data_fields,
            {"lastupdate": int(sleep_summary_since.timestamp())},
        )

    async def get_sleep_summary_in_period(
        self,
        start_date: date,
        end_date: date,
        sleep_summary_data_fields: list[SleepSummaryDataFields] | None = None,
    ) -> list[SleepSummary]:
        """Get sleep summary during period."""
        return await self._get_sleep_summary(
            sleep_summary_data_fields,
            {"startdateymd": str(start_date), "enddateymd": str(end_date)},
        )

    async def _get_activities(
        self,
        activity_data_fields: list[ActivityDataFields] | None,
        base_data: dict[str, Any],
    ) -> list[Activity]:
        data = {**base_data, "action": "getactivity"}
        if activity_data_fields is not None:
            data["data_fields"] = ",".join(
                [
                    str(activity_data_field)
                    for activity_data_field in activity_data_fields
                ],
            )
        response = await self._request(
            "v2/measure",
            data=data,
        )
        return [Activity.from_api(activity) for activity in response["activities"]]

    async def get_activities_since(
        self,
        activities_since: datetime,
        activity_data_fields: list[ActivityDataFields] | None = None,
    ) -> list[Activity]:
        """Get activities since activities_since."""
        return await self._get_activities(
            activity_data_fields,
            {"lastupdate": int(activities_since.timestamp())},
        )

    async def get_activities_in_period(
        self,
        start_date: date,
        end_date: date,
        activity_data_fields: list[ActivityDataFields] | None = None,
    ) -> list[Activity]:
        """Get activities during period."""
        return await self._get_activities(
            activity_data_fields,
            {"startdateymd": str(start_date), "enddateymd": str(end_date)},
        )

    async def _get_workouts(
        self,
        workout_data_fields: list[WorkoutDataFields] | None,
        base_data: dict[str, Any],
    ) -> list[Workout]:
        data = {**base_data, "action": "getworkouts"}
        if workout_data_fields is not None:
            data["data_fields"] = ",".join(
                [str(workout_data_field) for workout_data_field in workout_data_fields],
            )
        response = await self._request(
            "v2/measure",
            data=data,
        )
        return [Workout.from_api(workout) for workout in response["series"]]

    async def get_workouts_since(
        self,
        workouts_since: datetime,
        workout_data_fields: list[WorkoutDataFields] | None = None,
    ) -> list[Workout]:
        """Get workouts since workouts_since."""
        return await self._get_workouts(
            workout_data_fields,
            {"lastupdate": int(workouts_since.timestamp())},
        )

    async def get_workouts_in_period(
        self,
        start_date: date,
        end_date: date,
        workout_data_fields: list[WorkoutDataFields] | None = None,
    ) -> list[Workout]:
        """Get workouts during period."""
        return await self._get_workouts(
            workout_data_fields,
            {"startdateymd": str(start_date), "enddateymd": str(end_date)},
        )

    async def subscribe_notification(
        self,
        callback_url: str,
        notification_category: NotificationCategory,
    ) -> None:
        """Subscribe the callback_url for webhook updates."""
        await self._request(
            "notify",
            data={
                "action": "subscribe",
                "callbackurl": callback_url,
                "appli": notification_category,
            },
        )

    async def list_notification_configurations(
        self,
        notification_category: NotificationCategory | None = None,
    ) -> list[NotificationConfiguration]:
        """Subscribe the callback_url for webhook updates."""
        request_data: dict[str, Any] = {
            "action": "list",
        }
        if notification_category:
            request_data["appli"] = notification_category
        response = await self._request(
            "notify",
            data=request_data,
        )
        return [
            NotificationConfiguration.from_api(config)
            for config in response["profiles"]
        ]

    async def revoke_notification_configurations(
        self,
        callback_url: str,
        notification_category: NotificationCategory,
    ) -> None:
        """Revoke the configuration for webhook updates."""
        await self._request(
            "notify",
            data={
                "action": "revoke",
                "callbackurl": callback_url,
                "appli": notification_category,
            },
        )

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The WithingsClient object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
