# Historical Coverage Overview

The Danish Parliamentary Open Data API provides unprecedented access to over seven decades of parliamentary data, spanning from 1952 to the present day. This comprehensive historical dataset represents one of the most extensive digitized parliamentary archives available through a modern API interface.

## Temporal Scope and Depth

### Complete Historical Range
The API maintains structured data across **74+ years** of Danish parliamentary history:

- **Starting Point**: October 7, 1952 (Period ID 94)
- **Current Coverage**: Through present day (2025)
- **Forward Planning**: Defined periods extend to 2026
- **Total Periods**: 165+ distinct parliamentary periods

### Parliamentary Period Structure
Historical data is organized around Denmark's parliamentary calendar:

```http
GET /api/Periode?$orderby=startdato asc&$top=5
```

Each period contains:
- Precise start and end dates
- Unique period identifiers
- Parliamentary session metadata  
- Legislative framework context

## Data Availability Patterns

### Metadata vs. Content Distinction
Understanding the API's historical coverage requires distinguishing between two data layers:

#### 1. Period Metadata (Complete)
- **Coverage**: All 165+ periods from 1952-present
- **Quality**: Comprehensive structural data
- **Accessibility**: Fully queryable via API
- **Purpose**: Provides temporal framework for all content

#### 2. Content Data (Variable by Era)
- **Coverage**: Varies by entity type and historical importance
- **Quality**: Improves in more recent periods
- **Accessibility**: Subject to digitization completeness
- **Purpose**: Contains actual parliamentary records and documents

### Historical Data Migration Timeline

The API's `opdateringsdato` (update date) field reveals important migration patterns:

- **API Deployment**: Circa 2014
- **Migration Window**: 2014-2015
- **Update Timestamps**: Reflect system deployment, not original document dates
- **Historical Preservation**: Original dates maintained in entity-specific fields

```http
# Despite 2014+ update timestamps, historical records exist
GET /api/Sag?$filter=periodeid eq 94  # Returns 1952 period data
```

## Coverage Completeness by Era

### Modern Era (2000-Present)
- **Data Completeness**: 95-100%
- **Digital Integration**: Native digital workflows
- **Real-time Updates**: Continuous synchronization
- **Document Quality**: High-resolution PDFs and structured data

### Transition Era (1990-2000)
- **Data Completeness**: 80-95%
- **Digitization Source**: Scanned documents and databases
- **Migration Quality**: Comprehensive OCR processing
- **Document Quality**: Mixed digital and scanned formats

### Historical Era (1952-1990)
- **Data Completeness**: 60-80% (varies by record type)
- **Digitization Source**: Archival documents and microfiche
- **Migration Quality**: Selective digitization of significant records
- **Document Quality**: Primarily scanned historical documents

## Data Quality Evolution

### Temporal Data Quality Characteristics

The API demonstrates evolving data quality patterns across historical periods:

#### **Voting Records (Afstemning)**
- **1952-1970**: Limited electronic records, major votes preserved
- **1970-1990**: Increasing digital capture, systematic recording
- **1990-Present**: Complete electronic voting records

#### **Documents (Dokument)**
- **1952-1980**: Significant documents digitized selectively
- **1980-2000**: Comprehensive scanning initiatives
- **2000-Present**: Born-digital document workflows

#### **Parliamentary Actors (Aktør)**
- **1952-Present**: Complete biographical and role data
- **Quality**: Consistent across all eras due to administrative importance
- **Integration**: Full relationship mapping with cases and votes

## Historical Research Applications

### Legislative Archaeology
The historical dataset enables comprehensive analysis of:

- **Long-term Policy Evolution**: Track legislation across decades
- **Political Party Development**: Analyze changing party positions
- **Institutional Changes**: Study parliamentary procedure evolution
- **Social Progress Indicators**: Measure societal change through legislation

### Temporal Analysis Capabilities

