"""
Module for fetching campaign data using Stats API and Campaign Meta API
"""
import requests
import base64
import time
from typing import Dict, List, Optional


class CampaignFetcher:
    """Fetch campaign performance data from MoEngage"""
    
    def __init__(self, workspace_id: str, campaign_api_key: str, data_center: str = '01'):
        self.workspace_id = workspace_id
        self.campaign_api_key = campaign_api_key
        self.data_center = data_center
        self.stats_api_url = f"https://api-{data_center}.moengage.com/v1/campaigns/stats"
        self.meta_api_url = f"https://api-{data_center}.moengage.com/core-services/v1/campaigns/meta"
        
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
    
    def fetch_campaign_stats(self, start_date: str, end_date: str, 
                            limit: int = 10, offset: int = 0, timeout: int = 30) -> Dict:
        """
        Fetch campaign statistics using Stats API
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Number of campaigns per page (max 10)
            offset: Offset for pagination
            timeout: Request timeout
            
        Returns:
            Dict with campaign stats or error
        """
        try:
            payload = {
                "from_date": start_date,
                "to_date": end_date,
                "limit": limit,
                "offset": offset
            }
            
            response = requests.post(
                self.stats_api_url,
                json=payload,
                headers=self._get_headers(),
                timeout=timeout
            )
            
            print(f"Stats API Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Stats API returned data with keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                return data
            else:
                error_msg = f"Stats API Error: {response.status_code}"
                print(f"❌ {error_msg}")
                print(f"   Response: {response.text[:500]}")
                return {
                    'error': error_msg,
                    'message': response.text[:200]
                }
                
        except requests.exceptions.Timeout:
            return {'error': 'Timeout', 'message': 'Stats API request timed out'}
        except Exception as e:
            return {'error': 'Exception', 'message': str(e)}
    
    def fetch_campaign_meta(self, campaign_id: str, timeout: int = 15) -> Dict:
        """
        Fetch campaign metadata using Campaign Meta API
        
        Args:
            campaign_id: Campaign ID
            timeout: Request timeout
            
        Returns:
            Dict with campaign metadata
        """
        try:
            payload = {
                "request_id": f"meta_{campaign_id}",
                "page": 1,
                "limit": 1,
                "campaign_fields": {
                    "id": campaign_id
                }
            }
            
            response = requests.post(
                self.meta_api_url,
                json=payload,
                headers=self._get_headers(),
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    campaign = data[0]
                    return {
                        'success': True,
                        'campaign_id': campaign.get('campaign_id', campaign_id),
                        'campaign_name': campaign.get('campaign_name', ''),
                        'channel': campaign.get('channel', ''),
                        'delivery_type': campaign.get('campaign_delivery_type', 'unknown'),
                        'status': campaign.get('campaign_status', ''),
                        'platform': campaign.get('platform', []),
                        'tags': campaign.get('campaign_tags', [])
                    }
                else:
                    return {
                        'success': False,
                        'campaign_id': campaign_id,
                        'delivery_type': 'unknown',
                        'error': 'No data in response'
                    }
            else:
                return {
                    'success': False,
                    'campaign_id': campaign_id,
                    'delivery_type': 'unknown',
                    'error': f"API Error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'campaign_id': campaign_id,
                'delivery_type': 'unknown',
                'error': str(e)
            }
    
    def fetch_all_campaigns(self, start_date: str, end_date: str, 
                           max_pages: Optional[int] = None,
                           fetch_meta: bool = True) -> List[Dict]:
        """
        Fetch all campaigns with pagination
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_pages: Maximum pages to fetch (None = all)
            fetch_meta: Whether to fetch metadata for each campaign
            
        Returns:
            List of campaign dictionaries
        """
        all_campaigns = []
        offset = 0
        limit = 10
        pages_fetched = 0
        
        print(f"Fetching campaigns from {start_date} to {end_date}...")
        if max_pages:
            print(f"Max pages limit: {max_pages}")
        
        while True:
            result = self.fetch_campaign_stats(start_date, end_date, limit, offset)
            
            if 'error' in result:
                print(f"❌ Error fetching campaigns: {result['error']}")
                print(f"   Message: {result.get('message', 'No message')}")
                # Return what we have so far instead of breaking with nothing
                if all_campaigns:
                    print(f"⚠️  Returning {len(all_campaigns)} campaigns fetched before error")
                    return all_campaigns
                else:
                    print(f"⚠️  No campaigns fetched, returning empty list")
                    return []
            
            # Check if response has the expected structure
            if 'data' not in result:
                print(f"❌ Unexpected API response structure: {list(result.keys())}")
                return all_campaigns
            
            total_campaigns = result.get('total_campaigns', 0)
            total_pages = result.get('total_pages', 0)
            current_page = result.get('current_page', 1)
            pages_fetched += 1
            
            print(f"Page {current_page}/{total_pages} - Total campaigns: {total_campaigns}")
            
            # Extract campaign data
            campaign_data = result.get('data', {})
            
            for campaign_id, campaign_stats_list in campaign_data.items():
                campaign_info = self._parse_campaign_stats(campaign_id, campaign_stats_list)
                
                # Fetch metadata to determine promotional vs transactional
                if fetch_meta:
                    meta = self.fetch_campaign_meta(campaign_id)
                    if meta.get('success'):
                        campaign_info['campaign_name'] = meta.get('campaign_name', '')
                        campaign_info['channel'] = meta.get('channel', '')
                        campaign_info['delivery_type'] = meta.get('delivery_type', 'unknown')
                        
                        # Categorize based on delivery type
                        if meta.get('delivery_type') == 'ONE_TIME':
                            campaign_info['category'] = 'promotional'
                        elif meta.get('delivery_type') == 'EVENT_TRIGGERED':
                            campaign_info['category'] = 'transactional'
                        else:
                            campaign_info['category'] = 'unknown'
                    else:
                        campaign_info['delivery_type'] = 'unknown'
                        campaign_info['category'] = 'unknown'
                
                all_campaigns.append(campaign_info)
            
            # Check max pages limit
            if max_pages and pages_fetched >= max_pages:
                print(f"⚠️  Reached max pages limit: {max_pages}/{total_pages}")
                print(f"✅ Fetched {len(all_campaigns)} campaigns (partial data)")
                return all_campaigns
            
            # Check if there are more pages
            if current_page >= total_pages:
                break
            
            offset += limit
            time.sleep(0.5)  # Small delay between requests
        
        print(f"✅ Fetched {len(all_campaigns)} campaigns")
        return all_campaigns
    
    def _parse_campaign_stats(self, campaign_id: str, campaign_stats: List[Dict]) -> Dict:
        """Parse campaign statistics from API response"""
        
        if not campaign_stats or len(campaign_stats) == 0:
            return {
                'campaign_id': campaign_id,
                'error': 'No stats available'
            }
        
        # Get the first stats entry
        stats = campaign_stats[0]
        platforms = stats.get('platforms', {})
        all_platforms = platforms.get('ALL_PLATFORMS', {})
        locales = all_platforms.get('locales', {})
        all_locale = locales.get('all_locale', {})
        variations = all_locale.get('variations', {})
        all_variations = variations.get('all_variations', {})
        
        # Extract performance stats
        performance = all_variations.get('performance_stats', {})
        
        return {
            'campaign_id': campaign_id,
            'sent': performance.get('sent', 0),
            'delivered': performance.get('delivered', 0),
            'open': performance.get('open', 0),
            'click': performance.get('click', 0),
            'unsubscribe': performance.get('unsubscribe', 0),
            'bounce': performance.get('bounce', 0),
            'failed': performance.get('failed', 0)
        }
    
    def group_campaigns_by_category(self, campaigns: List[Dict]) -> Dict:
        """
        Group campaigns into 8 categories:
        - UK Promotional Push
        - UK Promotional Email
        - UK Transactional Push
        - UK Transactional Email
        - UAE Promotional Push
        - UAE Promotional Email
        - UAE Transactional Push
        - UAE Transactional Email
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
            campaign_name = campaign.get('campaign_name', '').lower()
            channel = campaign.get('channel', '').lower()
            category = campaign.get('category', 'unknown')
            
            # Determine country
            is_uk = 'uk' in campaign_name or 'gb' in campaign_name
            is_uae = 'uae' in campaign_name or 'ae' in campaign_name
            
            # Determine channel
            is_push = channel in ['push', 'android', 'ios'] or 'push' in campaign_name
            is_email = channel == 'email' or 'email' in campaign_name
            
            # Determine type
            is_promotional = category == 'promotional'
            is_transactional = category == 'transactional'
            
            # Categorize
            if is_uk and is_promotional and is_push:
                categories['uk_promotional_push'].append(campaign)
            elif is_uk and is_promotional and is_email:
                categories['uk_promotional_email'].append(campaign)
            elif is_uk and is_transactional and is_push:
                categories['uk_transactional_push'].append(campaign)
            elif is_uk and is_transactional and is_email:
                categories['uk_transactional_email'].append(campaign)
            elif is_uae and is_promotional and is_push:
                categories['uae_promotional_push'].append(campaign)
            elif is_uae and is_promotional and is_email:
                categories['uae_promotional_email'].append(campaign)
            elif is_uae and is_transactional and is_push:
                categories['uae_transactional_push'].append(campaign)
            elif is_uae and is_transactional and is_email:
                categories['uae_transactional_email'].append(campaign)
        
        return categories
    
    def aggregate_campaign_metrics(self, campaigns: List[Dict]) -> Dict:
        """Aggregate metrics from campaign list"""
        return {
            'total_campaigns': len(campaigns),
            'sent': sum(c.get('sent', 0) for c in campaigns),
            'delivered': sum(c.get('delivered', 0) for c in campaigns),
            'open': sum(c.get('open', 0) for c in campaigns),
            'click': sum(c.get('click', 0) for c in campaigns),
            'unsubscribe': sum(c.get('unsubscribe', 0) for c in campaigns),
            'bounce': sum(c.get('bounce', 0) for c in campaigns),
            'failed': sum(c.get('failed', 0) for c in campaigns)
        }
