"""Asynchronous Python client for Withings."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import IntEnum, IntFlag, StrEnum
from typing import Any, Self

from aiowithings.util import get_measurement_from_dict, to_enum


class AuthScope(StrEnum):
    """Enum representing the auth scopes."""

    USER_INFO = "user.info"
    USER_METRICS = "user.metrics"
    USER_ACTIVITY = "user.activity"
    USER_SLEEP_EVENTS = "user.sleepevents"


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


def get_sleep_series_time_data(time: str, value: int) -> SleepSeriesTimeData:
    """Return sleep series time data."""
    return SleepSeriesTimeData(
        time=datetime.fromtimestamp(
            int(time),
            tz=timezone.utc,
        ),
        value=value,
    )


def get_sleep_series_time_data_list(
    data: dict[str, int] | None,
) -> list[SleepSeriesTimeData] | None:
    """Return sleep series time data."""
    if data is None:
        return None
    return [get_sleep_series_time_data(time, value) for time, value in data.items()]


class SleepState(IntEnum):
    """Enum representing the sleep states."""

    AWAKE = 0
    LIGHT_SLEEP = 1
    DEEP_SLEEP = 2
    REM_SLEEP = 3
    MANUAL = 4
    UNSPECIFIED = 5


class SleepDataFields(StrEnum):
    """Enum representing the sleep data fields."""

    HEART_RATE = "hr"
    RESPIRATION_RATE = "rr"
    SNORING = "snoring"
    HEART_RATE_VARIABILITY = "sdnn_1"
    HEART_RATE_VARIABILITY_2 = "rmssd"
    MOVEMENT_SCORE = "mvt_score"


@dataclass(slots=True)
class SleepSeriesTimeData:
    """Represents data point in sleep data."""

    time: datetime
    value: int


@dataclass(slots=True)
class SleepSeries:
    """Represents sleep data."""

    start_date: datetime
    end_date: datetime
    state: SleepState
    hashed_device_id: str
    heart_rate: list[SleepSeriesTimeData] | None
    respiration_rate: list[SleepSeriesTimeData] | None
    snoring: list[SleepSeriesTimeData] | None
    heart_rate_variability: list[SleepSeriesTimeData] | None
    heart_rate_variability_2: list[SleepSeriesTimeData] | None
    movement_score: list[SleepSeriesTimeData] | None

    @classmethod
    def from_api(cls, sleep_data: dict[str, Any]) -> Self:
        """Initialize from the API."""
        return cls(
            start_date=datetime.fromtimestamp(
                sleep_data["startdate"],
                tz=timezone.utc,
            ),
            end_date=datetime.fromtimestamp(
                sleep_data["enddate"],
                tz=timezone.utc,
            ),
            state=to_enum(SleepState, sleep_data["state"], SleepState.UNSPECIFIED),
            hashed_device_id=sleep_data["hash_deviceid"],
            heart_rate=get_sleep_series_time_data_list(sleep_data.get("hr")),
            respiration_rate=get_sleep_series_time_data_list(sleep_data.get("rr")),
            snoring=get_sleep_series_time_data_list(sleep_data.get("snoring")),
            heart_rate_variability=get_sleep_series_time_data_list(
                sleep_data.get("sdnn_1"),
            ),
            heart_rate_variability_2=get_sleep_series_time_data_list(
                sleep_data.get("rmssd"),
            ),
            movement_score=get_sleep_series_time_data_list(sleep_data.get("mvt_score")),
        )


class SleepSummaryDataFields(StrEnum):
    """Enum representing the sleep summary data fields."""

    # Standard sleep medicine metrics
    REM_SLEEP_PHASE_COUNT = "nb_rem_episodes"
    SLEEP_EFFICIENCY = "sleep_efficiency"
    SLEEP_LATENCY = "sleep_latency"
    TOTAL_SLEEP_TIME = "total_sleep_time"
    TOTAL_TIME_IN_BED = "total_timeinbed"
    WAKE_UP_LATENCY = "wakeup_latency"
    TIME_AWAKE_DURING_SLEEP = "waso"

    # Sleep apnea and breathing disturbances
    APNEA_HYPOPNEA_INDEX = "apnea_hypopnea_index"
    BREATHING_DISTURBANCES_INTENSITY = "breathing_disturbances_intensity"

    # Other sleep datapoints and vitals
    EXTERNAL_TOTAL_SLEEP_TIME = "asleepduration"
    DEEP_SLEEP_DURATION = "deepsleepduration"
    AVERAGE_HEART_RATE = "hr_average"
    MIN_HEART_RATE = "hr_min"
    MAX_HEART_RATE = "hr_max"
    LIGHT_SLEEP_DURATION = "lightsleepduration"
    ACTIVE_MOVEMENT_DURATION = "mvt_active_duration"
    AVERAGE_MOVEMENT_SCORE = "mvt_score_avg"
    NIGHT_EVENTS = "night_events"
    OUT_OF_BED_COUNT = "out_of_bed_count"
    REM_SLEEP_DURATION = "remsleepduration"
    AVERAGE_RESPIRATION_RATE = "rr_average"
    MIN_RESPIRATION_RATE = "rr_min"
    MAX_RESPIRATION_RATE = "rr_max"
    SLEEP_SCORE = "sleep_score"
    SNORING = "snoring"
    SNORING_COUNT = "snoringepisodecount"
    WAKE_UP_COUNT = "wakeupcount"
    TOTAL_TIME_AWAKE = "wakeupduration"
    WITHINGS_INDEX = "withings_index"


@dataclass(slots=True)
class SleepSummary:
    """Class representing sleep summary."""

    start_date: datetime
    end_date: datetime
    date: date
    hashed_device_id: str
    apnea_hypopnea_index: int | None
    external_time_asleep: int | None
    breathing_disturbances_intensity: int | None
    deep_sleep_duration: int | None
    average_heart_rate: int | None
    min_heart_rate: int | None
    max_heart_rate: int | None
    light_sleep_duration: int | None
    active_movement_duration: int | None
    average_movement_score: int | None
    rem_sleep_phase_count: int | None
    out_of_bed_count: int | None
    rem_sleep_duration: int | None
    average_respiration_rate: int | None
    min_respiration_rate: int | None
    max_respiration_rate: int | None
    sleep_efficiency: int | None
    sleep_latency: int | None
    sleep_score: int | None
    snoring: int | None
    snoring_count: int | None
    total_sleep_time: int | None
    total_time_in_bed: int | None
    wake_up_latency: int | None
    wake_up_count: int | None
    total_time_awake: int | None
    time_awake_during_sleep: int | None
    withings_index: int | None

    @classmethod
    def from_api(cls, sleep_data: dict[str, Any]) -> Self:
        """Initialize from the API."""
        return cls(
            start_date=datetime.fromtimestamp(
                sleep_data["startdate"],
                tz=timezone.utc,
            ),
            end_date=datetime.fromtimestamp(
                sleep_data["enddate"],
                tz=timezone.utc,
            ),
            date=date.fromisoformat(sleep_data["date"]),
            hashed_device_id=sleep_data["hash_deviceid"],
            apnea_hypopnea_index=sleep_data["data"].get("apnea_hypopnea_index"),
            external_time_asleep=sleep_data["data"].get("asleepduration"),
            breathing_disturbances_intensity=sleep_data["data"].get(
                "breathing_disturbances_intensity",
            ),
            deep_sleep_duration=sleep_data["data"].get("deepsleepduration"),
            average_heart_rate=sleep_data["data"].get("hr_average"),
            min_heart_rate=sleep_data["data"].get("hr_min"),
            max_heart_rate=sleep_data["data"].get("hr_max"),
            light_sleep_duration=sleep_data["data"].get("lightsleepduration"),
            active_movement_duration=sleep_data["data"].get("mvt_active_duration"),
            average_movement_score=sleep_data["data"].get("mvt_score_avg"),
            rem_sleep_phase_count=sleep_data["data"].get("nb_rem_episodes"),
            out_of_bed_count=sleep_data["data"].get("out_of_bed_count"),
            rem_sleep_duration=sleep_data["data"].get("remsleepduration"),
            average_respiration_rate=sleep_data["data"].get("rr_average"),
            min_respiration_rate=sleep_data["data"].get("rr_min"),
            max_respiration_rate=sleep_data["data"].get("rr_max"),
            sleep_efficiency=sleep_data["data"].get("sleep_efficiency"),
            sleep_latency=sleep_data["data"].get("sleep_latency"),
            sleep_score=sleep_data["data"].get("sleep_score"),
            snoring=sleep_data["data"].get("snoring"),
            snoring_count=sleep_data["data"].get("snoringepisodecount"),
            total_sleep_time=sleep_data["data"].get("total_sleep_time"),
            total_time_in_bed=sleep_data["data"].get("total_timeinbed"),
            wake_up_latency=sleep_data["data"].get("wakeup_latency"),
            wake_up_count=sleep_data["data"].get("wakeupcount"),
            total_time_awake=sleep_data["data"].get("wakeupduration"),
            time_awake_during_sleep=sleep_data["data"].get("waso"),
            withings_index=sleep_data["data"].get("withings_index"),
        )
