#!/usr/bin/env python3
"""
MTU Segment Creator
Creates all required segments in MoEngage for MTU calculations
You fetch the counts from MoEngage dashboard and input them manually
"""

import requests
import base64
from datetime import datetime, timedelta
import json

class MTUSegmentCreator:
    def __init__(self, workspace_id, data_api_key, data_center="01"):
        self.workspace_id = workspace_id
        self.data_api_key = data_api_key
        self.data_center = data_center
        self.created_segments = []
    
    def get_date_range(self, end_date_str):
        """Get date range from month start to selected date"""
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            yesterday = datetime.now() - timedelta(days=1)
            
            if end_date > yesterday:
                raise ValueError(f"End date cannot exceed {yesterday.strftime('%Y-%m-%d')}")
            
            start_date = end_date.replace(day=1)
            return start_date, end_date
            
        except ValueError as e:
            print(f"Date error: {e}")
            return None, None
    
    def create_segment(self, segment_name, description, filters):
        """Create a segment using MoEngage Custom Segment API"""
        try:
            url = f"https://api-{self.data_center}.moengage.com/v3/custom-segments/"
            
            # Auth
            auth_string = f"{self.workspace_id}:{self.data_api_key}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_auth}',
                'Content-Type': 'application/json',
                'MOE-APPKEY': self.workspace_id
            }
            
            # Add random component to description to avoid duplicate detection
            import random
            import string
            random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            unique_description = f"{description} [ID: {random_id}]"
            
            payload = {
                "name": segment_name,
                "description": unique_description,
                "included_filters": filters
            }
            
            print(f"🔍 Creating segment: {segment_name}")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                data = response.json()
                segment_id = data['data']['id']
                segment_info = {
                    'name': segment_name,
                    'id': segment_id,
                    'description': unique_description
                }
                self.created_segments.append(segment_info)
                print(f"✅ Created: {segment_id}")
                return segment_id
            elif response.status_code == 409:
                # Conflict - try with different random ID and timestamp
                import time
                time.sleep(1)
                random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                unique_description = f"{description} [ID: {random_id}]"
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:17]
                unique_name = f"{segment_name}_{timestamp}"
                
                payload = {
                    "name": unique_name,
                    "description": unique_description,
                    "included_filters": filters
                }
                
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                if response.status_code in [200, 201]:
                    data = response.json()
                    segment_id = data['data']['id']
                    segment_info = {
                        'name': unique_name,
                        'id': segment_id,
                        'description': unique_description
                    }
                    self.created_segments.append(segment_info)
                    print(f"✅ Created after retry: {segment_id}")
                    return segment_id
                else:
                    print(f"❌ Error after retry: {response.status_code} - {response.text}")
                    return None
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating segment: {e}")
            return None
    
    def create_country_segment(self, country_code, country_name):
        """Create segment for all users in a country"""
        segment_name = f"Automated_{country_code}_AllUsers_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        description = f"All {country_name} users for MTU calculation"
        
        filters = {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
                    "negate": False,
                    "case_sensitive": False
                }
            ]
        }
        
        return self.create_segment(segment_name, description, filters)
    
    def create_active_users_segment(self, country_code, country_name, days=60):
        """Create segment for users who transacted in last N days"""
        segment_name = f"Automated_{country_code}_Active{days}d_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        description = f"{country_name} users who transacted in last {days} days"
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        filters = {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
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
                        "value": start_date.strftime('%Y-%m-%dT00:00:00.000Z'),
                        "value1": end_date.strftime('%Y-%m-%dT23:59:59.999Z'),
                        "value_type": "absolute",
                        "period_unit": "days"
                    },
                    "action_name": "ORDER",  # Updated to correct event name
                    "execution": {
                        "count": 1,
                        "type": "atleast"
                    }
                }
            ]
        }
        
        return self.create_segment(segment_name, description, filters)
    
    def create_comms_received_segment(self, country_code, country_name, channel, start_date, end_date):
        """Create segment for users who received communications in period"""
        segment_name = f"Automated_{country_code}_{channel.title()}Received_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        description = f"{country_name} users who received {channel} from {start_date} to {end_date}"
        
        # Determine event name based on channel
        event_name = "MOE_EMAIL_SENT" if channel == "email" else "MOE_PUSH_SENT"
        
        filters = {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
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
                    "action_name": event_name,
                    "execution": {
                        "count": 1,
                        "type": "atleast"
                    }
                }
            ]
        }
        
        return self.create_segment(segment_name, description, filters)
    
    def create_active_comms_received_segment(self, country_code, country_name, channel, start_date, end_date, active_days=60):
        """Create segment for active users who received communications"""
        segment_name = f"Automated_{country_code}_{channel.title()}Active{active_days}d_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        description = f"{country_name} active users ({active_days}d) who received {channel} from {start_date} to {end_date}"
        
        # Determine event name based on channel
        event_name = "MOE_EMAIL_SENT" if channel == "email" else "MOE_PUSH_SENT"
        
        # Calculate active period
        active_end = datetime.now()
        active_start = active_end - timedelta(days=active_days)
        
        filters = {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
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
                    "action_name": event_name,
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
                        "value": active_start.strftime('%Y-%m-%dT00:00:00.000Z'),
                        "value1": active_end.strftime('%Y-%m-%dT23:59:59.999Z'),
                        "value_type": "absolute",
                        "period_unit": "days"
                    },
                    "action_name": "ORDER",  # Updated to correct event name
                    "execution": {
                        "count": 1,
                        "type": "atleast"
                    }
                }
            ]
        }
        
        return self.create_segment(segment_name, description, filters)
    
    def create_all_mtu_segments(self, end_date):
        """Create all segments needed for MTU calculations"""
        
        print("🚀 Creating All MTU Segments")
        print("=" * 40)
        
        # Get date range
        start_date, end_date_obj = self.get_date_range(end_date)
        if not start_date:
            return False
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date_obj.strftime('%Y-%m-%d')
        
        print(f"📅 Period: {start_date_str} to {end_date_str}")
        
        countries = {'UK': 'GB', 'UAE': 'AE'}
        channels = ['push', 'email']
        
        print(f"\n📊 Creating segments for MTU calculations...")
        
        for country_name, country_code in countries.items():
            print(f"\n--- {country_name} ({country_code}) Segments ---")
            
            # 1. All users in country
            self.create_country_segment(country_code, country_name)
            
            # 2. Active users in country (60 days)
            self.create_active_users_segment(country_code, country_name, 60)
            
            # 3. Users who received communications (for each channel)
            for channel in channels:
                self.create_comms_received_segment(country_code, country_name, channel, start_date_str, end_date_str)
                
                # 4. Active users who received communications
                self.create_active_comms_received_segment(country_code, country_name, channel, start_date_str, end_date_str, 60)
        
        return True
    
    def print_segment_summary(self):
        """Print summary of created segments"""
        print(f"\n📋 SEGMENT SUMMARY")
        print("=" * 50)
        print(f"Created {len(self.created_segments)} segments:")
        
        for i, segment in enumerate(self.created_segments, 1):
            print(f"{i:2d}. {segment['name']}")
            print(f"    ID: {segment['id']}")
            print(f"    Description: {segment['description']}")
            print()
        
        print("📝 NEXT STEPS:")
        print("1. Go to MoEngage Dashboard → Segments")
        print("2. Find each segment by name/ID above")
        print("3. Note down the user count for each segment")
        print("4. Use these counts to calculate MTU percentages")
        
        print(f"\n🔗 MoEngage Dashboard: https://app.moengage.com/v3/#/segments")

def main():
    print("MTU Segment Creator")
    print("=" * 25)
    
    # Configuration
    WORKSPACE_ID = "95PNUHBSYSLLJZ22PEOFMKF2"
    DATA_API_KEY = "Mj5JSGKcwYum9NKAGmGHJG_E"  # DATA API KEY (not Campaign API)
    DATA_CENTER = "01"
    
    # Get inputs
    end_date = input("End date (YYYY-MM-DD): ").strip()
    
    if not end_date:
        print("❌ End date is required")
        return
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("   - This will create segments in your MoEngage account")
    print("   - Segments will be named with Automated_ prefix and timestamp")
    print("   - You'll need to check segment counts in MoEngage dashboard")
    print("   - Adjust 'transaction' event name if different in your setup")
    
    confirm = input("\nProceed with segment creation? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Initialize and create segments
    creator = MTUSegmentCreator(WORKSPACE_ID, DATA_API_KEY, DATA_CENTER)
    
    success = creator.create_all_mtu_segments(end_date)
    
    if success:
        creator.print_segment_summary()
    else:
        print("\n❌ Segment creation failed. Please check the errors above.")

if __name__ == "__main__":
    main()