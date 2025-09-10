# OData Ordering & Sorting

The Danish Parliament API's `$orderby` parameter provides powerful sorting capabilities across all entities. This guide covers single-field sorting, multi-field ordering, performance considerations, and practical examples with Danish parliamentary data.

## Ordering Syntax Overview

The API uses **OData 3.0 ordering syntax** with support for:

- ** Single-field sorting**: Sort by one field ascending or descending
- ** Multi-field sorting**: Sort by multiple fields with individual direction control
- ** Related entity sorting**: Sort by fields from expanded entities
- ** Date/time sorting**: Efficient temporal ordering with `opdateringsdato`
- ** String sorting**: Alphabetical ordering with Danish character support
- ** Numeric sorting**: Integer and ID-based sorting

## Basic Sorting Syntax

### Single Field Sorting

Sort by a single field with optional direction (default is ascending):

```bash
# Sort cases by ID (ascending - default)
curl "https://oda.ft.dk/api/Sag?%24orderby=id&%24top=5"

# Sort cases by ID (descending - explicit)
curl "https://oda.ft.dk/api/Sag?%24orderby=id%20desc&%24top=5"

# Sort cases by ID (ascending - explicit)
curl "https://oda.ft.dk/api/Sag?%24orderby=id%20asc&%24top=5"
```

### Direction Keywords

| Direction | Keyword | Description |
|-----------|---------|-------------|
| Ascending | `asc` | A-Z, 0-9, oldest first (default) |
| Descending | `desc` | Z-A, 9-0, newest first |

## Multi-Field Sorting

Sort by multiple fields with individual direction control:

```bash
# Sort by update date (newest first), then by ID (ascending)
curl "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc,id%20asc&%24top=5"

# Sort by case type, then by title alphabetically
curl "https://oda.ft.dk/api/Sag?%24orderby=typeid,titel&%24top=5"

# Sort by multiple criteria with mixed directions
curl "https://oda.ft.dk/api/Aktør?%24orderby=typeid%20asc,navn%20asc,id%20desc&%24top=5"
```

**Important**: Use comma separation between sort fields, and encode commas as `%2C` if needed in some HTTP clients.

## Common Sorting Patterns

### Date-Based Sorting

Sort by temporal fields - most common for tracking recent activity:

```bash
# Most recently updated cases
curl "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc&%24top=10"

# Oldest cases by update date
curl "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20asc&%24top=10"

# Most recent parliamentary meetings
curl "https://oda.ft.dk/api/Møde?%24orderby=opdateringsdato%20desc&%24top=5"

# Recent voting activity
curl "https://oda.ft.dk/api/Afstemning?%24orderby=opdateringsdato%20desc&%24top=5"
```

### ID-Based Sorting

Sort by entity IDs for consistent ordering and finding newest/oldest records:

```bash
# Highest case ID (newest case number)
curl "https://oda.ft.dk/api/Sag?%24orderby=id%20desc&%24top=3"

# Lowest case ID (oldest case number)
curl "https://oda.ft.dk/api/Sag?%24orderby=id%20asc&%24top=3"

# Recent actor registrations
curl "https://oda.ft.dk/api/Aktør?%24orderby=id%20desc&%24top=5"
```

### Alphabetical Sorting

Sort text fields alphabetically with Danish character support (æ, ø, å):

```bash
# Politicians sorted alphabetically by name
curl "https://oda.ft.dk/api/Aktør?%24orderby=navn&%24top=10"

# Cases sorted by title
curl "https://oda.ft.dk/api/Sag?%24orderby=titel&%24top=5"

# Reverse alphabetical order
curl "https://oda.ft.dk/api/Aktør?%24orderby=navn%20desc&%24top=10"
```

## Sorting with Filters and Selection

Combine ordering with other OData parameters:

```bash
# Recent EU-related legislation sorted by update date
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('eu',titel)&%24orderby=opdateringsdato%20desc&%24select=id,titel,opdateringsdato&%24top=5"

# 2025 cases sorted by title, showing only title and date
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025&%24orderby=titel&%24select=titel,opdateringsdato&%24top=10"

# Politicians from a specific party sorted by name
curl "https://oda.ft.dk/api/Aktør?%24filter=gruppeid%20eq%205&%24orderby=navn&%24top=20"
```

## Sorting with Expanded Entities

Sort by fields from related entities using `$expand`:

