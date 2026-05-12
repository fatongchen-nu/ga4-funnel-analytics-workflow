# AI-Assisted GA4 Funnel Analytics Workflow

This project is a portfolio-ready marketing analytics workflow for diagnosing GA4 ecommerce funnel opportunities. It uses AI as an analyst accelerator for QA, synthesis, and executive memo drafting, while keeping all final metrics deterministic and reproducible through SQL and Python.

The key principle is simple: AI can help explain the evidence, but it cannot create the evidence.

## Dataset

This project uses Google's public GA4 ecommerce BigQuery sample dataset:

```text
bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*
```

The dataset contains obfuscated GA4 BigQuery event export data from the Google Merchandise Store for `2020-11-01` through `2021-01-31`.

Official reference:

- https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset
- https://support.google.com/analytics/answer/7029846

Because the data is obfuscated, analysis should explicitly note that some fields may contain placeholder values such as `NULL`, empty strings, or `<Other>`, and internal consistency may be limited.

## Project Goal

Build a GA4 funnel analytics workflow that can:

- Transform GA4 BigQuery event data into clean funnel and channel metrics.
- Identify material conversion opportunities from the available data instead of assuming a predefined storyline.
- Estimate conversion and revenue opportunity using transparent counterfactual benchmarks.
- Evaluate experiment feasibility using baseline conversion rate, MDE, statistical power, required sample size, and estimated test duration.
- Generate an executive memo from a structured `metric_evidence_packet.json` using a local `MockProvider`, without calling live LLM APIs.
- Support Tableau dashboard workflows through generated CSV extracts, optional Hyper extract creation, and optional Tableau Cloud/Server publishing.

## What Makes This AI-Assisted

AI is used to accelerate analyst work:

- SQL review and metric QA.
- GA4 event taxonomy checks.
- Funnel diagnosis narrative.
- Executive memo drafting.
- Experiment design review.

AI is not used to calculate, invent, or backfill metrics. Every numeric claim must come from `metric_evidence_packet.json`.

## Repository Structure

```text
/sql
/src
/ai_workflow
/tableau
/data
/outputs
```

- `/sql`: BigQuery SQL templates for GA4 event extraction, sessionization, funnel tables, channel analysis, and evidence inputs.
- `/src`: Python code for metric processing, evidence packet generation, experiment feasibility, and `MockProvider`.
- `/ai_workflow`: AI-assisted QA checklists, prompt templates, and memo generation workflow.
- `/tableau`: Dashboard planning notes, calculated field documentation, screenshots, and workbook exports.
- `/data`: Local sample exports or input CSV files. Do not commit private or sensitive data.
- `/outputs`: Generated metric packets, memo drafts, and analysis outputs.

## Source Of Truth

The source of truth is:

```text
outputs/metric_evidence_packet.json
```

Any executive memo, Tableau annotation, business recommendation, or experiment decision must trace back to a field in that file.

## No Live API Policy

This project intentionally avoids live commercial APIs for the AI layer. Memo generation uses `MockProvider` only. In a production environment, the provider interface could be swapped for a real LLM API, but this portfolio version remains local, reproducible, and evidence-constrained.

Tableau publishing is optional and explicit. The Tableau publisher defaults to dry-run mode and requires `--confirm-live-api` before it contacts Tableau Cloud or Tableau Server. With Tableau Cloud/Server API credentials and an existing Tableau workbook template, the workflow can publish a finished dashboard artifact; the API path is template-based rather than dashboard-authoring-from-scratch.

## Planned Workflow

1. Extract GA4 event and session metrics with BigQuery SQL.
2. Use the Google public dataset as the initial source of truth.
3. Use Python to generate `metric_evidence_packet.json`.
4. Use `MockProvider` to draft an executive memo from the evidence packet.
5. Build Tableau-ready CSV files and, optionally, a Tableau Hyper extract from the same metric outputs.
6. Publish a datasource or workbook template to Tableau Cloud/Server only when the user explicitly provides credentials and confirms the live API call.
7. Document recommendations only when they are supported by the evidence packet.

## Current Portfolio Outputs

The current deterministic run identifies `view_item_to_add_to_cart` as the largest funnel drop-off and `google / organic / desktop` as the highest estimated revenue opportunity segment. The experiment feasibility estimate returns a long test duration under the default 10% relative lift assumption because the selected segment has limited eligible checkout traffic. This should be interpreted as a traffic sufficiency warning, not a launch-ready A/B test recommendation.

Recommended next step for experimentation: expand the eligible population, combine similar segments, choose a larger practical effect size, or use a quasi-experimental design before committing to a randomized test.

## Tableau Workbook Status

The repository now generates Tableau-ready CSV files and an optional Hyper extract. A finished portfolio version should also include a real Tableau workbook export:

```text
tableau/ga4_funnel_dashboard.twbx
```

The workbook should be created in Tableau Public or Tableau Desktop from the generated files, then committed to the repository. See:

```text
tableau/workbook_manifest.md
```

Once that template exists, a user with Tableau Cloud/Server API credentials can run the publishing script to deliver the dashboard without manually re-uploading it through the Tableau UI:

```bash
python src/publish_tableau.py \
  --publish-type workbook \
  --path tableau/ga4_funnel_dashboard.twbx \
  --name "GA4 Funnel Portfolio Dashboard" \
  --confirm-live-api
```

## BigQuery Starting Point

Use this first query to confirm access and data coverage:

```sql
SELECT
  COUNT(*) AS event_count,
  COUNT(DISTINCT user_pseudo_id) AS user_count,
  COUNT(DISTINCT event_date) AS day_count,
  MIN(event_date) AS min_event_date,
  MAX(event_date) AS max_event_date
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`;
```

For command-line steps, see:

```text
ai_workflow/bigquery_runbook.md
```

For Tableau automation steps, see:

```text
tableau/automation.md
```

## GitHub Timing

Create or push to a GitHub repository after the first local checkpoint is complete:

- Project structure exists.
- README and AGENTS instructions are in place.
- Metric evidence schema is defined.
- Mock memo generation can run locally.
- No generated junk files or private data are staged.
