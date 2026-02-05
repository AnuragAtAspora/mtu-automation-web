#!/usr/bin/env python3
"""
Extract campaign performance data from MoEngage Campaign Details API
Now that we know the API works, let's extract all useful data
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

def get_all_campaigns_with_filters(start_date=None, end_date=None):
    """Get campaigns with date and channel filters"""
    
    print("🔍 GETTING CAMPAIGNS WITH FILTERS")
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
    
    # Build payload with filters
    payload = {
        "request_id": f"filtered_campaigns_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 15,
        "page": 1,
        "campaign_fields": {
            "channels": ["PUSH", "EMAIL"]  # Filter for Push and Email only
        }
    }
    
    # Add date filter if provided
    if start_date and end_date:
        payload["campaign_fields"]["created_date"] = {
            "from_date": start_date,
            "to_date": end_date
        }
        print(f"📅 Date filter: {start_date} to {end_date}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            campaigns = response.json()
            print(f"✅ Found {len(campaigns)} campaigns")
            return campaigns
        else:
            print(f"❌ Failed: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return []

def analyze_campaign_for_performance_data(campaign):
    """Analyze a single campaign for performance data"""
    
    campaign_id = campaign.get('campaign_id', 'Unknown')
    basic_details = campaign.get('basic_details', {})
    campaign_name = basic_details.get('name', 'Unknown')
    channel = campaign.get('channel', 'Unknown')
    status = campaign.get('status', 'Unknown')
    
    print(f"\n--- CAMPAIGN ANALYSIS ---")
    print(f"ID: {campaign_id}")
    print(f"Name: {campaign_name}")
    print(f"Channel: {channel}")
    print(f"Status: {status}")
    print(f"Created: {campaign.get('created_at', 'Unknown')}")
    print(f"Sent: {campaign.get('sent_time', 'Unknown')}")
    
    # Look for performance data in all nested objects
    performance_data = {}
    
    # Check direct fields
    for key, value in campaign.items():
        if any(word in key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered', 'open', 'click']):
            performance_data[key] = value
    
    # Check nested objects
    nested_objects = ['campaign_content', 'scheduling_details', 'delivery_controls', 'advanced', 'conversion_goal_details']
    
    for obj_key in nested_objects:
        if obj_key in campaign and isinstance(campaign[obj_key], dict):
            obj_data = campaign[obj_key]
            print(f"  Checking {obj_key}: {list(obj_data.keys())}")
            
            # Look for performance data in nested object
            for sub_key, sub_value in obj_data.items():
                if any(word in sub_key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered', 'open', 'click']):
                    performance_data[f"{obj_key}.{sub_key}"] = sub_value
                
                # Check deeper nesting
                if isinstance(sub_value, dict):
                    for deep_key, deep_value in sub_value.items():
                        if any(word in deep_key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered', 'open', 'click']):
                            performance_data[f"{obj_key}.{sub_key}.{deep_key}"] = deep_value
    
    if performance_data:
        print(f"  📊 Performance data found:")
        for key, value in performance_data.items():
            print(f"    {key}: {value}")
    else:
        print(f"  ❌ No performance data found")
    
    return {
        'campaign_id': campaign_id,
        'name': campaign_name,
        'channel': channel,
        'status': status,
        'created_at': campaign.get('created_at'),
        'sent_time': campaign.get('sent_time'),
        'performance_data': performance_data
    }

def test_individual_campaign_stats(campaign_id):
    """Test individual campaign stats endpoints"""
    
    print(f"\n🔍 TESTING INDIVIDUAL CAMPAIGN STATS: {campaign_id}")
    print("=" * 60)
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key']
    }
    
    # Try different individual campaign endpoints
    endpoints = [
        f"/core-services/v1/campaigns/{campaign_id}",
        f"/core-services/v1/campaigns/{campaign_id}/stats",
        f"/core-services/v1/campaigns/{campaign_id}/performance",
        f"/core-services/v1/campaigns/{campaign_id}/metrics",
        f"/core-services/v1/campaigns/{campaign_id}/analytics",
        f"/v1/campaigns/{campaign_id}/stats",
        f"/campaign_reports/v1/campaigns/{campaign_id}/stats"
    ]
    
    working_data = {}
    
    for endpoint in endpoints:
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
        print(f"Testing: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ SUCCESS! Data available")
                
                # Look for performance metrics
                performance_metrics = {}
                if isinstance(data, dict):
                    for key, value in data.items():
                        if any(word in key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered', 'open', 'click', 'conversion']):
                            performance_metrics[key] = value
                
                if performance_metrics:
                    print(f"  📊 Performance metrics found:")
                    for key, value in performance_metrics.items():
                        if isinstance(value, (int, float)):
                            print(f"    {key}: {value:,}")
                        else:
                            print(f"    {key}: {type(value)}")
                    working_data[endpoint] = performance_metrics
                else:
                    print(f"  📋 Available keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    working_data[endpoint] = data
                
            elif response.status_code == 404:
                print(f"  ❌ 404 - Not found")
            elif response.status_code == 403:
                print(f"  ❌ 403 - Forbidden")
            else:
                print(f"  ❌ {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
    
    return working_data

def extract_communication_counts_by_country(campaigns):
    """Extract communication counts by country from campaign data"""
    
    print(f"\n📊 EXTRACTING COMMUNICATION COUNTS BY COUNTRY")
    print("=" * 60)
    
    # Initialize counters
    counts = {
        'uk': {'push': 0, 'email': 0, 'campaigns': []},
        'uae': {'push': 0, 'email': 0, 'campaigns': []},
        'other': {'push': 0, 'email': 0, 'campaigns': []}
    }
    
    for campaign in campaigns:
        basic_details = campaign.get('basic_details', {})
        campaign_name = basic_details.get('name', '').lower()
        channel = campaign.get('channel', '').lower()
        status = campaign.get('status', '')
        
        # Only count sent campaigns
        if status.lower() != 'sent':
            continue
        
        print(f"Campaign: {campaign_name} | Channel: {channel} | Status: {status}")
        
        # Determine country
        country = 'other'
        if 'uk' in campaign_name:
            country = 'uk'
        elif 'uae' in campaign_name:
            country = 'uae'
        
        # Determine channel type
        channel_type = 'other'
        if 'push' in channel:
            channel_type = 'push'
        elif 'email' in channel:
            channel_type = 'email'
        
        if country in counts and channel_type in counts[country]:
            # For now, count campaigns (we'll need individual stats for actual sent counts)
            counts[country][channel_type] += 1
            counts[country]['campaigns'].append({
                'name': campaign_name,
                'channel': channel,
                'id': campaign.get('campaign_id'),
                'sent_time': campaign.get('sent_time')
            })
            print(f"  → Counted as {country} {channel_type}")
        else:
            print(f"  → Unclassified: {country} {channel_type}")
    
    print(f"\n📈 CAMPAIGN COUNTS BY COUNTRY:")
    for country, data in counts.items():
        if data['push'] > 0 or data['email'] > 0:
            print(f"{country.upper()}:")
            print(f"  Push campaigns: {data['push']}")
            print(f"  Email campaigns: {data['email']}")
            print(f"  Total campaigns: {len(data['campaigns'])}")
    
    return counts

def main():
    """Main analysis function"""
    
    print("🚀 COMPREHENSIVE CAMPAIGN PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    # Get campaigns with filters
    campaigns = get_all_campaigns_with_filters()
    
    if not campaigns:
        print("❌ No campaigns found")
        return
    
    # Analyze each campaign for performance data
    campaign_analyses = []
    for i, campaign in enumerate(campaigns[:5]):  # Analyze first 5 campaigns
        analysis = analyze_campaign_for_performance_data(campaign)
        campaign_analyses.append(analysis)
        
        # Test individual campaign stats for first campaign
        if i == 0:
            individual_stats = test_individual_campaign_stats(campaign.get('campaign_id'))
            analysis['individual_stats'] = individual_stats
    
    # Extract communication counts by country
    country_counts = extract_communication_counts_by_country(campaigns)
    
    print(f"\n" + "=" * 80)
    print("📊 FINAL ASSESSMENT:")
    
    # Check if we found any performance data
    has_performance_data = any(analysis['performance_data'] for analysis in campaign_analyses)
    has_individual_stats = any(analysis.get('individual_stats') for analysis in campaign_analyses)
    
    if has_performance_data:
        print("✅ Performance data found in campaign objects")
    else:
        print("❌ No performance data in campaign objects")
    
    if has_individual_stats:
        print("✅ Individual campaign stats endpoints working")
    else:
        print("❌ No individual campaign stats endpoints working")
    
    # Check if we can filter by country
    has_country_campaigns = country_counts['uk']['push'] > 0 or country_counts['uk']['email'] > 0 or country_counts['uae']['push'] > 0 or country_counts['uae']['email'] > 0
    
    if has_country_campaigns:
        print("✅ Can filter campaigns by UK/UAE in campaign names")
    else:
        print("❌ No UK/UAE campaigns found in names")
    
    print(f"\n💡 RECOMMENDATION:")
    if has_performance_data or has_individual_stats:
        print("🎯 This API can potentially replace Reports API!")
        print("  ✅ Dynamic date filtering available")
        print("  ✅ Campaign names available for country filtering")
        if has_performance_data:
            print("  ✅ Performance data in campaign objects")
        if has_individual_stats:
            print("  ✅ Individual campaign stats endpoints available")
        print("  🔧 Next: Implement full integration with sent count extraction")
    else:
        print("🔄 Partial replacement possible:")
        print("  ✅ Can get campaign lists with date filtering")
        print("  ✅ Can filter by country using campaign names")
        print("  ❌ Need to find performance data source")
        print("  💡 May need to contact MoEngage for performance API access")

if __name__ == "__main__":
    main()