"""Experiment feasibility helpers for funnel optimization tests."""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict

from scipy.stats import norm


@dataclass(frozen=True)
class ExperimentFeasibility:
    baseline_conversion_rate: float
    mde_relative_lift: float
    alpha: float
    power: float
    required_sample_per_variant: int
    daily_eligible_users: int | None
    estimated_test_duration_days: int | None


def sample_size_two_proportion(
    baseline_conversion_rate: float,
    mde_relative_lift: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """Estimate per-variant sample size for a two-sided two-proportion z-test."""
    if not 0 < baseline_conversion_rate < 1:
        raise ValueError("baseline_conversion_rate must be between 0 and 1.")
    if mde_relative_lift <= 0:
        raise ValueError("mde_relative_lift must be greater than 0.")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1.")
    if not 0 < power < 1:
        raise ValueError("power must be between 0 and 1.")

    p1 = baseline_conversion_rate
    p2 = baseline_conversion_rate * (1 + mde_relative_lift)
    if p2 >= 1:
        raise ValueError("baseline_conversion_rate * (1 + mde_relative_lift) must be below 1.")

    pooled = (p1 + p2) / 2
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)
    numerator = (
        z_alpha * math.sqrt(2 * pooled * (1 - pooled))
        + z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    ) ** 2
    denominator = (p2 - p1) ** 2
    return math.ceil(numerator / denominator)


def assess_experiment_feasibility(
    baseline_conversion_rate: float,
    mde_relative_lift: float,
    daily_eligible_users: int | None = None,
    alpha: float = 0.05,
    power: float = 0.80,
) -> dict:
    """Return experiment feasibility metrics as a JSON-serializable dict."""
    required_sample = sample_size_two_proportion(
        baseline_conversion_rate=baseline_conversion_rate,
        mde_relative_lift=mde_relative_lift,
        alpha=alpha,
        power=power,
    )

    estimated_days = None
    if daily_eligible_users is not None:
        if daily_eligible_users <= 0:
            raise ValueError("daily_eligible_users must be greater than 0 when provided.")
        estimated_days = math.ceil((required_sample * 2) / daily_eligible_users)

    return asdict(
        ExperimentFeasibility(
            baseline_conversion_rate=baseline_conversion_rate,
            mde_relative_lift=mde_relative_lift,
            alpha=alpha,
            power=power,
            required_sample_per_variant=required_sample,
            daily_eligible_users=daily_eligible_users,
            estimated_test_duration_days=estimated_days,
        )
    )

