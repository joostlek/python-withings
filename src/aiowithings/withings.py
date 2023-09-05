"""Asynchronous Python client for Withings."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from importlib import metadata
from typing import TYPE_CHECKING, Any, cast

import async_timeout
from aiohttp import ClientSession
from aiohttp.hdrs import METH_POST
from yarl import URL

from .exceptions import (
    WithingsConnectionError,
    WithingsError,
)
from .models import Device, Goals

if TYPE_CHECKING:
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

        return cast(dict[str, Any], await response.json())

    async def get_devices(self) -> list[Device]:
        """Get devices."""
        response = await self._request("v2/user", data={"action": "getdevice"})
        return [Device.from_api(device) for device in response["body"]["devices"]]

    async def get_goals(self) -> Goals:
        """Get goals."""
        response = await self._request("v2/user", data={"action": "getgoals"})
        return Goals.from_api(response["body"]["goals"])

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
