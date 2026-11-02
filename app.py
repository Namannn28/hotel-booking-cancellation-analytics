"""
Hotel Revenue & Cancellation Analytics Dashboard
Author: Naman Gupta

Interactive dashboard built with Streamlit for exploring hotel booking trends,
cancellation drivers, running SQL models, and testing live reservation cancellation risk.
"""

import os
import streamlit as st
import pandas as pd
import altair as alt
import joblib
import duckdb

# Streamlit Page Setup
st.set_page_config(
    page_title="Hotel Revenue & Cancellation Analytics",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "data", "raw", "hotel_bookings.csv")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")


@st.cache_data
def load_booking_data():
    """Loads and caches the 119,390 hotel booking dataset."""
    df = pd.read_csv(DATA_FILE)
    df["children"] = df["children"].fillna(0).astype(int)
    df["country"] = df["country"].fillna("Unknown")
    df["adr"] = df["adr"].clip(lower=0, upper=1000)
    df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
    df["booking_revenue"] = df["total_nights"] * df["adr"]
    return df


@st.cache_resource
def load_cancellation_model():
    """Loads the trained model or retrains if running in a new cloud environment."""
    model_file_path = os.path.join(MODELS_DIR, "hotel_cancellation_rf.joblib")
    features_file_path = os.path.join(MODELS_DIR, "feature_columns.joblib")
    try:
        model = joblib.load(model_file_path)
        features = joblib.load(features_file_path)
        return model, features
    except Exception:
        from ml.train_cancellation_model import load_and_preprocess_data, train_cancellation_model
        _, feature_matrix, target_series = load_and_preprocess_data()
        model, _ = train_cancellation_model(feature_matrix, target_series)
        return model, feature_matrix.columns.tolist()


df_bookings = load_booking_data()

# Sidebar Navigation and Filters
st.sidebar.title("🏨 Hotel Analytics")
st.sidebar.caption("119,390 Real Reservation Records")

selected_page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Dashboard",
        "Lead Time & Root Causes",
        "Cancellation Risk Calculator",
        "SQL Query Explorer"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Filter Bookings")

selected_hotels = st.sidebar.multiselect(
    "Property Type",
    options=["City Hotel", "Resort Hotel"],
    default=["City Hotel", "Resort Hotel"]
)

available_segments = sorted(df_bookings["market_segment"].dropna().unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Market Segment",
    options=available_segments,
    default=["Online TA", "Offline TA/TO", "Direct", "Corporate"]
)

# Apply global filters
filtered_df = df_bookings[
    (df_bookings["hotel"].isin(selected_hotels)) &
    (df_bookings["market_segment"].isin(selected_segments))
]

# -----------------------------------------------------------------------------
# 1. Executive Dashboard Page
# -----------------------------------------------------------------------------
if selected_page == "Executive Dashboard":
    st.title("Hotel Revenue & Cancellation Executive Dashboard")
    st.markdown("Portfolio-level revenue realization, cancellations, and daily rate analysis.")

    total_bookings = len(filtered_df)
    total_cancellations = int((filtered_df["is_canceled"] == 1).sum())
    cancellation_percentage = (total_cancellations / max(total_bookings, 1)) * 100.0
    realized_revenue = filtered_df[filtered_df["is_canceled"] == 0]["booking_revenue"].sum()
    lost_revenue = filtered_df[filtered_df["is_canceled"] == 1]["booking_revenue"].sum()
    average_daily_rate = filtered_df["adr"].mean()

    # Executive Metric Ribbon
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Bookings", f"{total_bookings:,}")
    col2.metric("Cancellation Rate", f"{cancellation_percentage:.1f}%")
    col3.metric("Realized Revenue", f"${realized_revenue:,.0f}")
    col4.metric("Lost Revenue", f"${lost_revenue:,.0f}")
    col5.metric("Average Daily Rate (ADR)", f"${average_daily_rate:.2f}")

    st.markdown("---")

    chart_col_left, chart_col_right = st.columns(2)

    with chart_col_left:
        st.subheader("Monthly Realized Revenue vs. Cancellation Loss")
        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        monthly_summary = filtered_df.groupby("arrival_date_month").agg(
            realized_amount=("booking_revenue", lambda revs: filtered_df.loc[revs.index][filtered_df.loc[revs.index, "is_canceled"] == 0]["booking_revenue"].sum()),
            lost_amount=("booking_revenue", lambda revs: filtered_df.loc[revs.index][filtered_df.loc[revs.index, "is_canceled"] == 1]["booking_revenue"].sum())
        ).reindex(month_order).reset_index()

        monthly_melted = monthly_summary.melt(
            id_vars="arrival_date_month",
            value_vars=["realized_amount", "lost_amount"],
            var_name="Category",
            value_name="Revenue"
        )
        monthly_melted["Category"] = monthly_melted["Category"].map({
            "realized_amount": "Realized Revenue",
            "lost_amount": "Lost to Cancellations"
        })

        revenue_bar_chart = alt.Chart(monthly_melted).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("arrival_date_month:N", sort=month_order, title="Month of Arrival"),
            y=alt.Y("Revenue:Q", title="Revenue ($)"),
            color=alt.Color("Category:N", scale=alt.Scale(range=["#1B365D", "#C00000"])),
            tooltip=["arrival_date_month", "Category", alt.Tooltip("Revenue:Q", format="$,.0f")]
        ).properties(height=340)

        st.altair_chart(revenue_bar_chart, use_container_width=True)

    with chart_col_right:
        st.subheader("Cancellation Rate by Distribution Channel")
        channel_summary = filtered_df.groupby("market_segment").agg(
            total=("is_canceled", "count"),
            canceled=("is_canceled", "sum")
        ).reset_index()
        channel_summary["cancellation_rate"] = (channel_summary["canceled"] / channel_summary["total"]) * 100.0

        channel_bar_chart = alt.Chart(channel_summary).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color="#008080").encode(
            x=alt.X("market_segment:N", title="Distribution Channel", sort="-y"),
            y=alt.Y("cancellation_rate:Q", title="Cancellation Rate (%)"),
            tooltip=["market_segment", alt.Tooltip("cancellation_rate:Q", format=".1f")]
        ).properties(height=340)

        st.altair_chart(channel_bar_chart, use_container_width=True)


