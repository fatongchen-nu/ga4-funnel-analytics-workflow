# Tableau Workbook Manifest

The portfolio-ready dashboard should include a real Tableau workbook export:

```text
tableau/ga4_funnel_dashboard.twbx
```

## Status

Current project state:

- Tableau-ready CSV exports are generated locally.
- Optional Hyper extract generation is implemented.
- Tableau Cloud/Server publishing automation is implemented.
- A finished `.twbx` dashboard file still needs to be created in Tableau Public or Tableau Desktop.

## Required Data Sources

Use the generated files:

```text
tableau/funnel_overview.csv
tableau/segment_opportunity.csv
tableau/experiment_feasibility.csv
tableau/kpi_summary.csv
```

Optional packaged extract:

```text
tableau/ga4_funnel_portfolio.hyper
```

## Required Dashboard Tabs

### Funnel Overview

Purpose: show where the ecommerce journey loses the most sessions.

Required fields:

- `step_order`
- `step`
- `sessions`
- `step_conversion_rate`
- `dropoff_rate`

Recommended view:

- Horizontal funnel or descending bar chart by `sessions`
- Label `dropoff_rate`
- Sort by `step_order`

### Segment Opportunity

Purpose: rank channel/device opportunities by estimated revenue impact.

Required fields:

- `segment_name`
- `user_source`
- `user_medium`
- `device_category`
- `segment_conversion_rate`
- `benchmark_conversion_rate`
- `estimated_missed_conversions`
- `estimated_revenue_opportunity`

Recommended view:

- Bar chart sorted by `estimated_revenue_opportunity`
- Tooltip includes conversion gap and benchmark conversion rate
- Highlight `google / organic / desktop`

### Experiment Feasibility

Purpose: explain whether the opportunity is testable with available traffic.

Required fields:

- `metric_name`
- `metric_value`
- `metric_source`

Required note:

```text
The 253-day estimate is a traffic sufficiency warning. The selected segment does not have enough eligible checkout traffic for a practical 10% relative-lift A/B test, so the next step is to expand the eligible population, combine similar segments, choose a larger practical effect size, or use a quasi-experimental design.
```

### KPI Summary

Purpose: provide executive context without replacing the evidence views.

Recommended KPI cards:

- Events analyzed
- Top drop-off step
- Top opportunity segment
- Estimated revenue opportunity

## Evidence Rule

Every number and annotation in the workbook must trace back to:

```text
outputs/metric_evidence_packet.json
```

or one of the generated Tableau CSV files.
