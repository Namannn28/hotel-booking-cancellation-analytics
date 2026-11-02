-- ====================================================================
-- Hotel Booking Cancellation & Revenue Analytics
-- Schema DDL (DuckDB / PostgreSQL / Snowflake Compatible)
-- Data Source: Real-world Hotel Booking Demand Dataset (119,390 records)
-- ====================================================================

CREATE TABLE IF NOT EXISTS hotel_bookings (
    hotel VARCHAR(50) NOT NULL,
    is_canceled INT NOT NULL,
    lead_time INT NOT NULL,
    arrival_date_year INT NOT NULL,
    arrival_date_month VARCHAR(20) NOT NULL,
    arrival_date_week_number INT NOT NULL,
    arrival_date_day_of_month INT NOT NULL,
    stays_in_weekend_nights INT NOT NULL,
    stays_in_week_nights INT NOT NULL,
    adults INT NOT NULL,
    children NUMERIC(4, 1) DEFAULT 0,
    babies INT DEFAULT 0,
    meal VARCHAR(20),
    country VARCHAR(10),
    market_segment VARCHAR(50),
    distribution_channel VARCHAR(50),
    is_repeated_guest INT DEFAULT 0,
    previous_cancellations INT DEFAULT 0,
    previous_bookings_not_canceled INT DEFAULT 0,
    reserved_room_type VARCHAR(10),
    assigned_room_type VARCHAR(10),
    booking_changes INT DEFAULT 0,
    deposit_type VARCHAR(50),
    agent VARCHAR(20),
    company VARCHAR(20),
    days_in_waiting_list INT DEFAULT 0,
    customer_type VARCHAR(50),
    adr NUMERIC(10, 2) NOT NULL,
    required_car_parking_spaces INT DEFAULT 0,
    total_of_special_requests INT DEFAULT 0,
    reservation_status VARCHAR(50),
    reservation_status_date DATE
);
