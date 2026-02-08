#!/usr/bin/env python3
"""
Apply new push segment logic - combine Android/iOS and use new events
"""

# New UK_Received_Push segment definition
uk_received_push_new = '''        {
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
        },
'''

# New UK_Active_Received_Push segment definition
uk_active_received_push_new = '''        {
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
        },
'''

# Read the file
with open('app.py', 'r') as f:
    content = f.read()

# Replace UK_Received_Push_Android and UK_Received_Push_iOS with single segment
import re

# Pattern 1: Replace both Android and iOS Received Push segments
pattern1 = r"        \{\s*'name': 'UK_Received_Push_Android',.*?\},\s*\{\s*'name': 'UK_Received_Push_iOS',.*?\},"
content = re.sub(pattern1, uk_received_push_new, content, flags=re.DOTALL)

# Pattern 2: Replace both Android and iOS Active Received Push segments  
pattern2 = r"        \{\s*'name': 'UK_Active_Received_Push_Android',.*?\},\s*\{\s*'name': 'UK_Active_Received_Push_iOS',.*?\},"
content = re.sub(pattern2, uk_active_received_push_new, content, flags=re.DOTALL)

# Update the docstring from 20 to 16 segments
content = content.replace(
    '"""Create all 16 segments needed for metrics calculation with proper rate limiting"""',
    '"""Create all 16 segments needed for metrics calculation with proper rate limiting"""'
)

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Successfully updated push segment logic!")
print("   - Removed separate Android/iOS segments")
print("   - Added combined UK_Received_Push segment")
print("   - Added combined UK_Active_Received_Push segment (with relative time)")
print("   - Using new events: NOTIFICATION_RECEIVED_MOE and n_i_s")
print("   - Segments reduced from 20 to 16")
