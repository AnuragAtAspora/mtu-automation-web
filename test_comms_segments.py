#!/usr/bin/env python3
"""
Test the Communications Per User segment creation
"""

from app import CommsPerUserAutomation
from datetime import datetime

def test_segment_creation():
    print("🧪 Testing Communications Per User Segment Creation")
    print("=" * 50)
    
    # Initialize automation
    comms_automation = CommsPerUserAutomation()
    
    # Test with January 2026 (month start to end)
    end_date = "2026-01-31"
    
    print(f"📅 Testing segment creation for period ending: {end_date}")
    
    try:
        # Step 1: Create segments (no manual counts)
        result = comms_automation.calculate_comms_per_user(end_date)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        if result.get('step') == 'segments_created':
            print(f"✅ Segments created successfully!")
            print(f"📊 Period: {result['segments']['period']}")
            print()
            
            # Display segment info
            segments = result['segments']
            
            print("🇬🇧 UK SEGMENTS:")
            print(f"  Total Users: {segments['uk_total_segment']['name']}")
            print(f"  URL: {segments['uk_total_segment']['url']}")
            print(f"  Transacted Users: {segments['uk_transacted_segment']['name']}")
            print(f"  URL: {segments['uk_transacted_segment']['url']}")
            print()
            
            print("🇦🇪 UAE SEGMENTS:")
            print(f"  Total Users: {segments['uae_total_segment']['name']}")
            print(f"  URL: {segments['uae_total_segment']['url']}")
            print(f"  Transacted Users: {segments['uae_transacted_segment']['name']}")
            print(f"  URL: {segments['uae_transacted_segment']['url']}")
            print()
            
            # Test Step 2 with sample manual counts
            print("🧪 Testing Step 2 with sample user counts...")
            manual_counts = {
                'uk_total_users': 289564,
                'uk_transacted_users': 125659,
                'uae_total_users': 598837,
                'uae_transacted_users': 247692
            }
            
            final_result = comms_automation.calculate_comms_per_user(end_date, manual_counts)
            
            if 'error' in final_result:
                print(f"❌ Step 2 Error: {final_result['error']}")
                return False
            
            print(f"✅ Step 2 successful!")
            print(f"📊 Final Results Period: {final_result['period']}")
            
            # Display sample results
            print("\n🇬🇧 UK RESULTS:")
            print(f"  Transactional PN per User: {final_result['uk']['transactional_pn']:.4f}")
            print(f"  Promotional PN per User: {final_result['uk']['promotional_pn']:.4f}")
            
            print("\n🇦🇪 UAE RESULTS:")
            print(f"  Transactional PN per User: {final_result['uae']['transactional_pn']:.4f}")
            print(f"  Promotional PN per User: {final_result['uae']['promotional_pn']:.4f}")
            
            return True
        else:
            print(f"❌ Unexpected result: {result}")
            return False
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_segment_creation()
    
    if success:
        print("\n🎉 Communications Per User with Segmentation API is working correctly!")
        print("The two-step process (segments → manual counts → calculation) is ready.")
    else:
        print("\n❌ Communications Per User segment creation failed.")
        print("Please check the error messages above.")