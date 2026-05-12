"""Local mock provider for evidence-constrained memo generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MockProvider:
    """Drafts narrative from a metric evidence packet without calling live APIs."""

    def generate_executive_memo(self, evidence_packet: dict[str, Any]) -> str:
        project = evidence_packet.get("project", {})
        funnel = evidence_packet.get("funnel", {})
        opportunity = evidence_packet.get("opportunity", {})
        experiment = evidence_packet.get("experiment_feasibility", {})

        lines = [
            "# Executive Memo Draft",
            "",
            "## Context",
            self._context(project),
            "",
            "## Evidence Summary",
            f"- Top funnel step: {self._field('funnel', funnel, 'top_dropoff_step')}",
            f"- Top segment: {self._field('opportunity', opportunity, 'segment_name')}",
            f"- Benchmark field: {self._field('opportunity', opportunity, 'benchmark_name')}",
            f"- Estimated missed conversions: {self._field('opportunity', opportunity, 'estimated_missed_conversions')}",
            f"- Estimated revenue opportunity: {self._field('opportunity', opportunity, 'estimated_revenue_opportunity')}",
            "",
            "## Experiment Feasibility",
            f"- Baseline conversion rate: {self._field('experiment_feasibility', experiment, 'baseline_conversion_rate')}",
            f"- MDE relative lift: {self._field('experiment_feasibility', experiment, 'mde_relative_lift')}",
            f"- Required sample per variant: {self._field('experiment_feasibility', experiment, 'required_sample_per_variant')}",
            f"- Estimated test duration days: {self._field('experiment_feasibility', experiment, 'estimated_test_duration_days')}",
            f"- Feasibility interpretation: {self._field('experiment_feasibility', experiment, 'feasibility_interpretation')}",
            f"- Recommended next step: {self._field('experiment_feasibility', experiment, 'recommended_next_step')}",
            "",
            "## Recommendation",
            self._recommendation(opportunity, experiment),
        ]
        return "\n".join(lines)

    def _recommendation(self, opportunity: dict[str, Any], experiment: dict[str, Any]) -> str:
        if not opportunity or not experiment:
            return "No recommendation is available because the required evidence fields are missing."

        missing = [
            key
            for key in (
                "segment_name",
                "estimated_missed_conversions",
                "estimated_revenue_opportunity",
            )
            if opportunity.get(key) is None
        ]
        missing += [
            key
            for key in (
                "required_sample_per_variant",
                "estimated_test_duration_days",
                "feasibility_interpretation",
                "recommended_next_step",
            )
            if experiment.get(key) is None
        ]
        if missing:
            return "No recommendation is available because these evidence fields are missing: " + ", ".join(missing)

        return (
            "Prioritize this opportunity for stakeholder review, but do not treat the current A/B test sizing "
            "as launch-ready until the traffic sufficiency issue has been resolved."
        )

    def _field(self, section_name: str, section: dict[str, Any], key: str) -> str:
        value = section.get(key)
        path = f"metric_evidence_packet.{section_name}.{key}"
        if value is None:
            return f"unavailable: {path}"
        return f"{value} (source: {path})"

    def _context(self, project: dict[str, Any]) -> str:
        period = project.get("analysis_period_label")
        if period is None:
            return (
                "This memo summarizes the GA4 funnel opportunity analysis based only on fields "
                "available in metric_evidence_packet.json. The analysis period is unavailable."
            )
        return (
            f"This memo summarizes the GA4 funnel opportunity analysis for {period} based only "
            "on fields available in metric_evidence_packet.json."
        )


def load_packet(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def write_memo(packet_path: str | Path, output_path: str | Path) -> None:
    packet = load_packet(packet_path)
    memo = MockProvider().generate_executive_memo(packet)
    Path(output_path).write_text(memo, encoding="utf-8")


if __name__ == "__main__":
    write_memo("outputs/metric_evidence_packet.json", "outputs/executive_memo.md")
