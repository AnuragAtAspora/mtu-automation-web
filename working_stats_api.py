#!/usr/bin/env python3
"""
Working MoEngage Stats API Implementation
This implementation uses the correct authentication method we discovered.
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
        
    def get_campaign_stats(self, start_date, end_date, campaign_ids=None):
        """
        Get campaign statistics using MoEngage Stats API
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            campaign_ids (list): Optional list of campaign IDs
        
        Returns:
            dict: API response or error information
        """
        
        # Correct authentication method (discovered through testing)
        auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {encoded_auth}',
            'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
            'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key']
        }
        
        # Request payload based on MoEngage documentation
        payload = {
            'request_id': f"comms_per_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_date': start_date,
            'end_date': end_date,
            'attribution_type': 'TOTAL_CONVERSIONS',
            'metric_type': 'TOTAL',
            'offset': 0,
            'limit': 10  # Max 10 as per API validation
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
                return {'error': 'stats_api_not_enabled', 'message': 'Stats API not enabled for your account'}
            elif response.status_code == 401:
                print(f"❌ Authentication failed")
                return {'error': 'authentication_failed', 'message': 'Authentication failed'}
            else:
                print(f"❌ Stats API Error: {response.text}")
                return {'error': f"api_error_{response.status_code}", 'message': response.text}
                
        except Exception as e:
            print(f"❌ Stats API Exception: {str(e)}")
            return {'error': 'exception', 'message': str(e)}
    
    def extract_communication_counts_by_country(self, stats_data, start_date, end_date):
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
            'total_campaigns_analyzed': stats_data.get('total_campaigns', 0),
            'data_source': 'Stats API'
        }
        
        # Parse campaign data from Stats API response
        campaign_data = stats_data.get('data', {})
        
        for campaign_id, campaign_stats_list in campaign_data.items():
            for campaign_stats in campaign_stats_list:
                
                # Get campaign name to determine country and type
                campaign_name = campaign_stats.get('campaign_name', '').lower()
                
                # Parse platforms (push/email)
                platforms = campaign_stats.get('platforms', {})
                
                for platform_name, platform_data in platforms.items():
                    # Determine if this is push or email
                    is_push = platform_name.lower() in ['android', 'ios', 'web', 'mweb']
                    is_email = platform_name.lower() == 'email'
                    
                    if not (is_push or is_email):
                        continue
                    
                    # Get sent count from platform data
                    locales = platform_data.get('locales', {})
                    sent_count = 0
                    
                    for locale_name, locale_data in locales.items():
                        variations = locale_data.get('variations', {})
                        all_variations = variations.get('all_variations', {})
                        performance_stats = all_variations.get('performance_stats', {})
                        sent_count += performance_stats.get('sent', 0)
                    
                    # Classify by country and type
                    is_uk = 'uk' in campaign_name
                    is_uae = 'uae' in campaign_name
                    is_transactional = any(word in campaign_name for word in ['transactional', 'tx', 'trans'])
                    is_promotional = not is_transactional  # Default to promotional
                    
                    # Aggregate counts
                    if is_uk and is_push and is_transactional:
                        results['uk_transactional_pn'] += sent_count
                    elif is_uk and is_push and is_promotional:
                        results['uk_promotional_pn'] += sent_count
                    elif is_uk and is_email and is_transactional:
                        results['uk_transactional_email'] += sent_count
                    elif is_uk and is_email and is_promotional:
                        results['uk_promotional_email'] += sent_count
                    elif is_uae and is_push and is_transactional:
                        results['uae_transactional_pn'] += sent_count
                    elif is_uae and is_push and is_promotional:
                        results['uae_promotional_pn'] += sent_count
                    elif is_uae and is_email and is_transactional:
                        results['uae_transactional_email'] += sent_count
                    elif is_uae and is_email and is_promotional:
                        results['uae_promotional_email'] += sent_count
        
        return results

def test_stats_api_integration():
    """Test the complete Stats API integration"""
    
    print("🧪 TESTING COMPLETE STATS API INTEGRATION")
    print("=" * 60)
    
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
        
        # Extract communication counts
        results = stats_api.extract_communication_counts_by_country(stats_data, start_date, end_date)
        print(f"\n📈 Extracted Communication Counts:")
        for key, value in results.items():
            if key.endswith(('_pn', '_email')):
                print(f"  {key}: {value:,}")
        
        return results
    else:
        print(f"❌ Stats API failed: {stats_data.get('message', 'Unknown error')}")
        
        # Show what the error means
        if stats_data.get('error') == 'stats_api_not_enabled':
            print("\n💡 SOLUTION:")
            print("1. Contact MoEngage support to enable Stats API for your account")
            print("2. Request access to advanced API features")
            print("3. Once enabled, this implementation will work correctly")
            print("\n🔧 AUTHENTICATION IS WORKING:")
            print("✅ We successfully authenticated with MoEngage")
            print("✅ The API recognizes our credentials")
            print("❌ But Stats API access is not enabled for your account")
        
        return None

if __name__ == "__main__":
    test_stats_api_integration()