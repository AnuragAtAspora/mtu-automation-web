#!/usr/bin/env python3
"""
Test script to determine the correct MoEngage data center
"""

import requests
import base64
from datetime import datetime, timedelta

def test_data_center(app_id, api_key, data_center):
    """Test if a data center works with your credentials"""
    
    # Create auth header
    auth_string = f"{app_id}:{api_key}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': app_id
    }
    
    # Test with Stats API
    url = f"https://api-{data_center}.moengage.com/v1/campaigns/stats"
    
    # Use a recent date range for testing
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=7)
    
    payload = {
        'request_id': f'test_{int(datetime.now().timestamp())}',
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'attribution_type': 'TOTAL_CONVERSIONS',
        'metric_type': 'TOTAL'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Data Center {data_center}: Status {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ SUCCESS: Data Center {data_center} works!")
            return True
        elif response.status_code == 401:
            print(f"❌ Authentication failed for DC {data_center}")
        elif response.status_code == 404:
            print(f"❌ Endpoint not found for DC {data_center}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error for DC {data_center}: {e}")
    
    return False

def main():
    # Your credentials
    APP_ID = "95PNUHBSYSLLJZ22PEOFMKF2"
    API_KEY = "3XMHJ83D2X4V"
    
    print("Testing MoEngage Data Centers...")
    print("=" * 40)
    
    # Test common data centers
    data_centers = ["01", "02", "03", "04", "05"]
    
    working_dc = None
    for dc in data_centers:
        if test_data_center(APP_ID, API_KEY, dc):
            working_dc = dc
            break
        print()
    
    if working_dc:
        print(f"\n🎉 Your data center is: {working_dc}")
        print(f"Use DATA_CENTER = \"{working_dc}\" in your config.py")
    else:
        print("\n❌ Could not determine data center.")
        print("Please check:")
        print("1. Your credentials are correct")
        print("2. Your MoEngage dashboard URL (e.g., app-01.moengage.com)")
        print("3. Contact MoEngage support for your data center number")

if __name__ == "__main__":
    main()