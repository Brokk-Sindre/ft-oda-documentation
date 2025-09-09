# OData Overview & Capabilities

The Danish Parliament API uses **OData 3.0** (Open Data Protocol) to provide powerful querying capabilities over parliamentary data. This comprehensive guide covers all supported operations, limitations, and best practices.

## OData 3.0 Compliance

The API implements a robust subset of OData 3.0 with excellent performance and reliability:

- **✅ Full OData 3.0 Support**: Complete implementation of core OData operations
- **L No OData 4.0 Features**: Advanced OData 4.0 functions not available
- **ø High Performance**: Response times from 85ms to 2 seconds
- **=ø Large Scale**: Handles 96,538+ cases, 18,139+ actors seamlessly

## Supported OData Parameters

### Core Query Parameters

| Parameter | Purpose | Support Level | Max Limit |
|-----------|---------|---------------|-----------|
| `$top` | Limit number of records | ✅ Full | 100 records |
| `$skip` | Skip records for pagination | ✅ Full | No limit |
| `$filter` | Filter records by conditions | ✅ Full | Complex expressions |
| `$expand` | Include related data | ✅ Full | 2-3 levels deep |
| `$select` | Choose specific fields | ✅ Full | All fields |
| `$orderby` | Sort results | ✅ Full | Multiple fields |
| `$inlinecount` | Include total count | ✅ Full | Allpages only |
| `$format` | Response format | ✅ Full | JSON/XML |

### Advanced Filter Functions

| Function | Purpose | Example | Support |
|----------|---------|---------|---------|
| `substringof()` | Text search | `substringof('klima', titel)` | ✅ Full |
| `startswith()` | Text prefix | `startswith(titel, 'Forslag')` | ✅ Full |
| `endswith()` | Text suffix | `endswith(titel, 'lov')` | ✅ Full |
| `year()` | Extract year | `year(opdateringsdato) eq 2025` | ✅ Full |
| `month()` | Extract month | `month(opdateringsdato) eq 9` | ✅ Full |
| `day()` | Extract day | `day(opdateringsdato) eq 9` | ✅ Full |

## Unsupported OData Features

The following OData 4.0+ features are **not supported**:

- **L `$search`** - Use `$filter` with `substringof()` instead
- **L `$batch`** - No batch operations (returns HTTP 501)
- **L `$compute`** - No computed fields
- **L `$apply`** - No aggregation operations
- **L `$count`** - Use `$inlinecount=allpages` instead
- **L Lambda operators** - No `$any` or `$all` operations

## Critical URL Encoding Requirement

!!! danger "Most Common Developer Mistake"
    **Always use `%24` instead of `$` in OData parameters**. This is the #1 error developers make.
    
    **L Wrong:**
    ```
    https://oda.ft.dk/api/Sag?$top=5
    ```
    
    **✅ Correct:**
    ```
    https://oda.ft.dk/api/Sag?%24top=5
    ```

### Why URL Encoding is Required

The API server requires proper URL encoding of special characters:

- `$` must become `%24`
- Spaces must become `%20`
- Single quotes must become `%27`
- Parentheses need encoding in complex expressions

## Basic Query Examples

### Simple Record Retrieval
```bash
# Get 5 recent parliamentary cases
curl "https://oda.ft.dk/api/Sag?%24top=5"
```

### Filtering by Status
```bash
# Get public cases only
curl "https://oda.ft.dk/api/Sag?%24filter=offentlighedskode%20eq%20'O'&%24top=10"
```

### Text Search
```bash
# Find climate-related legislation
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)"
```

### Date Filtering
```bash
# Cases updated in 2025
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025&%24top=10"
```

### Including Related Data
```bash
# Cases with category information
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=3"
```

## Error Handling Patterns

### HTTP Response Codes

