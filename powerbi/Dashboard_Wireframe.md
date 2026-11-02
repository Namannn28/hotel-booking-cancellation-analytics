# Power BI Dashboard Visual Wireframe & Layout Specification

## Report Canvas Layout (16:9 1920x1080)

### Page 1: Executive Revenue & Cancellation Overview
* **Header Bar (Navy #1B365D):** Title *"Hotel Revenue Optimization & Cancellation Recovery"*, Global Slicers: `Hotel Type`, `Year`, `Market Segment`.
* **Top Metric Ribbon (5 Cards):**
  1. `[Total Reservations]` (119,390)
  2. `[Cancellation Rate %]` (37.0% - Conditional Red if >35%)
  3. `[Realized Room Revenue]` ($18.42M)
  4. `[Lost Revenue from Cancellations]` ($11.22M)
  5. `[Average Daily Rate (ADR)]` ($101.83)
* **Middle Left (Area/Line Chart):** Monthly Booking & Cancellation Trends (Volume vs % Canceled over 2015-2017).
* **Middle Right (Clustered Bar Chart):** Lost Revenue & Cancellation Rate across Market Segments (Online TA vs Direct vs Corporate).
* **Bottom Row (Decomposition Tree / Map):** Global Guest Origin Map showing Top 10 origin countries with highest cancellation rates.

---

### Page 2: Lead Time Risk & Overbooking Strategy
* **Top Slicer Bar:** `Lead Time Bucket` (0-7 days, 8-30 days, 31-90 days, 91-180 days, >180 days).
* **Chart 1 (Waterfall / Bar):** Cancellation % Escalation by Lead Time Bucket (14% at 0-7 days jumping to 56% at >180 days).
* **Chart 2 (Heatmap Matrix):** Month vs Property Type showing Empirical Cancellation % and Recommended Overbooking Buffer %.
* **Chart 3 (Scatter Plot):** ADR vs Lead Time categorized by Confirmation vs Cancellation.
* **Operational Action Card:** Real-time overbooking recommendation calculator.
