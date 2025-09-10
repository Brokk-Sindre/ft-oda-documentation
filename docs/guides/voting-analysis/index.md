# Voting Analysis Guide

## Overview

The Danish Parliamentary OData API provides comprehensive access to voting records from the Folketing, enabling sophisticated analysis of parliamentary voting behavior. With detailed individual vote tracking, party alignment data, and historical voting patterns spanning multiple decades, researchers and analysts can conduct deep investigations into Danish democratic processes.

This guide provides a complete overview of voting analysis capabilities, from basic vote counting to advanced political trend analysis and coalition dynamics tracking.

## Available Voting Data

### Core Voting Entities

The API provides access to voting data through four primary entities:

#### Afstemning (Voting Sessions)
Contains voting session metadata including:
- **konklusion**: Detailed voting results by party
- **vedtaget**: Boolean indicating if proposal passed
- **nummer**: Sequential voting session number
- **typeid**: Type of voting session (final adoption, committee recommendation, etc.)
- **mødeid**: Link to meeting where vote occurred
- **sagstrinid**: Connection to case step in legislative process

#### Stemme (Individual Votes) 
Tracks individual politician votes with:
- **typeid**: Vote choice (1=for, 2=against, 3=absent, 4=abstain)
- **afstemningid**: Reference to voting session
- **aktørid**: Reference to specific politician
- **opdateringsdato**: Last update timestamp

#### Stemmetype (Vote Types)
Four possible voting choices:
1. **For** (Yes/Support)
2. **Imod** (No/Against) 
3. **Fravær** (Absent)
4. **Hverken for eller imod** (Abstain/Neither)

#### Afstemningstype (Voting Session Types)
Classification of voting contexts:
1. **Endelig vedtagelse** (Final Adoption)
2. **Udvalgsindstilling** (Committee Recommendation)
3. **Forslag til vedtagelse** (Adoption Proposal)
4. **Ændringsforslag** (Amendment)

## Voting Analysis Capabilities

### Individual Politician Analysis

Track specific politicians' voting behavior with complete biographical context:

```bash
# Get all votes by specific politician with voting session details
curl "https://oda.ft.dk/api/Stemme?%24expand=Afstemning,Aktør&%24filter=Aktør/navn%20eq%20'[Politician Name]'"
```

**Key Insights Available:**
- Personal voting patterns and consistency
- Coalition loyalty vs. independent positions
- Issue-specific voting behavior
- Attendance rates and abstention patterns
- Career progression impact on voting behavior

### Party-Level Voting Analysis

Analyze party cohesion and alignment patterns:

```bash
# Get voting patterns by party affiliation
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktör,Afstemning&%24filter=Aktör/gruppenavnkort%20eq%20'[Party Abbreviation]'"
```

**Analysis Capabilities:**
- **Party Cohesion**: Measure internal voting consistency
- **Cross-Party Alliances**: Identify collaboration patterns
- **Opposition Dynamics**: Track government vs. opposition voting
- **Issue-Based Coalitions**: Find topic-specific alliances
- **Minority Government Support**: Analyze external support patterns

### Voting Pattern Recognition

Identify trends and patterns across time periods:

**Temporal Analysis:**
- Long-term voting trend identification
- Parliamentary period comparisons
- Seasonal or cyclical voting patterns
- Crisis response voting behavior

**Issue-Based Pattern Analysis:**
- Topic categorization through case linkage
- Policy area voting consistency
- Amendment vs. final vote patterns
- Committee recommendation alignment

### Coalition and Opposition Dynamics

Track government formation and opposition behavior:

**Government Coalition Analysis:**
- Coalition partner voting alignment
- Coalition discipline measurement
- Minority government support tracking
- Government stability indicators

**Opposition Strategy Analysis:**
- Opposition unity measurements
- Strategic abstention patterns
- Alternative proposal success rates
- Opposition influence on amendments

## Historical Voting Analysis

### Parliamentary Period Comparisons

The API provides access to voting data across multiple parliamentary periods:

```bash
# Get voting data by specific period
curl "https://oda.ft.dk/api/Afstemning?%24expand=Møde/Periode&%24filter=Møde/Periode/id%20eq%20[PeriodID]"
```

**Historical Analysis Capabilities:**
- **Electoral Impact**: Compare pre/post-election voting patterns
- **Government Changes**: Analyze voting shifts during transitions
- **Long-term Trends**: Track issue evolution across decades
- **Institutional Changes**: Measure voting behavior changes with rule modifications
- **Crisis Response**: Compare voting during different crisis periods

