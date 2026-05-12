-- Opportunity input table for metric_evidence_packet.json.
-- This query estimates transparent counterfactual opportunity by segment.
-- It does not rank with subjective actionability weights.
--
-- Input table:
-- ga4-funnel-portfolio-fatong.ga4_funnel_portfolio.funnel_metrics

WITH segment_metrics AS (
  SELECT
    user_source,
    user_medium,
    device_category,
    SUM(sessions) AS eligible_sessions,
    SUM(begin_checkout_sessions) AS begin_checkout_sessions,
    SUM(purchase_sessions) AS purchase_sessions,
    SUM(revenue) AS revenue,
    SAFE_DIVIDE(SUM(purchase_sessions), SUM(begin_checkout_sessions)) AS segment_conversion_rate,
    SAFE_DIVIDE(SUM(revenue), SUM(purchase_sessions)) AS average_order_value
  FROM `ga4-funnel-portfolio-fatong.ga4_funnel_portfolio.funnel_metrics`
  GROUP BY
    user_source,
    user_medium,
    device_category
),

benchmark AS (
  SELECT
    SAFE_DIVIDE(SUM(purchase_sessions), SUM(begin_checkout_sessions)) AS benchmark_conversion_rate
  FROM `ga4-funnel-portfolio-fatong.ga4_funnel_portfolio.funnel_metrics`
)

SELECT
  s.user_source,
  s.user_medium,
  s.device_category,
  s.eligible_sessions,
  s.begin_checkout_sessions,
  s.purchase_sessions,
  s.revenue,
  s.segment_conversion_rate,
  b.benchmark_conversion_rate,
  b.benchmark_conversion_rate - s.segment_conversion_rate AS conversion_rate_gap,
  s.average_order_value,
  GREATEST(
    0,
    s.begin_checkout_sessions * (b.benchmark_conversion_rate - s.segment_conversion_rate)
  ) AS estimated_missed_conversions,
  GREATEST(
    0,
    s.begin_checkout_sessions * (b.benchmark_conversion_rate - s.segment_conversion_rate) * s.average_order_value
  ) AS estimated_revenue_opportunity
FROM segment_metrics AS s
CROSS JOIN benchmark AS b
WHERE s.begin_checkout_sessions > 0;
