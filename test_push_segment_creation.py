#!/usr/bin/env python3
"""
Test creating the UK_Received_Push segment to see why it's failing
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

# Test the UK_Received_Push segment with new notification events
segment_name = f"Test_UK_Push_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
description = "Test UK users who received push notifications"

filters = {
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
    "included_filters": filters
}

print("=" * 70)
print("TESTING UK_Received_Push SEGMENT CREATION")
print("=" * 70)
print()
print(f"Segment name: {segment_name}")
print(f"Description: {description}")
print()
print("Filter structure:")
print("  - Country: GB")
print("  - OR condition:")
print("    - Notification Received Android")
print("    - Notification Received iOS")
print()
print("Sending request to MoEngage...")
print()

try:
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code in [200, 201]:
        data = response.json()
        segment_id = data['data']['id']
        print(f"✅ SUCCESS! Segment created")
        print(f"   Segment ID: {segment_id}")
        print(f"   URL: https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments/{segment_id}")
    elif response.status_code == 409:
        print(f"⚠️  Segment already exists (409 conflict)")
        print(f"   Response: {response.text}")
    else:
        print(f"❌ FAILED")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print()
print("=" * 70)
