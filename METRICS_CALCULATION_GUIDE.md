# Comprehensive Metrics - Calculation Guide

## 📊 METRIC DEFINITIONS AND FORMULAS

This guide explains how each metric in the Comprehensive Metrics Dashboard is calculated, including the numerator and denominator for each calculation.

---

## 1. % RECEIVING COMMUNICATIONS (TOTAL USERBASE)

**Purpose**: Measure what percentage of your entire user base received communications

### Push Notifications
```
Formula: (Users who received push / Total users) × 100

Numerator: Users who received at least 1 push notification
Denominator: Total users in the country (all users)

Example (UK):
34,250 users received push / 50,000 total users = 68.5%
```

### Email
```
Formula: (Users who received email / Total users) × 100

Numerator: Users who received at least 1 email
Denominator: Total users in the country (all users)

Example (UK):
36,150 users received email / 50,000 total users = 72.3%
```

---

## 2. UNSUBSCRIBE RATE

**Purpose**: Measure the percentage of recipients who unsubscribed from communications

### Push Notifications
```
Formula: (Push unsubscribes / Push recipients) × 100

Numerator: Users who unsubscribed from push notifications
Denominator: Users who received push notifications

Example (UK):
719 unsubscribes / 34,250 recipients = 2.1%
```

### Email
```
Formula: (Email unsubscribes / Email recipients) × 100

Numerator: Users who unsubscribed from emails
Denominator: Users who received emails

Example (UK):
651 unsubscribes / 36,150 recipients = 1.8%
```

---

## 3. % RECEIVING COMMUNICATIONS (ACTIVE USERBASE)

**Purpose**: Measure what percentage of active users (those who transacted in last 60 days) received communications

### Push Notifications
```
Formula: (Active users who received push / Total active users) × 100

Numerator: Active users who received at least 1 push notification
Denominator: Total active users (transacted in last 60 days)

Example (UK):
17,840 active users received push / 20,000 active users = 89.2%
```

### Email
```
Formula: (Active users who received email / Total active users) × 100

Numerator: Active users who received at least 1 email
Denominator: Total active users (transacted in last 60 days)

Example (UK):
18,300 active users received email / 20,000 active users = 91.5%
```

---

## 4. COMMUNICATIONS PER USER

**Purpose**: Measure the average number of communications sent per user

### Transactional Push Notifications
```
Formula: Total transactional push sent / Transacted users

Numerator: Total transactional push notifications sent
Denominator: Users who made a transaction in the period

Example (UK):
64,000 transactional push sent / 20,000 transacted users = 3.2 per user
```

### Transactional Email
```
Formula: Total transactional email sent / Transacted users

Numerator: Total transactional emails sent
Denominator: Users who made a transaction in the period

Example (UK):
56,000 transactional emails sent / 20,000 transacted users = 2.8 per user
```

### Promotional Push Notifications
```
Formula: Total promotional push sent / Total users

Numerator: Total promotional push notifications sent
Denominator: Total users in the country (all users)

Example (UK):
80,000 promotional push sent / 50,000 total users = 1.6 per user
```

### Promotional Email
```
Formula: Total promotional email sent / Total users

Numerator: Total promotional emails sent
Denominator: Total users in the country (all users)

Example (UK):
70,000 promotional emails sent / 50,000 total users = 1.4 per user
```

**Note**: Different denominators are used because:
- **Transactional**: Only sent to users who transacted → use transacted users
- **Promotional**: Sent to broader audience → use total users

---

## 5. PUSH NOTIFICATION CTR (CLICK-THROUGH RATE)

**Purpose**: Measure the percentage of delivered push notifications that were clicked

```
Formula: (Push clicks / Push delivered) × 100

Numerator: Total push notification clicks
Denominator: Total push notifications delivered

Example (UK):
6,768 clicks / 144,000 delivered = 4.7%
```

**Note**: "Delivered" means successfully delivered to device, not just sent

---

## 6. EMAIL OPEN RATE

**Purpose**: Measure the percentage of delivered emails that were opened

```
Formula: (Email opens / Email delivered) × 100

Numerator: Total email opens
Denominator: Total emails delivered

Example (UK):
28,098 opens / 126,000 delivered = 22.3%
```

**Note**: "Delivered" means successfully delivered to inbox, not bounced

---

