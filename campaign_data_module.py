#!/usr/bin/env python3
"""
Campaign Data Module
Fetch and analyze MoEngage campaign data using Stats API
"""

import requests
import base64
from datetime import datetime, timedelta
import json
import csv
from typing import Dict, List, Optional

class CampaignDataFetcher:
    """Fetch campaign data from MoEngage Stats API"""
    
    def __init__(self, workspace_id: str, campaign_api_key: str, data_center: str = '01'):
        self.workspace_id = workspace_id
        self.campaign_api_key = campaign_api_key
        self.data_center = data_center
        self.base_url = f"https://api-{data_center}.moengage.com/core-services/v1"
        
    def _get_headers(self) -> Dict:
        """Generate authentication headers"""
        auth_string = f"{self.workspace_id}:{self.campaign_api_key}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {encoded_auth}',
            'MOE-APPKEY': self.workspace_id,
            'APP_SECRET_KEY': self.campaign_api_key
        }
    
    def get_campaign_meta(self, campaign_id: str) -> Dict:
        """
        Fetch campaign metadata including delivery type using Campaign Meta API
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Dict with campaign metadata including delivery_type
        """
        url = f"{self.base_url}/campaigns/meta"
        
        payload = {
            "request_id": f"meta_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "page": 1,
            "limit": 1,
            "campaign_fields": {
                "id": campaign_id
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Response is an array of campaigns
                if isinstance(data, list) and len(data) > 0:
                    campaign = data[0]
                    return {
                        'campaign_id': campaign.get('campaign_id', campaign_id),
                        'delivery_type': campaign.get('campaign_delivery_type', 'unknown'),
                        'campaign_name': campaign.get('campaign_name', ''),
                        'channel': campaign.get('channel', ''),
                        'status': campaign.get('campaign_status', ''),
                        'platform': campaign.get('platform', []),
                        'tags': campaign.get('campaign_tags', [])
                    }
                else:
                    return {
                        'campaign_id': campaign_id,
                        'delivery_type': 'unknown',
                        'error': 'No campaign data in response'
                    }
            else:
                return {
                    'campaign_id': campaign_id,
                    'error': f"API Error: {response.status_code}",
                    'delivery_type': 'unknown'
                }
        except Exception as e:
            return {
                'campaign_id': campaign_id,
                'error': str(e),
                'delivery_type': 'unknown'
            }
    
    def fetch_campaigns(self, start_date: str, end_date: str, 
                       limit: int = 10, offset: int = 0) -> Dict:
        """
        Fetch campaign data for a date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Number of campaigns per page (max 100)
            offset: Pagination offset
            
        Returns:
            Dict with campaign data
        """
        url = f"{self.base_url}/campaign-stats"
        
        payload = {
            'request_id': f"fetch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_date': start_date,
            'end_date': end_date,
            'attribution_type': 'TOTAL_CONVERSIONS',
            'metric_type': 'TOTAL',
            'offset': offset,
            'limit': limit
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f"API Error: {response.status_code}",
                    'message': response.text
                }
        except Exception as e:
            return {
                'error': 'Exception',
                'message': str(e)
            }
    
    def fetch_all_campaigns(self, start_date: str, end_date: str, 
                           max_campaigns: Optional[int] = None,
                           fetch_meta: bool = True) -> List[Dict]:
        """
        Fetch all campaigns with pagination and optionally fetch metadata
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            max_campaigns: Maximum number of campaigns to fetch (None = all)
            fetch_meta: Whether to fetch campaign metadata (delivery type, etc.)
            
        Returns:
            List of campaign data dictionaries
        """
        all_campaigns = []
        offset = 0
        limit = 10  # MoEngage API max limit
        
        print(f"Fetching campaigns from {start_date} to {end_date}...")
        
        while True:
            result = self.fetch_campaigns(start_date, end_date, limit, offset)
            
            if 'error' in result:
                print(f"Error: {result['error']} - {result['message']}")
                break
            
            total_campaigns = result.get('total_campaigns', 0)
            total_pages = result.get('total_pages', 0)
            current_page = result.get('current_page', 1)
            
            print(f"Page {current_page}/{total_pages} - Total campaigns: {total_campaigns}")
            
            # Extract campaign data
            campaign_data = result.get('data', {})
            
            for campaign_id, campaign_stats in campaign_data.items():
                campaign_info = self._parse_campaign_stats(campaign_id, campaign_stats)
                
                # Fetch metadata to get delivery type
                if fetch_meta:
                    meta = self.get_campaign_meta(campaign_id)
                    campaign_info['delivery_type'] = meta.get('delivery_type', 'unknown')
                    campaign_info['campaign_name'] = meta.get('campaign_name', '')
                    campaign_info['channel'] = meta.get('channel', '')
                    
                    # Categorize as promotional or transactional
                    if meta.get('delivery_type') == 'ONE_TIME':
                        campaign_info['category'] = 'promotional'
                    elif meta.get('delivery_type') == 'EVENT_TRIGGERED':
                        campaign_info['category'] = 'transactional'
                    else:
                        campaign_info['category'] = 'unknown'
                
                all_campaigns.append(campaign_info)
                
                if max_campaigns and len(all_campaigns) >= max_campaigns:
                    print(f"Reached max campaigns limit: {max_campaigns}")
                    return all_campaigns
            
            # Check if there are more pages
            if current_page >= total_pages:
                break
            
            offset += limit
        
        print(f"✅ Fetched {len(all_campaigns)} campaigns")
        return all_campaigns
    
    def _parse_campaign_stats(self, campaign_id: str, campaign_stats: List[Dict]) -> Dict:
        """Parse campaign statistics from API response"""
        
        if not campaign_stats or len(campaign_stats) == 0:
            return {
                'campaign_id': campaign_id,
                'error': 'No stats available'
            }
        
        # Get the first stats entry (usually contains all platforms)
        stats = campaign_stats[0]
        platforms = stats.get('platforms', {})
        all_platforms = platforms.get('ALL_PLATFORMS', {})
        locales = all_platforms.get('locales', {})
        all_locale = locales.get('all_locale', {})
        variations = all_locale.get('variations', {})
        all_variations = variations.get('all_variations', {})
        
        # Extract performance stats
        performance = all_variations.get('performance_stats', {})
        delivery = all_variations.get('delivery_funnel', {})
        
        return {
            'campaign_id': campaign_id,
            'sent': performance.get('sent', 0),
            'delivered': performance.get('delivered', 0),
            'open': performance.get('open', 0),
            'click': performance.get('click', 0),
            'unsubscribe': performance.get('unsubscribe', 0),
            'bounce': performance.get('bounce', 0),
            'failed': performance.get('failed', 0),
            'open_rate': performance.get('open_rate', 0),
            'ctr': performance.get('ctr', 0),
            'delivery_rate': performance.get('delivery_rate', 0),
            'total_users_in_segment': delivery.get('total_user_in_segment', 0)
        }


class CampaignAnalyzer:
    """Analyze campaign data"""
    
    @staticmethod
    def filter_by_country(campaigns: List[Dict], country: str) -> List[Dict]:
        """Filter campaigns by country code in campaign name"""
        country_lower = country.lower()
        return [c for c in campaigns if country_lower in c.get('campaign_name', '').lower() 
                or country_lower in c.get('campaign_id', '').lower()]
    
    @staticmethod
    def filter_by_channel(campaigns: List[Dict], channel: str) -> List[Dict]:
        """Filter campaigns by channel (push/email)"""
        channel_lower = channel.lower()
        return [c for c in campaigns if channel_lower in c.get('channel', '').lower()]
    
    @staticmethod
    def filter_by_category(campaigns: List[Dict], category: str) -> List[Dict]:
        """Filter campaigns by category (promotional/transactional)"""
        return [c for c in campaigns if c.get('category', '').lower() == category.lower()]
    
    @staticmethod
    def group_by_category(campaigns: List[Dict]) -> Dict[str, List[Dict]]:
        """Group campaigns by category"""
        promotional = [c for c in campaigns if c.get('category') == 'promotional']
        transactional = [c for c in campaigns if c.get('category') == 'transactional']
        unknown = [c for c in campaigns if c.get('category') == 'unknown']
        
        return {
            'promotional': promotional,
            'transactional': transactional,
            'unknown': unknown
        }
    
    @staticmethod
    def group_by_8_categories(campaigns: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group campaigns into 8 categories:
        Country (UK/UAE) x Channel (Push/Email) x Type (Promotional/Transactional)
        """
        categories = {
            'uk_promotional_push': [],
            'uk_promotional_email': [],
            'uk_transactional_push': [],
            'uk_transactional_email': [],
            'uae_promotional_push': [],
            'uae_promotional_email': [],
            'uae_transactional_push': [],
            'uae_transactional_email': []
        }
        
        for campaign in campaigns:
            # Determine country
            campaign_name = campaign.get('campaign_name', '').lower()
            campaign_id = campaign.get('campaign_id', '').lower()
            
            if 'uk' in campaign_name or 'uk' in campaign_id:
                country = 'uk'
            elif 'uae' in campaign_name or 'uae' in campaign_id:
                country = 'uae'
            else:
                continue  # Skip if country not identified
            
            # Determine channel
            channel = campaign.get('channel', '').lower()
            if channel == 'push':
                channel_key = 'push'
            elif channel == 'email':
                channel_key = 'email'
            else:
                continue  # Skip if channel not identified
            
            # Determine type
            category = campaign.get('category', '').lower()
            if category == 'promotional':
                type_key = 'promotional'
            elif category == 'transactional':
                type_key = 'transactional'
            else:
                continue  # Skip if type not identified
            
            # Build category key
            category_key = f"{country}_{type_key}_{channel_key}"
            
            if category_key in categories:
                categories[category_key].append(campaign)
        
        return categories
    
    @staticmethod
    def aggregate_stats(campaigns: List[Dict]) -> Dict:
        """Aggregate statistics across campaigns"""
        total_sent = sum(c.get('sent', 0) for c in campaigns)
        total_delivered = sum(c.get('delivered', 0) for c in campaigns)
        total_opens = sum(c.get('open', 0) for c in campaigns)
        total_clicks = sum(c.get('click', 0) for c in campaigns)
        total_unsubscribes = sum(c.get('unsubscribe', 0) for c in campaigns)
        
        return {
            'total_campaigns': len(campaigns),
            'total_sent': total_sent,
            'total_delivered': total_delivered,
            'total_opens': total_opens,
            'total_clicks': total_clicks,
            'total_unsubscribes': total_unsubscribes,
            'avg_open_rate': (total_opens / total_delivered * 100) if total_delivered > 0 else 0,
            'avg_ctr': (total_clicks / total_delivered * 100) if total_delivered > 0 else 0,
            'delivery_rate': (total_delivered / total_sent * 100) if total_sent > 0 else 0
        }
    
    @staticmethod
    def export_to_csv(campaigns: List[Dict], filename: str):
        """Export campaign data to CSV"""
        if not campaigns:
            print("No campaigns to export")
            return
        
        # Get all unique keys
        keys = set()
        for campaign in campaigns:
            keys.update(campaign.keys())
        
        keys = sorted(list(keys))
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(campaigns)
        
        print(f"✅ Exported {len(campaigns)} campaigns to {filename}")
    
    @staticmethod
    def print_summary(campaigns: List[Dict], title: str = "CAMPAIGN SUMMARY"):
        """Print campaign summary"""
        stats = CampaignAnalyzer.aggregate_stats(campaigns)
        
        print()
        print("=" * 70)
        print(title)
        print("=" * 70)
        print(f"Total Campaigns: {stats['total_campaigns']}")
        print(f"Total Sent: {stats['total_sent']:,}")
        print(f"Total Delivered: {stats['total_delivered']:,}")
        print(f"Total Opens: {stats['total_opens']:,}")
        print(f"Total Clicks: {stats['total_clicks']:,}")
        print(f"Total Unsubscribes: {stats['total_unsubscribes']:,}")
        print()
        print(f"Delivery Rate: {stats['delivery_rate']:.2f}%")
        print(f"Average Open Rate: {stats['avg_open_rate']:.2f}%")
        print(f"Average CTR: {stats['avg_ctr']:.2f}%")
        print("=" * 70)
    
    @staticmethod
    def print_category_breakdown(campaigns: List[Dict]):
        """Print breakdown by promotional vs transactional"""
        grouped = CampaignAnalyzer.group_by_category(campaigns)
        
        print()
        print("=" * 70)
        print("PROMOTIONAL VS TRANSACTIONAL BREAKDOWN")
        print("=" * 70)
        
        for category, camp_list in grouped.items():
            if camp_list:
                print()
                print(f"📊 {category.upper()}: {len(camp_list)} campaigns")
                stats = CampaignAnalyzer.aggregate_stats(camp_list)
                print(f"   Sent: {stats['total_sent']:,}")
                print(f"   Delivered: {stats['total_delivered']:,}")
                print(f"   Opens: {stats['total_opens']:,}")
                print(f"   Clicks: {stats['total_clicks']:,}")
        
        print("=" * 70)
    
    @staticmethod
    def print_8_category_breakdown(campaigns: List[Dict]):
        """Print detailed breakdown by all 8 categories"""
        categories = CampaignAnalyzer.group_by_8_categories(campaigns)
        
        print()
        print("=" * 70)
        print("8-CATEGORY BREAKDOWN (Country x Channel x Type)")
        print("=" * 70)
        
        # Define display order and labels
        category_labels = {
            'uk_promotional_push': 'UK - Promotional - Push',
            'uk_promotional_email': 'UK - Promotional - Email',
            'uk_transactional_push': 'UK - Transactional - Push',
            'uk_transactional_email': 'UK - Transactional - Email',
            'uae_promotional_push': 'UAE - Promotional - Push',
            'uae_promotional_email': 'UAE - Promotional - Email',
            'uae_transactional_push': 'UAE - Transactional - Push',
            'uae_transactional_email': 'UAE - Transactional - Email'
        }
        
        for key, label in category_labels.items():
            camp_list = categories.get(key, [])
            if camp_list:
                print()
                print(f"📊 {label}: {len(camp_list)} campaigns")
                stats = CampaignAnalyzer.aggregate_stats(camp_list)
                print(f"   Sent: {stats['total_sent']:,}")
                print(f"   Delivered: {stats['total_delivered']:,}")
                print(f"   Opens: {stats['total_opens']:,}")
                print(f"   Clicks: {stats['total_clicks']:,}")
        
        print("=" * 70)


# Example usage
if __name__ == "__main__":
    # Configuration
    WORKSPACE_ID = '95PNUHBSYSLLJZ22PEOFMKF2'
    CAMPAIGN_API_KEY = '3XMHJ83D2X4V'
    DATA_CENTER = '01'
    
    # Initialize fetcher
    fetcher = CampaignDataFetcher(WORKSPACE_ID, CAMPAIGN_API_KEY, DATA_CENTER)
    analyzer = CampaignAnalyzer()
    
    # Set date range (current month)
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date.replace(day=1)
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    print(f"Fetching campaigns from {start_date_str} to {end_date_str}")
    print()
    
    # Fetch campaigns (limit to 20 for demo, with metadata)
    campaigns = fetcher.fetch_all_campaigns(start_date_str, end_date_str, max_campaigns=20, fetch_meta=True)
    
    if campaigns:
        # Print overall summary
        analyzer.print_summary(campaigns, "OVERALL CAMPAIGN SUMMARY")
        
        # Print 8-category breakdown
        analyzer.print_8_category_breakdown(campaigns)
        
        # Export to CSV
        analyzer.export_to_csv(campaigns, 'campaign_data.csv')
        
        print()
        print("✅ Campaign data exported to campaign_data.csv")
        print("✅ Data categorized into 8 groups: Country x Channel x Type")
    else:
        print("No campaigns fetched")
