#!/usr/bin/env python3
"""
Test the updated create_metrics_segments function
"""

import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta

# Import the function
from app import create_metrics_segments

print("=" * 70)
print("TESTING UPDATED create_metrics_segments FUNCTION")
print("=" * 70)
print()

# Test with sample dates
start_date = "2026-02-01"
end_date = "2026-02-05"

print(f"Test parameters:")
print(f"  Start date: {start_date}")
print(f"  End date: {end_date}")
print()

try:
    # Call the function (it won't actually create segments, just build the definitions)
    print("Calling create_metrics_segments...")
    result = create_metrics_segments(start_date, end_date)
    
    print(f"✅ Function executed successfully!")
    print()
    print(f"Result structure:")
    print(f"  - segments: {len(result.get('segments', []))} segments")
    print(f"  - segment_ids: {len(result.get('segment_ids', []))} IDs")
    print()
    
    # Check a few key segments
    segments = result.get('segments', [])
    
    if segments:
        print("Sample segment names:")
        for seg in segments[:5]:
            print(f"  - {seg.get('display_name', 'N/A')}")
        print(f"  ... and {len(segments) - 5} more")
    else:
        print("⚠️  No segments returned (this is expected if not actually creating them)")
    
    print()
    print("=" * 70)
    print("✅ FUNCTION TEST PASSED - No syntax errors!")
    print("=" * 70)
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
