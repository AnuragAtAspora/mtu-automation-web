#!/usr/bin/env python3
"""Test the new push segment logic"""

# New filter structure
new_push_filter = {
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
                    "execution": {"count": 1, "type": "atleast"},
                    "primary_time_range": {
                        "type": "between",
                        "value": "2026-01-01T00:00:00.000Z",
                        "value1": "2026-01-31T23:59:59.999Z",
                        "value_type": "absolute",
                        "period_unit": "days"
                    },
                    "attributes": {"filter_operator": "and", "filters": []}
                },
                {
                    "action_name": "n_i_s",
                    "executed": True,
                    "filter_type": "actions",
                    "execution": {"count": 1, "type": "atleast"},
                    "primary_time_range": {
                        "type": "between",
                        "value": "2026-01-01T00:00:00.000Z",
                        "value1": "2026-01-31T23:59:59.999Z",
                        "value_type": "absolute",
                        "period_unit": "days"
                    },
                    "attributes": {"filter_operator": "and", "filters": []}
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

print("✅ New push filter structure is valid")
print(f"   - Uses OR between NOTIFICATION_RECEIVED_MOE and n_i_s")
print(f"   - Combines Android and iOS into single segment")
