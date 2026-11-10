"""Asynchronous Python client for Withings."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import IntEnum, IntFlag, StrEnum
from typing import Any, Self

from mashumaro import DataClassDictMixin, field_options, pass_through
from mashumaro.config import BaseConfig

from aiowithings.util import get_measurement_from_dict, to_enum


class _WithingsModel(DataClassDictMixin):
    """Base class for models parsed from the Withings API."""

    __slots__ = ()

    class Config(BaseConfig):  # pylint: disable=too-few-public-methods
        """Mashumaro configuration."""

        # Withings sends timestamps as epoch seconds. Primitives pass through
        # because mashumaro coerces them by default, for example None to "None".
        serialization_strategy = {  # noqa: RUF012
            datetime: {"deserialize": lambda ts: datetime.fromtimestamp(ts, tz=UTC)},
            bool: pass_through,
            float: pass_through,
            int: pass_through,
            str: pass_through,
        }

    @classmethod
    def from_api(cls, data: Any) -> Self:
        """Initialize from the API."""
        return cls.from_dict(data)


def _enum_options[EnumT](
    enum_class: type[EnumT],
    default_value: EnumT,
    alias: str | None = None,
) -> dict[str, Any]:
    """Return field options that map unknown API values to a default."""
    return field_options(
        alias=alias,
        deserialize=lambda value: to_enum(enum_class, value, default_value),
    )


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
    SLEEP_ANALYZER = 13
    BODY_SCALE = 14
    BODY_COMP_2 = 15
    BODY_SMART = 16
    BODY_PRO_2 = 17
    BODY_COMP = 18
    BODY_SCAN_2 = 19
    BODY_FIT = 20
    SMART_BABY_MONITOR = 21
    WITHINGS_HOME = 22
    WITHINGS_BLOOD_PRESSURE_MONITOR_V1 = 41
    WITHINGS_BLOOD_PRESSURE_MONITOR_V2 = 42
    WITHINGS_BLOOD_PRESSURE_MONITOR_V3 = 43
    BPM_CORE = 44
    BPM_CONNECT = 45
    BPM_CONNECT_PRO = 46
    BPM_PRO_2 = 47
    BPM_VISION = 48
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
    SCANWATCH_2 = 94
    SCANWATCH_LIGHT = 95
    AURA_DOCK = 60
    AURA_SENSOR = 61
    AURA_SENSOR_V2 = 63
    THERMO = 70
    BEAMO = 71
    WUP01 = 100
    U_SCAN = 102
    IGLUCOSE_GLUCOMETER = 1061
    LINGO_SENSOR = 1063
    IGLUCOSE_ESSENTIAL = 1065
    IPULSE_OX = 1066
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
    FLUID_ANALYZER = "Fluid Analyzer"
    GATEWAY = "Gateway"
    IGLUCOSE = "iGlucose"
    SMART_METER = "Smart Meter"
    LINGO = "Lingo"
    HEALTHKIT_APPLE = "HealthKit Apple"
    HEALTHKIT_GOOGLE = "HealthKit Google"
    HEALTHKIT_HUAWEI = "HealthKit Huawei"


class DeviceBattery(StrEnum):
    """Enum representing the battery state of the device."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(slots=True)
class Device(_WithingsModel):
    """Model for a Withings device."""

    device_type: DeviceType = field(
        metadata=_enum_options(DeviceType, DeviceType.UNKNOWN, "type")
    )
    battery: DeviceBattery | None = field(
        metadata=field_options(
            deserialize=lambda battery: (
                DeviceBattery(battery) if battery != "unknown" else None
            )
        )
    )
    raw_model: str = field(metadata=field_options(alias="model"))
    model: DeviceModel = field(
        metadata=_enum_options(DeviceModel, DeviceModel.UNKNOWN, "model_id")
    )
    first_session_date: datetime | None
    last_session_date: datetime | None
    device_id: str = field(metadata=field_options(alias="deviceid"))
    hashed_device_id: str = field(metadata=field_options(alias="hash_deviceid"))

    @classmethod
    def __post_deserialize__(cls, obj: Self) -> Self:
        """Fix model names that the API reports wrong for model 13."""
        if (
            obj.model is DeviceModel.SLEEP_ANALYZER
            and obj.device_type is DeviceType.SCALE
            and obj.raw_model in ("", "Sleep Analyzer")
        ):
            obj.raw_model = "Body+"
        elif not obj.raw_model and obj.model is DeviceModel.SLEEP_ANALYZER:
            obj.raw_model = "Sleep Analyzer"
        return obj


