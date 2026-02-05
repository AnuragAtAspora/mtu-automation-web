#!/usr/bin/env python3
"""
Deep dive into campaign data structure to find hidden performance metrics
Look for nested data, alternative fields, and creative extraction methods
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

def get_detailed_campaign_data():
    """Get campaigns with maximum detail and analyze every field"""
    
    print("🔍 GETTING DETAILED CAMPAIGN DATA")
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
    
    # Request with all possible fields to get maximum data
    payload = {
        "request_id": f"detailed_campaigns_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 5,
        "page": 1,
        "campaign_fields": {
            "channels": ["PUSH", "EMAIL"]
        },
        "include_child_campaigns": True,
        "include_archive_campaigns": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
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

def deep_analyze_campaign_structure(campaign, depth=0, path=""):
    """Recursively analyze campaign structure to find any performance data"""
    
    indent = "  " * depth
    found_metrics = []
    
    if isinstance(campaign, dict):
        for key, value in campaign.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check if this key might contain performance data
            performance_keywords = ['sent', 'delivered', 'open', 'click', 'conversion', 'bounce', 'unsubscribe', 'stat', 'metric', 'performance', 'count', 'total', 'analytics']
            
            if any(keyword in key.lower() for keyword in performance_keywords):
                if isinstance(value, (int, float)) and value > 0:
                    found_metrics.append({
                        'path': current_path,
                        'key': key,
                        'value': value,
                        'type': type(value).__name__
                    })
                    print(f"{indent}🎯 POTENTIAL METRIC: {current_path} = {value}")
                elif isinstance(value, dict):
                    print(f"{indent}📊 PERFORMANCE OBJECT: {current_path}")
                    nested_metrics = deep_analyze_campaign_structure(value, depth + 1, current_path)
                    found_metrics.extend(nested_metrics)
                elif isinstance(value, list) and value:
                    print(f"{indent}📋 PERFORMANCE LIST: {current_path} ({len(value)} items)")
                    for i, item in enumerate(value[:3]):  # Check first 3 items
                        item_metrics = deep_analyze_campaign_structure(item, depth + 1, f"{current_path}[{i}]")
                        found_metrics.extend(item_metrics)
                else:
                    print(f"{indent}📄 PERFORMANCE FIELD: {current_path} = {value}")
            
            # Recursively check nested objects and arrays
            elif isinstance(value, dict):
                nested_metrics = deep_analyze_campaign_structure(value, depth + 1, current_path)
                found_metrics.extend(nested_metrics)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                for i, item in enumerate(value[:2]):  # Check first 2 items
                    item_metrics = deep_analyze_campaign_structure(item, depth + 1, f"{current_path}[{i}]")
                    found_metrics.extend(item_metrics)
    
    return found_metrics

def analyze_campaign_content_for_metrics(campaign):
    """Specifically analyze campaign_content for hidden performance data"""
    
    print(f"\n🔍 DEEP ANALYSIS OF CAMPAIGN CONTENT")
    print("=" * 50)
    
    campaign_content = campaign.get('campaign_content', {})
    if not campaign_content:
        print("❌ No campaign_content found")
        return []
    
    print(f"Campaign content keys: {list(campaign_content.keys())}")
    
    found_metrics = []
    
    # Check content structure
    content = campaign_content.get('content', {})
    if content:
        print(f"Content locales: {list(content.keys())}")
        
        for locale, locale_data in content.items():
            print(f"\nLocale: {locale}")
            if isinstance(locale_data, dict):
                for variation, variation_data in locale_data.items():
                    print(f"  Variation: {variation}")
                    if isinstance(variation_data, dict):
                        # Look for channel-specific data
                        for channel, channel_data in variation_data.items():
                            print(f"    Channel: {channel}")
                            if isinstance(channel_data, dict):
                                print(f"      Keys: {list(channel_data.keys())}")
                                
                                # Look for any numeric values that might be metrics
                                for key, value in channel_data.items():
                                    if isinstance(value, (int, float)) and value > 0:
                                        found_metrics.append({
                                            'path': f"campaign_content.content.{locale}.{variation}.{channel}.{key}",
                                            'key': key,
                                            'value': value,
                                            'context': f"{locale}/{variation}/{channel}"
                                        })
                                        print(f"        🎯 METRIC: {key} = {value}")
    
    return found_metrics

def analyze_scheduling_details_for_metrics(campaign):
    """Analyze scheduling details for performance data"""
    
    print(f"\n🔍 ANALYZING SCHEDULING DETAILS")
    print("=" * 50)
    
    scheduling_details = campaign.get('scheduling_details', {})
    if not scheduling_details:
        print("❌ No scheduling_details found")
        return []
    
    print(f"Scheduling details keys: {list(scheduling_details.keys())}")
    
    found_metrics = []
    
    # Look for any performance-related data in scheduling
    for key, value in scheduling_details.items():
        if isinstance(value, (int, float)) and value > 0:
            found_metrics.append({
                'path': f"scheduling_details.{key}",
                'key': key,
                'value': value,
                'context': 'scheduling'
            })
            print(f"🎯 SCHEDULING METRIC: {key} = {value}")
        elif isinstance(value, dict):
            print(f"Scheduling object: {key}")
            nested_metrics = deep_analyze_campaign_structure(value, 1, f"scheduling_details.{key}")
            found_metrics.extend(nested_metrics)
    
    return found_metrics

def test_campaign_with_different_parameters():
    """Test if different request parameters reveal more data"""
    
    print(f"\n🔍 TESTING DIFFERENT REQUEST PARAMETERS")
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
    
    # Try different parameter combinations
    test_payloads = [
        {
            "name": "Include performance data",
            "payload": {
                "request_id": f"perf_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "limit": 3,
                "page": 1,
                "campaign_fields": {
                    "channels": ["PUSH", "EMAIL"],
                    "include_performance": True,  # Try this parameter
                    "include_stats": True,        # Try this parameter
                    "include_analytics": True     # Try this parameter
                },
                "include_child_campaigns": True,
                "include_archive_campaigns": False
            }
        },
        {
            "name": "Request with stats fields",
            "payload": {
                "request_id": f"stats_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "limit": 3,
                "page": 1,
                "campaign_fields": {
                    "channels": ["PUSH", "EMAIL"],
                    "fields": ["stats", "performance", "analytics", "metrics"]  # Try requesting specific fields
                },
                "include_child_campaigns": True
            }
        },
        {
            "name": "Detailed response format",
            "payload": {
                "request_id": f"detailed_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "limit": 3,
                "page": 1,
                "response_format": "detailed",  # Try this parameter
                "include_performance_data": True,  # Try this parameter
                "campaign_fields": {
                    "channels": ["PUSH", "EMAIL"]
                }
            }
        }
    ]
    
    for test in test_payloads:
        print(f"\n--- Testing: {test['name']} ---")
        
        try:
            response = requests.post(url, json=test['payload'], headers=headers, timeout=30)
            
            if response.status_code == 200:
                campaigns = response.json()
                print(f"✅ Success: {len(campaigns)} campaigns")
                
                if campaigns:
                    # Check if we got different/additional data
                    sample_campaign = campaigns[0]
                    keys = list(sample_campaign.keys())
                    print(f"Available keys: {keys}")
                    
                    # Look for new performance-related keys
                    performance_keys = [key for key in keys if any(word in key.lower() for word in ['stat', 'metric', 'performance', 'analytics'])]
                    if performance_keys:
                        print(f"🎯 Performance keys found: {performance_keys}")
                        for key in performance_keys:
                            print(f"  {key}: {sample_campaign[key]}")
                    else:
                        print("❌ No new performance keys found")
                        
            elif response.status_code == 400:
                error_data = response.json()
                print(f"❌ Bad Request: {error_data.get('error', {}).get('message', 'Unknown error')}")
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def estimate_performance_from_campaign_data(campaigns):
    """Try to estimate performance metrics from available campaign data"""
    
    print(f"\n🔍 ESTIMATING PERFORMANCE FROM AVAILABLE DATA")
    print("=" * 50)
    
    estimates = {
        'uk': {'push': 0, 'email': 0},
        'uae': {'push': 0, 'email': 0}
    }
    
    for campaign in campaigns:
        basic_details = campaign.get('basic_details', {})
        name = basic_details.get('name', '').lower()
        channel = campaign.get('channel', '').lower()
        status = campaign.get('status', '')
        
        if status.lower() != 'sent':
            continue
        
        print(f"\nCampaign: {name}")
        print(f"Channel: {channel}")
        
        # Look for any numeric indicators in the campaign data
        segmentation_details = campaign.get('segmentation_details', {})
        
        # Check if it's an "all user" campaign
        is_all_user = segmentation_details.get('is_all_user_campaign', False)
        print(f"All user campaign: {is_all_user}")
        
        # Analyze filters to estimate audience size
        included_filters = segmentation_details.get('included_filters', {})
        excluded_filters = segmentation_details.get('excluded_filters', {})
        
        print(f"Has included filters: {bool(included_filters)}")
        print(f"Has excluded filters: {bool(excluded_filters)}")
        
        # Look for platform details that might indicate reach
        platforms = basic_details.get('platforms', [])
        platform_details = basic_details.get('platform_specific_details', {})
        
        print(f"Platforms: {platforms}")
        if platform_details:
            print(f"Platform details: {list(platform_details.keys())}")
        
        # Try to estimate based on campaign type and targeting
        estimated_reach = 0
        
        if is_all_user:
            # All user campaigns likely have higher reach
            if 'uk' in name:
                estimated_reach = 50000  # Estimate for UK all-user campaigns
            elif 'uae' in name:
                estimated_reach = 30000  # Estimate for UAE all-user campaigns
        else:
            # Targeted campaigns likely have lower reach
            if 'inactive' in name or 'churned' in name:
                estimated_reach = 5000   # Estimate for reactivation campaigns
            elif 'rate' in name or 'payday' in name:
                estimated_reach = 15000  # Estimate for promotional campaigns
            else:
                estimated_reach = 10000  # Default estimate
        
        print(f"Estimated reach: {estimated_reach:,}")
        
        # Classify by country and channel
        country = 'other'
        if 'uk' in name:
            country = 'uk'
        elif 'uae' in name:
            country = 'uae'
        
        channel_type = 'other'
        if 'push' in channel:
            channel_type = 'push'
        elif 'email' in channel:
            channel_type = 'email'
        
        if country in estimates and channel_type in estimates[country]:
            estimates[country][channel_type] += estimated_reach
    
    print(f"\n📊 ESTIMATED COMMUNICATION COUNTS:")
    for country, channels in estimates.items():
        if channels['push'] > 0 or channels['email'] > 0:
            print(f"{country.upper()}:")
            print(f"  Push: {channels['push']:,}")
            print(f"  Email: {channels['email']:,}")
    
    return estimates

def main():
    """Main function for deep campaign data analysis"""
    
    print("🚀 DEEP CAMPAIGN DATA EXTRACTION")
    print("=" * 80)
    
    # Get detailed campaign data
    campaigns = get_detailed_campaign_data()
    
    if not campaigns:
        print("❌ No campaigns available for analysis")
        return
    
    all_found_metrics = []
    
    # Analyze each campaign in detail
    for i, campaign in enumerate(campaigns[:3]):  # Analyze first 3 campaigns
        basic_details = campaign.get('basic_details', {})
        campaign_name = basic_details.get('name', f'Campaign {i+1}')
        
        print(f"\n" + "="*60)
        print(f"🎯 DEEP ANALYSIS: {campaign_name}")
        print("="*60)
        
        # Deep structure analysis
        print(f"\n1. COMPLETE STRUCTURE ANALYSIS:")
        structure_metrics = deep_analyze_campaign_structure(campaign)
        all_found_metrics.extend(structure_metrics)
        
        # Campaign content analysis
        content_metrics = analyze_campaign_content_for_metrics(campaign)
        all_found_metrics.extend(content_metrics)
        
        # Scheduling details analysis
        scheduling_metrics = analyze_scheduling_details_for_metrics(campaign)
        all_found_metrics.extend(scheduling_metrics)
    
    # Test different request parameters
    test_campaign_with_different_parameters()
    
    # Estimate performance from available data
    estimates = estimate_performance_from_campaign_data(campaigns)
    
    print(f"\n" + "="*80)
    print("📊 FINAL ANALYSIS RESULTS")
    print("="*80)
    
    if all_found_metrics:
        print(f"✅ FOUND {len(all_found_metrics)} POTENTIAL METRICS!")
        
        # Group metrics by type
        metric_types = {}
        for metric in all_found_metrics:
            key = metric['key'].lower()
            if key not in metric_types:
                metric_types[key] = []
            metric_types[key].append(metric)
        
        print(f"\n📊 METRICS BY TYPE:")
        for metric_type, metrics in metric_types.items():
            print(f"  {metric_type}: {len(metrics)} occurrences")
            for metric in metrics[:3]:  # Show first 3 examples
                print(f"    • {metric['path']} = {metric['value']}")
        
        # Check if any metrics look like sent counts
        sent_like_metrics = [m for m in all_found_metrics if any(word in m['key'].lower() for word in ['sent', 'delivered', 'total', 'count'])]
        if sent_like_metrics:
            print(f"\n🎯 POTENTIAL SENT COUNT METRICS:")
            for metric in sent_like_metrics:
                print(f"  • {metric['path']} = {metric['value']}")
    else:
        print("❌ NO PERFORMANCE METRICS FOUND IN CAMPAIGN DATA")
    
    print(f"\n💡 RECOMMENDATIONS:")
    if all_found_metrics:
        print("🔍 INVESTIGATE FOUND METRICS:")
        print("  1. Test if found metrics correlate with actual campaign performance")
        print("  2. Validate metrics against MoEngage dashboard")
        print("  3. Implement extraction of most promising metrics")
    else:
        print("🎯 ALTERNATIVE APPROACHES:")
        print("  1. Use estimated reach based on campaign targeting")
        print("  2. Implement campaign count approach as proxy")
        print("  3. Contact MoEngage support for performance API access")
        print("  4. Wait for Stats API enablement")
    
    print(f"\n📈 ESTIMATED PERFORMANCE (if no metrics found):")
    for country, channels in estimates.items():
        if channels['push'] > 0 or channels['email'] > 0:
            print(f"  {country.upper()}: Push {channels['push']:,}, Email {channels['email']:,}")

if __name__ == "__main__":
    main()