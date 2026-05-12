-- Session-level funnel metrics.
-- This query expects the event base logic from 01_ga4_event_base.sql.
-- Data source: bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*
-- Available period: 2020-11-01 through 2021-01-31.

WITH events AS (
  SELECT
    PARSE_DATE('%Y%m%d', event_date) AS event_date,
    event_timestamp,
    event_name,
    user_pseudo_id,
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
    ecommerce.purchase_revenue AS purchase_revenue
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
),

session_flags AS (
  SELECT
    session_key,
    ANY_VALUE(user_pseudo_id) AS user_pseudo_id,
    MIN(event_date) AS session_date,
    ANY_VALUE(user_source) AS user_source,
    ANY_VALUE(user_medium) AS user_medium,
    ANY_VALUE(user_campaign) AS user_campaign,
    ANY_VALUE(device_category) AS device_category,
    MAX(CASE WHEN event_name = 'session_start' THEN 1 ELSE 0 END) AS has_session_start,
    MAX(CASE WHEN event_name = 'view_item' THEN 1 ELSE 0 END) AS has_view_item,
    MAX(CASE WHEN event_name = 'add_to_cart' THEN 1 ELSE 0 END) AS has_add_to_cart,
    MAX(CASE WHEN event_name = 'begin_checkout' THEN 1 ELSE 0 END) AS has_begin_checkout,
    MAX(CASE WHEN event_name = 'purchase' THEN 1 ELSE 0 END) AS has_purchase,
    SUM(CASE WHEN event_name = 'purchase' THEN COALESCE(purchase_revenue, 0) ELSE 0 END) AS revenue
  FROM events
  GROUP BY session_key
)

SELECT
  session_date,
  user_source,
  user_medium,
  user_campaign,
  device_category,
  COUNT(DISTINCT session_key) AS sessions,
  SUM(has_view_item) AS view_item_sessions,
  SUM(has_add_to_cart) AS add_to_cart_sessions,
  SUM(has_begin_checkout) AS begin_checkout_sessions,
  SUM(has_purchase) AS purchase_sessions,
  SUM(revenue) AS revenue,
  SAFE_DIVIDE(SUM(has_add_to_cart), SUM(has_view_item)) AS view_to_cart_rate,
  SAFE_DIVIDE(SUM(has_begin_checkout), SUM(has_add_to_cart)) AS cart_to_checkout_rate,
  SAFE_DIVIDE(SUM(has_purchase), SUM(has_begin_checkout)) AS checkout_to_purchase_rate,
  SAFE_DIVIDE(SUM(has_purchase), COUNT(DISTINCT session_key)) AS session_purchase_rate
FROM session_flags
GROUP BY
  session_date,
  user_source,
  user_medium,
  user_campaign,
  device_category;
