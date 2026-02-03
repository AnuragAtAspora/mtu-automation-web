#!/usr/bin/env python3
"""
Analyze the actual date periods covered by existing MoEngage reports
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

def analyze_report_date_range(report_filename):
    """Download report and analyze what date range it actually covers"""
    
    # Generate signature
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
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Parse the report to find date clues
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                
                if csv_files:
                    csv_filename = csv_files[0]
                    with zip_file.open(csv_filename) as csv_file:
                        csv_content = csv_file.read().decode('utf-8')
                    
                    # Parse CSV and look for date patterns
                    csv_reader = csv.DictReader(io.StringIO(csv_content))
                    
                    print(f"\n📊 ANALYZING: {report_filename}")
                    print(f"CSV File: {csv_filename}")
                    print(f"Headers: {csv_reader.fieldnames}")
                    
                    # Look for date-related fields
                    date_fields = [field for field in csv_reader.fieldnames if 'date' in field.lower() or 'time' in field.lower()]
                    if date_fields:
                        print(f"Date fields found: {date_fields}")
                    
                    # Analyze campaign data
                    uk_total = 0
                    uae_total = 0
                    total_rows = 0
                    campaign_samples = []
                    
                    for row in csv_reader:
                        total_rows += 1
                        campaign_name = row.get('Campaign Name', '').lower()
                        
                        # Store sample campaigns
                        if total_rows <= 10:
                            campaign_samples.append({
                                'name': campaign_name,
                                'sent': row.get('All Platform Sent', row.get('Sent', 0))
                            })
                        
                        # Count totals
                        if 'pn' in report_filename.lower():
                            sent_count = int(row.get('All Platform Sent', 0) or 0)
                        else:  # Email
                            sent_count = int(row.get('Sent', 0) or 0)
                        
                        if 'uk' in campaign_name:
                            uk_total += sent_count
                        elif 'uae' in campaign_name:
                            uae_total += sent_count
                    
                    print(f"Total campaigns: {total_rows}")
                    print(f"UK total communications: {uk_total:,}")
                    print(f"UAE total communications: {uae_total:,}")
                    
                    print(f"\nSample campaigns (first 10):")
                    for camp in campaign_samples:
                        print(f"  - {camp['name']}: {camp['sent']}")
                    
                    # Try to infer date range from campaign names or patterns
                    print(f"\n🔍 INFERRING DATE RANGE:")
                    
                    # Look for date patterns in campaign names
                    date_patterns = []
                    for camp in campaign_samples:
                        name = camp['name']
                        # Look for common date patterns
                        if '2026' in name or '2025' in name:
                            date_patterns.append(name)
                        if 'jan' in name or 'feb' in name or 'dec' in name:
                            date_patterns.append(name)
                    
                    if date_patterns:
                        print(f"Date patterns in campaign names: {date_patterns}")
                    else:
                        print("No obvious date patterns in campaign names")
                    
                    # Check filename for date clues
                    filename_date = report_filename.split('_')[-1]  # 20260202
                    if len(filename_date) == 8 and filename_date.isdigit():
                        year = filename_date[:4]
                        month = filename_date[4:6]
                        day = filename_date[6:8]
                        print(f"Report filename suggests date: {year}-{month}-{day}")
                        print(f"This is likely the REPORT GENERATION date, not the data period")
                    
                    return {
                        'uk_total': uk_total,
                        'uae_total': uae_total,
                        'total_rows': total_rows,
                        'csv_filename': csv_filename
                    }
        else:
            print(f"❌ Error downloading {report_filename}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception analyzing {report_filename}: {str(e)}")
        return None

def main():
    print("🔍 ANALYZING ACTUAL DATE RANGES OF MOENGAGE REPORTS")
    print("=" * 60)
    
    # Analyze all 4 reports
    reports = {
        'Transactional PN': "API_TX_PN_20260202",
        'Transactional Email': "API_TX_Email_20260202", 
        'Promotional PN': "API_PR_PN_20260202",
        'Promotional Email': "API_PR_Email_20260202"
    }
    
    results = {}
    
    for report_type, filename in reports.items():
        result = analyze_report_date_range(filename)
        if result:
            results[report_type] = result
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY OF ALL REPORTS:")
    
    for report_type, data in results.items():
        print(f"\n{report_type}:")
        print(f"  UK Total: {data['uk_total']:,}")
        print(f"  UAE Total: {data['uae_total']:,}")
        print(f"  Total Campaigns: {data['total_rows']}")
    
    print(f"\n🎯 YOUR EXPECTED UK TRANSACTIONAL PN: 101,404")
    if 'Transactional PN' in results:
        actual = results['Transactional PN']['uk_total']
        print(f"🤖 SYSTEM ACTUAL UK TRANSACTIONAL PN: {actual:,}")
        print(f"📊 DIFFERENCE: {abs(101404 - actual):,}")
    
    print(f"\n💡 CONCLUSION:")
    print(f"The reports appear to have FIXED date ranges that cannot be changed via API.")
    print(f"To get accurate data for your desired period, you may need to:")
    print(f"1. Create new reports in MoEngage dashboard with correct date ranges")
    print(f"2. Use the current reports but document their actual coverage period")
    print(f"3. Contact MoEngage support for dynamic date filtering options")

if __name__ == "__main__":
    main()