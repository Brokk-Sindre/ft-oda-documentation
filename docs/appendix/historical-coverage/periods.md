# Historical Periods

This section provides comprehensive documentation of the historical periods covered in the Danish Parliamentary OData API, spanning 74+ years of Danish democratic history from 1952 to 2026.

## Overview

The Danish Parliament API provides access to one of the world's most extensive parliamentary datasets, with period metadata covering **165+ distinct parliamentary periods** from October 7, 1952 to October 6, 2026. This exceptional historical depth makes the API invaluable for longitudinal political research, democratic analysis, and institutional studies.

!!! info "Period Definition"
    In Danish parliamentary context, a **period** (*periode*) represents an annual parliamentary session, typically running from October to September of the following year. Each period is identified by a unique `periodeid` and has precise start (`startdato`) and end (`slutdato`) dates.

## Historical Timeline

### Complete Period Coverage

```bash
# Query earliest periods
curl "https://oda.ft.dk/api/Periode?%24orderby=startdato%20asc&%24top=5"

# Query latest periods  
curl "https://oda.ft.dk/api/Periode?%24orderby=slutdato%20desc&%24top=5"
```

**Key Findings:**
- **Start Date**: October 7, 1952 (earliest period)
- **End Date**: October 6, 2026 (latest defined period)
- **Total Span**: 74+ years of continuous coverage
- **Period Count**: 165+ distinct parliamentary periods
- **Future Planning**: Periods pre-defined through 2026

### Era Breakdown

#### 1. Post-War Reconstruction Era (1952-1965)
- **Historical Context**: Recovery from WWII occupation, welfare state foundation
- **Data Characteristics**: Limited digital records, focus on major legislation
- **Key Developments**: NATO membership, social democratic policies
- **Research Applications**: Post-war democratic rebuilding patterns

#### 2. Welfare State Expansion (1965-1980)
- **Historical Context**: Economic growth, comprehensive welfare system development
- **Data Characteristics**: Increasing record keeping, systematic documentation
- **Key Developments**: EEC membership debates, social policy expansion
- **Research Applications**: Welfare state evolution analysis

#### 3. Economic Crisis & Reform (1980-1995)
- **Historical Context**: Economic challenges, political coalition changes
- **Data Characteristics**: Enhanced parliamentary documentation
- **Key Developments**: EU integration, economic liberalization
- **Research Applications**: Crisis response mechanisms, coalition dynamics

#### 4. Digital Era Transition (1995-2014)
- **Historical Context**: Information age adaptation, EU integration
- **Data Characteristics**: Systematic digitization begins
- **Key Developments**: Maastricht Treaty, digital government initiatives
- **Research Applications**: Technology impact on governance

#### 5. Modern Comprehensive Coverage (2014-Present)
- **Historical Context**: Full digital transparency, real-time data
- **Data Characteristics**: Complete record keeping, API-accessible data
- **Key Developments**: Open data initiatives, democratic transparency
- **Research Applications**: Real-time parliamentary analysis

## Data Completeness Analysis

### Metadata vs. Content Availability

!!! warning "Important Distinction"
    The API provides **complete period metadata** back to 1952, but actual **content data availability** varies significantly across historical periods.

#### Period Structure Completeness
```bash
# All periods have complete metadata
curl "https://oda.ft.dk/api/Periode?%24select=startdato,slutdato,titel&%24orderby=startdato"
```
-  **Period Definitions**: 100% complete back to 1952
-  **Date Ranges**: Precise start/end dates for all periods
-  **Temporal Continuity**: No gaps in period sequence

#### Content Data Patterns
```bash
# Check data availability by period
curl "https://oda.ft.dk/api/Sag?%24filter=periodeid%20eq%2094"  # 1952 period
curl "https://oda.ft.dk/api/Afstemning?%24filter=periodeid%20eq%20100"  # 1960s period
```

**Data Availability Characteristics:**

| Period Range | Metadata | Cases (Sag) | Votes (Afstemning) | Documents (Dokument) | Quality Level |
|-------------|----------|-------------|-------------------|------------------|---------------|
| 1952-1965 | Complete | Selective | Minimal | Limited | Archival |
| 1965-1980 | Complete | Moderate | Partial | Moderate | Enhanced |
| 1980-1995 | Complete | Good | Good | Good | Systematic |
| 1995-2014 | Complete | Excellent | Excellent | Excellent | Digital |
| 2014-Present | Complete | Complete | Complete | Complete | Real-time |

### Update Timestamp Analysis

!!! note "Data Migration Pattern"
    The `opdateringsdato` (update date) field shows most historical data was migrated to the API system around 2014, regardless of original document dates.

```bash
# Earliest update timestamps vs. period coverage
curl "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20asc&%24top=3"
```

**Key Insights:**
- **System Deployment**: API system operational since ~2014
- **Historical Migration**: Pre-2014 data migrated during system implementation  
- **Maintenance Updates**: Ongoing data quality improvements reflected in update dates
- **Source Dating**: Original document dates preserved in entity-specific date fields

