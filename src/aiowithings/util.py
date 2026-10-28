"""Asynchronous Python client for Withings."""

from __future__ import annotations

from typing import Any, cast

from aiowithings.const import LOGGER

_LOGGED_UNSUPPORTED_VALUES: set[tuple[type[Any], Any]] = set()


def to_enum[EnumT](
    enum_class: type[EnumT],
    value: Any,
    default_value: EnumT,
) -> EnumT:
    """Convert a value to an enum and log if it doesn't exist.

    Logged once per distinct (enum, value) pair for the life of the
    process, not on every call. A polled account with one unmapped device
    or attribution otherwise repeats the identical warning on every poll --
    reported as 1,250 occurrences in 5 days for a single undocumented
    value (joostlek/python-withings#86). The API returns a small, bounded
    set of distinct codes, so this does not grow unbounded in practice.
    """
    try:
        return enum_class(value)  # type: ignore[call-arg]
    except ValueError:
        key = (enum_class, value)
        if key not in _LOGGED_UNSUPPORTED_VALUES:
            _LOGGED_UNSUPPORTED_VALUES.add(key)
            LOGGER.warning(
                "%s is an unsupported value for %s, please report this at https://github.com/joostlek/python-withings/issues",
                value,
                str(enum_class),
            )
        return default_value


def get_measurement(value: int, unit: int) -> float:
    """Convert value and unit to real value."""
    return cast("float", value * pow(10, unit))


def get_measurement_from_dict(input_dict: dict[str, Any]) -> float:
    """Convert dict with value and unit to real value."""
    value = cast("int", input_dict["value"])
    unit = cast("int", input_dict["unit"])
    return get_measurement(value, unit)
