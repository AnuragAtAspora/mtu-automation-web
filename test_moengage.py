#!/usr/bin/env python3
"""
Test MoEngage API connection and basic functionality
"""

import requests
import base64
from datetime import datetime, timedelta
from config import MOENGAGE_APP_ID, MOENGAGE_API_KEY, DATA_CENTER

def test_stats_api():
    """Test the Stats API with your credentials"""
    
    # Create auth header
    auth_string = f"{MOENGAGE_APP_ID}:{MOENGAGE_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': MOENGAGE_APP_ID
    }
    
    # Test with a recent 7-day period
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=7)
    
    url = f"https://api-{DATA_CENTER}.moengage.com/v1/campaigns/stats"
    
    payload = {
        'request_id': f'test_{int(datetime.now().timestamp())}',
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'attribution_type': 'TOTAL_CONVERSIONS',
        'metric_type': 'TOTAL'
    }
    
    print(f"Testing Stats API...")
    print(f"URL: {url}")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Stats API working!")
            print(f"Response keys: {list(data.keys())}")
            
            # Look for campaign data
            if 'data' in data and data['data']:
                print(f"Found {len(data['data'])} campaigns")
                
                # Check for email/push data in first campaign
                first_campaign = data['data'][0]
                if 'platforms' in first_campaign:
                    platforms = list(first_campaign['platforms'].keys())
                    print(f"Available platforms: {platforms}")
                else:
                    print("No platform data found in response")
            else:
                print("No campaign data found (this might be normal if no campaigns in date range)")
                
            return True
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def test_segments_api():
    """Test the Custom Segments API"""
    
    # Create auth header
    auth_string = f"{MOENGAGE_APP_ID}:{MOENGAGE_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': MOENGAGE_APP_ID
    }
    
    url = f"https://api-{DATA_CENTER}.moengage.com/v1/segments"
    
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
    
    print(f"\nTesting Custom Segments API...")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Segments API working!")
            
            segment_id = data.get('data', {}).get('id')
            if segment_id:
                print(f"Created test segment: {segment_id}")
                
                # Try to get segment details (which should include user count)
                get_url = f"{url}/{segment_id}"
                get_response = requests.get(get_url, headers=headers, timeout=30)
                
                if get_response.status_code == 200:
                    segment_data = get_response.json()
                    user_count = segment_data.get('data', {}).get('user_count', 'Not available')
                    print(f"User count: {user_count}")
                
                # Clean up: delete test segment
                delete_response = requests.delete(get_url, headers=headers, timeout=30)
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
    print("MoEngage API Test")
    print("=" * 30)
    print(f"Workspace ID: {MOENGAGE_APP_ID}")
    print(f"Data Center: {DATA_CENTER}")
    print()
    
    # Test both APIs
    stats_ok = test_stats_api()
    segments_ok = test_segments_api()
    
    print("\n" + "=" * 30)
    if stats_ok and segments_ok:
        print("🎉 All tests passed! Your MoEngage setup is working.")
        print("You can now run the main automation script.")
    else:
        print("❌ Some tests failed. Please check your credentials and try again.")

if __name__ == "__main__":
    main()