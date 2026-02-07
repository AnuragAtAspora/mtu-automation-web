# Campaign Data Analysis Module - Requirements

## Feature Overview
A standalone Python module to fetch, categorize, and analyze MoEngage campaign data across multiple dimensions: country (UK/UAE), channel (Push/Email), and type (Promotional/Transactional).

## User Stories

### US-1: Fetch Campaign Data by Date Range
**As a** marketing analyst  
**I want to** fetch all campaigns within a specific date range  
**So that** I can analyze campaign performance for any time period

**Acceptance Criteria:**
- 1.1: User can specify start_date and end_date in YYYY-MM-DD format
- 1.2: System fetches all campaigns using MoEngage Stats API with pagination
- 1.3: System handles API rate limiting with appropriate delays
- 1.4: System returns complete campaign list with performance metrics (sent, delivered, opens, clicks, unsubscribes)

### US-2: Categorize Campaigns by Delivery Type
**As a** marketing analyst  
**I want to** distinguish between promotional and transactional campaigns  
**So that** I can analyze each type separately

**Acceptance Criteria:**
- 2.1: System fetches campaign metadata using Campaign Meta API
- 2.2: System categorizes ONE_TIME campaigns as "promotional"
- 2.3: System categorizes EVENT_TRIGGERED campaigns as "transactional"
- 2.4: System handles unknown delivery types gracefully

### US-3: Organize Campaigns into 8 Categories
**As a** marketing analyst  
**I want to** view campaigns organized by country, channel, and type  
**So that** I can analyze performance across all dimensions

**Acceptance Criteria:**
- 3.1: System identifies country from campaign name/ID (UK or UAE)
- 3.2: System identifies channel from campaign metadata (Push or Email)
- 3.3: System creates 8 distinct categories:
  - UK-Promotional-Push
  - UK-Promotional-Email
  - UK-Transactional-Push
  - UK-Transactional-Email
  - UAE-Promotional-Push
  - UAE-Promotional-Email
  - UAE-Transactional-Push
  - UAE-Transactional-Email
- 3.4: Each campaign is assigned to exactly one category
- 3.5: Campaigns that cannot be categorized are excluded with logging

### US-4: Generate Summary Statistics
**As a** marketing analyst  
**I want to** see aggregated statistics for each category  
**So that** I can quickly understand performance across segments

**Acceptance Criteria:**
- 4.1: System calculates total campaigns per category
- 4.2: System calculates total sent, delivered, opens, clicks, unsubscribes per category
- 4.3: System calculates delivery rate, open rate, and CTR per category
- 4.4: System displays statistics in readable format

### US-5: Export Campaign Data
**As a** marketing analyst  
**I want to** export campaign data to CSV files  
**So that** I can perform additional analysis in spreadsheet tools

**Acceptance Criteria:**
- 5.1: System exports all campaigns to a single CSV file
- 5.2: CSV includes all campaign fields (ID, name, channel, category, metrics)
- 5.3: System provides option to export each of the 8 categories to separate CSV files
- 5.4: Export includes summary statistics at the top or in a separate summary file

## Technical Requirements

### TR-1: API Integration
- Use MoEngage Stats API for campaign performance data
- Use MoEngage Campaign Meta API for delivery type information
- Implement proper authentication with workspace ID and campaign API key
- Handle API pagination (10 campaigns per request limit)
- Implement rate limiting (2-second delays between requests)

### TR-2: Data Structure
- Campaign data must include: campaign_id, campaign_name, channel, delivery_type, category, sent, delivered, open, click, unsubscribe, bounce, failed, open_rate, ctr, delivery_rate
- Category grouping must use dictionary with 8 predefined keys
- All numeric metrics must be integers or floats as appropriate

### TR-3: Error Handling
- Handle API errors gracefully with informative messages
- Handle missing or malformed campaign data
- Handle network timeouts and connection errors
- Log campaigns that cannot be categorized

### TR-4: Performance
- Fetch campaigns with pagination to handle large datasets
- Support max_campaigns parameter to limit fetching for testing
- Minimize API calls by batching where possible

## Non-Functional Requirements

### NFR-1: Usability
- Module should be runnable as standalone script
- Module should be importable for use in other applications
- Clear console output showing progress and results

### NFR-2: Maintainability
- Clean separation between fetching (CampaignDataFetcher) and analysis (CampaignAnalyzer)
- Well-documented methods with type hints
- Configurable credentials and data center

### NFR-3: Extensibility
- Easy to add new filtering dimensions
- Easy to add new export formats
- Easy to add new aggregation metrics

## Out of Scope
- Real-time campaign monitoring
- Campaign creation or modification
- Integration with web application (this is a standalone module)
- Advanced statistical analysis (correlation, forecasting, etc.)
- Visualization/charting capabilities

## Dependencies
- Python 3.7+
- requests library
- MoEngage API access (Stats API and Campaign Meta API enabled)
- Valid workspace credentials

## Success Metrics
- Successfully fetch and categorize 100% of campaigns in date range
- Correctly identify country, channel, and type for 95%+ of campaigns
- Complete data fetch and analysis within reasonable time (< 5 minutes for 1000 campaigns)
- Export data in format compatible with Excel/Google Sheets
