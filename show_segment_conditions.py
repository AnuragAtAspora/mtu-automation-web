#!/usr/bin/env python3
"""
Show the exact conditions being fed to MoEngage API for a specific segment
"""

import json
from datetime import datetime, timedelta

def show_uk_active_push_conditions():
    """Show the exact conditions for UK - Active Users Received Push segment"""
    
    print("🔍 SEGMENT CONDITIONS ANALYSIS")
    print("=" * 60)
    print("📋 Segment: UK - Active Users Received Push")
    print("📝 Description: UK active users who received push notifications")
    print()
    
    # Date ranges
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    active_start = datetime.now() - timedelta(days=60)
    active_end = datetime.now()
    
    print(f"📅 Communication Period: {start_date} to {end_date}")
    print(f"📅 Active User Period: {active_start.strftime('%Y-%m-%d')} to {active_end.strftime('%Y-%m-%d')}")
    print()
    
    # The exact filters being sent to MoEngage API
    filters = {
        "filter_operator": "and",
        "filters": [
            {
                "filter_type": "user_attributes",
                "name": "country",
                "data_type": "string",
                "operator": "in",
                "value": ["GB"],
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
                "action_name": "MOE_PUSH_SENT",
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
    
    print("🎯 CONDITIONS BREAKDOWN:")
    print()
    
    print("1️⃣ COUNTRY FILTER:")
    print("   - User attribute: country")
    print("   - Operator: in")
    print("   - Value: ['GB'] (United Kingdom)")
    print("   - Case sensitive: False")
    print()
    
    print("2️⃣ PUSH NOTIFICATION RECEIVED FILTER:")
    print("   - Event: MOE_PUSH_SENT")
    print("   - Time range: 2026-01-01 to 2026-01-31")
    print("   - Execution: At least 1 time")
    print("   - Logic: User received at least 1 push notification in January 2026")
    print()
    
    print("3️⃣ ACTIVE USER FILTER:")
    print("   - Event: ORDER (transaction)")
    print(f"   - Time range: {active_start.strftime('%Y-%m-%d')} to {active_end.strftime('%Y-%m-%d')} (last 60 days)")
    print("   - Execution: At least 1 time")
    print("   - Logic: User made at least 1 transaction in the last 60 days")
    print()
    
    print("🔗 COMBINED LOGIC:")
    print("   Users who meet ALL of these conditions:")
    print("   ✅ Are from United Kingdom (country = 'GB')")
    print("   ✅ Received at least 1 push notification between Jan 1-31, 2026")
    print("   ✅ Made at least 1 transaction in the last 60 days")
    print()
    
    print("📋 FULL JSON PAYLOAD:")
    print(json.dumps(filters, indent=2))
    
    return filters

if __name__ == "__main__":
    show_uk_active_push_conditions()