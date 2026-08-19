from datetime import datetime
from decimal import Decimal

from parking.calculator import ParkingRateCalculator
from parking.models import LoyaltyTier, ParkingSession, VehicleType


def create_session(
    entry: datetime,
    exit: datetime,
    vehicle_type: VehicleType = VehicleType.CAR,
    loyalty_tier: LoyaltyTier = LoyaltyTier.NONE,
) -> ParkingSession:
    return ParkingSession(
        vehicle_type=vehicle_type,
        entry_time=entry,
        exit_time=exit,
        loyalty_tier=loyalty_tier,
    )


def test_calculator_selects_early_bird_over_standard_hourly():
    calculator = ParkingRateCalculator()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 17, 16, 0),
    )

    assert calculator.calculate(session) == Decimal("15.00")


def test_calculator_selects_night_owl_over_standard_hourly():
    calculator = ParkingRateCalculator()

    session = create_session(
        datetime(2026, 8, 17, 20, 0),
        datetime(2026, 8, 18, 8, 0),
    )

    assert calculator.calculate(session) == Decimal("8.00")


def test_calculator_selects_lowest_fare_with_platinum_loyalty():
    calculator = ParkingRateCalculator()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 17, 16, 0),
        loyalty_tier=LoyaltyTier.PLATINUM,
    )

    assert calculator.calculate(session) == Decimal("10.50")


def test_calculator_uses_standard_hourly_when_special_policy_is_invalid():
    calculator = ParkingRateCalculator()

    session = create_session(
        datetime(2026, 8, 17, 11, 0),
        datetime(2026, 8, 17, 12, 0),
    )

    assert calculator.calculate(session) == Decimal("5.00")


def test_calculator_applies_vehicle_multiplier_to_best_policy():
    calculator = ParkingRateCalculator()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 17, 16, 0),
        vehicle_type=VehicleType.MOTORCYCLE,
    )

    assert calculator.calculate(session) == Decimal("12.00")


def test_calculator_uses_standard_hourly_after_more_than_24_hours():
    calculator = ParkingRateCalculator()

    session = create_session(
        datetime(2026, 8, 17, 11, 0),
        datetime(2026, 8, 18, 11, 1),
    )

    expected = Decimal("60.00")

    assert calculator.calculate(session) == expected
