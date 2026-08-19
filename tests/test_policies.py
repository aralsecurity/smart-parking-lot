from datetime import datetime
from decimal import Decimal

from parking.models import LoyaltyTier, ParkingSession, VehicleType
from parking.policies import (
    EarlyBirdPolicy,
    NightOwlPolicy,
    StandardHourlyPolicy,
)


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


# ---------------------------------------------------------------------------
# Standard Hourly Policy
# ---------------------------------------------------------------------------


def test_standard_hourly_one_hour():
    policy = StandardHourlyPolicy()

    session = create_session(
        datetime(2026, 8, 17, 11, 0),
        datetime(2026, 8, 17, 12, 0),
    )

    assert policy.calculate(session) == Decimal("5.00")


def test_standard_hourly_two_hours():
    policy = StandardHourlyPolicy()

    session = create_session(
        datetime(2026, 8, 17, 11, 0),
        datetime(2026, 8, 17, 13, 0),
    )

    assert policy.calculate(session) == Decimal("8.00")


def test_standard_hourly_three_hours():
    policy = StandardHourlyPolicy()

    session = create_session(
        datetime(2026, 8, 17, 11, 0),
        datetime(2026, 8, 17, 14, 0),
    )

    assert policy.calculate(session) == Decimal("10.00")


def test_standard_hourly_partial_hour_rounds_up():
    policy = StandardHourlyPolicy()

    session = create_session(
        datetime(2026, 8, 17, 11, 0),
        datetime(2026, 8, 17, 11, 30),
    )

    assert policy.calculate(session) == Decimal("5.00")


def test_standard_hourly_one_hour_and_one_minute_rounds_up():
    policy = StandardHourlyPolicy()

    session = create_session(
        datetime(2026, 8, 17, 11, 0),
        datetime(2026, 8, 17, 12, 1),
    )

    assert policy.calculate(session) == Decimal("8.00")


def test_standard_hourly_assignment_peak_example():
    """
    Assignment example:
    06:30 -> 08:30 on a weekday.

    Hour 1: 06:30 -> 07:30 overlaps peak => $5 * 1.5 = $7.50
    Hour 2: 07:30 -> 08:30 overlaps peak => $3 * 1.5 = $4.50

    Expected total = $12.00
    """
    policy = StandardHourlyPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 17, 8, 30),
    )

    assert policy.calculate(session) == Decimal("12.00")


def test_standard_hourly_partial_peak_overlap():
    policy = StandardHourlyPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 17, 7, 30),
    )

    assert policy.calculate(session) == Decimal("7.50")


def test_standard_hourly_hour_ending_at_peak_start_is_not_peak():
    policy = StandardHourlyPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 0),
        datetime(2026, 8, 17, 7, 0),
    )

    assert policy.calculate(session) == Decimal("5.00")


def test_standard_hourly_hour_starting_at_peak_end_is_not_peak():
    policy = StandardHourlyPolicy()

    session = create_session(
        datetime(2026, 8, 17, 10, 0),
        datetime(2026, 8, 17, 11, 0),
    )

    assert policy.calculate(session) == Decimal("5.00")


def test_standard_hourly_weekend_has_no_peak_surcharge():
    policy = StandardHourlyPolicy()

    session = create_session(
        datetime(2026, 8, 22, 7, 0),
        datetime(2026, 8, 22, 8, 0),
    )

    assert policy.calculate(session) == Decimal("5.00")


def test_standard_hourly_motorcycle_multiplier():
    policy = StandardHourlyPolicy()

    session = create_session(
        datetime(2026, 8, 17, 11, 0),
        datetime(2026, 8, 17, 12, 0),
        vehicle_type=VehicleType.MOTORCYCLE,
    )

    assert policy.calculate(session) == Decimal("4.00")


def test_standard_hourly_bus_multiplier():
    policy = StandardHourlyPolicy()

    session = create_session(
        datetime(2026, 8, 17, 11, 0),
        datetime(2026, 8, 17, 12, 0),
        vehicle_type=VehicleType.BUS,
    )

    assert policy.calculate(session) == Decimal("10.00")


# ---------------------------------------------------------------------------
# Early Bird Policy
# ---------------------------------------------------------------------------


def test_early_bird_valid():
    policy = EarlyBirdPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 17, 16, 0),
    )

    assert policy.calculate(session) == Decimal("15.00")


def test_early_bird_entry_at_6am_is_valid():
    policy = EarlyBirdPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 0),
        datetime(2026, 8, 17, 16, 0),
    )

    assert policy.calculate(session) == Decimal("15.00")


def test_early_bird_entry_at_9am_is_invalid():
    policy = EarlyBirdPolicy()

    session = create_session(
        datetime(2026, 8, 17, 9, 0),
        datetime(2026, 8, 17, 16, 0),
    )

    assert policy.calculate(session) is None


def test_early_bird_exit_at_3_30pm_is_valid():
    policy = EarlyBirdPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 17, 15, 30),
    )

    assert policy.calculate(session) == Decimal("15.00")


