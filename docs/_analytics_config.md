# Google Analytics Configuration for Danish Parliament API Documentation

## Analytics Setup Guide

### 1. Google Analytics 4 Property Setup

1. Create a new GA4 property at [analytics.google.com](https://analytics.google.com)
2. Set property name: "Danish Parliament API Documentation"
3. Set industry category: "Technology > Software"
4. Set business objectives: 
   - "Examine user behavior"
   - "Measure content and product performance"

### 2. Measurement ID Configuration

Replace the placeholder `G-XXXXXXXXXX` in `mkdocs.yml` with your actual Measurement ID.

### 3. Event Tracking Categories

Our documentation tracks the following events automatically:

#### API Usage Events
- **Event Category**: `API_Usage`
- **Actions**:
  - `query_built` - When users build API queries using interactive builder
  - `filter_used` - When users add filters to queries
  - `expand_used` - When users add expand parameters

#### Documentation Events
- **Event Category**: `Documentation`
- **Actions**:
  - `code_copied` - When users copy code examples
  - **Labels**: Programming language (python, javascript, bash, etc.)

#### External Links Events
- **Event Category**: `External_Links`
- **Actions**:
  - `click` - When users click external links
  - **Labels**: Destination URL

#### Navigation Events
- **Event Category**: `Navigation`
- **Actions**:
  - `anchor_click` - When users click internal anchor links
  - **Labels**: Anchor target (#section-name)

#### Search Events
- **Event Category**: `Search`
- **Actions**:
  - `query` - When users search documentation
  - **Labels**: `short_query` (<=10 chars) or `long_query` (>10 chars)

#### Engagement Events
- **Event Category**: `Engagement`
- **Actions**:
  - `scroll_depth` - Track scrolling in 25% increments
  - `time_on_page` - Track time spent (short/medium/long)

### 4. Recommended Goals Setup

#### Goal 1: API Query Builder Usage
- **Type**: Event
- **Event Conditions**: 
  - Event name equals `query_built`
- **Purpose**: Track how many users interact with API examples

#### Goal 2: Code Copy Engagement
- **Type**: Event
- **Event Conditions**:
  - Event name equals `code_copied`
- **Purpose**: Measure code example utility

#### Goal 3: Deep Engagement
- **Type**: Event
- **Event Conditions**:
  - Event name equals `scroll_depth`
  - Event parameter `value` greater than 50
- **Purpose**: Track users who read more than half the page

#### Goal 4: External API Access
- **Type**: Event
- **Event Conditions**:
  - Event name equals `click`
  - Event parameter `event_label` contains `oda.ft.dk`
- **Purpose**: Track users who access the actual API

### 5. Custom Dimensions

Set up these custom dimensions for better insights:

1. **Page Section** - Track which documentation section users engage with most
2. **User Type** - Distinguish between new and returning developers
3. **Device Category** - Mobile vs Desktop usage patterns
4. **Programming Language Interest** - Based on code copy events

### 6. Audience Segments

Create these segments for targeted analysis:

#### Active API Users
- Users who triggered `API_Usage` events
- Minimum session duration: 2 minutes

#### Code-Heavy Users
- Users who copied 3+ code examples
- Multiple `Documentation` events

#### Mobile Users
- Device category: Mobile
- Useful for mobile optimization insights

#### Research-Heavy Users
- High scroll depth (>75%)
- Long time on page (>5 minutes)
- Multiple search queries

### 7. Reports to Monitor

#### Engagement Reports
- **Pages and screens**: Most viewed documentation sections
- **Events**: Top triggered events and their frequency
- **Conversions**: Goal completion rates

#### Technology Reports
- **Browser**: Ensure compatibility across browsers
- **Operating System**: Desktop vs mobile usage
- **Screen Resolution**: Optimize for common resolutions

#### Acquisition Reports
- **Traffic acquisition**: How users find the documentation
- **User acquisition**: New vs returning user patterns

### 8. Dashboard Recommendations

Create a custom dashboard with:

1. **API Usage Tile**
   - Total API queries built
   - Most popular entities
   - Filter usage rate

2. **Content Performance Tile**
   - Most copied code examples
   - Page scroll depth averages
   - Search query trends

3. **User Engagement Tile**
   - Average session duration
   - Pages per session
   - Bounce rate by section

4. **Technical Performance Tile**
   - Page load times
   - Mobile vs desktop usage
   - Browser compatibility issues

### 9. Privacy Considerations

The analytics configuration includes:

- **Cookie consent** - Users can opt out via Material theme consent
- **IP anonymization** - Enabled by default in GA4
- **Data retention** - Set to 14 months (recommended for API docs)
- **No PII collection** - Only anonymous usage patterns tracked

### 10. Regular Review Schedule

#### Weekly
- Check for broken external links (via External_Links events)
- Monitor search queries for content gaps
- Review mobile usage patterns

#### Monthly
- Analyze code copy patterns to improve examples
- Review scroll depth to optimize content length
- Check goal conversion rates

#### Quarterly
- Update audience segments based on usage patterns
- Review custom dimensions effectiveness
- Optimize based on top user flows

## Implementation Notes

All event tracking is implemented in `assets/js/interactive.js` and will automatically work once the GA4 Measurement ID is configured in `mkdocs.yml`.

The tracking respects user privacy and follows GDPR guidelines with opt-in cookie consent.