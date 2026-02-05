def create_metrics_segments(start_date, end_date):
    """Create segments needed for metrics calculation"""
    
    segments = []
    countries = {'UK': 'GB', 'UAE': 'AE'}
    
    for country_name, country_code in countries.items():
        # 1. Total users
        segment_name = "UK_All_Users" if country_code == 'GB' else "UAE_All_Users"
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
        
        result = automation.create_segment(segment_name, f"All {country_name} users", filters)
        if 'error' not in result:
            result['display_name'] = f"{country_name} - All Users"
            result['field_name'] = f"{country_name.lower()}_total_users"
            segments.append(result)
        
        # 2. Active users (60 days)
        segment_name = "UK_Active_Users" if country_code == 'GB' else "UAE_Active_Users"
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
        
        result = automation.create_segment(segment_name, f"{country_name} active users (60d)", filters)
        if 'error' not in result:
            result['display_name'] = f"{country_name} - Active Users"
            result['field_name'] = f"{country_name.lower()}_active_users"
            segments.append(result)
        
        # 3. Users who received push/email
        for channel, event_names in [('Push', ['MOE_PUSH_SENT']), ('Email', ['MOE_EMAIL_SENT'])]:
            segment_name = f"UK_Received_{channel}" if country_code == 'GB' else f"UAE_Received_{channel}"
            
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
                        "action_name": event_names[0],
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
            
            result = automation.create_segment(segment_name, f"{country_name} users who received {channel.lower()}", filters)
            if 'error' not in result:
                result['display_name'] = f"{country_name} - Received {channel}"
                result['field_name'] = f"{country_name.lower()}_{channel.lower()}_received"
                segments.append(result)
            
            # 4. Active users who received communications
            segment_name = f"UK_Active_Received_{channel}" if country_code == 'GB' else f"UAE_Active_Received_{channel}"
            
            active_end_comm = datetime.now()
            active_start_comm = active_end_comm - timedelta(days=60)
            
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
                        "action_name": event_names[0],
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
                            "value": active_start_comm.strftime('%Y-%m-%dT00:00:00.000Z'),
                            "value1": active_end_comm.strftime('%Y-%m-%dT23:59:59.999Z'),
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
            
            result = automation.create_segment(segment_name, f"{country_name} active users who received {channel.lower()}", filters)
            if 'error' not in result:
                result['display_name'] = f"{country_name} - Active Users Received {channel}"
                result['field_name'] = f"{country_name.lower()}_{channel.lower()}_received_active"
                segments.append(result)
        
        # 5. Users who unsubscribed from push/email
        for channel, event_names in [('Push', ['unsubscribed to push']), ('Email', ['email unsubscribes'])]:
            segment_name = f"UK_Unsubscribed_{channel}" if country_code == 'GB' else f"UAE_Unsubscribed_{channel}"
            
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
                        "action_name": event_names[0],
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
            
            result = automation.create_segment(segment_name, f"{country_name} users who unsubscribed from {channel.lower()}", filters)
            if 'error' not in result:
                result['display_name'] = f"{country_name} - Unsubscribed {channel}"
                result['field_name'] = f"{country_name.lower()}_{channel.lower()}_unsubscribed"
                segments.append(result)
    
    return {
        'segments': segments,
        'segment_ids': [seg['id'] for seg in segments if seg.get('id') and seg['id'] != 'unknown']
    }
