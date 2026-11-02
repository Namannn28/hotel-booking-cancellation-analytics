-- ====================================================================
-- 04. Top Origin Countries & Cancellation Rankings
-- Demonstrates: DENSE_RANK() Window function, Country filtering, Revenue impact
-- Business Value: Highlights geographic segments requiring targeted deposit strategies
-- ====================================================================

WITH country_stats AS (
    SELECT 
        country,
        COUNT(*) AS total_bookings,
        SUM(is_canceled) AS cancellations,
        ROUND(AVG(is_canceled) * 100.0, 2) AS cancellation_rate_pct,
        ROUND(AVG(adr), 2) AS avg_adr,
        ROUND(SUM(CASE WHEN is_canceled = 0 THEN (stays_in_weekend_nights + stays_in_week_nights) * adr ELSE 0 END), 2) AS realized_revenue,
        ROUND(SUM(CASE WHEN is_canceled = 1 THEN (stays_in_weekend_nights + stays_in_week_nights) * adr ELSE 0 END), 2) AS lost_revenue
    FROM hotel_bookings
    WHERE country IS NOT NULL AND country != 'NULL' AND country != ''
    GROUP BY country
    HAVING COUNT(*) >= 500 -- Filter statistically significant countries
)
SELECT 
    country,
    total_bookings,
    cancellations,
    cancellation_rate_pct,
    DENSE_RANK() OVER (ORDER BY cancellation_rate_pct DESC) AS cancellation_risk_rank,
    realized_revenue,
    lost_revenue,
    avg_adr
FROM country_stats
ORDER BY total_bookings DESC
LIMIT 15;
