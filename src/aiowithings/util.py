"""Asynchronous Python client for Withings."""

from __future__ import annotations

from typing import Any, TypeVar, cast

from aiowithings.const import LOGGER

_EnumT = TypeVar("_EnumT")


def to_enum(
    enum_class: type[_EnumT],
    value: Any,
    default_value: _EnumT,
) -> _EnumT:
    """Convert a value to an enum and log if it doesn't exist."""
    try:
        return enum_class(value)  # type: ignore[call-arg]
    except ValueError:
        LOGGER.warning(
            "%s is an unsupported value for %s, please report this at https://github.com/joostlek/python-withings/issues",
            value,
            str(enum_class),
        )
        return default_value


def get_measurement(value: int, unit: int) -> float:
    """Convert value and unit to real value."""
    return cast(float, value * pow(10, unit))


def get_measurement_from_dict(input_dict: dict[str, Any]) -> float:
    """Convert dict with value and unit to real value."""
    value = cast(int, input_dict["value"])
    unit = cast(int, input_dict["unit"])
    return get_measurement(value, unit)
