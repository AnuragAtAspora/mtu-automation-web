# API Integration Plan for Comprehensive Metrics Dashboard

## CURRENT STATE
- Dashboard displays sample data for all 6 metrics
- User selects date range (start_date, end_date)
- Data refreshes with random sample values

## INTEGRATION OPTIONS

### OPTION 1: Stats API (Preferred - Once Enabled)

**Status**: API exists but returns 403 (not enabled for account)

**What We Get**:
- Campaign sent counts by platform
- Delivered counts
- Click counts (for CTR)
- Open counts (for open rate)
- All data with exact date ranges

**Integration Process**:

1. **User Input**: Select start_date and end_date
2. **API Call**: POST to `/core-services/v1/campaign-stats`
3. **Response Processing**:
   - Parse campaign data by country (UK/UAE from campaign names)
   - Parse by channel (Push/Email from platforms)
   - Parse by type (Transactional/Promotional from campaign names)
   - Extract sent, delivered, clicks, opens
4. **Segment Creation** (for user counts):
   - Create segments for total users by country
   - Create segments for active users by country
   - Create segments for users who received comms
5. **User Manual Input**: Get segment counts from MoEngage dashboard
6. **Calculate Metrics**: Apply formulas with real data
7. **Display Results**: Show in dashboard

**Data Flow**:
```
User selects dates → Stats API call → Parse campaigns → Create segments → 
User enters counts → Calculate metrics → Display dashboard
```

---

### OPTION 2: Campaign Details API (Current Fallback)

**Status**: Working, but missing performance metrics

**What We Get**:
- Campaign lists with dynamic date filtering
- Campaign names (for UK/UAE classification)
- Campaign channels (Push/Email)
- Campaign status (Sent)

**What We DON'T Get**:
- Sent counts per campaign
- Delivered counts
- Click counts
- Open counts
- Unsubscribe counts

**Integration Process**:

1. **User Input**: Select start_date and end_date
2. **API Call**: POST to `/core-services/v1/campaigns/search`
3. **Response Processing**:
   - Count campaigns by country/channel/type
   - Use campaign counts as proxy metrics
4. **Limitation**: Cannot calculate actual performance metrics

**Not Recommended**: Missing critical performance data

---

### OPTION 3: Reports API (Current Implementation)

**Status**: Working but has fixed date ranges

**What We Get**:
- Campaign sent counts
- Delivered counts (for some channels)
- All data from pre-configured reports

**What We DON'T Get**:
- Dynamic date ranges (reports have fixed periods)
- Click/open data (not in current reports)
- Unsubscribe data

**Limitation**: Reports cover ~January 1-2, 2026 only

**Not Recommended**: Cannot support user-selected date ranges

---

## RECOMMENDED APPROACH

### Phase 1: Contact MoEngage Support
**Action**: Request Stats API enablement
**Timeline**: 1-2 weeks
**Outcome**: Full access to performance data with dynamic dates

### Phase 2: Implement Stats API Integration
Once enabled, implement the following workflow:

#### Step 1: Date Selection
```
User Interface:
- Start Date input
- End Date input
- "Generate Report" button
```

#### Step 2: Stats API Call
```python
def get_campaign_stats(start_date, end_date):
    url = "https://api-01.moengage.com/core-services/v1/campaign-stats"
    payload = {
        'request_id': f"metrics_{timestamp}",
        'start_date': start_date,
        'end_date': end_date,
        'attribution_type': 'TOTAL_CONVERSIONS',
        'metric_type': 'TOTAL',
        'offset': 0,
        'limit': 100
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

#### Step 3: Parse Campaign Data
```python
def parse_campaign_data(stats_data):
    metrics = {
        'uk': {'tx_pn': 0, 'tx_email': 0, 'pr_pn': 0, 'pr_email': 0},
        'uae': {'tx_pn': 0, 'tx_email': 0, 'pr_pn': 0, 'pr_email': 0}
    }
    
    for campaign in stats_data['data']:
        name = campaign['campaign_name'].lower()
        
        # Classify country
        country = 'uk' if 'uk' in name else 'uae' if 'uae' in name else None
        
        # Classify type
        is_tx = any(word in name for word in ['tx', 'transactional', 'trans'])
        
        # Parse platforms
        for platform, data in campaign['platforms'].items():
            is_push = platform in ['android', 'ios', 'web']
            is_email = platform == 'email'
            
            sent = data['performance_stats']['sent']
            delivered = data['performance_stats']['delivered']
            clicks = data['performance_stats']['clicks']
            opens = data['performance_stats']['opens']
            
            # Aggregate by classification
            # ... (aggregate logic)
    
    return metrics
