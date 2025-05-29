"""HERE Routing API models."""

from dataclasses import dataclass
from enum import Enum


class TrafficMode(Enum):
    """Available TrafficMode Values."""

    DISABLED = "disabled"
    DEFAULT = "default"


class TransportMode(Enum):
    """Available TransportModes."""

    CAR = "car"
    TRUCK = "truck"
    PEDESTRIAN = "pedestrian"
    BICYCLE = "bicycle"
    SCOOTER = "scooter"


class RoutingMode(Enum):
    """Available RoutingMode Values."""

    SHORT = "short"
    FAST = "fast"


class UnitSystem(Enum):
    """Available UnitSystem Values."""

    METRIC = "metric"
    IMPERIAL = "imperial"


class Return(Enum):
    """Available Return Values."""

    POLYINE = "polyline"
    ACTIONS = "actions"
    INSTRUCTIONS = "instructions"
    SUMMARY = "summary"
    TRAVEL_SUMMARY = "travelSummary"
    ML_DURATION = "mlDuration"
    TYPICAL_DURATION = "typicalDuration"
    TURN_BY_TURN_ACTIONS = "turnByTurnActions"
    ELEVATION = "elevation"
    ROUTE_HANDLE = "routeHandle"
    PASSTHROUGH = "passthrough"
    INCIDENTS = "incidents"
    ROUTING_ZONES = "routingZones"
    TRUCK_ROAD_TYPES = "truckRoadTypes"
    TOLLS = "tolls"


class Spans(Enum):
    """Available Spans Values."""

    WALK_ATTRIBUTES = "walkAttributes"
    STREET_ATTRIBUTES = "streetAttributes"
    CAR_ATTRIBUTES = "carAttributes"
    TRUCK_ATTRIBUTES = "truckAttributes"
    SCOOTER_ATTRIBUTES = "scooterAttributes"
    NAMES = "names"
    LENGTH = "length"
    DURATION = "duration"
    BASE_DURATION = "baseDuration"
    TYPICAL_DURATION = "typicalDuration"
    COUNTRY_CODE = "countryCode"
    FUNCTIONAL_CLASS = "functionalClass"
    ROUTE_NUMBERS = "routeNumbers"
    SPEED_LIMIT = "speedLimit"
    MAX_SPEED = "maxSpeed"
    DYNAMIC_SPEED_INFO = "dynamicSpeedInfo"
    SEGMENT_ID = "segmentId"
    SEGMENT_REF = "segmentRef"
    CONSUMPTION = "consumption"
    ROUTING_ZONES = "routingZones"
    TRUCK_ROAD_TYPES = "truckRoadTypes"
    NOTICES = "notices"
    INCIDENTS = "incidents"
    TOLL_SYSTEMS = "tollSystems"


@dataclass
class Place:
    """Place for route requests."""

    latitude: float
    longitude: float
