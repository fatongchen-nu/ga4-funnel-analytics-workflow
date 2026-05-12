# Metric QA Checklist

Use this checklist before writing any executive memo or Tableau annotation.

## GA4 Event QA

- Confirm required ecommerce events exist in the selected period: `session_start`, `view_item`, `add_to_cart`, `begin_checkout`, `purchase`.
- Confirm session logic uses `user_pseudo_id` plus `ga_session_id`.
- Confirm funnel steps are session-based unless the analysis explicitly states otherwise.
- Confirm purchase revenue is sourced from GA4 ecommerce fields, not AI-generated narrative.

## Channel And UTM QA

- Confirm source, medium, campaign, and channel grouping logic are documented.
- Flag unknown or missing campaign parameters instead of reclassifying them silently.
- Keep user acquisition fields separate from session acquisition fields if both are used.

## Evidence Packet QA

- Confirm every numeric memo claim appears in `metric_evidence_packet.json`.
- Confirm every recommendation cites at least one evidence packet field.
- If a metric is unavailable, do not estimate it in prose.
- Do not publish memo output until `qa.metric_definitions_reviewed` is true.

## Experiment QA

- Confirm baseline conversion rate comes from the selected segment and funnel step.
- Confirm MDE is documented as an assumption.
- Confirm alpha, power, required sample per variant, and estimated duration are included.
- Confirm guardrail metrics are named before recommending launch.

