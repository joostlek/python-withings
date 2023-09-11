"""Asynchronous Python client for Withings."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import IntEnum, IntFlag, StrEnum
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


class MeasurementGroupAttribution(IntEnum):
    """Measure group attributions."""

    UNKNOWN = -1
    DEVICE_ENTRY_FOR_USER = 0
    DEVICE_ENTRY_FOR_USER_AMBIGUOUS = 1
    MANUAL_USER_ENTRY = 2
    MANUAL_USER_DURING_ACCOUNT_CREATION = 4
    MEASURE_AUTO = 5
    MEASURE_USER_CONFIRMED = 7


class MeasurementGroupCategory(IntEnum):
    """Measure categories."""

    UNKNOWN = 0
    REAL = 1
    USER_OBJECTIVES = 2


@dataclass(slots=True)
class MeasurementGroup:
    """Model for a measurement group."""

    group_id: int
    attribution: MeasurementGroupAttribution
    taken_at: datetime
    stored_at: datetime
    updated_at: datetime
    category: MeasurementGroupCategory
    device_id: str
    hashed_device_id: str
    measurements: list[Measurement]

    @classmethod
    def from_api(cls, measurement_group: dict[str, Any]) -> Self:
        """Initialize from the API."""
        if measurement_group["attrib"] == 8:
            measurement_group["attrib"] = 0
        return cls(
            group_id=measurement_group["grpid"],
            attribution=to_enum(
                MeasurementGroupAttribution,
                measurement_group["attrib"],
                MeasurementGroupAttribution.UNKNOWN,
            ),
            taken_at=datetime.fromtimestamp(
                measurement_group["date"],
                tz=timezone.utc,
            ),
            stored_at=datetime.fromtimestamp(
                measurement_group["created"],
                tz=timezone.utc,
            ),
            updated_at=datetime.fromtimestamp(
                measurement_group["modified"],
                tz=timezone.utc,
            ),
            category=to_enum(
                MeasurementGroupCategory,
                measurement_group["category"],
                MeasurementGroupCategory.UNKNOWN,
            ),
            device_id=measurement_group["deviceid"],
            hashed_device_id=measurement_group["hash_deviceid"],
            measurements=[
                Measurement.from_api(measurement)
                for measurement in measurement_group["measures"]
            ],
        )


class MeasurementType(IntEnum):
    """Measurement types."""

    UNKNOWN = 0
    WEIGHT = 1
    HEIGHT = 4
    FAT_FREE_MASS = 5
    FAT_RATIO = 6
    FAT_MASS_WEIGHT = 8
    DIASTOLIC_BLOOD_PRESSURE = 9
    SYSTOLIC_BLOOD_PRESSURE = 10
    HEART_RATE = 11
    TEMPERATURE = 12
    SP02 = 54
    BODY_TEMPERATURE = 71
    SKIN_TEMPERATURE = 73
    MUSCLE_MASS = 76
    HYDRATION = 77
    BONE_MASS = 88
    PULSE_WAVE_VELOCITY = 91
    VO2 = 123
    ATRIAL_FIBRILLATION = 130
    QRS_INTERVAL = 135
    PR_INTERVAL = 136
    QT_INTERVAL = 137
    CORRECTED_QT_INTERVAL = 138
    ATRIAL_FIBRILLATION_FROM_PPG = 139
    VASCULAR_AGE = 155
    NERVE_HEALTH_SCORE_LEFT_FOOT = 158
    NERVE_HEALTH_SCORE_RIGHT_FOOT = 159
    NERVE_HEALTH_SCORE_FEET = 167
    EXTRACELLULAR_WATER = 168
    INTRACELLULAR_WATER = 169
    VISCERAL_FAT = 170
    FAT_MASS_FOR_SEGMENTS = 174
    MUSCLE_MASS_FOR_SEGMENTS = 175
    ELECTRODERMAL_ACTIVITY_FEET = 196
    ELECTRODERMAL_ACTIVITY_LEFT_FOOT = 197
    ELECTRODERMAL_ACTIVITY_RIGHT_FOOT = 198


@dataclass(slots=True)
class Measurement:
    """Model for a measurement."""

    measurement_type: MeasurementType
    value: float

    @classmethod
    def from_api(cls, measurement: dict[str, Any]) -> Self:
        """Initialize from the API."""
        return cls(
            measurement_type=to_enum(
                MeasurementType,
                measurement["type"],
                MeasurementType.UNKNOWN,
            ),
            value=get_measurement_from_dict(measurement),
        )


class NotificationCategory(IntEnum):
    """Enum representing the notification category (Appli)."""

    UNKNOWN = 0
    WEIGHT = 1
    TEMPERATURE = 2
    PRESSURE = 4
    ACTIVITY = 16
    SLEEP = 44
    USER_DATA = 46
    IN_BED = 50
    OUT_BED = 51
    INITIAL_INFLATION_DONE = 52
    NO_ACCOUNT_ASSOCIATED = 53
    ECG = 54
    ECG_FAILED = 55
    GLUCOSE = 58


class Services(IntFlag):
    """Enum representing the possible services."""

    MEASURE_GET_MEAS = 1
    MEASURE_V2_GET_ACTIVITY = 2
    MEASURE_V2_GET_INTRA_DAY_ACTIVITY = 4
    MEASURE_V2_GET_WORKOUTS = 8
    SLEEP_V2_GET_SLEEP = 16
    SLEEP_V2_GET_SUMMARY = 32
    USER_V2_ACTIVATE = 64
    USER_V2_LINK = 128
    HEART_V2_LIST = 256


def get_measurement_type_from_notification_category(
    category: NotificationCategory,
) -> list[MeasurementType]:
    """Get measurement types from notification category."""
    match category:
        case NotificationCategory.WEIGHT:
            return [
                MeasurementType.WEIGHT,
                MeasurementType.FAT_FREE_MASS,
                MeasurementType.FAT_RATIO,
                MeasurementType.FAT_MASS_WEIGHT,
                MeasurementType.BODY_TEMPERATURE,
                MeasurementType.SKIN_TEMPERATURE,
                MeasurementType.MUSCLE_MASS,
                MeasurementType.HYDRATION,
                MeasurementType.BONE_MASS,
                MeasurementType.PULSE_WAVE_VELOCITY,
            ]
        case NotificationCategory.TEMPERATURE:
            return [
                MeasurementType.TEMPERATURE,
                MeasurementType.BODY_TEMPERATURE,
                MeasurementType.SKIN_TEMPERATURE,
            ]
        case NotificationCategory.PRESSURE:
            return [
                MeasurementType.DIASTOLIC_BLOOD_PRESSURE,
                MeasurementType.SYSTOLIC_BLOOD_PRESSURE,
                MeasurementType.HEART_RATE,
                MeasurementType.SP02,
            ]
    return []


@dataclass(slots=True)
class NotificationConfiguration:
    """Class representing the webhook config from Withings."""

    notification_category: NotificationCategory
    callback_url: str
    expires: datetime
    comment: str

    @classmethod
    def from_api(cls, configuration: dict[str, Any]) -> Self:
        """Initialize from the API."""
        return cls(
            notification_category=to_enum(
                NotificationCategory,
                configuration["appli"],
                NotificationCategory.UNKNOWN,
            ),
            callback_url=configuration["callbackurl"],
            expires=datetime.fromtimestamp(
                configuration["expires"],
                tz=timezone.utc,
            ),
            comment=configuration["comment"],
        )


@dataclass(slots=True)
class WebhookCall:
    """Class representing the webhook call from Withings."""

    user_id: int
    notification_category: NotificationCategory
    start_date: datetime
    end_date: datetime

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Self:
        """Initialize from the API."""
        return cls(
            user_id=data["userid"],
            notification_category=to_enum(
                NotificationCategory,
                data["appli"],
                NotificationCategory.UNKNOWN,
            ),
            start_date=datetime.fromtimestamp(
                data["startdate"],
                tz=timezone.utc,
            ),
            end_date=datetime.fromtimestamp(
                data["enddate"],
                tz=timezone.utc,
            ),
        )
