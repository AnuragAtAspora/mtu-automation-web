#!/usr/bin/env python3
"""
MTU Automation Web Interface - Clean Version
Streamlined web app for MoEngage metrics and MTU calculations
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session
import requests
import base64
from datetime import datetime, timedelta
import json
import os
import gspread
from google.oauth2.service_account import Credentials
import csv
import io
from campaign_data_module import CampaignDataFetcher, CampaignAnalyzer

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mtu-automation-secret-key-2026')

# Make datetime available in templates
@app.context_processor
def inject_datetime():
    return {'datetime': datetime, 'timedelta': timedelta}

# Configuration
MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'campaign_api_key': '3XMHJ83D2X4V',
    'data_center': '01'
}

GOOGLE_SHEET_ID = "1A30FfO319eiKW0c6zHj2lwr04WLE0fL6eLteZf4CvHM"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_segment(segment_name, description, filters):
    """Create a segment using MoEngage Custom Segment API"""
    try:
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v3/custom-segments/"
        
        # Auth
        auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/json',
            'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id']
        }
        
        payload = {
            "name": segment_name,
            "description": description,
            "included_filters": filters
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code in [200, 201]:
            data = response.json()
            segment_id = data['data']['id']
            return {
                'name': segment_name,
                'id': segment_id,
                'description': description,
                'url': f"https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments/{segment_id}",
                'status': 'created'
            }
        elif response.status_code == 409:
            # Segment already exists - reuse it
            try:
                error_data = response.json()
                existing_name = error_data.get('error', {}).get('existing_cs_name', segment_name)
                existing_id = error_data.get('error', {}).get('existing_cs_id', 'unknown')
                
                return {
                    'name': existing_name,
                    'id': existing_id,
                    'description': f"Reusing existing segment: {existing_name}",
                    'url': f"https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments/{existing_id}",
                    'status': 'reused'
                }
            except:
                return {'error': 'Segment conflict but could not parse existing segment info'}
        else:
            return {'error': f"API Error: {response.status_code} - {response.text}"}
            
    except requests.exceptions.Timeout:
        return {'error': 'Request timeout - MoEngage API took too long to respond'}
    except Exception as e:
        return {'error': f"Error creating segment: {str(e)}"}


def create_metrics_segments(start_date, end_date):
    """
    Create 16 segments for comprehensive metrics calculation
    - 8 UK segments (All, Active, Push Received, Email Received, Active+Push, Active+Email, Push Unsub, Email Unsub)
    - 8 UAE segments (same as UK)
    
    Uses COMBINED Android/iOS segments with OR logic for push notifications
    """
    import time
    
    created_segments = []
    segment_ids = []
    
    # UK Segments (8 total)
    uk_segments = [
        {
            'name': f'UK_All_Users_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'display_name': 'UK - All Users',
            'field_name': 'uk_total_users',
            'description': 'All UK users',
            'filters': {
                "filter_operator": "and",
                "filters": [
                    {
                        "filter_type": "user_attributes",
                        "name": "country",
                        "data_type": "string",
                        "operator": "in",
                        "value": ["GB"],
                        "negate": False,
                        "case_sensitive": False
                    }
                ]
            }
        },
        {
            'name': f'UK_Active_Users_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'display_name': 'UK - Active Users (60d)',
            'field_name': 'uk_active_users',
            'description': 'UK active users (60d)',
            'filters': {
                "filter_operator": "and",
                "filters": [
                    {
                        "filter_type": "user_attributes",
                        "name": "country",
                        "data_type": "string",
                        "operator": "in",
                        "value": ["GB"],
                        "negate": False,
                        "case_sensitive": False
                    },
                    {
                        "filter_type": "actions",
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
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%dT00:00:00.000Z'),
                            "value1": datetime.now().strftime('%Y-%m-%dT23:59:59.999Z'),
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": "ORDER",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        },
        {
            'name': f'UK_Received_Push_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'display_name': 'UK - Received Push (Combined Android/iOS)',
            'field_name': 'uk_push_received',
            'description': 'UK users who received push notifications (Android OR iOS)',
            'filters': {
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
                        "value": ["GB"],
                        "negate": False,
                        "case_sensitive": False
                    }
                ]
            }
        },
        {
            'name': f'UK_Received_Email_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'display_name': 'UK - Received Email',
            'field_name': 'uk_email_received',
            'description': 'UK users who received email',
            'filters': {
                "filter_operator": "and",
                "filters": [
                    {
                        "filter_type": "user_attributes",
                        "name": "country",
                        "data_type": "string",
                        "operator": "in",
                        "value": ["GB"],
                        "negate": False,
                        "case_sensitive": False
                    },
                    {
                        "filter_type": "actions",
                        "attributes": {
                            "filter_operator": "and",
                            "filters": []
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": f"{start_date}T00:00:00.000Z",
                            "value1": f"{end_date}T23:59:59.999Z",
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": "MOE_EMAIL_SENT",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        },
        {
            'name': f'UK_Active_Received_Push_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'display_name': 'UK - Active Users Received Push (Combined)',
            'field_name': 'uk_push_received_active',
            'description': 'UK active users who received push (Android OR iOS, last 60 days)',
            'filters': {
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
                                    "value_type": "relative",
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
                                    "value_type": "relative",
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
                        "value": ["GB"],
                        "negate": False,
                        "case_sensitive": False
                    },
                    {
                        "filter_type": "actions",
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
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "inTheLast",
                            "value": 60,
                            "value_type": "relative",
                            "period_unit": "days"
                        },
                        "action_name": "ORDER",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        },
        {
            'name': f'UK_Active_Received_Email_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'display_name': 'UK - Active Users Received Email',
            'field_name': 'uk_email_received_active',
            'description': 'UK active users who received email',
            'filters': {
                "filter_operator": "and",
                "filters": [
                    {
                        "filter_type": "user_attributes",
                        "name": "country",
                        "data_type": "string",
                        "operator": "in",
                        "value": ["GB"],
                        "negate": False,
                        "case_sensitive": False
                    },
                    {
                        "filter_type": "actions",
                        "attributes": {
                            "filter_operator": "and",
                            "filters": []
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": f"{start_date}T00:00:00.000Z",
                            "value1": f"{end_date}T23:59:59.999Z",
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": "MOE_EMAIL_SENT",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    },
                    {
                        "filter_type": "actions",
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
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%dT00:00:00.000Z'),
                            "value1": datetime.now().strftime('%Y-%m-%dT23:59:59.999Z'),
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": "ORDER",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        },
        {
            'name': f'UK_Unsubscribed_Push_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'display_name': 'UK - Unsubscribed Push',
            'field_name': 'uk_push_unsubscribed',
            'description': 'UK users who unsubscribed from push',
            'filters': {
                "filter_operator": "and",
                "filters": [
                    {
                        "filter_type": "user_attributes",
                        "name": "country",
                        "data_type": "string",
                        "operator": "in",
                        "value": ["GB"],
                        "negate": False,
                        "case_sensitive": False
                    },
                    {
                        "filter_type": "actions",
                        "attributes": {
                            "filter_operator": "and",
                            "filters": []
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": f"{start_date}T00:00:00.000Z",
                            "value1": f"{end_date}T23:59:59.999Z",
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": "MOE_PUSH_UNSUBSCRIBED",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        },
        {
            'name': f'UK_Unsubscribed_Email_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'display_name': 'UK - Unsubscribed Email',
            'field_name': 'uk_email_unsubscribed',
            'description': 'UK users who unsubscribed from email',
            'filters': {
                "filter_operator": "and",
                "filters": [
                    {
                        "filter_type": "user_attributes",
                        "name": "country",
                        "data_type": "string",
                        "operator": "in",
                        "value": ["GB"],
                        "negate": False,
                        "case_sensitive": False
                    },
                    {
                        "filter_type": "actions",
                        "attributes": {
                            "filter_operator": "and",
                            "filters": []
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": f"{start_date}T00:00:00.000Z",
                            "value1": f"{end_date}T23:59:59.999Z",
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": "MOE_EMAIL_UNSUBSCRIBED",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        }
    ]
    
    # UAE Segments (8 total) - Copy UK segments and change country code
    uae_segments = []
    for uk_seg in uk_segments:
        uae_seg = json.loads(json.dumps(uk_seg))  # Deep copy
        uae_seg['name'] = uk_seg['name'].replace('UK_', 'UAE_')
        uae_seg['display_name'] = uk_seg['display_name'].replace('UK', 'UAE')
        uae_seg['field_name'] = uk_seg['field_name'].replace('uk_', 'uae_')
        uae_seg['description'] = uk_seg['description'].replace('UK', 'UAE')
        
        # Replace country code GB with AE in filters
        filters_str = json.dumps(uae_seg['filters'])
        filters_str = filters_str.replace('"GB"', '"AE"')
        uae_seg['filters'] = json.loads(filters_str)
        
        uae_segments.append(uae_seg)
    
    # Combine all segments (16 total)
    all_segments = uk_segments + uae_segments
    
    # Create segments with rate limiting
    for i, seg_def in enumerate(all_segments):
        print(f"Creating segment {i+1}/16: {seg_def['display_name']}")
        
        result = create_segment(
            seg_def['name'],
            seg_def['description'],
            seg_def['filters']
        )
        
        if 'error' in result:
            print(f"  ❌ Error: {result['error']}")
            # Continue with other segments
        else:
            print(f"  ✅ Created: {result['id']}")
            created_segments.append({
                'display_name': seg_def['display_name'],
                'field_name': seg_def['field_name'],
                'segment_id': result['id'],
                'segment_url': result['url'],
                'status': result.get('status', 'created')
            })
            segment_ids.append(result['id'])
        
        # Rate limiting: Wait 1 second between requests
        if i < len(all_segments) - 1:
            time.sleep(1)
    
    return {
        'segments': created_segments,
        'segment_ids': segment_ids,
        'total_created': len(created_segments),
        'total_expected': 16
    }


def get_campaign_performance_data(start_date, end_date):
    """Get campaign performance data using CampaignDataFetcher"""
    
    try:
        # Initialize campaign data fetcher
        fetcher = CampaignDataFetcher(
            workspace_id=MOENGAGE_CONFIG['workspace_id'],
            campaign_api_key=MOENGAGE_CONFIG['campaign_api_key'],
            data_center=MOENGAGE_CONFIG['data_center']
        )
        
        # Fetch all campaigns with metadata
        campaigns = fetcher.fetch_all_campaigns(start_date, end_date, fetch_meta=True)
        
        if not campaigns:
            raise Exception("No campaigns found for the date range")
        
        # Group campaigns into 8 categories
        analyzer = CampaignAnalyzer()
        categories = analyzer.group_by_8_categories(campaigns)
        
        # Store full campaign data in session for CSV export
        session['campaign_categories'] = {
            key: [
                {
                    'campaign_id': c.get('campaign_id'),
                    'campaign_name': c.get('campaign_name'),
                    'channel': c.get('channel'),
                    'category': c.get('category'),
                    'sent': c.get('sent', 0),
                    'delivered': c.get('delivered', 0),
                    'open': c.get('open', 0),
                    'click': c.get('click', 0),
                    'unsubscribe': c.get('unsubscribe', 0)
                }
                for c in camp_list
            ]
            for key, camp_list in categories.items()
        }
        
        # Aggregate data by country and type for metrics calculation
        uk_data = {
            'tx_pn_sent': sum(c.get('sent', 0) for c in categories['uk_transactional_push']),
            'tx_email_sent': sum(c.get('sent', 0) for c in categories['uk_transactional_email']),
            'pr_pn_sent': sum(c.get('sent', 0) for c in categories['uk_promotional_push']),
            'pr_email_sent': sum(c.get('sent', 0) for c in categories['uk_promotional_email']),
            'pn_delivered': sum(c.get('delivered', 0) for c in categories['uk_transactional_push'] + categories['uk_promotional_push']),
            'email_delivered': sum(c.get('delivered', 0) for c in categories['uk_transactional_email'] + categories['uk_promotional_email']),
            'pn_clicks': sum(c.get('click', 0) for c in categories['uk_transactional_push'] + categories['uk_promotional_push']),
            'email_opens': sum(c.get('open', 0) for c in categories['uk_transactional_email'] + categories['uk_promotional_email']),
            'pn_unsubscribes': sum(c.get('unsubscribe', 0) for c in categories['uk_transactional_push'] + categories['uk_promotional_push']),
            'email_unsubscribes': sum(c.get('unsubscribe', 0) for c in categories['uk_transactional_email'] + categories['uk_promotional_email'])
        }
        
        uae_data = {
            'tx_pn_sent': sum(c.get('sent', 0) for c in categories['uae_transactional_push']),
            'tx_email_sent': sum(c.get('sent', 0) for c in categories['uae_transactional_email']),
            'pr_pn_sent': sum(c.get('sent', 0) for c in categories['uae_promotional_push']),
            'pr_email_sent': sum(c.get('sent', 0) for c in categories['uae_promotional_email']),
            'pn_delivered': sum(c.get('delivered', 0) for c in categories['uae_transactional_push'] + categories['uae_promotional_push']),
            'email_delivered': sum(c.get('delivered', 0) for c in categories['uae_transactional_email'] + categories['uae_promotional_email']),
            'pn_clicks': sum(c.get('click', 0) for c in categories['uae_transactional_push'] + categories['uae_promotional_push']),
            'email_opens': sum(c.get('open', 0) for c in categories['uae_transactional_email'] + categories['uae_promotional_email']),
            'pn_unsubscribes': sum(c.get('unsubscribe', 0) for c in categories['uae_transactional_push'] + categories['uae_promotional_push']),
            'email_unsubscribes': sum(c.get('unsubscribe', 0) for c in categories['uae_transactional_email'] + categories['uae_promotional_email'])
        }
        
        return {
            'data_source': 'Stats API + Campaign Meta API (Real-time)',
            'uk': uk_data,
            'uae': uae_data,
            'total_campaigns': len(campaigns)
        }
        
    except Exception as e:
        print(f"Error fetching campaign data: {e}")
        return {
            'error': str(e)
        }


def calculate_comprehensive_metrics(campaign_data, user_counts):
    """Calculate comprehensive metrics from campaign data and user counts"""
    
    metrics = {
        'uk': {},
        'uae': {}
    }
    
    for country in ['uk', 'uae']:
        cd = campaign_data[country]
        
        # Get user counts
        total_users = user_counts[f'{country}_total_users']
        active_users = user_counts[f'{country}_active_users']
        push_received = user_counts[f'{country}_push_received']
        email_received = user_counts[f'{country}_email_received']
        push_received_active = user_counts[f'{country}_push_received_active']
        email_received_active = user_counts[f'{country}_email_received_active']
        
        # Calculate metrics
        metrics[country] = {
            # Transactional metrics (per transacted user)
            'tx_pn_per_user': round(cd['tx_pn_sent'] / active_users, 4) if active_users > 0 else 0,
            'tx_email_per_user': round(cd['tx_email_sent'] / active_users, 4) if active_users > 0 else 0,
            
            # Promotional metrics (per total user)
            'pr_pn_per_user': round(cd['pr_pn_sent'] / total_users, 4) if total_users > 0 else 0,
            'pr_email_per_user': round(cd['pr_email_sent'] / total_users, 4) if total_users > 0 else 0,
            
            # MTU metrics
            'push_mtu': round((push_received_active / active_users) * 100, 2) if active_users > 0 else 0,
            'email_mtu': round((email_received_active / active_users) * 100, 2) if active_users > 0 else 0,
            
            # Delivery rates
            'push_delivery_rate': round((cd['pn_delivered'] / cd['tx_pn_sent'] + cd['pr_pn_sent']) * 100, 2) if (cd['tx_pn_sent'] + cd['pr_pn_sent']) > 0 else 0,
            'email_delivery_rate': round((cd['email_delivered'] / (cd['tx_email_sent'] + cd['pr_email_sent'])) * 100, 2) if (cd['tx_email_sent'] + cd['pr_email_sent']) > 0 else 0,
            
            # Engagement rates
            'push_ctr': round((cd['pn_clicks'] / cd['pn_delivered']) * 100, 2) if cd['pn_delivered'] > 0 else 0,
            'email_open_rate': round((cd['email_opens'] / cd['email_delivered']) * 100, 2) if cd['email_delivered'] > 0 else 0,
            
            # Unsubscribe rates
            'push_unsub_rate': round((cd['pn_unsubscribes'] / cd['pn_delivered']) * 100, 4) if cd['pn_delivered'] > 0 else 0,
            'email_unsub_rate': round((cd['email_unsubscribes'] / cd['email_delivered']) * 100, 4) if cd['email_delivered'] > 0 else 0
        }
    
    return metrics



# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading home page: {str(e)}", 500


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "MTU Automation is running"}, 200


@app.route('/comprehensive-metrics')
def comprehensive_metrics():
    """Show comprehensive metrics dashboard with date selection"""
    return render_template('comprehensive_metrics.html')


@app.route('/generate-metrics', methods=['POST'])
def generate_metrics():
    """Generate metrics by calling APIs and creating segments"""
    try:
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        if not start_date or not end_date:
            flash('Please select both start and end dates', 'error')
            return redirect(url_for('comprehensive_metrics'))
        
        # Step 1: Get campaign performance data
        campaign_data = get_campaign_performance_data(start_date, end_date)
        
        if 'error' in campaign_data:
            flash(f'Error getting campaign data: {campaign_data["error"]}', 'error')
            return redirect(url_for('comprehensive_metrics'))
        
        # Step 2: Create 16 segments for user counts
        segments_result = create_metrics_segments(start_date, end_date)
        
        if 'error' in segments_result:
            flash(f'Error creating segments: {segments_result["error"]}', 'error')
            return redirect(url_for('comprehensive_metrics'))
        
        # Step 3: Show segments input page
        campaign_data['segment_ids'] = segments_result.get('segment_ids', [])
        
        return render_template('segments_input.html',
                             start_date=start_date,
                             end_date=end_date,
                             segments=segments_result['segments'],
                             campaign_data_json=json.dumps(campaign_data))
        
    except Exception as e:
        flash(f'Error generating metrics: {str(e)}', 'error')
        return redirect(url_for('comprehensive_metrics'))


@app.route('/calculate-final-metrics', methods=['POST'])
def calculate_final_metrics():
    """Calculate final metrics with user-provided segment counts"""
    try:
        # Get form data
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        campaign_data_json = request.form.get('campaign_data')
        
        # Parse campaign data
        campaign_data = json.loads(campaign_data_json)
        
        # Get user counts from form
        user_counts = {
            'uk_total_users': int(request.form.get('uk_total_users', 0)),
            'uk_active_users': int(request.form.get('uk_active_users', 0)),
            'uk_push_received': int(request.form.get('uk_push_received', 0)),
            'uk_email_received': int(request.form.get('uk_email_received', 0)),
            'uk_push_received_active': int(request.form.get('uk_push_received_active', 0)),
            'uk_email_received_active': int(request.form.get('uk_email_received_active', 0)),
            'uk_push_unsubscribed': int(request.form.get('uk_push_unsubscribed', 0)),
            'uk_email_unsubscribed': int(request.form.get('uk_email_unsubscribed', 0)),
            'uae_total_users': int(request.form.get('uae_total_users', 0)),
            'uae_active_users': int(request.form.get('uae_active_users', 0)),
            'uae_push_received': int(request.form.get('uae_push_received', 0)),
            'uae_email_received': int(request.form.get('uae_email_received', 0)),
            'uae_push_received_active': int(request.form.get('uae_push_received_active', 0)),
            'uae_email_received_active': int(request.form.get('uae_email_received_active', 0)),
            'uae_push_unsubscribed': int(request.form.get('uae_push_unsubscribed', 0)),
            'uae_email_unsubscribed': int(request.form.get('uae_email_unsubscribed', 0)),
        }
        
        # Calculate metrics
        metrics = calculate_comprehensive_metrics(campaign_data, user_counts)
        
        # Convert to objects for template access
        from types import SimpleNamespace
        
        metrics_obj = SimpleNamespace(**{
            'uk': SimpleNamespace(**metrics['uk']),
            'uae': SimpleNamespace(**metrics['uae'])
        })
        
        campaign_data_obj = SimpleNamespace(**{
            'uk': SimpleNamespace(**campaign_data['uk']),
            'uae': SimpleNamespace(**campaign_data['uae'])
        })
        
        user_counts_obj = SimpleNamespace(**user_counts)
        
        # Extract segment IDs for cleanup
        try:
            campaign_data_dict = json.loads(campaign_data_json)
            segment_ids = campaign_data_dict.get('segment_ids', [])
        except:
            segment_ids = []
        
        return render_template('metrics_results.html',
                             start_date=start_date,
                             end_date=end_date,
                             data_source=campaign_data.get('data_source', 'API'),
                             metrics=metrics_obj,
                             campaign_data=campaign_data_obj,
                             user_counts=user_counts_obj,
                             segment_ids=segment_ids)
        
    except Exception as e:
        flash(f'Error calculating final metrics: {str(e)}', 'error')
        return redirect(url_for('comprehensive_metrics'))



@app.route('/export-campaign-csv/<category>')
def export_campaign_csv(category):
    """Export campaign data for a specific category to CSV"""
    try:
        # Get campaign data from session
        campaign_categories = session.get('campaign_categories', {})
        
        if not campaign_categories or category not in campaign_categories:
            flash('No campaign data available for export', 'error')
            return redirect(url_for('comprehensive_metrics'))
        
        campaigns = campaign_categories[category]
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'campaign_id', 'campaign_name', 'channel', 'category',
            'sent', 'delivered', 'open', 'click', 'unsubscribe'
        ])
        
        writer.writeheader()
        for campaign in campaigns:
            writer.writerow(campaign)
        
        # Create response
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{category}_campaigns.csv'
        )
        
    except Exception as e:
        flash(f'Error exporting CSV: {str(e)}', 'error')
        return redirect(url_for('comprehensive_metrics'))


@app.route('/export-all-campaigns-csv')
def export_all_campaigns_csv():
    """Export all campaign data to a single CSV"""
    try:
        # Get campaign data from session
        campaign_categories = session.get('campaign_categories', {})
        
        if not campaign_categories:
            flash('No campaign data available for export', 'error')
            return redirect(url_for('comprehensive_metrics'))
        
        # Combine all campaigns
        all_campaigns = []
        for category, campaigns in campaign_categories.items():
            all_campaigns.extend(campaigns)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'campaign_id', 'campaign_name', 'channel', 'category',
            'sent', 'delivered', 'open', 'click', 'unsubscribe'
        ])
        
        writer.writeheader()
        for campaign in all_campaigns:
            writer.writerow(campaign)
        
        # Create response
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='all_campaigns.csv'
        )
        
    except Exception as e:
        flash(f'Error exporting CSV: {str(e)}', 'error')
        return redirect(url_for('comprehensive_metrics'))


@app.route('/calculate-mtu')
def calculate_mtu_form():
    """Show MTU calculation form"""
    return render_template('calculate_mtu.html')


@app.route('/calculate-mtu', methods=['POST'])
def calculate_mtu():
    """Calculate MTU from segment counts"""
    try:
        # Get form data
        segment_counts = {}
        countries = ['UK', 'UAE']
        
        for country in countries:
            segment_counts[f'{country}_all_users'] = int(request.form.get(f'{country.lower()}_all_users', 0))
            segment_counts[f'{country}_active_users'] = int(request.form.get(f'{country.lower()}_active_users', 0))
            segment_counts[f'{country}_push_received'] = int(request.form.get(f'{country.lower()}_push_received', 0))
            segment_counts[f'{country}_push_received_active'] = int(request.form.get(f'{country.lower()}_push_received_active', 0))
            segment_counts[f'{country}_email_received'] = int(request.form.get(f'{country.lower()}_email_received', 0))
            segment_counts[f'{country}_email_received_active'] = int(request.form.get(f'{country.lower()}_email_received_active', 0))
        
        period_info = request.form.get('period', f"Generated on {datetime.now().strftime('%Y-%m-%d')}")
        
        # Calculate MTU percentages
        results = {}
        for country in countries:
            results[country] = {}
            
            # Get base counts
            all_users = segment_counts.get(f"{country}_all_users", 0)
            active_users = segment_counts.get(f"{country}_active_users", 0)
            
            results[country]['all_users'] = all_users
            results[country]['active_users'] = active_users
            
            # Calculate active user percentage
            if all_users > 0:
                active_percentage = (active_users / all_users) * 100
                results[country]['active_percentage'] = round(active_percentage, 2)
            else:
                results[country]['active_percentage'] = 0
            
            # Calculate MTU for each channel
            for channel in ['push', 'email']:
                received = segment_counts.get(f"{country}_{channel}_received", 0)
                received_active = segment_counts.get(f"{country}_{channel}_received_active", 0)
                
                results[country][f'{channel}_received'] = received
                results[country][f'{channel}_received_active'] = received_active
                
                # MTU = (Active users who received comms / Active users) * 100
                if active_users > 0:
                    mtu_percentage = (received_active / active_users) * 100
                    results[country][f'{channel}_mtu'] = round(mtu_percentage, 2)
                else:
                    results[country][f'{channel}_mtu'] = 0
                
                # Additional metric: Reach percentage (received / all users)
                if all_users > 0:
                    reach_percentage = (received / all_users) * 100
                    results[country][f'{channel}_reach'] = round(reach_percentage, 2)
                else:
                    results[country][f'{channel}_reach'] = 0
        
        return render_template('mtu_results.html', 
                             results=results,
                             period=period_info,
                             sheets_updated=False,
                             sheet_url=f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}")
        
    except Exception as e:
        flash(f'Error calculating MTU: {str(e)}', 'error')
        return redirect(url_for('calculate_mtu_form'))


# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