## Political Context & Milestones

### Electoral Cycles and Government Transitions

#### Major Government Changes by Period

**1950s Foundation Period**
- **1953**: New Constitution adopted
- **1957**: Social Democratic government consolidation
- **Research Impact**: Constitutional framework establishment

**1960s-1970s Expansion Era**
- **1968**: Student movements, social change
- **1973**: "Landslide Election" - political fragmentation
- **1975**: EEC membership referendum
- **Research Impact**: Democratic participation evolution

**1980s-1990s Transformation**
- **1982**: Conservative-Liberal government
- **1993**: Maastricht Treaty ratification
- **Research Impact**: European integration patterns

**2000s-2010s Modernization**
- **2001**: Liberal-Conservative coalition
- **2011**: Social Democratic return
- **Research Impact**: Modern coalition dynamics

**2010s-Present Digital Era**
- **2015**: Immigration policy debates
- **2019**: Social Democratic government
- **Research Impact**: Contemporary policy challenges

### Significant Legislative Milestones

```bash
# Query landmark legislation by period
curl "https://oda.ft.dk/api/Sag?%24filter=contains(titel,'grundlov')"  # Constitution
curl "https://oda.ft.dk/api/Sag?%24filter=contains(titel,'EU')"       # EU legislation
```

**Key Legislative Periods:**
- **1953**: Constitutional reform period
- **1973**: Social policy expansion
- **1986**: Single European Act
- **1992**: Maastricht Treaty implementation
- **2000**: Freedom of Information Act
- **2014**: Open Data Act

## Data Quality Variations

### Historical Period Characteristics

#### Early Periods (1952-1980)
**Strengths:**
- Major legislation well-documented
- Constitutional proceedings complete
- Significant votes recorded

**Limitations:**
- Committee work documentation sparse
- Minor procedural matters missing
- Limited actor relationship data

#### Transition Periods (1980-2000)
**Strengths:**
- Systematic case documentation
- Improved actor tracking
- Enhanced voting records

**Improvements:**
- Digital storage transition
- Standardized procedures
- Better cross-referencing

#### Modern Periods (2000-Present)
**Comprehensive Coverage:**
- Real-time data updates
- Complete procedural records
- Full actor relationship tracking
- Document management systems

### Research Reliability Assessment

| Analysis Type | 1952-1965 | 1965-1980 | 1980-1995 | 1995-2014 | 2014+ |
|--------------|-----------|-----------|-----------|-----------|-------|
| Major Legislation | Excellent | Excellent | Excellent | Excellent | Excellent |
| Voting Analysis | Limited | Good | Excellent | Excellent | Excellent |
| Committee Work | Minimal | Moderate | Good | Excellent | Excellent |
| Actor Networks | Basic | Moderate | Good | Excellent | Excellent |
| Document Flow | Limited | Good | Excellent | Excellent | Excellent |

## Period-Specific Analysis Capabilities

### Temporal Query Patterns

#### By Period ID
```bash
# Analyze specific parliamentary period
curl "https://oda.ft.dk/api/Sag?%24filter=periodeid%20eq%20[PERIOD_ID]&%24expand=SagAktør"
```

#### By Date Range
```bash
# Cross-period temporal analysis
curl "https://oda.ft.dk/api/Afstemning?%24filter=dato%20ge%20datetime'1990-01-01'%20and%20dato%20le%20datetime'1999-12-31'"
```

#### Multi-Period Comparisons
```bash
# Compare across multiple periods
curl "https://oda.ft.dk/api/Sag?%24filter=periodeid%20in%20(120,130,140)&%24select=titel,periodeid,dagsordensnummer"
```

### Research Applications by Era

#### Historical Analysis (1952-1980)
**Recommended Research:**
- Constitutional development studies
- Post-war democratization patterns
- Welfare state formation analysis
- International relations evolution

**Data Considerations:**
- Focus on major legislation
- Limited committee work data
- Selective case coverage

#### Comparative Studies (1980-2014)
**Research Opportunities:**
- Coalition government patterns
- EU integration processes
- Policy innovation cycles
- Democratic institutional changes

**Data Advantages:**
- Comprehensive case tracking
- Systematic voting records
- Enhanced actor documentation

#### Real-Time Analysis (2014-Present)
**Contemporary Research:**
- Live parliamentary monitoring
- Policy development tracking
- Coalition dynamics analysis
- Democratic engagement studies

**Full Data Access:**
- Complete procedural records
- Real-time updates
- Comprehensive relationship data

## Temporal Data Patterns

### Parliamentary Rhythm Analysis

#### Annual Cycles
```bash
# Analyze parliamentary activity patterns
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202023&%24select=opdateringsdato"
```

**Seasonal Patterns:**
- **October-December**: New session startup, budget processes
- **January-March**: Major legislation debates
- **April-June**: Committee work intensification  
- **July-September**: Summer recess, reduced activity

