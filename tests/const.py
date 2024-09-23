"""Constants for tests."""

from importlib import metadata

WITHINGS_URL = "https://wbsapi.withings.net"

version = metadata.version("aiowithings")

HEADERS = {
    "User-Agent": f"AioWithings/{version}",
    "Accept": "application/json, text/plain, */*",
    "Authorization": "Bearer test",
}
