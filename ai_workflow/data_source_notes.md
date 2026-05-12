# Data Source Notes

## Selected Dataset

This project uses Google's public GA4 ecommerce BigQuery sample dataset:

```text
bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*
```

Official documentation:

- https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset
- https://support.google.com/analytics/answer/7029846

## Dataset Scope

- Property type: GA4 ecommerce web implementation.
- Source business: Google Merchandise Store.
- Date range: `2020-11-01` through `2021-01-31`.
- Data type: obfuscated BigQuery event export data.

## Limitations To Mention In The Portfolio

- The dataset is obfuscated and should not be treated as a perfect mirror of the Google Analytics demo account.
- Some fields may contain placeholders, nulls, empty strings, or `<Other>`.
- Any analysis conclusion must be derived from the queried data, not from a predefined story.
- The dataset has only three months of data, so seasonality and long-term trend analysis should be limited.

## Initial BigQuery Check

Run:

```sql
SELECT
  COUNT(*) AS event_count,
  COUNT(DISTINCT user_pseudo_id) AS user_count,
  COUNT(DISTINCT event_date) AS day_count,
  MIN(event_date) AS min_event_date,
  MAX(event_date) AS max_event_date
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`;
```

Save the result into `metric_evidence_packet.json` before writing any project narrative about data coverage.
