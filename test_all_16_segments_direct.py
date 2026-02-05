#!/usr/bin/env python3
"""
Create all 16 segments directly with delays, bypassing the create_metrics_segments function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import automation
from datetime import datetime, timedelta
import time

def create_all_16_segments_direct():
    """Create all 16 segments directly with delays"""
    
    print("🎯 CREATING ALL 16 SEGMENTS DIRECTLY WITH DELAYS")
    print("=" * 70)
    
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    print(f"📅 Date Range: {start_date} to {end_date}")
    print(f"⏱️  Using 2-second delays between API calls")
    print()
    
    # Define all 16 segments
    all_segments = []
    
    # UK Segments (8 total)
    uk_segments = [
        {
            'name': 'UK_All_Users_Direct',
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
            'name': 'UK_Active_Users_Direct',
            'display_name': 'UK - Active Users',
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
        },
        {
            'name': 'UK_Received_Push_Direct',
            'display_name': 'UK - Received Push',
            'field_name': 'uk_push_received',
            'description': 'UK users who received push',
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
                        "action_name": "MOE_PUSH_SENT",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        },
        {
            'name': 'UK_Received_Email_Direct',
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
            'name': 'UK_Active_Received_Push_Direct',
            'display_name': 'UK - Active Users Received Push',
            'field_name': 'uk_push_received_active',
            'description': 'UK active users who received push',
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
                        "action_name": "MOE_PUSH_SENT",
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
        },
        {
            'name': 'UK_Active_Received_Email_Direct',
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
        },
        {
            'name': 'UK_Unsubscribed_Push_Direct',
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
                        "action_name": "unsubscribed to push",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        },
        {
            'name': 'UK_Unsubscribed_Email_Direct',
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
                        "action_name": "email unsubscribes",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        }
    ]
    
    # UAE Segments (8 total) - same structure but with AE country code
    uae_segments = []
    for uk_segment in uk_segments:
        uae_segment = uk_segment.copy()
        uae_segment['name'] = uk_segment['name'].replace('UK_', 'UAE_')
        uae_segment['display_name'] = uk_segment['display_name'].replace('UK', 'UAE')
        uae_segment['field_name'] = uk_segment['field_name'].replace('uk_', 'uae_')
        uae_segment['description'] = uk_segment['description'].replace('UK', 'UAE')
        
        # Deep copy filters and change country code
        import copy
        uae_segment['filters'] = copy.deepcopy(uk_segment['filters'])
        uae_segment['filters']['filters'][0]['value'] = ['AE']  # Change GB to AE
        
        uae_segments.append(uae_segment)
    
    # Combine all segments
    all_segments = uk_segments + uae_segments
    
    print(f"📋 Total segments to create: {len(all_segments)}")
    print()
    
    successful_segments = []
    failed_segments = []
    
    # Create each segment with delays
    for i, segment_def in enumerate(all_segments, 1):
        print(f"{i:2d}. Creating: {segment_def['display_name']}")
        
        start_time = time.time()
        
        try:
            result = automation.create_segment(
                segment_def['name'], 
                segment_def['description'], 
                segment_def['filters']
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if isinstance(result, dict) and 'error' not in result:
                # Add display info like the function does
                result['display_name'] = segment_def['display_name']
                result['field_name'] = segment_def['field_name']
                
                print(f"    ✅ SUCCESS: {result.get('status', 'unknown')} (Response: {response_time:.2f}s)")
                print(f"    🆔 ID: {result.get('id', 'unknown')}")
                successful_segments.append(result)
            elif isinstance(result, dict) and 'error' in result:
                print(f"    ❌ ERROR: {result['error']} (Response: {response_time:.2f}s)")
                failed_segments.append({
                    'segment': segment_def['display_name'],
                    'error': result['error']
                })
            else:
                print(f"    ⚠️  UNEXPECTED: {result} (Response: {response_time:.2f}s)")
                failed_segments.append({
                    'segment': segment_def['display_name'],
                    'error': f"Unexpected result: {result}"
                })
                
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"    💥 EXCEPTION: {str(e)} (Response: {response_time:.2f}s)")
            failed_segments.append({
                'segment': segment_def['display_name'],
                'error': str(e)
            })
        
        # Add delay between requests (except after the last one)
        if i < len(all_segments):
            print(f"    ⏳ Waiting 2 seconds...")
            time.sleep(2)
        
        print()
    
    print(f"📊 FINAL RESULTS:")
    print(f"✅ Successful: {len(successful_segments)}")
    print(f"❌ Failed: {len(failed_segments)}")
    print(f"🎯 Expected: 16 segments")
    
    if successful_segments:
        print(f"\n✅ SUCCESSFUL SEGMENTS:")
        uk_count = len([s for s in successful_segments if 'UK' in s.get('display_name', '')])
        uae_count = len([s for s in successful_segments if 'UAE' in s.get('display_name', '')])
        print(f"   🇬🇧 UK: {uk_count} segments")
        print(f"   🇦🇪 UAE: {uae_count} segments")
        
        for seg in successful_segments:
            print(f"   - {seg.get('display_name', 'Unknown')}: {seg.get('status', 'unknown')}")
    
    if failed_segments:
        print(f"\n❌ FAILED SEGMENTS:")
        for seg in failed_segments:
            print(f"   - {seg['segment']}: {seg['error']}")
    
    return {
        'segments': successful_segments,
        'failed': failed_segments,
        'segment_ids': [seg['id'] for seg in successful_segments if seg.get('id') and seg['id'] != 'unknown']
    }

if __name__ == "__main__":
    result = create_all_16_segments_direct()
    
    print(f"\n🎯 FINAL ANALYSIS:")
    success_rate = len(result['segments']) / 16 * 100
    print(f"Success rate: {success_rate:.1f}% ({len(result['segments'])}/16)")
    
    if success_rate == 100:
        print("🎉 PERFECT: All 16 segments created successfully!")
        print("💡 The issue was definitely in the create_metrics_segments function logic")
    elif success_rate >= 80:
        print("🎊 EXCELLENT: Most segments created successfully!")
    elif success_rate >= 50:
        print("⚠️  PARTIAL: Some segments created")
    else:
        print("❌ POOR: Few segments created")