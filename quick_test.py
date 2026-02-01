#!/usr/bin/env python3
import gspread
from google.oauth2.service_account import Credentials

# Setup
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('google_credentials.json', scopes=scope)
client = gspread.authorize(creds)

# Test
sheet_id = "1A30FfO319eiKW0c6zHj2lwr04WLE0fL6eLteZf4CvHM"
sheet = client.open_by_key(sheet_id).sheet1

print("✅ Connected successfully!")
print("Sheet title:", sheet.title)

# Add test data
test_row = ["2026-01-28", "2026-01-28", "0.5", "1.2", "500", "1200", "1000", "5"]
sheet.append_row(test_row)
print("✅ Data added successfully!")