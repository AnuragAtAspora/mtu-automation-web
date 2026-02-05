#!/usr/bin/env python3
"""
Test Stats API with individual campaign IDs to get performance metrics
This might work even if the general Stats API is not enabled
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

def get_recent_sent_campaigns():
    """Get recent sent campaigns to test individual stats"""
    
    print("🔍 GETTING RECENT SENT CAMPAIGNS")
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
        "request_id": f"sent_campaigns_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 10,
        "page": 1,
        "campaign_fields": {
            "channels": ["PUSH", "EMAIL"],
            "created_date": {
                "from_date": "2026-02-01",
                "to_date": "2026-02-28"
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            campaigns = response.json()
            
            # Filter for sent campaigns only
            sent_campaigns = []
            for campaign in campaigns:
                if campaign.get('status', '').lower() == 'sent':
                    basic_details = campaign.get('basic_details', {})
                    sent_campaigns.append({
                        'id': campaign.get('campaign_id'),
                        'name': basic_details.get('name', 'Unknown'),
                        'channel': campaign.get('channel'),
                        'status': campaign.get('status'),
                        'sent_time': campaign.get('sent_time'),
                        'created_at': campaign.get('created_at')
                    })
            
            print(f"✅ Found {len(sent_campaigns)} sent campaigns")
            for campaign in sent_campaigns[:5]:
                print(f"  • {campaign['name']} | {campaign['channel']} | {campaign['sent_time']}")
            
            return sent_campaigns
        else:
            print(f"❌ Failed: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return []

def test_stats_api_with_campaign_ids(campaign_ids):
    """Test Stats API with specific campaign IDs"""
    
    print(f"\n🔍 TESTING STATS API WITH SPECIFIC CAMPAIGN IDS")
    print("=" * 60)
    
    stats_url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaign-stats"
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key']
    }
    
    # Test with specific campaign IDs
    payload = {
        'request_id': f"individual_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'start_date': '2026-02-01',
        'end_date': '2026-02-28',
        'attribution_type': 'TOTAL_CONVERSIONS',
        'metric_type': 'TOTAL',
        'campaign_ids': campaign_ids[:5],  # Test with first 5 campaigns
        'offset': 0,
        'limit': 10
    }
    
    try:
        print(f"📡 Testing Stats API with campaign IDs: {campaign_ids[:5]}")
        response = requests.post(stats_url, json=payload, headers=headers, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Stats API returned data for individual campaigns")
            print(f"Response keys: {list(data.keys())}")
            
            # Look for campaign-specific data
            campaign_data = data.get('data', {})
            if campaign_data:
                print(f"📊 Campaign data found for {len(campaign_data)} campaigns")
                
                for campaign_id, stats_list in campaign_data.items():
                    print(f"\nCampaign ID: {campaign_id}")
                    for stats in stats_list:
                        campaign_name = stats.get('campaign_name', 'Unknown')
                        print(f"  Name: {campaign_name}")
                        
                        # Look for performance metrics
                        platforms = stats.get('platforms', {})
                        for platform_name, platform_data in platforms.items():
                            print(f"    Platform: {platform_name}")
                            
                            locales = platform_data.get('locales', {})
                            for locale_name, locale_data in locales.items():
                                variations = locale_data.get('variations', {})
                                all_variations = variations.get('all_variations', {})
                                performance_stats = all_variations.get('performance_stats', {})
                                
                                if performance_stats:
                                    print(f"      📊 Performance stats found:")
                                    for metric, value in performance_stats.items():
                                        if isinstance(value, (int, float)):
                                            print(f"        {metric}: {value:,}")
                
                return data
            else:
                print(f"❌ No campaign data in response")
                return None
                
        elif response.status_code == 403:
            print(f"❌ 403 Forbidden - Stats API not enabled")
            return None
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_alternative_stats_endpoints(campaign_ids):
    """Test alternative stats endpoints with campaign IDs"""
    
    print(f"\n🔍 TESTING ALTERNATIVE STATS ENDPOINTS")
    print("=" * 60)
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key']
    }
    
    # Alternative stats endpoints to test
    stats_endpoints = [
        "/core-services/v1/stats",
        "/core-services/v1/analytics",
        "/core-services/v1/performance",
        "/core-services/v1/metrics",
        "/v1/campaign-stats",
        "/v1/stats",
        "/v1/analytics",
        "/analytics/v1/campaigns",
        "/stats/v1/campaigns",
        "/performance/v1/campaigns"
    ]
    
    working_endpoints = []
    
    for endpoint in stats_endpoints:
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
        
        payload = {
            'request_id': f"alt_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_date': '2026-02-01',
            'end_date': '2026-02-28',
            'campaign_ids': campaign_ids[:3]  # Test with first 3 campaigns
        }
        
        try:
            print(f"Testing: {endpoint}")
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: {endpoint}")
                try:
                    data = response.json()
                    print(f"  📊 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    working_endpoints.append({'endpoint': endpoint, 'data': data})
                except:
                    print(f"  📄 Non-JSON response")
                    working_endpoints.append({'endpoint': endpoint, 'data': response.text})
                    
            elif response.status_code == 404:
                pass  # Expected
            elif response.status_code == 403:
                print(f"  🔒 403 Forbidden")
            elif response.status_code == 401:
                print(f"  🔑 401 Unauthorized")
            else:
                print(f"  ❓ {response.status_code}")
                
        except Exception as e:
            pass  # Skip connection errors
    
    return working_endpoints

def test_campaign_meta_api(campaign_ids):
    """Test Campaign Meta and Reachability API for performance data"""
    
    print(f"\n🔍 TESTING CAMPAIGN META AND REACHABILITY API")
    print("=" * 60)
    
    # Based on search results, there's a "Campaign Meta and Reachability API"
    meta_url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/meta"
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key']
    }
    
    # Test different payloads for meta API
    test_payloads = [
        {
            "name": "Campaign meta with IDs",
            "payload": {
                "request_id": f"meta_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "campaign_ids": campaign_ids[:5]
            }
        },
        {
            "name": "Campaign reachability",
            "payload": {
                "request_id": f"reach_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "campaign_ids": campaign_ids[:5],
                "include_reachability": True
            }
        },
        {
            "name": "Campaign performance meta",
            "payload": {
                "request_id": f"perf_meta_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "campaign_ids": campaign_ids[:5],
                "include_performance": True,
                "include_stats": True
            }
        }
    ]
    
    working_responses = []
    
    for test in test_payloads:
        print(f"\n--- Testing: {test['name']} ---")
        
        try:
            response = requests.post(meta_url, json=test['payload'], headers=headers, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS!")
                try:
                    data = response.json()
                    print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    # Look for performance data
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if any(word in key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered']):
                                print(f"  📊 Performance key found: {key}")
                                if isinstance(value, dict):
                                    print(f"    Subkeys: {list(value.keys())}")
                    
                    working_responses.append({'test': test['name'], 'data': data})
                except:
                    print(f"Non-JSON response")
                    working_responses.append({'test': test['name'], 'data': response.text})
                    
            elif response.status_code == 404:
                print(f"❌ 404 - Endpoint not found")
            elif response.status_code == 403:
                print(f"🔒 403 - Forbidden")
            elif response.status_code == 400:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                print(f"❌ 400 - Bad Request: {error_data}")
            else:
                print(f"❓ {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    return working_responses

def main():
    """Main function to test individual campaign performance approaches"""
    
    print("🚀 INDIVIDUAL CAMPAIGN PERFORMANCE TESTING")
    print("=" * 80)
    
    # Get recent sent campaigns
    sent_campaigns = get_recent_sent_campaigns()
    
    if not sent_campaigns:
        print("❌ No sent campaigns available for testing")
        return
    
    campaign_ids = [campaign['id'] for campaign in sent_campaigns]
    print(f"\nTesting with {len(campaign_ids)} campaign IDs")
    
    # Test 1: Stats API with specific campaign IDs
    stats_result = test_stats_api_with_campaign_ids(campaign_ids)
    
    # Test 2: Alternative stats endpoints
    alt_stats = test_alternative_stats_endpoints(campaign_ids)
    
    # Test 3: Campaign Meta API
    meta_results = test_campaign_meta_api(campaign_ids)
    
    print(f"\n" + "="*80)
    print("📊 FINAL RESULTS")
    print("="*80)
    
    success_count = 0
    
    if stats_result:
        print("✅ Stats API with campaign IDs: SUCCESS")
        success_count += 1
    else:
        print("❌ Stats API with campaign IDs: FAILED")
    
    if alt_stats:
        print(f"✅ Alternative stats endpoints: {len(alt_stats)} working")
        for endpoint_info in alt_stats:
            print(f"  • {endpoint_info['endpoint']}")
        success_count += len(alt_stats)
    else:
        print("❌ Alternative stats endpoints: NONE WORKING")
    
    if meta_results:
        print(f"✅ Campaign Meta API: {len(meta_results)} working responses")
        for result in meta_results:
            print(f"  • {result['test']}")
        success_count += len(meta_results)
    else:
        print("❌ Campaign Meta API: FAILED")
    
    print(f"\n💡 FINAL RECOMMENDATION:")
    if success_count > 0:
        print("🎯 PERFORMANCE DATA SOURCES FOUND!")
        print("  1. Implement working endpoints for performance metrics")
        print("  2. Extract sent/delivered counts from successful responses")
        print("  3. Integrate with Campaign Details API for complete solution")
    else:
        print("❌ NO INDIVIDUAL CAMPAIGN PERFORMANCE SOURCES FOUND")
        print("🔄 FALLBACK APPROACHES:")
        print("  1. Implement Campaign Details API with campaign counts")
        print("  2. Use estimated reach based on campaign targeting")
        print("  3. Contact MoEngage support for performance API access")
        print("  4. Wait for Stats API general enablement")

if __name__ == "__main__":
    main()