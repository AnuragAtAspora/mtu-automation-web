#!/usr/bin/env python3
"""
Test creating a single simplified segment to debug the issue
"""

import requests
import base64
import json
from datetime import datetime, timedelta

# MoEngage API Configuration
MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'campaign_api_key': '3XMHJ83D2X4V',
    'data_center': '01'
}

def test_active_users_segment():
    """Test creating the simplified Active Users segment"""
    
    print("🧪 Testing Simplified Active Users Segment")
    print("=" * 50)
    
    # Test creating UK Active Users with simplified filter
    segment_name = "UK_Active_Users"
    description = "UK active users (60d)"
    
    active_end = datetime.now()
    active_start = active_end - timedelta(days=60)
    
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
                "filter_type": "actions",
                "attributes": {
                    "filter_operator": "and",
                    "filters": []
                },
                "executed": True,
                "primary_time_range": {
                    "type": "between",
                    "value": active_start.strftime('%Y-%m-%dT00:00:00.000Z'),
                    "value1": active_end.strftime('%Y-%m-%dT23:59:59.999Z'),
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
    
    print(f"📝 Creating segment: {segment_name}")
    print(f"📅 Date range: {active_start.strftime('%Y-%m-%d')} to {active_end.strftime('%Y-%m-%d')}")
    print(f"📋 Filters: {json.dumps(filters, indent=2)}")
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v3/custom-segments/"
    
    # Auth
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
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            segment_id = data['data']['id']
            print(f"✅ SUCCESS: Created with ID {segment_id}")
            return True
        elif response.status_code == 409:
            print(f"⚠️  DUPLICATE: Segment already exists")
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        return False

def test_received_push_segment():
    """Test creating the simplified Received Push segment"""
    
    print("\n🧪 Testing Simplified Received Push Segment")
    print("=" * 50)
    
    # Test creating UK Received Push with MOE_PUSH_SENT
    segment_name = "UK_Received_Push"
    description = "UK users who received push"
    
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
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
                "action_name": "MOE_PUSH_SENT",
                "execution": {
                    "count": 1,
                    "type": "atleast"
                }
            }
        ]
    }
    
    print(f"📝 Creating segment: {segment_name}")
    print(f"📅 Date range: {start_date} to {end_date}")
    print(f"📋 Filters: {json.dumps(filters, indent=2)}")
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v3/custom-segments/"
    
    # Auth
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
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            segment_id = data['data']['id']
            print(f"✅ SUCCESS: Created with ID {segment_id}")
            return True
        elif response.status_code == 409:
            print(f"⚠️  DUPLICATE: Segment already exists")
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    # Test both failing segment types
    success1 = test_active_users_segment()
    success2 = test_received_push_segment()
    
    if success1 and success2:
        print("\n🎉 Both simplified segments work!")
    else:
        print("\n❌ Some segments still failing")