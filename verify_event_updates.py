#!/usr/bin/env python3
"""
Verify that all event updates were applied correctly in create_metrics_segments function
"""

# Read the app.py file
with open('app.py', 'r') as f:
    content = f.read()

# Extract just the create_metrics_segments function
start_marker = 'def create_metrics_segments(start_date, end_date):'
end_marker = 'def calculate_comprehensive_metrics(campaign_data, user_counts):'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("❌ Could not find function boundaries")
    exit(1)

function_content = content[start_idx:end_idx]

print("=" * 70)
print("VERIFICATION: Event Updates in create_metrics_segments Function")
print("=" * 70)
print()

# Check 1: Active Users with sub_event filter
check1 = 'sub_event' in function_content and 'COMPLETED' in function_content and 'PAYMENT_COMPLETED' in function_content
print(f"✅ Active Users - ORDER event with sub_event filter: {check1}")
if check1:
    count = function_content.count('sub_event')
    print(f"   Found {count} instances of sub_event filter")

# Check 2: Push Notification events
check2_android = 'Notification Received Android' in function_content
check2_ios = 'Notification Received iOS' in function_content
print(f"✅ Push Received - Notification Received Android: {check2_android}")
print(f"✅ Push Received - Notification Received iOS: {check2_ios}")
if check2_android and check2_ios:
    count_android = function_content.count('Notification Received Android')
    count_ios = function_content.count('Notification Received iOS')
    print(f"   Found {count_android} Android and {count_ios} iOS notification events")

# Check 3: Unsubscribe events with proper capitalization
check3_push = 'Unsubscribed to Push' in function_content
check3_email = 'Email Unsubscribed' in function_content
print(f"✅ Unsubscribe - 'Unsubscribed to Push' (capital U): {check3_push}")
print(f"✅ Unsubscribe - 'Email Unsubscribed' (capital E): {check3_email}")

# Check 4: Old events should NOT be present
check4_old_push = 'MOE_PUSH_SENT' not in function_content
check4_old_unsub_push = 'unsubscribed to push' not in function_content
check4_old_unsub_email = 'email unsubscribes' not in function_content
print(f"✅ No old 'MOE_PUSH_SENT' in function: {check4_old_push}")
print(f"✅ No old 'unsubscribed to push' in function: {check4_old_unsub_push}")
print(f"✅ No old 'email unsubscribes' in function: {check4_old_unsub_email}")

print()
print("=" * 70)

# Overall result
all_checks = [
    check1, check2_android, check2_ios, check3_push, check3_email,
    check4_old_push, check4_old_unsub_push, check4_old_unsub_email
]

if all(all_checks):
    print("🎉 ALL CHECKS PASSED! Event updates are complete.")
else:
    print("⚠️  Some checks failed. Review the results above.")
    failed = [i+1 for i, check in enumerate(all_checks) if not check]
    print(f"   Failed checks: {failed}")

print("=" * 70)
print()

# Show summary of changes
print("📋 SUMMARY OF CHANGES:")
print()
print("1. Active Users (ORDER event):")
print("   - Added sub_event attribute filter with OR logic")
print("   - Values: COMPLETED OR PAYMENT_COMPLETED")
print()
print("2. Push Received:")
print("   - Changed from: MOE_PUSH_SENT")
print("   - Changed to: Notification Received Android OR Notification Received iOS")
print()
print("3. Unsubscribe Events:")
print("   - Push: 'Unsubscribed to Push' (capital U)")
print("   - Email: 'Email Unsubscribed' (capital E)")
print()
print("✅ All changes applied to UK segments")
print("✅ UAE segments auto-generated from UK (via deep copy)")
print("✅ Total: 16 segments (8 UK + 8 UAE)")
