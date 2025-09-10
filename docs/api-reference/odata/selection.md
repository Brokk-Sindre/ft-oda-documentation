# Field Selection Documentation

The Danish Parliament API's `$select` parameter enables you to specify exactly which fields to retrieve, dramatically reducing response size and improving performance. This guide covers all selection patterns, performance optimization, and practical examples with parliamentary data.

## $select Syntax Overview

The `$select` parameter follows **OData 3.0 field selection syntax**:

### Basic Selection Patterns

| Pattern | Purpose | Example |
|---------|---------|---------|
| Single field | Retrieve only one field | `$select=titel` |
| Multiple fields | Retrieve specific fields | `$select=titel,offentlighedskode` |
| Related fields | Fields from expanded entities | `$select=titel,Sagskategori/kategori` |
| Complex selection | Multiple entities with specific fields | `$select=titel,Aktør/navn,Dokument/titel` |

!!! warning "URL Encoding Required"
    Always use `%24select` instead of `$select` in URLs:
    ```
     Correct: ?%24select=titel,offentlighedskode
    L Wrong: ?$select=titel,offentlighedskode
    ```

## Single Field Selection

### Core Field Selection

#### Sag (Cases) Field Selection
```bash
# Only case titles
curl "https://oda.ft.dk/api/Sag?%24select=titel&%24top=5"

# Only public visibility codes
curl "https://oda.ft.dk/api/Sag?%24select=offentlighedskode&%24top=5"

# Only update dates
curl "https://oda.ft.dk/api/Sag?%24select=opdateringsdato&%24top=5"

# Only case IDs
curl "https://oda.ft.dk/api/Sag?%24select=id&%24top=5"
```

#### Aktør (Actors) Field Selection
```bash
# Only actor names
curl "https://oda.ft.dk/api/Aktør?%24select=navn&%24top=5"

# Only update dates
curl "https://oda.ft.dk/api/Aktør?%24select=opdateringsdato&%24top=5"

# Only IDs and names
curl "https://oda.ft.dk/api/Aktør?%24select=id,navn&%24top=5"
```

#### Dokument (Documents) Field Selection
```bash
# Only document titles
curl "https://oda.ft.dk/api/Dokument?%24select=titel&%24top=5"

# Document type and date
curl "https://oda.ft.dk/api/Dokument?%24select=dokumenttypeid,dato&%24top=5"
```

## Multiple Field Selection

### Essential Field Combinations

#### Sag (Cases) Essential Fields
```bash
# Title and status - minimal case overview
curl "https://oda.ft.dk/api/Sag?%24select=titel,offentlighedskode&%24top=5"

# Legislative tracking essentials
curl "https://oda.ft.dk/api/Sag?%24select=titel,opdateringsdato,periodeid&%24top=5"

# Case identification bundle
curl "https://oda.ft.dk/api/Sag?%24select=id,titel,nummer,nummerprefix&%24top=5"

# Status monitoring fields
curl "https://oda.ft.dk/api/Sag?%24select=titel,sagsstatus,opdateringsdato&%24top=5"
```

#### Aktør (Actors) Essential Fields
```bash
# Basic politician information
curl "https://oda.ft.dk/api/Aktør?%24select=navn,fornavn,efternavn&%24top=5"

# Actor classification
curl "https://oda.ft.dk/api/Aktør?%24select=navn,typeid,opdateringsdato&%24top=5"

# Full name context
curl "https://oda.ft.dk/api/Aktør?%24select=id,navn,gruppenavnkort&%24top=5"
```

#### Stemme (Votes) Essential Fields
```bash
# Vote analysis basics
curl "https://oda.ft.dk/api/Stemme?%24select=typeid,aktoeid,afstemningid&%24top=10"

# Vote tracking with dates
curl "https://oda.ft.dk/api/Stemme?%24select=typeid,aktoeid,opdateringsdato&%24top=10"
```

## Related Field Selection (with $expand)

### Combining $select with $expand

When using `$expand`, you can select specific fields from both the main entity and related entities:

#### Cases with Category Information
```bash
# Case title with category name
curl "https://oda.ft.dk/api/Sag?%24select=titel,Sagskategori/kategori&%24expand=Sagskategori&%24top=5"

# Case essentials with category and status
curl "https://oda.ft.dk/api/Sag?%24select=titel,opdateringsdato,Sagskategori/kategori,Sagsstatus/status&%24expand=Sagskategori,Sagsstatus&%24top=5"

# Minimal case with period information
curl "https://oda.ft.dk/api/Sag?%24select=titel,Periode/kode,Periode/titel&%24expand=Periode&%24top=5"
```

