# Filter Documentation

The Danish Parliament API's `$filter` parameter provides powerful querying capabilities with full support for text search, date operations, and complex logical expressions. This guide covers all filtering syntax with practical Danish parliamentary data examples.

## Filter Syntax Overview

The API uses **OData 3.0 filter syntax** with these key operators and functions:

### Comparison Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `eq` | Equals | `offentlighedskode eq 'O'` |
| `ne` | Not equals | `offentlighedskode ne 'O'` |
| `gt` | Greater than | `id gt 100000` |
| `ge` | Greater or equal | `id ge 100000` |
| `lt` | Less than | `year(opdateringsdato) lt 2025` |
| `le` | Less or equal | `year(opdateringsdato) le 2024` |

### Logical Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `and` | Logical AND | `offentlighedskode eq 'O' and year(opdateringsdato) eq 2025` |
| `or` | Logical OR | `substringof('klima',titel) or substringof('miljø',titel)` |
| `not` | Logical NOT | `not (offentlighedskode eq 'O')` |

## String Functions (Danish Text Search)

### substringof() - Text Contains

Most commonly used function for searching Danish parliamentary content:

```bash
# Find climate legislation (klima = climate)
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)&%24top=5"

# Find environment-related cases (miljø = environment)
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('miljø',titel)&%24top=5"

# Search for minister mentions (ministeren = the minister)
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('ministeren',titel)&%24top=5"

# Find EU-related legislation
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('eu',titel)&%24top=5"
```

### startswith() - Text Prefix

Perfect for finding specific types of parliamentary documents:

```bash
# Find legislative proposals (Forslag = Proposal)
curl "https://oda.ft.dk/api/Sag?%24filter=startswith(titel,'Forslag')&%24top=5"

# Find committee reports (Betænkning = Report)
curl "https://oda.ft.dk/api/Sag?%24filter=startswith(titel,'Betænkning')&%24top=5"

# Find government bills (Lovforslag = Bill)
curl "https://oda.ft.dk/api/Sag?%24filter=startswith(titel,'Lovforslag')&%24top=5"
```

### endswith() - Text Suffix

Useful for finding documents by their conclusion type:

```bash
# Find laws (ends with 'lov')
curl "https://oda.ft.dk/api/Sag?%24filter📁ndswith(titel,'lov')&%24top=5"

# Find questions (ends with '?')
curl "https://oda.ft.dk/api/Sag?%24filter📁ndswith(titel,'%3F')&%24top=5"
```

## Date and Time Functions

### year() - Extract Year

```bash
# All cases from 2025
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025&%24top=10"

# Historical cases from specific years
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%201995&%24top=5"

# Cases from multiple years
curl "https://oda.ft.dk/api/Sag?%24filter=(year(opdateringsdato)%20eq%202024%20or%20year(opdateringsdato)%20eq%202025)&%24top=10"
```

### month() and day() - Specific Dates

```bash
# Cases updated in September (month 9)
curl "https://oda.ft.dk/api/Sag?%24filter=month(opdateringsdato)%20eq%209&%24top=10"

# Cases from a specific day
curl "https://oda.ft.dk/api/Sag?%24filter=day(opdateringsdato)%20eq%209%20and%20month(opdateringsdato)%20eq%209&%24top=5"
```

### DateTime Comparisons

```bash
# Cases updated since January 1st, 2025
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-01-01T00:00:00'&%24top=10"

# Cases updated today (replace with current date)
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-09-09T00:00:00'&%24top=10"

# Date range queries
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-09-08T00:00:00'%20and%20opdateringsdato%20lt%20datetime'2025-09-09T00:00:00'&%24top=5"
```

## Complex Filter Examples with Danish Content

### Legislative Type Filtering

```bash
# Climate AND environment legislation
curl "https://oda.ft.dk/api/Sag?%24filter=(substringof('klima',titel)%20or%20substringof('miljø',titel))%20and%20year(opdateringsdato)%20gt%202020&%24top=5"

# Government proposals vs. member proposals
curl "https://oda.ft.dk/api/Sag?%24filter=startswith(titel,'Forslag')%20and%20substringof('regeringen',titel)&%24top=5"

# Budget-related legislation (budget = budget)
curl "https://oda.ft.dk/api/Sag?%24filter=(substringof('budget',titel)%20or%20substringof('finanslov',titel))&%24top=5"
```