@dataclass(slots=True)
class Goals(_WithingsModel):
    """Model for Withings goals."""

    steps: int | None = None
    sleep: int | None = None
    weight: float | None = field(
        default=None,
        metadata=field_options(deserialize=get_measurement_from_dict),
    )

    @classmethod
    def __pre_deserialize__(cls, d: Any) -> dict[str, Any]:
        """Treat the empty list that the API sends without goals as no goals."""
        return {} if isinstance(d, list) else d


class MeasurementAttribution(IntEnum):
    """Measure attributions."""

    UNKNOWN = -1
    DEVICE_ENTRY_FOR_USER = 0
    DEVICE_ENTRY_FOR_USER_AMBIGUOUS = 1
    MANUAL_USER_ENTRY = 2
    USER_PICKED = 3
    MANUAL_USER_DURING_ACCOUNT_CREATION = 4
    MEASURE_AUTO = 5
    MEASURE_USER_CONFIRMED = 7
    GUIDED_CONDITIONS = 15


class MeasurementGroupCategory(IntEnum):
    """Measure categories."""

    UNKNOWN = 0
    REAL = 1
    USER_OBJECTIVES = 2


@dataclass(slots=True)
class MeasurementGroup(_WithingsModel):
    """Model for a measurement group."""

    group_id: int = field(metadata=field_options(alias="grpid"))
    attribution: MeasurementAttribution = field(
        metadata=_enum_options(
            MeasurementAttribution, MeasurementAttribution.UNKNOWN, "attrib"
        )
    )
    taken_at: datetime = field(metadata=field_options(alias="date"))
    stored_at: datetime = field(metadata=field_options(alias="created"))
    updated_at: datetime = field(metadata=field_options(alias="modified"))
    category: MeasurementGroupCategory = field(
        metadata=_enum_options(
            MeasurementGroupCategory, MeasurementGroupCategory.UNKNOWN
        )
    )
    device_id: str = field(metadata=field_options(alias="deviceid"))
    hashed_device_id: str = field(metadata=field_options(alias="hash_deviceid"))
    measurements: list[Measurement] = field(metadata=field_options(alias="measures"))

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        """Map attributions 8 and 17 to the enum values they belong to."""
        return d | {"attrib": {8: 0, 17: 15}.get(d["attrib"], d["attrib"])}


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
    URINARY_PH = 147
    URINE_SPECIFIC_GRAVITY = 148
    URINARY_NITRITES = 151
    VASCULAR_AGE = 155
    NERVE_HEALTH_SCORE_LEFT_FOOT = 158
    NERVE_HEALTH_SCORE_RIGHT_FOOT = 159
    NERVE_HEALTH_SCORE_FEET = 167
    EXTRACELLULAR_WATER = 168
    INTRACELLULAR_WATER = 169
    VISCERAL_FAT = 170
    FAT_FREE_MASS_FOR_SEGMENTS = 173
    FAT_MASS_FOR_SEGMENTS = 174
    MUSCLE_MASS_FOR_SEGMENTS = 175
    ELECTRODERMAL_ACTIVITY_FEET = 196
    ELECTRODERMAL_ACTIVITY_LEFT_FOOT = 197
    ELECTRODERMAL_ACTIVITY_RIGHT_FOOT = 198
    URINARY_KETONES = 204
    URINARY_VITAMIN_C = 205
    BASAL_METABOLIC_RATE = 226
    METABOLIC_AGE = 227
    ELECTROCHEMICAL_SKIN_CONDUCTANCE = 229
    URINARY_CALCIUM = 248
    URINARY_CREATININE = 249
    URINARY_CALCIUM_CREATININE_RATIO = 251


