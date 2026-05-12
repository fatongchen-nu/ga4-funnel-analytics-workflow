# BigQuery Runbook

Use this runbook to query the Google public GA4 ecommerce dataset.

## Authentication

If `bq query` fails with an expired token, run:

```bash
gcloud auth login
gcloud auth application-default login
```

Then confirm the active account:

```bash
gcloud auth list
gcloud config list project
```

## Dataset Profile

Run:

```bash
bq query --use_legacy_sql=false < sql/00_dataset_profile.sql
```

This validates access and confirms the dataset coverage before any analysis narrative is written.

## Event Coverage

Run:

```bash
bq query --use_legacy_sql=false < sql/04_event_coverage.sql
```

This confirms whether the funnel events needed for analysis are present in the selected date range.

## Funnel Metrics

Run:

```bash
bq query \
  --use_legacy_sql=false \
  --replace \
  --destination_table=ga4-funnel-portfolio-fatong:ga4_funnel_portfolio.funnel_metrics \
  < sql/02_funnel_metrics.sql
```

This saves the deterministic funnel metric table to:

```text
ga4-funnel-portfolio-fatong.ga4_funnel_portfolio.funnel_metrics
```

## Opportunity Inputs

Run:

```bash
bq query \
  --use_legacy_sql=false \
  --replace \
  --destination_table=ga4-funnel-portfolio-fatong:ga4_funnel_portfolio.opportunity_inputs \
  < sql/03_opportunity_inputs.sql
```

This saves the segment opportunity table to:

```text
ga4-funnel-portfolio-fatong.ga4_funnel_portfolio.opportunity_inputs
```

## Local Evidence Exports

Export the deterministic query results to local CSV files:

```bash
bq query --quiet --format=csv --max_rows=1000000 --use_legacy_sql=false < sql/00_dataset_profile.sql > data/dataset_profile.csv
bq query --quiet --format=csv --max_rows=1000000 --use_legacy_sql=false < sql/04_event_coverage.sql > data/event_coverage.csv
bq query --quiet --format=csv --max_rows=1000000 --use_legacy_sql=false 'SELECT * FROM `ga4-funnel-portfolio-fatong.ga4_funnel_portfolio.funnel_metrics`' > data/funnel_metrics.csv
bq query --quiet --format=csv --max_rows=1000000 --use_legacy_sql=false 'SELECT * FROM `ga4-funnel-portfolio-fatong.ga4_funnel_portfolio.opportunity_inputs`' > data/opportunity_inputs.csv
```

## Evidence Packet And Memo

Build the packet and memo:

```bash
python src/build_metric_evidence_packet.py
python src/mock_provider.py
```

Outputs:

```text
outputs/metric_evidence_packet.json
outputs/executive_memo.md
```

## Rule

Do not write business conclusions until the queried results have been saved into the metric evidence packet or a documented source metric table.
