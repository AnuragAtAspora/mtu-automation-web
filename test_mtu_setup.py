#!/usr/bin/env python3
"""
Test MTU Sheet Setup
Creates the MTU Metrics sheet tab and sets up headers
"""

import gspread
from google.oauth2.service_account import Credentials

def test_mtu_sheet_setup():
    """Test creating MTU Metrics sheet tab"""
    
    try:
        print("🧪 Testing MTU Sheet Setup")
        print("=" * 30)
        
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
        print(f"✅ Opened spreadsheet: {spreadsheet.title}")
        
        # Check if MTU Metrics sheet exists
        try:
            sheet = spreadsheet.worksheet("MTU Metrics")
            print("✅ MTU Metrics sheet already exists")
            
            # Show current headers
            headers = sheet.row_values(1)
            print(f"   Current headers: {len(headers)} columns")
            for i, header in enumerate(headers, 1):
                print(f"   {i:2d}. {header}")
                
        except gspread.WorksheetNotFound:
            print("2. Creating MTU Metrics sheet...")
            
            # Create new sheet
            sheet = spreadsheet.add_worksheet(title="MTU Metrics", rows=1000, cols=25)
            print("✅ Created new MTU Metrics sheet")
            
            # Add headers
            headers = [
                "Period Start", "Period End",
                "UK Total Users", "UK Active Users (60d)",
                "UK Push All Users", "UK Push All %", 
                "UK Push Active Users", "UK Push Active %",
                "UK Email All Users", "UK Email All %",
                "UK Email Active Users", "UK Email Active %",
                "UAE Total Users", "UAE Active Users (60d)",
                "UAE Push All Users", "UAE Push All %",
                "UAE Push Active Users", "UAE Push Active %", 
                "UAE Email All Users", "UAE Email All %",
                "UAE Email Active Users", "UAE Email Active %"
            ]
            
            print("3. Adding headers...")
            sheet.append_row(headers)
            print("✅ Added headers to MTU Metrics sheet")
            
            print(f"\n📊 Created {len(headers)} columns:")
            for i, header in enumerate(headers, 1):
                print(f"   {i:2d}. {header}")
        
        # Add sample data for testing
        print("\n4. Adding sample test data...")
        sample_data = [
            "2026-01-01", "2026-01-27",  # Period
            "50000", "30000",  # UK totals
            "15000", "30.0", "9000", "30.0",  # UK Push
            "12000", "24.0", "7200", "24.0",  # UK Email  
            "75000", "45000",  # UAE totals
            "22500", "30.0", "13500", "30.0",  # UAE Push
            "18000", "24.0", "10800", "24.0"   # UAE Email
        ]
        
        sheet.append_row(sample_data)
        print("✅ Added sample test data")
        
        print(f"\n🎉 MTU Sheet setup completed successfully!")
        print(f"📋 Sheet URL: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}")
        print(f"📊 Check the 'MTU Metrics' tab")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up MTU sheet: {e}")
        return False

if __name__ == "__main__":
    test_mtu_sheet_setup()