class MeasurementPosition(IntEnum):
    """Measurement positions."""

    RIGHT_WRIST = 0
    LEFT_WRIST = 1
    RIGHT_ARM = 2
    LEFT_ARM = 3
    RIGHT_FOOT = 4
    LEFT_FOOT = 5
    BETWEEN_LEGS = 6
    WHOLE_BODY = 7
    LEFT_PART_OF_BODY = 8
    RIGHT_PART_OF_BODY = 9
    LEFT_LEG = 10
    RIGHT_LEG = 11
    TORSO = 12
    LEFT_HAND = 13
    RIGHT_HAND = 14


@dataclass(slots=True)
class Measurement(_WithingsModel):
    """Model for a measurement."""

    measurement_type: MeasurementType = field(
        metadata=_enum_options(MeasurementType, MeasurementType.UNKNOWN, "type")
    )
    value: float
    position: MeasurementPosition | None = field(
        default=None,
        metadata=field_options(
            deserialize=lambda position: to_enum(MeasurementPosition, position, None)
        ),
    )

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        """Apply the unit exponent to the value."""
        return d | {"value": get_measurement_from_dict(d)}


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
class NotificationConfiguration(_WithingsModel):
    """Class representing the webhook config from Withings."""

    notification_category: NotificationCategory = field(
        metadata=_enum_options(
            NotificationCategory, NotificationCategory.UNKNOWN, "appli"
        )
    )
    callback_url: str = field(metadata=field_options(alias="callbackurl"))
    comment: str


@dataclass(slots=True)
class WebhookCall(_WithingsModel):
    """Class representing the webhook call from Withings."""

    user_id: int = field(metadata=field_options(alias="userid"))
    notification_category: NotificationCategory = field(
        metadata=_enum_options(
            NotificationCategory, NotificationCategory.UNKNOWN, "appli"
        )
    )
    start_date: datetime = field(metadata=field_options(alias="startdate"))
    end_date: datetime = field(metadata=field_options(alias="enddate"))


def get_sleep_series_time_data(time: str, value: int) -> SleepSeriesTimeData:
    """Return sleep series time data."""
    return SleepSeriesTimeData(
        time=datetime.fromtimestamp(
            int(time),
            tz=UTC,
        ),
        value=value,
    )


def get_sleep_series_time_data_list(
    data: dict[str, int],
) -> list[SleepSeriesTimeData]:
    """Return sleep series time data."""
    return [get_sleep_series_time_data(time, value) for time, value in data.items()]


def _sleep_series_options(alias: str) -> dict[str, Any]:
    """Return field options that read a timestamp-to-value dict of sleep data."""
    return field_options(alias=alias, deserialize=get_sleep_series_time_data_list)


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
    HEART_RATE_VARIABILITY_QUALITY = "hrv_quality"
    CHEST_MOVEMENT_RATE = "chest_movement_rate"
    BREATHING_SOUNDS = "breathing_sounds"
    WITHINGS_INDEX = "withings_index"


@dataclass(slots=True)
class SleepSeriesTimeData:
    """Represents data point in sleep data."""

    time: datetime
    value: int


