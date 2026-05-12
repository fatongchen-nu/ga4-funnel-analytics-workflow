# Tableau Automation

This project can automate Tableau datasource publishing after the metric evidence layer is generated.

## Supported Automation

1. Generate dashboard-ready CSV files.
2. Convert those CSV files into a Tableau `.hyper` extract.
3. Publish the `.hyper` datasource, or an existing workbook template, to Tableau Cloud or Tableau Server.

The script does not generate visual dashboard layouts from scratch. For production-quality dashboards, create a Tableau workbook template once, connect it to the published datasource, then republish or refresh the datasource through this workflow.

## Install Optional Tableau Dependencies

```bash
pip install -r requirements-tableau.txt
```

## Build Local Tableau Files

Run the evidence and Tableau export steps:

```bash
python src/build_metric_evidence_packet.py
python src/mock_provider.py
python src/build_tableau_exports.py
python src/build_tableau_hyper.py
```

This creates:

```text
tableau/funnel_overview.csv
tableau/segment_opportunity.csv
tableau/experiment_feasibility.csv
tableau/kpi_summary.csv
tableau/ga4_funnel_portfolio.hyper
```

## Tableau Cloud / Server Auth

Create a Tableau Personal Access Token, then set these environment variables:

```bash
export TABLEAU_SERVER_URL="https://prod-useast-a.online.tableau.com"
export TABLEAU_SITE_ID="your-site-content-url"
export TABLEAU_TOKEN_NAME="your-token-name"
export TABLEAU_TOKEN_VALUE="your-token-value"
export TABLEAU_PROJECT_NAME="Default"
```

Do not commit token values.

## Dry-Run Publish Validation

The publisher defaults to dry-run mode:

```bash
python src/publish_tableau.py
```

## Publish Datasource

Only run this when you intentionally want to call the Tableau API:

```bash
python src/publish_tableau.py --confirm-live-api
```

## Publish Workbook Template

If you have a packaged Tableau workbook template:

```bash
python src/publish_tableau.py \
  --publish-type workbook \
  --path tableau/ga4_funnel_dashboard.twbx \
  --name "GA4 Funnel Portfolio Dashboard" \
  --confirm-live-api
```

## Evidence Rule

Any Tableau annotation or dashboard text should reference fields from:

```text
outputs/metric_evidence_packet.json
```
