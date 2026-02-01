#!/usr/bin/env python3
"""
MoEngage Google Sheets Automation using Campaign Report API
This approach downloads pre-configured reports instead of using real-time stats API
"""

import requests
import json
import csv
import io
from datetime import datetime, timedelta
from calendar import monthrange
import gspread
from google.oauth2.service_account import Credentials
import hashlib
import hmac
import base64

class MoEngageReportsAutomation:
    def __init__(self, moengage_app_id, campaign_api_key, google_sheet_id, data_center="01"):
        self.moengage_app_id = moengage_app_id
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
    
    def generate_signature(self, filename, secret_key):
        """
        Generate signature for Campaign Report API
        """
        message = f"{self.moengage_app_id}{filename}{secret_key}"
        signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def download_campaign_report(self, filename, secret_key):
        """
        Download a pre-configured campaign report
        
        SETUP REQUIRED:
        1. Go to MoEngage Dashboard → Engage → Campaigns
        2. Click Export → Advanced
        3. Configure your report with email/push campaigns
        4. In "Send report to" section, select "Rest API"
        5. Note the filename and secret key provided
        """
        
        # Generate signature
        signature = self.generate_signature(filename, secret_key)
        
        # API endpoint for downloading reports
        url = f"{self.base_url}/reports/download/{self.moengage_app_id}/{filename}"
        
        # Create auth header
        auth_string = f"{self.moengage_app_id}:{self.campaign_api_key}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_auth}',
        }
        
        params = {
            'signature': signature
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=60)
            response.raise_for_status()
            
            # The response should be a CSV file
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading report: {e}")
            return None
    
    def parse_campaign_report(self, csv_content):
        """
        Parse the downloaded CSV report to extract email and push counts
        """
        if not csv_content:
            return {'email_sent': 0, 'push_sent': 0}
        
        # Parse CSV content
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        email_sent = 0
        push_sent = 0
        
        for row in csv_reader:
            # The exact column names depend on your report configuration
            # Common column names might be:
            campaign_type = row.get('Campaign Type', '').lower()
            sent_count = int(row.get('Sent', 0) or 0)
            
            if 'email' in campaign_type:
                email_sent += sent_count
            elif 'push' in campaign_type or 'notification' in campaign_type:
                push_sent += sent_count
        
        return {
            'email_sent': email_sent,
            'push_sent': push_sent
        }
    
    def get_user_count_estimate(self):
        """
        Get user count estimate
        Since we can't access the segments API, we'll need an alternative approach:
        1. Use a pre-configured user analytics report
        2. Or ask user to provide this number manually
        3. Or use a reasonable estimate based on historical data
        """
        
        # For now, we'll ask the user to provide this
        # In a production setup, you could:
        # - Download a user analytics report
        # - Store historical user counts
        # - Use MoEngage dashboard export
        
        print("\n" + "="*50)
        print("USER COUNT NEEDED")
        print("="*50)
        print("Since we cannot access the Segments API directly,")
        print("please provide your current total user base count.")
        print("You can find this in your MoEngage dashboard under Analytics.")
        print()
        
        while True:
            try:
                user_count = input("Enter total user count: ").strip()
                return int(user_count)
            except ValueError:
                print("Please enter a valid number.")
    
    def calculate_comms_per_user(self, start_date, end_date, report_filename, secret_key):
        """
        Calculate communications received per user metrics using report download
        """
        print(f"Calculating metrics for period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Download and parse campaign report
        print("Downloading campaign report...")
        csv_content = self.download_campaign_report(report_filename, secret_key)
        
        if not csv_content:
            print("Failed to download report. Please check:")
            print("1. Report filename and secret key are correct")
            print("2. Report is configured in MoEngage dashboard")
            print("3. API access is enabled")
            return None
        
        # Parse the report
        campaign_data = self.parse_campaign_report(csv_content)
        
        # Get user count
        total_users = self.get_user_count_estimate()
        
        print(f"Raw data - Emails: {campaign_data['email_sent']}, Push: {campaign_data['push_sent']}, Users: {total_users}")
        
        # Calculate metrics
        email_per_user = campaign_data['email_sent'] / total_users if total_users > 0 else 0
        push_per_user = campaign_data['push_sent'] / total_users if total_users > 0 else 0
        
        return {
            'period_start': start_date.strftime('%Y-%m-%d'),
            'period_end': end_date.strftime('%Y-%m-%d'),
            'email_sent': campaign_data['email_sent'],
            'push_sent': campaign_data['push_sent'],
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
            
            # Prepare row data
            row_data = [
                metrics_data['period_start'],
                metrics_data['period_end'],
                metrics_data['email_per_user'],
                metrics_data['push_per_user'],
                metrics_data['email_sent'],
                metrics_data['push_sent'],
                metrics_data['total_users']
            ]
            
            # Append to next row
            sheet.append_row(row_data)
            
            print(f"Successfully updated Google Sheet with metrics for {metrics_data['period_end']}")
            
        except Exception as e:
            print(f"Error updating Google Sheet: {e}")

def main():
    """
    Main function to run the reports-based automation
    """
    print("MoEngage Reports-Based Automation")
    print("=" * 40)
    print()
    print("SETUP REQUIRED FIRST:")
    print("1. Go to MoEngage Dashboard → Engage → Campaigns")
    print("2. Click Export → Advanced")
    print("3. Configure report with your email/push campaigns")
    print("4. Select 'Rest API' in 'Send report to' section")
    print("5. Note the filename and secret key provided")
    print()
    
    # Configuration
    MOENGAGE_APP_ID = "95PNUHBSYSLLJZ22PEOFMKF2"
    CAMPAIGN_API_KEY = "3XMHJ83D2X4V"
    GOOGLE_SHEET_ID = "your_google_sheet_id"
    DATA_CENTER = "01"
    
    # Get report configuration from user
    report_filename = input("Enter report filename from MoEngage: ").strip()
    secret_key = input("Enter secret key from MoEngage: ").strip()
    
    if not report_filename or not secret_key:
        print("Report filename and secret key are required!")
        return
    
    # Initialize automation
    automation = MoEngageReportsAutomation(MOENGAGE_APP_ID, CAMPAIGN_API_KEY, GOOGLE_SHEET_ID, DATA_CENTER)
    
    # Get user input for end date
    while True:
        end_date_input = input("Enter end date (YYYY-MM-DD, max: yesterday): ").strip()
        
        start_date, end_date = automation.get_date_range(end_date_input)
        if start_date and end_date:
            break
        else:
            print("Invalid date. Please try again.")
    
    # Calculate metrics
    metrics = automation.calculate_comms_per_user(start_date, end_date, report_filename, secret_key)
    
    if metrics:
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