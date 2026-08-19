from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class VehicleType(Enum):
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"
    BUS = "BUS"


class LoyaltyTier(Enum):
    NONE = "NONE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"


@dataclass(frozen=True)
class ParkingSession:
    vehicle_type: VehicleType
    entry_time: datetime
    exit_time: datetime
    loyalty_tier: LoyaltyTier = LoyaltyTier.NONE

    def __post_init__(self) -> None:
        if self.exit_time <= self.entry_time:
            raise ValueError("Exit time must be after entry time")