def test_early_bird_exit_at_7pm_is_invalid():
    policy = EarlyBirdPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 17, 19, 0),
    )

    assert policy.calculate(session) is None


def test_early_bird_must_exit_same_day():
    policy = EarlyBirdPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 18, 16, 0),
    )

    assert policy.calculate(session) is None


def test_early_bird_silver_discount():
    policy = EarlyBirdPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 17, 16, 0),
        loyalty_tier=LoyaltyTier.SILVER,
    )

    assert policy.calculate(session) == Decimal("13.50")


def test_early_bird_gold_discount():
    policy = EarlyBirdPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 17, 16, 0),
        loyalty_tier=LoyaltyTier.GOLD,
    )

    assert policy.calculate(session) == Decimal("12.00")


def test_early_bird_platinum_discount():
    policy = EarlyBirdPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 17, 16, 0),
        loyalty_tier=LoyaltyTier.PLATINUM,
    )

    assert policy.calculate(session) == Decimal("10.50")


def test_early_bird_motorcycle():
    policy = EarlyBirdPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 17, 16, 0),
        vehicle_type=VehicleType.MOTORCYCLE,
    )

    assert policy.calculate(session) == Decimal("12.00")


def test_early_bird_bus():
    policy = EarlyBirdPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 17, 16, 0),
        vehicle_type=VehicleType.BUS,
    )

    assert policy.calculate(session) == Decimal("30.00")


# ---------------------------------------------------------------------------
# Night Owl Policy
# ---------------------------------------------------------------------------


def test_night_owl_valid():
    policy = NightOwlPolicy()

    session = create_session(
        datetime(2026, 8, 17, 20, 0),
        datetime(2026, 8, 18, 8, 0),
    )

    assert policy.calculate(session) == Decimal("8.00")


def test_night_owl_entry_at_6pm_is_valid():
    policy = NightOwlPolicy()

    session = create_session(
        datetime(2026, 8, 17, 18, 0),
        datetime(2026, 8, 18, 8, 0),
    )

    assert policy.calculate(session) == Decimal("8.00")


def test_night_owl_entry_before_6pm_is_invalid():
    policy = NightOwlPolicy()

    session = create_session(
        datetime(2026, 8, 17, 17, 59),
        datetime(2026, 8, 18, 8, 0),
    )

    assert policy.calculate(session) is None


def test_night_owl_exit_at_5am_is_valid():
    policy = NightOwlPolicy()

    session = create_session(
        datetime(2026, 8, 17, 20, 0),
        datetime(2026, 8, 18, 5, 0),
    )

    assert policy.calculate(session) == Decimal("8.00")


def test_night_owl_exit_at_10am_is_invalid():
    policy = NightOwlPolicy()

    session = create_session(
        datetime(2026, 8, 17, 20, 0),
        datetime(2026, 8, 18, 10, 0),
    )

    assert policy.calculate(session) is None


def test_night_owl_must_exit_next_calendar_day():
    policy = NightOwlPolicy()

    session = create_session(
        datetime(2026, 8, 17, 20, 0),
        datetime(2026, 8, 19, 8, 0),
    )

    assert policy.calculate(session) is None


def test_night_owl_silver_discount():
    policy = NightOwlPolicy()

    session = create_session(
        datetime(2026, 8, 17, 20, 0),
        datetime(2026, 8, 18, 8, 0),
        loyalty_tier=LoyaltyTier.SILVER,
    )

    assert policy.calculate(session) == Decimal("7.20")


def test_night_owl_gold_discount():
    policy = NightOwlPolicy()

    session = create_session(
        datetime(2026, 8, 17, 20, 0),
        datetime(2026, 8, 18, 8, 0),
        loyalty_tier=LoyaltyTier.GOLD,
    )

    assert policy.calculate(session) == Decimal("6.40")


def test_night_owl_platinum_motorcycle():
    policy = NightOwlPolicy()

    session = create_session(
        datetime(2026, 8, 17, 20, 0),
        datetime(2026, 8, 18, 8, 0),
        vehicle_type=VehicleType.MOTORCYCLE,
        loyalty_tier=LoyaltyTier.PLATINUM,
    )

    assert policy.calculate(session) == Decimal("4.48")


# ---------------------------------------------------------------------------
# More-than-24-hour rule
# ---------------------------------------------------------------------------


def test_early_bird_is_invalid_after_24_hours():
    policy = EarlyBirdPolicy()

    session = create_session(
        datetime(2026, 8, 17, 6, 30),
        datetime(2026, 8, 18, 6, 31),
    )

    assert policy.calculate(session) is None


def test_night_owl_is_invalid_after_24_hours():
    policy = NightOwlPolicy()

    session = create_session(
        datetime(2026, 8, 17, 20, 0),
        datetime(2026, 8, 18, 20, 1),
    )

    assert policy.calculate(session) is None
