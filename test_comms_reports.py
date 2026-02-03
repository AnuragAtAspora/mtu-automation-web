#!/usr/bin/env python3
"""
Test Communications Per User report download and parsing
"""

import requests
import base64
import hashlib
import zipfile
import csv
import io
from datetime import datetime, timedelta

# Configuration
MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'campaign_api_key': '3XMHJ83D2X4V',
    'data_center': '01'
}

def download_report(report_filename, start_date=None, end_date=None):
    """Download campaign report from MoEngage with date parameters"""
    
    # Generate signature: App_ID|FILENAME|SECRET_KEY
    signature_key = f"{MOENGAGE_CONFIG['workspace_id']}|{report_filename}|{MOENGAGE_CONFIG['campaign_api_key']}"
    signature = hashlib.sha256(signature_key.encode('utf-8')).hexdigest()
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/campaign_reports/rest_api/{MOENGAGE_CONFIG['workspace_id']}/{report_filename}"
    
    # Headers
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Signature': signature
    }
    
    # Add date parameters if provided
    params = {}
    if start_date and end_date:
        params['start_date'] = start_date
        params['end_date'] = end_date
    
    try:
        print(f"📥 Testing report: {report_filename}")
        if params:
            print(f"📅 Date range: {start_date} to {end_date}")
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"✅ Report downloaded successfully")
            print(f"Content Length: {len(response.content)} bytes")
            return response.content
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response Text: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        return None

def parse_report(zip_content, report_type):
    """Parse report and extract communication counts by country"""
    
    if not zip_content:
        print("❌ No report data available")
        return None
    
    try:
        # Extract ZIP content
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
            print(f"📁 ZIP contents: {zip_file.namelist()}")
            
            csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
            
            if not csv_files:
                print("❌ No CSV files found in report")
                return None
            
            # Read the first CSV file
            csv_filename = csv_files[0]
            with zip_file.open(csv_filename) as csv_file:
                csv_content = csv_file.read().decode('utf-8')
            
            print(f"📊 Parsing CSV: {csv_filename}")
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            # Print headers
            fieldnames = csv_reader.fieldnames
            print(f"📋 CSV Headers: {fieldnames}")
            
            uk_total = 0
            uae_total = 0
            total_rows = 0
            
            for row in csv_reader:
                total_rows += 1
                campaign_name = row.get('Campaign Name', '').lower()
                
                # Print first few rows for debugging
                if total_rows <= 3:
                    print(f"Row {total_rows}: Campaign Name = '{campaign_name}'")
                    for key, value in row.items():
                        if 'sent' in key.lower() or 'platform' in key.lower():
                            print(f"  {key}: {value}")
                
                # Determine sent count based on report type
                if 'pn' in report_type.lower():
                    sent_count = int(row.get('All Platform Sent', 0) or 0)
                else:  # Email
                    sent_count = int(row.get('Sent', 0) or 0)
                
                # Filter by country
                if 'uk' in campaign_name:
                    uk_total += sent_count
                elif 'uae' in campaign_name:
                    uae_total += sent_count
            
            print(f"📈 Results for {report_type}:")
            print(f"  UK Total: {uk_total:,}")
            print(f"  UAE Total: {uae_total:,}")
            print(f"  Total Rows: {total_rows}")
            
            return {
                'uk_total': uk_total,
                'uae_total': uae_total,
                'csv_filename': csv_filename,
                'total_rows': total_rows
            }
            
    except Exception as e:
        print(f"❌ Error parsing report: {str(e)}")
        return None

def main():
    print("🧪 Testing Communications Per User Reports")
    print("=" * 50)
    
    # Test date range (January 2026)
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    # Static report filenames (as configured in MoEngage)
    reports = {
        'transactional_pn': "API_TX_PN_20260202",
        'transactional_email': "API_TX_Email_20260202", 
        'promotional_pn': "API_PR_PN_20260202",
        'promotional_email': "API_PR_Email_20260202"
    }
    
    # Test each report
    for report_type, filename in reports.items():
        print(f"\n🔍 Testing {report_type} ({filename})")
        print("-" * 40)
        
        # Test without date parameters first
        print("Testing without date parameters:")
        zip_content = download_report(filename)
        
        if zip_content:
            result = parse_report(zip_content, report_type)
            if result:
                print(f"✅ Successfully parsed {report_type}")
            else:
                print(f"❌ Failed to parse {report_type}")
        else:
            print(f"❌ Failed to download {report_type}")
        
        print("\nTesting with date parameters:")
        zip_content_with_dates = download_report(filename, start_date, end_date)
        
        if zip_content_with_dates:
            result_with_dates = parse_report(zip_content_with_dates, report_type)
            if result_with_dates:
                print(f"✅ Successfully parsed {report_type} with dates")
            else:
                print(f"❌ Failed to parse {report_type} with dates")
        else:
            print(f"❌ Failed to download {report_type} with dates")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    main()