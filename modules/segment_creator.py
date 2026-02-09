"""
Module for creating MoEngage segments using Segmentation API
"""
import requests
import base64
import time
from datetime import datetime
from typing import Dict, List, Optional


class SegmentCreator:
    """Handle MoEngage segment creation"""
    
    def __init__(self, workspace_id: str, data_api_key: str, data_center: str = '01'):
        self.workspace_id = workspace_id
        self.data_api_key = data_api_key
        self.data_center = data_center
        self.base_url = f"https://api-{data_center}.moengage.com/v3/custom-segments/"
        
    def _get_headers(self) -> Dict:
        """Generate authentication headers"""
        auth_string = f"{self.workspace_id}:{self.data_api_key}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        return {
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/json',
            'MOE-APPKEY': self.workspace_id
        }
    
    def create_segment(self, name: str, description: str, filters: Dict, timeout: int = 60) -> Dict:
        """
        Create a single segment
        
        Args:
            name: Segment name
            description: Segment description
            filters: Filter configuration
            timeout: Request timeout in seconds
            
        Returns:
            Dict with segment info or error
        """
        try:
            payload = {
                "name": name,
                "description": description,
                "included_filters": filters
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self._get_headers(),
                timeout=timeout
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                segment_id = data['data']['id']
                return {
                    'success': True,
                    'name': name,
                    'id': segment_id,
                    'description': description,
                    'url': f"https://dashboard-{self.data_center}.moengage.com/v4/segmentation/all-segments/custom-segments/{segment_id}",
                    'status': 'created'
                }
            elif response.status_code == 409:
                # Segment already exists
                try:
                    error_data = response.json()
                    existing_id = error_data.get('error', {}).get('existing_cs_id', 'unknown')
                    return {
                        'success': True,
                        'name': name,
                        'id': existing_id,
                        'description': f"Reused existing segment",
                        'url': f"https://dashboard-{self.data_center}.moengage.com/v4/segmentation/all-segments/custom-segments/{existing_id}",
                        'status': 'reused'
                    }
                except:
                    return {'success': False, 'error': 'Segment conflict'}
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code} - {response.text[:200]}"
                }
                
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_metrics_segments(self, start_date: str, end_date: str, rate_limit_delay: float = 1.0) -> Dict:
        """
        Create all 18 segments needed for metrics calculation
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            rate_limit_delay: Delay between API calls in seconds
            
        Returns:
            Dict with created segments and summary
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        created_segments = []
        failed_segments = []
        
        # Define all 18 segments (16 original + 2 transacted users)
        segment_definitions = self._get_segment_definitions(start_date, end_date, timestamp)
        
        print(f"Creating {len(segment_definitions)} segments...")
        
        for i, seg_def in enumerate(segment_definitions, 1):
            print(f"[{i}/{len(segment_definitions)}] Creating: {seg_def['display_name']}")
            
            result = self.create_segment(
                seg_def['name'],
                seg_def['description'],
                seg_def['filters']
            )
            
            if result.get('success'):
                created_segments.append({
                    'display_name': seg_def['display_name'],
                    'field_name': seg_def['field_name'],
                    'name': result['name'],
                    'id': result['id'],
                    'url': result['url'],
                    'status': result['status']
                })
                print(f"  ✓ {result['status'].upper()}: {result['id']}")
            else:
                failed_segments.append({
                    'display_name': seg_def['display_name'],
                    'error': result.get('error')
                })
                print(f"  ✗ FAILED: {result.get('error')}")
            
            # Rate limiting
            if i < len(segment_definitions):
                time.sleep(rate_limit_delay)
        
        return {
            'success': len(failed_segments) == 0,
            'segments': created_segments,
            'failed': failed_segments,
            'total_created': len(created_segments),
            'total_failed': len(failed_segments),
            'segment_ids': [s['id'] for s in created_segments]
        }
    
    def _get_segment_definitions(self, start_date: str, end_date: str, timestamp: str) -> List[Dict]:
        """Generate segment definitions for UK and UAE"""
        
        # UK Segments
        uk_segments = [
            {
                'name': f'UK_All_Users_{timestamp}',
                'display_name': 'UK - All Users',
                'field_name': 'uk_total_users',
                'description': 'All UK users',
                'filters': self._filter_all_users('GB')
            },
            {
                'name': f'UK_Active_Users_{timestamp}',
                'display_name': 'UK - Active Users (60d)',
                'field_name': 'uk_active_users',
                'description': 'UK active users (last 60 days)',
                'filters': self._filter_active_users('GB')
            },
            {
                'name': f'UK_Received_Push_{timestamp}',
                'display_name': 'UK - Received Push (Combined Android/iOS)',
                'field_name': 'uk_push_received',
                'description': 'UK users who received push notifications',
                'filters': self._filter_received_push('GB', start_date, end_date)
            },
            {
                'name': f'UK_Received_Email_{timestamp}',
                'display_name': 'UK - Received Email',
                'field_name': 'uk_email_received',
                'description': 'UK users who received email',
                'filters': self._filter_received_email('GB', start_date, end_date)
            },
            {
                'name': f'UK_Active_Received_Push_{timestamp}',
                'display_name': 'UK - Active + Received Push',
                'field_name': 'uk_push_received_active',
                'description': 'UK active users who received push (last 60 days)',
                'filters': self._filter_active_received_push('GB')
            },
            {
                'name': f'UK_Active_Received_Email_{timestamp}',
                'display_name': 'UK - Active + Received Email',
                'field_name': 'uk_email_received_active',
                'description': 'UK active users who received email',
                'filters': self._filter_active_received_email('GB', start_date, end_date)
            },
            {
                'name': f'UK_Unsubscribed_Push_{timestamp}',
                'display_name': 'UK - Unsubscribed Push',
                'field_name': 'uk_push_unsubscribed',
                'description': 'UK users who unsubscribed from push',
                'filters': self._filter_unsubscribed_push('GB', start_date, end_date)
            },
            {
                'name': f'UK_Unsubscribed_Email_{timestamp}',
                'display_name': 'UK - Unsubscribed Email',
                'field_name': 'uk_email_unsubscribed',
                'description': 'UK users who unsubscribed from email',
                'filters': self._filter_unsubscribed_email('GB', start_date, end_date)
            },
            {
                'name': f'UK_Transacted_Users_{timestamp}',
                'display_name': 'UK - Transacted Users (Period)',
                'field_name': 'uk_transacted_users',
                'description': 'UK users who transacted in the selected period',
                'filters': self._filter_transacted_users('GB', start_date, end_date)
            }
        ]
        
        # UAE Segments (copy UK and change country code)
        uae_segments = []
        for uk_seg in uk_segments:
            uae_seg = {
                'name': uk_seg['name'].replace('UK_', 'UAE_'),
                'display_name': uk_seg['display_name'].replace('UK', 'UAE'),
                'field_name': uk_seg['field_name'].replace('uk_', 'uae_'),
                'description': uk_seg['description'].replace('UK', 'UAE'),
                'filters': self._replace_country_code(uk_seg['filters'], 'GB', 'AE')
            }
            uae_segments.append(uae_seg)
        
        return uk_segments + uae_segments
    
    def _filter_all_users(self, country_code: str) -> Dict:
        """Filter for all users in a country"""
        return {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
                    "negate": False,
                    "case_sensitive": False
                }
            ]
        }
    
    def _filter_active_users(self, country_code: str) -> Dict:
        """Filter for active users (with ORDER event in last 60 days)"""
        return {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
                    "negate": False,
                    "case_sensitive": False
                },
                {
                    "filter_type": "actions",
                    "action_name": "ORDER",
                    "executed": True,
                    "execution": {"count": 1, "type": "atleast"},
                    "primary_time_range": {
                        "type": "inTheLast",
                        "value": 60,
                        "value_type": "relative_past",
                        "period_unit": "days"
                    },
                    "attributes": {
                        "filter_operator": "or",
                        "filters": [
                            {
                                "filter_type": "event_attributes",
                                "name": "sub_event",
                                "data_type": "string",
                                "operator": "in",
                                "value": ["COMPLETED"],
                                "negate": False,
                                "case_sensitive": False
                            },
                            {
                                "filter_type": "event_attributes",
                                "name": "sub_event",
                                "data_type": "string",
                                "operator": "in",
                                "value": ["PAYMENT_COMPLETED"],
                                "negate": False,
                                "case_sensitive": False
                            }
                        ]
                    }
                }
            ]
        }
    
    def _filter_received_push(self, country_code: str, start_date: str, end_date: str) -> Dict:
        """Filter for users who received push (Combined Android/iOS with OR logic)"""
        return {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_operator": "or",
                    "filter_type": "nested_filters",
                    "filters": [
                        {
                            "action_name": "NOTIFICATION_RECEIVED_MOE",
                            "executed": True,
                            "filter_type": "actions",
                            "execution": {"count": 1, "type": "atleast"},
                            "primary_time_range": {
                                "type": "between",
                                "value": f"{start_date}T00:00:00.000Z",
                                "value1": f"{end_date}T23:59:59.999Z",
                                "value_type": "absolute",
                                "period_unit": "days"
                            },
                            "attributes": {"filter_operator": "and", "filters": []}
                        },
                        {
                            "action_name": "n_i_s",
                            "executed": True,
                            "filter_type": "actions",
                            "execution": {"count": 1, "type": "atleast"},
                            "primary_time_range": {
                                "type": "between",
                                "value": f"{start_date}T00:00:00.000Z",
                                "value1": f"{end_date}T23:59:59.999Z",
                                "value_type": "absolute",
                                "period_unit": "days"
                            },
                            "attributes": {"filter_operator": "and", "filters": []}
                        }
                    ]
                },
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
                    "negate": False,
                    "case_sensitive": False
                }
            ]
        }
    
    def _filter_received_email(self, country_code: str, start_date: str, end_date: str) -> Dict:
        """Filter for users who received email"""
        return {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
                    "negate": False,
                    "case_sensitive": False
                },
                {
                    "filter_type": "actions",
                    "action_name": "MOE_EMAIL_SENT",
                    "executed": True,
                    "execution": {"count": 1, "type": "atleast"},
                    "primary_time_range": {
                        "type": "between",
                        "value": f"{start_date}T00:00:00.000Z",
                        "value1": f"{end_date}T23:59:59.999Z",
                        "value_type": "absolute",
                        "period_unit": "days"
                    },
                    "attributes": {"filter_operator": "and", "filters": []}
                }
            ]
        }
    
    def _filter_active_received_push(self, country_code: str) -> Dict:
        """Filter for active users who received push (last 60 days, relative time)"""
        return {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_operator": "or",
                    "filter_type": "nested_filters",
                    "filters": [
                        {
                            "action_name": "NOTIFICATION_RECEIVED_MOE",
                            "executed": True,
                            "filter_type": "actions",
                            "execution": {"count": 1, "type": "atleast"},
                            "primary_time_range": {
                                "type": "inTheLast",
                                "value": 60,
                                "value_type": "relative_past",
                                "period_unit": "days"
                            },
                            "attributes": {"filter_operator": "and", "filters": []}
                        },
                        {
                            "action_name": "n_i_s",
                            "executed": True,
                            "filter_type": "actions",
                            "execution": {"count": 1, "type": "atleast"},
                            "primary_time_range": {
                                "type": "inTheLast",
                                "value": 60,
                                "value_type": "relative_past",
                                "period_unit": "days"
                            },
                            "attributes": {"filter_operator": "and", "filters": []}
                        }
                    ]
                },
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
                    "negate": False,
                    "case_sensitive": False
                },
                {
                    "filter_type": "actions",
                    "action_name": "ORDER",
                    "executed": True,
                    "execution": {"count": 1, "type": "atleast"},
                    "primary_time_range": {
                        "type": "inTheLast",
                        "value": 60,
                        "value_type": "relative_past",
                        "period_unit": "days"
                    },
                    "attributes": {
                        "filter_operator": "or",
                        "filters": [
                            {
                                "filter_type": "event_attributes",
                                "name": "sub_event",
                                "data_type": "string",
                                "operator": "in",
                                "value": ["COMPLETED"],
                                "negate": False,
                                "case_sensitive": False
                            },
                            {
                                "filter_type": "event_attributes",
                                "name": "sub_event",
                                "data_type": "string",
                                "operator": "in",
                                "value": ["PAYMENT_COMPLETED"],
                                "negate": False,
                                "case_sensitive": False
                            }
                        ]
                    }
                }
            ]
        }
    
    def _filter_active_received_email(self, country_code: str, start_date: str, end_date: str) -> Dict:
        """Filter for active users who received email"""
        return {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
                    "negate": False,
                    "case_sensitive": False
                },
                {
                    "filter_type": "actions",
                    "action_name": "MOE_EMAIL_SENT",
                    "executed": True,
                    "execution": {"count": 1, "type": "atleast"},
                    "primary_time_range": {
                        "type": "between",
                        "value": f"{start_date}T00:00:00.000Z",
                        "value1": f"{end_date}T23:59:59.999Z",
                        "value_type": "absolute",
                        "period_unit": "days"
                    },
                    "attributes": {"filter_operator": "and", "filters": []}
                },
                {
                    "filter_type": "actions",
                    "action_name": "ORDER",
                    "executed": True,
                    "execution": {"count": 1, "type": "atleast"},
                    "primary_time_range": {
                        "type": "inTheLast",
                        "value": 60,
                        "value_type": "relative_past",
                        "period_unit": "days"
                    },
                    "attributes": {
                        "filter_operator": "or",
                        "filters": [
                            {
                                "filter_type": "event_attributes",
                                "name": "sub_event",
                                "data_type": "string",
                                "operator": "in",
                                "value": ["COMPLETED"],
                                "negate": False,
                                "case_sensitive": False
                            },
                            {
                                "filter_type": "event_attributes",
                                "name": "sub_event",
                                "data_type": "string",
                                "operator": "in",
                                "value": ["PAYMENT_COMPLETED"],
                                "negate": False,
                                "case_sensitive": False
                            }
                        ]
                    }
                }
            ]
        }
    
    def _filter_unsubscribed_push(self, country_code: str, start_date: str, end_date: str) -> Dict:
        """Filter for users who unsubscribed from push"""
        return {
            "filter_operator": "and",
            "filters": [
                {
                    "data_type": "string",
                    "category": "Tracked Custom Attribute",
                    "name": "country",
                    "value": [country_code],
                    "filter_type": "user_attributes",
                    "case_sensitive": False,
                    "operator": "in",
                    "negate": False
                },
                {
                    "action_name": "MOE_PUSH_PERMISSION_STATE_BLOCKED",
                    "executed": True,
                    "filter_type": "actions",
                    "execution": {"count": 1, "type": "atleast"},
                    "primary_time_range": {
                        "type": "between",
                        "value": f"{start_date}T00:00:00.000Z",
                        "value1": f"{end_date}T23:59:59.999Z",
                        "value_type": "absolute",
                        "period_unit": "days"
                    },
                    "attributes": {"filter_operator": "and", "filters": []}
                }
            ]
        }
    
    def _filter_unsubscribed_email(self, country_code: str, start_date: str, end_date: str) -> Dict:
        """Filter for users who unsubscribed from email"""
        return {
            "filter_operator": "and",
            "filters": [
                {
                    "data_type": "string",
                    "category": "Tracked Custom Attribute",
                    "name": "country",
                    "value": [country_code],
                    "filter_type": "user_attributes",
                    "case_sensitive": False,
                    "operator": "in",
                    "negate": False
                },
                {
                    "action_name": "MOE_EMAIL_UNSUBSCRIBE",
                    "executed": True,
                    "filter_type": "actions",
                    "execution": {"count": 1, "type": "atleast"},
                    "primary_time_range": {
                        "type": "between",
                        "value": f"{start_date}T00:00:00.000Z",
                        "value1": f"{end_date}T23:59:59.999Z",
                        "value_type": "absolute",
                        "period_unit": "days"
                    },
                    "attributes": {"filter_operator": "and", "filters": []}
                }
            ]
        }
    
    def _filter_transacted_users(self, country_code: str, start_date: str, end_date: str) -> Dict:
        """Filter for users who transacted in the selected period"""
        return {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
                    "negate": False,
                    "case_sensitive": False
                },
                {
                    "filter_type": "actions",
                    "action_name": "ORDER",
                    "executed": True,
                    "execution": {"count": 1, "type": "atleast"},
                    "primary_time_range": {
                        "type": "between",
                        "value": f"{start_date}T00:00:00.000Z",
                        "value1": f"{end_date}T23:59:59.999Z",
                        "value_type": "absolute",
                        "period_unit": "days"
                    },
                    "attributes": {
                        "filter_operator": "or",
                        "filters": [
                            {
                                "filter_type": "event_attributes",
                                "name": "sub_event",
                                "data_type": "string",
                                "operator": "in",
                                "value": ["COMPLETED"],
                                "negate": False,
                                "case_sensitive": False
                            },
                            {
                                "filter_type": "event_attributes",
                                "name": "sub_event",
                                "data_type": "string",
                                "operator": "in",
                                "value": ["PAYMENT_COMPLETED"],
                                "negate": False,
                                "case_sensitive": False
                            }
                        ]
                    }
                }
            ]
        }
    
    def _replace_country_code(self, filters: Dict, old_code: str, new_code: str) -> Dict:
        """Replace country code in filters (deep copy and replace)"""
        import json
        filters_str = json.dumps(filters)
        filters_str = filters_str.replace(f'"{old_code}"', f'"{new_code}"')
        return json.loads(filters_str)