@dataclass(slots=True)
class SleepSeries(_WithingsModel):
    """Represents sleep data."""

    start_date: datetime = field(metadata=field_options(alias="startdate"))
    end_date: datetime = field(metadata=field_options(alias="enddate"))
    state: SleepState = field(
        metadata=_enum_options(SleepState, SleepState.UNSPECIFIED)
    )
    hashed_device_id: str = field(metadata=field_options(alias="hash_deviceid"))
    heart_rate: list[SleepSeriesTimeData] | None = field(
        default=None, metadata=_sleep_series_options("hr")
    )
    respiration_rate: list[SleepSeriesTimeData] | None = field(
        default=None, metadata=_sleep_series_options("rr")
    )
    snoring: list[SleepSeriesTimeData] | None = field(
        default=None, metadata=_sleep_series_options("snoring")
    )
    heart_rate_variability: list[SleepSeriesTimeData] | None = field(
        default=None, metadata=_sleep_series_options("sdnn_1")
    )
    heart_rate_variability_2: list[SleepSeriesTimeData] | None = field(
        default=None, metadata=_sleep_series_options("rmssd")
    )
    movement_score: list[SleepSeriesTimeData] | None = field(
        default=None, metadata=_sleep_series_options("mvt_score")
    )
    heart_rate_variability_quality: list[SleepSeriesTimeData] | None = field(
        default=None, metadata=_sleep_series_options("hrv_quality")
    )
    chest_movement_rate: list[SleepSeriesTimeData] | None = field(
        default=None, metadata=_sleep_series_options("chest_movement_rate")
    )
    breathing_sounds: list[SleepSeriesTimeData] | None = field(
        default=None, metadata=_sleep_series_options("breathing_sounds")
    )
    withings_index: list[SleepSeriesTimeData] | None = field(
        default=None, metadata=_sleep_series_options("withings_index")
    )


class CoreBodyTemperatureStatus(StrEnum):
    """Enum representing the core body temperature status."""

    UNKNOWN = "unknown"
    USUAL = "usual"
    ELEVATED = "elevated"


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
    BREATHING_QUALITY_ASSESSMENT = "breathing_quality_assessment"
    BREATHING_SOUNDS = "breathing_sounds"
    BREATHING_SOUNDS_COUNT = "breathing_sounds_episode_count"
    AVERAGE_CHEST_MOVEMENT_RATE = "chest_movement_rate_average"
    MIN_CHEST_MOVEMENT_RATE = "chest_movement_rate_min"
    MAX_CHEST_MOVEMENT_RATE = "chest_movement_rate_max"
    AVERAGE_CHEST_MOVEMENT_RATE_WELLNESS = "chest_movement_rate_wellness_average"
    MIN_CHEST_MOVEMENT_RATE_WELLNESS = "chest_movement_rate_wellness_min"
    MAX_CHEST_MOVEMENT_RATE_WELLNESS = "chest_movement_rate_wellness_max"

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
    AVERAGE_CORE_BODY_TEMPERATURE = "core_body_temperature_avg"
    MIN_CORE_BODY_TEMPERATURE = "core_body_temperature_min"
    MAX_CORE_BODY_TEMPERATURE = "core_body_temperature_max"
    CORE_BODY_TEMPERATURE_STATUS = "core_body_temperature_status"
    AVERAGE_HEART_RATE_VARIABILITY_START = "rmssd_start_avg"
    AVERAGE_HEART_RATE_VARIABILITY_END = "rmssd_end_avg"


