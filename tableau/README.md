# Tableau Dashboard Notes

The Tableau dashboard should use the same metric outputs that feed `metric_evidence_packet.json`.

## Tableau-Ready CSV Exports

Generate dashboard-ready CSV files after building `outputs/metric_evidence_packet.json`:

```bash
python src/build_tableau_exports.py
```

This creates:

```text
tableau/funnel_overview.csv
tableau/segment_opportunity.csv
tableau/experiment_feasibility.csv
tableau/kpi_summary.csv
```

Use these files directly in Tableau Public or Tableau Desktop with **Connect > Text file**.

For Hyper extract generation and Tableau Cloud/Server publishing, see:

```text
tableau/automation.md
```

## Planned Views

1. Funnel Overview
   - Data source: `tableau/funnel_overview.csv`
   - Sessions by funnel step.
   - Step conversion rates.
   - Drop-off rates.

2. Segment Opportunity
   - Data source: `tableau/segment_opportunity.csv`
   - Channel, device, and campaign segments.
   - Benchmark conversion rate.
   - Estimated missed conversions.
   - Estimated revenue opportunity.

3. Experiment Feasibility
   - Data source: `tableau/experiment_feasibility.csv`
   - Baseline conversion rate.
   - MDE assumption.
   - Required sample per variant.
   - Estimated test duration.

4. KPI Summary
   - Data source: `tableau/kpi_summary.csv`
   - Portfolio-friendly headline metrics.
   - Evidence source path for each displayed value.

## Dashboard Rule

Do not add Tableau annotations that are not supported by `metric_evidence_packet.json` or the source metric tables.
