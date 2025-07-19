import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Define the fund codes and names
funds = {
    "INF109K01BL4": "ICICI Prudential Infrastructure Fund",
    "INF277K01HQ0": "Parag Parikh Flexi Cap Fund",
    "INF109K01VQ1": "ICICI Prudential Liquid Fund"
}

# AMFI NAV data URL
AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"

# Google Sheet details
SHEET_NAME = "SIP_NAV_History"
TAB_NAME = "NAV History"

# Load credentials and authorize gspread
def authorize_gspread():
    creds = Credentials.from_service_account_file("service_account.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    return client

# Fetch NAV for a given fund code
def fetch_nav(fund_code):
    response = requests.get(AMFI_URL)
    lines = response.text.splitlines()
    for line in lines:
        if fund_code in line:
            parts = line.strip().split(";")
            if len(parts) >= 7:
                try:
                    return float(parts[4]), parts[6]
                except ValueError:
                    continue
    return None, None

# Main function to update the sheet
def main():
    client = authorize_gspread()
    sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)

    nav_data = []
    for code, name in funds.items():
        nav, date = fetch_nav(code)
        if nav is not None and date is not None:
            nav_data.append([date, name, nav])

    if nav_data:
        sheet.append_rows(nav_data, value_input_option="USER_ENTERED")

if __name__ == "__main__":
    main()
