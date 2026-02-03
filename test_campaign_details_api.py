#!/usr/bin/env python3
"""
Test MoEngage Campaign Details API for getting campaign statistics
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

def test_campaign_details_api():
    """Test Campaign Details API to get campaign statistics"""
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/search"
    
    # Try with Data API credentials
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Content-Type': 'application/json'
    }
    
    # Payload to search for campaigns in January 2026
    payload = {
        "filters": {
            "campaign_type": ["push", "email"],
            "status": ["sent", "completed"],
            "created_date": {
                "start_date": "2026-01-01T00:00:00.000Z",
                "end_date": "2026-01-31T23:59:59.999Z"
            }
        },
        "include_stats": True,
        "page_size": 100
    }
    
    print("🧪 Testing Campaign Details API")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Response structure:")
            
            if isinstance(data, dict):
                print(f"Top-level keys: {list(data.keys())}")
                
                # Look for campaigns data
                if 'campaigns' in data:
                    campaigns = data['campaigns']
                    print(f"Found {len(campaigns)} campaigns")
                    
                    # Analyze first few campaigns
                    uk_total_push = 0
                    uae_total_push = 0
                    uk_total_email = 0
                    uae_total_email = 0
                    
                    for i, campaign in enumerate(campaigns[:10]):  # First 10 campaigns
                        print(f"\nCampaign {i+1}:")
                        print(f"  Name: {campaign.get('name', 'N/A')}")
                        print(f"  Type: {campaign.get('campaign_type', 'N/A')}")
                        print(f"  Status: {campaign.get('status', 'N/A')}")
                        
                        # Look for stats
                        if 'stats' in campaign:
                            stats = campaign['stats']
                            print(f"  Stats keys: {list(stats.keys())}")
                            
                            sent_count = stats.get('sent', 0)
                            campaign_name = campaign.get('name', '').lower()
                            campaign_type = campaign.get('campaign_type', '').lower()
                            
                            # Count by country and type
                            if 'uk' in campaign_name:
                                if 'push' in campaign_type:
                                    uk_total_push += sent_count
                                elif 'email' in campaign_type:
                                    uk_total_email += sent_count
                            elif 'uae' in campaign_name:
                                if 'push' in campaign_type:
                                    uae_total_push += sent_count
                                elif 'email' in campaign_type:
                                    uae_total_email += sent_count
                    
                    print(f"\n📊 AGGREGATED RESULTS:")
                    print(f"UK Push Total: {uk_total_push:,}")
                    print(f"UK Email Total: {uk_total_email:,}")
                    print(f"UAE Push Total: {uae_total_push:,}")
                    print(f"UAE Email Total: {uae_total_email:,}")
                    
                    return {
                        'uk_push': uk_total_push,
                        'uk_email': uk_total_email,
                        'uae_push': uae_total_push,
                        'uae_email': uae_total_email,
                        'total_campaigns': len(campaigns)
                    }
                else:
                    print(f"No 'campaigns' key found. Available keys: {list(data.keys())}")
                    if len(str(data)) < 1000:
                        print(f"Full response: {json.dumps(data, indent=2)}")
            
            return data
            
        elif response.status_code == 401:
            print(f"❌ Authentication failed: {response.text}")
            print("This API might require different credentials or API enablement")
            return None
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_simple_campaign_list():
    """Test a simpler campaign list endpoint"""
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v1/campaigns"
    
    # Try with Campaign API credentials
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Content-Type': 'application/json'
    }
    
    print("\n🧪 Testing Simple Campaign List API")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            return data
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def main():
    print("🔍 TESTING MOENGAGE CAMPAIGN DETAILS API")
    print("=" * 60)
    
    # Test 1: Campaign Details API with search
    result1 = test_campaign_details_api()
    
    # Test 2: Simple campaign list
    result2 = test_simple_campaign_list()
    
    print("\n" + "=" * 60)
    print("📊 CONCLUSION:")
    
    if result1 or result2:
        print("✅ Found working API endpoint(s) for campaign data!")
        if result1 and isinstance(result1, dict) and 'uk_push' in result1:
            print(f"Campaign Details API provided aggregated stats:")
            print(f"  UK Push: {result1['uk_push']:,}")
            print(f"  UAE Push: {result1['uae_push']:,}")
            print(f"  Total campaigns: {result1['total_campaigns']}")
    else:
        print("❌ No working campaign API endpoints found")
        print("The Stats API might need to be enabled by MoEngage support")

if __name__ == "__main__":
    main()