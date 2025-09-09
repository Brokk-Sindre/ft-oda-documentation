---
title: Sag Entity - Danish Parliament Cases API Reference
description: Complete reference for the Sag (Cases) entity in the Danish Parliament API. Access 96,538+ legislative cases, bills, and proposals with detailed field descriptions and query examples.
keywords: sag entity, danish parliament cases, legislative bills api, parliamentary matters, oda.ft.dk cases, odata cases
---

# Sag (Cases) Entity

The `Sag` entity is the core of the Danish Parliament API, representing legislative cases, bills, proposals, and other parliamentary matters. With **96,538+ records**, it contains the complete history of Danish parliamentary cases.

## Overview

- **Entity Name**: `Sag`
- **Endpoint**: `https://oda.ft.dk/api/Sag`
- **Total Records**: 96,538+ (as of September 2025)
- **Primary Key**: `id` (Int32)
- **Historical Coverage**: 1952-2026 (74+ years)

## Field Reference

### Core Identification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | Int32 | Primary key, unique case identifier | `102903` |
| `titel` | String | Case title | `"Kommissionsmeddelelse om den europøiske grønne pagt"` |
| `titelkort` | String | Short title | `"Grønne pagt"` |
| `nummer` | String | Case number | `"L 123"` |

### Classification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `typeid` | Int32 | Case type ID (foreign key) | `5` |
| `statusid` | Int32 | Current status ID (foreign key) | `11` |
| `kategoriid` | Int32 | Category ID (foreign key) | `19` |
| `offentlighedskode` | String | Publicity code (`"O"` = Open) | `"O"` |

### Temporal Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `opdateringsdato` | DateTime | Last update timestamp | `"2025-09-09T17:49:11.87"` |
| `periodeid` | Int32 | Parliamentary period ID | `32` |
| `afgørelsesdato` | DateTime | Decision date | `"2025-09-09T10:30:00"` |
| `lovnummerdato` | DateTime | Law number date | `"2025-09-09T10:30:00"` |
| `rådsmødedato` | DateTime | Council meeting date | `"2025-09-09T14:00:00"` |

### Content Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `resume` | String | Case summary | `"Forslag til..."` |
| `afgørelse` | String | Decision text | `"Vedtaget"` |
| `afgørelsesresultatkode` | String | Decision result code | `"V"` |
| `afstemningskonklusion` | String | Voting conclusion | `"Forslaget vedtages"` |
| `baggrundsmateriale` | String | Background material | `"Se bilag"` |
| `begrundelse` | String | Justification | `"Jøvnfør..."` |

### Legal References

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `lovnummer` | String | Law number if enacted | `"LOV nr 123"` |
| `paragraf` | String | Paragraph reference | `"ø 15, stk. 2"` |
| `paragrafnummer` | Int32 | Paragraph number | `15` |
| `retsinformationsurl` | String | Legal information URL | `"https://retsinformation.dk/..."` |

### Relationship Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `fremsatundersagid` | Int32 | Parent case ID if sub-case | `102900` |
| `deltundersagid` | Int32 | Sub-case ID reference | `102905` |

### Special Classifications

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `statsbudgetsag` | Boolean | State budget case flag | `true` |

### Number Parsing Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `nummernumerisk` | String | Numeric part of number | `"123"` |
| `nummerprefix` | String | Number prefix | `"L"` |
| `nummerpostfix` | String | Number postfix | `"A"` |

## Common Query Examples

### Basic Queries

```bash
# Get latest 5 cases
curl "https://oda.ft.dk/api/Sag?%24top=5&%24orderby=opdateringsdato%20desc"

# Get specific case by ID
curl "https://oda.ft.dk/api/Sag(102903)"

# Count total cases
curl "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1"
```

### Filter Queries

```bash
# Open/public cases only
curl "https://oda.ft.dk/api/Sag?%24filter=offentlighedskode%20eq%20'O'&%24top=10"

# Cases updated in 2025
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025&%24top=10"

# Budget-related cases
curl "https://oda.ft.dk/api/Sag?%24filter=statsbudgetsag%20eq%20true&%24top=10"

# Climate-related legislation
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)&%24top=10"
```

### Advanced Filtering

```bash
# Complex boolean logic
curl "https://oda.ft.dk/api/Sag?%24filter=%28substringof('klima',titel)%20or%20substringof('miljø',titel)%29%20and%20year(opdateringsdato)%20gt%202020&%24top=10"

# Cases from specific period
curl "https://oda.ft.dk/api/Sag?%24filter=periodeid%20eq%2032&%24top=10"

# Recent decisions
curl "https://oda.ft.dk/api/Sag?%24filter=afgørelsesdato%20gt%20datetime'2025-09-01T00:00:00'&%24top=10"
```

### Field Selection

```bash
# Only essential fields
curl "https://oda.ft.dk/api/Sag?%24select=id,titel,opdateringsdato,statusid&%24top=10"

# Title and classification
curl "https://oda.ft.dk/api/Sag?%24select=titel,offentlighedskode,typeid,statusid&%24top=10"
```

