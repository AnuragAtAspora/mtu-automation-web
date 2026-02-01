#!/usr/bin/env python3
"""
Test MoEngage Segment APIs to see if we can get segment counts
"""

import requests
import base64
import json

def test_list_segments_api():
    """Test the List Custom Segments API"""
    
    # Configuration
    WORKSPACE_ID = "95PNUHBSYSLLJZ22PEOFMKF2"
    DATA_API_KEY = "Mj5JSGKcwYum9NKAGmGHJG_E"
    DATA_CENTER = "01"
    
    try:
        # List Custom Segments API
        url = f"https://api-{DATA_CENTER}.moengage.com/v3/custom-segments"
        
        # Auth
        auth_string = f"{WORKSPACE_ID}:{DATA_API_KEY}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/json',
            'MOE-APPKEY': WORKSPACE_ID
        }
        
        print("🔍 Testing List Custom Segments API...")
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response received!")
            print(f"Response keys: {list(data.keys())}")
            
            if 'data' in data and isinstance(data['data'], list):
                segments = data['data']
                print(f"Found {len(segments)} segments")
                
                # Look for MTU segments
                mtu_segments = [s for s in segments if s.get('name', '').startswith('MTU_')]
                print(f"Found {len(mtu_segments)} MTU segments")
                
                for segment in mtu_segments[:3]:  # Show first 3
                    print(f"\nSegment: {segment.get('name', 'Unknown')}")
                    print(f"ID: {segment.get('id', 'Unknown')}")
                    print(f"Keys: {list(segment.keys())}")
                    
                    # Check if count/size is included
                    if 'count' in segment:
                        print(f"Count: {segment['count']}")
                    elif 'size' in segment:
                        print(f"Size: {segment['size']}")
                    elif 'user_count' in segment:
                        print(f"User Count: {segment['user_count']}")
                    else:
                        print("❌ No count field found")
            
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_segment_by_id():
    """Test getting a specific segment by ID"""
    
    # Configuration
    WORKSPACE_ID = "95PNUHBSYSLLJZ22PEOFMKF2"
    DATA_API_KEY = "Mj5JSGKcwYum9NKAGmGHJG_E"
    DATA_CENTER = "01"
    
    # Use one of the segment IDs we created
    segment_id = "697fd30caaa05331f7bb1ad6"  # UK All Users
    
    try:
        url = f"https://api-{DATA_CENTER}.moengage.com/v3/custom-segments/{segment_id}"
        
        # Auth
        auth_string = f"{WORKSPACE_ID}:{DATA_API_KEY}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/json',
            'MOE-APPKEY': WORKSPACE_ID
        }
        
        print(f"\n🔍 Testing Get Segment by ID API for: {segment_id}")
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response received!")
            
            if 'data' in data:
                segment = data['data']
                print(f"Segment: {segment.get('name', 'Unknown')}")
                print(f"Keys: {list(segment.keys())}")
                
                # Check for count fields
                if 'count' in segment:
                    print(f"✅ Count: {segment['count']}")
                elif 'size' in segment:
                    print(f"✅ Size: {segment['size']}")
                elif 'user_count' in segment:
                    print(f"✅ User Count: {segment['user_count']}")
                else:
                    print("❌ No count field found")
                    print(f"Full response: {json.dumps(segment, indent=2)}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("Testing MoEngage Segment APIs for Count Data")
    print("=" * 50)
    
    # Test List API
    success1 = test_list_segments_api()
    
    # Test Get by ID API
    success2 = test_get_segment_by_id()
    
    if success1 or success2:
        print("\n🎉 Found working API! We can potentially get segment counts.")
    else:
        print("\n❌ No working API found for segment counts.")

if __name__ == "__main__":
    main()