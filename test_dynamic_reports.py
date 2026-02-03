#!/usr/bin/env python3
"""
Test different approaches for dynamic date ranges in MoEngage Reports
"""

import requests
import base64
import hashlib
import json
from datetime import datetime, timedelta

# Configuration
MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'campaign_api_key': '3XMHJ83D2X4V',
    'data_center': '01'
}

def test_post_request_with_dates():
    """Test POST request with date parameters in body"""
    
    report_filename = "API_TX_PN_20260202"
    
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
        'Signature': signature,
        'Content-Type': 'application/json'
    }
    
    # Try POST with date parameters in body
    payload = {
        'start_date': '2026-01-01',
        'end_date': '2026-01-31'
    }
    
    print("🧪 Testing POST request with date parameters in body")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"✅ POST request successful - Content Length: {len(response.content)}")
            return True
        else:
            print(f"❌ POST failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_stats_api():
    """Test Stats API for real-time campaign data"""
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v1/campaigns/stats"
    
    # Headers for Data API
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Content-Type': 'application/json'
    }
    
    # Try to get campaign stats with date range
    payload = {
        'start_date': '2026-01-01',
        'end_date': '2026-01-31',
        'campaign_type': 'push'
    }
    
    print("\n🧪 Testing Stats API for campaign data")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats API successful")
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            return data
        else:
            print(f"❌ Stats API failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_data_export_api():
    """Test Data Export API for event-level data"""
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v1/export/events"
    
    # Headers for Data API
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Content-Type': 'application/json'
    }
    
    # Try to export push/email events with date range
    payload = {
        'start_date': '2026-01-01T00:00:00.000Z',
        'end_date': '2026-01-31T23:59:59.999Z',
        'event_names': ['MOE_PUSH_SENT', 'MOE_EMAIL_SENT'],
        'format': 'json'
    }
    
    print("\n🧪 Testing Data Export API for event data")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Data Export API successful")
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            return data
        else:
            print(f"❌ Data Export API failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def main():
    print("🔍 TESTING ALTERNATIVE APPROACHES FOR DYNAMIC DATE RANGES")
    print("=" * 60)
    
    # Test 1: POST request with dates in body
    test_post_request_with_dates()
    
    # Test 2: Stats API
    test_stats_api()
    
    # Test 3: Data Export API
    test_data_export_api()
    
    print("\n" + "=" * 60)
    print("📊 CONCLUSION:")
    print("If all tests fail, we may need to:")
    print("1. Create new reports in MoEngage dashboard with dynamic date ranges")
    print("2. Use a different API endpoint")
    print("3. Contact MoEngage support for proper date filtering method")

if __name__ == "__main__":
    main()