## Relationship Expansion

### Core Relationships

```bash
# Case with category
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=3"

# Case with type and status
curl "https://oda.ft.dk/api/Sag?%24expand=Sagstype,Sagsstatus&%24top=3"

# Case with period information
curl "https://oda.ft.dk/api/Sag?%24expand=Periode&%24top=3"
```

### Actor Relationships

```bash
# Cases with involved actors
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør&%24top=3"

# Cases with actor roles
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør,SagAktør/SagAktørRolle&%24top=3"
```

### Document Relationships

```bash
# Cases with documents
curl "https://oda.ft.dk/api/Sag?%24expand=SagDokument/Dokument&%24top=3"

# Cases with case steps
curl "https://oda.ft.dk/api/Sag?%24expand=Sagstrin&%24top=3"
```

## Data Analysis Examples

### Recent Activity Monitoring

```bash
# Today's updates
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-09-09T00:00:00'&%24orderby=opdateringsdato%20desc"

# This week's new cases
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-09-02T00:00:00'&%24orderby=opdateringsdato%20desc"
```

### Legislative Tracking

```bash
# Track specific legislation through process
curl "https://oda.ft.dk/api/Sag?%24expand=Sagstrin,Sagsstatus&%24filter=substringof('digital',titel)&%24top=5"

# Find related/sub cases
curl "https://oda.ft.dk/api/Sag?%24filter=fremsatundersagid%20eq%20102900"
```

### Historical Analysis

```bash
# Cases by year
curl "https://oda.ft.dk/api/Sag?%24filter=year(afgørelsesdato)%20eq%202024&%24inlinecount=allpages&%24top=1"

# Long-running cases (updated multiple times)
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025&%24orderby=opdateringsdato%20desc&%24top=20"
```

## Performance Optimization

### Use Field Selection

```bash
# Good: Only request needed fields
curl "https://oda.ft.dk/api/Sag?%24select=id,titel,opdateringsdato&%24top=100"

# Avoid: Requesting all fields unnecessarily
curl "https://oda.ft.dk/api/Sag?%24top=100"  # Downloads ~25+ fields per record
```

### Efficient Pagination

```bash
# Paginate through large result sets
curl "https://oda.ft.dk/api/Sag?%24skip=0&%24top=100"
curl "https://oda.ft.dk/api/Sag?%24skip=100&%24top=100"
curl "https://oda.ft.dk/api/Sag?%24skip=200&%24top=100"
```

### Smart Filtering

```bash
# Filter before expanding to reduce data
curl "https://oda.ft.dk/api/Sag?%24filter=offentlighedskode%20eq%20'O'&%24expand=SagAktør&%24top=10"
```

## Common Use Cases

### 1. Legislative Monitoring Dashboard

```python
def get_recent_legislation():
    """Get cases updated in last 24 hours"""
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    filter_query = f"opdateringsdato gt datetime'{yesterday}'"
    return get_cases(filter_query=filter_query, select="id,titel,opdateringsdato,statusid")
```

### 2. Climate Policy Tracker

```python
def track_climate_policy():
    """Track all climate-related legislation"""
    filter_query = "(substringof('klima',titel) or substringof('miljø',titel) or substringof('grøn',titel))"
    return get_cases(filter_query=filter_query, expand="Sagsstatus,Sagstype", top=50)
```

### 3. Budget Analysis

```python
def analyze_budget_cases():
    """Get all state budget cases with their status"""
    filter_query = "statsbudgetsag eq true"
    return get_cases(filter_query=filter_query, expand="Sagsstatus", orderby="opdateringsdato desc")
```

## Important Notes

### Data Freshness
- **Real-time Updates**: Cases are updated within hours of parliamentary activity
- **Latest Example**: 2025-09-09T17:49:11.87 (EU Commission communication)
- **Daily Volume**: 50+ cases updated daily on average

### Pagination Limits
- **Maximum Records**: 100 per request (hard limit, updated from previous 1000)
- **Recommended**: Use pagination for large datasets
- **Total Records**: Use `$inlinecount=allpages` to get total count

### Silent Filter Failures
ø **Critical Warning**: Invalid filter field names return ALL data instead of errors!

```bash
# L Dangerous: Typo returns all 96,538+ records
curl "https://oda.ft.dk/api/Sag?%24filter=tittel%20eq%20'test'"  # 'tittel' should be 'titel'

#  Safe: Always test filters with $top=1 first
curl "https://oda.ft.dk/api/Sag?%24filter=titel%20eq%20'test'&%24top=1"
```

### Related Entities

The `Sag` entity connects to many other entities:

- **Sagskategori** - Case categories
- **Sagstype** - Case types (13 different types)
- **Sagsstatus** - Case statuses (68 different statuses)
- **SagAktør** - Case-actor relationships (23 role types)
- **SagDokument** - Case-document relationships
- **Sagstrin** - Case steps/stages
- **Periode** - Parliamentary periods
- **Afstemning** - Related voting sessions

This makes `Sag` the central hub for exploring Danish parliamentary data.