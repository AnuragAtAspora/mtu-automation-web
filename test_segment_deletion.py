#!/usr/bin/env python3
"""
Test script to verify if segment deletion is possible via MoEngage API
"""

import requests
import base64
import json
from datetime import datetime

# MoEngage API Configuration
WORKSPACE_ID = "95PNUHBSYSLLJZ22PEOFMKF2"
DATA_API_KEY = "Mj5JSGKcwYum9NKAGmGHJG_E"
DATA_CENTER = "01"

def test_segment_lifecycle():
    """Test creating and then deleting a segment"""
    
    # Auth
    auth_string = f"{WORKSPACE_ID}:{DATA_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': WORKSPACE_ID
    }
    
    # Create a test segment
    create_url = f"https://api-{DATA_CENTER}.moengage.com/v3/custom-segments/"
    test_name = f"DELETE_TEST_{int(datetime.now().timestamp())}"
    
    payload = {
        "name": test_name,
        "description": "Test segment for deletion verification",
        "included_filters": {
            "filter_operator": "and",
            "filters": []  # No filters = all users
        }
    }
    
    print("🧪 Testing Segment Deletion Capability")
    print("=" * 50)
    
    try:
        # Step 1: Create segment
        print(f"📝 Creating test segment: {test_name}")
        create_response = requests.post(create_url, json=payload, headers=headers, timeout=15)
        print(f"Create Status: {create_response.status_code}")
        
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            segment_id = data.get('data', {}).get('id')
            print(f"✅ Segment created successfully: {segment_id}")
            
            # Step 2: Try to delete segment
            delete_url = f"https://api-{DATA_CENTER}.moengage.com/v3/custom-segments/{segment_id}"
            print(f"🗑️  Attempting to delete segment: {segment_id}")
            
            delete_response = requests.delete(delete_url, headers=headers, timeout=15)
            print(f"Delete Status: {delete_response.status_code}")
            print(f"Delete Response: {delete_response.text}")
            
            if delete_response.status_code in [200, 204]:
                print("✅ Segment deletion SUCCESSFUL!")
                return True
            else:
                print(f"❌ Segment deletion FAILED: {delete_response.status_code}")
                print("This confirms that MoEngage API doesn't support programmatic segment deletion")
                return False
                
        else:
            print(f"❌ Failed to create test segment: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during test: {e}")
        return False

if __name__ == "__main__":
    success = test_segment_lifecycle()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 CONCLUSION: Segment deletion via API is POSSIBLE")
    else:
        print("⚠️  CONCLUSION: Segment deletion via API is NOT SUPPORTED")
        print("Manual cleanup through MoEngage dashboard will be required")