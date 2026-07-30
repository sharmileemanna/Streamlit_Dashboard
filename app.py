import streamlit as st

import pandas as pd

import plotly.express as px 

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Healthcare System Capacity Dashboard",
    page_icon="🏥",
    layout="wide"
)

# ============================
# Load Dataset
# ============================
df = pd.read_excel("data/HHS_Unaccompanied_Alien_Children_Program.csv.xlsx")

# Convert Date column to datetime
df["Date"] = pd.to_datetime(df["Date"])

# Create Year and Month columns
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.strftime("%B")



# ============================
# KPI Calculations
# ============================

total_children_under_care = df["Children in HHS Care"].sum()

# -----------------------------
# Dashboard Header
# -----------------------------
st.title("🏥 Healthcare System Capacity & Care Load Dashboard")

st.markdown(
    """
    ### Healthcare Data Analysis (2023–2025)

    This dashboard provides an overview of healthcare system capacity,
    care load trends, KPI performance, and operational insights.
    """
)

st.divider()
# ============================
# KPI Cards Layout
# ============================

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

# ============================
# KPI Card 1
# ============================

with kpi1:
    st.metric(
        label="Total Children Under Care",
        value=f"{total_children_under_care:,.0f}"
    )

# ============================
# KPI Calculations
# ============================

total_children_under_care = df["Children in HHS Care"].sum()

net_intake_pressure = (
    df["Children apprehended and placed in CBP custody*"].sum()
    - df["Children discharged from HHS Care"].sum()
)

with kpi2:
    st.metric(
        label="Net Intake Pressure",
        value=f"{net_intake_pressure:,.0f}"
    )

 # ============================
# KPI Card 3
# ============================

care_load_volatility = round(df["Children in HHS Care"].std(), 2)

with kpi3:
    st.metric(
        label="Care Load Volatility Index",
        value=f"{care_load_volatility:,.2f}"
    )   

    # ============================
# KPI Card 4
# ============================

backlog_accumulation_rate = (
    df["Children apprehended and placed in CBP custody*"].sum()
    - df["Children transferred out of CBP custody"].sum()
)

with kpi4:
    st.metric(
        label="Backlog Accumulation Rate",
        value=f"{backlog_accumulation_rate:,.0f}"
    )

    # ============================
# KPI Card 5
# ============================

discharge_offset_ratio = (
    df["Children discharged from HHS Care"].sum()
    / df["Children apprehended and placed in CBP custody*"].sum()
)

with kpi5:
    st.metric(
        label="Discharge Offset Ratio",
        value=f"{discharge_offset_ratio:.2f}"
    )

# ============================
# Sidebar Filters
# ============================

st.sidebar.header("Dashboard Filters")

selected_year = st.sidebar.multiselect(
    "Select Year",
    options=sorted(df["Year"].unique()),
    default=sorted(df["Year"].unique())
)

selected_month = st.sidebar.multiselect(
    "Select Month",
    options=sorted(df["Month"].unique()),
    default=sorted(df["Month"].unique())
)    

# Apply Filters
filtered_df = df[
    (df["Year"].isin(selected_year)) &
    (df["Month"].isin(selected_month))
]
# ============================
# Filter Summary
# ============================

st.success(f"📊 Showing {len(filtered_df)} records based on the selected filters.")


# ============================
# Business Insights
# ============================

st.subheader("📊 Business Insights")

if filtered_df["Children in HHS Care"].mean() > 12000:
    st.success("✔ Average HHS care load is high. Additional healthcare resources may be required.")

if filtered_df["Children in CBP custody"].mean() > 3000:
    st.warning("⚠ CBP custody remains under significant operational pressure.")

if filtered_df["Children discharged from HHS Care"].sum() > filtered_df["Children transferred out of CBP custody"].sum():
    st.info("ℹ HHS discharge performance is keeping pace with incoming transfers.")

# ============================
# Healthcare Trends Analysis
# ============================

st.subheader("📈 Healthcare Trends Analysis")
chart_option = st.radio(
    "Select a Chart",
    [
        "Monthly HHS Care Trend",
        "CBP vs HHS Comparison"
    ],
    horizontal=True
)

col1, col2 = st.columns(2)

