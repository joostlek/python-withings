"""Asynchronous Python client for Withings."""


class WithingsError(Exception):
    """Generic exception."""


class WithingsConnectionError(WithingsError):
    """Withings connection exception."""


class WithingsAuthenticationFailedError(WithingsError):
    """Withings authentication failed exception."""


class WithingsInvalidParamsError(WithingsError):
    """Withings invalid params exception."""


class WithingsUnauthorizedError(WithingsError):
    """Withings unauthorized exception."""


class WithingsErrorOccurredError(WithingsError):
    """Withings error occurred exception."""


class WithingsBadStateError(WithingsError):
    """Withings bad state exception."""


class WithingsTooManyRequestsError(WithingsError):
    """Withings too many requests exception."""


class WithingsUnknownStatusError(WithingsError):
    """Withings unknown status exception."""
