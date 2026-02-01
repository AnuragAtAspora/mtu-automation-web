#!/usr/bin/env python3
"""
Enhanced MoEngage to Google Sheets Automation
Downloads MoEngage reports, calculates metrics with automatic user count estimation
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

class EnhancedMoEngageAutomation:
    def __init__(self, workspace_id, campaign_api_key, google_sheet_id, data_center="01"):
        self.workspace_id = workspace_id
        self.campaign_api_key = campaign_api_key
        self.google_sheet_id = google_sheet_id
        self.data_center = data_center
        
    def estimate_user_count_from_campaigns(self, campaign_data):
        """
        Estimate user count from campaign data
        Uses the highest reach from campaigns as an approximation
        """
        try:
            # If we have reach data from campaigns, use the maximum
            max_reach = 0
            
            # Look for reach indicators in campaign data
            if 'max_reach' in campaign_data:
                max_reach = campaign_data['max_reach']
            elif 'push_sent' in campaign_data and campaign_data['push_sent'] > 0:
                # Estimate based on push sent (assuming not all users get push)
                # This is a rough estimate - push campaigns typically reach 60-80% of users
                estimated_users = int(campaign_data['push_sent'] / 0.7)  # Assume 70% reach
                max_reach = estimated_users
            
            return max_reach if max_reach > 0 else None
            
        except Exception as e:
            print(f"⚠️  Could not estimate user count: {e}")
            return None
    
    def get_user_count_from_stats_api(self, start_date, end_date):
        """
        Try to get user metrics from MoEngage Stats API
        This might give us reach data we can use to estimate users
        """
        try:
            url = f"https://api-{self.data_center}.moengage.com/v1/stats"
            
            # Auth
            auth_string = f"{self.workspace_id}:{self.campaign_api_key}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_auth}',
                'Content-Type': 'application/json',
                'MOE-APPKEY': self.workspace_id
            }
            
            payload = {
                "request_id": f"user_count_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "start_date": start_date,
                "end_date": end_date,
                "attribution_type": "TOTAL_CONVERSIONS",
                "metric_type": "UNIQUE",
                "limit": 10
            }
            
            print("🔍 Trying to fetch user metrics from Stats API...")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Stats API response received")
                
                # Try to extract user count from response
                # This is experimental - the exact structure depends on your data
                max_users = 0
                if 'data' in data:
                    for campaign in data['data']:
                        # Look for user-related metrics
                        if 'unique_users' in campaign:
                            max_users = max(max_users, campaign['unique_users'])
                        elif 'reach' in campaign:
                            max_users = max(max_users, campaign['reach'])
                
                return max_users if max_users > 0 else None
            else:
                print(f"⚠️  Stats API returned {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"⚠️  Stats API error: {e}")
            return None
    
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
        
        # Generate signature
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
        """Extract ZIP and parse CSV to get email/push counts and user estimates"""
        
        try:
            # Extract ZIP content
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
                csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                
                if not csv_files:
                    print("❌ No CSV files found in report")
                    return {'email_sent': 0, 'push_sent': 0, 'estimated_users': None}
                
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
                max_reach = 0
                
                for row in csv_reader:
                    campaign_count += 1
                    
                    # Push notifications
                    if 'All Platform Sent' in row:
                        push_count = int(row['All Platform Sent'] or 0)
                        push_sent += push_count
                    
                    # Email
                    if 'Email Sent' in row:
                        email_count = int(row['Email Sent'] or 0)
                        email_sent += email_count
                    
                    # Try to find reach/user indicators
                    for key, value in row.items():
                        if 'reach' in key.lower() or 'user' in key.lower():
                            try:
                                reach_value = int(value or 0)
                                max_reach = max(max_reach, reach_value)
                            except:
                                pass
                
                # Estimate users from campaign data
                estimated_users = None
                if max_reach > 0:
                    estimated_users = max_reach
                elif push_sent > 0:
                    # Rough estimate: assume push reaches 70% of users
                    estimated_users = int(push_sent / 0.7)
                
                print(f"📈 Parsed data - Emails: {email_sent:,}, Push: {push_sent:,}, Campaigns: {campaign_count}")
                if estimated_users:
                    print(f"👥 Estimated users: {estimated_users:,}")
                
                return {
                    'email_sent': email_sent,
                    'push_sent': push_sent,
                    'csv_filename': csv_filename,
                    'total_campaigns': campaign_count,
                    'estimated_users': estimated_users,
                    'max_reach': max_reach
                }
                
        except Exception as e:
            print(f"❌ Parse error: {e}")
            return {'email_sent': 0, 'push_sent': 0, 'total_campaigns': 0, 'estimated_users': None}
    
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
            
        except Exception as e:
            print(f"❌ Error updating Google Sheet: {e}")
            return False
    
    def run_automation(self, end_date, report_filename, manual_user_count=None):
        """Run the complete automation with automatic user count detection"""
        
        print("🚀 Starting Enhanced MoEngage to Google Sheets Automation")
        print("=" * 60)
        
        # 1. Validate date range
        start_date, end_date_obj = self.get_date_range(end_date)
        if not start_date:
            return False
        
        print(f"📅 Period: {start_date.strftime('%Y-%m-%d')} to {end_date_obj.strftime('%Y-%m-%d')}")
        
        # 2. Download report
        zip_content = self.download_report(report_filename)
        if not zip_content:
            return False
        
        # 3. Parse data and estimate users
        campaign_data = self.extract_and_parse_report(zip_content)
        
        # 4. Determine user count
        user_count = manual_user_count
        
        if not user_count:
            print("\n🔍 Attempting to determine user count automatically...")
            
            # Try Stats API first
            api_user_count = self.get_user_count_from_stats_api(
                start_date.strftime('%Y-%m-%d'), 
                end_date_obj.strftime('%Y-%m-%d')
            )
            
            if api_user_count:
                user_count = api_user_count
                print(f"✅ User count from Stats API: {user_count:,}")
            elif campaign_data['estimated_users']:
                user_count = campaign_data['estimated_users']
                print(f"✅ Estimated user count from campaigns: {user_count:,}")
            else:
                print("⚠️  Could not determine user count automatically")
                user_count = int(input("Please enter total user count manually: "))
        
        # 5. Calculate metrics
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
        
        # 6. Display results
        print("\n📊 CALCULATED METRICS")
        print("=" * 30)
        print(f"Email per user: {metrics['email_per_user']}")
        print(f"Push per user: {metrics['push_per_user']}")
        print(f"Total emails sent: {metrics['email_sent']:,}")
        print(f"Total push sent: {metrics['push_sent']:,}")
        print(f"Total users: {metrics['total_users']:,}")
        print(f"Total campaigns: {metrics['total_campaigns']}")
        
        # 7. Update Google Sheet
        success = self.update_google_sheet(metrics)
        
        if success:
            print(f"\n🎉 Automation completed successfully!")
            return True
        else:
            print(f"\n⚠️  Metrics calculated but Google Sheets update failed")
            return False

def main():
    print("Enhanced MoEngage to Google Sheets Automation")
    print("=" * 50)
    
    # Configuration
    WORKSPACE_ID = "95PNUHBSYSLLJZ22PEOFMKF2"
    CAMPAIGN_API_KEY = "3XMHJ83D2X4V"
    DATA_CENTER = "01"
    GOOGLE_SHEET_ID = "1A30FfO319eiKW0c6zHj2lwr04WLE0fL6eLteZf4CvHM"
    
    # Get inputs
    report_filename = input("Report filename (or press Enter for default): ").strip() or "API_Test_PN_report_20260128"
    end_date = input("End date (YYYY-MM-DD): ").strip()
    
    # Ask if user wants to provide manual count or try auto-detection
    auto_detect = input("Try to auto-detect user count? (y/n, default: y): ").strip().lower()
    manual_user_count = None
    
    if auto_detect == 'n':
        try:
            manual_user_count = int(input("Enter total user count: ").strip())
        except ValueError:
            print("❌ Invalid user count")
            return
    
    # Initialize and run automation
    automation = EnhancedMoEngageAutomation(WORKSPACE_ID, CAMPAIGN_API_KEY, GOOGLE_SHEET_ID, DATA_CENTER)
    
    success = automation.run_automation(end_date, report_filename, manual_user_count)
    
    if success:
        print("\n✅ All done! Check your Google Sheet for the updated data.")
    else:
        print("\n❌ Automation failed. Please check the errors above.")

if __name__ == "__main__":
    main()