with col1:
    monthly_data = (
        filtered_df.groupby("Date")["Children in HHS Care"]
        .sum()
        .reset_index()
    )
if chart_option == "Monthly HHS Care Trend":
    fig = px.line(
        monthly_data,
        x="Date",
        y="Children in HHS Care",
        title="Monthly Children in HHS Care Trend",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)
with col2:
    comparison_data = filtered_df[[
        "Date",
        "Children in CBP custody",
        "Children in HHS Care"
    ]]

    comparison_data = comparison_data.groupby("Date").sum().reset_index()
if chart_option == "CBP vs HHS Comparison":
    fig = px.bar(
        comparison_data,
        x="Date",
        y=[
            "Children in CBP custody",
            "Children in HHS Care"
        ],
        barmode="group",
        title="CBP vs HHS Load Comparison"
    )

    st.plotly_chart(fig, use_container_width=True)
# ============================
# Net Intake & Backlog Trends
# ============================

st.subheader("📈 Net Intake & Backlog Trends")

trend_data = filtered_df.copy()

trend_data["Net Intake"] = (
    trend_data["Children apprehended and placed in CBP custody*"]
    - trend_data["Children transferred out of CBP custody"]
)

trend_data["Backlog"] = (
    trend_data["Children in CBP custody"]
    + trend_data["Children in HHS Care"]
)

trend_data = trend_data.groupby("Date")[["Net Intake", "Backlog"]].sum().reset_index()

fig = px.line(
    trend_data,
    x="Date",
    y=["Net Intake", "Backlog"],
    markers=True,
    title="Net Intake vs Backlog Over Time"
)

st.plotly_chart(fig, use_container_width=True)

# ============================
# Derived Healthcare Capacity Metrics
# ============================

st.subheader("📊 Derived Healthcare Capacity Metrics")

metric1, metric2, metric3 = st.columns(3)

average_hhs = filtered_df["Children in HHS Care"].mean()
average_cbp = filtered_df["Children in CBP custody"].mean()
care_ratio = average_hhs / average_cbp if average_cbp != 0 else 0

with metric1:
    st.metric(
        "Average HHS Care Load",
        f"{average_hhs:,.0f}"
    )

with metric2:
    st.metric(
        "Average CBP Custody",
        f"{average_cbp:,.0f}"
    )

with metric3:
    st.metric(
        "HHS / CBP Ratio",
        f"{care_ratio:.2f}"
    )

# ============================
# Download Filtered Data
# ============================

st.subheader("⬇ Download Filtered Dataset")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Data (CSV)",
    data=csv,
    file_name="Healthcare_Filtered_Data.csv",
    mime="text/csv"
)
# ============================
# Dashboard Summary
# ============================

st.subheader("📝 Dashboard Summary")

st.markdown(f"""
This dashboard analyzes healthcare system capacity using filtered data.

**Current Selection**
- **Years:** {', '.join(map(str, selected_year))}
- **Months Selected:** {len(selected_month)}

### Key Highlights
- Total Children Under Care: **{filtered_df['Children in HHS Care'].sum():,.0f}**
- Average Children in HHS Care: **{filtered_df['Children in HHS Care'].mean():,.0f}**
- Average Children in CBP Custody: **{filtered_df['Children in CBP custody'].mean():,.0f}**
- Total Discharged from HHS Care: **{filtered_df['Children discharged from HHS Care'].sum():,.0f}**
""")
# ============================
# Data Preview
# ============================

with st.expander("🔍 View Filtered Dataset"):
    st.dataframe(filtered_df, use_container_width=True)

# ============================
# Project Information
# ============================

st.subheader("📌 Project Information")

st.info("""
**Project:** Healthcare System Capacity Dashboard

**Tools Used:**
- Python
- Streamlit
- Pandas
- Plotly Express

**Key Features:**
✔ KPI Cards
✔ Interactive Filters
✔ Trend Analysis
✔ Business Insights
✔ Capacity Metrics
✔ Download Filtered Dataset
✔ Data Preview
""")
# ============================
# Last Updated
# ============================

from datetime import datetime

st.caption(
    f"🕒 Dashboard Last Updated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}"
)
st.divider()

st.caption(
    "Healthcare System Capacity Dashboard | Built with Streamlit, Pandas & Plotly | Created by Sharmilee Manna"
)
