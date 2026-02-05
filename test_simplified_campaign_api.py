#!/usr/bin/env python3
"""
Test MoEngage Campaign Details API with simplified parameters
Fix the status values and test step by step
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

def test_minimal_campaign_api():
    """Test with minimal parameters first"""
    
    print("🔍 TESTING MINIMAL CAMPAIGN API")
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
    
    # Minimal payload - just required fields
    payload = {
        "request_id": f"minimal_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 15,
        "page": 1
    }
    
    try:
        print(f"📡 Testing minimal parameters...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            campaigns = response.json()
            print(f"✅ SUCCESS! Found {len(campaigns)} campaigns")
            return campaigns
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_with_channel_filter():
    """Test with channel filter only"""
    
    print("\n🔍 TESTING WITH CHANNEL FILTER")
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
    
    # Test with channel filter
    payload = {
        "request_id": f"channel_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 15,
        "page": 1,
        "campaign_fields": {
            "channels": ["PUSH", "EMAIL"]
        }
    }
    
    try:
        print(f"📡 Testing with channel filter...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            campaigns = response.json()
            print(f"✅ SUCCESS! Found {len(campaigns)} campaigns")
            return campaigns
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_with_date_filter():
    """Test with date filter only"""
    
    print("\n🔍 TESTING WITH DATE FILTER")
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
    
    # Test with date filter
    payload = {
        "request_id": f"date_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 15,
        "page": 1,
        "campaign_fields": {
            "created_date": {
                "from_date": "2026-01-01",
                "to_date": "2026-01-31"
            }
        }
    }
    
    try:
        print(f"📡 Testing with date filter...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            campaigns = response.json()
            print(f"✅ SUCCESS! Found {len(campaigns)} campaigns")
            return campaigns
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_different_status_values():
    """Test different status values to find the correct ones"""
    
    print("\n🔍 TESTING DIFFERENT STATUS VALUES")
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
    
    # Try different status values
    status_options = [
        ["ACTIVE"],
        ["SENT"],
        ["SCHEDULED"],
        ["PAUSED"],
        ["ACTIVE", "SENT"],
        ["LIVE"],
        ["COMPLETED"],
        ["DRAFT"]
    ]
    
    for status_list in status_options:
        payload = {
            "request_id": f"status_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "limit": 5,
            "page": 1,
            "campaign_fields": {
                "status": status_list
            }
        }
        
        try:
            print(f"📡 Testing status: {status_list}")
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                campaigns = response.json()
                print(f"✅ SUCCESS with {status_list}! Found {len(campaigns)} campaigns")
                return campaigns, status_list
            elif response.status_code == 400:
                error_data = response.json()
                print(f"❌ 400 Bad Request: {error_data.get('error', {}).get('message', 'Unknown error')}")
            else:
                print(f"❌ {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    return None, None

def analyze_campaign_structure(campaigns):
    """Analyze the structure of returned campaigns"""
    
    if not campaigns:
        print("❌ No campaigns to analyze")
        return
    
    print(f"\n📊 ANALYZING CAMPAIGN STRUCTURE")
    print("=" * 50)
    print(f"Total campaigns: {len(campaigns)}")
    
    # Analyze first campaign in detail
    if campaigns:
        campaign = campaigns[0]
        print(f"\nSample campaign structure:")
        print(f"Available keys: {list(campaign.keys())}")
        
        # Check each key
        for key, value in campaign.items():
            if isinstance(value, dict):
                print(f"  {key}: {list(value.keys())}")
            elif isinstance(value, list):
                print(f"  {key}: list with {len(value)} items")
            else:
                print(f"  {key}: {value}")
        
        # Look for campaign name
        basic_details = campaign.get('basic_details', {})
        if basic_details:
            print(f"\nBasic Details:")
            for key, value in basic_details.items():
                print(f"  {key}: {value}")
        
        # Look for performance data
        performance_keys = []
        for key in campaign.keys():
            if any(word in key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered', 'open', 'click']):
                performance_keys.append(key)
        
        if performance_keys:
            print(f"\nPerformance-related keys found: {performance_keys}")
            for key in performance_keys:
                print(f"  {key}: {campaign[key]}")
        else:
            print(f"\n❌ No performance data found in campaign object")

def main():
    """Main test function"""
    
    print("🚀 STEP-BY-STEP CAMPAIGN API TESTING")
    print("=" * 80)
    
    # Step 1: Test minimal parameters
    campaigns = test_minimal_campaign_api()
    if campaigns:
        analyze_campaign_structure(campaigns)
        return campaigns
    
    # Step 2: Test with channel filter
    campaigns = test_with_channel_filter()
    if campaigns:
        analyze_campaign_structure(campaigns)
        return campaigns
    
    # Step 3: Test with date filter
    campaigns = test_with_date_filter()
    if campaigns:
        analyze_campaign_structure(campaigns)
        return campaigns
    
    # Step 4: Test different status values
    campaigns, working_status = test_different_status_values()
    if campaigns:
        print(f"\n✅ Working status values: {working_status}")
        analyze_campaign_structure(campaigns)
        return campaigns
    
    print("\n❌ All tests failed - API may not be enabled")
    return None

if __name__ == "__main__":
    main()