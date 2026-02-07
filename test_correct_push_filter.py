#!/usr/bin/env python3
"""
Test the correct way to create OR condition for push notifications in MoEngage
According to MoEngage API, we need to use multiple action filters in AND, not OR
"""

import requests
import base64
from datetime import datetime

MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'data_center': '01'
}

start_date = "2026-02-01"
end_date = "2026-02-05"

# Try approach 1: Just use one event (Android only) first to see if it works
segment_name = f"Test_UK_Push_Android_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
description = "Test UK users who received Android push"

filters_android_only = {
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

url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v3/custom-segments/"

auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
encoded_auth = base64.b64encode(auth_string.encode()).decode()

headers = {
    'Authorization': f'Basic {encoded_auth}',
    'Content-Type': 'application/json',
    'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id']
}

payload = {
    "name": segment_name,
    "description": description,
    "included_filters": filters_android_only
}

print("=" * 70)
print("TEST 1: Android notification only")
print("=" * 70)

try:
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"✅ SUCCESS! Android-only segment works")
        print(f"   Segment ID: {data['data']['id']}")
    else:
        print(f"❌ FAILED: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print()

# Now test if we can create a segment that captures EITHER Android OR iOS
# by using filter_operator: "or" at the root level
segment_name2 = f"Test_UK_Push_Both_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
description2 = "Test UK users who received push (Android OR iOS)"

filters_or_root = {
    "filter_operator": "or",
    "filters": [
        {
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
        },
        {
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
    ]
}

payload2 = {
    "name": segment_name2,
    "description": description2,
    "included_filters": filters_or_root
}

print("=" * 70)
print("TEST 2: Android OR iOS with OR at root level")
print("=" * 70)

try:
    response = requests.post(url, json=payload2, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"✅ SUCCESS! OR at root level works")
        print(f"   Segment ID: {data['data']['id']}")
        print(f"   This is the correct structure!")
    else:
        print(f"❌ FAILED: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print()
print("=" * 70)