#### Trend Analysis
```http
# Analyze voting patterns over decades
GET /api/Afstemning?$expand=stemme&$filter=year(Sag/periodeid) ge 1960
```

#### Historical Comparison
```http
# Compare party positions across eras  
GET /api/Aktør?$filter=startswith(navn,'Socialdemokratiet') and periodeid le 100
```

#### Longitudinal Studies
```http
# Track individual politicians across multiple periods
GET /api/Aktør?$expand=stemme&$filter=substringof('Hansen',navn)
```

## Digital Preservation Standards

### Archival Integration
The API serves as a bridge between:

- **Danish National Archives**: Primary source material
- **Parliamentary IT Systems**: Modern legislative workflows  
- **Public Access Platforms**: Citizen-facing transparency tools
- **Research Infrastructure**: Academic and journalistic analysis

### Data Integrity Measures
- **Referential Integrity**: Cross-period relationship validation
- **Source Attribution**: Original document references maintained
- **Version Control**: Historical amendments and corrections tracked
- **Audit Trails**: Complete change history for all records

## Best Practices for Historical Analysis

### Temporal Query Strategies

#### 1. Period-Based Filtering
```http
# Focus on specific parliamentary periods
GET /api/Sag?$filter=periodeid ge 120 and periodeid le 130
```

#### 2. Date Range Analysis  
```http
# Use actual document dates, not API update timestamps
GET /api/Dokument?$filter=dato ge datetime'1960-01-01' and dato le datetime'1970-01-01'
```

#### 3. Cross-Reference Validation
```http
# Verify data completeness across related entities
GET /api/Sag?$expand=dokumenter,aktører&$filter=periodeid eq 94
```

### Research Methodology Considerations

#### Data Completeness Assessment
- Always verify record counts for historical periods
- Cross-reference with parliamentary archives when possible
- Account for digitization gaps in older periods
- Use multiple entity types to validate findings

#### Temporal Context Awareness
- Understand changing parliamentary procedures over time
- Account for evolving political party structures
- Consider historical context of data collection methods
- Recognize limitations of retrospective digitization

## Navigation to Detailed Sections

### Deep-Dive Documentation
- **[Parliamentary Periods](periods.md)**: Detailed period-by-period analysis
- **[Data Migration](data-migration.md)**: Technical migration processes and timelines

### Related Analysis Tools
- **[Timeline Analysis Guide](../../guides/advanced-analysis/timeline-analysis.md)**: Temporal analysis methodologies
- **[Historical Data Mining](../../guides/advanced-analysis/data-mining.md)**: Research techniques for historical datasets

### Data Model Context  
- **[Parliamentary Process](../../data-model/parliamentary-process/index.md)**: Understanding institutional evolution
- **[Entity Relationships](../../data-model/entity-relationships.md)**: Cross-temporal data connections

## Research Impact and Applications

The Danish Parliamentary API's historical coverage enables groundbreaking research across multiple disciplines:

### Political Science Applications
- **Comparative Politics**: Cross-national parliamentary studies
- **Electoral Behavior**: Long-term voting pattern analysis  
- **Institutional Development**: Parliamentary procedure evolution
- **Policy Studies**: Legislative lifecycle tracking

### Digital Humanities Research
- **Text Analysis**: Historical document corpus studies
- **Network Analysis**: Political relationship mapping over time
- **Quantitative History**: Statistical analysis of parliamentary behavior
- **Computational Social Science**: Large-scale historical data mining

### Transparency and Accountability
- **Historical Accountability**: Track promises and policy outcomes
- **Institutional Memory**: Preserve parliamentary knowledge
- **Citizen Education**: Accessible historical political education
- **Journalist Resources**: In-depth historical context for reporting

---

The Danish Parliamentary API's 74+ year historical coverage represents a unique global resource for understanding democratic processes, political evolution, and institutional development. This comprehensive temporal dataset, combined with modern API accessibility, opens new possibilities for historical research, transparency initiatives, and democratic engagement.