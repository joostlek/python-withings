"""Asynchronous Python client for Withings."""
from __future__ import annotations

from typing import Any, TypeVar

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
