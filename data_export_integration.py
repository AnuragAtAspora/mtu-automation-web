#!/usr/bin/env python3
"""
MoEngage Data Export Integration
Combines Campaign Reports API with Data Export API for comprehensive automation
"""

import requests
import base64
import hashlib
import zipfile
import csv
import io
import sqlite3
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

class DataExportIntegration:
    def __init__(self, workspace_id, campaign_api_key, google_sheet_id, data_center="01", webhook_db_path="moengage_data.db"):
        self.workspace_id = workspace_id
        self.campaign_api_key = campaign_api_key
        self.google_sheet_id = google_sheet_id
        self.data_center = data_center
        self.webhook_db_path = webhook_db_path
    
    def get_user_count_from_webhook_data(self, date=None):
        """Get user count from webhook data stored in SQLite"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            conn = sqlite3.connect(self.webhook_db_path)
            cursor = conn.cursor()
            
            # Check if we have data for this date
            cursor.execute('''
                SELECT total_users, active_users, email_users, push_users 
                FROM user_metrics 
                WHERE date = ?
            ''', (date,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'total_users': result[0],
                    'active_users': result[1],
                    'email_users': result[2], 
                    'push_users': result[3],
                    'source': 'webhook_data',
                    'date': date
                }
            else:
                print(f"⚠️  No webhook data found for {date}")
                return None
                
        except Exception as e:
            print(f"❌ Error accessing webhook data: {e}")
            return None
    
    def get_user_count_from_date_range(self, start_date, end_date):
        """Get user metrics for a date range from webhook data"""
        try:
            conn = sqlite3.connect(self.webhook_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    MAX(total_users) as max_users,
                    AVG(active_users) as avg_active_users,
                    MAX(email_users) as max_email_users,
                    MAX(push_users) as max_push_users,
                    SUM(campaign_interactions) as total_interactions
                FROM user_metrics 
                WHERE date BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return {
                    'max_users': result[0],
                    'avg_active_users': int(result[1]) if result[1] else 0,
                    'max_email_users': result[2] if result[2] else 0,
                    'max_push_users': result[3] if result[3] else 0,
                    'total_interactions': result[4] if result[4] else 0,
                    'source': 'webhook_data_range',
                    'start_date': start_date,
                    'end_date': end_date
                }
            else:
                print(f"⚠️  No webhook data found for range {start_date} to {end_date}")
                return None
                
        except Exception as e:
            print(f"❌ Error accessing webhook data range: {e}")
            return None
    
    def get_campaign_data_from_webhook(self, start_date, end_date):
        """Get campaign interaction data from webhook events"""
        try:
            conn = sqlite3.connect(self.webhook_db_path)
            cursor = conn.cursor()
            
            # Convert dates to timestamps
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()) + 86400  # End of day
            
            cursor.execute('''
                SELECT 
                    campaign_channel,
                    COUNT(*) as interactions,
                    COUNT(DISTINCT uid) as unique_users,
                    COUNT(DISTINCT campaign_id) as unique_campaigns
                FROM events 
                WHERE event_time BETWEEN ? AND ?
                AND campaign_channel != ''
                GROUP BY campaign_channel
            ''', (start_ts, end_ts))
            
            results = cursor.fetchall()
            conn.close()
            
            webhook_data = {
                'email_interactions': 0,
                'push_interactions': 0,
                'total_interactions': 0,
                'unique_users': 0,
                'unique_campaigns': 0
            }
            
            for row in results:
                channel, interactions, users, campaigns = row
                webhook_data['total_interactions'] += interactions
                webhook_data['unique_users'] = max(webhook_data['unique_users'], users)
                webhook_data['unique_campaigns'] += campaigns
                
                if 'email' in channel.lower():
                    webhook_data['email_interactions'] += interactions
                elif 'push' in channel.lower():
                    webhook_data['push_interactions'] += interactions
            
            return webhook_data if webhook_data['total_interactions'] > 0 else None
            
        except Exception as e:
            print(f"❌ Error getting campaign data from webhook: {e}")
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
    
    def download_campaign_report(self, report_filename):
        """Download campaign report from MoEngage (existing functionality)"""
        signature_key = f"{self.workspace_id}|{report_filename}|{self.campaign_api_key}"
        signature = hashlib.sha256(signature_key.encode('utf-8')).hexdigest()
        
        url = f"https://api-{self.data_center}.moengage.com/campaign_reports/rest_api/{self.workspace_id}/{report_filename}"
        
        auth_string = f"{self.workspace_id}:{self.campaign_api_key}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'MOE-APPKEY': self.workspace_id,
            'Signature': signature
        }
        
        try:
            print(f"📥 Downloading campaign report: {report_filename}")
            response = requests.get(url, headers=headers, timeout=60)
            
            if response.status_code == 200:
                print("✅ Campaign report downloaded successfully")
                return response.content
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Download error: {e}")
            return None
    
    def parse_campaign_report(self, zip_content):
        """Parse campaign report ZIP file"""
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
                csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                
                if not csv_files:
                    print("❌ No CSV files found in report")
                    return {'email_sent': 0, 'push_sent': 0, 'total_campaigns': 0}
                
                csv_filename = csv_files[0]
                with zip_file.open(csv_filename) as csv_file:
                    csv_content = csv_file.read().decode('utf-8')
                
                print(f"📊 Parsing campaign report: {csv_filename}")
                
                csv_reader = csv.DictReader(io.StringIO(csv_content))
                
                email_sent = 0
                push_sent = 0
                campaign_count = 0
                
                for row in csv_reader:
                    campaign_count += 1
                    
                    if 'All Platform Sent' in row:
                        push_count = int(row['All Platform Sent'] or 0)
                        push_sent += push_count
                    
                    if 'Email Sent' in row:
                        email_count = int(row['Email Sent'] or 0)
                        email_sent += email_count
                
                return {
                    'email_sent': email_sent,
                    'push_sent': push_sent,
                    'total_campaigns': campaign_count,
                    'csv_filename': csv_filename
                }
                
        except Exception as e:
            print(f"❌ Parse error: {e}")
            return {'email_sent': 0, 'push_sent': 0, 'total_campaigns': 0}
    
    def update_google_sheet(self, metrics_data, sheet_name="Sheet1"):
        """Update Google Sheet with calculated metrics"""
        try:
            print("📝 Connecting to Google Sheets...")
            
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            creds = Credentials.from_service_account_file('google_credentials.json', scopes=scope)
            client = gspread.authorize(creds)
            
            sheet = client.open_by_key(self.google_sheet_id).worksheet(sheet_name)
            
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
            
            sheet.append_row(row_data)
            
            print(f"✅ Successfully updated Google Sheet!")
            return True
            
        except Exception as e:
            print(f"❌ Error updating Google Sheet: {e}")
            return False
    
    def run_integrated_automation(self, end_date, report_filename=None, prefer_webhook_data=True):
        """Run automation using both Campaign Reports and Data Export APIs"""
        
        print("🚀 Starting Integrated MoEngage Automation")
        print("📊 Using Campaign Reports API + Data Export API")
        print("=" * 60)
        
        # 1. Get date range
        start_date, end_date_obj = self.get_date_range(end_date)
        if not start_date:
            return False
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date_obj.strftime('%Y-%m-%d')
        
        print(f"📅 Period: {start_date_str} to {end_date_str}")
        
        # 2. Get user count from webhook data (preferred)
        user_data = None
        if prefer_webhook_data:
            print("\n🔍 Checking Data Export API data...")
            user_data = self.get_user_count_from_date_range(start_date_str, end_date_str)
            
            if user_data:
                print(f"✅ Found webhook data - Max users: {user_data['max_users']:,}")
                user_count = user_data['max_users']
            else:
                print("⚠️  No webhook data available, will use manual input")
                user_count = int(input("Enter total user count: "))
        else:
            user_count = int(input("Enter total user count: "))
        
        # 3. Get campaign data
        campaign_data = {'email_sent': 0, 'push_sent': 0, 'total_campaigns': 0}
        
        # Try webhook data first
        webhook_campaign_data = self.get_campaign_data_from_webhook(start_date_str, end_date_str)
        if webhook_campaign_data:
            print(f"✅ Found webhook campaign data - Interactions: {webhook_campaign_data['total_interactions']:,}")
            # Use webhook interaction data as sent counts (approximation)
            campaign_data['email_sent'] = webhook_campaign_data['email_interactions']
            campaign_data['push_sent'] = webhook_campaign_data['push_interactions'] 
            campaign_data['total_campaigns'] = webhook_campaign_data['unique_campaigns']
        
        # If we have a report filename, also get campaign report data
        if report_filename:
            print(f"\n📥 Also downloading campaign report: {report_filename}")
            zip_content = self.download_campaign_report(report_filename)
            if zip_content:
                report_data = self.parse_campaign_report(zip_content)
                # Use report data if it has higher numbers (more accurate)
                if report_data['email_sent'] > campaign_data['email_sent']:
                    campaign_data['email_sent'] = report_data['email_sent']
                if report_data['push_sent'] > campaign_data['push_sent']:
                    campaign_data['push_sent'] = report_data['push_sent']
                if report_data['total_campaigns'] > campaign_data['total_campaigns']:
                    campaign_data['total_campaigns'] = report_data['total_campaigns']
        
        # 4. Calculate metrics
        email_per_user = campaign_data['email_sent'] / user_count if user_count > 0 else 0
        push_per_user = campaign_data['push_sent'] / user_count if user_count > 0 else 0
        
        metrics = {
            'period_start': start_date_str,
            'period_end': end_date_str,
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
        
        if user_data:
            print(f"\n📈 ADDITIONAL DATA EXPORT METRICS")
            print(f"Average active users: {user_data.get('avg_active_users', 0):,}")
            print(f"Max email users: {user_data.get('max_email_users', 0):,}")
            print(f"Max push users: {user_data.get('max_push_users', 0):,}")
        
        # 6. Update Google Sheet
        success = self.update_google_sheet(metrics)
        
        if success:
            print(f"\n🎉 Integrated automation completed successfully!")
            return True
        else:
            print(f"\n⚠️  Metrics calculated but Google Sheets update failed")
            return False

def main():
    print("Integrated MoEngage Automation")
    print("Campaign Reports API + Data Export API")
    print("=" * 50)
    
    # Configuration
    WORKSPACE_ID = "95PNUHBSYSLLJZ22PEOFMKF2"
    CAMPAIGN_API_KEY = "3XMHJ83D2X4V"
    DATA_CENTER = "01"
    GOOGLE_SHEET_ID = "1A30FfO319eiKW0c6zHj2lwr04WLE0fL6eLteZf4CvHM"
    
    # Get inputs
    end_date = input("End date (YYYY-MM-DD): ").strip()
    report_filename = input("Campaign report filename (optional): ").strip() or None
    
    use_webhook = input("Use Data Export API data if available? (y/n, default: y): ").strip().lower() != 'n'
    
    # Initialize and run
    integration = DataExportIntegration(WORKSPACE_ID, CAMPAIGN_API_KEY, GOOGLE_SHEET_ID, DATA_CENTER)
    
    success = integration.run_integrated_automation(end_date, report_filename, use_webhook)
    
    if success:
        print("\n✅ All done! Check your Google Sheet for the updated data.")
    else:
        print("\n❌ Automation failed. Please check the errors above.")

if __name__ == "__main__":
    main()