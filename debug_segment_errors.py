#!/usr/bin/env python3
"""
Debug segment creation errors to see what's causing the missing segments
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import automation
from datetime import datetime, timedelta
import json

def test_missing_segments_with_errors():
    """Test creating the missing segments and capture any errors"""
    
    print("🔍 DEBUGGING MISSING SEGMENT ERRORS")
    print("=" * 60)
    
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    print(f"📅 Date Range: {start_date} to {end_date}")
    
    # Define the missing segments that we need to test
    missing_segments = [
        {
            'name': 'UK_Active_Users',
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
            'name': 'UK_Received_Push',
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
            'name': 'UK_Active_Received_Push',
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
            'name': 'UK_Active_Received_Email',
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
        }
    ]
    
    successful_segments = []
    failed_segments = []
    
    for i, segment_def in enumerate(missing_segments, 1):
        print(f"\n{i}. Testing: {segment_def['display_name']}")
        print(f"   Name: {segment_def['name']}")
        print(f"   Description: {segment_def['description']}")
        
        try:
            result = automation.create_segment(
                segment_def['name'], 
                segment_def['description'], 
                segment_def['filters']
            )
            
            print(f"   📊 Result Type: {type(result)}")
            
            if isinstance(result, dict):
                if 'error' in result:
                    print(f"   ❌ ERROR: {result['error']}")
                    failed_segments.append({
                        'segment': segment_def['display_name'],
                        'error': result['error'],
                        'type': 'API Error'
                    })
                else:
                    print(f"   ✅ SUCCESS: {result.get('status', 'unknown')}")
                    print(f"   🆔 ID: {result.get('id', 'unknown')}")
                    print(f"   📝 Name: {result.get('name', 'unknown')}")
                    successful_segments.append({
                        'segment': segment_def['display_name'],
                        'status': result.get('status', 'unknown'),
                        'id': result.get('id', 'unknown')
                    })
            else:
                print(f"   ⚠️  UNEXPECTED RESULT: {result}")
                failed_segments.append({
                    'segment': segment_def['display_name'],
                    'error': f"Unexpected result type: {type(result)}",
                    'type': 'Unexpected Response'
                })
                
        except Exception as e:
            print(f"   💥 EXCEPTION: {str(e)}")
            failed_segments.append({
                'segment': segment_def['display_name'],
                'error': str(e),
                'type': 'Exception'
            })
            
            # Print full traceback for debugging
            import traceback
            print(f"   📋 Full traceback:")
            traceback.print_exc()
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Successful: {len(successful_segments)}")
    print(f"❌ Failed: {len(failed_segments)}")
    
    if successful_segments:
        print(f"\n✅ SUCCESSFUL SEGMENTS:")
        for seg in successful_segments:
            print(f"   - {seg['segment']}: {seg['status']} (ID: {seg['id']})")
    
    if failed_segments:
        print(f"\n❌ FAILED SEGMENTS:")
        for seg in failed_segments:
            print(f"   - {seg['segment']}: {seg['type']}")
            print(f"     Error: {seg['error']}")
            print()
    
    return {
        'successful': successful_segments,
        'failed': failed_segments
    }

if __name__ == "__main__":
    result = test_missing_segments_with_errors()
    
    print(f"\n🎯 CONCLUSION:")
    if len(result['failed']) == 0:
        print("🎉 All missing segments can be created successfully!")
    elif len(result['successful']) > 0:
        print("⚠️  Some segments work, some fail - mixed results")
    else:
        print("💀 All missing segments are failing - there's a systematic issue")