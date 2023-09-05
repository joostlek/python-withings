"""Asynchronous Python client for Withings."""


class WithingsError(Exception):
    """Generic exception."""


class WithingsConnectionError(WithingsError):
    """Withings connection exception."""


class WithingsAuthenticationError(WithingsError):
    """Withings authentication exception."""
