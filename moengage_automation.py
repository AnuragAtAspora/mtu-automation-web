#!/usr/bin/env python3
"""
MoEngage Google Sheets Automation
Automates fetching business metrics from MoEngage and updating Google Sheets
"""

import requests
import json
from datetime import datetime, timedelta
from calendar import monthrange
import gspread
from google.oauth2.service_account import Credentials

class MoEngageAutomation:
    def __init__(self, moengage_app_id, data_api_key, campaign_api_key, google_sheet_id, data_center="01"):
        self.moengage_app_id = moengage_app_id
        self.data_api_key = data_api_key
        self.campaign_api_key = campaign_api_key
        self.google_sheet_id = google_sheet_id
        self.data_center = data_center
        self.base_url = f"https://api-{data_center}.moengage.com/v1"
        
    def get_date_range(self, end_date_str):
        """
        Get date range from month beginning to selected date
        end_date_str: format 'YYYY-MM-DD'
        Returns: (start_date, end_date) as datetime objects
        """
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
            # Validate end_date is not today or future
            yesterday = datetime.now() - timedelta(days=1)
            if end_date > yesterday:
                raise ValueError(f"End date cannot exceed {yesterday.strftime('%Y-%m-%d')}")
            
            # Get month beginning
            start_date = end_date.replace(day=1)
            
            return start_date, end_date
            
        except ValueError as e:
            print(f"Date validation error: {e}")
            return None, None
    
    def _get_auth_headers(self, api_type="campaign"):
        """
        Generate authentication headers for MoEngage API
        api_type: "campaign" for stats API, "data" for segments API
        """
        import base64
        
        if api_type == "campaign":
            api_key = self.campaign_api_key
        else:
            api_key = self.data_api_key
            
        auth_string = f"{self.moengage_app_id}:{api_key}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        return {
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/json',
            'MOE-APPKEY': self.moengage_app_id
        }
    
    def get_email_sent_count(self, start_date, end_date):
        """
        Fetch total emails sent in the given period from MoEngage Stats API
        """
        url = f"{self.base_url}/campaigns/stats"
        headers = self._get_auth_headers("campaign")
        
        payload = {
            'request_id': f'email_stats_{int(datetime.now().timestamp())}',
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'attribution_type': 'TOTAL_CONVERSIONS',
            'metric_type': 'TOTAL'
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Sum up email sent counts from all campaigns
            total_emails = 0
            if 'data' in data:
                for campaign_data in data['data']:
                    # Look for email platform data
                    if 'platforms' in campaign_data:
                        for platform, stats in campaign_data['platforms'].items():
                            if platform == 'EMAIL':
                                total_emails += stats.get('sent', 0)
            
            return total_emails
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching email data: {e}")
            return 0
    
    def get_push_notification_sent_count(self, start_date, end_date):
        """
        Fetch total push notifications sent in the given period from MoEngage Stats API
        """
        url = f"{self.base_url}/campaigns/stats"
        headers = self._get_auth_headers("campaign")
        
        payload = {
            'request_id': f'push_stats_{int(datetime.now().timestamp())}',
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'attribution_type': 'TOTAL_CONVERSIONS',
            'metric_type': 'TOTAL'
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Sum up push notification sent counts from all campaigns
            total_push = 0
            if 'data' in data:
                for campaign_data in data['data']:
                    # Look for push platform data (ANDROID, IOS, WEB, MWEB)
                    if 'platforms' in campaign_data:
                        for platform, stats in campaign_data['platforms'].items():
                            if platform in ['ANDROID', 'IOS', 'WEB', 'MWEB']:
                                total_push += stats.get('sent', 0)
            
            return total_push
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching push notification data: {e}")
            return 0
    
    def get_total_user_base(self, as_of_date):
        """
        Fetch total user base as of the specified date using Custom Segment API
        Creates a segment with no filters to get all users
        """
        url = f"{self.base_url}/segments"
        headers = self._get_auth_headers("data")
        
        # Create a segment with no filters to include all users
        segment_name = f"all_users_temp_{int(datetime.now().timestamp())}"
        
        payload = {
            "name": segment_name,
            "description": f"Temporary segment to get user count as of {as_of_date.strftime('%Y-%m-%d')}",
            "included_filters": {
                "filter_operator": "and",
                "filters": [
                    {
                        "filter_type": "user_attributes",
                        "name": "created_time",
                        "data_type": "date",
                        "operator": "lte",
                        "value": as_of_date.strftime('%Y-%m-%d'),
                        "negate": False
                    }
                ]
            }
        }
        
        try:
            # Create the segment
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            segment_id = data.get('data', {}).get('id')
            
            if not segment_id:
                print("Failed to create segment for user count")
                return 0
            
            # Get segment details which should include user count
            # Note: You might need to wait a moment for segment to be processed
            import time
            time.sleep(2)  # Wait for segment processing
            
            get_url = f"{self.base_url}/segments/{segment_id}"
            get_response = requests.get(get_url, headers=headers)
            get_response.raise_for_status()
            
            segment_data = get_response.json()
            user_count = segment_data.get('data', {}).get('user_count', 0)
            
            # Clean up: Delete the temporary segment
            delete_url = f"{self.base_url}/segments/{segment_id}"
            requests.delete(delete_url, headers=headers)
            
            return user_count
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user base data: {e}")
            return 0
    
    def calculate_comms_per_user(self, start_date, end_date):
        """
        Calculate communications received per user metrics
        Returns: dict with email and PN metrics
        """
        print(f"Calculating metrics for period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Fetch data from MoEngage
        email_sent = self.get_email_sent_count(start_date, end_date)
        push_sent = self.get_push_notification_sent_count(start_date, end_date)
        total_users = self.get_total_user_base(end_date)
        
        print(f"Raw data - Emails: {email_sent}, Push: {push_sent}, Users: {total_users}")
        
        # Calculate metrics
        email_per_user = email_sent / total_users if total_users > 0 else 0
        push_per_user = push_sent / total_users if total_users > 0 else 0
        
        return {
            'period_start': start_date.strftime('%Y-%m-%d'),
            'period_end': end_date.strftime('%Y-%m-%d'),
            'email_sent': email_sent,
            'push_sent': push_sent,
            'total_users': total_users,
            'email_per_user': round(email_per_user, 4),
            'push_per_user': round(push_per_user, 4)
        }
    
    def update_google_sheet(self, metrics_data, sheet_name="Metrics"):
        """
        Update Google Sheet with calculated metrics
        """
        try:
            # Setup Google Sheets connection
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            # You'll need to create service account credentials
            creds = Credentials.from_service_account_file('google_credentials.json', scopes=scope)
            client = gspread.authorize(creds)
            
            # Open the sheet
            sheet = client.open_by_key(self.google_sheet_id).worksheet(sheet_name)
            
            # Find next empty row or update existing row for this period
            # This is a basic implementation - you can customize based on your sheet structure
            row_data = [
                metrics_data['period_start'],
                metrics_data['period_end'],
                metrics_data['email_per_user'],
                metrics_data['push_per_user'],
                metrics_data['email_sent'],
                metrics_data['push_sent'],
                metrics_data['total_users']
            ]
            
            # Append to next row (you can modify this logic based on your needs)
            sheet.append_row(row_data)
            
            print(f"Successfully updated Google Sheet with metrics for {metrics_data['period_end']}")
            
        except Exception as e:
            print(f"Error updating Google Sheet: {e}")

def main():
    """
    Main function to run the automation
    """
    # Configuration - you'll need to set these values
    MOENGAGE_APP_ID = "95PNUHBSYSLLJZ22PEOFMKF2"
    DATA_API_KEY = "Mj5JSGKcwYum9NKAGmGHJG_E"
    CAMPAIGN_API_KEY = "3XMHJ83D2X4V"
    GOOGLE_SHEET_ID = "your_google_sheet_id"
    DATA_CENTER = "01"
    
    # Initialize automation
    automation = MoEngageAutomation(MOENGAGE_APP_ID, DATA_API_KEY, CAMPAIGN_API_KEY, GOOGLE_SHEET_ID, DATA_CENTER)
    
    # Get user input for end date
    print("MoEngage Metrics Automation")
    print("=" * 30)
    
    while True:
        end_date_input = input("Enter end date (YYYY-MM-DD, max: yesterday): ").strip()
        
        start_date, end_date = automation.get_date_range(end_date_input)
        if start_date and end_date:
            break
        else:
            print("Invalid date. Please try again.")
    
    # Calculate metrics
    metrics = automation.calculate_comms_per_user(start_date, end_date)
    
    # Display results
    print("\nCalculated Metrics:")
    print(f"Period: {metrics['period_start']} to {metrics['period_end']}")
    print(f"Email per user: {metrics['email_per_user']}")
    print(f"Push notifications per user: {metrics['push_per_user']}")
    print(f"Total emails sent: {metrics['email_sent']}")
    print(f"Total push notifications sent: {metrics['push_sent']}")
    print(f"Total user base: {metrics['total_users']}")
    
    # Update Google Sheet
    update_sheet = input("\nUpdate Google Sheet? (y/n): ").strip().lower()
    if update_sheet == 'y':
        automation.update_google_sheet(metrics)

if __name__ == "__main__":
    main()