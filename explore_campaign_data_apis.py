#!/usr/bin/env python3
"""
Explore all possible ways to get campaign data from MoEngage
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

def test_campaign_search_api():
    """Test Campaign Search API - this one we know works"""
    
    print("🔍 1. CAMPAIGN SEARCH API")
    print("=" * 50)
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/search"
    
    # Use Data API credentials
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Content-Type': 'application/json'
    }
    
    # Search for campaigns with date range
    payload = {
        "filters": {
            "campaign_type": ["push", "email"],
            "status": ["sent", "completed"],
            "sent_date": {
                "start_date": "2026-01-01T00:00:00.000Z",
                "end_date": "2026-01-31T23:59:59.999Z"
            }
        },
        "page_size": 100,
        "sort_by": "sent_date",
        "sort_order": "desc"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Found campaigns")
            
            if 'campaigns' in data:
                campaigns = data['campaigns']
                print(f"Total campaigns: {len(campaigns)}")
                
                # Show sample campaign structure
                if campaigns:
                    sample = campaigns[0]
                    print(f"Sample campaign keys: {list(sample.keys())}")
                    print(f"Campaign name: {sample.get('name', 'N/A')}")
                    print(f"Campaign type: {sample.get('campaign_type', 'N/A')}")
                    print(f"Status: {sample.get('status', 'N/A')}")
                    
                    # Look for stats/metrics
                    if 'stats' in sample:
                        print(f"Stats available: {list(sample['stats'].keys())}")
                    if 'metrics' in sample:
                        print(f"Metrics available: {list(sample['metrics'].keys())}")
                    if 'performance' in sample:
                        print(f"Performance available: {list(sample['performance'].keys())}")
                
                return data
            else:
                print(f"Response structure: {list(data.keys())}")
                
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return None

def test_campaign_details_api():
    """Test getting individual campaign details"""
    
    print("\n🔍 2. CAMPAIGN DETAILS API")
    print("=" * 50)
    
    # First get a campaign ID from search
    search_result = test_campaign_search_api()
    if not search_result or 'campaigns' not in search_result:
        print("❌ No campaigns found to test details API")
        return None
    
    campaign_id = search_result['campaigns'][0].get('id')
    if not campaign_id:
        print("❌ No campaign ID found")
        return None
    
    print(f"Testing details for campaign ID: {campaign_id}")
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/{campaign_id}"
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id']
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Campaign details retrieved")
            print(f"Available keys: {list(data.keys())}")
            
            # Look for performance data
            if 'performance' in data:
                print(f"Performance data: {data['performance']}")
            if 'stats' in data:
                print(f"Stats data: {data['stats']}")
            if 'metrics' in data:
                print(f"Metrics data: {data['metrics']}")
                
            return data
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return None

def test_analytics_endpoints():
    """Test various analytics endpoints"""
    
    print("\n🔍 3. ANALYTICS ENDPOINTS")
    print("=" * 50)
    
    endpoints = [
        '/v1/analytics/campaigns',
        '/v2/analytics/campaigns', 
        '/core-services/v1/analytics/campaigns',
        '/v1/reports/campaigns',
        '/v2/reports/campaigns',
        '/core-services/v1/reports/campaigns',
        '/v1/campaign-analytics',
        '/v2/campaign-analytics',
        '/core-services/v1/campaign-analytics'
    ]
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Content-Type': 'application/json'
    }
    
    payload = {
        'start_date': '2026-01-01',
        'end_date': '2026-01-31',
        'metrics': ['sent', 'delivered', 'opened', 'clicked']
    }
    
    working_endpoints = []
    
    for endpoint in endpoints:
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
        print(f"\nTesting: {endpoint}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS! Working endpoint: {endpoint}")
                working_endpoints.append(endpoint)
                data = response.json()
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            elif response.status_code == 404:
                print("❌ 404 - Not found")
            elif response.status_code == 401:
                print("❌ 401 - Auth issue")
            elif response.status_code == 403:
                print("❌ 403 - Forbidden")
            else:
                print(f"❌ {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    return working_endpoints

def test_data_export_api():
    """Test Data Export API for campaign data"""
    
    print("\n🔍 4. DATA EXPORT API")
    print("=" * 50)
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v1/data-export/campaigns"
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Content-Type': 'application/json'
    }
    
    payload = {
        'start_date': '2026-01-01T00:00:00.000Z',
        'end_date': '2026-01-31T23:59:59.999Z',
        'export_type': 'campaigns',
        'format': 'json'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Data Export API working")
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            return data
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return None

def test_webhook_data():
    """Test if we can get campaign data via webhooks"""
    
    print("\n🔍 5. WEBHOOK DATA")
    print("=" * 50)
    print("Webhooks require server setup and real-time campaign events")
    print("This would give us real-time campaign performance data")
    print("But requires infrastructure and doesn't provide historical data")
    
    return None

def test_dashboard_api():
    """Test dashboard-related APIs"""
    
    print("\n🔍 6. DASHBOARD APIs")
    print("=" * 50)
    
    endpoints = [
        '/v1/dashboard/campaigns',
        '/v2/dashboard/campaigns',
        '/core-services/v1/dashboard/campaigns',
        '/v1/dashboard/analytics',
        '/v2/dashboard/analytics'
    ]
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Content-Type': 'application/json'
    }
    
    payload = {
        'date_range': {
            'start': '2026-01-01',
            'end': '2026-01-31'
        }
    }
    
    for endpoint in endpoints:
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
        print(f"\nTesting: {endpoint}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS! Working endpoint: {endpoint}")
                data = response.json()
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            elif response.status_code == 404:
                print("❌ 404 - Not found")
            else:
                print(f"❌ {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def main():
    print("🚀 EXPLORING ALL MOENGAGE CAMPAIGN DATA SOURCES")
    print("=" * 60)
    
    # Test all possible data sources
    search_result = test_campaign_search_api()
    details_result = test_campaign_details_api()
    analytics_endpoints = test_analytics_endpoints()
    export_result = test_data_export_api()
    test_webhook_data()
    test_dashboard_api()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY OF AVAILABLE DATA SOURCES:")
    
    print("\n✅ WORKING APIS:")
    if search_result:
        print("1. Campaign Search API - ✅ Working (basic campaign info)")
    if details_result:
        print("2. Campaign Details API - ✅ Working (individual campaign data)")
    if analytics_endpoints:
        print(f"3. Analytics Endpoints - ✅ {len(analytics_endpoints)} working")
    if export_result:
        print("4. Data Export API - ✅ Working")
    
    print("\n❌ NOT AVAILABLE:")
    print("• Stats API - 403 Forbidden (not enabled)")
    print("• Most Analytics endpoints - 404 Not Found")
    
    print("\n🔧 CURRENT BEST OPTIONS:")
    print("1. Campaign Reports API (what you're using) - Fixed date ranges")
    print("2. Campaign Search API - Get campaign list with basic stats")
    print("3. Campaign Details API - Get individual campaign performance")
    print("4. Data Export API - If available, might provide bulk data")
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. Keep using Reports API as primary (most reliable)")
    print("2. Try Campaign Search + Details APIs for dynamic date ranges")
    print("3. Contact MoEngage to enable Stats API for best results")
    print("4. Consider Data Export API for bulk historical data")

if __name__ == "__main__":
    main()