"""Asynchronous Python client for Withings."""

import enum
import logging

import pytest

from aiowithings.util import (
    _LOGGED_UNSUPPORTED_VALUES,
    get_measurement,
    get_measurement_from_dict,
    to_enum,
)


def test_measurement() -> None:
    """Test measurement."""
    assert get_measurement(20, -1) == 2


def test_measurement_from_dict() -> None:
    """Test measurement."""
    assert get_measurement_from_dict({"value": 20, "unit": -1}) == 2


class _Color(enum.IntEnum):
    """A throwaway enum, isolated from the library's real ones.

    Reusing a real enum (e.g. DeviceModel) would share the module-level
    dedup set across tests and across the library's own real usage,
    exactly the "shared mutable fixture" bug the project's own contribution
    notes warn about (a fixture/state one test populates silently changes
    the result of another).
    """

    RED = 1
    GREEN = 2


@pytest.fixture(autouse=True)
def _reset_logged_unsupported_values() -> None:
    """Clear the module-level dedup state before every test in this file."""
    _LOGGED_UNSUPPORTED_VALUES.clear()


def test_to_enum_returns_the_matching_member() -> None:
    """The common case: the value is a real member."""
    assert to_enum(_Color, 1, _Color.RED) == _Color.RED


def test_to_enum_falls_back_and_warns_once(caplog: pytest.LogCaptureFixture) -> None:
    """An unsupported value degrades to the default and is reported once."""
    with caplog.at_level(logging.WARNING):
        result = to_enum(_Color, 99, _Color.RED)

    assert result == _Color.RED
    assert len(caplog.records) == 1
    assert "99" in caplog.records[0].message
    assert "_Color" in caplog.records[0].message


def test_to_enum_does_not_repeat_the_same_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The motivating case: a polled attribute stays broken between polls.

    Before this, every poll of an account with one unmapped device or
    attribution logged the same warning again -- one user reported it
    1,250 times in 5 days for a single undocumented value.
    """
    with caplog.at_level(logging.WARNING):
        first = to_enum(_Color, 99, _Color.RED)
        second = to_enum(_Color, 99, _Color.RED)
        third = to_enum(_Color, 99, _Color.RED)

    assert first == second == third == _Color.RED
    assert len(caplog.records) == 1


def test_to_enum_still_warns_for_a_different_unsupported_value(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Dedup is per-value, not "this enum already had a failure"."""
    with caplog.at_level(logging.WARNING):
        to_enum(_Color, 99, _Color.RED)
        to_enum(_Color, 100, _Color.RED)

    assert len(caplog.records) == 2


def test_to_enum_still_warns_for_a_different_enum_with_the_same_value(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Dedup keys on (enum_class, value), not on value alone.

    Two unrelated enums can coincidentally share an undocumented numeric
    value; the second one failing is real information, not a repeat.
    """

    class _Shape(enum.IntEnum):
        CIRCLE = 1

    with caplog.at_level(logging.WARNING):
        to_enum(_Color, 99, _Color.RED)
        to_enum(_Shape, 99, _Shape.CIRCLE)

    assert len(caplog.records) == 2
