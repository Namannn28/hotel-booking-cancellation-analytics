-- ====================================================================
-- PulseMetrics-AI: 01. Monthly MRR / ARR Waterfall Analysis
-- Demonstrates: CTEs, Window Functions (SUM OVER, LAG), Safe TRY_CAST
-- Business Value: Tracks Net New ARR, Churned ARR, and Net Revenue Retention (NRR)
-- ====================================================================

WITH parsed_subscriptions AS (
    SELECT 
        customer_id,
        mrr,
        arr,
        status,
        TRY_CAST(start_date AS DATE) AS start_dt,
        TRY_CAST(churn_date AS DATE) AS churn_dt
    FROM fact_subscriptions
),
monthly_cohort_movements AS (
    SELECT 
        STRFTIME('%Y-%m', start_dt) AS activity_month,
        COUNT(customer_id) AS new_customers_added,
        SUM(mrr) AS new_mrr_added,
        SUM(arr) AS new_arr_added
    FROM parsed_subscriptions
    WHERE start_dt IS NOT NULL
    GROUP BY 1
),
churn_movements AS (
    SELECT 
        STRFTIME('%Y-%m', churn_dt) AS churn_month,
        COUNT(customer_id) AS churned_customers,
        SUM(mrr) AS churned_mrr,
        SUM(arr) AS churned_arr
    FROM parsed_subscriptions
    WHERE status = 'Churned' AND churn_dt IS NOT NULL
    GROUP BY 1
),
timeline AS (
    SELECT DISTINCT STRFTIME('%Y-%m', start_dt) AS report_month FROM parsed_subscriptions WHERE start_dt IS NOT NULL
    UNION
    SELECT DISTINCT STRFTIME('%Y-%m', churn_dt) FROM parsed_subscriptions WHERE churn_dt IS NOT NULL
),
waterfall_base AS (
    SELECT 
        t.report_month,
        COALESCE(m.new_customers_added, 0) AS new_customers,
        COALESCE(m.new_arr_added, 0.0) AS new_arr,
        COALESCE(c.churned_customers, 0) AS churned_customers,
        COALESCE(c.churned_arr, 0.0) AS lost_arr,
        COALESCE(m.new_arr_added, 0.0) - COALESCE(c.churned_arr, 0.0) AS net_new_arr
    FROM timeline t
    LEFT JOIN monthly_cohort_movements m ON t.report_month = m.activity_month
    LEFT JOIN churn_movements c ON t.report_month = c.churn_month
    WHERE t.report_month IS NOT NULL
),
cumulative_arr AS (
    SELECT 
        report_month,
        new_customers,
        new_arr,
        churned_customers,
        lost_arr,
        net_new_arr,
        -- Running cumulative active ARR trajectory
        SUM(net_new_arr) OVER (ORDER BY report_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS ending_arr
    FROM waterfall_base
)
SELECT 
    report_month,
    new_customers,
    new_arr,
    churned_customers,
    lost_arr,
    net_new_arr,
    ending_arr,
    -- Prior Month ARR
    LAG(ending_arr, 1) OVER (ORDER BY report_month) AS prior_month_arr,
    -- MoM ARR Growth %
    ROUND(
        ((ending_arr - LAG(ending_arr, 1) OVER (ORDER BY report_month)) / 
        NULLIF(LAG(ending_arr, 1) OVER (ORDER BY report_month), 0)) * 100.0, 2
    ) AS mom_arr_growth_pct
FROM cumulative_arr
ORDER BY report_month ASC;
