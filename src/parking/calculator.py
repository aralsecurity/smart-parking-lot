from decimal import Decimal

from .models import ParkingSession
from .policies import (
    EarlyBirdPolicy,
    NightOwlPolicy,
    PricingPolicy,
    StandardHourlyPolicy,
)


class ParkingRateCalculator:
    """Evaluates all pricing policies and returns the lowest valid fare."""

    def __init__(self, policies: list[PricingPolicy] | None = None) -> None:
        self._policies = policies or [
            StandardHourlyPolicy(),
            EarlyBirdPolicy(),
            NightOwlPolicy(),
        ]

    def calculate(self, session: ParkingSession) -> Decimal:
        fares = []

        for policy in self._policies:
            fare = policy.calculate(session)

            if fare is not None:
                fares.append(fare)

        if not fares:
            raise ValueError("No applicable pricing policy")

        return min(fares)
