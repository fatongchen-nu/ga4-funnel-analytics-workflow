# Project Agent Instructions

## Project Background

This project is a GA4 funnel analytics workflow for marketing analyst portfolio work. It uses AI to accelerate analysis, documentation, metric QA, and business memo drafting, but all final metrics must come from deterministic SQL or Python outputs.

AI should assist the workflow, not invent measurements. The source of truth for insights, funnel diagnostics, experiment feasibility, and dashboard commentary is the generated metric evidence layer.

## Skill Routing

- Use `market-funnel` for funnel diagnosis, drop-off analysis, conversion path interpretation, and funnel optimization recommendations.
- Use `market-report` for executive-ready memos, stakeholder summaries, and final business recommendation reports.
- Use `analytics-tracking` for GA4 metric QA, event taxonomy checks, attribution logic review, tracking implementation review, and validation of metric definitions.
- Use `ga4-bigquery-schema` for GA4 BigQuery export schema reference, nested event parameter handling, and query pattern validation.
- Use `ga4-events` for GA4 event taxonomy, recommended ecommerce events, custom dimensions, and event naming validation.
- Use `utm-builder` for UTM naming conventions, channel grouping logic, campaign parameter QA, and source / medium consistency checks.
- Use `conversion-debug` for cross-platform conversion tracking diagnosis, event firing checks, and funnel measurement troubleshooting.
- Use `ab-test-setup` or `experiment-designer` for A/B test design, hypothesis framing, primary and guardrail metrics, MDE, power analysis, sample size, and test duration validation.

## Data And AI Rules

- Do not invent numbers, trends, percentages, segment names, conversion rates, revenue values, or sample size estimates.
- Every numeric claim must reference a field from `metric_evidence_packet.json`.
- Every business recommendation must be traceable to one or more fields in `metric_evidence_packet.json`.
- If a metric is missing from `metric_evidence_packet.json`, state that the metric is unavailable and identify the required SQL or Python output needed to support the claim.
- Use only `MockProvider` for AI-generated summaries or memo generation.
- Do not call real LLM APIs, OpenAI APIs, Claude APIs, marketing platform APIs, GA4 APIs, Google Ads APIs, or any other live commercial APIs.
- Treat AI outputs as draft narrative only. SQL and Python outputs remain the source of truth.
- Prefer explicit evidence references such as `metric_evidence_packet.funnel.top_dropoff.step` or `metric_evidence_packet.experiment.required_sample_per_variant` when writing memos or recommendations.

## Directory Structure

Use the following project structure:

```text
/sql
/src
/ai_workflow
/tableau
```

- `/sql`: SQL queries for GA4 event extraction, sessionization, funnel tables, channel analysis, and metric evidence inputs.
- `/src`: Python source code for metric processing, experiment feasibility calculations, evidence packet generation, and `MockProvider`.
- `/ai_workflow`: prompt templates, AI-assisted QA checklists, generated evidence-backed memos, and workflow documentation.
- `/tableau`: Tableau workbook files, dashboard exports, screenshots, and dashboard documentation.
