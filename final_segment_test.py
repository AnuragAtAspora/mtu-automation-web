#!/usr/bin/env python3
"""
Final comprehensive test to understand and fix the segment display issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_metrics_segments

def test_final_segments():
    """Test the create_metrics_segments function and show exactly what's returned"""
    
    print("🎯 FINAL COMPREHENSIVE SEGMENT TEST")
    print("=" * 70)
    
    # Test with sample dates
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    print(f"📅 Testing with dates: {start_date} to {end_date}")
    
    try:
        result = create_metrics_segments(start_date, end_date)
        
        print(f"\n📊 FUNCTION RESULT:")
        print(f"Type: {type(result)}")
        print(f"Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if 'segments' in result:
            segments = result['segments']
            print(f"\n✅ Total segments returned: {len(segments)}")
            
            # Group by country using display_name (like the template does)
            uk_segments = [s for s in segments if 'UK' in s.get('display_name', '')]
            uae_segments = [s for s in segments if 'UAE' in s.get('display_name', '')]
            
            print(f"\n🇬🇧 UK Segments (by display_name): {len(uk_segments)}")
            for i, segment in enumerate(uk_segments, 1):
                print(f"{i:2d}. Display: {segment.get('display_name', 'Unknown')}")
                print(f"    Name: {segment.get('name', 'Unknown')}")
                print(f"    Field: {segment.get('field_name', 'Unknown')}")
                print(f"    Status: {segment.get('status', 'Unknown')}")
                print(f"    ID: {segment.get('id', 'Unknown')}")
                print()
            
            print(f"🇦🇪 UAE Segments (by display_name): {len(uae_segments)}")
            for i, segment in enumerate(uae_segments, 1):
                print(f"{i:2d}. Display: {segment.get('display_name', 'Unknown')}")
                print(f"    Name: {segment.get('name', 'Unknown')}")
                print(f"    Field: {segment.get('field_name', 'Unknown')}")
                print(f"    Status: {segment.get('status', 'Unknown')}")
                print(f"    ID: {segment.get('id', 'Unknown')}")
                print()
            
            # Check what segment types we have
            print(f"📋 SEGMENT TYPES ANALYSIS:")
            expected_fields = [
                'uk_total_users', 'uk_active_users', 'uk_push_received', 'uk_email_received',
                'uk_push_received_active', 'uk_email_received_active', 'uk_push_unsubscribed', 'uk_email_unsubscribed',
                'uae_total_users', 'uae_active_users', 'uae_push_received', 'uae_email_received',
                'uae_push_received_active', 'uae_email_received_active', 'uae_push_unsubscribed', 'uae_email_unsubscribed'
            ]
            
            found_fields = [s.get('field_name', '') for s in segments]
            
            print(f"Expected fields: {len(expected_fields)}")
            print(f"Found fields: {len(found_fields)}")
            
            missing_fields = [f for f in expected_fields if f not in found_fields]
            if missing_fields:
                print(f"\n❌ MISSING FIELDS:")
                for field in missing_fields:
                    print(f"   - {field}")
            else:
                print(f"\n✅ ALL FIELDS FOUND!")
            
            print(f"\n📝 FOUND FIELDS:")
            for field in found_fields:
                print(f"   - {field}")
        
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
    result = test_final_segments()
    
    if result and 'segments' in result:
        total_segments = len(result['segments'])
        print(f"\n🎯 FINAL SUMMARY:")
        print(f"Expected: 16 segments (8 per country)")
        print(f"Actual: {total_segments} segments")
        
        if total_segments == 16:
            print("🎉 SUCCESS: All segments found!")
        elif total_segments >= 8:
            print("⚠️  PARTIAL: Some segments found, but not all")
        else:
            print("❌ FAILURE: Very few segments found")
    else:
        print("💀 CRITICAL: No segments returned")