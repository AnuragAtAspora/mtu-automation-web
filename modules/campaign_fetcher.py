"""
Module for fetching campaign data using Stats API and Campaign Meta API
"""
import requests
import base64
import time
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


class CampaignFetcher:
    """Fetch campaign performance data from MoEngage"""
    
    def __init__(self, workspace_id: str, campaign_api_key: str, data_center: str = '01'):
        self.workspace_id = workspace_id
        self.campaign_api_key = campaign_api_key
        self.data_center = data_center
        # Stats API endpoint
        self.stats_api_url = f"https://api-{data_center}.moengage.com/core-services/v1/campaign-stats"
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
            # Stats API payload
            payload = {
                "request_id": f"stats_{int(time.time())}",
                "start_date": start_date,
                "end_date": end_date,
                "attribution_type": "VIEW_THROUGH",
                "metric_type": "TOTAL",
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
                
                # Stats API returns data with campaign_id as keys
                campaign_data = data.get('data', {})
                total_campaigns = data.get('total_campaigns', len(campaign_data))
                current_page = data.get('current_page', (offset // limit) + 1)
                total_pages = data.get('total_pages', max(1, (total_campaigns + limit - 1) // limit))
                
                print(f"Processed {len(campaign_data)} campaigns from response")
                
                return {
                    'data': campaign_data,
                    'total_campaigns': total_campaigns,
                    'total_pages': total_pages,
                    'current_page': current_page
                }
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
    
    def fetch_campaigns_by_date(self, start_date: str, end_date: str, 
                                limit: int = 10, page: int = 1, timeout: int = 30) -> Dict:
        """
        Fetch campaigns created within date range using Campaign Meta API
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Number of campaigns per page (max 15)
            page: Page number
            timeout: Request timeout
            
        Returns:
            Dict with campaign list or error
        """
        try:
            # Campaign Meta API expects YYYY-MM-DD format (same as Stats API)
            print(f"Fetching campaigns with created_date: {start_date} to {end_date}")
            
            payload = {
                "request_id": f"meta_date_{int(time.time())}",
                "page": page,
                "limit": min(limit, 15),  # Max 15 per API docs
                "campaign_fields": {
                    "created_date": {
                        "from_date": start_date,
                        "to_date": end_date
                    }
                }
            }
            
            response = requests.post(
                self.meta_api_url,
                json=payload,
                headers=self._get_headers(),
                timeout=timeout
            )
            
            print(f"Campaign Meta API Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Campaign Meta API returns array of campaigns
                if isinstance(data, list):
                    campaigns = data
                else:
                    campaigns = data.get('campaigns', [])
                
                print(f"Campaign Meta API returned {len(campaigns)} campaigns")
                
                return {
                    'success': True,
                    'campaigns': campaigns,
                    'count': len(campaigns)
                }
            else:
                error_msg = f"Campaign Meta API Error: {response.status_code}"
                print(f"❌ {error_msg}")
                print(f"   Response: {response.text[:500]}")
                return {
                    'success': False,
                    'error': error_msg,
                    'message': response.text[:200]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }
    
    def fetch_campaign_meta_batch(self, campaign_ids: List[str], timeout: int = 30) -> Dict:
        """
        Fetch metadata for multiple campaigns in parallel
        
        Args:
            campaign_ids: List of campaign IDs
            timeout: Request timeout per call
            
        Returns:
            Dict mapping campaign_id to metadata
        """
        try:
            results = {}
            
            # Use ThreadPoolExecutor to make parallel API calls
            with ThreadPoolExecutor(max_workers=10) as executor:
                # Submit all tasks
                future_to_id = {
                    executor.submit(self.fetch_campaign_meta, cid, 10): cid 
                    for cid in campaign_ids
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_id):
                    campaign_id = future_to_id[future]
                    try:
                        meta = future.result()
                        if meta.get('success'):
                            results[campaign_id] = meta
                    except Exception as e:
                        print(f"Error fetching meta for {campaign_id[:8]}: {e}")
            
            return results
                
        except Exception as e:
            print(f"Meta batch exception: {e}")
            return {}
    
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
                        'campaign_start_time': campaign.get('campaign_start_time', ''),  # When campaign was sent
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
    
    def fetch_onetime_campaigns(self, start_date: str, end_date: str, 
                                max_pages: Optional[int] = None) -> List[Dict]:
        """
        Fetch ONE_TIME (promotional) campaigns using Campaign Meta API
        Uses created_date as proxy for sent date
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_pages: Maximum pages to fetch
            
        Returns:
            List of campaign dictionaries with stats
        """
        all_campaigns = []
        page = 1
        limit = 15  # Max for Campaign Meta API
        
        print(f"Fetching ONE_TIME campaigns created from {start_date} to {end_date}...")
        
        while True:
            # Fetch campaigns by created_date
            meta_result = self.fetch_campaigns_by_date(start_date, end_date, limit, page)
            
            if not meta_result.get('success'):
                print(f"❌ Error fetching campaigns: {meta_result.get('error')}")
                break
            
            campaigns = meta_result.get('campaigns', [])
            
            if not campaigns:
                print(f"No more campaigns on page {page}")
                break
            
            print(f"Page {page} - Found {len(campaigns)} campaigns")
            
            # Filter for ONE_TIME campaigns only
            onetime_campaigns = [c for c in campaigns if c.get('campaign_delivery_type') == 'ONE_TIME']
            print(f"  {len(onetime_campaigns)} are ONE_TIME campaigns")
            
            if onetime_campaigns:
                # Get campaign IDs
                campaign_ids = [c.get('campaign_id') for c in onetime_campaigns if c.get('campaign_id')]
                
                # Fetch stats in batches of 10
                for i in range(0, len(campaign_ids), 10):
                    batch_ids = campaign_ids[i:i+10]
                    stats_batch = self.fetch_campaign_stats_batch(batch_ids, start_date, end_date)
                    
                    # Match stats with campaigns
                    for campaign in onetime_campaigns:
                        campaign_id = campaign.get('campaign_id')
                        if not campaign_id or campaign_id not in batch_ids:
                            continue
                        
                        # Get stats
                        if campaign_id in stats_batch:
                            campaign_info = stats_batch[campaign_id]
                        else:
                            campaign_info = {
                                'campaign_id': campaign_id,
                                'sent': 0,
                                'delivered': 0,
                                'open': 0,
                                'click': 0,
                                'unsubscribe': 0,
                                'bounce': 0,
                                'failed': 0
                            }
                        
                        # Add metadata
                        campaign_info['campaign_name'] = campaign.get('campaign_name', '')
                        campaign_info['channel'] = campaign.get('channel', '')
                        campaign_info['delivery_type'] = campaign.get('campaign_delivery_type', 'ONE_TIME')
                        campaign_info['status'] = campaign.get('campaign_status', '')
                        campaign_info['campaign_start_time'] = campaign.get('campaign_start_time', '')
                        campaign_info['category'] = 'promotional'
                        
                        all_campaigns.append(campaign_info)
            
            # Check max pages limit
            if max_pages and page >= max_pages:
                print(f"⚠️  Reached max pages limit: {page}")
                break
            
            # If we got less than limit, we're done
            if len(campaigns) < limit:
                break
            
            page += 1
            time.sleep(0.2)
        
        print(f"✅ Fetched {len(all_campaigns)} ONE_TIME campaigns")
        return all_campaigns
    
    def fetch_transactional_campaigns(self, start_date: str, end_date: str, 
                                     transactional_list: List[Dict]) -> List[Dict]:
        """
        Fetch EVENT_TRIGGERED (transactional) campaigns using predefined list
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            transactional_list: List of dicts with campaign_id, campaign_name, country
            
        Returns:
            List of campaign dictionaries with stats
        """
        all_campaigns = []
        
        if not transactional_list:
            print("No transactional campaigns configured")
            return all_campaigns
        
        print(f"Fetching stats for {len(transactional_list)} transactional campaigns...")
        print(f"Date range for transactional stats: {start_date} to {end_date}")
        
        # Get campaign IDs
        campaign_ids = [c['campaign_id'] for c in transactional_list]
        
        # Fetch stats in batches of 10
        for i in range(0, len(campaign_ids), 10):
            batch_ids = campaign_ids[i:i+10]
            print(f"Fetching batch {i//10 + 1}: {len(batch_ids)} campaigns for period {start_date} to {end_date}")
            stats_batch = self.fetch_campaign_stats_batch(batch_ids, start_date, end_date)
            
            # Match stats with campaigns
            for campaign_config in transactional_list:
                campaign_id = campaign_config['campaign_id']
                if campaign_id not in batch_ids:
                    continue
                
                # Get stats
                if campaign_id in stats_batch:
                    campaign_info = stats_batch[campaign_id]
                else:
                    campaign_info = {
                        'campaign_id': campaign_id,
                        'sent': 0,
                        'delivered': 0,
                        'open': 0,
                        'click': 0,
                        'unsubscribe': 0,
                        'bounce': 0,
                        'failed': 0
                    }
                
                # Add metadata from config
                campaign_info['campaign_name'] = campaign_config['campaign_name']
                campaign_info['country'] = campaign_config['country']
                campaign_info['channel'] = campaign_config.get('channel', '').upper()  # Normalize to uppercase
                campaign_info['delivery_type'] = 'EVENT_TRIGGERED'
                campaign_info['category'] = 'transactional'
                campaign_info['status'] = 'LIVE'
                campaign_info['campaign_start_time'] = ''
                
                # Debug: Log what we got
                print(f"  Campaign {campaign_id[:8]}: sent={campaign_info.get('sent', 0)}, channel={campaign_info['channel']}, country={campaign_info['country']}")
                
                all_campaigns.append(campaign_info)
        
        print(f"✅ Fetched stats for {len(all_campaigns)} transactional campaigns")
        return all_campaigns
    
    def fetch_all_campaigns(self, start_date: str, end_date: str, 
                           max_pages: Optional[int] = None,
                           fetch_meta: bool = True) -> List[Dict]:
        """
        Fetch all campaigns that SENT during the date range
        
        Strategy: 
        1. Use Stats API without campaign_ids to get ALL campaigns with stats in date range
        2. Then fetch meta for each to get delivery type
        
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
        limit = 10  # Stats API max
        
        print(f"Fetching campaigns that SENT from {start_date} to {end_date}...")
        if max_pages:
            print(f"Max pages limit: {max_pages}")
        
        page = 1
        while True:
            # Fetch stats for all campaigns in date range (no campaign_ids filter)
            result = self.fetch_campaign_stats(start_date, end_date, limit, offset)
            
            if 'error' in result:
                print(f"❌ Error fetching campaigns: {result['error']}")
                print(f"   Message: {result.get('message', 'No message')}")
                if all_campaigns:
                    print(f"⚠️  Returning {len(all_campaigns)} campaigns fetched before error")
                    return all_campaigns
                else:
                    print(f"⚠️  No campaigns fetched, returning empty list")
                    return []
            
            campaign_data = result.get('data', {})
            total_campaigns = result.get('total_campaigns', 0)
            total_pages = result.get('total_pages', 0)
            current_page = result.get('current_page', 1)
            
            print(f"Page {current_page}/{total_pages} - Found {len(campaign_data)} campaigns")
            
            if not campaign_data:
                print(f"No more campaigns on page {page}")
                break
            
            # Get all campaign IDs from this page
            campaign_ids = list(campaign_data.keys())
            
            # Batch fetch metadata for all campaigns on this page
            print(f"Fetching metadata for {len(campaign_ids)} campaigns...")
            meta_batch = self.fetch_campaign_meta_batch(campaign_ids)
            
            # Process each campaign
            for campaign_id, campaign_stats_list in campaign_data.items():
                campaign_info = self._parse_campaign_stats(campaign_id, campaign_stats_list)
                
                # Get metadata from batch
                meta = meta_batch.get(campaign_id, {})
                if meta.get('success'):
                    campaign_info['campaign_name'] = meta.get('campaign_name', '')
                    campaign_info['channel'] = meta.get('channel', '')
                    campaign_info['delivery_type'] = meta.get('delivery_type', 'unknown')
                    campaign_info['status'] = meta.get('status', '')
                    campaign_start_time = meta.get('campaign_start_time', '')
                    campaign_info['campaign_start_time'] = campaign_start_time
                    
                    # Filter: Only include campaigns where start time is within date range
                    if campaign_start_time:
                        # Extract date from datetime string (YYYY-MM-DD)
                        campaign_date = campaign_start_time.split('T')[0] if 'T' in campaign_start_time else campaign_start_time[:10]
                        
                        # Check if campaign was sent within the date range
                        if campaign_date < start_date or campaign_date > end_date:
                            continue
                    
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
                    campaign_info['campaign_name'] = ''
                    campaign_info['channel'] = ''
                    campaign_info['status'] = ''
                    campaign_info['campaign_start_time'] = ''
                
                all_campaigns.append(campaign_info)
            
            # Check max pages limit
            if max_pages and page >= max_pages:
                print(f"⚠️  Reached max pages limit: {page}")
                print(f"⚠️  WARNING: Only fetched {len(all_campaigns)} campaigns. There may be more campaigns in this period.")
                print(f"✅ Fetched {len(all_campaigns)} campaigns (partial data)")
                return all_campaigns
            
            # Check if there are more pages
            if current_page >= total_pages:
                break
            
            offset += limit
            page += 1
            time.sleep(0.2)  # Reduced delay between requests
        
        print(f"✅ Fetched {len(all_campaigns)} campaigns")
        return all_campaigns
    
    def fetch_campaign_stats_batch(self, campaign_ids: List[str], start_date: str, end_date: str, timeout: int = 30) -> Dict:
        """
        Fetch stats for multiple campaigns in one call (max 10)
        
        Args:
            campaign_ids: List of campaign IDs (max 10)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            timeout: Request timeout
            
        Returns:
            Dict mapping campaign_id to stats dict
        """
        try:
            payload = {
                "request_id": f"stats_batch_{int(time.time())}",
                "campaign_ids": campaign_ids[:10],  # Max 10
                "start_date": start_date,
                "end_date": end_date,
                "attribution_type": "VIEW_THROUGH",
                "metric_type": "TOTAL"
            }
            
            print(f"Stats API batch request: {len(campaign_ids[:10])} campaigns, dates: {start_date} to {end_date}")
            print(f"Payload: campaign_ids={campaign_ids[:10][:2]}... (showing first 2), start_date={start_date}, end_date={end_date}")
            
            response = requests.post(
                self.stats_api_url,
                json=payload,
                headers=self._get_headers(),
                timeout=timeout
            )
            
            print(f"Stats API response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                campaign_data = data.get('data', {})
                
                print(f"Stats API returned data for {len(campaign_data)} campaigns")
                
                # Debug: Show first campaign's structure
                if campaign_data:
                    first_id = list(campaign_data.keys())[0]
                    print(f"Sample campaign {first_id[:8]} structure: {list(campaign_data[first_id][0].keys()) if campaign_data[first_id] else 'empty'}")
                
                result = {}
                for campaign_id in campaign_ids:
                    if campaign_id in campaign_data:
                        result[campaign_id] = self._parse_campaign_stats(campaign_id, campaign_data[campaign_id])
                    else:
                        print(f"  No data for campaign {campaign_id[:8]}")
                        result[campaign_id] = {
                            'campaign_id': campaign_id,
                            'sent': 0,
                            'delivered': 0,
                            'open': 0,
                            'click': 0,
                            'unsubscribe': 0,
                            'bounce': 0,
                            'failed': 0
                        }
                
                return result
            else:
                print(f"Stats API batch error: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return {cid: {
                    'campaign_id': cid,
                    'sent': 0,
                    'delivered': 0,
                    'open': 0,
                    'click': 0,
                    'unsubscribe': 0,
                    'bounce': 0,
                    'failed': 0
                } for cid in campaign_ids}
                
        except Exception as e:
            print(f"Stats API batch exception: {e}")
            import traceback
            traceback.print_exc()
            return {cid: {
                'campaign_id': cid,
                'sent': 0,
                'delivered': 0,
                'open': 0,
                'click': 0,
                'unsubscribe': 0,
                'bounce': 0,
                'failed': 0
            } for cid in campaign_ids}
    
    def fetch_campaign_stats_by_id(self, campaign_id: str, start_date: str, end_date: str, timeout: int = 30) -> Dict:
        """
        Fetch stats for a specific campaign ID
        
        Args:
            campaign_id: Campaign ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            timeout: Request timeout
            
        Returns:
            Dict with campaign stats
        """
        try:
            payload = {
                "request_id": f"stats_{campaign_id}",
                "campaign_ids": [campaign_id],
                "start_date": start_date,
                "end_date": end_date,
                "attribution_type": "VIEW_THROUGH",
                "metric_type": "TOTAL"
            }
            
            response = requests.post(
                self.stats_api_url,
                json=payload,
                headers=self._get_headers(),
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                campaign_data = data.get('data', {})
                
                if campaign_id in campaign_data:
                    return self._parse_campaign_stats(campaign_id, campaign_data[campaign_id])
                else:
                    return {
                        'campaign_id': campaign_id,
                        'sent': 0,
                        'delivered': 0,
                        'open': 0,
                        'click': 0,
                        'unsubscribe': 0,
                        'bounce': 0,
                        'failed': 0
                    }
            else:
                return {'error': f"Stats API Error: {response.status_code}"}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _parse_campaign_stats(self, campaign_id: str, campaign_stats: List[Dict]) -> Dict:
        """Parse campaign statistics from Stats API response"""
        
        if not campaign_stats or len(campaign_stats) == 0:
            return {
                'campaign_id': campaign_id,
                'error': 'No stats available'
            }
        
        # Get the campaign data - Stats API returns nested structure
        campaign = campaign_stats[0]
        
        # Initialize totals
        sent = 0
        delivered = 0
        opened = 0
        click = 0
        unsubscribe = 0
        bounce = 0
        failed = 0
        
        # Stats API has nested structure: platforms -> locales -> all_locale -> variations -> performance_stats
        platforms = campaign.get('platforms', {})
        
        if not platforms:
            print(f"  ⚠️  Campaign {campaign_id[:8]} has no platforms data")
        
        # Check if ALL_PLATFORMS exists - if so, use only that to avoid double counting
        if 'ALL_PLATFORMS' in platforms:
            # Use only ALL_PLATFORMS which already aggregates all platforms
            platform_data = platforms['ALL_PLATFORMS']
            locales = platform_data.get('locales', {})
            all_locale = locales.get('all_locale', {})
            if all_locale:
                variations = all_locale.get('variations', {})
                all_variations = variations.get('all_variations', {})
                if all_variations:
                    perf_stats = all_variations.get('performance_stats', {})
                    
                    sent = perf_stats.get('sent', 0)
                    delivered = perf_stats.get('delivered', 0)
                    opened = perf_stats.get('open', 0)  # Unique opens
                    click = perf_stats.get('click', 0)  # Unique clicks
                    unsubscribe = perf_stats.get('unsubscribe', 0)
                    bounce = perf_stats.get('bounced', 0)
                    failed = perf_stats.get('failed', 0)
        else:
            # No ALL_PLATFORMS, aggregate across individual platforms
            for platform_name, platform_data in platforms.items():
                locales = platform_data.get('locales', {})
                
                # API returns 'all_locale' (singular), not 'all_locales' (plural)
                all_locale = locales.get('all_locale', {})
                if all_locale:
                    variations = all_locale.get('variations', {})
                    all_variations = variations.get('all_variations', {})
                    if all_variations:
                        perf_stats = all_variations.get('performance_stats', {})
                        
                        # Aggregate stats across platforms
                        sent += perf_stats.get('sent', 0)
                        delivered += perf_stats.get('delivered', 0)
                        opened += perf_stats.get('open', 0)  # Field is 'open' not 'opened'
                        click += perf_stats.get('click', 0)
                        unsubscribe += perf_stats.get('unsubscribe', 0)
                        bounce += perf_stats.get('bounced', 0)
                        failed += perf_stats.get('failed', 0)
        
        print(f"  Campaign {campaign_id[:8]}: sent={sent}, opened={opened}, click={click}")
        
        return {
            'campaign_id': campaign_id,
            'sent': sent,
            'delivered': delivered,
            'open': opened,
            'click': click,
            'unsubscribe': unsubscribe,
            'bounce': bounce,
            'failed': failed
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
            
            # Determine country - check explicit country field first (for transactional)
            country = campaign.get('country', '').upper()
            if country == 'UK':
                is_uk = True
                is_uae = False
            elif country == 'UAE':
                is_uk = False
                is_uae = True
            else:
                # Infer from campaign name (for promotional)
                is_uk = 'uk' in campaign_name or 'gb' in campaign_name
                is_uae = 'uae' in campaign_name or 'ae' in campaign_name
            
            # Determine channel
            is_push = channel in ['push', 'android', 'ios'] or 'push' in campaign_name or 'pn' in campaign_name
            is_email = channel in ['email'] or 'email' in campaign_name
            
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
