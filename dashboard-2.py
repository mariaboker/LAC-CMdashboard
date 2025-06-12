
import streamlit as st
import pandas as pd
import altair as alt

# Load dataset
df = pd.read_csv("disease_case_dashboard_final-2.csv", parse_dates=["Date Opened", "Initial Contact Date"])

# Override Patient Name (already set)
df = df

# Page config
st.set_page_config(layout="wide", page_title="Disease Case Dashboard")

# Fixed red ribbon
st.markdown(
    '<div style="background-color:#D32F2F; padding:8px; text-align:center; color:white; font-weight:bold; position:fixed; top:0; left:0; width:100%; z-index:1000;">'
    'SIMULATED DASHBOARD FOR PROTOTYPING PURPOSES | DATA IS NOT REAL'
    '</div>',
    unsafe_allow_html=True
)

# CSS to offset content for ribbon
st.markdown("""<style>
.block-container { padding-top: 50px; }
</style>""", unsafe_allow_html=True)

# Title and filters
st.title("Prototype Dashboard | Case Management")
c1, c2, c3 = st.columns([1,1,1])
with c1:
    selected_spas = st.multiselect("Select SPA(s)", sorted(df["SPA"].unique()), default=sorted(df["SPA"].unique()))
with c2:
    selected_supervisor = st.selectbox("Select Supervisor", ["All"] + sorted(df["Supervisor Name"].dropna().unique()))
with c3:
    selected_investigator = st.selectbox("Select Investigator", ["All"] + sorted(df["Investigator Name"].dropna().unique()))

# Apply filters
filtered = df[df["SPA"].isin(selected_spas)]
if selected_supervisor != "All":
    filtered = filtered[filtered["Supervisor Name"] == selected_supervisor]
if selected_investigator != "All":
    filtered = filtered[filtered["Investigator Name"] == selected_investigator]

# Status categories
active_statuses = ["Open","New Supervisor (assigned)","New PHN (assigned)",
                   "Returned (by Supervisor)","Returned (by Investigator)",
                   "To Supervisor (under review)","PHI Support Requested","Reassign"]
supervisor_actions = ["New Supervisor (assigned)","Reassign","Returned (by Investigator)",
                      "To Supervisor (under review)","Returned (by AMD)","Approved (by AMD)"]

# Metrics
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Active Cases", len(filtered[filtered["Status"].isin(active_statuses)]))
m2.metric("Supervisor Action Needed", len(filtered[filtered["Status"].isin(supervisor_actions)]))
m3.metric("Currently with PHI", len(filtered[filtered["Status"]=="PHI Support Requested"]))
m4.metric("Records Past Due", len(filtered[filtered["Contact Made"]=="past due"]))

# Status chart
st.subheader("Case Status Distribution")
status_order = ["New Supervisor (assigned)","New PHN (assigned)","Open","Reassign",
                "Returned (by Investigator)","Returned (by Supervisor)",
                "To Supervisor (under review)","PHI Support Requested"]
filtered["Status"] = pd.Categorical(filtered["Status"], categories=status_order, ordered=True)
vis = filtered.dropna(subset=["Status"])
chart = alt.Chart(vis).mark_bar(size=20).encode(
    x=alt.X("count():Q", title="Cases", scale=alt.Scale(nice=False), axis=alt.Axis(tickMinStep=1)),
    y=alt.Y("Status:N", sort=status_order),
    color="Status:N", tooltip=["Status","count()"]
).properties(height=400)
st.altair_chart(chart, use_container_width=True)

# Table filter
st.markdown("### Filtered Case Table")
choice = st.radio("Show:", ["All","Active Cases","Cases Needing Supervisor Action"])
if choice == "Active Cases":
    table = filtered[filtered["Status"].isin(active_statuses)]
elif choice == "Cases Needing Supervisor Action":
    table = filtered[filtered["Status"].isin(supervisor_actions)]
else:
    table = filtered.copy()

# Prepare table
table = table.rename(columns={"Date Opened":"Date of Onset"})
cols = ["Case ID","Type","Patient Name","Disease","Status","Priority","Date of Onset",
        "Initial Contact Date","Contact Made","SPA","Supervisor Name","Investigator Name"]
table = table[[c for c in cols if c in table.columns]]

# Link and tag styling
def make_link(v): return f'<a href="https://iris-record/{v}" target="_blank" style="color:blue;text-decoration:underline;">{v}</a>'
def style_contact(v):
    return '<span style="color:white;background-color:green;padding:4px 8px;border-radius:8px;">on track</span>' if v=="on track" else '<span style="color:white;background-color:red;padding:4px 8px;border-radius:8px;">past due</span>'

table_html = table.copy()
table_html["Case ID"] = table_html["Case ID"].apply(make_link)
table_html["Contact Made"] = table_html["Contact Made"].apply(style_contact)

st.markdown(table_html.to_html(classes="dashboard-table", escape=False, index=False), unsafe_allow_html=True)
