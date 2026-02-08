#!/usr/bin/env python3
"""
New segment definitions with combined Android/iOS push segments
"""

# This is the new UK_Received_Push segment (replaces Android and iOS separate segments)
UK_RECEIVED_PUSH = {
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
                            "value": "{start_date}T00:00:00.000Z",  # Will be formatted
                            "value1": "{end_date}T23:59:59.999Z",  # Will be formatted
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
                            "value": "{start_date}T00:00:00.000Z",  # Will be formatted
                            "value1": "{end_date}T23:59:59.999Z",  # Will be formatted
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
}

# This is the new UK_Active_Received_Push segment (uses relative time)
UK_ACTIVE_RECEIVED_PUSH = {
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
                    "value": "{sixty_days_ago}",  # Will be formatted
                    "value1": "{now}",  # Will be formatted
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
}

print("Segment definitions ready")
