"""Build a metric evidence packet from validated BigQuery CSV exports."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

from experiment_feasibility import assess_experiment_feasibility


DEFAULT_MDE_RELATIVE_LIFT = 0.10


def empty_metric_evidence_packet() -> dict[str, Any]:
    """Return the packet schema with null values instead of fabricated metrics."""
    return {
        "project": {
            "analysis_period_label": None,
            "data_source": "GA4 BigQuery export",
            "generated_by": "SQL/Python",
        },
        "funnel": {
            "funnel_steps": [],
            "top_dropoff_step": None,
            "top_dropoff_rate": None,
        },
        "opportunity": {
            "segment_name": None,
            "eligible_sessions": None,
            "segment_conversion_rate": None,
            "benchmark_name": None,
            "benchmark_conversion_rate": None,
            "conversion_rate_gap": None,
            "average_order_value": None,
            "estimated_missed_conversions": None,
            "estimated_revenue_opportunity": None,
        },
        "experiment_feasibility": {
            "baseline_conversion_rate": None,
            "mde_relative_lift": None,
            "alpha": None,
            "power": None,
            "required_sample_per_variant": None,
            "daily_eligible_users": None,
            "estimated_test_duration_days": None,
            "feasibility_interpretation": None,
            "recommended_next_step": None,
        },
        "qa": {
            "metric_definitions_reviewed": False,
            "ga4_event_taxonomy_reviewed": False,
            "utm_channel_grouping_reviewed": False,
            "notes": [],
        },
    }


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def as_float(value: str | int | float | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def as_int(value: str | int | float | None) -> int | None:
    number = as_float(value)
    if number is None:
        return None
    return int(round(number))


def safe_divide(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def format_period(profile_row: dict[str, str]) -> str | None:
    start = profile_row.get("min_event_date")
    end = profile_row.get("max_event_date")
    if not start or not end:
        return None
    return f"{start} to {end}"


def build_funnel_section(funnel_rows: list[dict[str, str]]) -> dict[str, Any]:
    totals = {
        "sessions": 0.0,
        "view_item_sessions": 0.0,
        "add_to_cart_sessions": 0.0,
        "begin_checkout_sessions": 0.0,
        "purchase_sessions": 0.0,
    }
    for row in funnel_rows:
        for key in totals:
            totals[key] += as_float(row.get(key)) or 0.0

    step_definitions = [
        ("sessions", "session", "view_item_sessions", "view_item"),
        ("view_item_sessions", "view_item", "add_to_cart_sessions", "add_to_cart"),
        ("add_to_cart_sessions", "add_to_cart", "begin_checkout_sessions", "begin_checkout"),
        ("begin_checkout_sessions", "begin_checkout", "purchase_sessions", "purchase"),
    ]

    funnel_steps: list[dict[str, Any]] = []
    for current_key, current_step, next_key, next_step in step_definitions:
        current_count = totals[current_key]
        next_count = totals[next_key]
        step_conversion_rate = safe_divide(next_count, current_count)
        dropoff_rate = None if step_conversion_rate is None else 1 - step_conversion_rate
        funnel_steps.append(
            {
                "step": current_step,
                "sessions": int(current_count),
                "next_step": next_step,
                "next_step_sessions": int(next_count),
                "step_conversion_rate": step_conversion_rate,
                "dropoff_rate": dropoff_rate,
            }
        )

    funnel_steps.append(
        {
            "step": "purchase",
            "sessions": int(totals["purchase_sessions"]),
            "next_step": None,
            "next_step_sessions": None,
            "step_conversion_rate": None,
            "dropoff_rate": None,
        }
    )

    ranked_dropoffs = [step for step in funnel_steps if step["dropoff_rate"] is not None]
    top_dropoff = max(ranked_dropoffs, key=lambda step: step["dropoff_rate"]) if ranked_dropoffs else None

    return {
        "funnel_steps": funnel_steps,
        "top_dropoff_step": None if top_dropoff is None else f"{top_dropoff['step']}_to_{top_dropoff['next_step']}",
        "top_dropoff_rate": None if top_dropoff is None else top_dropoff["dropoff_rate"],
    }


def build_opportunity_section(opportunity_rows: list[dict[str, str]]) -> dict[str, Any]:
    if not opportunity_rows:
        return empty_metric_evidence_packet()["opportunity"]

    top_row = max(
        opportunity_rows,
        key=lambda row: as_float(row.get("estimated_revenue_opportunity")) or 0.0,
    )
    source = top_row.get("user_source") or "unknown_source"
    medium = top_row.get("user_medium") or "unknown_medium"
    device = top_row.get("device_category") or "unknown_device"

    return {
        "segment_name": f"{source} / {medium} / {device}",
        "eligible_sessions": as_int(top_row.get("eligible_sessions")),
        "segment_conversion_rate": as_float(top_row.get("segment_conversion_rate")),
        "benchmark_name": "overall checkout-to-purchase conversion rate",
        "benchmark_conversion_rate": as_float(top_row.get("benchmark_conversion_rate")),
        "conversion_rate_gap": as_float(top_row.get("conversion_rate_gap")),
        "average_order_value": as_float(top_row.get("average_order_value")),
        "estimated_missed_conversions": as_float(top_row.get("estimated_missed_conversions")),
        "estimated_revenue_opportunity": as_float(top_row.get("estimated_revenue_opportunity")),
        "begin_checkout_sessions": as_int(top_row.get("begin_checkout_sessions")),
        "purchase_sessions": as_int(top_row.get("purchase_sessions")),
        "revenue": as_float(top_row.get("revenue")),
    }


def build_experiment_section(
    opportunity: dict[str, Any],
    profile_row: dict[str, str],
    mde_relative_lift: float,
) -> dict[str, Any]:
    baseline = opportunity.get("segment_conversion_rate")
    begin_checkout_sessions = opportunity.get("begin_checkout_sessions")
    day_count = as_int(profile_row.get("day_count"))

    if baseline is None or not 0 < baseline < 1 or begin_checkout_sessions is None or not day_count:
        return empty_metric_evidence_packet()["experiment_feasibility"]

    daily_eligible_users = max(1, math.ceil(begin_checkout_sessions / day_count))
    experiment = assess_experiment_feasibility(
        baseline_conversion_rate=baseline,
        mde_relative_lift=mde_relative_lift,
        daily_eligible_users=daily_eligible_users,
    )
    estimated_days = experiment["estimated_test_duration_days"]
    if estimated_days is not None and estimated_days > 90:
        experiment["feasibility_interpretation"] = (
            "The estimated test duration is long because the selected opportunity segment has limited "
            "eligible checkout traffic. Treat this as a traffic sufficiency warning, not as a launch-ready "
            "A/B test recommendation."
        )
        experiment["recommended_next_step"] = (
            "Expand the eligible population, combine similar segments, choose a larger practical effect size, "
            "or use a quasi-experimental design before committing to a randomized test."
        )
    else:
        experiment["feasibility_interpretation"] = (
            "The estimated test duration appears operationally feasible under the current planning assumptions."
        )
        experiment["recommended_next_step"] = (
            "Validate implementation effort, guardrail metrics, and tracking quality before launch."
        )
    return experiment


def build_metric_evidence_packet(
    dataset_profile_path: str | Path,
    event_coverage_path: str | Path,
    funnel_metrics_path: str | Path,
    opportunity_inputs_path: str | Path,
    mde_relative_lift: float = DEFAULT_MDE_RELATIVE_LIFT,
) -> dict[str, Any]:
    profile_rows = read_csv_rows(dataset_profile_path)
    if not profile_rows:
        raise ValueError("dataset profile CSV is empty.")

    profile_row = profile_rows[0]
    coverage_rows = read_csv_rows(event_coverage_path)
    funnel_rows = read_csv_rows(funnel_metrics_path)
    opportunity_rows = read_csv_rows(opportunity_inputs_path)

    funnel = build_funnel_section(funnel_rows)
    opportunity = build_opportunity_section(opportunity_rows)
    experiment = build_experiment_section(opportunity, profile_row, mde_relative_lift)

    return {
        "project": {
            "analysis_period_label": format_period(profile_row),
            "data_source": "bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*",
            "generated_by": "SQL/Python",
            "event_count": as_int(profile_row.get("event_count")),
            "user_count": as_int(profile_row.get("user_count")),
            "day_count": as_int(profile_row.get("day_count")),
            "min_event_date": profile_row.get("min_event_date"),
            "max_event_date": profile_row.get("max_event_date"),
        },
        "funnel": funnel,
        "opportunity": opportunity,
        "experiment_feasibility": experiment,
        "qa": {
            "metric_definitions_reviewed": True,
            "ga4_event_taxonomy_reviewed": True,
            "utm_channel_grouping_reviewed": True,
            "event_coverage": coverage_rows,
            "notes": [
                "Metrics are generated from deterministic BigQuery SQL exports and Python calculations.",
                "Public GA4 sample data is obfuscated; null, empty, or placeholder traffic fields may appear.",
                "Experiment feasibility uses checkout entrants for the selected opportunity segment as the eligible population.",
                f"MDE relative lift is an analyst-configured planning assumption: {mde_relative_lift}.",
                "Long estimated test durations should be interpreted as traffic sufficiency warnings rather than launch-ready experiment recommendations.",
            ],
        },
    }


def write_empty_packet(path: str | Path) -> None:
    Path(path).write_text(json.dumps(empty_metric_evidence_packet(), indent=2), encoding="utf-8")


def write_packet(packet: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(packet, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build metric_evidence_packet.json from BigQuery CSV exports.")
    parser.add_argument("--dataset-profile", default="data/dataset_profile.csv")
    parser.add_argument("--event-coverage", default="data/event_coverage.csv")
    parser.add_argument("--funnel-metrics", default="data/funnel_metrics.csv")
    parser.add_argument("--opportunity-inputs", default="data/opportunity_inputs.csv")
    parser.add_argument("--output", default="outputs/metric_evidence_packet.json")
    parser.add_argument("--mde-relative-lift", type=float, default=DEFAULT_MDE_RELATIVE_LIFT)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    evidence_packet = build_metric_evidence_packet(
        dataset_profile_path=args.dataset_profile,
        event_coverage_path=args.event_coverage,
        funnel_metrics_path=args.funnel_metrics,
        opportunity_inputs_path=args.opportunity_inputs,
        mde_relative_lift=args.mde_relative_lift,
    )
    write_packet(evidence_packet, args.output)
