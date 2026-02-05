#!/usr/bin/env python3
"""
Test the full create_metrics_segments function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_metrics_segments
from datetime import datetime

def test_full_function():
    """Test the actual create_metrics_segments function"""
    
    print("🧪 Testing Full create_metrics_segments Function")
    print("=" * 60)
    
    # Test with January 2026 date range
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    print(f"📅 Date Range: {start_date} to {end_date}")
    
    try:
        result = create_metrics_segments(start_date, end_date)
        
        print(f"📊 Function returned: {type(result)}")
        
        if isinstance(result, dict):
            if 'error' in result:
                print(f"❌ ERROR: {result['error']}")
                return False
            
            segments = result.get('segments', [])
            segment_ids = result.get('segment_ids', [])
            
            print(f"✅ SUCCESS: {len(segments)} segments returned")
            print(f"🆔 Segment IDs: {len(segment_ids)} IDs")
            
            print("\n📋 Segments Details:")
            for i, segment in enumerate(segments, 1):
                print(f"  {i}. {segment.get('display_name', 'Unknown')}")
                print(f"     Name: {segment.get('name', 'Unknown')}")
                print(f"     Field: {segment.get('field_name', 'Unknown')}")
                print(f"     Status: {segment.get('status', 'Unknown')}")
                print(f"     ID: {segment.get('id', 'Unknown')}")
                print()
            
            return len(segments) > 0
        else:
            print(f"❌ Unexpected return type: {type(result)}")
            print(f"Content: {result}")
            return False
            
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_function()
    
    if success:
        print("🎉 Full function test PASSED!")
    else:
        print("❌ Full function test FAILED!")