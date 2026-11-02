-- ====================================================================
-- PulseMetrics-AI: 03. Customer RFM Segmentation Analysis
-- Demonstrates: NTILE Window Functions, Multi-factor composite scoring, CASE mapping
-- Business Value: Segments accounts into Champions, Loyal, At-Risk, and Churned cohorts
-- ====================================================================

WITH rfm_raw_metrics AS (
    SELECT 
        c.customer_id,
        c.company_name,
        c.industry,
        c.tier,
        s.status,
        s.mrr,
        s.arr,
        u.last_active_days_ago AS recency_days,
        u.avg_weekly_logins * 4 AS monthly_frequency,
        s.arr AS monetary_value
    FROM dim_customers c
    JOIN fact_subscriptions s ON c.customer_id = s.customer_id
    JOIN fact_product_usage u ON c.customer_id = u.customer_id
),
rfm_ranked AS (
    SELECT 
        customer_id,
        company_name,
        industry,
        tier,
        status,
        recency_days,
        monthly_frequency,
        monetary_value,
        -- R Score: Lower days ago = higher rank (1 to 4)
        NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,
        -- F Score: Higher login frequency = higher rank (1 to 4)
        NTILE(4) OVER (ORDER BY monthly_frequency ASC) AS f_score,
        -- M Score: Higher ARR = higher rank (1 to 4)
        NTILE(4) OVER (ORDER BY monetary_value ASC) AS m_score
    FROM rfm_raw_metrics
),
rfm_composite AS (
    SELECT 
        *,
        (r_score * 100 + f_score * 10 + m_score) AS rfm_combined_code,
        ROUND((r_score + f_score + m_score) / 3.0, 2) AS rfm_avg_score
    FROM rfm_ranked
)
SELECT 
    customer_id,
    company_name,
    industry,
    tier,
    status,
    recency_days,
    monthly_frequency,
    monetary_value,
    r_score,
    f_score,
    m_score,
    rfm_combined_code,
    rfm_avg_score,
    CASE 
        WHEN status = 'Churned' THEN 'Lost / Churned'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champion Accounts'
        WHEN r_score >= 3 AND f_score >= 2 THEN 'Loyal Power Users'
        WHEN r_score >= 3 AND f_score <= 2 THEN 'Potential Loyalists'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'Need Attention / Risk'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'High-Value At Risk'
        ELSE 'Hibernating / Low Engagement'
    END AS customer_rfm_segment
FROM rfm_composite
ORDER BY monetary_value DESC;
