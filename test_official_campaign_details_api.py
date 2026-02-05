#!/usr/bin/env python3
"""
Test Official MoEngage "Get Campaign Details API" with proper documented parameters
Based on official documentation: https://developers.moengage.com/hc/en-us/articles/40800964029076-Get-SMS-Campaign-Details
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

def test_official_campaign_details_api():
    """Test the official Get Campaign Details API with documented parameters"""
    
    print("🔍 TESTING OFFICIAL GET CAMPAIGN DETAILS API")
    print("=" * 60)
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/search"
    
    # Official authentication method
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key'],
        'Content-Type': 'application/json'
    }
    
    # Official request payload with documented parameters
    payload = {
        "request_id": f"official_campaign_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 15,  # Maximum allowed
        "page": 1,
        "campaign_fields": {
            "channels": ["PUSH", "EMAIL"],  # Filter for Push and Email campaigns
            "created_date": {
                "from_date": "2026-01-01",  # January 2026
                "to_date": "2026-01-31"
            },
            "status": ["Active", "Sent", "Scheduled", "Paused"]  # All relevant statuses
        },
        "include_child_campaigns": True,  # Include periodic child campaigns
        "include_archive_campaigns": False  # Exclude archived campaigns
    }
    
    try:
        print(f"📡 Calling Official API with documented parameters...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            campaigns = response.json()
            print(f"✅ SUCCESS! Found {len(campaigns)} campaigns")
            
            # Analyze response structure in detail
            if campaigns:
                print(f"\n📊 DETAILED CAMPAIGN ANALYSIS:")
                
                for i, campaign in enumerate(campaigns[:3]):  # Analyze first 3 campaigns
                    print(f"\n--- CAMPAIGN {i+1} ---")
                    print(f"Campaign ID: {campaign.get('campaign_id', 'N/A')}")
                    print(f"Status: {campaign.get('status', 'N/A')}")
                    print(f"Channel: {campaign.get('channel', 'N/A')}")
                    print(f"Created By: {campaign.get('created_by', 'N/A')}")
                    print(f"Created At: {campaign.get('created_at', 'N/A')}")
                    print(f"Sent Time: {campaign.get('sent_time', 'N/A')}")
                    
                    # Check basic_details for campaign name
                    basic_details = campaign.get('basic_details', {})
                    if basic_details:
                        print(f"Campaign Name: {basic_details.get('name', 'N/A')}")
                        print(f"Tags: {basic_details.get('tags', [])}")
                        print(f"Team: {basic_details.get('team', 'N/A')}")
                    
                    # Look for performance/stats data in all fields
                    print(f"All Available Fields: {list(campaign.keys())}")
                    
                    # Check for any performance-related fields
                    performance_fields = []
                    for key in campaign.keys():
                        if any(word in key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered', 'open', 'click', 'conversion']):
                            performance_fields.append(key)
                    
                    if performance_fields:
                        print(f"Performance-related fields: {performance_fields}")
                        for field in performance_fields:
                            print(f"  {field}: {campaign[field]}")
                    else:
                        print("❌ No performance data found in campaign object")
                
                # Try to extract communication counts by country
                print(f"\n📈 ATTEMPTING TO EXTRACT COMMUNICATION COUNTS:")
                uk_counts = {'push': 0, 'email': 0}
                uae_counts = {'push': 0, 'email': 0}
                
                for campaign in campaigns:
                    # Get campaign name from basic_details
                    basic_details = campaign.get('basic_details', {})
                    campaign_name = basic_details.get('name', '').lower()
                    channel = campaign.get('channel', '').lower()
                    
                    print(f"Campaign: {campaign_name} | Channel: {channel}")
                    
                    # Look for sent counts in various possible locations
                    sent_count = 0
                    
                    # Check direct fields
                    for field in ['sent', 'sent_count', 'total_sent', 'delivered']:
                        if field in campaign and isinstance(campaign[field], (int, float)):
                            sent_count = campaign[field]
                            print(f"  Found sent count in '{field}': {sent_count}")
                            break
                    
                    # Check nested objects
                    if sent_count == 0:
                        for obj_key in ['stats', 'metrics', 'performance', 'campaign_content']:
                            if obj_key in campaign and isinstance(campaign[obj_key], dict):
                                obj_data = campaign[obj_key]
                                for sub_key in ['sent', 'sent_count', 'total_sent', 'delivered']:
                                    if sub_key in obj_data:
                                        sent_count = obj_data[sub_key]
                                        print(f"  Found sent count in '{obj_key}.{sub_key}': {sent_count}")
                                        break
                                if sent_count > 0:
                                    break
                    
                    if sent_count == 0:
                        print(f"  ❌ No sent count found for this campaign")
                    
                    # Classify by country and channel
                    if 'uk' in campaign_name:
                        if 'push' in channel:
                            uk_counts['push'] += sent_count
                        elif 'email' in channel:
                            uk_counts['email'] += sent_count
                    elif 'uae' in campaign_name:
                        if 'push' in channel:
                            uae_counts['push'] += sent_count
                        elif 'email' in channel:
                            uae_counts['email'] += sent_count
                
                print(f"\n📊 AGGREGATED COUNTS:")
                print(f"UK Push: {uk_counts['push']:,}")
                print(f"UK Email: {uk_counts['email']:,}")
                print(f"UAE Push: {uae_counts['push']:,}")
                print(f"UAE Email: {uae_counts['email']:,}")
                
                return campaigns
            else:
                print("❌ No campaigns found in response")
                return []
                
        elif response.status_code == 403:
            print("❌ 403 Forbidden - API not enabled for your account")
            print("💡 Contact MoEngage support to enable Get Campaign Details API")
            return None
        elif response.status_code == 401:
            print("❌ 401 Unauthorized - Authentication issue")
            return None
        elif response.status_code == 400:
            print("❌ 400 Bad Request - Invalid parameters")
            print(f"Response: {response.text}")
            return None
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_individual_campaign_performance():
    """Test getting individual campaign performance data"""
    
    print(f"\n🔍 TESTING INDIVIDUAL CAMPAIGN PERFORMANCE")
    print("=" * 60)
    
    # First get campaigns
    campaigns = test_official_campaign_details_api()
    
    if not campaigns:
        print("❌ No campaigns available for individual testing")
        return None
    
    # Test individual campaign endpoints
    campaign_id = campaigns[0].get('campaign_id')
    if not campaign_id:
        print("❌ No campaign ID found")
        return None
    
    print(f"Testing individual campaign: {campaign_id}")
    
    # Try different individual campaign endpoints
    endpoints = [
        f"/core-services/v1/campaigns/{campaign_id}",
        f"/core-services/v1/campaigns/{campaign_id}/stats",
        f"/core-services/v1/campaigns/{campaign_id}/performance",
        f"/core-services/v1/campaigns/{campaign_id}/metrics"
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
                print(f"✅ SUCCESS! Individual campaign data available")
                
                # Look for performance metrics
                performance_data = {}
                if isinstance(data, dict):
                    for key, value in data.items():
                        if any(word in key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered', 'open', 'click']):
                            performance_data[key] = value
                
                if performance_data:
                    print(f"📊 Performance data found:")
                    for key, value in performance_data.items():
                        if isinstance(value, (int, float)):
                            print(f"  {key}: {value:,}")
                        elif isinstance(value, dict):
                            print(f"  {key}: {list(value.keys())}")
                        else:
                            print(f"  {key}: {type(value)}")
                else:
                    print(f"Available keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                working_endpoints.append(endpoint)
                
            elif response.status_code == 404:
                print("❌ 404 - Endpoint not found")
            elif response.status_code == 403:
                print("❌ 403 - Forbidden")
            else:
                print(f"❌ {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    return working_endpoints

def main():
    """Main test function"""
    
    print("🚀 COMPREHENSIVE OFFICIAL API TESTING")
    print("=" * 80)
    
    # Test main campaign details API
    campaigns = test_official_campaign_details_api()
    
    # Test individual campaign endpoints
    individual_endpoints = test_individual_campaign_performance()
    
    print("\n" + "=" * 80)
    print("📊 FINAL ASSESSMENT:")
    
    if campaigns:
        print(f"✅ Get Campaign Details API: {len(campaigns)} campaigns found")
        
        # Check if we found performance data
        has_performance_data = False
        for campaign in campaigns[:3]:
            for key in campaign.keys():
                if any(word in key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered']):
                    has_performance_data = True
                    break
            if has_performance_data:
                break
        
        if has_performance_data:
            print("✅ Performance data available in campaign objects")
        else:
            print("❌ No performance data in campaign objects")
        
        # Check campaign names
        has_names = False
        for campaign in campaigns[:3]:
            basic_details = campaign.get('basic_details', {})
            if basic_details.get('name'):
                has_names = True
                break
        
        if has_names:
            print("✅ Campaign names available for UK/UAE filtering")
        else:
            print("❌ Campaign names not easily accessible")
    else:
        print("❌ Get Campaign Details API not working")
    
    if individual_endpoints:
        print(f"✅ Individual campaign endpoints: {len(individual_endpoints)} working")
        for endpoint in individual_endpoints:
            print(f"  • {endpoint}")
    else:
        print("❌ No individual campaign endpoints working")
    
    print("\n💡 RECOMMENDATION:")
    if campaigns and has_performance_data:
        print("🎯 EXCELLENT! This API can replace Reports API:")
        print("  1. ✅ Dynamic date ranges via created_date filter")
        print("  2. ✅ Campaign names for UK/UAE filtering")
        print("  3. ✅ Performance data included")
        print("  4. ✅ Real-time data (not fixed like Reports API)")
    elif campaigns:
        print("🔄 PARTIAL replacement possible:")
        print("  1. ✅ Dynamic date ranges")
        print("  2. ✅ Campaign names for filtering")
        print("  3. ❌ Need to find performance data source")
        print("  4. 💡 May need individual campaign endpoints")
    else:
        print("❌ Not suitable as Reports API replacement")
        print("💡 Contact MoEngage support to enable this API")

if __name__ == "__main__":
    main()