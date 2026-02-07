#!/usr/bin/env python3
"""
Complete all event updates for create_metrics_segments function
"""

# Read the file
with open('app.py', 'r') as f:
    content = f.read()

changes_made = []

# Update 1: UK_Active_Received_Push - needs both push notification events AND sub_event filter
old_active_push = '''                    {
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
                    }'''

new_active_push = '''                    {
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
                    }'''

if old_active_push in content:
    content = content.replace(old_active_push, new_active_push)
    changes_made.append("✅ Updated UK_Active_Received_Push with notification events and sub_event filter")
else:
    changes_made.append("⚠️  Could not find UK_Active_Received_Push segment pattern")

# Update 2: UK_Active_Received_Email - needs sub_event filter for ORDER
old_active_email = '''                    {
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
            'name': 'UK_Unsubscribed_Push','''

new_active_email = '''                    {
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
            'name': 'UK_Unsubscribed_Push','''

if old_active_email in content:
    content = content.replace(old_active_email, new_active_email)
    changes_made.append("✅ Updated UK_Active_Received_Email with sub_event filter")
else:
    changes_made.append("⚠️  Could not find UK_Active_Received_Email segment pattern")

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print("=" * 70)
print("ADDITIONAL EVENT UPDATES APPLIED")
print("=" * 70)
for change in changes_made:
    print(change)
print("=" * 70)
print()
print("Now verifying all changes...")
print()

# Verify
with open('app.py', 'r') as f:
    content = f.read()

# Find the function
func_start = content.find('def create_metrics_segments(start_date, end_date):')
func_end = content.find('def calculate_comprehensive_metrics(campaign_data, user_counts):', func_start)
func_content = content[func_start:func_end]

checks = {
    'sub_event filter present': func_content.count('sub_event') >= 4,  # Should be in 4 places
    'Notification Received Android': 'Notification Received Android' in func_content,
    'Notification Received iOS': 'Notification Received iOS' in func_content,
    'Unsubscribed to Push': 'Unsubscribed to Push' in func_content,
    'Email Unsubscribed': 'Email Unsubscribed' in func_content,
    'No old MOE_PUSH_SENT': 'MOE_PUSH_SENT' not in func_content,
    'No old unsubscribed to push': 'unsubscribed to push' not in func_content,
    'No old email unsubscribes': 'email unsubscribes' not in func_content,
}

print("VERIFICATION RESULTS:")
print("=" * 70)
for name, result in checks.items():
    status = '✅' if result else '❌'
    print(f'{status} {name}: {result}')

if all(checks.values()):
    print("=" * 70)
    print("🎉 ALL EVENT UPDATES COMPLETED AND VERIFIED!")
    print()
    print("Summary of changes:")
    print("1. Active Users: ORDER event now filters by sub_event (COMPLETED OR PAYMENT_COMPLETED)")
    print("2. Push Received: Changed to Notification Received Android OR iOS")
    print("3. Unsubscribe: Updated capitalization (Unsubscribed to Push, Email Unsubscribed)")
    print("4. All changes applied to UK segments")
    print("5. UAE segments auto-generated via deep copy (will inherit all changes)")
else:
    print("=" * 70)
    print("⚠️  Some verifications failed - review above")
