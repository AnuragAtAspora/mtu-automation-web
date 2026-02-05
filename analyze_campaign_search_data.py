#!/usr/bin/env python3
"""
Analyze Campaign Search API data structure to extract campaign performance
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

def get_campaign_data():
    """Get campaign data and analyze structure"""
    
    print("🔍 ANALYZING CAMPAIGN SEARCH API DATA")
    print("=" * 50)
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/search"
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key'],
        'Content-Type': 'application/json'
    }
    
    payload = {
        "request_id": f"campaign_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "page": 1,
        "limit": 15
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            campaigns = response.json()
            print(f"✅ Found {len(campaigns)} campaigns")
            
            # Analyze each campaign in detail
            for i, campaign in enumerate(campaigns[:3]):  # Analyze first 3 campaigns
                print(f"\n📊 CAMPAIGN {i+1} DETAILED ANALYSIS:")
                print(f"Campaign ID: {campaign.get('campaign_id', 'N/A')}")
                print(f"Channel: {campaign.get('channel', 'N/A')}")
                print(f"Status: {campaign.get('status', 'N/A')}")
                print(f"Sent Time: {campaign.get('sent_time', 'N/A')}")
                
                # Analyze basic_details
                if 'basic_details' in campaign:
                    basic = campaign['basic_details']
                    print(f"Basic Details: {basic}")
                    if isinstance(basic, dict):
                        print(f"  Basic Details Keys: {list(basic.keys())}")
                        for key, value in basic.items():
                            if 'name' in key.lower() or 'title' in key.lower():
                                print(f"    {key}: {value}")
                
                # Analyze segmentation_details
                if 'segmentation_details' in campaign:
                    seg = campaign['segmentation_details']
                    if isinstance(seg, dict):
                        print(f"  Segmentation Keys: {list(seg.keys())}")
                
                # Look for performance data in all fields
                print(f"  All Keys: {list(campaign.keys())}")
                
                # Check if we can get individual campaign details
                campaign_id = campaign.get('campaign_id')
                if campaign_id:
                    details = get_individual_campaign_details(campaign_id)
                    if details:
                        print(f"  Individual Details Available: {list(details.keys())}")
            
            return campaigns
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def get_individual_campaign_details(campaign_id):
    """Get detailed info for a specific campaign"""
    
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
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n🔍 INDIVIDUAL CAMPAIGN DETAILS:")
            print(f"Available keys: {list(data.keys())}")
            
            # Look for performance/stats data
            for key, value in data.items():
                if any(word in key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered', 'open', 'click', 'analytics']):
                    print(f"  {key}: {value}")
            
            return data
        else:
            print(f"❌ Individual details failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Individual details exception: {str(e)}")
        return None

def test_campaign_performance_endpoints():
    """Test if there are performance-specific endpoints"""
    
    print("\n🔍 TESTING CAMPAIGN PERFORMANCE ENDPOINTS")
    print("=" * 50)
    
    # Get a campaign ID first
    campaigns = get_campaign_data()
    if not campaigns:
        print("❌ No campaigns to test performance endpoints")
        return
    
    campaign_id = campaigns[0].get('campaign_id')
    if not campaign_id:
        print("❌ No campaign ID found")
        return
    
    print(f"Testing performance endpoints for campaign: {campaign_id}")
    
    # Test various performance endpoints
    endpoints = [
        f'/core-services/v1/campaigns/{campaign_id}/stats',
        f'/core-services/v1/campaigns/{campaign_id}/performance',
        f'/core-services/v1/campaigns/{campaign_id}/metrics',
        f'/core-services/v1/campaigns/{campaign_id}/analytics',
        f'/v1/campaigns/{campaign_id}/stats',
        f'/v1/campaigns/{campaign_id}/performance'
    ]
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key']
    }
    
    working_endpoints = []
    
    for endpoint in endpoints:
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
        print(f"\nTesting: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS! Performance data available")
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                working_endpoints.append(endpoint)
                
                # Show sample performance data
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, (int, float)):
                            print(f"  {key}: {value:,}")
                        elif isinstance(value, dict):
                            print(f"  {key}: {list(value.keys())}")
                        else:
                            print(f"  {key}: {type(value)}")
                            
            elif response.status_code == 404:
                print("❌ 404 - Not found")
            elif response.status_code == 403:
                print("❌ 403 - Forbidden")
            else:
                print(f"❌ {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    return working_endpoints

def main():
    print("🚀 COMPREHENSIVE CAMPAIGN DATA ANALYSIS")
    print("=" * 60)
    
    # Get campaign data
    campaigns = get_campaign_data()
    
    # Test performance endpoints
    performance_endpoints = test_campaign_performance_endpoints()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    
    if campaigns:
        print(f"✅ Campaign Search API: {len(campaigns)} campaigns found")
        print("✅ Can get campaign list with basic info")
        
        # Check if we found campaign names
        has_names = False
        for campaign in campaigns[:3]:
            if 'basic_details' in campaign:
                basic = campaign['basic_details']
                if isinstance(basic, dict):
                    for key, value in basic.items():
                        if 'name' in key.lower() and value:
                            has_names = True
                            print(f"✅ Campaign names available in basic_details.{key}")
                            break
        
        if not has_names:
            print("❌ Campaign names not easily accessible")
    
    if performance_endpoints:
        print(f"✅ Performance endpoints: {len(performance_endpoints)} working")
        for endpoint in performance_endpoints:
            print(f"  • {endpoint}")
    else:
        print("❌ No performance endpoints found")
    
    print("\n💡 POTENTIAL AS REPORTS API ALTERNATIVE:")
    if campaigns and performance_endpoints:
        print("🎯 EXCELLENT! Full alternative available:")
        print("  1. Get campaign list with Search API")
        print("  2. Get performance data with Performance endpoints")
        print("  3. Filter by campaign names for UK/UAE")
        print("  4. Aggregate sent counts by country and type")
    elif campaigns:
        print("🔄 PARTIAL alternative available:")
        print("  1. Can get campaign list and basic info")
        print("  2. Need to find performance data source")
        print("  3. May need individual campaign details API")
    else:
        print("❌ Not suitable as Reports API alternative")

if __name__ == "__main__":
    main()