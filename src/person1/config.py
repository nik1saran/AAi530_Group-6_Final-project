from dataclasses import dataclass


ALLOWED_STATUS = {"confirmed", "preliminary", "unverified"}
ALLOWED_SOURCE_TIERS = {"tier_a", "tier_b", "tier_c"}

SOURCE_QUALITY_SCORE = {"tier_a": 0.35, "tier_b": 0.24, "tier_c": 0.10}
CORROBORATION_SCORE = {0: 0.00, 1: 0.15, 2: 0.25}
FRESHNESS_SCORE = {"fresh": 0.20, "moderate": 0.12, "stale": 0.05}
CONFLICT_PENALTY = {"none": 0.00, "minor": 0.07, "major": 0.15}
COMPLETENESS_SCORE = {"complete": 0.05, "partial": 0.02, "sparse": 0.00}


@dataclass(frozen=True)
class VerificationThresholds:
    confirmed_min: float = 0.80
    preliminary_min: float = 0.45
    max_staleness_hours: int = 24


THRESHOLDS = VerificationThresholds()

