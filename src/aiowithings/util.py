"""Asynchronous Python client for Withings."""
from __future__ import annotations

from enum import Enum
from typing import Any, TypeVar, cast

from aiowithings.const import LOGGER

T = TypeVar("T", bound=Enum)


def to_enum(
    enum_class: type[T],
    value: Any,
    default_value: T,
) -> T:
    """Convert a value to an enum and log if it doesn't exist."""
    try:
        return enum_class(value)
    except ValueError:
        LOGGER.warning(
            "%s is an unsupported value for %s, please report this at https://github.com/joostlek/python-withings/issues",
            value,
            str(enum_class),
        )
        return default_value


def to_enum_or_none(
    enum_class: type[T],
    value: Any,
) -> T | None:
    """Convert a value to an enum or None if it fails."""
    try:
        return enum_class(value)
    except ValueError:
        return None


def get_measurement(value: int, unit: int) -> float:
    """Convert value and unit to real value."""
    return cast(float, value * pow(10, unit))


def get_measurement_from_dict(input_dict: dict[str, Any]) -> float:
    """Convert dict with value and unit to real value."""
    value = cast(int, input_dict["value"])
    unit = cast(int, input_dict["unit"])
    return get_measurement(value, unit)
