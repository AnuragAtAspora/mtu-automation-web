#!/usr/bin/env python3
"""
Fix the create_metrics_segments function in app.py by replacing it with the working version
"""

# Read the entire app.py file
with open('app.py', 'r') as f:
    lines = f.readlines()

# Find the start of create_metrics_segments function
start_idx = None
for i, line in enumerate(lines):
    if line.strip() == 'def create_metrics_segments(start_date, end_date):':
        start_idx = i
        break

if start_idx is None:
    print("❌ Could not find create_metrics_segments function")
    exit(1)

print(f"✅ Found function at line {start_idx + 1}")

# Find the end of the function (next function definition or end of file)
end_idx = None
for i in range(start_idx + 1, len(lines)):
    # Look for next function definition at the same indentation level
    if lines[i].startswith('def ') and not lines[i].startswith('    '):
        end_idx = i
        break

if end_idx is None:
    # Function goes to end of file
    end_idx = len(lines)

print(f"✅ Function ends at line {end_idx}")
print(f"📏 Old function length: {end_idx - start_idx} lines")

# The new working function
new_function = '''def create_metrics_segments(start_date, end_date):
    """Create all 16 segments needed for metrics calculation with proper rate limiting"""
    
    import time
    import copy
    
    # Define all 16 segments upfront
    # UK Segments (8 total)
    uk_segments = [
        {
            'name': 'UK_All_Users',
            'display_name': 'UK - All Users',
            'field_name': 'uk_total_users',
            'description': 'All UK users',
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
                    }
                ]
            }
        },
        {
            'name': 'UK_Active_Users',
            'display_name': 'UK - Active Users',
            'field_name': 'uk_active_users',
            'description': 'UK active users (60d)',
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
        },
        {
            'name': 'UK_Received_Email',
            'display_name': 'UK - Received Email',
            'field_name': 'uk_email_received',
            'description': 'UK users who received email',
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
                        "action_name": "MOE_EMAIL_SENT",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        },
        {
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
            'name': 'UK_Active_Received_Email',
            'display_name': 'UK - Active Users Received Email',
            'field_name': 'uk_email_received_active',
            'description': 'UK active users who received email',
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
                        "action_name": "MOE_EMAIL_SENT",
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
            'name': 'UK_Unsubscribed_Push',
            'display_name': 'UK - Unsubscribed Push',
            'field_name': 'uk_push_unsubscribed',
            'description': 'UK users who unsubscribed from push',
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
                        "action_name": "unsubscribed to push",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        },
        {
            'name': 'UK_Unsubscribed_Email',
            'display_name': 'UK - Unsubscribed Email',
            'field_name': 'uk_email_unsubscribed',
            'description': 'UK users who unsubscribed from email',
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
                        "action_name": "email unsubscribes",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
        }
    ]
    
    # UAE Segments (8 total) - same structure but with AE country code
    uae_segments = []
    for uk_segment in uk_segments:
        uae_segment = uk_segment.copy()
        uae_segment['name'] = uk_segment['name'].replace('UK_', 'UAE_')
        uae_segment['display_name'] = uk_segment['display_name'].replace('UK', 'UAE')
        uae_segment['field_name'] = uk_segment['field_name'].replace('uk_', 'uae_')
        uae_segment['description'] = uk_segment['description'].replace('UK', 'UAE')
        
        # Deep copy filters and change country code
        uae_segment['filters'] = copy.deepcopy(uk_segment['filters'])
        uae_segment['filters']['filters'][0]['value'] = ['AE']  # Change GB to AE
        
        uae_segments.append(uae_segment)
    
    # Combine all segments
    all_segments = uk_segments + uae_segments
    
    # Create each segment with delays to avoid rate limiting
    successful_segments = []
    
    for i, segment_def in enumerate(all_segments):
        try:
            result = automation.create_segment(
                segment_def['name'], 
                segment_def['description'], 
                segment_def['filters']
            )
            
            if isinstance(result, dict) and 'error' not in result:
                # Add display info
                result['display_name'] = segment_def['display_name']
                result['field_name'] = segment_def['field_name']
                successful_segments.append(result)
            
        except Exception as e:
            # Continue processing other segments even if one fails
            continue
        
        # Add delay between API calls (except after the last one)
        if i < len(all_segments) - 1:
            time.sleep(2)  # 2-second delay between calls
    
    return {
        'segments': successful_segments,
        'segment_ids': [seg['id'] for seg in successful_segments if seg.get('id') and seg['id'] != 'unknown']
    }

'''

# Replace the old function with the new one
new_lines = lines[:start_idx] + [new_function + '\n'] + lines[end_idx:]

# Write back to file
with open('app.py', 'w') as f:
    f.writelines(new_lines)

print(f"✅ Successfully replaced function")
print(f"📏 New function length: {len(new_function.split(chr(10)))} lines")
print(f"📏 File size change: {len(new_lines) - len(lines)} lines")
print(f"✅ app.py has been updated!")