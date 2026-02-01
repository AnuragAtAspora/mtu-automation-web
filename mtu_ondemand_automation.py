#!/usr/bin/env python3
"""
MTU On-Demand Automation
Calculates MTU metrics using MoEngage APIs when requested (no background webhook)
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
import json

class MTUOnDemandAutomation:
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
    
    def create_segment_for_country(self, country_code, segment_name):
        """Create a segment for users in specific country"""
        try:
            url = f"https://api-{self.data_center}.moengage.com/core-services/v1/custom-segments"
            
            # Auth
            auth_string = f"{self.workspace_id}:{self.campaign_api_key}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_auth}',
                'Content-Type': 'application/json',
                'MOE-APPKEY': self.workspace_id
            }
            
            # Create segment payload for country filter
            payload = {
                "name": segment_name,
                "description": f"Users in {country_code} for MTU calculation",
                "included_filters": {
                    "filter_operator": "and",
                    "filters": [
                        {
                            "filter_type": "user_attributes",
                            "name": "country",  # Assuming country attribute exists
                            "data_type": "string",
                            "operator": "in",
                            "value": [country_code],
                            "negate": False,
                            "case_sensitive": False
                        }
                    ]
                }
            }
            
            print(f"🔍 Creating segment for {country_code} users...")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                segment_id = data['data']['id']
                print(f"✅ Created segment: {segment_id}")
                return segment_id
            else:
                print(f"❌ Error creating segment: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating segment: {e}")
            return None
    
    def create_segment_for_comms_received(self, country_code, channel, start_date, end_date, segment_name):
        """Create segment for users who received communications in period"""
        try:
            url = f"https://api-{self.data_center}.moengage.com/core-services/v1/custom-segments"
            
            # Auth
            auth_string = f"{self.workspace_id}:{self.campaign_api_key}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_auth}',
                'Content-Type': 'application/json',
                'MOE-APPKEY': self.workspace_id
            }
            
            # Determine event name based on channel
            event_name = "MOE_EMAIL_SENT" if channel == "email" else "MOE_PUSH_SENT"
            
            # Create segment payload
            payload = {
                "name": segment_name,
                "description": f"{country_code} users who received {channel} from {start_date} to {end_date}",
                "included_filters": {
                    "filter_operator": "and",
                    "filters": [
                        {
                            "filter_type": "user_attributes",
                            "name": "country",
                            "data_type": "string",
                            "operator": "in",
                            "value": [country_code],
                            "negate": False,
                            "case_sensitive": False
                        },
                        {
                            "filter_type": "actions",
                            "attributes": {
                                "filter_operator": "and",
                                "filters": []
                            },
                            "executed": True,
                            "primary_time_range": {
                                "type": "between",
                                "value": f"{start_date}T00:00:00.000Z",
                                "value1": f"{end_date}T23:59:59.999Z",
                                "value_type": "absolute",
                                "period_unit": "days"
                            },
                            "action_name": event_name,
                            "execution": {
                                "count": 1,
                                "type": "atleast"
                            }
                        }
                    ]
                }
            }
            
            print(f"🔍 Creating segment for {country_code} {channel} users...")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                segment_id = data['data']['id']
                print(f"✅ Created {channel} segment: {segment_id}")
                return segment_id
            else:
                print(f"❌ Error creating {channel} segment: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating {channel} segment: {e}")
            return None
    
    def create_segment_for_active_users(self, country_code, days, segment_name):
        """Create segment for users who transacted in last N days"""
        try:
            url = f"https://api-{self.data_center}.moengage.com/core-services/v1/custom-segments"
            
            # Auth
            auth_string = f"{self.workspace_id}:{self.campaign_api_key}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_auth}',
                'Content-Type': 'application/json',
                'MOE-APPKEY': self.workspace_id
            }
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            payload = {
                "name": segment_name,
                "description": f"{country_code} users who transacted in last {days} days",
                "included_filters": {
                    "filter_operator": "and",
                    "filters": [
                        {
                            "filter_type": "user_attributes",
                            "name": "country",
                            "data_type": "string",
                            "operator": "in",
                            "value": [country_code],
                            "negate": False,
                            "case_sensitive": False
                        },
                        {
                            "filter_type": "actions",
                            "attributes": {
                                "filter_operator": "and",
                                "filters": []
                            },
                            "executed": True,
                            "primary_time_range": {
                                "type": "between",
                                "value": start_date.strftime('%Y-%m-%dT00:00:00.000Z'),
                                "value1": end_date.strftime('%Y-%m-%dT23:59:59.999Z'),
                                "value_type": "absolute",
                                "period_unit": "days"
                            },
                            "action_name": "transaction",  # Adjust based on your transaction event name
                            "execution": {
                                "count": 1,
                                "type": "atleast"
                            }
                        }
                    ]
                }
            }
            
            print(f"🔍 Creating active users segment for {country_code}...")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                segment_id = data['data']['id']
                print(f"✅ Created active users segment: {segment_id}")
                return segment_id
            else:
                print(f"❌ Error creating active users segment: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating active users segment: {e}")
            return None
    
    def get_segment_count_estimate(self, segment_id):
        """
        Get estimated count for a segment
        Note: MoEngage doesn't provide direct segment count API, 
        so this is a placeholder for manual input or estimation
        """
        print(f"⚠️  MoEngage doesn't provide direct segment count API")
        print(f"   Please check segment {segment_id} in MoEngage dashboard for user count")
        
        # For now, ask user to input the count manually
        try:
            count = int(input(f"Enter user count for segment {segment_id}: "))
            return count
        except ValueError:
            print("Invalid input, using 0")
            return 0
    
    def calculate_mtu_metrics_ondemand(self, start_date, end_date):
        """Calculate MTU metrics using on-demand API calls"""
        
        print(f"🔍 Calculating MTU metrics for {start_date} to {end_date}")
        print("📝 Creating segments for user counting...")
        
        metrics = {
            'period_start': start_date,
            'period_end': end_date
        }
        
        countries = {'UK': 'GB', 'UAE': 'AE'}
        channels = ['push', 'email']
        
        for country_name, country_code in countries.items():
            print(f"\n📊 Processing {country_name} ({country_code})...")
            
            # Create base country segment
            total_segment_id = self.create_segment_for_country(
                country_code, 
                f"MTU_{country_code}_Total_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if total_segment_id:
                total_users = self.get_segment_count_estimate(total_segment_id)
                print(f"   Total users: {total_users:,}")
            else:
                total_users = 0
            
            # Create active users segment (60 days)
            active_segment_id = self.create_segment_for_active_users(
                country_code, 
                60,
                f"MTU_{country_code}_Active60d_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if active_segment_id:
                active_users = self.get_segment_count_estimate(active_segment_id)
                print(f"   Active users (60d): {active_users:,}")
            else:
                active_users = 0
            
            for channel in channels:
                # Segment for users who received comms (all users)
                comms_segment_id = self.create_segment_for_comms_received(
                    country_code, 
                    channel, 
                    start_date, 
                    end_date,
                    f"MTU_{country_code}_{channel}_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                
                if comms_segment_id:
                    users_received_all = self.get_segment_count_estimate(comms_segment_id)
                    percentage_all = (users_received_all / total_users * 100) if total_users > 0 else 0
                    print(f"   {channel.title()} users (all): {users_received_all:,} ({percentage_all:.2f}%)")
                else:
                    users_received_all = 0
                    percentage_all = 0
                
                # For active users, we'd need a more complex segment combining active + comms
                # For now, use a simplified approach
                users_received_active = int(users_received_all * (active_users / total_users)) if total_users > 0 else 0
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
        """Run the complete MTU automation on-demand"""
        
        print("🚀 Starting MTU On-Demand Automation")
        print("=" * 50)
        
        # 1. Get date range
        start_date, end_date_obj = self.get_date_range(end_date)
        if not start_date:
            return False
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date_obj.strftime('%Y-%m-%d')
        
        print(f"📅 Period: {start_date_str} to {end_date_str}")
        
        # 2. Calculate MTU metrics using API calls
        metrics = self.calculate_mtu_metrics_ondemand(start_date_str, end_date_str)
        
        # 3. Display results
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
        
        # 4. Update Google Sheet
        success = self.update_mtu_sheet(metrics)
        
        if success:
            print(f"\n🎉 MTU automation completed successfully!")
            return True
        else:
            print(f"\n⚠️  Metrics calculated but Google Sheets update failed")
            return False

def main():
    print("MTU On-Demand Automation")
    print("=" * 30)
    
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
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("   - This will create temporary segments in your MoEngage account")
    print("   - You'll need to manually enter segment counts from MoEngage dashboard")
    print("   - Segments will be named with MTU_ prefix and timestamp")
    
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Initialize and run automation
    mtu = MTUOnDemandAutomation(WORKSPACE_ID, CAMPAIGN_API_KEY, GOOGLE_SHEET_ID, DATA_CENTER)
    
    success = mtu.run_mtu_automation(end_date)
    
    if success:
        print("\n✅ All done! Check the 'MTU Metrics' tab in your Google Sheet.")
        print("💡 Remember to clean up temporary segments in MoEngage dashboard if needed.")
    else:
        print("\n❌ MTU automation failed. Please check the errors above.")

if __name__ == "__main__":
    main()