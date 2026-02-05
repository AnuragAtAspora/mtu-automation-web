#!/usr/bin/env python3
"""
Test to verify segment creation and display logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_metrics_segments

def test_segment_display():
    """Test the create_metrics_segments function and verify all segments are returned"""
    
    print("🧪 Testing create_metrics_segments function")
    print("=" * 60)
    
    # Test with sample dates
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    print(f"📅 Testing with dates: {start_date} to {end_date}")
    
    try:
        result = create_metrics_segments(start_date, end_date)
        
        print(f"\n📊 RESULT:")
        print(f"Type: {type(result)}")
        print(f"Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if 'segments' in result:
            segments = result['segments']
            print(f"\n✅ Found {len(segments)} segments:")
            
            uk_segments = []
            uae_segments = []
            
            for i, segment in enumerate(segments, 1):
                print(f"{i:2d}. {segment.get('display_name', 'Unknown')}")
                print(f"    Name: {segment.get('name', 'Unknown')}")
                print(f"    ID: {segment.get('id', 'Unknown')}")
                print(f"    Status: {segment.get('status', 'Unknown')}")
                print(f"    Field: {segment.get('field_name', 'Unknown')}")
                print(f"    URL: {segment.get('url', 'No URL')}")
                
                # Categorize by country
                if 'UK' in segment.get('name', ''):
                    uk_segments.append(segment)
                elif 'UAE' in segment.get('name', ''):
                    uae_segments.append(segment)
                print()
            
            print(f"🇬🇧 UK Segments: {len(uk_segments)}")
            print(f"🇦🇪 UAE Segments: {len(uae_segments)}")
            print(f"🎯 Expected: 8 segments per country (16 total)")
            
            # Check if we have all expected segment types
            expected_types = [
                'All_Users', 'Active_Users', 'Received_Push', 'Received_Email',
                'Active_Received_Push', 'Active_Received_Email', 
                'Unsubscribed_Push', 'Unsubscribed_Email'
            ]
            
            for country, segments_list in [('UK', uk_segments), ('UAE', uae_segments)]:
                print(f"\n{country} Segment Analysis:")
                found_types = []
                for segment in segments_list:
                    name = segment.get('name', '')
                    for expected_type in expected_types:
                        if expected_type in name:
                            found_types.append(expected_type)
                            break
                
                print(f"  Found types: {found_types}")
                missing_types = [t for t in expected_types if t not in found_types]
                if missing_types:
                    print(f"  ❌ Missing types: {missing_types}")
                else:
                    print(f"  ✅ All segment types found!")
        
        if 'segment_ids' in result:
            segment_ids = result['segment_ids']
            print(f"\n🆔 Segment IDs: {len(segment_ids)} found")
            valid_ids = [sid for sid in segment_ids if sid != 'unknown']
            print(f"🆔 Valid IDs: {len(valid_ids)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_segment_display()