| Code | Meaning | Cause | Response Body |
|------|---------|-------|---------------|
| 200 | Success | Valid request | JSON data |
| 400 | Bad Request | Invalid OData syntax | Empty (0 bytes) |
| 404 | Not Found | Invalid entity name | HTML error page |
| 501 | Not Implemented | Write operations | JSON error message |

### Silent Filter Failures

!!! warning "Critical Behavior"
    **Invalid filter field names are silently ignored** - they return the complete unfiltered dataset instead of an error.
    
    ```bash
    # This returns ALL records (not an error!)
    curl "https://oda.ft.dk/api/Sag?%24filter=invalid_field%20eq%20'test'"
    ```

## Performance Characteristics

### Response Times (Tested)

- **Small queries** (`$top=5`): ~85ms average
- **Medium queries** (`$top=100`): ~90ms average  
- **Complex expansion** (`$expand=Stemme/Aktør`): ~1.8s
- **Large datasets** (`$top=10000`): ~2s (capped at 100 records)

### Pagination Performance

```bash
# Efficient large dataset access
curl "https://oda.ft.dk/api/Sag?%24skip=10000&%24top=100"  # ~90ms
```

No significant performance penalty for large `$skip` values - pagination is highly efficient.

## Interactive Query Builder

Try building OData queries interactively:

<div class="query-builder"></div>

## Best Practices

### 1. Always Use URL Encoding
```bash
# Correct approach
curl "https://oda.ft.dk/api/Sag?%24top=100&%24skip=200"
```

### 2. Validate Filter Fields
```bash
# Test with small $top first to catch silent failures
curl "https://oda.ft.dk/api/Sag?%24filter=your_filter_here&%24top=1"
```

### 3. Use Pagination for Large Datasets
```bash
# Efficient pattern for accessing all data
for skip in 0 100 200 300; do
    curl "https://oda.ft.dk/api/Sag?%24skip=$skip&%24top=100"
done
```

### 4. Strategic Relationship Expansion
```bash
# Minimize API calls with targeted expansion
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori,Sagstrin&%24top=50"
```

### 5. Monitor Result Sizes
```python
# Python: Detect silent filter failures
response = requests.get(url)
data = response.json()
if len(data['value']) == 100 and '$top=100' not in url:
    print("Warning: Filter may have been ignored")
```

## Entity-Specific Considerations

### Large Entities (Require Pagination)
- **Sag** (Cases): 96,538+ records
- **Aktør** (Actors): 18,139+ records  
- **Stemme** (Votes): Millions of records
- **Dokument** (Documents): Large dataset

### Junction Tables (Relationship-Heavy)
- **SagAktør**: Case-Actor relationships (23 role types)
- **DokumentAktør**: Document-Actor relationships (25 role types)
- **SagDokument**: Case-Document relationships

## OData Metadata

Access complete schema information:
```bash
# Get full OData metadata
curl "https://oda.ft.dk/api/\$metadata"
```

The metadata document provides:
- Complete entity definitions
- Relationship mappings  
- Field types and constraints
- Navigation properties

## Next Steps

1. **[Filters](filters.md)** - Master filtering with Danish text examples
2. **[Pagination](pagination.md)** - Handle the 100 record limit effectively  
3. **[Expansion](expansion.md)** - Use relationship expansion strategically
4. **[Performance](../performance/)** - Optimize queries for production use

## Quick Reference

### Essential URL Encoding
```
$ ø %24    (space) ø %20    ' ø %27    ( ø %28    ) ø %29
```

### Common Query Patterns
```bash
# Pagination
?%24skip=200&%24top=100

# Filter + Expand
?%24filter=offentlighedskode%20eq%20'O'&%24expand=Sagskategori

# Date range
?%24filter=opdateringsdato%20gt%20datetime'2025-01-01T00:00:00'

# Text search
?%24filter=substringof('klima',titel)
```

The Danish Parliament API's OData implementation provides powerful, reliable access to comprehensive parliamentary data when used correctly. Master these fundamentals and you'll have efficient access to 74+ years of Danish democratic transparency.