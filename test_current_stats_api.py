#!/usr/bin/env python3
"""
Test the current Stats API implementation to show exact error
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import CommsPerUserAutomation

def test_stats_api_error():
    """Test Stats API and show the exact error message"""
    
    print("🧪 TESTING CURRENT STATS API IMPLEMENTATION")
    print("=" * 60)
    
    # Create automation instance
    automation = CommsPerUserAutomation()
    
    # Test Stats API with January 2026 date range
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    print(f"Testing Stats API with date range: {start_date} to {end_date}")
    print("Using the same authentication method as your web app...")
    
    # Call the Stats API method directly
    result = automation.try_stats_api_first(start_date, end_date)
    
    print("\n" + "=" * 60)
    print("📊 RESULT:")
    
    if result:
        print("✅ Stats API is working!")
        print(f"UK Transactional PN: {result.get('uk_transactional_pn', 0):,}")
        print(f"UK Transactional Email: {result.get('uk_transactional_email', 0):,}")
        print(f"UK Promotional PN: {result.get('uk_promotional_pn', 0):,}")
        print(f"UK Promotional Email: {result.get('uk_promotional_email', 0):,}")
        print(f"UAE Transactional PN: {result.get('uae_transactional_pn', 0):,}")
        print(f"UAE Transactional Email: {result.get('uae_transactional_email', 0):,}")
        print(f"UAE Promotional PN: {result.get('uae_promotional_pn', 0):,}")
        print(f"UAE Promotional Email: {result.get('uae_promotional_email', 0):,}")
    else:
        print("❌ Stats API is not working")
        print("\nThis means one of the following:")
        print("1. Stats API is not enabled for your MoEngage account (most likely)")
        print("2. Authentication issue")
        print("3. API endpoint or parameters incorrect")
        
        print("\n💡 NEXT STEPS:")
        print("1. Contact MoEngage support to enable Stats API")
        print("2. Request access to advanced API features")
        print("3. Once enabled, your web app will automatically use Stats API")
        print("4. Until then, it will continue using Reports API as fallback")

if __name__ == "__main__":
    test_stats_api_error()