# -----------------------------------------------------------------------------
# 2. Lead Time & Root Cause Analysis Page
# -----------------------------------------------------------------------------
elif selected_page == "Lead Time & Root Causes":
    st.title("Lead Time & Root Cause Diagnostics")
    st.markdown("Investigating booking advance windows, deposit policies, and customer intent signals.")

    filtered_df["lead_time_group"] = pd.cut(
        filtered_df["lead_time"],
        bins=[-1, 7, 30, 90, 180, 1000],
        labels=["0-7 Days", "8-30 Days", "31-90 Days", "91-180 Days", ">180 Days"]
    )

    lead_time_stats = filtered_df.groupby("lead_time_group", observed=False).agg(
        total_reservations=("is_canceled", "count"),
        total_cancellations=("is_canceled", "sum")
    ).reset_index()
    lead_time_stats["cancellation_rate_pct"] = (
        lead_time_stats["total_cancellations"] / lead_time_stats["total_reservations"]
    ) * 100.0

    col_chart, col_insights = st.columns([1, 1])

    with col_chart:
        st.subheader("Cancellation Rate Escalation by Advance Booking Window")
        lead_chart = alt.Chart(lead_time_stats).mark_bar(color="#C00000").encode(
            x=alt.X("lead_time_group:N", title="Advance Booking Window"),
            y=alt.Y("cancellation_rate_pct:Q", title="Cancellation Rate (%)"),
            tooltip=["lead_time_group", alt.Tooltip("cancellation_rate_pct:Q", format=".1f"), alt.Tooltip("total_reservations:Q", format=",")]
        ).properties(height=340)
        st.altair_chart(lead_chart, use_container_width=True)

    with col_insights:
        st.subheader("Key Findings")
        st.write("""
        * **The Lead Time Cliff:** Bookings made within a week of arrival have only a **14% cancellation rate**. In contrast, bookings made more than 6 months ahead cancel at **over 54%**.
        * **Zero-Deposit Vulnerability:** Over 85% of reservations have `No Deposit`. On Online Travel Agencies, guests treat reservations as options rather than commitments.
        * **Special Requests as Intent:** Guests with 2 or more special requests have an **82% show-up rate**, proving customer interaction is a strong indicator of intent.
        """)


