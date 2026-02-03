#!/usr/bin/env python3
"""
MoEngage Stats API implementation based on official documentation
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

class MoEngageStatsAPI:
    def __init__(self):
        self.base_url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaign-stats"
        
    def get_campaign_stats(self, start_date, end_date, campaign_ids=None, attribution_type="TOTAL_CONVERSIONS", metric_type="TOTAL"):
        """
        Get campaign statistics using MoEngage Stats API
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format (max 30 days range)
            campaign_ids (list): Optional list of campaign IDs (max 10)
            attribution_type (str): VIEW_THROUGH, CLICK_THROUGH, IN_SESSION, TOTAL_CONVERSIONS, CLICK_CONVERSIONS
            metric_type (str): TOTAL or UNIQUE
        """
        
        # Authentication using Campaign API credentials (as per documentation)
        auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {encoded_auth}',
            'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id']
        }
        
        # Request payload
        payload = {
            'request_id': f"comms_per_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_date': start_date,
            'end_date': end_date,
            'attribution_type': attribution_type,
            'metric_type': metric_type,
            'offset': 0,
            'limit': 10
        }
        
        # Add campaign IDs if provided
        if campaign_ids:
            payload['campaign_ids'] = campaign_ids[:10]  # Max 10 as per documentation
        
        try:
            print(f"📡 Calling Stats API: {start_date} to {end_date}")
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=60)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Stats API Success!")
                print(f"Total campaigns: {data.get('total_campaigns', 0)}")
                return data
            elif response.status_code == 403:
                print(f"❌ Stats API not enabled for your account")
                print(f"Contact MoEngage support to enable Stats API access")
                return {'error': 'Stats API not enabled'}
            else:
                print(f"❌ Stats API Error: {response.text}")
                return {'error': f"API Error: {response.status_code} - {response.text}"}
                
        except Exception as e:
            print(f"❌ Stats API Exception: {str(e)}")
            return {'error': f"Exception: {str(e)}"}
    
    def extract_communication_counts(self, stats_data, start_date, end_date):
        """
        Extract communication counts by country and type from Stats API response
        """
        
        if 'error' in stats_data:
            return stats_data
        
        # Initialize counters
        results = {
            'uk_transactional_pn': 0,
            'uk_transactional_email': 0,
            'uk_promotional_pn': 0,
            'uk_promotional_email': 0,
            'uae_transactional_pn': 0,
            'uae_transactional_email': 0,
            'uae_promotional_pn': 0,
            'uae_promotional_email': 0,
            'period': f"{start_date} to {end_date}",
            'total_campaigns_analyzed': stats_data.get('total_campaigns', 0)
        }
        
        # Parse campaign data
        campaign_data = stats_data.get('data', {})
        
        for campaign_id, campaign_stats_list in campaign_data.items():
            for campaign_stats in campaign_stats_list:
                
                # Extract campaign name (we'll need to get this from campaign details)
                # For now, we'll aggregate all stats by platform type
                
                platforms = campaign_stats.get('platforms', {})
                
                for platform_name, platform_data in platforms.items():
                    locales = platform_data.get('locales', {})
                    
                    for locale_name, locale_data in locales.items():
                        variations = locale_data.get('variations', {})
                        all_variations = variations.get('all_variations', {})
                        performance_stats = all_variations.get('performance_stats', {})
                        
                        sent_count = performance_stats.get('sent', 0)
                        
                        # Determine communication type based on platform
                        if platform_name.lower() in ['android', 'ios', 'web', 'mweb']:
                            # This is push notification
                            # We need campaign name to determine country and type (transactional vs promotional)
                            # For now, we'll need to make additional API calls to get campaign details
                            pass
                        elif platform_name.lower() == 'email':
                            # This is email
                            pass
        
        return results
    
    def get_campaign_details_for_stats(self, campaign_ids):
        """
        Get campaign details to determine campaign names and types
        This is needed to classify campaigns by country and type
        """
        
        # Use Campaign Search API to get campaign details
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/search"
        
        auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
            'Content-Type': 'application/json'
        }
        
        payload = {
            "filters": {
                "campaign_ids": campaign_ids
            },
            "page_size": len(campaign_ids)
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Campaign Details Error: {response.text}")
                return {'error': f"Campaign Details Error: {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Campaign Details Exception: {str(e)}")
            return {'error': f"Exception: {str(e)}"}

def test_stats_api():
    """Test the Stats API implementation"""
    
    print("🧪 TESTING MOENGAGE STATS API")
    print("=" * 50)
    
    stats_api = MoEngageStatsAPI()
    
    # Test with January 2026 date range
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    # Get campaign stats
    stats_data = stats_api.get_campaign_stats(start_date, end_date)
    
    if 'error' not in stats_data:
        print(f"📊 Stats API Response Structure:")
        print(f"Response ID: {stats_data.get('response_id')}")
        print(f"Total Campaigns: {stats_data.get('total_campaigns')}")
        print(f"Current Page: {stats_data.get('current_page')}")
        print(f"Total Pages: {stats_data.get('total_pages')}")
        
        # Show sample campaign data structure
        campaign_data = stats_data.get('data', {})
        if campaign_data:
            print(f"\nSample Campaign IDs: {list(campaign_data.keys())[:3]}")
            
            # Extract communication counts
            results = stats_api.extract_communication_counts(stats_data, start_date, end_date)
            print(f"\n📈 Extracted Results:")
            for key, value in results.items():
                print(f"  {key}: {value}")
        
        return stats_data
    else:
        print(f"❌ Stats API failed: {stats_data['error']}")
        return None

if __name__ == "__main__":
    test_stats_api()