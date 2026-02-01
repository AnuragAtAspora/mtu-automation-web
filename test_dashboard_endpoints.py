#!/usr/bin/env python3
"""
Test MoEngage dashboard endpoints with correct API keys
"""

import requests
import base64
from datetime import datetime, timedelta
from config import MOENGAGE_APP_ID, DATA_API_KEY, CAMPAIGN_API_KEY, DATA_CENTER

def test_dashboard_stats_api():
    """Test Campaign Stats API on dashboard domain"""
    
    auth_string = f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': MOENGAGE_APP_ID
    }
    
    # Test with a recent 7-day period
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=7)
    
    url = f"https://dashboard-{DATA_CENTER}.moengage.com/v1/campaigns/stats"
    
    payload = {
        'request_id': f'test_{int(datetime.now().timestamp())}',
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'attribution_type': 'TOTAL_CONVERSIONS',
        'metric_type': 'TOTAL'
    }
    
    print("Testing Dashboard Campaign Stats API...")
    print(f"URL: {url}")
    print(f"API Key: {CAMPAIGN_API_KEY}")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard Campaign Stats API working!")
            print(f"Response keys: {list(data.keys())}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def test_dashboard_segments_api():
    """Test Custom Segments API on dashboard domain"""
    
    auth_string = f"{MOENGAGE_APP_ID}:{DATA_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': MOENGAGE_APP_ID
    }
    
    url = f"https://dashboard-{DATA_CENTER}.moengage.com/v1/segments"
    
    # Create a simple test segment
    test_segment_name = f"test_segment_{int(datetime.now().timestamp())}"
    
    payload = {
        "name": test_segment_name,
        "description": "Test segment for API validation",
        "included_filters": {
            "filter_operator": "and",
            "filters": []  # No filters = all users
        }
    }
    
    print("\nTesting Dashboard Custom Segments API...")
    print(f"URL: {url}")
    print(f"API Key: {DATA_API_KEY}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard Segments API working!")
            
            segment_id = data.get('data', {}).get('id')
            if segment_id:
                print(f"Created test segment: {segment_id}")
                
                # Clean up: delete test segment
                delete_url = f"{url}/{segment_id}"
                delete_response = requests.delete(delete_url, headers=headers, timeout=30)
                if delete_response.status_code == 200:
                    print("✅ Test segment cleaned up")
                
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    print("MoEngage Dashboard API Test")
    print("=" * 40)
    print(f"Workspace ID: {MOENGAGE_APP_ID}")
    print(f"Data Center: {DATA_CENTER}")
    print()
    
    # Test both APIs on dashboard domain
    stats_ok = test_dashboard_stats_api()
    segments_ok = test_dashboard_segments_api()
    
    print("\n" + "=" * 40)
    if stats_ok and segments_ok:
        print("🎉 Dashboard APIs are working!")
        print("We'll use dashboard-01.moengage.com for the automation.")
    else:
        print("❌ Dashboard APIs not working either.")
        print("We'll need to use the Campaign Report API approach.")

if __name__ == "__main__":
    main()