-- ====================================================================
-- PulseMetrics-AI: 02. Customer Cohort Retention Matrix
-- Demonstrates: Date arithmetic, Conditional aggregation (CASE WHEN), Safe TRY_CAST
-- Business Value: Measures customer longevity and cohort-based churn decay curves
-- ====================================================================

WITH parsed_subscriptions AS (
    SELECT 
        customer_id,
        status,
        TRY_CAST(start_date AS DATE) AS start_dt,
        TRY_CAST(churn_date AS DATE) AS churn_dt
    FROM fact_subscriptions
),
customer_cohorts AS (
    SELECT 
        customer_id,
        STRFTIME('%Y-%m', start_dt) AS cohort_month,
        start_dt,
        status,
        churn_dt
    FROM parsed_subscriptions
    WHERE start_dt IS NOT NULL
),
cohort_tenure_calc AS (
    SELECT 
        customer_id,
        cohort_month,
        CASE 
            WHEN status = 'Active' THEN 24
            WHEN churn_dt IS NOT NULL THEN CAST((churn_dt - start_dt) / 30 AS INT)
            ELSE 1
        END AS months_retained
    FROM customer_cohorts
),
cohort_sizes AS (
    SELECT 
        cohort_month,
        COUNT(customer_id) AS total_cohort_customers
    FROM customer_cohorts
    GROUP BY 1
)
SELECT 
    c.cohort_month,
    s.total_cohort_customers AS cohort_size,
    100.0 AS m0_retention_pct,
    ROUND(COUNT(CASE WHEN c.months_retained >= 1 THEN 1 END) * 100.0 / s.total_cohort_customers, 1) AS m1_retention_pct,
    ROUND(COUNT(CASE WHEN c.months_retained >= 3 THEN 1 END) * 100.0 / s.total_cohort_customers, 1) AS m3_retention_pct,
    ROUND(COUNT(CASE WHEN c.months_retained >= 6 THEN 1 END) * 100.0 / s.total_cohort_customers, 1) AS m6_retention_pct,
    ROUND(COUNT(CASE WHEN c.months_retained >= 9 THEN 1 END) * 100.0 / s.total_cohort_customers, 1) AS m9_retention_pct,
    ROUND(COUNT(CASE WHEN c.months_retained >= 12 THEN 1 END) * 100.0 / s.total_cohort_customers, 1) AS m12_retention_pct
FROM cohort_tenure_calc c
JOIN cohort_sizes s ON c.cohort_month = s.cohort_month
GROUP BY c.cohort_month, s.total_cohort_customers
ORDER BY c.cohort_month ASC;
