"""Asynchronous Python client for Withings."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from importlib import metadata
from typing import TYPE_CHECKING, Any, cast

from aiohttp import ClientSession
from aiohttp.hdrs import METH_POST
import async_timeout
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
from .models import Device, Goals, MeasurementGroup, MeasurementType

if TYPE_CHECKING:
    from datetime import datetime

    from typing_extensions import Self


@dataclass
class WithingsClient:
    """Main class for handling connections with Withings."""

    session: ClientSession | None = None
    request_timeout: int = 10
    api_host: str = "wbsapi.withings.net"
    _token: str | None = None
    _close_session: bool = False

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
        version = metadata.version(__package__)
        url = URL.build(
            scheme="https",
            host=self.api_host,
            port=443,
        ).joinpath(uri)

        headers = {
            "User-Agent": f"AioWithings/{version}",
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {self._token}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
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
        if response_status in STATUS_AUTH_FAILED:
            raise WithingsAuthenticationFailedError
        if response_status in STATUS_INVALID_PARAMS:
            raise WithingsInvalidParamsError
        if response_status in STATUS_UNAUTHORIZED:
            raise WithingsUnauthorizedError
        if response_status in STATUS_ERROR_OCCURRED:
            raise WithingsErrorOccurredError
        if response_status in STATUS_TIMEOUT:
            raise WithingsConnectionError
        if response_status in STATUS_BAD_STATE:
            raise WithingsBadStateError
        if response_status in STATUS_TOO_MANY_REQUESTS:
            raise WithingsTooManyRequestsError
        raise WithingsUnknownStatusError

    async def get_devices(self) -> list[Device]:
        """Get devices."""
        response = await self._request("v2/user", data={"action": "getdevice"})
        return [Device.from_api(device) for device in response["devices"]]

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
            {"lastupdate": measurement_since.timestamp()},
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
            {"startdate": start_date.timestamp(), "enddate": end_date.timestamp()},
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
