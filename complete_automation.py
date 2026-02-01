#!/usr/bin/env python3
"""
Complete MoEngage to Google Sheets Automation
Downloads MoEngage reports, calculates metrics, and updates Google Sheets
"""

import requests
import base64
import hashlib
import zipfile
import csv
import io
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

class MoEngageToSheetsAutomation:
    def __init__(self, workspace_id, campaign_api_key, google_sheet_id, data_center="01"):
        self.workspace_id = workspace_id
        self.campaign_api_key = campaign_api_key
        self.google_sheet_id = google_sheet_id
        self.data_center = data_center
        
    def get_date_range(self, end_date_str):
        """Get date range from month start to selected date"""
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            yesterday = datetime.now() - timedelta(days=1)
            
            if end_date > yesterday:
                raise ValueError(f"End date cannot exceed {yesterday.strftime('%Y-%m-%d')}")
            
            start_date = end_date.replace(day=1)
            return start_date, end_date
            
        except ValueError as e:
            print(f"Date error: {e}")
            return None, None
    
    def download_report(self, report_filename):
        """Download campaign report from MoEngage"""
        
        # Generate signature: App_ID|FILENAME|SECRET_KEY
        signature_key = f"{self.workspace_id}|{report_filename}|{self.campaign_api_key}"
        signature = hashlib.sha256(signature_key.encode('utf-8')).hexdigest()
        
        url = f"https://api-{self.data_center}.moengage.com/campaign_reports/rest_api/{self.workspace_id}/{report_filename}"
        
        # Headers
        auth_string = f"{self.workspace_id}:{self.campaign_api_key}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'MOE-APPKEY': self.workspace_id,
            'Signature': signature
        }
        
        try:
            print(f"📥 Downloading report: {report_filename}")
            response = requests.get(url, headers=headers, timeout=60)
            
            if response.status_code == 200:
                print("✅ Report downloaded successfully")
                return response.content
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Download error: {e}")
            return None
    
    def extract_and_parse_report(self, zip_content):
        """Extract ZIP and parse CSV to get email/push counts"""
        
        try:
            # Extract ZIP content
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
                csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                
                if not csv_files:
                    print("❌ No CSV files found in report")
                    return {'email_sent': 0, 'push_sent': 0}
                
                # Read the first CSV file
                csv_filename = csv_files[0]
                with zip_file.open(csv_filename) as csv_file:
                    csv_content = csv_file.read().decode('utf-8')
                
                print(f"📊 Parsing CSV: {csv_filename}")
                
                # Parse CSV
                csv_reader = csv.DictReader(io.StringIO(csv_content))
                
                email_sent = 0
                push_sent = 0
                campaign_count = 0
                
                for row in csv_reader:
                    campaign_count += 1
                    
                    # For push notifications (based on your report structure)
                    if 'All Platform Sent' in row:
                        push_count = int(row['All Platform Sent'] or 0)
                        push_sent += push_count
                    
                    # For email (you'll need to create/configure an email report too)
                    if 'Email Sent' in row:
                        email_count = int(row['Email Sent'] or 0)
                        email_sent += email_count
                
                print(f"📈 Parsed data - Emails: {email_sent:,}, Push: {push_sent:,}, Campaigns: {campaign_count}")
                
                return {
                    'email_sent': email_sent,
                    'push_sent': push_sent,
                    'csv_filename': csv_filename,
                    'total_campaigns': campaign_count
                }
                
        except Exception as e:
            print(f"❌ Parse error: {e}")
            return {'email_sent': 0, 'push_sent': 0, 'total_campaigns': 0}
    
    def update_google_sheet(self, metrics_data, sheet_name="Sheet1"):
        """Update Google Sheet with calculated metrics"""
        try:
            print("📝 Connecting to Google Sheets...")
            
            # Setup Google Sheets connection
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            creds = Credentials.from_service_account_file('google_credentials.json', scopes=scope)
            client = gspread.authorize(creds)
            
            # Open the sheet
            sheet = client.open_by_key(self.google_sheet_id).worksheet(sheet_name)
            
            # Prepare row data
            row_data = [
                metrics_data['period_start'],
                metrics_data['period_end'],
                str(metrics_data['email_per_user']),
                str(metrics_data['push_per_user']),
                str(metrics_data['email_sent']),
                str(metrics_data['push_sent']),
                str(metrics_data['total_users']),
                str(metrics_data['total_campaigns'])
            ]
            
            # Append to next row
            sheet.append_row(row_data)
            
            print(f"✅ Successfully updated Google Sheet!")
            print(f"📊 Added row: {metrics_data['period_start']} to {metrics_data['period_end']}")
            
            return True
            
        except FileNotFoundError:
            print("❌ google_credentials.json not found")
            print("Please follow the setup guide to create this file")
            return False
            
        except Exception as e:
            print(f"❌ Error updating Google Sheet: {e}")
            return False
    
    def run_automation(self, end_date, report_filename, user_count):
        """Run the complete automation"""
        
        print("🚀 Starting MoEngage to Google Sheets Automation")
        print("=" * 50)
        
        # 1. Validate date range
        start_date, end_date_obj = self.get_date_range(end_date)
        if not start_date:
            return False
        
        print(f"📅 Period: {start_date.strftime('%Y-%m-%d')} to {end_date_obj.strftime('%Y-%m-%d')}")
        
        # 2. Download report
        zip_content = self.download_report(report_filename)
        if not zip_content:
            return False
        
        # 3. Parse data
        campaign_data = self.extract_and_parse_report(zip_content)
        
        # 4. Calculate metrics
        email_per_user = campaign_data['email_sent'] / user_count if user_count > 0 else 0
        push_per_user = campaign_data['push_sent'] / user_count if user_count > 0 else 0
        
        metrics = {
            'period_start': start_date.strftime('%Y-%m-%d'),
            'period_end': end_date_obj.strftime('%Y-%m-%d'),
            'email_sent': campaign_data['email_sent'],
            'push_sent': campaign_data['push_sent'],
            'total_users': user_count,
            'email_per_user': round(email_per_user, 4),
            'push_per_user': round(push_per_user, 4),
            'total_campaigns': campaign_data['total_campaigns']
        }
        
        # 5. Display results
        print("\n📊 CALCULATED METRICS")
        print("=" * 30)
        print(f"Email per user: {metrics['email_per_user']}")
        print(f"Push per user: {metrics['push_per_user']}")
        print(f"Total emails sent: {metrics['email_sent']:,}")
        print(f"Total push sent: {metrics['push_sent']:,}")
        print(f"Total users: {metrics['total_users']:,}")
        print(f"Total campaigns: {metrics['total_campaigns']}")
        
        # 6. Update Google Sheet
        success = self.update_google_sheet(metrics)
        
        if success:
            print(f"\n🎉 Automation completed successfully!")
            return True
        else:
            print(f"\n⚠️  Metrics calculated but Google Sheets update failed")
            return False

def main():
    print("MoEngage to Google Sheets Automation")
    print("=" * 40)
    
    # Configuration
    WORKSPACE_ID = "95PNUHBSYSLLJZ22PEOFMKF2"
    CAMPAIGN_API_KEY = "3XMHJ83D2X4V"
    DATA_CENTER = "01"
    
    # Get inputs
    google_sheet_id = input("Enter your Google Sheet ID: ").strip()
    if not google_sheet_id:
        print("❌ Google Sheet ID is required")
        return
    
    report_filename = input("Report filename (or press Enter for default): ").strip() or "API_Test_PN_report_20260128"
    end_date = input("End date (YYYY-MM-DD): ").strip()
    
    try:
        user_count = int(input("Total user count: ").strip())
    except ValueError:
        print("❌ Invalid user count")
        return
    
    # Initialize and run automation
    automation = MoEngageToSheetsAutomation(WORKSPACE_ID, CAMPAIGN_API_KEY, google_sheet_id, DATA_CENTER)
    
    success = automation.run_automation(end_date, report_filename, user_count)
    
    if success:
        print("\n✅ All done! Check your Google Sheet for the updated data.")
    else:
        print("\n❌ Automation failed. Please check the errors above.")

if __name__ == "__main__":
    main()