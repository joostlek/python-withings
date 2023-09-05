"""Asynchronous Python client for Withings."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import IntEnum, StrEnum
from typing import Any, Self

from aiowithings.util import get_measurement_from_dict, to_enum


class DeviceModel(IntEnum):
    """Enum with device models."""

    UNKNOWN = 0
    WBS01 = 1
    WS30 = 2
    KID_SCALE = 3
    SMART_BODY_ANALYZER = 4
    BODY_PLUS = 5
    BODY_CARDIO = 6
    BODY = 7
    BODY_SCAN = 10
    BODY_PRO = 9
    WBS10 = 11
    WBS11 = 12
    SMART_BABY_MONITOR = 21
    WITHINGS_HOME = 22
    WITHINGS_BLOOD_PRESSURE_MONITOR_V1 = 41
    WITHINGS_BLOOD_PRESSURE_MONITOR_V2 = 42
    WITHINGS_BLOOD_PRESSURE_MONITOR_V3 = 43
    BPM_CORE = 44
    BPM_CONNECT = 45
    BPM_CONNECT_PRO = 46
    PULSE = 51
    ACTIVITE = 52
    ACTIVITE_POP_STEEL = 53
    WITHINGS_GO = 54
    ACITIVTE_STEEL_HR = 55
    ACTIVITE_STEEL_HR_SPORT_EDITION = 59
    PULSE_HR = 58
    MOVE = 90
    MOVE_ECG_1 = 91
    MOVE_ECG_2 = 92
    SCANWATCH = 93
    AURA_DOCK = 60
    AURA_SENSOR = 61
    AURA_SENSOR_V2 = 63
    THERMO = 70
    WUP01 = 100
    IGLUCOSE_GLUCOMETER = 1061
    IOS_STEP_TRACKER_1 = 1051
    IOS_STEP_TRACKER_2 = 1052
    HEALTHKIT_STEP_IPHONE_TRACKER = 1057
    HEALTHKIT_STEP_APPLE_WATCH_TRACKER = 1058
    HEALTHKIT_OTHER_STEP_TRACKER = 1059
    ANDROID_STEP_TRACKER_1 = 1053
    ANDROID_STEP_TRACKER_2 = 1054
    ANDROID_STEP_TRACKER_3 = 1060
    GOOGLE_FIT_TRACKER = 1055
    SAMSUNG_HEALTH_TRACKER = 1056
    HUAWEI_TRACKER = 1062


class DeviceType(StrEnum):
    """Enum representing the device type."""

    UNKNOWN = "unknown"
    SCALE = "Scale"
    BABYPHONE = "Babyphone"
    BLOOD_PRESSURE_MONITOR = "Blood Pressure Monitor"
    ACTIVITY_TRACKER = "Activity Tracker"
    SLEEP_MONITOR = "Sleep Monitor"
    SMART_CONNECTED_THERMOMETER = "Smart Connected Thermometer"
    GATEWAY = "Gateway"
    IGLUCOSE = "iGlucose"
    HEALTHKIT_APPLE = "HealthKit Apple"
    HEALTHKIT_GOOGLE = "HealthKit Google"
    HEALTHKIT_HUAWEI = "HealthKit Huawei"


class DeviceBattery(StrEnum):
    """Enum representing the battery state of the device."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(slots=True)
class Device:
    """Model for a Withings device."""

    device_type: DeviceType
    battery: DeviceBattery
    model: DeviceModel
    first_session_date: datetime | None
    last_session_date: datetime | None
    device_id: str
    hashed_device_id: str

    @classmethod
    def from_api(cls, device: dict[str, Any]) -> Self:
        """Initialize from the API."""
        first_session_date = None
        if device["first_session_date"] is not None:
            first_session_date = datetime.fromtimestamp(
                device["first_session_date"],
                tz=timezone.utc,
            )
        last_session_date = None
        if device["last_session_date"] is not None:
            last_session_date = datetime.fromtimestamp(
                device["last_session_date"],
                tz=timezone.utc,
            )
        return cls(
            device_type=to_enum(DeviceType, device["type"], DeviceType.UNKNOWN),
            battery=DeviceBattery(device["battery"]),
            model=to_enum(DeviceModel, device["model_id"], DeviceModel.UNKNOWN),
            first_session_date=first_session_date,
            last_session_date=last_session_date,
            device_id=device["deviceid"],
            hashed_device_id=device["hash_deviceid"],
        )


@dataclass(slots=True)
class Goals:
    """Model for Withings goals."""

    steps: int
    sleep: int
    weight: float

    @classmethod
    def from_api(cls, goals: dict[str, Any]) -> Self:
        """Initialize from the API."""
        return cls(
            steps=goals["steps"],
            sleep=goals["sleep"],
            weight=get_measurement_from_dict(goals["weight"]),
        )
