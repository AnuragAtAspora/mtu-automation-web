#!/usr/bin/env python3
"""
Test the newly updated create_metrics_segments function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Force reload the module to get the updated function
import importlib
import app
importlib.reload(app)

from app import create_metrics_segments

def test_new_function():
    """Test the newly updated create_metrics_segments function"""
    
    print("🔄 TESTING NEWLY UPDATED create_metrics_segments FUNCTION")
    print("=" * 70)
    
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    print(f"📅 Date Range: {start_date} to {end_date}")
    print(f"⏱️  Function should now include 2-second delays")
    print()
    
    try:
        print("🚀 Calling create_metrics_segments...")
        result = create_metrics_segments(start_date, end_date)
        
        print(f"\n📊 RESULT:")
        print(f"Type: {type(result)}")
        print(f"Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if 'segments' in result:
            segments = result['segments']
            print(f"\n✅ Total segments returned: {len(segments)}")
            
            # Group by country
            uk_segments = [s for s in segments if 'UK' in s.get('display_name', '')]
            uae_segments = [s for s in segments if 'UAE' in s.get('display_name', '')]
            
            print(f"🇬🇧 UK Segments: {len(uk_segments)}")
            print(f"🇦🇪 UAE Segments: {len(uae_segments)}")
            
            print(f"\n📋 ALL SEGMENTS:")
            for i, segment in enumerate(segments, 1):
                print(f"{i:2d}. {segment.get('display_name', 'Unknown')}")
                print(f"    Field: {segment.get('field_name', 'Unknown')}")
                print(f"    Status: {segment.get('status', 'Unknown')}")
                print(f"    ID: {segment.get('id', 'Unknown')}")
                print()
            
            # Check expected fields
            expected_fields = [
                'uk_total_users', 'uk_active_users', 'uk_push_received', 'uk_email_received',
                'uk_push_received_active', 'uk_email_received_active', 'uk_push_unsubscribed', 'uk_email_unsubscribed',
                'uae_total_users', 'uae_active_users', 'uae_push_received', 'uae_email_received',
                'uae_push_received_active', 'uae_email_received_active', 'uae_push_unsubscribed', 'uae_email_unsubscribed'
            ]
            
            found_fields = [s.get('field_name', '') for s in segments]
            missing_fields = [f for f in expected_fields if f not in found_fields]
            
            if missing_fields:
                print(f"❌ MISSING FIELDS ({len(missing_fields)}):")
                for field in missing_fields:
                    print(f"   - {field}")
            else:
                print(f"✅ ALL FIELDS FOUND!")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_new_function()
    
    if result and 'segments' in result:
        total_segments = len(result['segments'])
        print(f"\n🎯 FINAL RESULT:")
        print(f"Expected: 16 segments")
        print(f"Actual: {total_segments} segments")
        print(f"Success rate: {total_segments/16*100:.1f}%")
        
        if total_segments == 16:
            print("🎉 PERFECT: All 16 segments found!")
        elif total_segments >= 12:
            print("🎊 EXCELLENT: Most segments found!")
        elif total_segments >= 8:
            print("⚠️  PARTIAL: Some segments found")
        else:
            print("❌ POOR: Few segments found")
    else:
        print("💀 CRITICAL: No result returned")