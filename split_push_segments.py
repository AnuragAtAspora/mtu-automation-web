#!/usr/bin/env python3
"""
Split push segments into separate Android and iOS segments
This will create 20 total segments (10 UK + 10 UAE) instead of 16
"""

with open('app.py', 'r') as f:
    content = f.read()

# Find and replace the UK_Received_Push segment with TWO segments (Android and iOS)
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

new_uk_push_split = '''        {
            'name': 'UK_Received_Push_Android',
            'display_name': 'UK - Received Push (Android)',
            'field_name': 'uk_push_received_android',
            'description': 'UK users who received Android push',
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
        },
        {
            'name': 'UK_Received_Push_iOS',
            'display_name': 'UK - Received Push (iOS)',
            'field_name': 'uk_push_received_ios',
            'description': 'UK users who received iOS push',
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
                        "action_name": "Notification Received iOS",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        },'''

if old_uk_push in content:
    content = content.replace(old_uk_push, new_uk_push_split)
    print("✅ Split UK_Received_Push into Android and iOS segments")
else:
    print("⚠️  Could not find UK_Received_Push pattern")

# Now split UK_Active_Received_Push into Android and iOS
old_active_push = '''        {
            'name': 'UK_Active_Received_Push',
            'display_name': 'UK - Active Users Received Push',
            'field_name': 'uk_push_received_active',
            'description': 'UK active users who received push',
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

new_active_push_split = '''        {
            'name': 'UK_Active_Received_Push_Android',
            'display_name': 'UK - Active Users Received Push (Android)',
            'field_name': 'uk_push_received_active_android',
            'description': 'UK active users who received Android push',
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
        {
            'name': 'UK_Active_Received_Push_iOS',
            'display_name': 'UK - Active Users Received Push (iOS)',
            'field_name': 'uk_push_received_active_ios',
            'description': 'UK active users who received iOS push',
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
                        "action_name": "Notification Received iOS",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
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

if old_active_push in content:
    content = content.replace(old_active_push, new_active_push_split)
    print("✅ Split UK_Active_Received_Push into Android and iOS segments")
else:
    print("⚠️  Could not find UK_Active_Received_Push pattern")

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print()
print("=" * 70)
print("PUSH SEGMENTS SPLIT COMPLETED")
print("=" * 70)
print()
print("New segment structure:")
print("  UK Segments: 10 (was 8)")
print("    - UK_All_Users")
print("    - UK_Active_Users")
print("    - UK_Received_Push_Android (NEW)")
print("    - UK_Received_Push_iOS (NEW)")
print("    - UK_Received_Email")
print("    - UK_Active_Received_Push_Android (NEW)")
print("    - UK_Active_Received_Push_iOS (NEW)")
print("    - UK_Active_Received_Email")
print("    - UK_Unsubscribed_Push")
print("    - UK_Unsubscribed_Email")
print()
print("  UAE Segments: 10 (auto-generated from UK)")
print()
print("  Total: 20 segments (10 UK + 10 UAE)")
print("=" * 70)
