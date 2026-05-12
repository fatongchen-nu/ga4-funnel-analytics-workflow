-- Confirm funnel event coverage before building conversion metrics.
-- Do not write funnel conclusions until this coverage table has been reviewed.

SELECT
  event_name,
  COUNT(*) AS event_count,
  COUNT(DISTINCT user_pseudo_id) AS user_count,
  COUNT(DISTINCT CONCAT(
    user_pseudo_id,
    '-',
    CAST((
      SELECT value.int_value
      FROM UNNEST(event_params)
      WHERE key = 'ga_session_id'
    ) AS STRING)
  )) AS session_count
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
  AND event_name IN (
    'session_start',
    'view_item',
    'add_to_cart',
    'begin_checkout',
    'purchase'
  )
GROUP BY event_name
ORDER BY event_count DESC;
