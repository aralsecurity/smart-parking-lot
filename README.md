# Smart Parking Lot Rate Calculator

A simple, extensible parking-rate calculation engine that determines the best applicable parking fare based on vehicle type, parking duration, peak hours, loyalty tier, and special pricing policies.

## Problem Overview

The parking lot supports three vehicle types:

- Motorcycle
- Car
- Bus

The system supports three pricing policies:

1. Standard Hourly
2. Early Bird
3. Night Owl

For every parking session, all applicable pricing policies are evaluated and the lowest valid fare is returned.

The implementation is intentionally kept as a small, platform-agnostic Python application without external frameworks or infrastructure dependencies.

---

## Design Approach

The solution separates the domain into four main areas:

```text
ParkingSession
      |
      v
Pricing Policies
      |
      +---- StandardHourlyPolicy
      +---- EarlyBirdPolicy
      +---- NightOwlPolicy
      |
      v
ParkingRateCalculator
      |
      v
Lowest applicable fare
