-- ====================================================================
-- PulseMetrics-AI: 04. Product Engagement & Feature Stickiness Analysis
-- Demonstrates: Multi-table joins, Percentile groupings, Correlation prep
-- Business Value: Identifies core feature adoption drivers that correlate with retention
-- ====================================================================

SELECT 
    c.tier,
    s.status,
    COUNT(c.customer_id) AS total_customers,
    ROUND(AVG(u.active_seat_utilization) * 100.0, 1) AS avg_seat_utilization_pct,
    ROUND(AVG(u.avg_weekly_logins), 2) AS avg_weekly_logins_per_user,
    ROUND(AVG(u.active_features_count), 1) AS avg_active_features,
    ROUND(AVG(u.nps_score), 2) AS avg_nps_score,
    ROUND(AVG(u.monthly_api_calls), 0) AS avg_monthly_api_calls,
    ROUND(AVG(s.mrr), 2) AS avg_mrr
FROM dim_customers c
JOIN fact_subscriptions s ON c.customer_id = s.customer_id
JOIN fact_product_usage u ON c.customer_id = u.customer_id
GROUP BY c.tier, s.status
ORDER BY c.tier, s.status DESC;
