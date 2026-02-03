#!/usr/bin/env python3
"""
Test the complete Communications Per User calculation workflow
"""

from app import CommsPerUserAutomation
from datetime import datetime

def test_comms_calculation():
    print("🧪 Testing Communications Per User Calculation")
    print("=" * 50)
    
    # Initialize automation
    comms_automation = CommsPerUserAutomation()
    
    # Test with January 2026 (month start to end)
    end_date = "2026-01-31"
    
    print(f"📅 Testing calculation for period ending: {end_date}")
    
    try:
        result = comms_automation.calculate_comms_per_user(end_date)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print(f"✅ Calculation successful!")
        print(f"📊 Period: {result['period']}")
        print()
        
        # Display UK results
        print("🇬🇧 UK RESULTS:")
        print(f"  Transactional PN per User: {result['uk']['transactional_pn']:.4f}")
        print(f"  Transactional Email per User: {result['uk']['transactional_email']:.4f}")
        print(f"  Promotional PN per User: {result['uk']['promotional_pn']:.4f}")
        print(f"  Promotional Email per User: {result['uk']['promotional_email']:.4f}")
        print(f"  Total Users: {result['uk']['total_users']:,}")
        print(f"  Transacted Users: {result['uk']['transacted_users']:,}")
        print()
        
        # Display UAE results
        print("🇦🇪 UAE RESULTS:")
        print(f"  Transactional PN per User: {result['uae']['transactional_pn']:.4f}")
        print(f"  Transactional Email per User: {result['uae']['transactional_email']:.4f}")
        print(f"  Promotional PN per User: {result['uae']['promotional_pn']:.4f}")
        print(f"  Promotional Email per User: {result['uae']['promotional_email']:.4f}")
        print(f"  Total Users: {result['uae']['total_users']:,}")
        print(f"  Transacted Users: {result['uae']['transacted_users']:,}")
        print()
        
        # Display raw counts
        print("📈 RAW COMMUNICATION COUNTS:")
        print("UK:")
        for comm_type, count in result['uk']['raw_counts'].items():
            print(f"  {comm_type}: {count:,}")
        print("UAE:")
        for comm_type, count in result['uae']['raw_counts'].items():
            print(f"  {comm_type}: {count:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_comms_calculation()
    
    if success:
        print("\n🎉 Communications Per User calculation is working correctly!")
        print("The web interface should now work properly.")
    else:
        print("\n❌ Communications Per User calculation failed.")
        print("Please check the error messages above.")