#### Actors with Type Information
```bash
# Actor name with type
curl "https://oda.ft.dk/api/Aktør?%24select=navn,Aktørtype/type&%24expand=Aktørtype&%24top=5"

# Full actor context
curl "https://oda.ft.dk/api/Aktør?%24select=navn,fornavn,efternavn,Aktørtype/type,Aktørtype/gruppe&%24expand=Aktørtype&%24top=5"
```

#### Votes with Actor and Voting Information
```bash
# Vote with actor name and vote type
curl "https://oda.ft.dk/api/Stemme?%24select=Aktør/navn,Stemmetype/type&%24expand=Aktør,Stemmetype&%24top=10"

# Complete vote analysis data
curl "https://oda.ft.dk/api/Stemme?%24select=Aktør/navn,Stemmetype/type,Afstemning/titel&%24expand=Aktør,Stemmetype,Afstemning&%24top=10"
```

## Performance Benefits of Field Selection

### Response Size Comparison

#### Full Response (No Selection)
```bash
# Full Sag entity (all 25+ fields)
curl "https://oda.ft.dk/api/Sag?%24top=1"
# Response size: ~800 bytes per record
```

#### Selective Response
```bash
# Only title and status (2 fields)
curl "https://oda.ft.dk/api/Sag?%24select=titel,offentlighedskode&%24top=1"
# Response size: ~150 bytes per record (80% reduction)
```

### Performance Optimization Examples

#### Efficient Legislative Tracking
```bash
# Minimal data for case monitoring
curl "https://oda.ft.dk/api/Sag?%24select=id,titel,opdateringsdato&%24filter=year(opdateringsdato)%20eq%202025&%24top=50"
```

#### Efficient Actor Lookup
```bash
# Quick politician search
curl "https://oda.ft.dk/api/Aktør?%24select=id,navn&%24filter=substringof('jensen',navn)&%24top=20"
```

#### Efficient Vote Analysis
```bash
# Essential voting data only
curl "https://oda.ft.dk/api/Stemme?%24select=aktoeid,typeid,afstemningid&%24filter=typeid%20eq%201&%24top=100"
```

## Complex Selection Patterns

### Multi-Entity Field Selection

#### Parliamentary Committee Analysis
```bash
# Committee cases with essential actor information
curl "https://oda.ft.dk/api/SagAktør?%24select=Sag/titel,Aktør/navn,Aktør/gruppenavnkort&%24expand=Sag,Aktør&%24filter=substringof('udvalg',Aktør/navn)&%24top=10"
```

#### Document Flow Tracking
```bash
# Document-actor relationships with minimal data
curl "https://oda.ft.dk/api/DokumentAktør?%24select=Dokument/titel,Aktør/navn,rolleid&%24expand=Dokument,Aktør&%24top=10"
```

#### Legislative Timeline Data
```bash
# Cases with step information
curl "https://oda.ft.dk/api/Sag?%24select=titel,Sagstrin/titel,Sagstrin/dato&%24expand=Sagstrin&%24filter=year(opdateringsdato)%20eq%202025&%24top=10"
```

## Danish Parliamentary Entity Field Guide

### Sag (Cases) - Most Useful Fields

| Field | Purpose | Selection Example |
|-------|---------|-------------------|
| `id` | Unique identifier | `%24select=id` |
| `titel` | Case title (Danish) | `%24select=titel` |
| `offentlighedskode` | Public/private status | `%24select=offentlighedskode` |
| `opdateringsdato` | Last update date | `%24select=opdateringsdato` |
| `nummer` | Case number | `%24select=nummer` |
| `nummerprefix` | Case number prefix | `%24select=nummerprefix` |
| `periodeid` | Parliamentary period | `%24select=periodeid` |
| `sagsstatus` | Current status | `%24select=sagsstatus` |

### Aktør (Actors) - Most Useful Fields

| Field | Purpose | Selection Example |
|-------|---------|-------------------|
| `id` | Unique identifier | `%24select=id` |
| `navn` | Full name | `%24select=navn` |
| `fornavn` | First name | `%24select=fornavn` |
| `efternavn` | Last name | `%24select=efternavn` |
| `gruppenavnkort` | Party abbreviation | `%24select=gruppenavnkort` |
| `typeid` | Actor type ID | `%24select=typeid` |
| `opdateringsdato` | Last update | `%24select=opdateringsdato` |

### Stemme (Votes) - Most Useful Fields

