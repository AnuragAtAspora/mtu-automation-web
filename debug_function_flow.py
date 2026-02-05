#!/usr/bin/env python3
"""
Debug the create_metrics_segments function flow to see where segments are being lost
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import automation
from datetime import datetime, timedelta

def debug_create_metrics_segments(start_date, end_date):
    """Debug version of create_metrics_segments with detailed logging"""
    
    print("🔍 DEBUGGING create_metrics_segments FUNCTION FLOW")
    print("=" * 70)
    print(f"📅 Date Range: {start_date} to {end_date}")
    
    segments = []
    countries = {'UK': 'GB', 'UAE': 'AE'}
    
    for country_name, country_code in countries.items():
        print(f"\n🌍 === Processing {country_name} ({country_code}) ===")
        
        # Define all segment types we need to create for this country
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
        
        print(f"📋 Defined {len(segment_definitions)} segments for {country_name}")
        
        # Create each segment with error handling and detailed logging
        for i, segment_def in enumerate(segment_definitions, 1):
            print(f"\n{i:2d}. Creating: {segment_def['display_name']}")
            
            try:
                print(f"    🔄 Calling automation.create_segment...")
                result = automation.create_segment(
                    segment_def['name'], 
                    segment_def['description'], 
                    segment_def['filters']
                )
                
                print(f"    📊 Result type: {type(result)}")
                print(f"    📊 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                
                if isinstance(result, dict) and 'error' not in result:
                    result['display_name'] = segment_def['display_name']
                    result['field_name'] = segment_def['field_name']
                    segments.append(result)
                    print(f"    ✅ SUCCESS: Added to segments list (Status: {result.get('status', 'unknown')})")
                    print(f"    📝 Total segments so far: {len(segments)}")
                elif isinstance(result, dict) and 'error' in result:
                    print(f"    ❌ ERROR in result: {result['error']}")
                    print(f"    ⚠️  Segment NOT added to list")
                else:
                    print(f"    ⚠️  UNEXPECTED result: {result}")
                    print(f"    ⚠️  Segment NOT added to list")
                
            except Exception as e:
                print(f"    💥 EXCEPTION: {str(e)}")
                print(f"    ⚠️  Segment NOT added to list")
                # Print traceback for debugging
                import traceback
                traceback.print_exc()
    
    print(f"\n📊 FINAL RESULT:")
    print(f"✅ Total segments in list: {len(segments)}")
    print(f"🎯 Expected: 16 segments")
    
    if len(segments) < 16:
        print(f"❌ MISSING: {16 - len(segments)} segments")
    
    return {
        'segments': segments,
        'segment_ids': [seg['id'] for seg in segments if seg.get('id') and seg['id'] != 'unknown']
    }

if __name__ == "__main__":
    result = debug_create_metrics_segments("2026-01-01", "2026-01-31")
    
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"Expected: 16 segments")
    print(f"Actual: {len(result['segments'])} segments")
    
    if len(result['segments']) == 16:
        print("🎉 SUCCESS: All segments found!")
    else:
        print("❌ ISSUE: Missing segments detected")