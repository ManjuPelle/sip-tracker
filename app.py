
import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="SIP Wealth Tracker", layout="wide")

# Initialize session state
if "sip_data" not in st.session_state:
    st.session_state.sip_data = []

if "nav_history" not in st.session_state:
    st.session_state.nav_history = []

if "rebalancing_log" not in st.session_state:
    st.session_state.rebalancing_log = []

if "tax_tracker" not in st.session_state:
    st.session_state.tax_tracker = []

st.title("📈 SIP Wealth Tracker")

# --- NAV History Section ---
st.sidebar.header("📊 NAV History")
with st.sidebar.form("nav_form"):
    nav_date = st.date_input("NAV Date", value=datetime.date(2025, 8, 1))
    nav_icici_infra = st.number_input("ICICI Infra NAV", value=191.49)
    nav_parag = st.number_input("Parag Parikh NAV", value=92.33)
    nav_liquid = st.number_input("ICICI Liquid NAV", value=400.0)
    submitted_nav = st.form_submit_button("Add NAV")
    if submitted_nav:
        st.session_state.nav_history.append({
            "Date": nav_date,
            "ICICI Infra NAV": nav_icici_infra,
            "Parag Parikh NAV": nav_parag,
            "ICICI Liquid NAV": nav_liquid
        })

# Convert NAV history to DataFrame
nav_df = pd.DataFrame(st.session_state.nav_history)

# --- SIP Entry Form ---
st.header("🧾 Add SIP Entry")
with st.form("sip_form"):
    sip_date = st.date_input("SIP Date", value=datetime.date(2025, 8, 1))
    month_number = st.number_input("Month Number", min_value=1, value=1)
    year = sip_date.year
    total_sip = 25000 if month_number <= 12 else 25000 * (1.1 ** ((month_number - 1) // 12))
    icici_infra_sip = total_sip * 0.6
    parag_sip = total_sip * 0.3
    liquid_sip = total_sip * 0.1 if month_number <= 36 else 0

    # Lookup NAVs
    nav_row = nav_df[nav_df["Date"] == sip_date]
    if not nav_row.empty:
        infra_nav = nav_row["ICICI Infra NAV"].values[0]
        parag_nav = nav_row["Parag Parikh NAV"].values[0]
        liquid_nav = nav_row["ICICI Liquid NAV"].values[0]
    else:
        infra_nav = parag_nav = liquid_nav = 1.0

    infra_units = icici_infra_sip / infra_nav
    parag_units = parag_sip / parag_nav
    liquid_units = liquid_sip / liquid_nav

    infra_value = infra_units * infra_nav
    parag_value = parag_units * parag_nav
    liquid_value = liquid_units * liquid_nav
    total_value = infra_value + parag_value + liquid_value
    goal_progress = total_value / 10000000

    step_up_check = "OK" if (month_number % 12 == 1 and total_sip == 25000 * (1.1 ** ((month_number - 1) // 12))) else ""

    submitted_sip = st.form_submit_button("Add SIP Entry")
    if submitted_sip:
        st.session_state.sip_data.append({
            "Date": sip_date,
            "Month Number": month_number,
            "Year": year,
            "Total SIP (₹)": total_sip,
            "ICICI Infra SIP (₹)": icici_infra_sip,
            "Parag Parikh SIP (₹)": parag_sip,
            "ICICI Liquid SIP (₹)": liquid_sip,
            "ICICI Infra Units": infra_units,
            "Parag Parikh Units": parag_units,
            "ICICI Liquid Units": liquid_units,
            "ICICI Infra Value (₹)": infra_value,
            "Parag Parikh Value (₹)": parag_value,
            "ICICI Liquid Value (₹)": liquid_value,
            "Total Portfolio Value (₹)": total_value,
            "Goal Progress (%)": f"{goal_progress*100:.2f}%",
            "Step-Up Check": step_up_check
        })

# --- SIP Tracker Table ---
st.subheader("📅 SIP Tracker")
sip_df = pd.DataFrame(st.session_state.sip_data)
st.dataframe(sip_df, use_container_width=True)

# --- Summary Dashboard ---
st.subheader("📊 Summary Dashboard")
if not sip_df.empty:
    total_invested = sip_df["Total SIP (₹)"].sum()
    current_value = sip_df["Total Portfolio Value (₹)"].iloc[-1]
    goal_progress = current_value / 10000000
    infra_weight = sip_df["ICICI Infra Value (₹)"].iloc[-1] / current_value if current_value else 0
    parag_weight = sip_df["Parag Parikh Value (₹)"].iloc[-1] / current_value if current_value else 0
    liquid_weight = sip_df["ICICI Liquid Value (₹)"].iloc[-1] / current_value if current_value else 0
    rebalance = "Rebalance Needed" if (
        infra_weight > 0.65 or infra_weight < 0.55 or
        parag_weight > 0.35 or parag_weight < 0.25 or
        liquid_weight > 0.15 or liquid_weight < 0.05
    ) else "No Action"

    st.metric("Total Invested", f"₹{total_invested:,.0f}")
    st.metric("Current Value", f"₹{current_value:,.0f}")
    st.metric("Goal Progress", f"{goal_progress*100:.2f}%")
    st.metric("ICICI Infra Weight", f"{infra_weight*100:.2f}%")
    st.metric("Parag Parikh Weight", f"{parag_weight*100:.2f}%")
    st.metric("ICICI Liquid Weight", f"{liquid_weight*100:.2f}%")
    st.metric("Rebalancing Action", rebalance)

# --- Goal Progress Chart ---
if not sip_df.empty:
    st.line_chart(sip_df.set_index("Date")["Total Portfolio Value (₹)"])

# --- Rebalancing Log ---
st.subheader("🔁 Rebalancing Log")
st.dataframe(pd.DataFrame(st.session_state.rebalancing_log), use_container_width=True)

# --- Tax Tracker ---
st.subheader("💰 Tax Tracker")
st.dataframe(pd.DataFrame(st.session_state.tax_tracker), use_container_width=True)