## 📋 DATA SOURCES

### Current Implementation (Sample Data):
- All numbers are generated as realistic sample data
- Used for demonstration and UI testing
- Refresh button generates new random variations

### Future Implementation (Real Data):
When APIs are available, data will come from:

1. **MoEngage Stats API** (once enabled):
   - Campaign sent counts
   - Delivered counts
   - Click counts
   - Open counts

2. **MoEngage Segmentation API**:
   - Total users by country
   - Active users (60-day transactors)
   - Users who received communications

3. **MoEngage Campaign Details API**:
   - Campaign lists by date range
   - Campaign classification (UK/UAE, Push/Email, TX/PR)

4. **MoEngage Reports API** (fallback):
   - Campaign performance data
   - Fixed date ranges

---

## 🎯 METRIC INTERPRETATION

### Good Benchmarks:

1. **% Receiving Comms (Total)**: 60-80%
   - Too low: Not reaching enough users
   - Too high: May be over-communicating

2. **Unsubscribe Rate**: < 2%
   - < 1%: Excellent
   - 1-2%: Good
   - > 2%: Review communication strategy

3. **% Receiving Comms (Active)**: 85-95%
   - High percentage is good for active users
   - Shows effective targeting

4. **Comms Per User**:
   - Transactional: 2-4 per user (depends on business)
   - Promotional: 1-2 per user (avoid fatigue)

5. **Push CTR**: 3-7%
   - < 3%: Review messaging and timing
   - 3-7%: Good performance
   - > 7%: Excellent engagement

6. **Email Open Rate**: 20-30%
   - < 15%: Review subject lines
   - 20-30%: Industry standard
   - > 30%: Excellent performance

---

## 🔄 CALCULATION WORKFLOW

### Step 1: Data Collection
1. Get total users by country (Segmentation API)
2. Get active users by country (Segmentation API)
3. Get campaign data by date range (Stats API or Reports API)
4. Get user engagement data (who received what)

### Step 2: Classification
1. Classify campaigns by country (UK/UAE)
2. Classify campaigns by channel (Push/Email)
3. Classify campaigns by type (Transactional/Promotional)

### Step 3: Aggregation
1. Sum sent counts by classification
2. Sum delivered counts by classification
3. Sum engagement counts (clicks, opens)
4. Count unique users by segment

### Step 4: Calculation
1. Apply formulas for each metric
2. Round to appropriate decimal places
3. Format as percentages where applicable

### Step 5: Presentation
1. Display in dashboard with color coding
2. Show raw numbers alongside percentages
3. Provide context and insights

---

## 📊 EXAMPLE CALCULATION WALKTHROUGH

### Scenario: Calculate UK Push CTR for February 2026

**Step 1: Collect Data**
- Total push notifications delivered: 144,000
- Total push notification clicks: 6,768

**Step 2: Apply Formula**
```
CTR = (Clicks / Delivered) × 100
CTR = (6,768 / 144,000) × 100
CTR = 0.047 × 100
CTR = 4.7%
```

**Step 3: Interpret**
- 4.7% is within the good range (3-7%)
- This means about 1 in 21 delivered push notifications were clicked
- Performance is healthy and meeting benchmarks

---

## 🎯 KEY TAKEAWAYS

1. **Different denominators matter**: Use the right user base for each metric
2. **Delivered vs Sent**: Always use delivered counts for engagement rates
3. **Active vs Total**: Active user metrics show engagement quality
4. **Transactional vs Promotional**: Different expectations and benchmarks
5. **Context is important**: Compare against industry benchmarks and historical data

---

## 📝 NOTES FOR IMPLEMENTATION

When implementing with real data:

1. **Handle edge cases**:
   - Division by zero (when denominator is 0)
   - Missing data (campaigns with no delivery data)
   - Outliers (unusually high/low values)

2. **Data validation**:
   - Ensure numerator ≤ denominator for percentages
   - Check for negative values
   - Verify date ranges match

3. **Performance optimization**:
   - Cache frequently accessed data
   - Batch API calls where possible
   - Use pagination for large datasets

4. **Error handling**:
   - Graceful fallbacks when APIs fail
   - Clear error messages for users
   - Logging for debugging

---

**Last Updated**: February 5, 2026
**Version**: 1.0
**Status**: Sample Data Implementation Complete
