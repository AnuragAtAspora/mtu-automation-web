#!/usr/bin/env python3
"""
Test MoEngage Stats API with proper APP_SECRET_KEY authentication
"""

import requests
import base64
import json
from datetime import datetime, timedelta

# Configuration
MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'campaign_api_key': '3XMHJ83D2X4V',  # This is our APP_SECRET_KEY
    'data_center': '01'
}

def test_stats_api_with_app_secret_key():
    """Test Stats API with proper APP_SECRET_KEY header"""
    
    print("🧪 TESTING STATS API WITH APP_SECRET_KEY")
    print("=" * 60)
    
    # The endpoint that was responding with 401 asking for APP_SECRET_KEY
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaign-stats"
    
    # Method 1: APP_SECRET_KEY as header
    print("🔑 Method 1: APP_SECRET_KEY as header")
    
    headers = {
        'Content-Type': 'application/json',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key']  # Using campaign API key as secret
    }
    
    payload = {
        'request_id': f"stats_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'start_date': '2026-01-01',
        'end_date': '2026-01-31',
        'attribution_type': 'TOTAL_CONVERSIONS',
        'metric_type': 'TOTAL',
        'offset': 0,
        'limit': 10
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Stats API is working!")
            data = response.json()
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            return data
        elif response.status_code == 403:
            print("❌ 403 Forbidden - Stats API not enabled for your account")
            print("Contact MoEngage support to enable Stats API access")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Method 2: Try with Basic Auth + APP_SECRET_KEY
    print("\n🔑 Method 2: Basic Auth + APP_SECRET_KEY header")
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key']
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Stats API is working!")
            data = response.json()
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            return data
        elif response.status_code == 403:
            print("❌ 403 Forbidden - Stats API not enabled for your account")
            print("Contact MoEngage support to enable Stats API access")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Method 3: Try with Data API key as APP_SECRET_KEY
    print("\n🔑 Method 3: Using Data API Key as APP_SECRET_KEY")
    
    headers = {
        'Content-Type': 'application/json',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['data_api_key']  # Try data API key instead
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Stats API is working!")
            data = response.json()
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            return data
        elif response.status_code == 403:
            print("❌ 403 Forbidden - Stats API not enabled for your account")
            print("Contact MoEngage support to enable Stats API access")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return None

def test_alternative_stats_endpoints():
    """Test alternative endpoints that might provide campaign stats"""
    
    print("\n🔍 TESTING ALTERNATIVE STATS ENDPOINTS")
    print("=" * 60)
    
    # Test different possible endpoints
    endpoints = [
        '/core-services/v1/campaigns/stats',
        '/v1/campaigns/stats', 
        '/v2/campaigns/stats',
        '/core-services/v2/campaign-stats',
        '/api/v1/campaigns/stats',
        '/analytics/v1/campaigns/stats'
    ]
    
    for endpoint in endpoints:
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
        
        headers = {
            'Content-Type': 'application/json',
            'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
            'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key']
        }
        
        payload = {
            'start_date': '2026-01-01',
            'end_date': '2026-01-31'
        }
        
        print(f"\n🧪 Testing: {endpoint}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS! Working endpoint: {endpoint}")
                return response.json()
            elif response.status_code == 404:
                print("❌ 404 - Endpoint not found")
            elif response.status_code == 401:
                print("❌ 401 - Authentication issue")
            elif response.status_code == 403:
                print("❌ 403 - Forbidden (API not enabled)")
            else:
                print(f"❌ {response.status_code} - {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    return None

def main():
    print("🚀 MOENGAGE STATS API IMPLEMENTATION")
    print("=" * 60)
    print(f"Using credentials:")
    print(f"  Workspace ID: {MOENGAGE_CONFIG['workspace_id']}")
    print(f"  Campaign API Key: {MOENGAGE_CONFIG['campaign_api_key']}")
    print(f"  Data API Key: {MOENGAGE_CONFIG['data_api_key']}")
    print(f"  Data Center: {MOENGAGE_CONFIG['data_center']}")
    
    # Test the main Stats API endpoint
    result1 = test_stats_api_with_app_secret_key()
    
    # Test alternative endpoints
    result2 = test_alternative_stats_endpoints()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS:")
    
    if result1 or result2:
        print("✅ Stats API is working!")
        if result1:
            print("✅ Main endpoint successful")
        if result2:
            print("✅ Alternative endpoint successful")
    else:
        print("❌ Stats API not accessible")
        print("\nPossible reasons:")
        print("1. Stats API not enabled for your MoEngage account")
        print("2. Different authentication method required")
        print("3. Need to contact MoEngage support for API access")
        print("4. Different endpoint URL structure")
        
        print("\nNext steps:")
        print("1. Contact MoEngage support to enable Stats API")
        print("2. Verify your account has access to advanced APIs")
        print("3. Check if there's a different secret key or auth method")

if __name__ == "__main__":
    main()