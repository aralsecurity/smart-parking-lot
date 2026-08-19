from decimal import Decimal

from parking.models import LoyaltyTier, VehicleType
from parking.pricing_components import (
    LoyaltyDiscountCalculator,
    PeakHourCalculator,
    VehicleRateCalculator,
)


def test_car_multiplier():
    calculator = VehicleRateCalculator()

    result = calculator.apply(
        Decimal("10.00"),
        VehicleType.CAR,
    )

    assert result == Decimal("10.00")


def test_motorcycle_multiplier():
    calculator = VehicleRateCalculator()

    result = calculator.apply(
        Decimal("10.00"),
        VehicleType.MOTORCYCLE,
    )

    assert result == Decimal("8.00")


def test_bus_multiplier():
    calculator = VehicleRateCalculator()

    result = calculator.apply(
        Decimal("10.00"),
        VehicleType.BUS,
    )

    assert result == Decimal("20.00")


def test_no_loyalty_discount():
    calculator = LoyaltyDiscountCalculator()

    result = calculator.apply(
        Decimal("15.00"),
        LoyaltyTier.NONE,
    )

    assert result == Decimal("15.00")


def test_silver_discount():
    calculator = LoyaltyDiscountCalculator()

    result = calculator.apply(
        Decimal("15.00"),
        LoyaltyTier.SILVER,
    )

    assert result == Decimal("13.50")


def test_gold_discount():
    calculator = LoyaltyDiscountCalculator()

    result = calculator.apply(
        Decimal("15.00"),
        LoyaltyTier.GOLD,
    )

    assert result == Decimal("12.00")


def test_platinum_discount():
    calculator = LoyaltyDiscountCalculator()

    result = calculator.apply(
        Decimal("15.00"),
        LoyaltyTier.PLATINUM,
    )

    assert result == Decimal("10.50")
