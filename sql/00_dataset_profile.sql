-- Profile the Google public GA4 ecommerce sample dataset before analysis.
-- Data source: bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*

SELECT
  COUNT(*) AS event_count,
  COUNT(DISTINCT user_pseudo_id) AS user_count,
  COUNT(DISTINCT event_date) AS day_count,
  MIN(event_date) AS min_event_date,
  MAX(event_date) AS max_event_date
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`;

