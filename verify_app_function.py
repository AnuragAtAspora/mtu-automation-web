#!/usr/bin/env python3
"""
Verify that the app.py function is actually using the new code
"""

import sys
import os

# Remove any cached modules
if 'app' in sys.modules:
    del sys.modules['app']

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import fresh
from app import create_metrics_segments
import inspect

print("🔍 VERIFYING app.py create_metrics_segments FUNCTION")
print("=" * 70)

# Check the function source code
source = inspect.getsource(create_metrics_segments)

print("📝 Function signature:")
print(f"   {inspect.signature(create_metrics_segments)}")
print()

# Check if it has the new structure
if 'uk_segments = [' in source:
    print("✅ Function has NEW structure (direct segment definitions)")
elif 'segment_definitions = [' in source:
    print("⚠️  Function has OLD structure (nested loops)")
else:
    print("❓ Function structure unclear")

print()

# Check for rate limiting
if 'time.sleep(2)' in source:
    print("✅ Function includes 2-second delays for rate limiting")
else:
    print("❌ Function missing rate limiting delays")

print()

# Check for all 16 segments
segment_count = source.count("'name':")
print(f"📊 Segment definitions found in source: {segment_count}")

if segment_count >= 8:
    print("✅ Function defines at least 8 UK segments")
else:
    print("❌ Function missing segment definitions")

print()
print("🧪 Now testing actual execution...")
print()

result = create_metrics_segments("2026-01-01", "2026-01-31")

print(f"📊 EXECUTION RESULT:")
print(f"   Segments returned: {len(result.get('segments', []))}")
print(f"   Expected: 16")

if len(result.get('segments', [])) == 16:
    print("   ✅ SUCCESS: All 16 segments returned!")
elif len(result.get('segments', [])) >= 8:
    print(f"   ⚠️  PARTIAL: Only {len(result.get('segments', []))} segments returned")
else:
    print(f"   ❌ FAILURE: Only {len(result.get('segments', []))} segments returned")

print()
print("📋 Returned segments:")
for i, seg in enumerate(result.get('segments', []), 1):
    print(f"   {i:2d}. {seg.get('display_name', 'Unknown')}")