```bash
# Cases with their type information, sorted by type name
curl "https://oda.ft.dk/api/Sag?%24expand=Sagtype&%24orderby=Sagtype/type&%24top=5"

# Actors with their group, sorted by group name then actor name
curl "https://oda.ft.dk/api/Aktør?%24expand=Aktørgruppe&%24orderby=Aktørgruppe/gruppenavn,navn&%24top=10"

# Votes with voter information, sorted by actor name
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktør&%24orderby=Aktør/navn&%24top=20"
```

## URL Encoding Requirements

**Critical**: Always use `%24` instead of `$` for the parameter name, and encode spaces as `%20`:

```bash
#  CORRECT: Proper URL encoding
curl "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc&%24top=5"

# L WRONG: Direct $ character (may fail in some clients)
curl "https://oda.ft.dk/api/Sag?$orderby=opdateringsdato desc&$top=5"
```

### Common Encoding Issues

| Character | URL Encoded | Usage |
|-----------|-------------|--------|
| `$` | `%24` | Parameter prefix: `%24orderby` |
| Space | `%20` | Between field and direction: `id%20desc` |
| Comma | `%2C` | Multi-field separator (optional) |

## Performance Considerations

### Response Time by Query Type

Based on testing with the Danish Parliament API:

| Sort Type | Typical Response Time | Notes |
|-----------|----------------------|--------|
| Single field, small dataset (d100 records) | ~85-150ms | Excellent performance |
| Multi-field, small dataset | ~100-200ms | Minimal overhead |
| Single field, large dataset (1000+ records) | ~300-500ms | Still very responsive |
| Multi-field with expansion | ~500ms-2s | Depends on complexity |

### Performance Best Practices

1. **Use ID sorting for pagination**: Most efficient for large datasets
2. **Limit expansions**: Only expand when sorting by related fields
3. **Use `$top` with sorting**: Avoid sorting entire large datasets
4. **Choose efficient fields**: ID fields sort faster than text fields

```bash
#  EFFICIENT: Sort by ID for pagination
curl "https://oda.ft.dk/api/Sag?%24orderby=id&%24skip=1000&%24top=100"

#   LESS EFFICIENT: Sort by text field on large dataset
curl "https://oda.ft.dk/api/Sag?%24orderby=titel&%24skip=1000&%24top=100"
```

## Practical Examples

### Recent Activity Monitoring

Track the most recent changes across different entities:

```javascript
// Recent parliamentary activity across all entities
const recentQueries = {
    cases: "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc&%24top=10",
    votes: "https://oda.ft.dk/api/Afstemning?%24orderby=opdateringsdato%20desc&%24top=10",
    meetings: "https://oda.ft.dk/api/Møde?%24orderby=opdateringsdato%20desc&%24top=10",
    actors: "https://oda.ft.dk/api/Aktør?%24orderby=opdateringsdato%20desc&%24top=10"
};

// Fetch most recent updates
async function getRecentActivity() {
    const results = {};
    for (const [entity, url] of Object.entries(recentQueries)) {
        const response = await fetch(url);
        results[entity] = await response.json();
    }
    return results;
}
```

### Historical Analysis

Find earliest and latest records for temporal analysis:

```bash
# Earliest available data (by update date)
curl "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20asc&%24top=5&%24select=id,titel,opdateringsdato"

# Most recent data (by case ID - representing newest case numbers)
curl "https://oda.ft.dk/api/Sag?%24orderby=id%20desc&%24top=5&%24select=id,titel,opdateringsdato"

# Parliamentary periods chronologically
curl "https://oda.ft.dk/api/Periode?%24orderby=startdato&%24select=id,titel,startdato,slutdato"
```

### Complex Sorting for Analysis

Multi-criteria sorting for sophisticated queries:

```bash
# Cases by type, then by most recent activity within each type
curl "https://oda.ft.dk/api/Sag?%24orderby=typeid,opdateringsdato%20desc&%24top=20"

# Politicians by party group, then alphabetically within group
curl "https://oda.ft.dk/api/Aktør?%24orderby=gruppeid,navn&%24top=50"

# Documents by case, then by creation order within each case
curl "https://oda.ft.dk/api/Dokument?%24orderby=sagid,id&%24top=100"
```

## Error Handling

### Common Sorting Errors

The API handles sorting errors gracefully:

```bash
# Invalid field name - returns HTTP 400 Bad Request
curl "https://oda.ft.dk/api/Sag?%24orderby=invalid_field"

# Invalid direction - returns HTTP 400 Bad Request  
curl "https://oda.ft.dk/api/Sag?%24orderby=id%20invalid"

# Sorting by non-existent expanded field - returns HTTP 400
curl "https://oda.ft.dk/api/Sag?%24orderby=NonExistentEntity/field"
```

