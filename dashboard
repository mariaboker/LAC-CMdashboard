
import streamlit as st
import pandas as pd
import altair as alt

# Load updated dataset
df = pd.read_csv("disease_case_dashboard_data_updated.csv", parse_dates=["Date Opened"])

# Set page configuration
st.set_page_config(layout="wide", page_title="Disease Case Dashboard")

# White background and padding fix
st.markdown("""
    <style>
        body {
            background-color: white !important;
            color: black !important;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .stMetric {
            font-size: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Top filters using columns
st.title("Disease Case Management Dashboard")
fcol1, fcol2, fcol3 = st.columns([1, 1, 1])
with fcol1:
    selected_spas = st.multiselect("Select SPA(s)", sorted(df["SPA"].unique()), default=sorted(df["SPA"].unique()))
with fcol2:
    selected_supervisor = st.selectbox("Select Supervisor", ["All"] + sorted(df["Supervisor Name"].dropna().unique()))
with fcol3:
    selected_investigator = st.selectbox("Select Investigator", ["All"] + sorted(df["Investigator Name"].dropna().unique()))

# Apply filters
filtered_df = df[df["SPA"].isin(selected_spas)]
if selected_supervisor != "All":
    filtered_df = filtered_df[filtered_df["Supervisor Name"] == selected_supervisor]
if selected_investigator != "All":
    filtered_df = filtered_df[filtered_df["Investigator Name"] == selected_investigator]

# Active/Closed logic
active_statuses = [
    "Open", "New Supervisor (assigned)", "New PHN (assigned)", "Returned (to Program)",
    "Returned (by Supervisor)", "Returned (by Investigator)", "To Supervisor (under review)",
    "PHI Support Requested", "Reassign"
]
closed_status = "Closed"

# Summary metrics
st.markdown("---")
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
with metric_col1:
    st.metric("Total Active Cases", len(filtered_df[filtered_df["Status"].isin(active_statuses)]))
with metric_col2:
    supervisor_action_statuses = [
        "New Supervisor (assigned)", "Reassign", "Returned (by Investigator)",
        "To Supervisor (under review)", "Returned (by AMD)", "Approved (by AMD)"
    ]
    st.metric("Cases Needing Supervisor Action", len(filtered_df[filtered_df["Status"].isin(supervisor_action_statuses)]))
with metric_col3:
    st.metric("Currently with PHI", len(filtered_df[filtered_df["Status"] == "PHI Support Requested"]))
with metric_col4:
    st.metric("Closed Cases", len(filtered_df[filtered_df["Status"] == closed_status]))

# Status order and filtered chart
status_order = [
    "New Supervisor (assigned)", "New PHN (assigned)", "Open", "Reassign",
    "Returned (by Investigator)", "Returned (by Supervisor)",
    "To Supervisor (under review)", "Returned (to Program)",
    "PHI Support Requested", "Closed"
]
filtered_df["Status"] = pd.Categorical(filtered_df["Status"], categories=status_order, ordered=True)
visible_status_df = filtered_df[filtered_df["Status"].notna()]

st.subheader("Case Status Distribution")
status_chart = alt.Chart(visible_status_df).mark_bar(size=20).encode(
    x=alt.X("count():Q", title="Cases"),
    y=alt.Y("Status:N", sort=status_order, axis=alt.Axis(labelLimit=400)),
    color="Status:N",
    tooltip=["Status", "count()"]
).properties(height=600, width=1000)
st.altair_chart(status_chart, use_container_width=True)

# Add table filter
st.markdown("### Filtered Case Table")
case_table_filter = st.radio("Show:", ["All", "Active Cases", "Closed Cases"])

if case_table_filter == "Active Cases":
    table_df = filtered_df[filtered_df["Status"].isin(active_statuses)]
elif case_table_filter == "Closed Cases":
    table_df = filtered_df[filtered_df["Status"] == closed_status]
else:
    table_df = filtered_df

# Move Status after Case ID
cols = table_df.columns.tolist()
if "Case ID" in cols and "Status" in cols:
    cols.insert(1, cols.pop(cols.index("Status")))
    table_df = table_df[cols]

st.dataframe(table_df.sort_values("Date Opened", ascending=False), use_container_width=True)

# Separator line
st.markdown("---")

# Program and SPA charts
col4, col5 = st.columns(2)
with col4:
    st.subheader("Active Cases per Program")
    active_cases = filtered_df[filtered_df["Status"].isin(active_statuses)]
    program_chart = alt.Chart(active_cases).mark_bar().encode(
        x=alt.X("count():Q", title="Cases"),
        y=alt.Y("Program:N", sort='-x'),
        color="Program:N"
    ).properties(height=300)
    st.altair_chart(program_chart, use_container_width=True)

with col5:
    st.subheader("Active Cases per SPA")
    spa_chart = alt.Chart(active_cases).mark_bar().encode(
        x=alt.X("SPA:N"),
        y=alt.Y("count():Q", title="Cases"),
        color="SPA:N"
    ).properties(height=300)
    st.altair_chart(spa_chart, use_container_width=True)

# Type and Priority charts
col6, col7 = st.columns(2)
with col6:
    st.subheader("Active Case Types")
    type_data = active_cases["Type"].value_counts().reset_index()
    type_data.columns = ["Type", "Count"]
    type_chart = alt.Chart(type_data).mark_arc().encode(
        theta="Count:Q",
        color="Type:N"
    )
    st.altair_chart(type_chart, use_container_width=True)

with col7:
    st.subheader("Active Cases by Priority")
    priority_data = active_cases["Priority"].value_counts().reset_index()
    priority_data.columns = ["Priority", "Count"]
    priority_data = priority_data.sort_values("Priority")
    priority_chart = alt.Chart(priority_data).mark_bar().encode(
        x=alt.X("Priority:O", sort=["1", "2", "3", "4", "5"]),
        y=alt.Y("Count:Q", title="Cases"),
        color="Priority:O"
    ).properties(height=300)
    st.altair_chart(priority_chart, use_container_width=True)
