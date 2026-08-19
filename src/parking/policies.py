from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal
from math import ceil

from .models import ParkingSession
from .pricing_components import (
    LoyaltyDiscountCalculator,
    PeakHourCalculator,
    VehicleRateCalculator,
)


class PricingPolicy(ABC):
    """Contract for a parking pricing policy."""

    @abstractmethod
    def calculate(self, session: ParkingSession) -> Decimal | None:
        """Return a fare when applicable, otherwise None."""
        raise NotImplementedError


class StandardHourlyPolicy(PricingPolicy):
    """Calculates the standard progressive hourly parking rate."""

    FIRST_HOUR_RATE = Decimal("5.00")
    SECOND_HOUR_RATE = Decimal("3.00")
    SUBSEQUENT_HOUR_RATE = Decimal("2.00")
    PEAK_MULTIPLIER = Decimal("1.5")

    def __init__(self) -> None:
        self._peak_hour_calculator = PeakHourCalculator()
        self._vehicle_rate_calculator = VehicleRateCalculator()

    def calculate(self, session: ParkingSession) -> Decimal:
        duration = session.exit_time - session.entry_time
        hours = ceil(duration.total_seconds() / 3600)

        total = Decimal("0.00")

        for hour_number in range(hours):
            block_start = session.entry_time + timedelta(hours=hour_number)
            block_end = block_start + timedelta(hours=1)

            rate = self._hourly_rate(hour_number)

            if self._peak_hour_calculator.overlaps_peak(
                block_start,
                block_end,
            ):
                rate *= self.PEAK_MULTIPLIER

            total += rate

        return self._vehicle_rate_calculator.apply(
            total,
            session.vehicle_type,
        )

    def _hourly_rate(self, hour_number: int) -> Decimal:
        if hour_number == 0:
            return self.FIRST_HOUR_RATE

        if hour_number == 1:
            return self.SECOND_HOUR_RATE

        return self.SUBSEQUENT_HOUR_RATE


class EarlyBirdPolicy(PricingPolicy):
    """Calculates the Early Bird flat-rate parking fare."""

    BASE_RATE = Decimal("15.00")
    MAX_SPECIAL_STAY = timedelta(hours=24)

    ENTRY_START = 6
    ENTRY_END = 9
    EXIT_START_MINUTES = 15 * 60 + 30
    EXIT_END_MINUTES = 19 * 60

    def __init__(self) -> None:
        self._loyalty_discount_calculator = LoyaltyDiscountCalculator()
        self._vehicle_rate_calculator = VehicleRateCalculator()

    def calculate(self, session: ParkingSession) -> Decimal | None:
        if not self._is_applicable(session):
            return None

        amount = self._loyalty_discount_calculator.apply(
            self.BASE_RATE,
            session.loyalty_tier,
        )

        return self._vehicle_rate_calculator.apply(
            amount,
            session.vehicle_type,
        )

    def _is_applicable(self, session: ParkingSession) -> bool:
        if session.exit_time - session.entry_time > self.MAX_SPECIAL_STAY:
            return False

        if session.entry_time.date() != session.exit_time.date():
            return False

        entry_minutes = (
            session.entry_time.hour * 60
            + session.entry_time.minute
        )

        exit_minutes = (
            session.exit_time.hour * 60
            + session.exit_time.minute
        )

        return (
            self.ENTRY_START * 60 <= entry_minutes < self.ENTRY_END * 60
            and self.EXIT_START_MINUTES <= exit_minutes < self.EXIT_END_MINUTES
        )


class NightOwlPolicy(PricingPolicy):
    """Calculates the Night Owl flat-rate parking fare."""

    BASE_RATE = Decimal("8.00")
    MAX_SPECIAL_STAY = timedelta(hours=24)

    ENTRY_START_MINUTES = 18 * 60
    ENTRY_END_MINUTES = 24 * 60

    EXIT_START_MINUTES = 5 * 60
    EXIT_END_MINUTES = 10 * 60

    def __init__(self) -> None:
        self._loyalty_discount_calculator = LoyaltyDiscountCalculator()
        self._vehicle_rate_calculator = VehicleRateCalculator()

    def calculate(self, session: ParkingSession) -> Decimal | None:
        if not self._is_applicable(session):
            return None

        amount = self._loyalty_discount_calculator.apply(
            self.BASE_RATE,
            session.loyalty_tier,
        )

        return self._vehicle_rate_calculator.apply(
            amount,
            session.vehicle_type,
        )

    def _is_applicable(self, session: ParkingSession) -> bool:
        duration = session.exit_time - session.entry_time

        if duration > self.MAX_SPECIAL_STAY:
            return False

        if session.exit_time.date() != (
            session.entry_time.date() + timedelta(days=1)
        ):
            return False

        entry_minutes = (
            session.entry_time.hour * 60
            + session.entry_time.minute
        )

        exit_minutes = (
            session.exit_time.hour * 60
            + session.exit_time.minute
        )

        return (
            self.ENTRY_START_MINUTES <= entry_minutes < self.ENTRY_END_MINUTES
            and self.EXIT_START_MINUTES <= exit_minutes < self.EXIT_END_MINUTES
        )