#### Multi-Year Trends
```bash
# Long-term activity analysis
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20ge%202010&%24inlinecount=allpages"
```

**Decadal Evolution:**
- Increasing case complexity over time
- Growing number of actors per case
- Enhanced documentation standards
- More frequent procedural updates

### Historical Comparison Capabilities

#### Cross-Period Statistical Analysis
```python
# Example: Compare legislative output across eras
periods_1960s = api_query("Periode", filter="startdato ge datetime'1960-01-01' and startdato le datetime'1969-12-31'")
periods_2010s = api_query("Periode", filter="startdato ge datetime'2010-01-01' and startdato le datetime'2019-12-31'")

# Analyze case volume changes
cases_1960s = api_query("Sag", filter=f"periodeid in ({','.join(period_ids_1960s)})")
cases_2010s = api_query("Sag", filter=f"periodeid in ({','.join(period_ids_2010s)})")
```

#### Longitudinal Research Design
**Recommended Approaches:**
- Panel studies across multiple periods
- Trend analysis using period breakpoints
- Cohort studies following specific actors
- Policy lifecycle tracking across periods

## Research Applications

### Academic Research Use Cases

#### Political Science Applications
```bash
# Government duration analysis
curl "https://oda.ft.dk/api/Aktør?%24filter=typeid%20eq%205&%24expand=Periode"  # Ministers by period

# Coalition stability research
curl "https://oda.ft.dk/api/Sag?%24filter=contains(titel,'tillid')&%24orderby=periodeid"  # Confidence votes
```

#### Historical Studies
```bash
# Policy innovation tracking
curl "https://oda.ft.dk/api/Sag?%24filter=contains(titel,'miljø')&%24orderby=periodeid"  # Environmental policy evolution

# Democratic participation analysis  
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme&%24orderby=dato"  # Voting participation trends
```

### Practical Applications

#### Journalism & Media
- Historical fact-checking capabilities
- Policy development storylines
- Government accountability tracking
- Legislative process transparency

#### Civic Organizations
- Democratic engagement monitoring
- Policy advocacy research
- Government performance analysis
- Transparency initiatives

#### Legal Research
- Legislative history reconstruction
- Constitutional interpretation support
- Precedent analysis across periods
- Legal development tracking

## Technical Implementation

### Efficient Historical Queries

#### Batch Period Analysis
```bash
# Optimized multi-period queries
curl "https://oda.ft.dk/api/Sag?%24filter=periodeid%20in%20(100,110,120)&%24select=titel,periodeid&%24inlinecount=allpages"
```

#### Temporal Indexing Strategy
```bash
# Use period boundaries for efficient filtering
curl "https://oda.ft.dk/api/Periode?%24select=id,startdato,slutdato&%24orderby=startdato"  # Get period mappings first
```

#### Performance Optimization
**Best Practices:**
- Query periods metadata first for date mapping
- Use period ID filtering over date ranges when possible
- Batch related entity queries for efficiency
- Cache period mappings for repeated analysis

### Data Export Strategies

#### Historical Dataset Construction
```python
# Example: Build comprehensive historical dataset
import requests
import pandas as pd

def build_historical_dataset(start_year, end_year):
    # Get period mappings
    periods = get_periods_by_year_range(start_year, end_year)
    
    # Extract data by period
    historical_data = []
    for period in periods:
        period_data = extract_period_data(period['id'])
        historical_data.append(period_data)
    
    return pd.concat(historical_data)
```

## Future Research Opportunities

### Emerging Research Areas

#### Computational Political Science
- Machine learning on historical parliamentary data
- Natural language processing of debates
- Network analysis across time periods
- Predictive modeling using historical patterns

#### Digital Humanities
- Text mining historical parliamentary records
- Visualization of democratic evolution
- Quantitative analysis of political rhetoric
- Cross-national comparative studies

#### Data Science Applications
- Time series analysis of legislative activity
- Cluster analysis of policy domains
- Social network analysis of political actors
- Sentiment analysis of parliamentary discourse

## Conclusion

The Danish Parliamentary API's 74+ years of historical coverage represents an unprecedented resource for understanding democratic processes over time. From the foundational period of 1952 through the modern digital era, researchers have access to increasingly comprehensive data that enables sophisticated longitudinal analysis.

The combination of complete period metadata, varying content depth across eras, and modern real-time capabilities makes this API uniquely valuable for both historical research and contemporary analysis. As digital preservation efforts continue and data quality improvements are implemented, this historical coverage will only become more valuable for understanding the evolution of Danish democracy.

!!! tip "Getting Started with Historical Analysis"
    Begin your historical research by:
    
    1. **Mapping Periods**: Query the Periode entity to understand temporal boundaries
    2. **Assessing Coverage**: Test data availability for your periods of interest  
    3. **Planning Analysis**: Design research methodology based on data quality patterns
    4. **Validating Results**: Cross-reference findings with known historical events
    
    The API's exceptional historical depth ensures your research contributes to our understanding of democratic development over more than seven decades.