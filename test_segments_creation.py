#!/usr/bin/env python3
"""
Test the segments creation to see what's returned
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import automation
from datetime import datetime, timedelta

def test_create_metrics_segments():
    """Test the create_metrics_segments function"""
    
    print("🧪 Testing create_metrics_segments function")
    print("=" * 50)
    
    # Test with sample dates
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    print(f"📅 Testing with dates: {start_date} to {end_date}")
    
    # Import the function from app
    try:
        from app import create_metrics_segments
        
        result = create_metrics_segments(start_date, end_date)
        
        print(f"\n📊 RESULT:")
        print(f"Type: {type(result)}")
        print(f"Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if 'segments' in result:
            segments = result['segments']
            print(f"\n✅ Found {len(segments)} segments:")
            
            for i, segment in enumerate(segments, 1):
                print(f"{i:2d}. {segment.get('display_name', 'Unknown')}")
                print(f"    Name: {segment.get('name', 'Unknown')}")
                print(f"    ID: {segment.get('id', 'Unknown')}")
                print(f"    Status: {segment.get('status', 'Unknown')}")
                print(f"    Field: {segment.get('field_name', 'Unknown')}")
                print(f"    URL: {segment.get('url', 'No URL')}")
                print()
        
        if 'segment_ids' in result:
            segment_ids = result['segment_ids']
            print(f"🆔 Segment IDs: {len(segment_ids)} found")
            for sid in segment_ids[:5]:  # Show first 5
                print(f"   - {sid}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_create_metrics_segments()