| Field | Purpose | Selection Example |
|-------|---------|-------------------|
| `id` | Unique vote ID | `%24select=id` |
| `typeid` | Vote type (1=Yes, 2=No, etc.) | `%24select=typeid` |
| `aktoeid` | Actor ID who voted | `%24select=aktoeid` |
| `afstemningid` | Voting session ID | `%24select=afstemningid` |
| `opdateringsdato` | Vote timestamp | `%24select=opdateringsdato` |

## Selection with Filtering

### Optimized Query Patterns

#### Recent Public Legislation - Essentials Only
```bash
# Title and status of recent public cases
curl "https://oda.ft.dk/api/Sag?%24select=titel,offentlighedskode,opdateringsdato&%24filter=offentlighedskode%20eq%20'O'%20and%20year(opdateringsdato)%20eq%202025&%24top=20"
```

#### Climate Legislation Tracking
```bash
# Climate-related cases with minimal data
curl "https://oda.ft.dk/api/Sag?%24select=titel,nummer,opdateringsdato&%24filter=substringof('klima',titel)&%24top=15"
```

#### Active Politicians List
```bash
# Current MP names only
curl "https://oda.ft.dk/api/Aktør?%24select=navn,gruppenavnkort&%24filter=Aktørtype/type%20eq%20'person'%20and%20substringof('MF',navn)&%24expand=Aktørtype&%24top=20"
```

## Common Selection Mistakes

### Silent Field Name Errors

!!! danger "Invalid Field Names Return Full Data"
    **Invalid field names in `$select` are silently ignored** and return complete entities:
    
    ```bash
    # This returns ALL fields (not an error!)
    curl "https://oda.ft.dk/api/Sag?%24select=invalid_field,titel&%24top=1"
    ```

### How to Validate Field Selection

1. **Test with known good fields first**:
```bash
# Start with confirmed working fields
curl "https://oda.ft.dk/api/Sag?%24select=id&%24top=1"
```

2. **Add fields incrementally**:
```bash
# Add one field at a time to identify problems
curl "https://oda.ft.dk/api/Sag?%24select=id,titel&%24top=1"
curl "https://oda.ft.dk/api/Sag?%24select=id,titel,opdateringsdato&%24top=1"
```

3. **Check response size**:
```python
# Python: Monitor response sizes
import requests
response = requests.get("https://oda.ft.dk/api/Sag?%24select=titel&%24top=1")
data = response.json()
print(f"Fields returned: {len(data['value'][0].keys())}")  # Should be 1 for single field
```

4. **Validate against metadata**:
```bash
# Get valid field names
curl "https://oda.ft.dk/api/\$metadata" | grep -A 10 'EntityType Name="Sag"'
```

### Expansion Selection Mistakes

!!! warning "Related Field Selection Requires $expand"
    **Related entity fields require `$expand` to be included**:
    
    ```bash
    # This fails - no $expand
    curl "https://oda.ft.dk/api/Sag?%24select=titel,Sagskategori/kategori&%24top=1"
    
    # This works - includes $expand
    curl "https://oda.ft.dk/api/Sag?%24select=titel,Sagskategori/kategori&%24expand=Sagskategori&%24top=1"
    ```

## Best Practices for Field Selection

### Performance Optimization

1. **Select Only Needed Fields**:
```bash
# Good: Minimal data for display
curl "https://oda.ft.dk/api/Sag?%24select=titel,opdateringsdato&%24top=50"

# Avoid: All fields when not needed
curl "https://oda.ft.dk/api/Sag?%24top=50"  # Returns all 25+ fields
```

2. **Combine Selection with Filtering**:
```bash
# Efficient: Filter first, select specific fields
curl "https://oda.ft.dk/api/Sag?%24select=titel,nummer&%24filter=year(opdateringsdato)%20eq%202025&%24top=20"
```

3. **Use Selection for Large Datasets**:
```bash
# Essential for large exports
curl "https://oda.ft.dk/api/Stemme?%24select=aktoeid,typeid,afstemningid&%24top=1000"
```

### Memory Efficiency

#### Browser Applications
```javascript
// JavaScript: Select only fields for display
const url = "https://oda.ft.dk/api/Sag?%24select=titel,opdateringsdato&%24top=100";
fetch(url)
  .then(response => response.json())
  .then(data => {
    // Smaller payloads = faster loading
    displayCases(data.value);
  });
```

#### Data Analysis Scripts
```python
# Python: Minimize memory usage
import requests
import pandas as pd

# Only fields needed for analysis
url = "https://oda.ft.dk/api/Stemme?%24select=typeid,aktoeid&%24top=5000"
response = requests.get(url)
df = pd.DataFrame(response.json()['value'])
# Smaller DataFrame = less memory
```

## Entity-Specific Selection Guides

### Sag (Cases) Selection Strategies

