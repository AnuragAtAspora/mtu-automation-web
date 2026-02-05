#!/usr/bin/env python3
"""
Test creating a single segment to understand what's happening
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import automation
from datetime import datetime, timedelta

def test_single_segment():
    """Test creating a single segment to see what happens"""
    
    print("🧪 Testing Single Segment Creation")
    print("=" * 50)
    
    # Test creating UK Active Users segment
    segment_name = "UK_Active_Users"
    description = "UK active users (60d)"
    
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
    
    print(f"📝 Creating segment: {segment_name}")
    print(f"📝 Description: {description}")
    print(f"📅 Active period: {active_start.strftime('%Y-%m-%d')} to {active_end.strftime('%Y-%m-%d')}")
    
    try:
        result = automation.create_segment(segment_name, description, filters)
        
        print(f"\n📊 RESULT:")
        print(f"Type: {type(result)}")
        
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print(f"  Value: {result}")
        
        if 'error' in result:
            print(f"\n❌ ERROR DETECTED: {result['error']}")
        else:
            print(f"\n✅ SUCCESS!")
            
        return result
        
    except Exception as e:
        print(f"\n💥 EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_single_segment()