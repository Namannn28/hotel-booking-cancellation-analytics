# PulseMetrics-AI: Technical & Behavioral Interview Master Guide

This guide equips you to answer technical questions and behavioral interview scenarios using the **STAR Method** (Situation, Task, Action, Result).

---

## 1. Project Elevator Pitch (30-Second Version)
> *"I designed **PulseMetrics-AI**, an end-to-end Enterprise SaaS Customer 360 and Revenue Intelligence Platform. Many companies struggle because their quantitative telemetry lives in a database, while the qualitative 'reasons why' customers churn are locked in support tickets and sales notes.
> 
> I built a production dimensional star schema in SQL to calculate ARR waterfalls and cohort retention, trained a predictive churn model with 0.99 ROC-AUC, created an executive Power BI & Excel financial suite, and developed an autonomous GenAI Copilot combining Text-to-SQL with RAG vector search to deliver synthesized executive decision briefs."*

---

## 2. Technical Deep-Dive Interview Questions & Answers

### Q1: Why did you model the data in a Dimensional Star Schema instead of querying one wide table?
**Answer:**
- **Performance & Scalability:** Storing repeating customer attributes (like industry, region, size) across millions of event logs leads to severe storage bloat and slow aggregation times.
- **Single Source of Truth:** A normalized dimension (`dim_customers`) prevents update anomalies if a company rebrands or upgrades tiers.
- **BI BI-Directional Ambiguity:** In Power BI, star schemas allow single-direction 1-to-many filtering, avoiding circular dependency errors and expensive DAX memory overhead.

---

### Q2: Walk me through the SQL logic for the Monthly ARR Waterfall (`01_kpi_arr_waterfall.sql`).
**Answer:**
> *"The challenge with an ARR waterfall is tracking continuous state changes over discrete calendar months. 
> 
> 1. I created CTEs using date truncation (`STRFTIME('%Y-%m')`) to aggregate newly acquired subscription ARR and lost churned ARR per calendar month.
> 2. I used a master timeline union to align all months without gaps.
> 3. To compute cumulative active ARR, I used a window function: `SUM(net_new_arr) OVER (ORDER BY report_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`.
> 4. To calculate Month-over-Month (MoM) growth %, I wrapped the running total in a CTE and used `LAG(ending_arr, 1) OVER (ORDER BY report_month)` to ensure zero division errors via `NULLIF()`."*

---

### Q3: Why is Cohort Retention more insightful than a blended Churn Rate?
**Answer:**
> *"A blended churn rate (e.g., '16% annual churn') is a lagging metric that obscures whether attrition is coming from newly acquired customers during onboarding or legacy accounts experiencing product fatigue. 
> 
> Cohort analysis indexes accounts by their signup month and tracks their survival curves at Month 1, 3, 6, 9, and 12. If recent cohorts drop sharply at Month 1, it diagnoses an onboarding or time-to-value failure. If they drop at Month 12, it indicates contract renewal sticker shock or lack of executive buy-in."*

---

### Q4: In your Churn Model, why did you evaluate Recall and PR-AUC instead of just Accuracy?
**Answer:**
> *"In SaaS churn, datasets are heavily imbalanced (e.g., ~15-20% churners vs. 80-85% retained). A naive model that always predicts 'Active' would be 85% accurate, yet completely useless.
> 
> For our business problem, a **False Negative** (failing to detect an enterprise account that is about to cancel) costs $30,000+ in lost ARR. A **False Positive** only costs the Customer Success team a 15-minute check-in call. Therefore, I optimized for **Recall** (achieving 92.1%) and PR-AUC, ensuring we capture the vast majority of at-risk accounts."*

---

### Q5: How does your GenAI Copilot prevent LLM hallucinations?
**Answer:**
> *"The Copilot uses a deterministic **Dual-Retrieval Pipeline**:
> 1. **Structured Quant Facts:** Natural language questions are converted into validated SQL queries executed live against DuckDB. The LLM never invents numbers; it reports live database counts and sums.
> 2. **Qualitative RAG Grounding:** To explain the numbers, the Copilot searches vectorized customer QBRs and exit interviews via TF-IDF cosine similarity and requires direct citations (e.g., Document ID, Account ID, and Author).
> 3. If no relevant evidence exists in the vector store, the system falls back gracefully rather than hallucinating reasons."*

---

## 3. Behavioral STAR Story: Business Impact & Executive Communication

**Situation:**
Enterprise leadership noticed that churn in the Mid-Market Growth tier was rising, but traditional BI dashboards only showed the aggregate revenue loss without explaining the root cause.

**Task:**
My goal was to diagnose the primary drivers of churn and deliver an actionable intervention plan for executive leadership.

**Action:**
1. Ran correlation queries across support tickets and usage logs: discovered that accounts experiencing Tier-2 support escalations and resolution delays >48 hours were 3.8x more likely to churn.
2. Filtered RAG customer exit interview notes: confirmed that multiple mid-market customers specifically mentioned competitor pricing (Datadog) combined with webhook latency.
3. Built an automated High-Risk Customer Alert Feed in the dashboard that flags active accounts whenever their seat utilization dips below 45% or support SLA exceeds 36 hours.

**Result:**
Presented an executive brief with targeted recommendations: implementing a priority SLA queue for high-ARR accounts and introducing annual commitment discounts. This early-warning system provides Customer Success with a 60-day window to intervene, protecting up to \$1.8M in annual recurring revenue.
