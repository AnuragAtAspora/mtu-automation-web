#!/usr/bin/env python3
"""
Display the updated segment definitions to show the event changes
"""

import json
from datetime import datetime, timedelta

# Sample dates for demonstration
start_date = "2026-02-01"
end_date = "2026-02-05"

print("=" * 80)
print("UPDATED SEGMENT DEFINITIONS - EVENT CHANGES")
print("=" * 80)
print()

# Show UK_Active_Users with sub_event filter
print("1. UK_Active_Users - ORDER event with sub_event filter")
print("-" * 80)
uk_active = {
    "filter_operator": "and",
    "filters": [
        {
            "filter_type": "user_attributes",
            "name": "country",
            "value": ["GB"]
        },
        {
            "filter_type": "actions",
            "attributes": {
                "filter_operator": "or",
                "filters": [
                    {
                        "filter_type": "event_attributes",
                        "name": "sub_event",
                        "value": ["COMPLETED"]
                    },
                    {
                        "filter_type": "event_attributes",
                        "name": "sub_event",
                        "value": ["PAYMENT_COMPLETED"]
                    }
                ]
            },
            "action_name": "ORDER",
            "primary_time_range": "Last 60 days"
        }
    ]
}
print(json.dumps(uk_active, indent=2))
print()

# Show UK_Received_Push with notification events
print("2. UK_Received_Push - Notification Received events")
print("-" * 80)
uk_push = {
    "filter_operator": "and",
    "filters": [
        {
            "filter_type": "user_attributes",
            "name": "country",
            "value": ["GB"]
        },
        {
            "filter_type": "or",
            "filters": [
                {
                    "filter_type": "actions",
                    "action_name": "Notification Received Android",
                    "primary_time_range": f"{start_date} to {end_date}"
                },
                {
                    "filter_type": "actions",
                    "action_name": "Notification Received iOS",
                    "primary_time_range": f"{start_date} to {end_date}"
                }
            ]
        }
    ]
}
print(json.dumps(uk_push, indent=2))
print()

# Show UK_Unsubscribed_Push with updated capitalization
print("3. UK_Unsubscribed_Push - Updated event name")
print("-" * 80)
uk_unsub_push = {
    "filter_operator": "and",
    "filters": [
        {
            "filter_type": "user_attributes",
            "name": "country",
            "value": ["GB"]
        },
        {
            "filter_type": "actions",
            "action_name": "Unsubscribed to Push",  # Capital U
            "primary_time_range": f"{start_date} to {end_date}"
        }
    ]
}
print(json.dumps(uk_unsub_push, indent=2))
print()

# Show UK_Unsubscribed_Email with updated capitalization
print("4. UK_Unsubscribed_Email - Updated event name")
print("-" * 80)
uk_unsub_email = {
    "filter_operator": "and",
    "filters": [
        {
            "filter_type": "user_attributes",
            "name": "country",
            "value": ["GB"]
        },
        {
            "filter_type": "actions",
            "action_name": "Email Unsubscribed",  # Capital E
            "primary_time_range": f"{start_date} to {end_date}"
        }
    ]
}
print(json.dumps(uk_unsub_email, indent=2))
print()

# Show UK_Active_Received_Push with BOTH changes
print("5. UK_Active_Received_Push - Combined changes")
print("-" * 80)
uk_active_push = {
    "filter_operator": "and",
    "filters": [
        {
            "filter_type": "user_attributes",
            "name": "country",
            "value": ["GB"]
        },
        {
            "filter_type": "or",
            "filters": [
                {
                    "filter_type": "actions",
                    "action_name": "Notification Received Android",
                    "primary_time_range": f"{start_date} to {end_date}"
                },
                {
                    "filter_type": "actions",
                    "action_name": "Notification Received iOS",
                    "primary_time_range": f"{start_date} to {end_date}"
                }
            ]
        },
        {
            "filter_type": "actions",
            "attributes": {
                "filter_operator": "or",
                "filters": [
                    {
                        "filter_type": "event_attributes",
                        "name": "sub_event",
                        "value": ["COMPLETED"]
                    },
                    {
                        "filter_type": "event_attributes",
                        "name": "sub_event",
                        "value": ["PAYMENT_COMPLETED"]
                    }
                ]
            },
            "action_name": "ORDER",
            "primary_time_range": "Last 60 days"
        }
    ]
}
print(json.dumps(uk_active_push, indent=2))
print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("✅ All 8 UK segments updated with new event definitions")
print("✅ All 8 UAE segments will inherit changes (auto-generated from UK)")
print("✅ Total: 16 segments with updated events")
print()
print("Event Changes:")
print("  1. ORDER event: Now filters by sub_event (COMPLETED OR PAYMENT_COMPLETED)")
print("  2. Push events: Changed to Notification Received Android/iOS")
print("  3. Unsubscribe: Updated capitalization")
print()
print("=" * 80)
