#!/usr/bin/env python3
"""
Test if rate limiting is causing the segment creation issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import automation
from datetime import datetime, timedelta
import time

def test_rate_limiting_with_delays():
    """Test creating multiple segments with delays to avoid rate limiting"""
    
    print("🚦 TESTING RATE LIMITING HYPOTHESIS")
    print("=" * 60)
    
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    # Test segments that we know should work
    test_segments = [
        {
            'name': 'UK_All_Users_RateTest',
            'display_name': 'UK - All Users (Rate Test)',
            'description': 'UK all users - rate limiting test',
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
            'name': 'UK_Active_Users_RateTest',
            'display_name': 'UK - Active Users (Rate Test)',
            'description': 'UK active users - rate limiting test',
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
            'name': 'UK_Push_Received_RateTest',
            'display_name': 'UK - Push Received (Rate Test)',
            'description': 'UK push received - rate limiting test',
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
            'name': 'UK_Email_Received_RateTest',
            'display_name': 'UK - Email Received (Rate Test)',
            'description': 'UK email received - rate limiting test',
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
            'name': 'UK_Active_Push_RateTest',
            'display_name': 'UK - Active Push (Rate Test)',
            'description': 'UK active push - rate limiting test',
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
        }
    ]
    
    successful_segments = []
    failed_segments = []
    
    print(f"🧪 Testing {len(test_segments)} segments with 3-second delays...")
    print()
    
    for i, segment_def in enumerate(test_segments, 1):
        print(f"{i}. Creating: {segment_def['display_name']}")
        
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
                print(f"   ✅ SUCCESS: {result.get('status', 'unknown')} (Response time: {response_time:.2f}s)")
                successful_segments.append({
                    'segment': segment_def['display_name'],
                    'status': result.get('status', 'unknown'),
                    'response_time': response_time
                })
            elif isinstance(result, dict) and 'error' in result:
                print(f"   ❌ ERROR: {result['error']} (Response time: {response_time:.2f}s)")
                failed_segments.append({
                    'segment': segment_def['display_name'],
                    'error': result['error'],
                    'response_time': response_time
                })
            else:
                print(f"   ⚠️  UNEXPECTED: {result} (Response time: {response_time:.2f}s)")
                failed_segments.append({
                    'segment': segment_def['display_name'],
                    'error': f"Unexpected result: {result}",
                    'response_time': response_time
                })
                
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"   💥 EXCEPTION: {str(e)} (Response time: {response_time:.2f}s)")
            failed_segments.append({
                'segment': segment_def['display_name'],
                'error': str(e),
                'response_time': response_time
            })
        
        # Add delay between requests to avoid rate limiting
        if i < len(test_segments):  # Don't delay after the last request
            print(f"   ⏳ Waiting 3 seconds before next request...")
            time.sleep(3)
        
        print()
    
    print(f"📊 RESULTS:")
    print(f"✅ Successful: {len(successful_segments)}")
    print(f"❌ Failed: {len(failed_segments)}")
    
    if successful_segments:
        print(f"\n✅ SUCCESSFUL SEGMENTS:")
        avg_response_time = sum(s['response_time'] for s in successful_segments) / len(successful_segments)
        print(f"   Average response time: {avg_response_time:.2f}s")
        for seg in successful_segments:
            print(f"   - {seg['segment']}: {seg['status']} ({seg['response_time']:.2f}s)")
    
    if failed_segments:
        print(f"\n❌ FAILED SEGMENTS:")
        for seg in failed_segments:
            print(f"   - {seg['segment']}: {seg['error']} ({seg['response_time']:.2f}s)")
    
    return {
        'successful': successful_segments,
        'failed': failed_segments,
        'total_tested': len(test_segments)
    }

if __name__ == "__main__":
    result = test_rate_limiting_with_delays()
    
    print(f"\n🎯 RATE LIMITING ANALYSIS:")
    success_rate = len(result['successful']) / result['total_tested'] * 100
    print(f"Success rate with delays: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 HIGH SUCCESS RATE: Rate limiting is likely the issue!")
        print("💡 SOLUTION: Add delays between API calls in the main function")
    elif success_rate >= 50:
        print("⚠️  MODERATE SUCCESS: Rate limiting might be part of the issue")
    else:
        print("❌ LOW SUCCESS RATE: Rate limiting is probably not the main issue")