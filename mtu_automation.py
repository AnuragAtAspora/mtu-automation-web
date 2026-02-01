#!/usr/bin/env python3
"""
MTU (Marketing Touch Users) Automation
Calculates percentage of user base receiving communications based on MTU method
"""

import requests
import base64
import hashlib
import sqlite3
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

class MTUAutomation:
    def __init__(self, workspace_id, campaign_api_key, google_sheet_id, data_center="01", webhook_db_path="moengage_data.db"):
        self.workspace_id = workspace_id
        self.campaign_api_key = campaign_api_key
        self.google_sheet_id = google_sheet_id
        self.data_center = data_center
        self.webhook_db_path = webhook_db_path
    
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
    
    def get_users_received_comms_from_webhook(self, start_date, end_date, country, channel, active_only=False):
        """
        Get users who received communications from webhook data
        
        Args:
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            country: 'GB' for UK, 'AE' for UAE
            channel: 'push' or 'email'
            active_only: If True, only count users who transacted in last 60 days
        """
        try:
            conn = sqlite3.connect(self.webhook_db_path)
            cursor = conn.cursor()
            
            # Convert dates to timestamps
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()) + 86400
            
            # Base query for users who received communications
            base_query = '''
                SELECT COUNT(DISTINCT uid) as unique_users
                FROM events 
                WHERE event_time BETWEEN ? AND ?
                AND campaign_channel LIKE ?
                AND JSON_EXTRACT(user_attributes, '$.country') = ?
            '''
            
            # Channel filter
            channel_filter = f'%{channel}%'
            
            if active_only:
                # For 60-day active users, we need users who both:
                # 1. Received comms in the period
                # 2. Had transaction events in last 60 days
                
                # Get 60 days ago timestamp
                sixty_days_ago = int((datetime.now() - timedelta(days=60)).timestamp())
                
                query = '''
                    SELECT COUNT(DISTINCT e1.uid) as unique_users
                    FROM events e1
                    WHERE e1.event_time BETWEEN ? AND ?
                    AND e1.campaign_channel LIKE ?
                    AND JSON_EXTRACT(e1.user_attributes, '$.country') = ?
                    AND EXISTS (
                        SELECT 1 FROM events e2 
                        WHERE e2.uid = e1.uid 
                        AND e2.event_time >= ?
                        AND e2.event_name LIKE '%transaction%'
                        AND JSON_EXTRACT(e2.user_attributes, '$.country') = ?
                    )
                '''
                
                cursor.execute(query, (start_ts, end_ts, channel_filter, country, sixty_days_ago, country))
            else:
                cursor.execute(base_query, (start_ts, end_ts, channel_filter, country))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 0
            
        except Exception as e:
            print(f"❌ Error getting users who received {channel} comms: {e}")
            return 0
    
    def get_total_user_base_from_webhook(self, date, country):
        """Get total user base as of specific date for country"""
        try:
            conn = sqlite3.connect(self.webhook_db_path)
            cursor = conn.cursor()
            
            # Get timestamp for end of specified date
            date_ts = int(datetime.strptime(date, '%Y-%m-%d').timestamp()) + 86400
            
            # Count unique users who had any activity up to that date
            query = '''
                SELECT COUNT(DISTINCT uid) as total_users
                FROM events 
                WHERE event_time <= ?
                AND JSON_EXTRACT(user_attributes, '$.country') = ?
            '''
            
            cursor.execute(query, (date_ts, country))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 0
            
        except Exception as e:
            print(f"❌ Error getting total user base: {e}")
            return 0
    
    def get_active_users_from_webhook(self, country, days=60):
        """Get users who transacted in last N days"""
        try:
            conn = sqlite3.connect(self.webhook_db_path)
            cursor = conn.cursor()
            
            # Get timestamp for N days ago
            n_days_ago = int((datetime.now() - timedelta(days=days)).timestamp())
            
            query = '''
                SELECT COUNT(DISTINCT uid) as active_users
                FROM events 
                WHERE event_time >= ?
                AND event_name LIKE '%transaction%'
                AND JSON_EXTRACT(user_attributes, '$.country') = ?
            '''
            
            cursor.execute(query, (n_days_ago, country))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 0
            
        except Exception as e:
            print(f"❌ Error getting active users: {e}")
            return 0
    
    def calculate_mtu_metrics(self, start_date, end_date):
        """Calculate all MTU metrics for the specified period"""
        
        print(f"🔍 Calculating MTU metrics for {start_date} to {end_date}")
        
        metrics = {
            'period_start': start_date,
            'period_end': end_date
        }
        
        countries = {'UK': 'GB', 'UAE': 'AE'}
        channels = ['push', 'email']
        
        for country_name, country_code in countries.items():
            print(f"\n📊 Processing {country_name} ({country_code})...")
            
            # Get total user base as of end date
            total_users = self.get_total_user_base_from_webhook(end_date, country_code)
            print(f"   Total user base: {total_users:,}")
            
            # Get active users (transacted in last 60 days)
            active_users = self.get_active_users_from_webhook(country_code, 60)
            print(f"   Active users (60d): {active_users:,}")
            
            for channel in channels:
                # Metric 1: All users who received comms
                users_received_all = self.get_users_received_comms_from_webhook(
                    start_date, end_date, country_code, channel, active_only=False
                )
                
                percentage_all = (users_received_all / total_users * 100) if total_users > 0 else 0
                
                print(f"   {channel.title()} users (all): {users_received_all:,} ({percentage_all:.2f}%)")
                
                # Metric 2: Active users who received comms
                users_received_active = self.get_users_received_comms_from_webhook(
                    start_date, end_date, country_code, channel, active_only=True
                )
                
                percentage_active = (users_received_active / active_users * 100) if active_users > 0 else 0
                
                print(f"   {channel.title()} users (60d active): {users_received_active:,} ({percentage_active:.2f}%)")
                
                # Store metrics
                metrics[f'{country_name}_{channel}_all_users'] = users_received_all
                metrics[f'{country_name}_{channel}_all_percentage'] = round(percentage_all, 2)
                metrics[f'{country_name}_{channel}_active_users'] = users_received_active
                metrics[f'{country_name}_{channel}_active_percentage'] = round(percentage_active, 2)
            
            # Store base numbers
            metrics[f'{country_name}_total_users'] = total_users
            metrics[f'{country_name}_active_users'] = active_users
        
        return metrics
    
    def setup_mtu_sheet(self):
        """Create MTU Metrics sheet tab with transposed layout"""
        try:
            print("📝 Setting up MTU Metrics sheet...")
            
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            creds = Credentials.from_service_account_file('google_credentials.json', scopes=scope)
            client = gspread.authorize(creds)
            
            # Open the spreadsheet
            spreadsheet = client.open_by_key(self.google_sheet_id)
            
            # Check if MTU Metrics sheet exists
            try:
                sheet = spreadsheet.worksheet("MTU Metrics")
                print("✅ MTU Metrics sheet already exists")
            except gspread.WorksheetNotFound:
                # Create new sheet
                sheet = spreadsheet.add_worksheet(title="MTU Metrics", rows=1000, cols=5)
                print("✅ Created new MTU Metrics sheet")
            
            return sheet
            
        except Exception as e:
            print(f"❌ Error setting up MTU sheet: {e}")
            return None
    
    def update_mtu_sheet(self, metrics):
        """Update MTU Metrics sheet with calculated data (transposed format)"""
        try:
            sheet = self.setup_mtu_sheet()
            if not sheet:
                return False
            
            # Clear existing data
            sheet.clear()
            
            # Create transposed data structure
            transposed_data = [
                ["Metric", "Value"],  # Headers
                ["Period Start", metrics['period_start']],
                ["Period End", metrics['period_end']],
                ["", ""],  # Separator
                ["UK METRICS", ""],
                ["UK Total Users", str(metrics['UK_total_users'])],
                ["UK Active Users (60d)", str(metrics['UK_active_users'])],
                ["", ""],
                ["UK Push Notifications", ""],
                ["UK Push All Users", str(metrics['UK_push_all_users'])],
                ["UK Push All %", f"{metrics['UK_push_all_percentage']}%"],
                ["UK Push Active Users", str(metrics['UK_push_active_users'])],
                ["UK Push Active %", f"{metrics['UK_push_active_percentage']}%"],
                ["", ""],
                ["UK Email", ""],
                ["UK Email All Users", str(metrics['UK_email_all_users'])],
                ["UK Email All %", f"{metrics['UK_email_all_percentage']}%"],
                ["UK Email Active Users", str(metrics['UK_email_active_users'])],
                ["UK Email Active %", f"{metrics['UK_email_active_percentage']}%"],
                ["", ""],  # Separator
                ["UAE METRICS", ""],
                ["UAE Total Users", str(metrics['UAE_total_users'])],
                ["UAE Active Users (60d)", str(metrics['UAE_active_users'])],
                ["", ""],
                ["UAE Push Notifications", ""],
                ["UAE Push All Users", str(metrics['UAE_push_all_users'])],
                ["UAE Push All %", f"{metrics['UAE_push_all_percentage']}%"],
                ["UAE Push Active Users", str(metrics['UAE_push_active_users'])],
                ["UAE Push Active %", f"{metrics['UAE_push_active_percentage']}%"],
                ["", ""],
                ["UAE Email", ""],
                ["UAE Email All Users", str(metrics['UAE_email_all_users'])],
                ["UAE Email All %", f"{metrics['UAE_email_all_percentage']}%"],
                ["UAE Email Active Users", str(metrics['UAE_email_active_users'])],
                ["UAE Email Active %", f"{metrics['UAE_email_active_percentage']}%"]
            ]
            
            # Add all data at once
            for row in transposed_data:
                sheet.append_row(row)
            
            print(f"✅ Successfully updated MTU Metrics sheet!")
            return True
            
        except Exception as e:
            print(f"❌ Error updating MTU sheet: {e}")
            return False
    
    def run_mtu_automation(self, end_date):
        """Run the complete MTU automation"""
        
        print("🚀 Starting MTU Automation")
        print("=" * 50)
        
        # 1. Get date range
        start_date, end_date_obj = self.get_date_range(end_date)
        if not start_date:
            return False
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date_obj.strftime('%Y-%m-%d')
        
        print(f"📅 Period: {start_date_str} to {end_date_str}")
        
        # 2. Check if webhook data is available
        try:
            conn = sqlite3.connect(self.webhook_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM events")
            event_count = cursor.fetchone()[0]
            conn.close()
            
            if event_count == 0:
                print("❌ No webhook data available. Please ensure:")
                print("   1. Webhook server is running")
                print("   2. MoEngage Stream is configured")
                print("   3. Events are being received")
                return False
            
            print(f"✅ Found {event_count:,} events in webhook database")
            
        except Exception as e:
            print(f"❌ Cannot access webhook database: {e}")
            return False
        
        # 3. Calculate MTU metrics
        metrics = self.calculate_mtu_metrics(start_date_str, end_date_str)
        
        # 4. Display results
        print("\n📊 MTU METRICS SUMMARY")
        print("=" * 40)
        
        for country in ['UK', 'UAE']:
            print(f"\n{country}:")
            print(f"  Total Users: {metrics[f'{country}_total_users']:,}")
            print(f"  Active Users (60d): {metrics[f'{country}_active_users']:,}")
            print(f"  Push (All): {metrics[f'{country}_push_all_percentage']:.2f}%")
            print(f"  Push (Active): {metrics[f'{country}_push_active_percentage']:.2f}%")
            print(f"  Email (All): {metrics[f'{country}_email_all_percentage']:.2f}%")
            print(f"  Email (Active): {metrics[f'{country}_email_active_percentage']:.2f}%")
        
        # 5. Update Google Sheet
        success = self.update_mtu_sheet(metrics)
        
        if success:
            print(f"\n🎉 MTU automation completed successfully!")
            return True
        else:
            print(f"\n⚠️  Metrics calculated but Google Sheets update failed")
            return False

def main():
    print("MTU (Marketing Touch Users) Automation")
    print("=" * 50)
    
    # Configuration
    WORKSPACE_ID = "95PNUHBSYSLLJZ22PEOFMKF2"
    CAMPAIGN_API_KEY = "3XMHJ83D2X4V"
    DATA_CENTER = "01"
    GOOGLE_SHEET_ID = "1A30FfO319eiKW0c6zHj2lwr04WLE0fL6eLteZf4CvHM"
    
    # Get inputs
    end_date = input("End date (YYYY-MM-DD): ").strip()
    
    if not end_date:
        print("❌ End date is required")
        return
    
    # Initialize and run automation
    mtu = MTUAutomation(WORKSPACE_ID, CAMPAIGN_API_KEY, GOOGLE_SHEET_ID, DATA_CENTER)
    
    success = mtu.run_mtu_automation(end_date)
    
    if success:
        print("\n✅ All done! Check the 'MTU Metrics' tab in your Google Sheet.")
    else:
        print("\n❌ MTU automation failed. Please check the errors above.")

if __name__ == "__main__":
    main()