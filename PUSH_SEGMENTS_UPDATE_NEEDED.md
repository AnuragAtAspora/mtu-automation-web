# Push Segments Update - New Logic

## Status: Ready to Apply

The new push segment logic has been defined and tested. It needs to be applied to `app.py` in the `create_metrics_segments` function.

## Changes Required

### 1. Combine Android/iOS Segments
**Current**: 20 segments (separate Android and iOS)
- UK_Received_Push_Android
- UK_Received_Push_iOS  
- UK_Active_Received_Push_Android
- UK_Active_Received_Push_iOS
- (+ UAE equivalents)

**New**: 16 segments (combined)
- UK_Received_Push (single segment)
- UK_Active_Received_Push (single segment)
- (+ UAE equivalents)

### 2. New Event Names
**Old events**:
- `Notification Received Android`
- `Notification Received iOS`

**New events** (combined with OR):
- `NOTIFICATION_RECEIVED_MOE`
- `n_i_s`

### 3. Time Range Change for Active Segments
**UK_Active_Received_Push**:
- Old: Absolute time range (between start_date and end_date)
- New: Relative time range (last 60 days using `inTheLast`)

## New Filter Structure

### UK_Received_Push (Absolute Time)
```python
{
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
                        "value": f"{start_date}T00:00:00.000Z",
                        "value1": f"{end_date}T23:59:59.999Z",
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
                        "value": f"{start_date}T00:00:00.000Z",
                        "value1": f"{end_date}T23:59:59.999Z",
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
```

### UK_Active_Received_Push (Relative Time)
```python
{
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
                        "type": "inTheLast",
                        "value": 60,
                        "value_type": "relative_past",
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
                        "type": "inTheLast",
                        "value": 60,
                        "value_type": "relative_past",
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
            "execution": {"count": 1, "type": "atleast"}
        }
    ]
}
```

## Files to Update
- `app.py` - `create_metrics_segments()` function (lines ~1845-2122)
- Update segment definitions for UK and UAE
- Update field names in templates if needed

## Testing
- `test_new_push_logic.py` - Validates the filter structure
- Test segment creation with new logic
- Verify 16 segments are created (not 20)

## Next Steps
1. Manually update `app.py` with new segment definitions
2. Test segment creation
3. Update templates if field names changed
4. Deploy to Railway

---
**Date**: February 8, 2026
**Status**: Logic defined and tested, ready to apply
