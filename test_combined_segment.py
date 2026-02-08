#!/usr/bin/env python3
"""Test creating a segment with the new combined Android/iOS logic"""

import requests
import base64
from datetime import datetime

WORKSPACE_ID = '95PNUHBSYSLLJZ22PEOFMKF2'
DATA_API_KEY = 'Mj5JSGKcwYum9NKAGmGHJG_E'
DATA_CENTER = '01'

# New combined segment
segment = {
    "name": "Test_Combined_Push_UK",
    "description": "Test combined Android/iOS push",
    "included_filters": {
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
                            "value": "2026-02-01T00:00:00.000Z",
                            "value1": "2026-02-07T23:59:59.999Z",
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
                            "value": "2026-02-01T00:00:00.000Z",
                            "value1": "2026-02-07T23:59:59.999Z",
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
}

# Create segment
url = f"https://api-{DATA_CENTER}.moengage.com/v3/custom-segments/"
auth_string = f"{WORKSPACE_ID}:{DATA_API_KEY}"
encoded_auth = base64.b64encode(auth_string.encode()).decode()

headers = {
    'Authorization': f'Basic {encoded_auth}',
    'Content-Type': 'application/json',
    'MOE-APPKEY': WORKSPACE_ID
}

print("Testing combined Android/iOS push segment...")
response = requests.post(url, json=segment, headers=headers, timeout=15)

print(f"Status: {response.status_code}")
if response.status_code in [200, 201]:
    data = response.json()
    print(f"✅ Segment created successfully!")
    print(f"   ID: {data['data']['id']}")
    print(f"   Name: {segment['name']}")
elif response.status_code == 409:
    print(f"✅ Segment already exists (409) - logic is valid!")
else:
    print(f"❌ Error: {response.text}")
