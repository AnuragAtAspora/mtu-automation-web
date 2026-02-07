#!/usr/bin/env python3
"""
Update the MoEngage events in create_metrics_segments function
"""

# Read the file
with open('app.py', 'r') as f:
    content = f.read()

# 1. Update Active Users - add sub_event filter for ORDER
# Find and replace the ORDER action filter for active users
old_active_filter = '''                    {
                        "filter_type": "actions",
                        "attributes": {
                            "filter_operator": "and",
                            "filters": []
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%dT00:00:00.000Z'),
                            "value1": datetime.now().strftime('%Y-%m-%dT23:59:59.999Z'),
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": "ORDER",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }'''

new_active_filter = '''                    {
                        "filter_type": "actions",
                        "attributes": {
                            "filter_operator": "or",
                            "filters": [
                                {
                                    "filter_type": "event_attributes",
                                    "name": "sub_event",
                                    "data_type": "string",
                                    "operator": "in",
                                    "value": ["COMPLETED"],
                                    "negate": False,
                                    "case_sensitive": False
                                },
                                {
                                    "filter_type": "event_attributes",
                                    "name": "sub_event",
                                    "data_type": "string",
                                    "operator": "in",
                                    "value": ["PAYMENT_COMPLETED"],
                                    "negate": False,
                                    "case_sensitive": False
                                }
                            ]
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%dT00:00:00.000Z'),
                            "value1": datetime.now().strftime('%Y-%m-%dT23:59:59.999Z'),
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": "ORDER",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }'''

content = content.replace(old_active_filter, new_active_filter)

# 2. Update Push Received - change from MOE_PUSH_SENT to Notification Received events
# This is more complex as we need to change the action_name
content = content.replace('"action_name": "MOE_PUSH_SENT"', '"action_name": "Notification Received Android"')

# 3. Update Unsubscribe events
content = content.replace('"action_name": "unsubscribed to push"', '"action_name": "Unsubscribed to Push"')
content = content.replace('"action_name": "email unsubscribes"', '"action_name": "Email Unsubscribed"')

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Updated Active Users filter to include sub_event (COMPLETED or PAYMENT_COMPLETED)")
print("✅ Updated Push Received to use 'Notification Received Android'")
print("✅ Updated Push Unsubscribe to use 'Unsubscribed to Push'")
print("✅ Updated Email Unsubscribe to use 'Email Unsubscribed'")
print()
print("⚠️  NOTE: Push events now use 'Notification Received Android' only")
print("   Need to add OR logic for iOS separately...")
