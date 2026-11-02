-- ====================================================================
-- 02. Lead Time Buckets & Cancellation Risk Analysis
-- Demonstrates: CASE statements, Segmented Aggregation, Revenue Attrition
-- Business Value: Shows how booking advance window correlates with cancellation likelihood
-- ====================================================================

WITH lead_time_segmented AS (
    SELECT 
        hotel,
        CASE 
            WHEN lead_time <= 7 THEN '1. Last Minute (0-7 Days)'
            WHEN lead_time BETWEEN 8 AND 30 THEN '2. Short Notice (8-30 Days)'
            WHEN lead_time BETWEEN 31 AND 90 THEN '3. Moderate Advance (31-90 Days)'
            WHEN lead_time BETWEEN 91 AND 180 THEN '4. Long Advance (91-180 Days)'
            ELSE '5. Early Bird (>180 Days)'
        END AS lead_time_bucket,
        is_canceled,
        (stays_in_weekend_nights + stays_in_week_nights) * adr AS booking_value,
        adr
    FROM hotel_bookings
    WHERE adr >= 0
)
SELECT 
    hotel,
    lead_time_bucket,
    COUNT(*) AS total_reservations,
    SUM(is_canceled) AS canceled_reservations,
    ROUND(AVG(is_canceled) * 100.0, 2) AS cancellation_rate_pct,
    ROUND(AVG(adr), 2) AS avg_adr,
    ROUND(SUM(CASE WHEN is_canceled = 1 THEN booking_value ELSE 0 END), 2) AS lost_booking_revenue,
    ROUND(SUM(CASE WHEN is_canceled = 0 THEN booking_value ELSE 0 END), 2) AS realized_booking_revenue
FROM lead_time_segmented
GROUP BY hotel, lead_time_bucket
ORDER BY hotel, lead_time_bucket;
