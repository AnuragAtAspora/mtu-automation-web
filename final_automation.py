#!/usr/bin/env python3
"""
Complete MoEngage Automation - Working Version
Downloads reports, calculates metrics, updates Google Sheets
"""

import requests
import base64
import hashlib
import zipfile
import csv
import io
from datetime import datetime, timedelta
from calendar import monthrange
import gspread
from google.oauth2.service_account import Credentials

class MoEngageAutomation:
    def __init__(self, workspace_id, campaign_api_key, data_center="01"):
        self.workspace_id = workspace_id
        self.campaign_api_key = campaign_api_key
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
            print(f"Downloading report: {report_filename}")
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
                
                for row in csv_reader:
                    # Based on the sample data, push notifications are in 'All Platform Sent'
                    # You'll need to adjust these column names based on your actual reports
                    
                    # For push notifications
                    if 'All Platform Sent' in row:
                        push_count = int(row['All Platform Sent'] or 0)
                        push_sent += push_count
                    
                    # For email (you'll need to create/configure an email report too)
                    # This is just an example - adjust based on your email report columns
                    if 'Email Sent' in row:
                        email_count = int(row['Email Sent'] or 0)
                        email_sent += email_count
                
                print(f"📈 Parsed data - Emails: {email_sent}, Push: {push_sent}")
                
                return {
                    'email_sent': email_sent,
                    'push_sent': push_sent,
                    'csv_filename': csv_filename,
                    'total_campaigns': len(list(csv.DictReader(io.StringIO(csv_content))))
                }
                
        except Exception as e:
            print(f"❌ Parse error: {e}")
            return {'email_sent': 0, 'push_sent': 0}
    
    def get_user_count(self):
        """Get total user count - for now, ask user to input manually"""
        print("\n" + "="*50)
        print("USER COUNT NEEDED")
        print("="*50)
        print("Please provide your current total user base count.")
        print("You can find this in MoEngage Dashboard → Analytics → Key Metrics")
        print()
        
        while True:
            try:
                user_count = input("Enter total user count: ").strip()
                return int(user_count)
            except ValueError:
                print("Please enter a valid number.")
    
    def calculate_metrics(self, start_date, end_date, report_filename, user_count=None):
        """Calculate comms per user metrics"""
        
        print(f"Calculating metrics for: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Download report
        zip_content = self.download_report(report_filename)
        if not zip_content:
            return None
        
        # Parse data
        campaign_data = self.extract_and_parse_report(zip_content)
        
        # Get user count
        if not user_count:
            user_count = self.get_user_count()
        
        # Calculate metrics
        email_per_user = campaign_data['email_sent'] / user_count if user_count > 0 else 0
        push_per_user = campaign_data['push_sent'] / user_count if user_count > 0 else 0
        
        return {
            'period_start': start_date.strftime('%Y-%m-%d'),
            'period_end': end_date.strftime('%Y-%m-%d'),
            'email_sent': campaign_data['email_sent'],
            'push_sent': campaign_data['push_sent'],
            'total_users': user_count,
            'email_per_user': round(email_per_user, 4),
            'push_per_user': round(push_per_user, 4),
            'total_campaigns': campaign_data.get('total_campaigns', 0)
        }
    
    def update_google_sheet(self, metrics_data, sheet_id, sheet_name="Metrics"):
        """Update Google Sheet with calculated metrics"""
        try:
            # Setup Google Sheets connection
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            # You'll need to create service account credentials
            creds = Credentials.from_service_account_file('google_credentials.json', scopes=scope)
            client = gspread.authorize(creds)
            
            # Open the sheet
            sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
            
            # Prepare row data
            row_data = [
                metrics_data['period_start'],
                metrics_data['period_end'],
                metrics_data['email_per_user'],
                metrics_data['push_per_user'],
                metrics_data['email_sent'],
                metrics_data['push_sent'],
                metrics_data['total_users'],
                metrics_data['total_campaigns']
            ]
            
            # Append to next row
            sheet.append_row(row_data)
            
            print(f"✅ Successfully updated Google Sheet")
            
        except Exception as e:
            print(f"❌ Error updating Google Sheet: {e}")
            print("Make sure you have:")
            print("1. Created google_credentials.json file")
            print("2. Shared the sheet with the service account email")

def main():
    print("MoEngage Automation - Complete Solution")
    print("=" * 40)
    
    # Configuration
    WORKSPACE_ID = "95PNUHBSYSLLJZ22PEOFMKF2"
    CAMPAIGN_API_KEY = "3XMHJ83D2X4V"
    DATA_CENTER = "01"
    GOOGLE_SHEET_ID = "your_google_sheet_id_here"  # Replace with your sheet ID
    
    automation = MoEngageAutomation(WORKSPACE_ID, CAMPAIGN_API_KEY, DATA_CENTER)
    
    # Get inputs
    print("Current available report: API_Test_PN_report_20260128")
    report_filename = input("Report filename (or press Enter for default): ").strip() or "API_Test_PN_report_20260128"
    
    end_date = input("End date (YYYY-MM-DD): ").strip()
    
    # Validate date
    start_date, end_date_obj = automation.get_date_range(end_date)
    if not start_date:
        return
    
    # Calculate metrics
    metrics = automation.calculate_metrics(start_date, end_date_obj, report_filename)
    
    if metrics:
        print("\n" + "=" * 50)
        print("CALCULATED METRICS")
        print("=" * 50)
        print(f"Period: {metrics['period_start']} to {metrics['period_end']}")
        print(f"Email per user: {metrics['email_per_user']}")
        print(f"Push notifications per user: {metrics['push_per_user']}")
        print(f"Total emails sent: {metrics['email_sent']}")
        print(f"Total push notifications sent: {metrics['push_sent']}")
        print(f"Total user base: {metrics['total_users']}")
        print(f"Total campaigns processed: {metrics['total_campaigns']}")
        
        # Update Google Sheet
        if GOOGLE_SHEET_ID != "your_google_sheet_id_here":
            update_sheet = input("\nUpdate Google Sheet? (y/n): ").strip().lower()
            if update_sheet == 'y':
                automation.update_google_sheet(metrics, GOOGLE_SHEET_ID)
        else:
            print("\n📝 To enable Google Sheets update:")
            print("1. Replace GOOGLE_SHEET_ID with your actual sheet ID")
            print("2. Set up google_credentials.json file")

if __name__ == "__main__":
    main()