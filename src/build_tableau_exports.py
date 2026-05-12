"""Build Tableau-ready CSV exports from the metric evidence layer."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def write_csv(path: str | Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_funnel_overview(packet: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for index, step in enumerate(packet["funnel"]["funnel_steps"], start=1):
        rows.append(
            {
                "step_order": index,
                "step": step["step"],
                "sessions": step["sessions"],
                "next_step": step["next_step"],
                "next_step_sessions": step["next_step_sessions"],
                "step_conversion_rate": step["step_conversion_rate"],
                "dropoff_rate": step["dropoff_rate"],
                "metric_source": f"metric_evidence_packet.funnel.funnel_steps[{index - 1}]",
            }
        )
    return rows


def build_segment_opportunity(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    export_rows = []
    for row in rows:
        segment_name = f"{row['user_source']} / {row['user_medium']} / {row['device_category']}"
        export_rows.append(
            {
                "segment_name": segment_name,
                "user_source": row["user_source"],
                "user_medium": row["user_medium"],
                "device_category": row["device_category"],
                "eligible_sessions": row["eligible_sessions"],
                "begin_checkout_sessions": row["begin_checkout_sessions"],
                "purchase_sessions": row["purchase_sessions"],
                "revenue": row["revenue"],
                "segment_conversion_rate": row["segment_conversion_rate"],
                "benchmark_conversion_rate": row["benchmark_conversion_rate"],
                "conversion_rate_gap": row["conversion_rate_gap"],
                "average_order_value": row["average_order_value"],
                "estimated_missed_conversions": row["estimated_missed_conversions"],
                "estimated_revenue_opportunity": row["estimated_revenue_opportunity"],
                "metric_source": "ga4_funnel_portfolio.opportunity_inputs",
            }
        )
    return export_rows


def build_experiment_feasibility(packet: dict[str, Any]) -> list[dict[str, Any]]:
    experiment = packet["experiment_feasibility"]
    rows = []
    for key, value in experiment.items():
        rows.append(
            {
                "metric_name": key,
                "metric_value": value,
                "metric_source": f"metric_evidence_packet.experiment_feasibility.{key}",
            }
        )
    return rows


def build_kpi_summary(packet: dict[str, Any]) -> list[dict[str, Any]]:
    project = packet["project"]
    funnel = packet["funnel"]
    opportunity = packet["opportunity"]
    experiment = packet["experiment_feasibility"]
    metrics = [
        ("analysis_period_label", project["analysis_period_label"], "metric_evidence_packet.project.analysis_period_label"),
        ("event_count", project["event_count"], "metric_evidence_packet.project.event_count"),
        ("user_count", project["user_count"], "metric_evidence_packet.project.user_count"),
        ("top_dropoff_step", funnel["top_dropoff_step"], "metric_evidence_packet.funnel.top_dropoff_step"),
        ("top_dropoff_rate", funnel["top_dropoff_rate"], "metric_evidence_packet.funnel.top_dropoff_rate"),
        ("top_opportunity_segment", opportunity["segment_name"], "metric_evidence_packet.opportunity.segment_name"),
        (
            "estimated_missed_conversions",
            opportunity["estimated_missed_conversions"],
            "metric_evidence_packet.opportunity.estimated_missed_conversions",
        ),
        (
            "estimated_revenue_opportunity",
            opportunity["estimated_revenue_opportunity"],
            "metric_evidence_packet.opportunity.estimated_revenue_opportunity",
        ),
        (
            "required_sample_per_variant",
            experiment["required_sample_per_variant"],
            "metric_evidence_packet.experiment_feasibility.required_sample_per_variant",
        ),
        (
            "estimated_test_duration_days",
            experiment["estimated_test_duration_days"],
            "metric_evidence_packet.experiment_feasibility.estimated_test_duration_days",
        ),
    ]
    return [
        {
            "metric_name": name,
            "metric_value": value,
            "metric_source": source,
        }
        for name, value, source in metrics
    ]


def build_tableau_exports(
    packet_path: str | Path = "outputs/metric_evidence_packet.json",
    opportunity_inputs_path: str | Path = "data/opportunity_inputs.csv",
    output_dir: str | Path = "tableau",
) -> None:
    packet = load_json(packet_path)
    opportunity_rows = load_csv(opportunity_inputs_path)
    output_path = Path(output_dir)

    write_csv(
        output_path / "funnel_overview.csv",
        build_funnel_overview(packet),
        [
            "step_order",
            "step",
            "sessions",
            "next_step",
            "next_step_sessions",
            "step_conversion_rate",
            "dropoff_rate",
            "metric_source",
        ],
    )
    write_csv(
        output_path / "segment_opportunity.csv",
        build_segment_opportunity(opportunity_rows),
        [
            "segment_name",
            "user_source",
            "user_medium",
            "device_category",
            "eligible_sessions",
            "begin_checkout_sessions",
            "purchase_sessions",
            "revenue",
            "segment_conversion_rate",
            "benchmark_conversion_rate",
            "conversion_rate_gap",
            "average_order_value",
            "estimated_missed_conversions",
            "estimated_revenue_opportunity",
            "metric_source",
        ],
    )
    write_csv(
        output_path / "experiment_feasibility.csv",
        build_experiment_feasibility(packet),
        ["metric_name", "metric_value", "metric_source"],
    )
    write_csv(
        output_path / "kpi_summary.csv",
        build_kpi_summary(packet),
        ["metric_name", "metric_value", "metric_source"],
    )


if __name__ == "__main__":
    build_tableau_exports()