# -----------------------------------------------------------------------------
# 3. Cancellation Risk Calculator Page
# -----------------------------------------------------------------------------
elif selected_page == "Cancellation Risk Calculator":
    st.title("Interactive Cancellation Risk Calculator")
    st.markdown("Test the Random Forest model live with custom reservation inputs.")

    trained_model, feature_column_names = load_cancellation_model()

    if trained_model is not None:
        col_input1, col_input2, col_input3 = st.columns(3)

        with col_input1:
            hotel_input = st.selectbox("Property Type", ["City Hotel", "Resort Hotel"])
            lead_time_input = st.slider("Lead Time (Days in Advance)", 0, 365, 45)
            adr_input = st.number_input("Average Daily Rate ($)", min_value=10.0, max_value=800.0, value=120.0)

        with col_input2:
            market_input = st.selectbox("Market Segment", ["Online TA", "Offline TA/TO", "Direct", "Corporate"])
            deposit_input = st.selectbox("Deposit Type", ["No Deposit", "Non Refund", "Refundable"])
            customer_type_input = st.selectbox("Customer Type", ["Transient", "Contract", "Transient-Party", "Group"])

        with col_input3:
            special_requests_input = st.slider("Total Special Requests", 0, 5, 0)
            parking_spaces_input = st.selectbox("Parking Space Required", [0, 1])
            previous_cancels_input = st.number_input("Prior Cancellations on Record", min_value=0, max_value=10, value=0)

        # Assemble input dictionary
        sample_record = {
            "lead_time": lead_time_input,
            "stays_in_weekend_nights": 1,
            "stays_in_week_nights": 2,
            "adults": 2,
            "children": 0,
            "is_repeated_guest": 0,
            "previous_cancellations": previous_cancels_input,
            "previous_bookings_not_canceled": 0,
            "booking_changes": 0,
            "days_in_waiting_list": 0,
            "adr": adr_input,
            "required_car_parking_spaces": parking_spaces_input,
            "total_of_special_requests": special_requests_input,
            f"hotel_{hotel_input}": 1,
            f"market_segment_{market_input}": 1,
            f"deposit_type_{deposit_input}": 1,
            f"customer_type_{customer_type_input}": 1
        }

        # Format dataframe to match model columns
        sample_df = pd.DataFrame([sample_record])
        for column in feature_column_names:
            if column not in sample_df.columns:
                sample_df[column] = 0
        sample_df = sample_df[feature_column_names]

        cancellation_probability = trained_model.predict_proba(sample_df)[0, 1]

        st.markdown("---")
        result_col1, result_col2 = st.columns([1, 2])

        with result_col1:
            if cancellation_probability > 0.50:
                st.error(f"### High Risk\n## {cancellation_probability * 100:.1f}% Chance of Cancellation")
            else:
                st.success(f"### Low Risk\n## {cancellation_probability * 100:.1f}% Chance of Cancellation")

        with result_col2:
            st.markdown("#### Recommended Action:")
            if cancellation_probability > 0.50:
                st.warning(
                    "**Action Required:**\n"
                    "- Require a 20% deposit or credit card pre-authorization.\n"
                    "- Include reservation in property overbooking buffer."
                )
            else:
                st.success(
                    "**Standard Booking:**\n"
                    "- Low cancellation likelihood.\n"
                    "- Confirm room assignment as requested."
                )


# -----------------------------------------------------------------------------
# 4. SQL Query Explorer Page
# -----------------------------------------------------------------------------
elif selected_page == "SQL Query Explorer":
    st.title("SQL Analytical Models (DuckDB)")
    st.markdown("Run the production SQL models directly against the 119k dataset in-memory.")

    query_catalog = {
        "1. Monthly Cancellation & Revenue Trends": "sql/01_monthly_cancellation_trends.sql",
        "2. Lead Time Buckets & Risk Escalation": "sql/02_lead_time_cancellation_risk.sql",
        "3. Channel & Market Segment Performance": "sql/03_market_segment_channel_analysis.sql",
        "4. Origin Country Rankings (DENSE_RANK)": "sql/04_country_cancellation_ranking.sql",
        "5. Deposit Policy & Repeated Guest Analysis": "sql/05_deposit_and_repeated_guest_paradox.sql"
    }

    selected_query_title = st.selectbox("Choose a query to inspect", list(query_catalog.keys()))
    sql_file_relative_path = query_catalog[selected_query_title]

    with open(os.path.join(BASE_DIR, sql_file_relative_path), "r", encoding="utf-8") as sql_file:
        query_sql_code = sql_file.read()

    st.code(query_sql_code, language="sql")

    if st.button("Run Query in DuckDB", type="primary"):
        with st.spinner("Running query..."):
            db_conn = duckdb.connect(database=":memory:")
            db_conn.execute(f"CREATE TABLE hotel_bookings AS SELECT * FROM read_csv_auto('{DATA_FILE.replace('\\', '/')}');")
            query_results = db_conn.execute(query_sql_code).df()
            st.success(f"Query returned {len(query_results)} rows.")
            st.dataframe(query_results, use_container_width=True)
