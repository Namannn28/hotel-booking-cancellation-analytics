# Power BI Dashboard Visual Wireframe & Layout Guide

## Layout Overview (16:9 1920x1080 Aspect Ratio)

### 1. Header Banner (Height: 80px, Background: #1F4E79)
- **Left:** Logo + Title *"PulseMetrics-AI: Executive Revenue & Retention Intelligence"*
- **Right:** Slicers for `Date Range` (Slider), `Plan Tier` (Dropdown), `Industry` (Multi-select)

### 2. Top Metric Cards Row (KPI Banner)
- **Card 1:** `[Total ARR]` (Formatted as Currency `$#,##0`) + Target Delta
- **Card 2:** `[Active Customer Count]` (Formatted as Integer `#,##0`)
- **Card 3:** `[Customer Churn Rate %]` (Formatted as Percentage `0.0%`, Conditional Color: Green <15%, Red >20%)
- **Card 4:** `[Net Revenue Retention (NRR) %]` (Formatted as Percentage `0.0%`, Benchmark: 105%)
- **Card 5:** `[Quick Ratio]` (Target: >4.0)

### 3. Visual Grid Section (Middle Row)
- **Visual 1 (Left 50%):** Clustered Column Chart
  - **X-Axis:** `timeline[report_month]`
  - **Y-Axis:** `[New ARR]`, `[Expansion ARR]`, `[Contraction ARR]`, `[Lost Churned ARR]`
  - **Line Overlay:** `[Net New ARR]`
- **Visual 2 (Right 50%):** Matrix Table (Cohort Retention Heatmap)
  - **Rows:** `cohort_month`
  - **Columns:** `Month 0`, `Month 1`, `Month 3`, `Month 6`, `Month 9`, `Month 12`
  - **Values:** `[Cohort Retention Rate %]`
  - **Conditional Formatting:** Color scale background (Red for <60%, Yellow for 75%, Green for 90%+)

### 4. Bottom Row: Customer 360 & Operational SLAs
- **Visual 3 (Left 50%):** Scatter Plot
  - **X-Axis:** `[Avg Seat Utilization %]`
  - **Y-Axis:** `[Total ARR]`
  - **Legend:** `[Customer Health Status]`
  - **Tooltip:** `Company Name`, `Primary Contact Role`, `NPS Score`
- **Visual 4 (Right 50%):** Bar Chart
  - **Category:** `fact_support_tickets[category]`
  - **Values:** `[Avg Support Resolution Time (Hours)]`
  - **Color Saturation:** `[Tier 2 Escalation Rate %]`