@dataclass(slots=True)
class SleepSummary(_WithingsModel):
    """Class representing sleep summary."""

    start_date: datetime = field(metadata=field_options(alias="startdate"))
    end_date: datetime = field(metadata=field_options(alias="enddate"))
    date: date
    hashed_device_id: str = field(metadata=field_options(alias="hash_deviceid"))
    apnea_hypopnea_index: int | None = None
    external_time_asleep: int | None = field(
        default=None, metadata=field_options(alias="asleepduration")
    )
    breathing_disturbances_intensity: int | None = None
    deep_sleep_duration: int | None = field(
        default=None, metadata=field_options(alias="deepsleepduration")
    )
    average_heart_rate: int | None = field(
        default=None, metadata=field_options(alias="hr_average")
    )
    min_heart_rate: int | None = field(
        default=None, metadata=field_options(alias="hr_min")
    )
    max_heart_rate: int | None = field(
        default=None, metadata=field_options(alias="hr_max")
    )
    light_sleep_duration: int | None = field(
        default=None, metadata=field_options(alias="lightsleepduration")
    )
    active_movement_duration: int | None = field(
        default=None, metadata=field_options(alias="mvt_active_duration")
    )
    average_movement_score: int | None = field(
        default=None, metadata=field_options(alias="mvt_score_avg")
    )
    rem_sleep_phase_count: int | None = field(
        default=None, metadata=field_options(alias="nb_rem_episodes")
    )
    out_of_bed_count: int | None = None
    rem_sleep_duration: int | None = field(
        default=None, metadata=field_options(alias="remsleepduration")
    )
    average_respiration_rate: int | None = field(
        default=None, metadata=field_options(alias="rr_average")
    )
    min_respiration_rate: int | None = field(
        default=None, metadata=field_options(alias="rr_min")
    )
    max_respiration_rate: int | None = field(
        default=None, metadata=field_options(alias="rr_max")
    )
    sleep_efficiency: int | None = None
    sleep_latency: int | None = None
    sleep_score: int | None = None
    snoring: int | None = None
    snoring_count: int | None = field(
        default=None, metadata=field_options(alias="snoringepisodecount")
    )
    total_sleep_time: int | None = None
    total_time_in_bed: int | None = field(
        default=None, metadata=field_options(alias="total_timeinbed")
    )
    wake_up_latency: int | None = field(
        default=None, metadata=field_options(alias="wakeup_latency")
    )
    wake_up_count: int | None = field(
        default=None, metadata=field_options(alias="wakeupcount")
    )
    total_time_awake: int | None = field(
        default=None, metadata=field_options(alias="wakeupduration")
    )
    time_awake_during_sleep: int | None = field(
        default=None, metadata=field_options(alias="waso")
    )
    withings_index: int | None = None
    breathing_quality_assessment: int | None = None
    breathing_sounds: int | None = None
    breathing_sounds_count: int | None = field(
        default=None, metadata=field_options(alias="breathing_sounds_episode_count")
    )
    average_chest_movement_rate: int | None = field(
        default=None, metadata=field_options(alias="chest_movement_rate_average")
    )
    min_chest_movement_rate: int | None = field(
        default=None, metadata=field_options(alias="chest_movement_rate_min")
    )
    max_chest_movement_rate: int | None = field(
        default=None, metadata=field_options(alias="chest_movement_rate_max")
    )
    average_chest_movement_rate_wellness: int | None = field(
        default=None,
        metadata=field_options(alias="chest_movement_rate_wellness_average"),
    )
    min_chest_movement_rate_wellness: int | None = field(
        default=None, metadata=field_options(alias="chest_movement_rate_wellness_min")
    )
    max_chest_movement_rate_wellness: int | None = field(
        default=None, metadata=field_options(alias="chest_movement_rate_wellness_max")
    )
    average_core_body_temperature: float | None = field(
        default=None, metadata=field_options(alias="core_body_temperature_avg")
    )
    min_core_body_temperature: float | None = field(
        default=None, metadata=field_options(alias="core_body_temperature_min")
    )
    max_core_body_temperature: float | None = field(
        default=None, metadata=field_options(alias="core_body_temperature_max")
    )
    core_body_temperature_status: CoreBodyTemperatureStatus | None = field(
        default=None,
        metadata=_enum_options(
            CoreBodyTemperatureStatus,
            CoreBodyTemperatureStatus.UNKNOWN,
            "core_body_temperature_status",
        ),
    )
    average_heart_rate_variability_start: float | None = field(
        default=None, metadata=field_options(alias="rmssd_start_avg")
    )
    average_heart_rate_variability_end: float | None = field(
        default=None, metadata=field_options(alias="rmssd_end_avg")
    )

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        """Move the nested sleep metrics to the top level."""
        return {**d, **d["data"]}


class ActivityDataFields(StrEnum):
    """Enum representing the activity data fields."""

    STEPS = "steps"
    DISTANCE = "distance"
    ELEVATION = "elevation"
    SOFT_ACTIVITY = "soft"
    MODERATE_ACTIVITY = "moderate"
    INTENSE_ACTIVITY = "intense"
    TOTAL_TIME_ACTIVE = "active"
    ACTIVE_CALORIES_BURNT = "calories"
    TOTAL_CALORIES_BURNT = "totalcalories"
    AVERAGE_HEART_RATE = "hr_average"
    MIN_HEART_RATE = "hr_min"
    MAX_HEART_RATE = "hr_max"
    DURATION_HEART_RATE_LIGHT_ZONE = "hr_zone_0"
    DURATION_HEART_RATE_MODERATE_ZONE = "hr_zone_1"
    DURATION_HEART_RATE_INTENSE_ZONE = "hr_zone_2"
    DURATION_HEART_RATE_MAXIMAL_ZONE = "hr_zone_3"


