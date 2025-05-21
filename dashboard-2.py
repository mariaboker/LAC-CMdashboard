
import streamlit as st
import pandas as pd
import altair as alt

# Load dataset
df = pd.read_csv("disease_case_dashboard_final.csv", parse_dates=["Date Opened", "Initial Contact Date"])

# Set Streamlit config
st.set_page_config(layout="wide", page_title="Disease Case Dashboard")

# Set styling
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

# Top filters
st.title("Disease Case Management Dashboard")
fcol1, fcol2, fcol3 = st.columns([1, 1, 1])
with fcol1:
    selected_spas = st.multiselect("Select SPA(s)", sorted(df["SPA"].unique()), default=sorted(df["SPA"].unique()))
with fcol2:
    selected_supervisor = st.selectbox("Select Supervisor", ["All"] + sorted(df["Supervisor Name"].dropna().unique()))
with fcol3:
    selected_investigator = st.selectbox("Select Investigator", ["All"] + sorted(df["Investigator Name"].dropna().unique()))

# Filter dataframe
filtered_df = df[df["SPA"].isin(selected_spas)]
if selected_supervisor != "All":
    filtered_df = filtered_df[filtered_df["Supervisor Name"] == selected_supervisor]
if selected_investigator != "All":
    filtered_df = filtered_df[filtered_df["Investigator Name"] == selected_investigator]

# Status categories
active_statuses = [
    "Open", "New Supervisor (assigned)", "New PHN (assigned)", "Returned (to Program)",
    "Returned (by Supervisor)", "Returned (by Investigator)", "To Supervisor (under review)",
    "PHI Support Requested", "Reassign"
]
closed_status = "Closed"
supervisor_action_statuses = [
    "New Supervisor (assigned)", "Reassign", "Returned (by Investigator)",
    "To Supervisor (under review)", "Returned (by AMD)", "Approved (by AMD)"
]

# Metrics
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Cases", len(filtered_df[filtered_df["Status"].isin(active_statuses)]))
col2.metric("Supervisor Action Needed", len(filtered_df[filtered_df["Status"].isin(supervisor_action_statuses)]))
col3.metric("Currently with PHI", len(filtered_df[filtered_df["Status"] == "PHI Support Requested"]))
col4.metric("Closed Cases", len(filtered_df[filtered_df["Status"] == closed_status]))

# Case Status Chart
st.subheader("Case Status Distribution")
status_order = [
    "New Supervisor (assigned)", "New PHN (assigned)", "Open", "Reassign",
    "Returned (by Investigator)", "Returned (by Supervisor)",
    "To Supervisor (under review)", "Returned (to Program)",
    "PHI Support Requested", "Closed"
]
filtered_df["Status"] = pd.Categorical(filtered_df["Status"], categories=status_order, ordered=True)
visible_status_df = filtered_df[filtered_df["Status"].notna()]
status_chart = alt.Chart(visible_status_df).mark_bar(size=20).encode(
    x=alt.X("count():Q", title="Cases", scale=alt.Scale(nice=False), axis=alt.Axis(tickMinStep=1)),
    y=alt.Y("Status:N", sort=status_order, axis=alt.Axis(labelLimit=400)),
    color="Status:N",
    tooltip=["Status", "count()"]
).properties(height=600, width=1000)
st.altair_chart(status_chart, use_container_width=True)

# Table filter
st.markdown("### Filtered Case Table")
case_table_filter = st.radio("Show:", ["All", "Active Cases", "Closed Cases", "Cases Needing Supervisor Action"])
if case_table_filter == "Active Cases":
    table_df = filtered_df[filtered_df["Status"].isin(active_statuses)]
elif case_table_filter == "Closed Cases":
    table_df = filtered_df[filtered_df["Status"] == closed_status]
elif case_table_filter == "Cases Needing Supervisor Action":
    table_df = filtered_df[filtered_df["Status"].isin(supervisor_action_statuses)]
else:
    table_df = filtered_df

# Rename and reorder columns
table_df = table_df.rename(columns={"Date Opened": "Date of Onset"})
column_order = [
    "Case ID", "Type", "Patient Name", "Disease", "Status", "Priority", "Date of Onset",
    "Initial Contact Date", "Contact Made", "SPA", "Supervisor Name", "Investigator Name"
]
table_df = table_df[[col for col in column_order if col in table_df.columns]]

# Display table

# Display styled table
def style_contact(val):
    if val == "on track":
        return '<span style="color: white; background-color: green; padding: 4px 8px; border-radius: 8px;">on track</span>'
    elif val == "past due":
        return '<span style="color: white; background-color: red; padding: 4px 8px; border-radius: 8px;">past due</span>'
    return val

# Format and render table with styled "Contact Made"
styled_table = table_df.copy()
if "Contact Made" in styled_table.columns:
    styled_table["Contact Made"] = styled_table["Contact Made"].apply(style_contact)

# Convert DataFrame to HTML
st.markdown(styled_table.to_html(escape=False, index=False), unsafe_allow_html=True)


# Divider
st.markdown("---")

# Charts: Program and SPA
col4, col5 = st.columns(2)
with col4:
    st.subheader("Active Cases per Program")
    active_cases = filtered_df[filtered_df["Status"].isin(active_statuses)]
    program_chart = alt.Chart(active_cases).mark_bar().encode(
        x=alt.X("count():Q", title="Cases", scale=alt.Scale(nice=False), axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("Program:N", sort='-x'),
        color="Program:N"
    ).properties(height=300)
    st.altair_chart(program_chart, use_container_width=True)

with col5:
    st.subheader("Active Cases per SPA")
    spa_chart = alt.Chart(active_cases).mark_bar().encode(
        x=alt.X("SPA:N"),
        y=alt.Y("count():Q", title="Cases", scale=alt.Scale(nice=False), axis=alt.Axis(tickMinStep=1)),
        color="SPA:N"
    ).properties(height=300)
    st.altair_chart(spa_chart, use_container_width=True)

# Charts: Type and Priority
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
        y=alt.Y("Count:Q", title="Cases", scale=alt.Scale(nice=False), axis=alt.Axis(tickMinStep=1)),
        color="Priority:O"
    ).properties(height=300)
    st.altair_chart(priority_chart, use_container_width=True)
