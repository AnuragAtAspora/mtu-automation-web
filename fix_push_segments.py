#!/usr/bin/env python3
"""
Fix the push notification segments - use just Android event for now
OR create two separate segments (one for Android, one for iOS)
"""

with open('app.py', 'r') as f:
    content = f.read()

# Replace the UK_Received_Push segment with a simpler version using just Android
# (MoEngage doesn't support OR at that level)

old_uk_push = '''        {
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

new_uk_push = '''        {
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
                        "action_name": "Notification Received Android",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        },'''

if old_uk_push in content:
    content = content.replace(old_uk_push, new_uk_push)
    print("✅ Updated UK_Received_Push to use Android event only")
else:
    print("⚠️  Could not find UK_Received_Push pattern")

# Now fix UK_Active_Received_Push - same issue
old_active_push = '''                    {
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
                    },'''

new_active_push = '''                    {
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
                    },'''

if old_active_push in content:
    content = content.replace(old_active_push, new_active_push)
    print("✅ Updated UK_Active_Received_Push to use Android event only")
else:
    print("⚠️  Could not find UK_Active_Received_Push pattern")

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print()
print("=" * 70)
print("PUSH SEGMENTS FIXED")
print("=" * 70)
print()
print("Changed from: Notification Received Android OR iOS (invalid structure)")
print("Changed to: Notification Received Android only (valid structure)")
print()
print("Note: This will capture Android push notifications.")
print("iOS notifications would need a separate segment if needed.")
print("=" * 70)
