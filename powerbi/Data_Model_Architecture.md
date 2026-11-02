# Power BI Semantic Model & Star Schema Architecture

## Overview
The PulseMetrics semantic model is architected around a strict **Dimensional Star Schema** designed for sub-second query performance and clean DAX calculations in Power BI and Microsoft Fabric.

```
       +--------------------+
       |   dim_customers    |
       +--------------------+
                 | (1)
                 |
                 | (*)
       +--------------------+          (1) +--------------------+
       | fact_subscriptions |<-------------|     dim_plans      |
       +--------------------+              +--------------------+
                 | (1)
                 |
                 | (1)
       +--------------------+
       | fact_product_usage |
       +--------------------+
                 | (1)
                 |
                 | (*)
       +--------------------+
       |fact_support_tickets|
       +--------------------+
```

## Table Roles & Cardinality

| Table Name | Type | Key Columns | Cardinality & Filter Direction | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`dim_customers`** | Dimension | `customer_id` (PK) | 1 to Many (`1:*`), Single | Core customer profile (Industry, Region, Tier, Size) |
| **`dim_plans`** | Dimension | `plan_tier` (PK) | 1 to Many (`1:*`), Single | Tier metadata, base pricing, SLA standards |
| **`fact_subscriptions`**| Fact | `subscription_id` (PK), `customer_id` (FK) | Core Fact | Subscription contracts, MRR, ARR, Billing status |
| **`fact_product_usage`** | Fact (Degenerate) | `customer_id` (PK/FK) | 1 to 1 (`1:1`), Bi-directional | Weekly logins, seat utilization %, NPS, API volume |
| **`fact_support_tickets`**| Fact | `ticket_id` (PK), `customer_id` (FK) | Many to 1 (`*:1`), Single | Support cases, resolution latency, CSAT scores |

## Best Practices Implemented
1. **Single-Direction Filtering**: Enforced single-directional filtering on dimension tables to avoid circular dependency paths and DAX ambiguity.
2. **Hidden Foreign Keys**: All raw surrogate keys (`customer_id`, `subscription_id`) are hidden from report view, exposing clean business attributes.
3. **Calculated Columns vs Measures**: Row-level transforms were kept strictly in SQL ETL. All metrics (ARR, Churn %, NRR) are computed dynamically via optimized DAX measures.