### Actor-Based Filtering

```bash
# Cases involving specific politicians
curl "https://oda.ft.dk/api/Stemme?%24filter=Aktør/navn%20eq%20'Frank%20Aaen'&%24expand=Afstemning&%24top=10"

# Cases from specific committees
curl "https://oda.ft.dk/api/SagAktør?%24filter=substringof('udvalg',Aktør/navn)&%24expand=Sag,Aktør&%24top=10"
```

### Status and Category Filtering

```bash
# Only public cases
curl "https://oda.ft.dk/api/Sag?%24filter=offentlighedskode%20eq%20'O'&%24top=10"

# Cases by specific status
curl "https://oda.ft.dk/api/Sag?%24filter=Sagsstatus/status%20eq%20'Afsluttet'&%24expand=Sagsstatus&%24top=5"
```

## Danish Character Support

The API fully supports Danish special characters in filters:

### Vowels with Accents
```bash
# Search for ø character
curl "https://oda.ft.dk/api/Aktør?%24filter=substringof('ø',navn)&%24top=3"

# Search for å character  
curl "https://oda.ft.dk/api/Aktør?%24filter=substringof('å',navn)&%24top=3"

# Search for æ character
curl "https://oda.ft.dk/api/Aktør?%24filter=substringof('æ',navn)&%24top=3"
```

### Common Danish Terms in Politics

```bash
# Folketinget (Parliament)
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('Folketinget',titel)&%24top=5"

# Statsministeren (Prime Minister)
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('statsministeren',titel)&%24top=5"

# Finansministeren (Finance Minister)
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('finansministeren',titel)&%24top=5"

# Udvalg (Committee)
curl "https://oda.ft.dk/api/Aktør?%24filter=substringof('udvalg',navn)&%24top=5"
```

## Critical Filter Warnings

!!! danger "Silent Filter Failures"
    **Invalid filter field names are silently ignored** and return the complete unfiltered dataset. This is the most dangerous behavior in the API.
    
    ```bash
    # This returns ALL records (not an error!)
    curl "https://oda.ft.dk/api/Sag?%24filter=invalid_field%20eq%20'test'&%24top=5"  # Returns 100 records!
    ```

### How to Detect Silent Failures

1. **Always test with small `$top` values first**:
```bash
# Test your filter with a small result set
curl "https://oda.ft.dk/api/Sag?%24filter=your_filter_here&%24top=1"
```

2. **Monitor result counts**:
```python
# Python: Check for unexpected result sizes
response = requests.get(url)
data = response.json()
if len(data['value']) == 100 and '$top=100' not in url:
    print("Warning: Filter may have been ignored")
```

