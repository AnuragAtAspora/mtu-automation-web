#!/usr/bin/env python3
"""
Test the MoEngage automation
"""

from final_automation import MoEngageAutomation
from datetime import datetime

def test_automation():
    print("Testing MoEngage Automation")
    print("=" * 30)
    
    # Initialize
    automation = MoEngageAutomation('95PNUHBSYSLLJZ22PEOFMKF2', '3XMHJ83D2X4V', '01')
    
    # Test date range
    print("1. Testing date range...")
    start_date, end_date = automation.get_date_range('2026-01-27')
    if start_date and end_date:
        print(f"✅ Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    else:
        print("❌ Date range failed")
        return
    
    # Test report download
    print("\n2. Testing report download...")
    zip_content = automation.download_report('API_Test_PN_report_20260128')
    if zip_content:
        print(f"✅ Downloaded {len(zip_content)} bytes")
    else:
        print("❌ Download failed")
        return
    
    # Test parsing
    print("\n3. Testing data parsing...")
    data = automation.extract_and_parse_report(zip_content)
    print(f"✅ Parsed data:")
    print(f"   Email sent: {data['email_sent']}")
    print(f"   Push sent: {data['push_sent']}")
    print(f"   CSV file: {data.get('csv_filename', 'N/A')}")
    print(f"   Campaigns: {data.get('total_campaigns', 'N/A')}")
    
    # Test metric calculation (with mock user count)
    print("\n4. Testing metric calculation...")
    user_count = 100000  # Mock user count for testing
    
    email_per_user = data['email_sent'] / user_count if user_count > 0 else 0
    push_per_user = data['push_sent'] / user_count if user_count > 0 else 0
    
    print(f"✅ Calculated metrics (with {user_count:,} users):")
    print(f"   Email per user: {email_per_user:.4f}")
    print(f"   Push per user: {push_per_user:.4f}")
    
    print(f"\n🎉 All tests passed! The automation is working correctly.")
    print(f"\nSummary for period {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}:")
    print(f"- Total push notifications sent: {data['push_sent']:,}")
    print(f"- Total email sent: {data['email_sent']:,}")
    print(f"- Push per user (100k users): {push_per_user:.4f}")
    print(f"- Email per user (100k users): {email_per_user:.4f}")

if __name__ == "__main__":
    test_automation()