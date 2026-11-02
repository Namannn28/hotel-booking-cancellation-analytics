-- ====================================================================
-- PulseMetrics-AI: 05. Support Ticket Escalation & Churn Correlation
-- Demonstrates: Aggregated subqueries, CSAT metrics, Resolution latency impact
-- Business Value: Uncovers leading support indicators that precede customer churn
-- ====================================================================

WITH customer_ticket_summary AS (
    SELECT 
        customer_id,
        COUNT(ticket_id) AS total_support_tickets,
        SUM(escalated_to_tier2) AS tier2_escalations,
        ROUND(AVG(resolution_time_hours), 1) AS avg_resolution_time_hrs,
        ROUND(AVG(csat_rating), 2) AS avg_csat_score
    FROM fact_support_tickets
    GROUP BY customer_id
)
SELECT 
    s.status,
    c.tier,
    COUNT(s.customer_id) AS customer_count,
    ROUND(AVG(t.total_support_tickets), 1) AS avg_tickets_per_account,
    ROUND(AVG(t.tier2_escalations), 2) AS avg_tier2_escalations,
    ROUND(AVG(t.avg_resolution_time_hrs), 1) AS avg_support_sla_hours,
    ROUND(AVG(t.avg_csat_score), 2) AS avg_csat_rating,
    ROUND(SUM(s.arr), 2) AS cohort_arr
FROM fact_subscriptions s
JOIN dim_customers c ON s.customer_id = c.customer_id
LEFT JOIN customer_ticket_summary t ON s.customer_id = t.customer_id
GROUP BY s.status, c.tier
ORDER BY c.tier, s.status DESC;