3. **Validate field names** against [OData metadata](https://oda.ft.dk/api/$metadata):
```bash
# Get valid field names for an entity
curl "https://oda.ft.dk/api/\$metadata" | grep "Property Name"
```

## URL Encoding Requirements

!!! warning "Critical: Special Character Encoding"
    All special characters in filters must be URL encoded:

| Character | Encoding | Example |
|-----------|----------|---------|
| `$` | `%24` | `%24filter=` |
| Space | `%20` | `navn%20eq%20'Frank%20Aaen'` |
| `'` | `%27` | `eq%20%27O%27` |
| `(` | `%28` | `%28substringof` |
| `)` | `%29` | `titel%29` |
| `?` | `%3F` | `endswith(titel,'%3F')` |

## Performance Optimization

### Filter Early, Expand Late
```bash
# Efficient: Filter first, then expand
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025&%24expand=Sagskategori&%24top=10"

# Less efficient: Expand everything, then filter  
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori,Sagstrin,SagAktør&%24filter=year(opdateringsdato)%20eq%202025&%24top=10"
```

### Index-Friendly Filters
The API performs best with these filter patterns:
- **ID-based filtering**: `id eq 12345`
- **Year-based filtering**: `year(opdateringsdato) eq 2025`
- **Exact string matches**: `offentlighedskode eq 'O'`

## Entity-Specific Filter Examples

### Sag (Cases) Entity
```bash
# Public legislation from current year
curl "https://oda.ft.dk/api/Sag?%24filter=offentlighedskode%20eq%20'O'%20and%20year(opdateringsdato)%20eq%202025&%24top=10"

# Bills containing climate provisions
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('lovforslag',titel)%20and%20substringof('klima',titel)&%24top=5"
```

### Aktør (Actors) Entity
```bash
# Current members of parliament (active politicians)
curl "https://oda.ft.dk/api/Aktør?%24filter=Aktørtype/type%20eq%20'person'%20and%20substringof('MF',navn)&%24expand=Aktørtype&%24top=10"

# Parliamentary committees
curl "https://oda.ft.dk/api/Aktør?%24filter=substringof('udvalg',navn)&%24top=10"
```

### Stemme (Votes) Entity
```bash
# Votes by specific politician on climate issues
curl "https://oda.ft.dk/api/Stemme?%24filter=Aktør/navn%20eq%20'Frank%20Aaen'&%24expand=Aktør,Afstemning&%24top=10"

# All "yes" votes (typeid = 1)  
curl "https://oda.ft.dk/api/Stemme?%24filter=typeid%20eq%201&%24expand=Stemmetype&%24top=10"
```

## Advanced Filter Patterns

### Multi-Language Search
```bash
# Search in both Danish and English terms
curl "https://oda.ft.dk/api/Sag?%24filter=(substringof('klima',titel)%20or%20substringof('climate',titel))&%24top=5"
```

### Temporal Filtering
```bash  
# Recent activity (last 7 days)
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-09-02T00:00:00'&%24top=10"

# Historical comparison (same month, different years)
curl "https://oda.ft.dk/api/Sag?%24filter=month(opdateringsdato)%20eq%209%20and%20(year(opdateringsdato)%20eq%202024%20or%20year(opdateringsdato)%20eq%202025)&%24top=10"
```

### Negation Patterns
```bash
# Non-public cases
curl "https://oda.ft.dk/api/Sag?%24filter=not%20(offentlighedskode%20eq%20'O')&%24top=10"

# Cases NOT containing specific terms
curl "https://oda.ft.dk/api/Sag?%24filter=not%20substringof('eu',titel)&%24top=10"
```

## Filter Function Reference

### Tested and Working Functions

| Function | Syntax | Purpose | Example |
|----------|--------|---------|---------|
| `substringof(needle, haystack)` | Text contains | `substringof('klima', titel)` | ✅ |
| `startswith(text, prefix)` | Text starts with | `startswith(titel, 'Forslag')` | ✅ |
| `endswith(text, suffix)` | Text ends with | `endswith(titel, 'lov')` | ✅ |
| `year(date)` | Extract year | `year(opdateringsdato) eq 2025` | ✅ |
| `month(date)` | Extract month | `month(opdateringsdato) eq 9` | ✅ |
| `day(date)` | Extract day | `day(opdateringsdato) eq 9` | ✅ |

### Unsupported Functions (OData 4.0+)

- `contains()` - Use `substringof()` instead
- `toupper()`, `tolower()` - Not available
- `length()` - Not supported
- `indexof()` - Not supported

## Best Practices Summary

1. **Always URL encode** special characters (`$`  `%24`)
2. **Test filters with small `$top`** values first 
3. **Monitor result sizes** to detect silent failures
4. **Use specific field names** from the metadata
5. **Filter early** before expanding relationships
6. **Leverage Danish character support** for authentic searches
7. **Combine multiple criteria** with logical operators
8. **Validate field names** against the OData metadata

The Danish Parliament API's filter capabilities provide exceptional access to 74+ years of parliamentary data when used correctly. Master these patterns and you'll efficiently find exactly the democratic information you need.