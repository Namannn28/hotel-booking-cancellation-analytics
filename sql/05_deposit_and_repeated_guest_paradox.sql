-- ====================================================================
-- 05. Deposit Type Policy & Repeated Guest Loyalty Analysis
-- Demonstrates: Cross-tabulation, Boolean flags, Special requests impact
-- Business Value: Unveils the deposit anomaly and repeat guest retention power
-- ====================================================================

SELECT 
    hotel,
    deposit_type,
    CASE WHEN is_repeated_guest = 1 THEN 'Repeated Guest' ELSE 'First-Time Guest' END AS guest_loyalty_status,
    COUNT(*) AS total_bookings,
    SUM(is_canceled) AS cancellations,
    ROUND(AVG(is_canceled) * 100.0, 2) AS cancellation_rate_pct,
    ROUND(AVG(total_of_special_requests), 2) AS avg_special_requests,
    ROUND(AVG(adr), 2) AS avg_adr,
    ROUND(SUM(CASE WHEN is_canceled = 0 THEN (stays_in_weekend_nights + stays_in_week_nights) * adr ELSE 0 END), 2) AS realized_revenue
FROM hotel_bookings
GROUP BY hotel, deposit_type, is_repeated_guest
ORDER BY hotel, total_bookings DESC;
