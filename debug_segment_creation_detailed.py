#!/usr/bin/env python3
"""
Debug segment creation with detailed error handling to understand why only 8 segments are created
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import automation
from datetime import datetime, timedelta
import time

def create_segments_with_retry(start_date, end_date, max_retries=3):
    """Create segments with retry logic and detailed error reporting"""
    
    print("🔍 DETAILED DEBUG: Segment Creation with Retry Logic")
    print("=" * 70)
    print(f"📅 Date Range: {start_date} to {end_date}")
    
    segments = []
    countries = {'UK': 'GB', 'UAE': 'AE'}
    failed_segments = []
    
    for country_name, country_code in countries.items():
        print(f"\n🌍 === Processing {country_name} ({country_code}) ===")
        
        # Define all segment types we need to create
        segment_definitions = [
            {
                'name': f"{country_name}_All_Users",
                'display_name': f"{country_name} - All Users",
                'field_name': f"{country_name.lower()}_total_users",
                'description': f"All {country_name} users",
                'filters': {
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
            },
            {
                'name': f"{country_name}_Active_Users",
                'display_name': f"{country_name} - Active Users",
                'field_name': f"{country_name.lower()}_active_users",
                'description': f"{country_name} active users (60d)",
                'filters': {
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
                            "attributes": {
                                "filter_operator": "and",
                                "filters": []
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
            }
        ]
        
        # Add communication segments
        for channel, event_name in [('Push', 'MOE_PUSH_SENT'), ('Email', 'MOE_EMAIL_SENT')]:
            # Received communications
            segment_definitions.append({
                'name': f"{country_name}_Received_{channel}",
                'display_name': f"{country_name} - Received {channel}",
                'field_name': f"{country_name.lower()}_{channel.lower()}_received",
                'description': f"{country_name} users who received {channel.lower()}",
                'filters': {
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
                            "action_name": event_name,
                            "execution": {
                                "count": 1,
                                "type": "atleast"
                            }
                        }
                    ]
                }
            })
            
            # Active users who received communications
            segment_definitions.append({
                'name': f"{country_name}_Active_Received_{channel}",
                'display_name': f"{country_name} - Active Users Received {channel}",
                'field_name': f"{country_name.lower()}_{channel.lower()}_received_active",
                'description': f"{country_name} active users who received {channel.lower()}",
                'filters': {
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
                            "action_name": event_name,
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
            })
            
            # Unsubscribed users
            unsub_event = 'unsubscribed to push' if channel == 'Push' else 'email unsubscribes'
            segment_definitions.append({
                'name': f"{country_name}_Unsubscribed_{channel}",
                'display_name': f"{country_name} - Unsubscribed {channel}",
                'field_name': f"{country_name.lower()}_{channel.lower()}_unsubscribed",
                'description': f"{country_name} users who unsubscribed from {channel.lower()}",
                'filters': {
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
                            "action_name": unsub_event,
                            "execution": {
                                "count": 1,
                                "type": "atleast"
                            }
                        }
                    ]
                }
            })
        
        # Create each segment with retry logic
        for i, segment_def in enumerate(segment_definitions, 1):
            print(f"\n{i:2d}. Creating: {segment_def['display_name']}")
            
            success = False
            for attempt in range(max_retries):
                try:
                    result = automation.create_segment(
                        segment_def['name'], 
                        segment_def['description'], 
                        segment_def['filters']
                    )
                    
                    if 'error' not in result:
                        result['display_name'] = segment_def['display_name']
                        result['field_name'] = segment_def['field_name']
                        segments.append(result)
                        print(f"    ✅ SUCCESS: {result.get('status', 'unknown')} (Attempt {attempt + 1})")
                        success = True
                        break
                    else:
                        print(f"    ❌ ATTEMPT {attempt + 1} FAILED: {result['error']}")
                        if attempt < max_retries - 1:
                            print(f"    ⏳ Waiting 2 seconds before retry...")
                            time.sleep(2)
                        
                except Exception as e:
                    print(f"    ❌ ATTEMPT {attempt + 1} EXCEPTION: {str(e)}")
                    if attempt < max_retries - 1:
                        print(f"    ⏳ Waiting 2 seconds before retry...")
                        time.sleep(2)
            
            if not success:
                failed_segments.append({
                    'name': segment_def['name'],
                    'display_name': segment_def['display_name'],
                    'error': 'All retry attempts failed'
                })
                print(f"    💀 FINAL FAILURE: {segment_def['display_name']}")
    
    print(f"\n📊 FINAL SUMMARY:")
    print(f"✅ Successfully created/reused: {len(segments)} segments")
    print(f"❌ Failed segments: {len(failed_segments)}")
    print(f"🎯 Expected: 16 segments (8 per country)")
    
    if failed_segments:
        print(f"\n💀 FAILED SEGMENTS:")
        for failed in failed_segments:
            print(f"   - {failed['display_name']}: {failed['error']}")
    
    return {
        'segments': segments,
        'failed_segments': failed_segments,
        'segment_ids': [seg['id'] for seg in segments if seg.get('id') and seg['id'] != 'unknown']
    }

if __name__ == "__main__":
    result = create_segments_with_retry("2026-01-01", "2026-01-31")
    
    print(f"\n🎯 Expected: 16 segments (8 per country)")
    print(f"🎯 Actual: {len(result['segments'])} segments")
    
    if len(result['segments']) == 16:
        print("🎉 SUCCESS: All segments created!")
    else:
        print("❌ ISSUE: Missing segments")
        
        # Show what we have by country
        uk_count = len([s for s in result['segments'] if 'UK' in s.get('display_name', '')])
        uae_count = len([s for s in result['segments'] if 'UAE' in s.get('display_name', '')])
        print(f"🇬🇧 UK segments: {uk_count}")
        print(f"🇦🇪 UAE segments: {uae_count}")