### Error Response Format

```json
{
    "error": {
        "code": "",
        "message": {
            "lang": "en",
            "value": "Could not find a property named 'invalid_field' on type 'DataServiceProviderDemo.Sag'."
        }
    }
}
```

## Client Implementation Examples

### JavaScript/TypeScript

```javascript
class ParliamentSorter {
    constructor(baseUrl = 'https://oda.ft.dk/api') {
        this.baseUrl = baseUrl;
    }

    // Build orderby parameter from sort configuration
    buildOrderBy(sorts) {
        return sorts
            .map(sort => `${sort.field}${sort.direction ? ' ' + sort.direction : ''}`)
            .join(',');
    }

    // Fetch sorted data with proper URL encoding
    async getSortedData(entity, sorts, options = {}) {
        const orderBy = this.buildOrderBy(sorts);
        const params = new URLSearchParams();
        
        params.set('$orderby', orderBy);
        if (options.top) params.set('$top', options.top);
        if (options.skip) params.set('$skip', options.skip);
        if (options.select) params.set('$select', options.select);
        if (options.filter) params.set('$filter', options.filter);

        const url = `${this.baseUrl}/${entity}?${params.toString()}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Sort failed: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    }
}

// Usage examples
const sorter = new ParliamentSorter();

// Single field sort
const recentCases = await sorter.getSortedData('Sag', [
    { field: 'opdateringsdato', direction: 'desc' }
], { top: 10 });

// Multi-field sort
const sortedActors = await sorter.getSortedData('Aktør', [
    { field: 'gruppeid' },              // Ascending by default
    { field: 'navn', direction: 'asc' }  // Explicit ascending
], { top: 50 });
```

### Python

```python
import requests
from urllib.parse import urlencode
from typing import List, Dict, Optional

class ParliamentSorter:
    def __init__(self, base_url: str = "https://oda.ft.dk/api"):
        self.base_url = base_url
    
    def build_orderby(self, sorts: List[Dict[str, str]]) -> str:
        """Build $orderby parameter from sort configuration."""
        order_parts = []
        for sort in sorts:
            field = sort['field']
            direction = sort.get('direction', '')
            if direction:
                order_parts.append(f"{field} {direction}")
            else:
                order_parts.append(field)
        return ','.join(order_parts)
    
    def get_sorted_data(self, entity: str, sorts: List[Dict[str, str]], 
                       top: Optional[int] = None, skip: Optional[int] = None,
                       select: Optional[str] = None, filter_expr: Optional[str] = None) -> Dict:
        """Fetch sorted data with proper URL encoding."""
        
        params = {
            '$orderby': self.build_orderby(sorts)
        }
        
        if top: params['$top'] = top
        if skip: params['$skip'] = skip
        if select: params['$select'] = select
        if filter_expr: params['$filter'] = filter_expr
        
        url = f"{self.base_url}/{entity}?{urlencode(params)}"
        
        response = requests.get(url)
        response.raise_for_status()  # Raises exception for HTTP errors
        
        return response.json()

# Usage examples
sorter = ParliamentSorter()

# Recent cases sorted by update date
recent_cases = sorter.get_sorted_data('Sag', [
    {'field': 'opdateringsdato', 'direction': 'desc'}
], top=10)

# Multi-field sorting
sorted_actors = sorter.get_sorted_data('Aktør', [
    {'field': 'gruppeid'},  # Ascending by default
    {'field': 'navn', 'direction': 'asc'}
], top=50)

# Complex query with filtering and sorting
climate_cases = sorter.get_sorted_data('Sag', [
    {'field': 'opdateringsdato', 'direction': 'desc'}
], filter_expr="substringof('klima',titel)", select="id,titel,opdateringsdato", top=20)
```

## Best Practices Summary

1. **Always URL encode**: Use `%24orderby` and `%20` for spaces
2. **Use appropriate field types**: ID fields for performance, dates for temporal ordering
3. **Combine with other parameters**: `$top`, `$filter`, `$select` for efficient queries
4. **Handle errors gracefully**: Check for HTTP 400 responses on invalid sort fields
5. **Consider performance**: Multi-field sorts and expansions add response time
6. **Test with real data**: Danish character sorting (æ, ø, å) works correctly
7. **Use consistent pagination**: ID-based sorting is most efficient for large datasets

The Danish Parliament API's ordering capabilities provide powerful tools for organizing and analyzing parliamentary data. With proper URL encoding and understanding of performance characteristics, you can build sophisticated applications that efficiently sort through Denmark's comprehensive legislative dataset.