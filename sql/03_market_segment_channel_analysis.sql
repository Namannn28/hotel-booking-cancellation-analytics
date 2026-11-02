-- ====================================================================
-- 03. Distribution Channel & Market Segment Performance
-- Demonstrates: Multi-dimensional grouping, Share of Total calculations (Window SUM)
-- Business Value: Pinpoints high-risk acquisition channels (e.g. Online TAs vs Direct)
-- ====================================================================

WITH channel_summary AS (
    SELECT 
        distribution_channel,
        market_segment,
        COUNT(*) AS total_bookings,
        SUM(is_canceled) AS cancellations,
        ROUND(AVG(is_canceled) * 100.0, 2) AS cancellation_rate_pct,
        ROUND(AVG(adr), 2) AS avg_adr,
        ROUND(SUM(CASE WHEN is_canceled = 0 THEN (stays_in_weekend_nights + stays_in_week_nights) * adr ELSE 0 END), 2) AS net_revenue
    FROM hotel_bookings
    WHERE distribution_channel != 'Undefined' AND market_segment != 'Undefined'
    GROUP BY distribution_channel, market_segment
)
SELECT 
    distribution_channel,
    market_segment,
    total_bookings,
    -- Channel volume share of entire hotel bookings portfolio
    ROUND((total_bookings * 100.0) / SUM(total_bookings) OVER (), 2) AS volume_share_pct,
    cancellations,
    cancellation_rate_pct,
    avg_adr,
    net_revenue,
    ROUND((net_revenue * 100.0) / SUM(net_revenue) OVER (), 2) AS revenue_share_pct
FROM channel_summary
WHERE total_bookings >= 50
ORDER BY total_bookings DESC;