### Data Coverage and Quality

Based on research findings:
- **Active Tracking**: Real-time updates with same-day accuracy
- **Individual Granularity**: Complete person-level voting records
- **Comprehensive Metadata**: Full biographical and institutional context
- **Referential Integrity**: Verified cross-entity relationship accuracy
- **Historical Depth**: Multiple decades of parliamentary periods available

## Performance Considerations

### Optimal Query Strategies

**For Large-Scale Analysis:**
- Use `$top` parameter with maximum 1000 records per request
- Implement pagination with `$skip` for complete datasets
- Leverage `$select` to reduce response size for specific fields only
- Use `opdateringsdato` for efficient change detection

**Query Performance Guidelines:**
- Simple queries: ~98ms response time
- Complex expansions: ~1-2 seconds for 100 records
- Large datasets: ~2 seconds for 10,000 records
- Multi-level expansions: Use strategically to minimize API calls

### Best Practices for Political Analysis

**Data Quality Assurance:**
- Verify politician names and IDs before large-scale queries
- Handle absent/abstain votes appropriately in calculations
- Account for party affiliation changes over time
- Cross-reference voting data with case metadata for context

**Analysis Methodology:**
- Use `konklusion` field for official party-level results
- Track individual votes through `Stemme` entity for detailed analysis
- Link voting sessions to meetings for temporal context
- Expand to `Aktör` entity for complete biographical context

## Navigation to Specific Guides

This section provides detailed guides for specific voting analysis use cases:

### [Politician Votes](politician-votes.md)
Deep dive into individual politician voting behavior analysis, including:
- Personal voting pattern analysis
- Career impact correlation
- Consistency measurements
- Biographical context integration

### [Party Analysis](party-analysis.md)
Comprehensive party-level voting analysis covering:
- Party cohesion metrics
- Internal discipline measurement
- Leadership influence analysis
- Policy position evolution

### [Voting Patterns](voting-patterns.md)
Advanced pattern recognition and trend analysis including:
- Temporal voting trends
- Issue-based pattern identification
- Coalition formation prediction
- Opposition strategy analysis

## Getting Started

### Basic Voting Analysis Query

Start with a simple query to understand the data structure:

```bash
# Get recent voting sessions with basic details
curl "https://oda.ft.dk/api/Afstemning?%24orderby=opdateringsdato%20desc&%24top=10"

# Get individual votes for a recent session
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktör&%24filter=afstemningid%20eq%20[VotingID]&%24top=100"
```

### Common Analysis Patterns

**Track Climate Legislation Voting:**
```bash
curl "https://oda.ft.dk/api/Sag?%24expand=Sagstrin/Afstemning/Stemme&%24filter=substringof('klima',titel)"
```

**Monitor Recent Parliamentary Activity:**
```bash
curl "https://oda.ft.dk/api/Afstemning?%24expand=Møde&%24filter=opdateringsdato%20gt%20datetime'2025-01-01'&%24orderby=opdateringsdato%20desc"
```

**Analyze Party Voting Alignment:**
```bash
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktör,Afstemning&%24filter=Aktör/gruppenavnkort%20eq%20'S'%20and%20Afstemning/vedtaget%20eq%20true"
```

## Key Technical Notes

### URL Encoding Requirements
Always use `%24` instead of `$` for OData parameters:
- `%24filter` instead of `$filter`
- `%24expand` instead of `$expand`
- `%24top` instead of `$top`

### Relationship Expansions
Supported expansion patterns for voting analysis:
- **Single Level**: `$expand=Afstemning` or `$expand=Aktör`
- **Two Level**: `$expand=Stemme/Aktör` or `$expand=Afstemning/Møde`
- **Strategic Use**: Balance detail needs with performance requirements

### Data Freshness
The API provides real-time or near real-time updates:
- Voting records updated within hours of sessions
- `opdateringsdato` timestamps reflect recent parliamentary activity
- Future meeting schedules available in advance

## Conclusion

The Danish Parliamentary OData API provides unprecedented access to voting data for political analysis, research, and civic engagement. With individual-level vote tracking, comprehensive party data, and historical depth, it enables sophisticated analysis of Danish democratic processes.

Whether conducting academic research, building transparency tools, or analyzing political trends, this voting analysis guide provides the foundation for extracting meaningful insights from Denmark's parliamentary voting records.