-- GA4 ecommerce event base table.
-- Data source: Google public GA4 ecommerce sample dataset.
-- Dataset: bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*
-- Available period: 2020-11-01 through 2021-01-31.

WITH events AS (
  SELECT
    PARSE_DATE('%Y%m%d', event_date) AS event_date,
    event_timestamp,
    event_name,
    user_pseudo_id,
    (
      SELECT value.int_value
      FROM UNNEST(event_params)
      WHERE key = 'ga_session_id'
    ) AS ga_session_id,
    CONCAT(
      user_pseudo_id,
      '-',
      CAST((
        SELECT value.int_value
        FROM UNNEST(event_params)
        WHERE key = 'ga_session_id'
      ) AS STRING)
    ) AS session_key,
    traffic_source.source AS user_source,
    traffic_source.medium AS user_medium,
    traffic_source.name AS user_campaign,
    device.category AS device_category,
    ecommerce.purchase_revenue AS purchase_revenue,
    items
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
)

SELECT *
FROM events
WHERE event_name IN (
  'session_start',
  'view_item',
  'add_to_cart',
  'begin_checkout',
  'purchase'
);
