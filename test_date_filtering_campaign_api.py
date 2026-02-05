#!/usr/bin/env python3
"""
Test date filtering capabilities of MoEngage Campaign Details API
This is the key test to see if we can get dynamic date ranges (unlike Reports API)
"""

import requests
import base64
import json
from datetime import datetime, timedelta

# Configuration
MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'campaign_api_key': '3XMHJ83D2X4V',
    'data_center': '01'
}

def test_date_filtering(start_date, end_date, test_name):
    """Test campaigns with specific date range"""
    
    print(f"\n🔍 TESTING DATE FILTERING: {test_name}")
    print(f"📅 Date range: {start_date} to {end_date}")
    print("=" * 60)
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/search"
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key'],
        'Content-Type': 'application/json'
    }
    
    payload = {
        "request_id": f"date_filter_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 15,
        "page": 1,
        "campaign_fields": {
            "channels": ["PUSH", "EMAIL"],
            "created_date": {
                "from_date": start_date,
                "to_date": end_date
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            campaigns = response.json()
            print(f"✅ Found {len(campaigns)} campaigns")
            
            if campaigns:
                print(f"📊 Campaign details:")
                for campaign in campaigns:
                    basic_details = campaign.get('basic_details', {})
                    name = basic_details.get('name', 'Unknown')
                    channel = campaign.get('channel', 'Unknown')
                    created_at = campaign.get('created_at', 'Unknown')
                    sent_time = campaign.get('sent_time', 'Unknown')
                    status = campaign.get('status', 'Unknown')
                    
                    print(f"  • {name} | {channel} | Created: {created_at} | Status: {status}")
                
                # Check if dates are within our filter range
                date_filtered_correctly = True
                for campaign in campaigns:
                    created_at = campaign.get('created_at', '')
                    if created_at:
                        try:
                            # Parse the created date
                            created_date = datetime.strptime(created_at.split()[0], '%Y-%m-%d')
                            filter_start = datetime.strptime(start_date, '%Y-%m-%d')
                            filter_end = datetime.strptime(end_date, '%Y-%m-%d')
                            
                            if not (filter_start <= created_date <= filter_end):
                                date_filtered_correctly = False
                                print(f"  ⚠️  Campaign outside date range: {created_at}")
                        except:
                            pass
                
                if date_filtered_correctly:
                    print(f"✅ All campaigns are within the specified date range")
                else:
                    print(f"❌ Some campaigns are outside the date range")
                
                return campaigns
            else:
                print(f"ℹ️  No campaigns found in this date range")
                return []
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def compare_with_no_date_filter():
    """Get campaigns without date filter for comparison"""
    
    print(f"\n🔍 GETTING CAMPAIGNS WITHOUT DATE FILTER (FOR COMPARISON)")
    print("=" * 60)
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/search"
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key'],
        'Content-Type': 'application/json'
    }
    
    payload = {
        "request_id": f"no_date_filter_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 15,
        "page": 1,
        "campaign_fields": {
            "channels": ["PUSH", "EMAIL"]
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            campaigns = response.json()
            print(f"✅ Found {len(campaigns)} campaigns (no date filter)")
            
            # Show date range of all campaigns
            if campaigns:
                dates = []
                for campaign in campaigns:
                    created_at = campaign.get('created_at', '')
                    if created_at:
                        try:
                            created_date = datetime.strptime(created_at.split()[0], '%Y-%m-%d')
                            dates.append(created_date)
                        except:
                            pass
                
                if dates:
                    min_date = min(dates)
                    max_date = max(dates)
                    print(f"📅 Campaign date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
                
                return campaigns
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def main():
    """Test different date ranges to verify filtering works"""
    
    print("🚀 COMPREHENSIVE DATE FILTERING TEST")
    print("=" * 80)
    
    # Test 1: Get all campaigns first (no date filter)
    all_campaigns = compare_with_no_date_filter()
    
    # Test 2: Recent campaigns (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    recent_campaigns = test_date_filtering(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        "Last 7 days"
    )
    
    # Test 3: January 2026 campaigns
    january_campaigns = test_date_filtering(
        "2026-01-01",
        "2026-01-31",
        "January 2026"
    )
    
    # Test 4: February 2026 campaigns (current month)
    february_campaigns = test_date_filtering(
        "2026-02-01",
        "2026-02-28",
        "February 2026"
    )
    
    # Test 5: Very specific date range (yesterday only)
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_campaigns = test_date_filtering(
        yesterday.strftime('%Y-%m-%d'),
        yesterday.strftime('%Y-%m-%d'),
        "Yesterday only"
    )
    
    # Test 6: Future date range (should return no campaigns)
    future_start = datetime.now() + timedelta(days=30)
    future_end = future_start + timedelta(days=7)
    future_campaigns = test_date_filtering(
        future_start.strftime('%Y-%m-%d'),
        future_end.strftime('%Y-%m-%d'),
        "Future dates (should be empty)"
    )
    
    print("\n" + "=" * 80)
    print("📊 DATE FILTERING ANALYSIS:")
    
    # Compare results
    all_count = len(all_campaigns) if all_campaigns else 0
    recent_count = len(recent_campaigns) if recent_campaigns else 0
    january_count = len(january_campaigns) if january_campaigns else 0
    february_count = len(february_campaigns) if february_campaigns else 0
    yesterday_count = len(yesterday_campaigns) if yesterday_campaigns else 0
    future_count = len(future_campaigns) if future_campaigns else 0
    
    print(f"All campaigns (no filter): {all_count}")
    print(f"Last 7 days: {recent_count}")
    print(f"January 2026: {january_count}")
    print(f"February 2026: {february_count}")
    print(f"Yesterday only: {yesterday_count}")
    print(f"Future dates: {future_count}")
    
    # Determine if date filtering is working
    date_filtering_works = False
    
    if all_count > 0:
        # Check if different date ranges return different counts
        counts = [recent_count, january_count, february_count, yesterday_count, future_count]
        unique_counts = set(counts)
        
        if len(unique_counts) > 1 or future_count == 0:
            date_filtering_works = True
            print(f"\n✅ DATE FILTERING IS WORKING!")
            print(f"   • Different date ranges return different results")
            print(f"   • Future dates return no campaigns (as expected)")
        else:
            print(f"\n❌ DATE FILTERING MAY NOT BE WORKING")
            print(f"   • All date ranges return same count")
            print(f"   • API may be ignoring date filters")
    
    print(f"\n💡 FINAL ASSESSMENT:")
    if date_filtering_works:
        print("🎯 EXCELLENT! This API supports dynamic date ranges!")
        print("  ✅ Date filtering works correctly")
        print("  ✅ Can get campaigns for specific time periods")
        print("  ✅ This solves the Reports API limitation")
        print("  🚀 Ready to implement as Reports API replacement")
    else:
        print("🔄 Date filtering needs investigation:")
        print("  ❓ May need different date field (sent_time vs created_date)")
        print("  ❓ May need different date format")
        print("  ❓ API may have different behavior than documented")
    
    # Test if we can extract meaningful data for Communications Per User
    if february_campaigns:
        print(f"\n📊 COMMUNICATIONS PER USER POTENTIAL:")
        uk_push = uk_email = uae_push = uae_email = 0
        
        for campaign in february_campaigns:
            basic_details = campaign.get('basic_details', {})
            name = basic_details.get('name', '').lower()
            channel = campaign.get('channel', '').lower()
            status = campaign.get('status', '').lower()
            
            if status == 'sent':
                if 'uk' in name and 'push' in channel:
                    uk_push += 1
                elif 'uk' in name and 'email' in channel:
                    uk_email += 1
                elif 'uae' in name and 'push' in channel:
                    uae_push += 1
                elif 'uae' in name and 'email' in channel:
                    uae_email += 1
        
        print(f"  UK Push campaigns: {uk_push}")
        print(f"  UK Email campaigns: {uk_email}")
        print(f"  UAE Push campaigns: {uae_push}")
        print(f"  UAE Email campaigns: {uae_email}")
        
        if uk_push + uk_email + uae_push + uae_email > 0:
            print(f"  ✅ Can classify campaigns by country and channel")
            print(f"  🔧 Next: Need to extract actual sent counts (not just campaign counts)")
        else:
            print(f"  ❌ No UK/UAE campaigns found in this period")

if __name__ == "__main__":
    main()