#### Legislative Monitoring
```bash
# Track case progress
curl "https://oda.ft.dk/api/Sag?%24select=titel,sagsstatus,opdateringsdato&%24top=50"
```

#### Public Records Requests
```bash
# Public case information only
curl "https://oda.ft.dk/api/Sag?%24select=titel,nummer,nummerprefix,offentlighedskode&%24filter=offentlighedskode%20eq%20'O'&%24top=100"
```

#### Search Results Display
```bash
# User-friendly case listing
curl "https://oda.ft.dk/api/Sag?%24select=titel,Periode/titel,Sagskategori/kategori&%24expand=Periode,Sagskategori&%24top=20"
```

### Aktør (Actors) Selection Strategies

#### Politician Directory
```bash
# Basic politician information
curl "https://oda.ft.dk/api/Aktør?%24select=navn,gruppenavnkort,Aktørtype/type&%24expand=Aktørtype&%24filter=Aktørtype/type%20eq%20'person'&%24top=50"
```

#### Committee Membership
```bash
# Committee information
curl "https://oda.ft.dk/api/Aktør?%24select=navn,Aktørtype/gruppe&%24expand=Aktørtype&%24filter=substringof('udvalg',navn)&%24top=30"
```

### Stemme (Votes) Selection Strategies

#### Vote Analysis
```bash
# Essential voting data
curl "https://oda.ft.dk/api/Stemme?%24select=typeid,Aktør/navn,Aktør/gruppenavnkort&%24expand=Aktør&%24top=100"
```

#### Politician Voting Record
```bash
# Specific politician's votes
curl "https://oda.ft.dk/api/Stemme?%24select=typeid,Afstemning/titel,opdateringsdato&%24expand=Afstemning&%24filter=Aktør/navn%20eq%20'Frank%20Aaen'&%24top=50"
```

## Advanced Selection Patterns

### Nested Entity Selection

#### Multi-Level Relationships
```bash
# Votes with full context (3-level expansion)
curl "https://oda.ft.dk/api/Stemme?%24select=Aktør/navn,Stemmetype/type,Afstemning/titel,Afstemning/Sag/titel&%24expand=Aktør,Stemmetype,Afstemning/Sag&%24top=10"
```

#### Junction Table Optimization
```bash
# Document-Actor relationships with minimal data
curl "https://oda.ft.dk/api/DokumentAktør?%24select=Dokument/titel,Aktør/navn,rolleid&%24expand=Dokument,Aktør&%24top=20"
```

### Dynamic Field Selection

#### Conditional Field Selection
```bash
# Different fields based on entity type
curl "https://oda.ft.dk/api/Aktør?%24select=navn,gruppenavnkort&%24filter=Aktørtype/type%20eq%20'person'&%24expand=Aktørtype&%24top=20"

# Versus committees (different fields needed)
curl "https://oda.ft.dk/api/Aktør?%24select=navn,Aktørtype/gruppe&%24filter=substringof('udvalg',navn)&%24expand=Aktørtype&%24top=20"
```

## Field Selection Reference

### Core Entity Fields Summary

#### Essential Fields by Use Case

| Use Case | Entity | Fields | Selection String |
|----------|--------|--------|-----------------|
| Case List | Sag | Title, Status, Date | `titel,offentlighedskode,opdateringsdato` |
| Politician List | Aktør | Name, Party | `navn,gruppenavnkort` |
| Vote Analysis | Stemme | Vote Type, Actor, Voting | `typeid,aktoeid,afstemningid` |
| Document Search | Dokument | Title, Type, Date | `titel,dokumenttypeid,dato` |
| Committee Work | SagAktør | Case, Actor, Role | `Sag/titel,Aktør/navn,rolleid` |

### Performance Impact Examples

| Selection Type | Response Size | Use Case |
|-----------------|---------------|----------|
| Single field (`id`) | ~50 bytes | ID lookups |
| Essential 3 fields | ~200 bytes | List displays |
| Full entity | ~800 bytes | Detail views |
| With relationships | ~1200 bytes | Complete analysis |

## Summary

The `$select` parameter is essential for building efficient applications with the Danish Parliament API:

1. **Always URL encode**: Use `%24select` instead of `$select`
2. **Select only needed fields** to reduce bandwidth and improve performance
3. **Combine with `$expand`** for related entity field selection
4. **Validate field names** to avoid silent failures
5. **Test incrementally** when building complex selections
6. **Use entity-specific patterns** for common use cases
7. **Monitor response sizes** to ensure optimization is working

Mastering field selection will make your parliamentary data applications faster, more efficient, and more responsive to users while minimizing API load.