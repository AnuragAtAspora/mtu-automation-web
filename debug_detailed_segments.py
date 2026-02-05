#!/usr/bin/env python3
"""
Debug script to see which segments are failing to create
"""

import requests
import base64
import json
from datetime import datetime, timedelta

# MoEngage API Configuration
MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'campaign_api_key': '3XMHJ83D2X4V',
    'data_center': '01'
}

def create_segment_debug(segment_name, description, filters):
    """Debug version of create_segment method with detailed logging"""
    
    print(f"\n🔧 Creating segment: {segment_name}")
    print(f"📝 Description: {description}")
    
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
    
    print(f"📋 Filters: {json.dumps(filters, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            segment_id = data['data']['id']
            print(f"✅ SUCCESS: Created with ID {segment_id}")
            return {
                'name': segment_name,
                'id': segment_id,
                'description': description,
                'url': f"https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments/{segment_id}",
                'status': 'created'
            }
        elif response.status_code == 409:
            print(f"⚠️  DUPLICATE: Reusing existing segment")
            try:
                error_data = response.json()
                existing_name = error_data.get('error', {}).get('existing_cs_name', segment_name)
                existing_id = error_data.get('error', {}).get('existing_cs_id', 'unknown')
                print(f"🔄 Existing: {existing_name} (ID: {existing_id})")
                
                return {
                    'name': existing_name,
                    'id': existing_id,
                    'description': f"Reusing existing segment: {existing_name}",
                    'url': f"https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments/{existing_id}",
                    'status': 'reused'
                }
            except Exception as e:
                print(f"❌ Error parsing duplicate response: {e}")
                return {'error': f"Duplicate parsing error: {e}"}
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return {'error': f"API Error: {response.status_code} - {response.text}"}
            
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT: Request took too long")
        return {'error': f"Request timeout - MoEngage API took too long to respond"}
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        return {'error': f"Error creating segment: {str(e)}"}

def test_all_segments():
    """Test creating all segments that should be created"""
    
    print("🧪 Testing All Segment Creation")
    print("=" * 60)
    
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    segments = []
    countries = {'UK': 'GB', 'UAE': 'AE'}
    
    for country_name, country_code in countries.items():
        print(f"\n🌍 === {country_name} ({country_code}) ===")
        
        # 1. Total users
        segment_name = "UK_All_Users" if country_code == 'GB' else "UAE_All_Users"
        filters = {
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
        
        result = create_segment_debug(segment_name, f"All {country_name} users", filters)
        if 'error' not in result:
            result['display_name'] = f"{country_name} - All Users"
            result['field_name'] = f"{country_name.lower()}_total_users"
            segments.append(result)
        else:
            print(f"❌ FAILED to create Total Users segment: {result['error']}")
        
        # 2. Active users (60 days)
        segment_name = "UK_Active_Users" if country_code == 'GB' else "UAE_Active_Users"
        active_end = datetime.now()
        active_start = active_end - timedelta(days=60)
        
        filters = {
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
                    "filter_operator": "or",
                    "filters": [
                        {
                            "filter_type": "actions",
                            "attributes": {
                                "filter_operator": "and",
                                "filters": [
                                    {
                                        "filter_type": "event_attributes",
                                        "name": "sub_event",
                                        "data_type": "string",
                                        "operator": "in",
                                        "value": ["COMPLETED"],
                                        "negate": False,
                                        "case_sensitive": False
                                    }
                                ]
                            },
                            "executed": True,
                            "primary_time_range": {
                                "type": "between",
                                "value": active_start.strftime('%Y-%m-%dT00:00:00.000Z'),
                                "value1": active_end.strftime('%Y-%m-%dT23:59:59.999Z'),
                                "value_type": "absolute",
                                "period_unit": "days"
                            },
                            "action_name": "ORDER",
                            "execution": {
                                "count": 1,
                                "type": "atleast"
                            }
                        },
                        {
                            "filter_type": "actions",
                            "attributes": {
                                "filter_operator": "and",
                                "filters": [
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
                                "value": active_start.strftime('%Y-%m-%dT00:00:00.000Z'),
                                "value1": active_end.strftime('%Y-%m-%dT23:59:59.999Z'),
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
            ]
        }
        
        result = create_segment_debug(segment_name, f"{country_name} active users (60d)", filters)
        if 'error' not in result:
            result['display_name'] = f"{country_name} - Active Users"
            result['field_name'] = f"{country_name.lower()}_active_users"
            segments.append(result)
        else:
            print(f"❌ FAILED to create Active Users segment: {result['error']}")
        
        # 3. Test just one push segment to see if it works
        segment_name = f"UK_Received_Push" if country_code == 'GB' else f"UAE_Received_Push"
        filters = {
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
                    "filter_operator": "or",
                    "filters": [
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
                            "action_name": "notification received Android",
                            "execution": {
                                "count": 1,
                                "type": "atleast"
                            }
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
                            "action_name": "notification received iOS",
                            "execution": {
                                "count": 1,
                                "type": "atleast"
                            }
                        }
                    ]
                }
            ]
        }
        
        result = create_segment_debug(segment_name, f"{country_name} users who received push", filters)
        if 'error' not in result:
            result['display_name'] = f"{country_name} - Received Push"
            result['field_name'] = f"{country_name.lower()}_push_received"
            segments.append(result)
        else:
            print(f"❌ FAILED to create Received Push segment: {result['error']}")
    
    print(f"\n📊 SUMMARY: {len(segments)} segments created successfully")
    return segments

if __name__ == "__main__":
    segments = test_all_segments()
    
    if len(segments) > 0:
        print(f"\n✅ Created {len(segments)} segments successfully")
    else:
        print(f"\n❌ No segments were created successfully")