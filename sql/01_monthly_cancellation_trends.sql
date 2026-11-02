-- ====================================================================
-- 01. Monthly Booking Volume, Cancellation Rates & Revenue Loss
-- Demonstrates: CTEs, Window Functions (LAG, SUM OVER), Conditional Aggregation
-- Business Value: Identifies peak cancellation seasons and lost revenue spikes
-- ====================================================================

WITH monthly_bookings AS (
    SELECT 
        arrival_date_year,
        arrival_date_month,
        -- Generate sortable date order
        CASE arrival_date_month
            WHEN 'January' THEN 1 WHEN 'February' THEN 2 WHEN 'March' THEN 3
            WHEN 'April' THEN 4 WHEN 'May' THEN 5 WHEN 'June' THEN 6
            WHEN 'July' THEN 7 WHEN 'August' THEN 8 WHEN 'September' THEN 9
            WHEN 'October' THEN 10 WHEN 'November' THEN 11 WHEN 'December' THEN 12
        END AS month_num,
        hotel,
        COUNT(*) AS total_bookings,
        SUM(is_canceled) AS total_cancellations,
        ROUND(AVG(is_canceled) * 100.0, 2) AS cancellation_rate_pct,
        -- Realized Revenue = (weekend_nights + week_nights) * ADR for non-canceled bookings
        ROUND(SUM(CASE WHEN is_canceled = 0 THEN (stays_in_weekend_nights + stays_in_week_nights) * adr ELSE 0 END), 2) AS realized_revenue,
        -- Lost Revenue = (weekend_nights + week_nights) * ADR for canceled bookings
        ROUND(SUM(CASE WHEN is_canceled = 1 THEN (stays_in_weekend_nights + stays_in_week_nights) * adr ELSE 0 END), 2) AS lost_revenue,
        ROUND(AVG(adr), 2) AS avg_daily_rate
    FROM hotel_bookings
    WHERE adr >= 0
    GROUP BY arrival_date_year, arrival_date_month, month_num, hotel
)
SELECT 
    arrival_date_year,
    arrival_date_month,
    hotel,
    total_bookings,
    total_cancellations,
    cancellation_rate_pct,
    realized_revenue,
    lost_revenue,
    avg_daily_rate,
    -- Prior Month Realized Revenue via LAG()
    LAG(realized_revenue, 1) OVER (PARTITION BY hotel ORDER BY arrival_date_year, month_num) AS prior_month_revenue,
    -- MoM Realized Revenue Growth %
    ROUND(
        ((realized_revenue - LAG(realized_revenue, 1) OVER (PARTITION BY hotel ORDER BY arrival_date_year, month_num)) / 
        NULLIF(LAG(realized_revenue, 1) OVER (PARTITION BY hotel ORDER BY arrival_date_year, month_num), 0)) * 100.0, 2
    ) AS mom_revenue_growth_pct
FROM monthly_bookings
ORDER BY hotel, arrival_date_year, month_num;
