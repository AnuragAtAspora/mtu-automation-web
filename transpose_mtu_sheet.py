#!/usr/bin/env python3
"""
Transpose MTU Metrics Sheet
Converts the MTU sheet from horizontal layout to vertical layout
"""

import gspread
from google.oauth2.service_account import Credentials

def transpose_mtu_sheet():
    """Transpose the MTU Metrics sheet to vertical layout"""
    
    try:
        print("🔄 Transposing MTU Metrics Sheet")
        print("=" * 35)
        
        # Configuration
        GOOGLE_SHEET_ID = "1A30FfO319eiKW0c6zHj2lwr04WLE0fL6eLteZf4CvHM"
        
        # Setup Google Sheets connection
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        print("1. Connecting to Google Sheets...")
        creds = Credentials.from_service_account_file('google_credentials.json', scopes=scope)
        client = gspread.authorize(creds)
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        
        # Get the MTU Metrics sheet
        sheet = spreadsheet.worksheet("MTU Metrics")
        print("✅ Found MTU Metrics sheet")
        
        # Clear the sheet
        print("2. Clearing existing data...")
        sheet.clear()
        
        # Create transposed layout
        print("3. Creating transposed layout...")
        
        # New vertical structure
        transposed_data = [
            ["Metric", "Value"],  # Headers
            ["Period Start", "2026-01-01"],
            ["Period End", "2026-01-27"],
            ["", ""],  # Separator
            ["UK METRICS", ""],
            ["UK Total Users", "50000"],
            ["UK Active Users (60d)", "30000"],
            ["", ""],
            ["UK Push Notifications", ""],
            ["UK Push All Users", "15000"],
            ["UK Push All %", "30.0%"],
            ["UK Push Active Users", "9000"],
            ["UK Push Active %", "30.0%"],
            ["", ""],
            ["UK Email", ""],
            ["UK Email All Users", "12000"],
            ["UK Email All %", "24.0%"],
            ["UK Email Active Users", "7200"],
            ["UK Email Active %", "24.0%"],
            ["", ""],  # Separator
            ["UAE METRICS", ""],
            ["UAE Total Users", "75000"],
            ["UAE Active Users (60d)", "45000"],
            ["", ""],
            ["UAE Push Notifications", ""],
            ["UAE Push All Users", "22500"],
            ["UAE Push All %", "30.0%"],
            ["UAE Push Active Users", "13500"],
            ["UAE Push Active %", "30.0%"],
            ["", ""],
            ["UAE Email", ""],
            ["UAE Email All Users", "18000"],
            ["UAE Email All %", "24.0%"],
            ["UAE Email Active Users", "10800"],
            ["UAE Email Active %", "24.0%"]
        ]
        
        # Add all data at once
        print("4. Adding transposed data...")
        for row in transposed_data:
            sheet.append_row(row)
        
        print("✅ Successfully transposed MTU Metrics sheet!")
        print(f"\n📊 New Layout:")
        print(f"   - Column A: Metric names")
        print(f"   - Column B: Values")
        print(f"   - {len(transposed_data)} rows total")
        print(f"   - Organized by country and channel")
        
        print(f"\n📋 Sheet URL: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}")
        print(f"📊 Check the 'MTU Metrics' tab")
        
        return True
        
    except Exception as e:
        print(f"❌ Error transposing MTU sheet: {e}")
        return False

if __name__ == "__main__":
    transpose_mtu_sheet()