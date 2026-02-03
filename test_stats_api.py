#!/usr/bin/env python3
"""
Test MoEngage Stats API for campaign statistics with date ranges
"""

import requests
import base64
import json
from datetime import datetime, timedelta

# Configuration
MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'campaign_api_key': '3XMHJ83D2X4V',
    'data_center': '01'
}

def test_stats_api_endpoint(endpoint, payload, test_name):
    """Test a Stats API endpoint with given payload"""
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
    
    # Try with Data API credentials first
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Content-Type': 'application/json'
    }
    
    print(f"\n🧪 {test_name}")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Success! Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                if isinstance(data, dict) and len(str(data)) < 1000:
                    print(f"Response: {json.dumps(data, indent=2)}")
                return data
            except:
                print(f"✅ Success! Response (not JSON): {response.text[:200]}...")
                return response.text
        else:
            print(f"❌ Failed: {response.text}")
            
            # If Data API fails, try Campaign API
            if 'data_api_key' in str(headers):
                print("🔄 Retrying with Campaign API credentials...")
                auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
                encoded_auth = base64.b64encode(auth_string.encode()).decode()
                headers['Authorization'] = f'Basic {encoded_auth}'
                
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                print(f"Campaign API Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✅ Campaign API Success! Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        return data
                    except:
                        print(f"✅ Campaign API Success! Response: {response.text[:200]}...")
                        return response.text
                else:
                    print(f"❌ Campaign API also failed: {response.text}")
            
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def main():
    print("🔍 TESTING MOENGAGE STATS API ENDPOINTS")
    print("=" * 60)
    
    # Test date range
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    # Test different possible Stats API endpoints
    test_cases = [
        {
            'endpoint': '/v1/campaigns/stats',
            'payload': {
                'start_date': start_date,
                'end_date': end_date,
                'campaign_type': 'push'
            },
            'name': 'Stats API v1 - Push campaigns'
        },
        {
            'endpoint': '/v2/campaigns/stats',
            'payload': {
                'start_date': start_date,
                'end_date': end_date,
                'channels': ['push', 'email']
            },
            'name': 'Stats API v2 - Multiple channels'
        },
        {
            'endpoint': '/core-services/v1/campaigns/stats',
            'payload': {
                'start_date': start_date,
                'end_date': end_date
            },
            'name': 'Core Services Stats API'
        },
        {
            'endpoint': '/v1/analytics/campaigns',
            'payload': {
                'date_range': {
                    'start': start_date,
                    'end': end_date
                },
                'metrics': ['sent', 'delivered', 'opened']
            },
            'name': 'Analytics API - Campaign metrics'
        },
        {
            'endpoint': '/core-services/v1/campaigns/search',
            'payload': {
                'filters': {
                    'date_range': {
                        'start_date': start_date,
                        'end_date': end_date
                    },
                    'campaign_type': ['push', 'email']
                }
            },
            'name': 'Campaign Search API with stats'
        },
        {
            'endpoint': '/v1/reports/campaigns',
            'payload': {
                'start_date': start_date,
                'end_date': end_date,
                'group_by': ['campaign_name', 'channel'],
                'metrics': ['sent', 'delivered']
            },
            'name': 'Reports API - Campaign aggregation'
        }
    ]
    
    successful_endpoints = []
    
    for test_case in test_cases:
        result = test_stats_api_endpoint(
            test_case['endpoint'],
            test_case['payload'],
            test_case['name']
        )
        
        if result:
            successful_endpoints.append({
                'endpoint': test_case['endpoint'],
                'name': test_case['name'],
                'result': result
            })
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    
    if successful_endpoints:
        print(f"✅ Found {len(successful_endpoints)} working endpoint(s):")
        for endpoint in successful_endpoints:
            print(f"  - {endpoint['name']}: {endpoint['endpoint']}")
    else:
        print("❌ No working Stats API endpoints found")
        print("Possible reasons:")
        print("1. Stats API not enabled for your account")
        print("2. Different endpoint structure")
        print("3. Different authentication method required")
        print("4. Need to contact MoEngage support for API access")

if __name__ == "__main__":
    main()