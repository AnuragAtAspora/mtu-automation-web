#!/usr/bin/env python3
"""
Update push segment logic to combine Android/iOS and use new events
"""

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Define the new UK_Received_Push segment (combining Android/iOS)
new_uk_received_push = '''        {
            'name': 'UK_Received_Push',
            'display_name': 'UK - Received Push',
            'field_name': 'uk_push_received',
            'description': 'UK users who received push',
            'filters': {
                "filter_operator": "and",
                "filters": [
                    {
                        "filter_operator": "or",
                        "filter_type": "nested_filters",
                        "filters": [
                            {
                                "action_name": "NOTIFICATION_RECEIVED_MOE",
                                "executed": True,
                                "filter_type": "actions",
                                "execution": {
                                    "count": 1,
                                    "type": "atleast"
                                },
                                "primary_time_range": {
                                    "type": "between",
                                    "value": f"{start_date}T00:00:00.000Z",
                                    "value1": f"{end_date}T23:59:59.999Z",
                                    "value_type": "absolute",
                                    "period_unit": "days"
                                },
                                "attributes": {
                                    "filter_operator": "and",
                                    "filters": []
                                }
                            },
                            {
                                "action_name": "n_i_s",
                                "executed": True,
                                "filter_type": "actions",
                                "execution": {
                                    "count": 1,
                                    "type": "atleast"
                                },
                                "primary_time_range": {
                                    "type": "between",
                                    "value": f"{start_date}T00:00:00.000Z",
                                    "value1": f"{end_date}T23:59:59.999Z",
                                    "value_type": "absolute",
                                    "period_unit": "days"
                                },
                                "attributes": {
                                    "filter_operator": "and",
                                    "filters": []
                                }
                            }
                        ]
                    },
                    {
                        "data_type": "string",
                        "category": "Tracked Custom Attribute",
                        "name": "country",
                        "value": ["GB"],
                        "filter_type": "user_attributes",
                        "case_sensitive": False,
                        "operator": "in",
                        "negate": False
                    }
                ]
            }
        },'''

# Find and replace UK_Received_Push_Android and UK_Received_Push_iOS with single segment
import re

# Pattern to match both Android and iOS segments
pattern = r"        \{\s*'name': 'UK_Received_Push_Android',.*?\},\s*\{\s*'name': 'UK_Received_Push_iOS',.*?\},"

# Replace with new combined segment
content = re.sub(pattern, new_uk_received_push, content, flags=re.DOTALL)

# Now update UK_Active_Received_Push to use relative time and new events
new_uk_active_received_push = '''        {
            'name': 'UK_Active_Received_Push',
            'display_name': 'UK - Active Users Received Push',
            'field_name': 'uk_push_received_active',
            'description': 'UK active users who received push',
            'filters': {
                "filter_operator": "and",
                "filters": [
                    {
                        "filter_operator": "or",
                        "filter_type": "nested_filters",
                        "filters": [
                            {
                                "action_name": "NOTIFICATION_RECEIVED_MOE",
                                "executed": True,
                                "filter_type": "actions",
                                "execution": {
                                    "count": 1,
                                    "type": "atleast"
                                },
                                "primary_time_range": {
                                    "type": "inTheLast",
                                    "value": 60,
                                    "value_type": "relative_past",
                                    "period_unit": "days"
                                },
                                "attributes": {
                                    "filter_operator": "and",
                                    "filters": []
                                }
                            },
                            {
                                "action_name": "n_i_s",
                                "executed": True,
                                "filter_type": "actions",
                                "execution": {
                                    "count": 1,
                                    "type": "atleast"
                                },
                                "primary_time_range": {
                                    "type": "inTheLast",
                                    "value": 60,
                                    "value_type": "relative_past",
                                    "period_unit": "days"
                                },
                                "attributes": {
                                    "filter_operator": "and",
                                    "filters": []
                                }
                            }
                        ]
                    },
                    {
                        "data_type": "string",
                        "category": "Tracked Custom Attribute",
                        "name": "country",
                        "value": ["GB"],
                        "filter_type": "user_attributes",
                        "case_sensitive": False,
                        "operator": "in",
                        "negate": False
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

# Pattern to match UK_Active_Received_Push (the old one with Android/iOS OR logic)
pattern_active = r"        \{\s*'name': 'UK_Active_Received_Push',.*?'filters': \{.*?\}\s*\},"

# Replace with new segment
content = re.sub(pattern_active, new_uk_active_received_push, content, flags=re.DOTALL)

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Updated push segment logic")
print("   - Combined Android/iOS into single segments")
print("   - Updated to use NOTIFICATION_RECEIVED_MOE and n_i_s events")
print("   - UK_Active_Received_Push now uses relative time (last 60 days)")
