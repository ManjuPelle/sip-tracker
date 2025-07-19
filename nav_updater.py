import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Define the mutual funds to track
funds = {
    "ICICI Prudential Infrastructure Fund - Growth": "120503",
    "Parag Parikh Flexi Cap Fund - Growth": "120825",
    "ICICI Prudential Liquid Fund - Growth": "100049"
}

# Fetch NAV data from AMFI
def fetch_nav(scheme_code):
    url = f"https://www.amfiindia.com/spages/NAVAll.txt"
    response = requests.get(url)
    lines = response.text.splitlines()
    for line in lines:
        if line.startswith(scheme_code):
            parts = line.split(';')
            return float(parts[4]), parts[6]
    return None, None

# Authenticate with Google Sheets
def get_gsheet_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_file("service_account.json", scopes=scopes)
    client = gspread.authorize(credentials)
    return client

# Update Google Sheet
def update_sheet(data):
    client = get_gsheet_client()
    sheet = client.open("SIP_NAV_History").worksheet("NAV History")
    sheet.append_row(data, value_input_option="USER_ENTERED")

# Main logic
def main():
    today = datetime.today().strftime("%d-%m-%Y")
    row = [today]
    for name, code in funds.items():
        nav, date = fetch_nav(code)
        row.append(nav)
    update_sheet(row)

if __name__ == "__main__":
    main()