class ActivityDataOrigin(IntEnum):
    """Enum representing the origin of activity data."""

    UNKNOWN = -1
    WITHINGS = 1
    EXTERNAL = 18


_ACTIVITY_HEART_RATE_KEYS = (
    "hr_average",
    "hr_min",
    "hr_max",
    "hr_zone_0",
    "hr_zone_1",
    "hr_zone_2",
    "hr_zone_3",
)


@dataclass(slots=True)
class Activity(_WithingsModel):
    """Class representing aggregated activity in a day."""

    steps: int
    distance: float
    elevation: int
    soft_activity: int = field(metadata=field_options(alias="soft"))
    moderate_activity: int = field(metadata=field_options(alias="moderate"))
    intense_activity: int = field(metadata=field_options(alias="intense"))
    total_time_active: int = field(metadata=field_options(alias="active"))
    active_calories_burnt: float = field(metadata=field_options(alias="calories"))
    total_calories_burnt: float = field(metadata=field_options(alias="totalcalories"))
    average_heart_rate: int | None = field(metadata=field_options(alias="hr_average"))
    min_heart_rate: int | None = field(metadata=field_options(alias="hr_min"))
    max_heart_rate: int | None = field(metadata=field_options(alias="hr_max"))
    duration_heart_rate_light_zone: int | None = field(
        metadata=field_options(alias="hr_zone_0")
    )
    duration_heart_rate_moderate_zone: int | None = field(
        metadata=field_options(alias="hr_zone_1")
    )
    duration_heart_rate_intense_zone: int | None = field(
        metadata=field_options(alias="hr_zone_2")
    )
    duration_heart_rate_maximal_zone: int | None = field(
        metadata=field_options(alias="hr_zone_3")
    )
    date: date
    modified: datetime
    is_withings_tracker: bool = field(metadata=field_options(alias="is_tracker"))
    origin: ActivityDataOrigin = field(
        metadata=_enum_options(ActivityDataOrigin, ActivityDataOrigin.UNKNOWN, "brand")
    )

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        """Drop the heart rate data when no heart rate was measured.

        The API sends 0 for all heart rate values in that case.
        """
        if d.get("hr_average", 0) == 0:
            return d | dict.fromkeys(_ACTIVITY_HEART_RATE_KEYS)
        return d