```

#### Step 4: Create User Segments
```python
def create_user_segments(start_date, end_date):
    segments = {}
    
    for country in ['UK', 'UAE']:
        # Total users
        segments[f'{country}_total'] = create_segment(
            filters={'country': country_code}
        )
        
        # Active users (60 days)
        segments[f'{country}_active'] = create_segment(
            filters={'country': country_code, 'transacted_last_60d': True}
        )
        
        # Users who received push
        segments[f'{country}_push_received'] = create_segment(
            filters={'country': country_code, 'received_push': True, 'date_range': (start_date, end_date)}
        )
        
        # Users who received email
        segments[f'{country}_email_received'] = create_segment(
            filters={'country': country_code, 'received_email': True, 'date_range': (start_date, end_date)}
        )
    
    return segments
```

#### Step 5: User Manual Input
```
Display segment URLs to user:
- UK Total Users: [link] → User enters count
- UK Active Users: [link] → User enters count
- UK Push Recipients: [link] → User enters count
- UK Email Recipients: [link] → User enters count
(repeat for UAE)
```

#### Step 6: Calculate Metrics
```python
def calculate_metrics(campaign_data, user_counts):
    metrics = {}
    
    # 1. % receiving comms (total userbase)
    metrics['uk_pn_total_reach'] = (user_counts['uk_push_received'] / user_counts['uk_total']) * 100
    metrics['uk_email_total_reach'] = (user_counts['uk_email_received'] / user_counts['uk_total']) * 100
    
    # 2. Unsubscribe rate
    # Note: Need unsubscribe data from Stats API
    metrics['uk_pn_unsub'] = (campaign_data['uk']['pn_unsubscribes'] / user_counts['uk_push_received']) * 100
    
    # 3. % receiving comms (active userbase)
    metrics['uk_pn_active_reach'] = (user_counts['uk_push_received_active'] / user_counts['uk_active']) * 100
    
    # 4. Comms per user
    metrics['uk_pn_trans_per_user'] = campaign_data['uk']['tx_pn_sent'] / user_counts['uk_transacted']
    metrics['uk_pn_promo_per_user'] = campaign_data['uk']['pr_pn_sent'] / user_counts['uk_total']
    
    # 5. Push CTR
    metrics['uk_pn_ctr'] = (campaign_data['uk']['pn_clicks'] / campaign_data['uk']['pn_delivered']) * 100
    
    # 6. Email Open Rate
    metrics['uk_email_open'] = (campaign_data['uk']['email_opens'] / campaign_data['uk']['email_delivered']) * 100
    
    return metrics
```

#### Step 7: Display Dashboard
```
Update dashboard with real data:
- Replace sample values with calculated metrics
- Show data source: "Stats API (Real-time)"
- Show date range: "Feb 1 - Feb 28, 2026"
- Add "Last Updated" timestamp
```

---

## DATA REQUIREMENTS

### From Stats API:
- Campaign sent counts (by platform)
- Campaign delivered counts
- Campaign click counts
- Campaign open counts
- Campaign unsubscribe counts (if available)

### From Segmentation API:
- Total users by country
- Active users by country (transacted in last 60 days)
- Users who received push (by date range)
- Users who received email (by date range)
- Active users who received push
- Active users who received email

### User Manual Input:
- Segment counts (since API doesn't return them)

---

## IMPLEMENTATION TIMELINE

### Week 1: MoEngage Support
- Contact MoEngage to enable Stats API
- Confirm data availability in Stats API response
- Test Stats API with sample date ranges

### Week 2: Backend Development
- Implement Stats API integration
- Implement segment creation logic
- Implement metric calculation functions
- Add error handling and fallbacks

### Week 3: Frontend Integration
- Update dashboard to accept real data
- Add loading states
- Add error messages
- Add data source indicators

### Week 4: Testing & Deployment
- Test with real data
- Verify calculations
- Deploy to production
- Monitor for issues

---

## FALLBACK STRATEGY

If Stats API cannot be enabled:

1. **Manual Data Entry**: Create form for user to manually enter all metrics
2. **Hybrid Approach**: Use Campaign Details API for campaign counts + manual entry for performance
3. **Reports API Enhancement**: Work with MoEngage to create custom reports with needed data

---

## NEXT STEPS

1. **Immediate**: Contact MoEngage support to enable Stats API
2. **Parallel**: Document exact data fields needed from Stats API
3. **Prepare**: Create test environment for Stats API integration
4. **Plan**: Schedule development sprint once Stats API is enabled
