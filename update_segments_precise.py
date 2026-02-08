#!/usr/bin/env python3
"""
Precisely update push segments by line numbers
"""

# Read all lines
with open('app.py', 'r') as f:
    lines = f.readlines()

# New UK_Received_Push segment (replaces lines 1845-1924: Android + iOS segments)
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
        },
'''

# New UK_Active_Received_Push segment (replaces lines 1965-2122: Android + iOS active segments)
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
        },
'''

# Build new file
# Lines 1-1844 (before first segment)
new_lines = lines[:1844]

# Add new UK_Received_Push
new_lines.append(new_uk_received_push)

# Lines 1925-1964 (UK_Received_Email segment, skip old Android/iOS push segments)
new_lines.extend(lines[1924:1964])

# Add new UK_Active_Received_Push  
new_lines.append(new_uk_active_received_push)

# Lines 2123-end (rest of file, skip old Android/iOS active push segments)
new_lines.extend(lines[2122:])

# Write back
with open('app.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Successfully updated push segments!")
print("   - Replaced UK_Received_Push_Android + UK_Received_Push_iOS")
print("   - Replaced UK_Active_Received_Push_Android + UK_Active_Received_Push_iOS")
print("   - Using new events: NOTIFICATION_RECEIVED_MOE and n_i_s")
print("   - UK_Active_Received_Push uses relative time (last 60 days)")