class WorkoutCategory(IntEnum):
    """Enum representing the workout category."""

    WALK = 1
    RUN = 2
    HIKING = 3
    SKATING = 4
    BMX = 5
    BICYCLING = 6
    SWIMMING = 7
    SURFING = 8
    KITESURFING = 9
    WINDSURFING = 10
    BODYBOARD = 11
    TENNIS = 12
    TABLE_TENNIS = 13
    SQUASH = 14
    BADMINTON = 15
    LIFT_WEIGHTS = 16
    FITNESS = 17
    ELLIPTICAL = 18
    PILATES = 19
    BASKET_BALL = 20
    SOCCER = 21
    FOOTBALL = 22
    RUGBY = 23
    VOLLEY_BALL = 24
    WATERPOLO = 25
    HORSE_RIDING = 26
    GOLF = 27
    YOGA = 28
    DANCING = 29
    BOXING = 30
    FENCING = 31
    WRESTLING = 32
    MARTIAL_ARTS = 33
    SKIING = 34
    SNOWBOARDING = 35
    OTHER = 36
    NO_ACTIVITY = 128
    ROWING = 187
    ZUMBA = 188
    BASEBALL = 191
    HANDBALL = 192
    HOCKEY = 193
    ICE_HOCKEY = 194
    CLIMBING = 195
    ICE_SKATING = 196
    MULTI_SPORT = 272
    INDOOR_WALK = 306
    INDOOR_RUNNING = 307
    INDOOR_CYCLING = 308
    STANDUP_PADDLEBOARDING = 455
    PADEL = 456
    GAMING = 457
    BEACH_VOLLEYBALL = 490
    STAIR_STEPPER = 491
    SKATEBOARDING = 492
    PARKOUR = 493
    KAYAKING = 494
    CANOEING = 495
    SAILING = 496
    FISHING = 497
    TRAIL_RUNNING = 498
    SNOWSHOEING = 499
    PAINTBALL = 500
    ARCHERY = 501
    SCUBA_DIVING = 502
    BASEBALL_TRAINING = 503
    BIATHLON = 504
    BOCCE = 505
    PETANQUE = 506
    PARAGLIDING = 507
    FRISBEE = 508
    SKYDIVING = 509
    PICKLEBALL = 510
    CORNHOLE = 511
    DODGEBALL = 512
    ULTIMATE = 513
    TEQBALL = 514
    PUSHING_A_WHEELCHAIR_RUNNING_PACE = 515
    PUSHING_A_WHEELCHAIR_WALKING_PACE = 516
    ATHLETICS = 517
    TRACK_CYCLING = 518
    PENTATHLON = 519
    SPORT_SHOOTING = 520
    TRIATHLON = 521
    DIVING = 522
    MOUNTAIN_BIKING = 523
    GRAVEL_BIKING = 524
    E_BIKING = 525
    E_MOUNTAIN_BIKING = 526
    HANDCYCLING = 527
    VELOMOBILE = 528
    BACKCOUNTRY_SKIING = 529
    NORDIC_SKIING = 530
    ROLLER_SKIING = 531
    RACQUETBALL = 532
    HIP_HOP = 534
    MUAYTHAI = 535
    TAEKWONDO = 536
    JUDO = 537
    TRAMPOLINE = 538
    STANDING_FRAME = 539
    SEATED_STRENGTH = 540
    SEATED_CARDIO = 541
    WALK_WITH_WALKER = 542
    WALK_WITH_CANE = 543
    BREAKING = 544
    CHORES = 545
    CROSSFIT = 546
    SPINCLASS = 547
    CRICKET = 548
    FLAMENCO_DANCING = 549
    HIIT = 550
    MEDITATION = 551
    STRETCHING = 552
    YARD_WORK_GARDENING = 553
    CLEANING = 554
    PUBLIC_SPEAKING = 555
    SPIKEBALL = 556
    LACROSSE = 557
    BABY_WEARING = 558
    DOG_WALKING = 559
    BREATHING_EXERCISES = 560
    BALANCE_DRILLS = 561
    PUSHING_A_STROLLER = 562
    TODDLER_WEARING = 563
    BOWLING = 564
    LASERTAG = 565
    NORDIC_WALKING = 566
    SUMO_WRESTLING = 567
    COOKING = 568
    MATCH_DAY = 569
    JUMP_ROPE = 570
    CALISTHENICS = 571
    BARRE = 572
    AQUA_AEROBICS = 573
    GYMNASTICS = 574
    AEROBICS = 575
    CHEERLEADING = 576
    TAI_CHI = 577
    QIGONG = 578
    SAUNA = 579
    COLD_PLUNGE = 580
    KARATE = 581
    KICKBOXING = 582
    NETBALL = 583
    SOFTBALL = 584
    FUTSAL = 585
    DARTS = 586
    BILLIARDS = 587
    MOUNTAINEERING = 588
    BOULDERING = 589
    DISC_GOLF = 590
    WAKEBOARDING = 591
    WATER_SKIING = 592
    HUNTING = 593
    RUCKING = 594
    INDOOR_ROWING = 595
    RESISTANCE_BAND_TRAINING = 596
    AUSTRALIAN_RULES_FOOTBALL = 597


