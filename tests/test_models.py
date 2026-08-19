
from datetime import datetime

import pytest

from parking.models import LoyaltyTier, ParkingSession, VehicleType


def test_creates_valid_parking_session():
    session = ParkingSession(
        vehicle_type=VehicleType.CAR,
        entry_time=datetime(2026, 8, 17, 11, 0),
        exit_time=datetime(2026, 8, 17, 12, 0),
        loyalty_tier=LoyaltyTier.GOLD,
    )

    assert session.vehicle_type == VehicleType.CAR
    assert session.loyalty_tier == LoyaltyTier.GOLD


def test_rejects_exit_before_entry():
    with pytest.raises(ValueError, match="Exit time must be after entry time"):
        ParkingSession(
            vehicle_type=VehicleType.CAR,
            entry_time=datetime(2026, 8, 17, 12, 0),
            exit_time=datetime(2026, 8, 17, 11, 0),
        )


def test_rejects_exit_equal_to_entry():
    with pytest.raises(ValueError, match="Exit time must be after entry time"):
        ParkingSession(
            vehicle_type=VehicleType.CAR,
            entry_time=datetime(2026, 8, 17, 12, 0),
            exit_time=datetime(2026, 8, 17, 12, 0),
        )
