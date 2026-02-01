#!/usr/bin/env python3
"""
Test both MoEngage API keys with their respective endpoints
"""

import requests
import base64
from datetime import datetime, timedelta
from config import MOENGAGE_APP_ID, DATA_API_KEY, CAMPAIGN_API_KEY, DATA_CENTER

def test_campaign_stats_api():
    """Test Campaign Stats API with Campaign API Key"""
    
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
    
    url = f"https://api-{DATA_CENTER}.moengage.com/v1/campaigns/stats"
    
    payload = {
        'request_id': f'test_{int(datetime.now().timestamp())}',
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'attribution_type': 'TOTAL_CONVERSIONS',
        'metric_type': 'TOTAL'
    }
    
    print("Testing Campaign Stats API...")
    print(f"URL: {url}")
    print(f"API Key: {CAMPAIGN_API_KEY}")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Campaign Stats API working!")
            print(f"Response keys: {list(data.keys())}")
            
            if 'data' in data and data['data']:
                print(f"Found campaign data with {len(data['data'])} entries")
                
                # Look for platform data in first campaign
                first_campaign_id = list(data['data'].keys())[0]
                first_campaign = data['data'][first_campaign_id][0]
                
                if 'platforms' in first_campaign:
                    platforms = list(first_campaign['platforms'].keys())
                    print(f"Available platforms: {platforms}")
                    
                    # Check for email/push data
                    for platform in platforms:
                        platform_data = first_campaign['platforms'][platform]
                        if 'locales' in platform_data:
                            locale_data = platform_data['locales']['all_locales']['variations']['all_variations']
                            if 'performance_stats' in locale_data:
                                sent_count = locale_data['performance_stats'].get('sent', 0)
                                print(f"{platform} sent count: {sent_count}")
                else:
                    print("No platform data found")
            else:
                print("No campaign data found (normal if no campaigns in date range)")
                
            return True
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def test_segments_api():
    """Test Custom Segments API with Data API Key"""
    
    auth_string = f"{MOENGAGE_APP_ID}:{DATA_API_KEY}"
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
    
    print("\nTesting Custom Segments API...")
    print(f"URL: {url}")
    print(f"API Key: {DATA_API_KEY}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Segments API working!")
            
            segment_id = data.get('data', {}).get('id')
            if segment_id:
                print(f"Created test segment: {segment_id}")
                
                # Try to get segment details
                import time
                time.sleep(3)  # Wait for segment processing
                
                get_url = f"{url}/{segment_id}"
                get_response = requests.get(get_url, headers=headers, timeout=30)
                
                if get_response.status_code == 200:
                    segment_data = get_response.json()
                    user_count = segment_data.get('data', {}).get('user_count', 'Processing...')
                    print(f"User count: {user_count}")
                else:
                    print(f"Could not get segment details: {get_response.status_code}")
                
                # Clean up: delete test segment
                delete_response = requests.delete(get_url, headers=headers, timeout=30)
                if delete_response.status_code == 200:
                    print("✅ Test segment cleaned up")
                else:
                    print(f"Could not delete test segment: {delete_response.status_code}")
                
            return True
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    print("MoEngage API Test with Both Keys")
    print("=" * 40)
    print(f"Workspace ID: {MOENGAGE_APP_ID}")
    print(f"Data Center: {DATA_CENTER}")
    print(f"Data API Key: {DATA_API_KEY}")
    print(f"Campaign API Key: {CAMPAIGN_API_KEY}")
    print()
    
    # Test both APIs
    stats_ok = test_campaign_stats_api()
    segments_ok = test_segments_api()
    
    print("\n" + "=" * 40)
    if stats_ok and segments_ok:
        print("🎉 All tests passed! Both API keys are working.")
        print("You can now run the main automation script.")
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()