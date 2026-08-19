from datetime import datetime, time
from decimal import Decimal

from .models import LoyaltyTier, VehicleType


VEHICLE_MULTIPLIERS = {
    VehicleType.MOTORCYCLE: Decimal("0.8"),
    VehicleType.CAR: Decimal("1.0"),
    VehicleType.BUS: Decimal("2.0"),
}


LOYALTY_DISCOUNTS = {
    LoyaltyTier.NONE: Decimal("0"),
    LoyaltyTier.SILVER: Decimal("0.10"),
    LoyaltyTier.GOLD: Decimal("0.20"),
    LoyaltyTier.PLATINUM: Decimal("0.30"),
}


class VehicleRateCalculator:
    """Applies the vehicle-specific rate multiplier."""

    def apply(
        self,
        amount: Decimal,
        vehicle_type: VehicleType,
    ) -> Decimal:
        multiplier = VEHICLE_MULTIPLIERS[vehicle_type]
        return amount * multiplier


class LoyaltyDiscountCalculator:
    """Applies the customer's loyalty discount."""

    def apply(
        self,
        amount: Decimal,
        loyalty_tier: LoyaltyTier,
    ) -> Decimal:
        discount = LOYALTY_DISCOUNTS[loyalty_tier]
        return amount * (Decimal("1") - discount)


class PeakHourCalculator:
    """Determines whether an hourly block overlaps a weekday peak window."""

    PEAK_WINDOWS = (
        (time(7, 0), time(10, 0)),
        (time(16, 0), time(19, 0)),
    )

    def overlaps_peak(
        self,
        start: datetime,
        end: datetime,
    ) -> bool:
        if start.weekday() >= 5:
            return False

        for window_start, window_end in self.PEAK_WINDOWS:
            if self._overlaps_window(
                start.time(),
                end.time(),
                window_start,
                window_end,
            ):
                return True

        return False

    @staticmethod
    def _overlaps_window(
        start: time,
        end: time,
        window_start: time,
        window_end: time,
    ) -> bool:
        return start < window_end and end > window_start
