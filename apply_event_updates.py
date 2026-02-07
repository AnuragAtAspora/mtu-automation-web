#!/usr/bin/env python3
"""
Apply event updates to create_metrics_segments function in app.py
"""

# Read the file
with open('app.py', 'r') as f:
    content = f.read()

# Track changes
changes_made = []

# 1. Update Active Users - add sub_event filter for ORDER
# Find the UK_Active_Users segment definition
old_active = '''        {
            'name': 'UK_Active_Users',
            'display_name': 'UK - Active Users',
            'field_name': 'uk_active_users',
            'description': 'UK active users (60d)',
            'filters': {
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
                    }
                ]
            }
        },'''

new_active = '''        {
            'name': 'UK_Active_Users',
            'display_name': 'UK - Active Users',
            'field_name': 'uk_active_users',
            'description': 'UK active users (60d)',
            'filters': {
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
                    }
                ]
            }
        },'''

if old_active in content:
    content = content.replace(old_active, new_active)
    changes_made.append("✅ Updated UK_Active_Users with sub_event filter")
else:
    changes_made.append("⚠️  Could not find UK_Active_Users segment to update")

# 2. Update Push Received - change to Notification Received events
old_push = '''        {
            'name': 'UK_Received_Push',
            'display_name': 'UK - Received Push',
            'field_name': 'uk_push_received',
            'description': 'UK users who received push',
            'filters': {
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
                    }
                ]
            }
        },'''

new_push = '''        {
            'name': 'UK_Received_Push',
            'display_name': 'UK - Received Push',
            'field_name': 'uk_push_received',
            'description': 'UK users who received push',
            'filters': {
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
                        "filter_type": "or",
                        "filters": [
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
                                "action_name": "Notification Received Android",
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
                                    "value": f"{start_date}T00:00:00.000Z",
                                    "value1": f"{end_date}T23:59:59.999Z",
                                    "value_type": "absolute",
                                    "period_unit": "days"
                                },
                                "action_name": "Notification Received iOS",
                                "execution": {
                                    "count": 1,
                                    "type": "atleast"
                                }
                            }
                        ]
                    }
                ]
            }
        },'''

if old_push in content:
    content = content.replace(old_push, new_push)
    changes_made.append("✅ Updated UK_Received_Push with Notification Received events")
else:
    changes_made.append("⚠️  Could not find UK_Received_Push segment to update")

# 3. Update Unsubscribe events - just the action_name
content = content.replace('"action_name": "unsubscribed to push"', '"action_name": "Unsubscribed to Push"')
content = content.replace('"action_name": "email unsubscribes"', '"action_name": "Email Unsubscribed"')
changes_made.append("✅ Updated unsubscribe event names (capitalization)")

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print("=" * 70)
print("EVENT UPDATES APPLIED")
print("=" * 70)
for change in changes_made:
    print(change)
print("=" * 70)
