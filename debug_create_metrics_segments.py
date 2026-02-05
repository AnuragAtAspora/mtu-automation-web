#!/usr/bin/env python3
"""
Debug version of create_metrics_segments with detailed error logging
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import automation
from datetime import datetime, timedelta

def debug_create_metrics_segments(start_date, end_date):
    """Debug version of create_metrics_segments with detailed logging"""
    
    print("🧪 DEBUG: create_metrics_segments Function")
    print("=" * 60)
    print(f"📅 Date Range: {start_date} to {end_date}")
    
    segments = []
    countries = {'UK': 'GB', 'UAE': 'AE'}
    
    for country_name, country_code in countries.items():
        print(f"\n🌍 === Processing {country_name} ({country_code}) ===")
        
        # 1. Total users
        print(f"\n1️⃣ Creating Total Users segment...")
        segment_name = "UK_All_Users" if country_code == 'GB' else "UAE_All_Users"
        filters = {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
                    "negate": False,
                    "case_sensitive": False
                }
            ]
        }
        
        result = automation.create_segment(segment_name, f"All {country_name} users", filters)
        if 'error' not in result:
            result['display_name'] = f"{country_name} - All Users"
            result['field_name'] = f"{country_name.lower()}_total_users"
            segments.append(result)
            print(f"✅ SUCCESS: {result['display_name']} (Status: {result.get('status', 'unknown')})")
        else:
            print(f"❌ FAILED: {result['error']}")
        
        # 2. Active users (60 days)
        print(f"\n2️⃣ Creating Active Users segment...")
        segment_name = "UK_Active_Users" if country_code == 'GB' else "UAE_Active_Users"
        active_end = datetime.now()
        active_start = active_end - timedelta(days=60)
        
        filters = {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
                    "negate": False,
                    "case_sensitive": False
                },
                {
                    "filter_type": "actions",
                    "attributes": {
                        "filter_operator": "and",
                        "filters": []
                    },
                    "executed": True,
                    "primary_time_range": {
                        "type": "between",
                        "value": active_start.strftime('%Y-%m-%dT00:00:00.000Z'),
                        "value1": active_end.strftime('%Y-%m-%dT23:59:59.999Z'),
                        "value_type": "absolute",
                        "period_unit": "days"
                    },
                    "action_name": "ORDER",
                    "execution": {
                        "count": 1,
                        "type": "atleast"
                    }
                }
            ]
        }
        
        result = automation.create_segment(segment_name, f"{country_name} active users (60d)", filters)
        if 'error' not in result:
            result['display_name'] = f"{country_name} - Active Users"
            result['field_name'] = f"{country_name.lower()}_active_users"
            segments.append(result)
            print(f"✅ SUCCESS: {result['display_name']} (Status: {result.get('status', 'unknown')})")
        else:
            print(f"❌ FAILED: {result['error']}")
        
        # 3. Users who received push/email
        print(f"\n3️⃣ Creating Received Communications segments...")
        for channel, event_names in [('Push', ['MOE_PUSH_SENT']), ('Email', ['MOE_EMAIL_SENT'])]:
            print(f"  📱 Creating {channel} segment...")
            segment_name = f"UK_Received_{channel}" if country_code == 'GB' else f"UAE_Received_{channel}"
            
            filters = {
                "filter_operator": "and",
                "filters": [
                    {
                        "filter_type": "user_attributes",
                        "name": "country",
                        "data_type": "string",
                        "operator": "in",
                        "value": [country_code],
                        "negate": False,
                        "case_sensitive": False
                    },
                    {
                        "filter_type": "actions",
                        "attributes": {
                            "filter_operator": "and",
                            "filters": []
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": f"{start_date}T00:00:00.000Z",
                            "value1": f"{end_date}T23:59:59.999Z",
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": event_names[0],
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
            
            result = automation.create_segment(segment_name, f"{country_name} users who received {channel.lower()}", filters)
            if 'error' not in result:
                result['display_name'] = f"{country_name} - Received {channel}"
                result['field_name'] = f"{country_name.lower()}_{channel.lower()}_received"
                segments.append(result)
                print(f"  ✅ SUCCESS: {result['display_name']} (Status: {result.get('status', 'unknown')})")
            else:
                print(f"  ❌ FAILED: {result['error']}")
            
            # 4. Active users who received communications
            print(f"  🎯 Creating Active {channel} segment...")
            segment_name = f"UK_Active_Received_{channel}" if country_code == 'GB' else f"UAE_Active_Received_{channel}"
            
            # Define active period for this segment
            active_end_comm = datetime.now()
            active_start_comm = active_end_comm - timedelta(days=60)
            
            filters = {
                "filter_operator": "and",
                "filters": [
                    {
                        "filter_type": "user_attributes",
                        "name": "country",
                        "data_type": "string",
                        "operator": "in",
                        "value": [country_code],
                        "negate": False,
                        "case_sensitive": False
                    },
                    {
                        "filter_type": "actions",
                        "attributes": {
                            "filter_operator": "and",
                            "filters": []
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": f"{start_date}T00:00:00.000Z",
                            "value1": f"{end_date}T23:59:59.999Z",
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": event_names[0],
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    },
                    {
                        "filter_type": "actions",
                        "attributes": {
                            "filter_operator": "and",
                            "filters": []
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": active_start_comm.strftime('%Y-%m-%dT00:00:00.000Z'),
                            "value1": active_end_comm.strftime('%Y-%m-%dT23:59:59.999Z'),
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": "ORDER",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
            
            result = automation.create_segment(segment_name, f"{country_name} active users who received {channel.lower()}", filters)
            if 'error' not in result:
                result['display_name'] = f"{country_name} - Active Users Received {channel}"
                result['field_name'] = f"{country_name.lower()}_{channel.lower()}_received_active"
                segments.append(result)
                print(f"  ✅ SUCCESS: {result['display_name']} (Status: {result.get('status', 'unknown')})")
            else:
                print(f"  ❌ FAILED: {result['error']}")
        
        # 5. Users who unsubscribed from push/email
        print(f"\n5️⃣ Creating Unsubscribed segments...")
        for channel, event_names in [('Push', ['unsubscribed to push']), ('Email', ['email unsubscribes'])]:
            print(f"  🚫 Creating Unsubscribed {channel} segment...")
            segment_name = f"UK_Unsubscribed_{channel}" if country_code == 'GB' else f"UAE_Unsubscribed_{channel}"
            
            filters = {
                "filter_operator": "and",
                "filters": [
                    {
                        "filter_type": "user_attributes",
                        "name": "country",
                        "data_type": "string",
                        "operator": "in",
                        "value": [country_code],
                        "negate": False,
                        "case_sensitive": False
                    },
                    {
                        "filter_type": "actions",
                        "attributes": {
                            "filter_operator": "and",
                            "filters": []
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": f"{start_date}T00:00:00.000Z",
                            "value1": f"{end_date}T23:59:59.999Z",
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": event_names[0],
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
            
            result = automation.create_segment(segment_name, f"{country_name} users who unsubscribed from {channel.lower()}", filters)
            if 'error' not in result:
                result['display_name'] = f"{country_name} - Unsubscribed {channel}"
                result['field_name'] = f"{country_name.lower()}_{channel.lower()}_unsubscribed"
                segments.append(result)
                print(f"  ✅ SUCCESS: {result['display_name']} (Status: {result.get('status', 'unknown')})")
            else:
                print(f"  ❌ FAILED: {result['error']}")
    
    print(f"\n📊 FINAL SUMMARY:")
    print(f"✅ Total segments created: {len(segments)}")
    print(f"🆔 Segment IDs: {len([seg['id'] for seg in segments if seg.get('id') and seg['id'] != 'unknown'])}")
    
    return {
        'segments': segments,
        'segment_ids': [seg['id'] for seg in segments if seg.get('id') and seg['id'] != 'unknown']
    }

if __name__ == "__main__":
    result = debug_create_metrics_segments("2026-01-01", "2026-01-31")
    
    print(f"\n🎯 Expected: 16 segments (8 per country)")
    print(f"🎯 Actual: {len(result['segments'])} segments")
    
    if len(result['segments']) == 16:
        print("🎉 SUCCESS: All segments created!")
    else:
        print("❌ ISSUE: Missing segments")