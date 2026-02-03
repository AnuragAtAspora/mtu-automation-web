#!/usr/bin/env python3
"""
Debug date filtering in MoEngage Reports API
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

def download_and_analyze_report(report_filename, start_date=None, end_date=None, test_name=""):
    """Download report and analyze the actual date range of data"""
    
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
    
    # Add date parameters if provided
    params = {}
    if start_date and end_date:
        params['start_date'] = start_date
        params['end_date'] = end_date
    
    print(f"\n🔍 {test_name}")
    print(f"Report: {report_filename}")
    if params:
        print(f"Date params: {params}")
    else:
        print("No date params")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            # Parse the report
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                
                if csv_files:
                    csv_filename = csv_files[0]
                    with zip_file.open(csv_filename) as csv_file:
                        csv_content = csv_file.read().decode('utf-8')
                    
                    # Parse CSV and analyze
                    csv_reader = csv.DictReader(io.StringIO(csv_content))
                    
                    uk_total = 0
                    uae_total = 0
                    total_rows = 0
                    sample_campaigns = []
                    
                    for row in csv_reader:
                        total_rows += 1
                        campaign_name = row.get('Campaign Name', '').lower()
                        
                        # Store first 5 campaigns for analysis
                        if total_rows <= 5:
                            sample_campaigns.append({
                                'name': campaign_name,
                                'sent': row.get('All Platform Sent', row.get('Sent', 0))
                            })
                        
                        # Count by country
                        if 'pn' in report_filename.lower():
                            sent_count = int(row.get('All Platform Sent', 0) or 0)
                        else:  # Email
                            sent_count = int(row.get('Sent', 0) or 0)
                        
                        if 'uk' in campaign_name:
                            uk_total += sent_count
                        elif 'uae' in campaign_name:
                            uae_total += sent_count
                    
                    print(f"✅ Downloaded successfully")
                    print(f"Total rows: {total_rows}")
                    print(f"UK total: {uk_total:,}")
                    print(f"UAE total: {uae_total:,}")
                    print(f"Sample campaigns:")
                    for camp in sample_campaigns:
                        print(f"  - {camp['name']}: {camp['sent']}")
                    
                    return {
                        'uk_total': uk_total,
                        'uae_total': uae_total,
                        'total_rows': total_rows,
                        'sample_campaigns': sample_campaigns
                    }
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def main():
    print("🔍 DEBUGGING DATE FILTERING IN MOENGAGE REPORTS API")
    print("=" * 60)
    
    # Test with UK Transactional PN report
    report_filename = "API_TX_PN_20260202"
    
    # Test 1: No date parameters
    result1 = download_and_analyze_report(
        report_filename, 
        test_name="TEST 1: No date parameters"
    )
    
    # Test 2: January 2026 date range
    result2 = download_and_analyze_report(
        report_filename, 
        start_date="2026-01-01", 
        end_date="2026-01-31",
        test_name="TEST 2: January 2026 (2026-01-01 to 2026-01-31)"
    )
    
    # Test 3: Different date format
    result3 = download_and_analyze_report(
        report_filename, 
        start_date="01-01-2026", 
        end_date="31-01-2026",
        test_name="TEST 3: Different date format (DD-MM-YYYY)"
    )
    
    # Test 4: Very narrow date range
    result4 = download_and_analyze_report(
        report_filename, 
        start_date="2026-01-15", 
        end_date="2026-01-16",
        test_name="TEST 4: Narrow range (2026-01-15 to 2026-01-16)"
    )
    
    print("\n" + "=" * 60)
    print("📊 ANALYSIS:")
    
    if result1 and result2:
        if result1['uk_total'] == result2['uk_total']:
            print("❌ Date parameters have NO EFFECT - same results")
            print(f"   Both returned UK total: {result1['uk_total']:,}")
        else:
            print("✅ Date parameters ARE WORKING - different results")
            print(f"   No params: {result1['uk_total']:,}")
            print(f"   With params: {result2['uk_total']:,}")
    
    print(f"\n🎯 YOUR EXPECTED VALUE: 101,404")
    if result1:
        print(f"🤖 SYSTEM CURRENT VALUE: {result1['uk_total']:,}")
        difference = abs(101404 - result1['uk_total'])
        print(f"📊 DIFFERENCE: {difference:,}")
        
        if difference > 1000:
            print("⚠️  SIGNIFICANT DIFFERENCE - Investigation needed")
        else:
            print("✅ MINOR DIFFERENCE - Likely acceptable")

if __name__ == "__main__":
    main()