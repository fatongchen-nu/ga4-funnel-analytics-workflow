# Tableau Dashboard Notes

The Tableau dashboard should use the same metric outputs that feed `metric_evidence_packet.json`.

## Planned Views

1. Funnel Overview
   - Sessions by funnel step.
   - Step conversion rates.
   - Drop-off rates.

2. Segment Opportunity
   - Channel, device, and campaign segments.
   - Benchmark conversion rate.
   - Estimated missed conversions.
   - Estimated revenue opportunity.

3. Experiment Feasibility
   - Baseline conversion rate.
   - MDE assumption.
   - Required sample per variant.
   - Estimated test duration.

## Dashboard Rule

Do not add Tableau annotations that are not supported by `metric_evidence_packet.json` or the source metric tables.
