-- ====================================================================
-- PulseMetrics-AI: Dimensional Star Schema DDL
-- Compatible with PostgreSQL, DuckDB, Snowflake, and SQLite
-- ====================================================================

-- 1. Customer Dimension
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    company_size VARCHAR(50) NOT NULL,
    tier VARCHAR(50) NOT NULL,
    signup_date DATE NOT NULL,
    primary_contact_role VARCHAR(100)
);

-- 2. Plan Tier Dimension
CREATE TABLE IF NOT EXISTS dim_plans (
    plan_tier VARCHAR(50) PRIMARY KEY,
    base_mrr NUMERIC(10, 2) NOT NULL,
    included_seats INT NOT NULL,
    support_tier VARCHAR(50) NOT NULL
);

-- 3. Subscription Fact Table
CREATE TABLE IF NOT EXISTS fact_subscriptions (
    subscription_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES dim_customers(customer_id),
    plan_tier VARCHAR(50) REFERENCES dim_plans(plan_tier),
    mrr NUMERIC(10, 2) NOT NULL,
    arr NUMERIC(12, 2) NOT NULL,
    licensed_seats INT NOT NULL,
    billing_cycle VARCHAR(20) NOT NULL,
    discount_percent NUMERIC(5, 2) DEFAULT 0.0,
    status VARCHAR(20) NOT NULL, -- 'Active' or 'Churned'
    start_date DATE NOT NULL,
    churn_date DATE
);

-- 4. Product Usage Telemetry Fact Table
CREATE TABLE IF NOT EXISTS fact_product_usage (
    customer_id VARCHAR(50) PRIMARY KEY REFERENCES dim_customers(customer_id),
    avg_weekly_logins NUMERIC(5, 2) NOT NULL,
    active_seat_utilization NUMERIC(5, 2) NOT NULL,
    monthly_api_calls BIGINT NOT NULL,
    active_features_count INT NOT NULL,
    nps_score INT CHECK (nps_score BETWEEN 0 AND 10),
    storage_used_gb NUMERIC(8, 2) NOT NULL,
    last_active_days_ago INT NOT NULL
);

-- 5. Support Tickets Fact Table
CREATE TABLE IF NOT EXISTS fact_support_tickets (
    ticket_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES dim_customers(customer_id),
    category VARCHAR(100) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    resolution_time_hours NUMERIC(6, 2) NOT NULL,
    csat_rating INT CHECK (csat_rating BETWEEN 1 AND 5),
    escalated_to_tier2 INT DEFAULT 0
);
