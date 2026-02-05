#!/usr/bin/env python3
"""
Test Campaign Search API with correct authentication
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

def test_campaign_search_with_correct_auth():
    """Test Campaign Search API with APP_SECRET_KEY"""
    
    print("🔍 TESTING CAMPAIGN SEARCH API")
    print("=" * 50)
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/search"
    
    # Try with Campaign API credentials + APP_SECRET_KEY (same as Stats API)
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key'],
        'Content-Type': 'application/json'
    }
    
    # Search for campaigns in January 2026
    payload = {
        "request_id": f"campaign_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "page": 1,
        "limit": 15
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Campaign Search API working!")
            
            # Handle different response structures
            campaigns = []
            if isinstance(data, list):
                campaigns = data
                print(f"Response is a list with {len(campaigns)} campaigns")
            elif isinstance(data, dict) and 'campaigns' in data:
                campaigns = data['campaigns']
                print(f"Response is a dict with {len(campaigns)} campaigns")
            elif isinstance(data, dict):
                print(f"Response is a dict with keys: {list(data.keys())}")
                # Look for campaigns in different possible keys
                for key in ['data', 'results', 'items', 'campaigns']:
                    if key in data and isinstance(data[key], list):
                        campaigns = data[key]
                        print(f"Found campaigns in '{key}': {len(campaigns)} items")
                        break
            
            if campaigns:
                print(f"Total campaigns found: {len(campaigns)}")
                
                # Analyze campaign data structure
                sample = campaigns[0]
                print(f"\nSample campaign structure:")
                print(f"  Available keys: {list(sample.keys()) if isinstance(sample, dict) else 'Not a dict'}")
                
                if isinstance(sample, dict):
                    print(f"  Name: {sample.get('name', 'N/A')}")
                    print(f"  Type: {sample.get('campaign_type', 'N/A')}")
                    print(f"  Status: {sample.get('status', 'N/A')}")
                    
                    # Look for performance/stats data
                    stats_keys = []
                    for key in sample.keys():
                        if any(word in key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered', 'open', 'click']):
                            stats_keys.append(key)
                    
                    if stats_keys:
                        print(f"  Stats-related keys: {stats_keys}")
                        for key in stats_keys:
                            print(f"    {key}: {sample[key]}")
                    else:
                        print("  No stats data found in campaign object")
                
                # Try to aggregate communication counts
                uk_counts = {'push': 0, 'email': 0}
                uae_counts = {'push': 0, 'email': 0}
                
                for campaign in campaigns:
                    if not isinstance(campaign, dict):
                        continue
                        
                    name = campaign.get('name', '').lower()
                    campaign_type = campaign.get('campaign_type', '').lower()
                    
                    # Look for sent count in various possible fields
                    sent_count = 0
                    for field in ['sent', 'sent_count', 'total_sent', 'delivered', 'stats', 'metrics', 'performance']:
                        if field in campaign:
                            if isinstance(campaign[field], (int, float)):
                                sent_count = campaign[field]
                                break
                            elif isinstance(campaign[field], dict) and 'sent' in campaign[field]:
                                sent_count = campaign[field]['sent']
                                break
                    
                    # Classify by country and type
                    if 'uk' in name:
                        if 'push' in campaign_type:
                            uk_counts['push'] += sent_count
                        elif 'email' in campaign_type:
                            uk_counts['email'] += sent_count
                    elif 'uae' in name:
                        if 'push' in campaign_type:
                            uae_counts['push'] += sent_count
                        elif 'email' in campaign_type:
                            uae_counts['email'] += sent_count
                
                print(f"\n📊 Aggregated counts (if available):")
                print(f"  UK Push: {uk_counts['push']:,}")
                print(f"  UK Email: {uk_counts['email']:,}")
                print(f"  UAE Push: {uae_counts['push']:,}")
                print(f"  UAE Email: {uae_counts['email']:,}")
                
                return data
            else:
                print("No campaigns found in response")
                print(f"Full response: {data}")
                return data
                
        elif response.status_code == 403:
            print("❌ 403 Forbidden - API not enabled or insufficient permissions")
        elif response.status_code == 401:
            print("❌ 401 Unauthorized - Authentication issue")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return None

def test_individual_campaign_details():
    """Test getting individual campaign details if search works"""
    
    print("\n🔍 TESTING INDIVIDUAL CAMPAIGN DETAILS")
    print("=" * 50)
    
    # First get campaigns from search
    search_result = test_campaign_search_with_correct_auth()
    
    if not search_result or 'campaigns' not in search_result or not search_result['campaigns']:
        print("❌ No campaigns available for details test")
        return None
    
    campaign_id = search_result['campaigns'][0].get('id')
    if not campaign_id:
        print("❌ No campaign ID found")
        return None
    
    print(f"Testing details for campaign: {campaign_id}")
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/{campaign_id}"
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key']
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Campaign details retrieved")
            print(f"Available keys: {list(data.keys())}")
            
            # Look for performance/stats data
            performance_data = {}
            for key in data.keys():
                if any(word in key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered', 'open', 'click']):
                    performance_data[key] = data[key]
            
            if performance_data:
                print(f"Performance data found:")
                for key, value in performance_data.items():
                    print(f"  {key}: {value}")
            else:
                print("No performance data found")
                
            return data
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return None

def main():
    print("🚀 TESTING ALTERNATIVE CAMPAIGN DATA SOURCES")
    print("=" * 60)
    
    search_result = test_campaign_search_with_correct_auth()
    details_result = test_individual_campaign_details()
    
    print("\n" + "=" * 60)
    print("📊 ALTERNATIVE DATA SOURCE ANALYSIS:")
    
    if search_result:
        print("✅ Campaign Search API - WORKING!")
        print("   • Can get list of campaigns with date filters")
        print("   • May include basic performance metrics")
        print("   • Could be used as alternative to Reports API")
    else:
        print("❌ Campaign Search API - Not working")
    
    if details_result:
        print("✅ Campaign Details API - WORKING!")
        print("   • Can get detailed info for individual campaigns")
        print("   • May include comprehensive performance data")
        print("   • Could complement Campaign Search API")
    else:
        print("❌ Campaign Details API - Not working")
    
    print("\n💡 RECOMMENDATIONS:")
    if search_result or details_result:
        print("1. ✅ You have working alternatives to Stats API!")
        print("2. 🔄 Can implement Campaign Search + Details as backup")
        print("3. 📊 May provide dynamic date ranges (unlike Reports API)")
        print("4. 🎯 Could give you real-time campaign performance data")
    else:
        print("1. ❌ No alternative APIs currently accessible")
        print("2. 📞 Contact MoEngage support for API access")
        print("3. 🔧 Continue using Reports API as primary method")
        print("4. ⏳ Wait for Stats API to be enabled")

if __name__ == "__main__":
    main()