class WorkoutDataFields(StrEnum):
    """Enum representing the workout data fields."""

    CALORIES = "calories"
    INTENSITY = "intensity"
    MANUAL_INTENSITY = "manual_intensity"
    MANUAL_DISTANCE = "manual_distance"
    MANUAL_CALORIES = "manual_calories"
    AVERAGE_HEART_RATE = "hr_average"
    MIN_HEART_RATE = "hr_min"
    MAX_HEART_RATE = "hr_max"
    DURATION_HEART_RATE_LIGHT_ZONE = "hr_zone_0"
    DURATION_HEART_RATE_MODERATE_ZONE = "hr_zone_1"
    DURATION_HEART_RATE_INTENSE_ZONE = "hr_zone_2"
    DURATION_HEART_RATE_MAXIMAL_ZONE = "hr_zone_3"
    PAUSE_DURATION = "pause_duration"
    ALGO_PAUSE_DURATION = "algo_pause_duration"
    SPO2_AVERAGE = "spo2_average"
    STEPS = "steps"
    DISTANCE = "distance"
    ELEVATION = "elevation"
    POOL_LAPS = "pool_laps"
    STROKES = "strokes"
    POOL_LENGTH = "pool_length"
    AVERAGE_CORE_BODY_TEMPERATURE = "core_body_temperature_avg"
    MIN_CORE_BODY_TEMPERATURE = "core_body_temperature_min"
    MAX_CORE_BODY_TEMPERATURE = "core_body_temperature_max"
    CORE_BODY_TEMPERATURE_STATUS = "core_body_temperature_status"


@dataclass(slots=True)
class Workout(_WithingsModel):
    """Class representing a workout."""

    workout_id: int = field(metadata=field_options(alias="id"))
    category: WorkoutCategory = field(
        metadata=_enum_options(WorkoutCategory, WorkoutCategory.OTHER)
    )
    attribution: MeasurementAttribution = field(
        metadata=_enum_options(
            MeasurementAttribution, MeasurementAttribution.UNKNOWN, "attrib"
        )
    )
    start_date: datetime = field(metadata=field_options(alias="startdate"))
    end_date: datetime = field(metadata=field_options(alias="enddate"))
    date: date

    active_calories_burnt: int | None = field(
        default=None, metadata=field_options(alias="calories")
    )
    distance: int | None = None
    elevation: int | None = None
    average_heart_rate: int | None = field(
        default=None, metadata=field_options(alias="hr_average")
    )
    min_heart_rate: int | None = field(
        default=None, metadata=field_options(alias="hr_min")
    )
    max_heart_rate: int | None = field(
        default=None, metadata=field_options(alias="hr_max")
    )
    duration_heart_rate_light_zone: int | None = field(
        default=None, metadata=field_options(alias="hr_zone_0")
    )
    duration_heart_rate_moderate_zone: int | None = field(
        default=None, metadata=field_options(alias="hr_zone_1")
    )
    duration_heart_rate_intense_zone: int | None = field(
        default=None, metadata=field_options(alias="hr_zone_2")
    )
    duration_heart_rate_maximal_zone: int | None = field(
        default=None, metadata=field_options(alias="hr_zone_3")
    )
    intensity: int | None = None
    pause_duration: int | None = None
    spo2_average: int | None = None
    steps: int | None = None
    manual_intensity: int | None = None
    average_core_body_temperature: float | None = field(
        default=None, metadata=field_options(alias="core_body_temperature_avg")
    )
    min_core_body_temperature: float | None = field(
        default=None, metadata=field_options(alias="core_body_temperature_min")
    )
    max_core_body_temperature: float | None = field(
        default=None, metadata=field_options(alias="core_body_temperature_max")
    )
    core_body_temperature_status: CoreBodyTemperatureStatus | None = field(
        default=None,
        metadata=_enum_options(
            CoreBodyTemperatureStatus,
            CoreBodyTemperatureStatus.UNKNOWN,
            "core_body_temperature_status",
        ),
    )

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        """Move the nested workout metrics to the top level.

        The API sends 0 for metrics that the device did not record.
        """
        return d | {key: value for key, value in d["data"].items() if value != 0}
