#!/usr/bin/env python3
"""
Test Google Sheets integration
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def test_google_sheets_connection(sheet_id):
    """Test connection to Google Sheets"""
    
    try:
        # Setup Google Sheets connection
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        print("1. Loading credentials...")
        creds = Credentials.from_service_account_file('google_credentials.json', scopes=scope)
        client = gspread.authorize(creds)
        print("✅ Credentials loaded successfully")
        
        print("2. Opening Google Sheet...")
        sheet = client.open_by_key(sheet_id).sheet1  # First worksheet
        print("✅ Sheet opened successfully")
        
        print("3. Testing write access...")
        # Test data
        test_row = [
            "2026-01-01",  # Period Start
            "2026-01-27",  # Period End
            "0.0000",      # Email per User
            "1.3000",      # Push per User  
            "0",           # Total Emails Sent
            "130000",      # Total Push Sent
            "100000",      # Total Users
            "9"            # Total Campaigns
        ]
        
        # Add test data
        sheet.append_row(test_row)
        print("✅ Test data written successfully")
        
        print("4. Reading back data...")
        all_values = sheet.get_all_values()
        print(f"✅ Sheet has {len(all_values)} rows")
        
        if len(all_values) > 0:
            print("Headers:", all_values[0])
        if len(all_values) > 1:
            print("Last row:", all_values[-1])
        
        return True
        
    except FileNotFoundError:
        print("❌ google_credentials.json not found")
        print("Please follow the setup guide to create this file")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("Google Sheets Integration Test")
    print("=" * 40)
    
    # You'll need to replace this with your actual Sheet ID
    sheet_id = input("Enter your Google Sheet ID: ").strip()
    
    if not sheet_id:
        print("❌ Sheet ID is required")
        return
    
    success = test_google_sheets_connection(sheet_id)
    
    if success:
        print("\n🎉 Google Sheets integration is working!")
        print("You can now run the full automation with Google Sheets updates.")
    else:
        print("\n❌ Google Sheets integration failed.")
        print("Please check the setup guide and try again.")

if __name__ == "__main__":
    main()