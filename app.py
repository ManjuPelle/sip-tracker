
import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe

# Streamlit page config
st.set_page_config(page_title="SIP Wealth Tracker", layout="wide")
st.title("📈 SIP Wealth Tracker")

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# Load NAV History from Google Sheet
try:
    sheet = client.open("SIP_NAV_HISTORY").worksheet("NAV History")
    nav_df = get_as_dataframe(sheet, evaluate_formulas=True)
    nav_df = nav_df.dropna(subset=["Date"])
    nav_df["Date"] = pd.to_datetime(nav_df["Date"])
    nav_df = nav_df.sort_values("Date")
except Exception as e:
    st.error(f"Failed to load NAV History: {e}")
    nav_df = pd.DataFrame()

# Show latest NAVs
if not nav_df.empty:
    st.subheader("📋 Latest NAVs")
    latest = nav_df.iloc[-1]
    st.write(f"**Date:** {latest['Date'].date()}")
    st.metric("ICICI Infra NAV", f"{latest['ICICI Infra NAV']:.2f}")
    st.metric("Parag Parikh NAV", f"{latest['Parag Parikh NAV']:.2f}")
    st.metric("ICICI Liquid NAV", f"{latest['ICICI Liquid NAV']:.2f}")

    # Plot NAV trends
    st.subheader("📊 NAV Trend Over Time")
    fig, ax = plt.subplots()
    for col in nav_df.columns[1:]:
        ax.plot(nav_df["Date"], nav_df[col], label=col)
    ax.set_xlabel("Date")
    ax.set_ylabel("NAV")
    ax.set_title("NAV Trends")
    ax.legend()
    st.pyplot(fig)

# Initialize session state for SIP data
if "sip_data" not in st.session_state:
    st.session_state.sip_data = []

# SIP Entry Form
with st.form("sip_form"):
    st.subheader("➕ Add SIP Entry")
    sip_date = st.date_input("SIP Date", value=datetime.date.today())
    month_number = st.number_input("Month Number", min_value=1, step=1)
    year = st.number_input("Year", min_value=2020, step=1)
    total_sip = st.number_input("Total SIP (₹)", min_value=0, step=1000, value=25000)

    submitted = st.form_submit_button("Add Entry")
    if submitted:
        icici_infra_sip = total_sip * 0.6
        parag_parikh_sip = total_sip * 0.3
        icici_liquid_sip = total_sip * 0.1 if month_number <= 36 else 0

        # Use latest NAVs if available
        if not nav_df.empty:
            nav_infra = latest['ICICI Infra NAV']
            nav_parikh = latest['Parag Parikh NAV']
            nav_liquid = latest['ICICI Liquid NAV']
        else:
            nav_infra = 191.49
            nav_parikh = 92.33
            nav_liquid = 400

        infra_units = icici_infra_sip / nav_infra
        parikh_units = parag_parikh_sip / nav_parikh
        liquid_units = icici_liquid_sip / nav_liquid

        infra_value = infra_units * nav_infra
        parikh_value = parikh_units * nav_parikh
        liquid_value = liquid_units * nav_liquid

        total_value = infra_value + parikh_value + liquid_value
        goal_progress = total_value / 10000000
        step_up_check = "OK" if (month_number % 12 == 1 and total_sip == 25000 * (1.1 ** ((month_number - 1) // 12))) else ""

        st.session_state.sip_data.append({
            "Date": sip_date.strftime("%d/%m/%Y"),
            "Month Number": month_number,
            "Year": year,
            "Total SIP (₹)": total_sip,
            "ICICI Infra SIP (₹)": icici_infra_sip,
            "Parag Parikh SIP (₹)": parag_parikh_sip,
            "ICICI Liquid SIP (₹)": icici_liquid_sip,
            "ICICI Infra Units": round(infra_units, 2),
            "Parag Parikh Units": round(parikh_units, 2),
            "ICICI Liquid Units": round(liquid_units, 2),
            "ICICI Infra Value (₹)": round(infra_value, 2),
            "Parag Parikh Value (₹)": round(parikh_value, 2),
            "ICICI Liquid Value (₹)": round(liquid_value, 2),
            "Total Portfolio Value (₹)": round(total_value, 2),
            "Goal Progress (%)": f"{round(goal_progress * 100, 2)}%",
            "Step-Up Check": step_up_check
        })

# Display SIP Tracker Table
if st.session_state.sip_data:
    st.subheader("📋 SIP Tracker Table")
    df = pd.DataFrame(st.session_state.sip_data)
    st.dataframe(df, use_container_width=True)

    # Summary Dashboard
    st.subheader("📊 Summary Dashboard")
    total_invested = df["Total SIP (₹)"].sum()
    current_value = df["Total Portfolio Value (₹)"].iloc[-1]
    goal_progress = current_value / 10000000

    infra_weight = df["ICICI Infra Value (₹)"].iloc[-1] / current_value if current_value else 0
    parikh_weight = df["Parag Parikh Value (₹)"].iloc[-1] / current_value if current_value else 0
    liquid_weight = df["ICICI Liquid Value (₹)"].iloc[-1] / current_value if current_value else 0

    rebalance_needed = (
        infra_weight > 0.65 or infra_weight < 0.55 or
        parikh_weight > 0.35 or parikh_weight < 0.25 or
        liquid_weight > 0.15 or liquid_weight < 0.05
    )

    st.metric("Total Invested", f"₹{total_invested:,.0f}")
    st.metric("Current Value", f"₹{current_value:,.0f}")
    st.metric("Goal Progress", f"{goal_progress*100:.2f}%")
    st.metric("ICICI Infra Weight", f"{infra_weight*100:.2f}%")
    st.metric("Parag Parikh Weight", f"{parikh_weight*100:.2f}%")
    st.metric("ICICI Liquid Weight", f"{liquid_weight*100:.2f}%")
    st.markdown(f"**Rebalancing Action:** {'🔁 Rebalance Needed' if rebalance_needed else '✅ No Action'}")
