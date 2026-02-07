#!/usr/bin/env python3
"""
Test the Stats API now that it's enabled
"""

import requests
import base64
from datetime import datetime, timedelta

MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'campaign_api_key': '3XMHJ83D2X4V',
    'data_center': '01'
}

# Test with recent dates
end_date = datetime.now() - timedelta(days=1)
start_date = end_date.replace(day=1)

start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

print("=" * 70)
print("TESTING STATS API (NOW ENABLED)")
print("=" * 70)
print()
print(f"Date range: {start_date_str} to {end_date_str}")
print()

# Stats API endpoint
stats_url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaign-stats"

# Authentication
auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
encoded_auth = base64.b64encode(auth_string.encode()).decode()

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {encoded_auth}',
    'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
    'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key']
}

payload = {
    'request_id': f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    'start_date': start_date_str,
    'end_date': end_date_str,
    'attribution_type': 'TOTAL_CONVERSIONS',
    'metric_type': 'TOTAL',
    'offset': 0,
    'limit': 10
}

print("Sending request to Stats API...")
print(f"URL: {stats_url}")
print()

try:
    response = requests.post(stats_url, json=payload, headers=headers, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS! Stats API is working!")
        print()
        print(f"Response keys: {list(data.keys())}")
        print()
        
        if 'data' in data:
            campaigns = data.get('data', [])
            print(f"Total campaigns returned: {len(campaigns)}")
            
            if campaigns:
                print()
                print("Sample campaign data:")
                sample = campaigns[0]
                print(f"  Campaign ID: {sample.get('campaign_id', 'N/A')}")
                print(f"  Campaign Name: {sample.get('campaign_name', 'N/A')}")
                print(f"  Channel: {sample.get('channel', 'N/A')}")
                print(f"  Sent: {sample.get('sent', 'N/A')}")
                print(f"  Delivered: {sample.get('delivered', 'N/A')}")
        
        print()
        print("Full response structure:")
        import json
        print(json.dumps(data, indent=2)[:1000] + "...")
        
    elif response.status_code == 403:
        print("❌ FAILED: Stats API not enabled (403 Forbidden)")
        print(f"Response: {response.text}")
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
