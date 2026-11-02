# Technical & Behavioral Interview Master Guide (Fresher Edition)

This guide provides word-for-word explanations and answers following the **STAR Method** (Situation, Task, Action, Result) so you can explain this project with 100% confidence.

---

## 1. The 30-Second Elevator Pitch
> *"For my portfolio project, I analyzed a real-world dataset of **119,000+ hotel booking transactions** from two Portuguese hotels (a City Hotel and a Resort Hotel). 
> 
> The core business problem was that **37% of reservations were being canceled**, resulting in over **\$11.2M in lost room revenue** and operational chaos for hotel housekeeping and staffing.
> 
> I used **SQL** to uncover the primary churn drivers—like lead times over 90 days and zero-deposit OTA bookings. I built an executive **Excel financial model** with dynamic formulas, a **Power BI dashboard** with custom DAX measures, and an explainable **Random Forest model (82% accuracy, 0.89 ROC-AUC)**. Based on the data, I proposed a dynamic deposit policy and a monthly overbooking strategy estimated to recover **\$1.4M annually**."*

---

## 2. Common Interview Questions & Answers

### Q1: Is this data real, and where did you source it?
**Answer:**
> *"Yes, it is 100% real-world operational data. It was collected from two real hotel properties (H1 Resort Hotel in Algarve and H2 City Hotel in Lisbon) and published in the peer-reviewed journal *Data in Brief* (2019) by researchers Nuno Antonio, Ana de Almeida, and Luis Nunes. It contains 119,390 actual booking records from July 2015 to August 2017."*

---

### Q2: What were the most surprising findings from your SQL analysis?
**Answer:**
> *"Three key insights stood out:
> 1. **The Lead Time Hazard Curve:** Bookings made within 7 days of arrival had only a **14% cancellation rate**. But for bookings made >180 days in advance, cancellations surged to **55%**. Guests treat advance bookings as risk-free reservations.
> 2. **Online Travel Agencies (OTAs):** Over 73% of all cancellations originated from Online TAs (like Booking.com/Expedia) because 85%+ of them had 'No Deposit' policies.
> 3. **The Special Requests Loyalty Signal:** Guests who made 2 or more special requests (e.g., quiet room, high floor) had an **82% show-up rate**. Even a small active engagement with the booking drastically reduced cancellation risk."*

---

### Q3: How did you use SQL window functions in this project?
**Answer:**
> *"I used window functions in two key areas:
> 1. In `01_monthly_cancellation_trends.sql`, I used `LAG(realized_revenue, 1) OVER (PARTITION BY hotel ORDER BY arrival_date_year, month_num)` to compute Month-over-Month (MoM) revenue growth % and compare seasonal performance.
> 2. In `04_country_cancellation_ranking.sql`, I used `DENSE_RANK() OVER (ORDER BY cancellation_rate_pct DESC)` across statistically significant origin countries (500+ bookings) to prioritize which international markets needed stricter booking policies."*

---

### Q4: Walk me through your Excel Financial Model (`Hotel_Revenue_Analysis_Executive_Model.xlsx`).
**Answer:**
> *"I built a multi-tab executive model designed for hotel general managers:
> - **Executive Dashboard:** Features KPI summary cards (Total Bookings, Cancellation Rate, Realized vs. Lost Revenue, ADR) and property comparison tables using `SUMIFS`, `COUNTIFS`, and `AVERAGEIFS`.
> - **Lead Time Sensitivity Tab:** Categorizes reservations into 5 lead-time windows and applies conditional formatting alerts where cancellation rates exceed 40%.
> - **Overbooking Schedule:** Calculates monthly empirical cancellation rates and maps them to a recommended 10–16% overbooking buffer."*

---

### Q5: Why did you choose Random Forest for Machine Learning, and how did you evaluate it?
**Answer:**
> *"I chose Random Forest because hotel booking data contains a mix of numeric metrics (lead time, ADR, nights) and categorical variables (hotel type, deposit type, market segment). Random Forest handles non-linear relationships without requiring complex scaling, and it gives clean **Feature Importance** that non-technical managers can understand.
> 
> I evaluated the model on a held-out test set (20% split) using:
> - **Accuracy:** 82.1%
> - **ROC-AUC:** 0.8944
> - **Precision (Cancellations):** 86.6%
> 
> In hospitality, **Precision** is vital: if we falsely flag a customer as going to cancel when they actually intend to show up, and we give away their room, we face angry guests and walk-away compensation fees. Our 86.6% precision ensures low false alarm risk."*

---

### Q6: What is your final business recommendation to hotel leadership?
**Answer:**
> *"I delivered three concrete recommendations:
> 1. **Dynamic Deposit Requirement:** For any booking with a lead time greater than 60 days made via Online Travel Agencies, require a 20% non-refundable deposit or a 48-hour card pre-authorization.
> 2. **Controlled Overbooking Strategy:** In high-cancellation peak months (April–August, where cancellations hit 40-44%), hotel revenue managers can safely overbook by 12–15% without risking customer walk-aways.
> 3. **Estimated ROI:** This strategy protects occupancy and is projected to recover approximately **\$1.4M annually in lost room revenue**."*
