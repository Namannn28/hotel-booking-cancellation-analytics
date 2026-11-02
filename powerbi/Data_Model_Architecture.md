# Power BI Semantic Model & Architecture Guide

## Overview
This document outlines the data model architecture for the **Hotel Booking Revenue Optimization & Cancellation Analytics** report in Power BI.

The model transforms the flat 119,390-row booking ledger into an optimized **Dimensional Star Schema** for sub-second visual performance, cross-filtering, and DAX metric calculation.

```
       +--------------------+
       |     dim_dates      |
       +--------------------+
                 | (1)
                 |
                 | (*)
       +--------------------+          (1) +--------------------+
       |   hotel_bookings   |<-------------|   dim_properties   |
       |    (Fact Table)    |              +--------------------+
       +--------------------+
          | (*)          (*) |
          |                  |
          | (1)              | (1)
+--------------------+   +--------------------+
|    dim_channels    |   |   dim_geography    |
+--------------------+   +--------------------+
```

## Table Breakdown & Cardinality

| Table | Role | Key Column(s) | Cardinality | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`hotel_bookings`** | Central Fact | `booking_id` | N/A | 119,390 reservation event records with ADR, stays, status |
| **`dim_properties`** | Dimension | `hotel` | `1 : *` (Single) | Property attributes (City Hotel vs Resort Hotel) |
| **`dim_dates`** | Dimension | `date_key` | `1 : *` (Single) | Continuous calendar table (Year, Month, Day, Weekday, Quarter) |
| **`dim_channels`** | Dimension | `market_segment` | `1 : *` (Single) | Distribution channel hierarchy (Online TA, Direct, Corporate) |
| **`dim_geography`** | Dimension | `country_code` | `1 : *` (Single) | Guest origin countries, ISO codes, continent rollups |

## DAX Modeling Best Practices Applied
1. **Separation of Fact and Dimension Tables:** Eliminates redundancy in filter slicers and enhances Power BI VertiPaq engine compression.
2. **Explicit Measures:** All financial aggregations (`Realized Revenue`, `Lost Revenue`, `ADR`) are written in explicit DAX measures with divide-by-zero protection via `DIVIDE()`.
3. **Single-Direction Relationships:** Prevents circular dependency loops and ensures predictable filter propagation.
