# Relationship Expansion Documentation

The Danish Parliament API's `$expand` parameter allows you to include related data in a single request, dramatically reducing the number of API calls needed. This guide covers all expansion patterns, performance implications, and junction table strategies.

## $expand Syntax Overview

The `$expand` parameter follows **OData 3.0 expansion syntax**:

### Basic Expansion Patterns

| Pattern | Purpose | Example |
|---------|---------|---------|
| Single relationship | Include one related entity | `$expand=Sagskategori` |
| Multiple relationships | Include several related entities | `$expand=Sagskategori,Sagstrin` |  
| Nested expansion | Multi-level relationship traversal | `$expand=Stemme/Aktør` |
| Complex nested | Multiple nested relationships | `$expand=SagAktør/Aktør,SagDokument/Dokument` |

!!! warning "URL Encoding Required"
    Always use `%24expand` instead of `$expand` in URLs:
    ```
     Correct: ?%24expand=Sagskategori
    L Wrong: ?$expand=Sagskategori
    ```

## Single Relationship Expansion

### Core Entity Expansions

#### Sag (Cases) Expansions
```bash
# Cases with their categories
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=3"

# Cases with their status information
curl "https://oda.ft.dk/api/Sag?%24expand=Sagsstatus&%24top=3"

# Cases with their type information
curl "https://oda.ft.dk/api/Sag?%24expand=Sagstype&%24top=3"

# Cases with parliamentary period
curl "https://oda.ft.dk/api/Sag?%24expand=Periode&%24top=3"
```

#### Aktør (Actors) Expansions
```bash
# Actors with their type information
curl "https://oda.ft.dk/api/Aktør?%24expand=Aktørtype&%24top=5"
```

#### Stemme (Votes) Expansions
```bash
# Individual votes with voting session details
curl "https://oda.ft.dk/api/Stemme?%24expand=Afstemning&%24top=10"

# Individual votes with politician details
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktør&%24top=10"

# Individual votes with vote type
curl "https://oda.ft.dk/api/Stemme?%24expand=Stemmetype&%24top=10"
```

#### Dokument (Documents) Expansions
```bash
# Documents with their type
curl "https://oda.ft.dk/api/Dokument?%24expand=Dokumenttype&%24top=5"

# Documents with attached files
curl "https://oda.ft.dk/api/Dokument?%24expand=Fil&%24top=5"

# Documents with their status
curl "https://oda.ft.dk/api/Dokument?%24expand=Dokumentstatus&%24top=5"
```

## Multiple Relationship Expansion

Expand several relationships in one request using comma separation:

### Common Multi-Expansion Patterns

```bash
# Cases with category and status
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori,Sagsstatus&%24top=3"

# Cases with category, status, and type  
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori,Sagsstatus,Sagstype&%24top=2"

# Cases with steps and documents
curl "https://oda.ft.dk/api/Sag?%24expand=Sagstrin,SagDokument&%24top=2"

# Votes with session, politician, and vote type
curl "https://oda.ft.dk/api/Stemme?%24expand=Afstemning,Aktør,Stemmetype&%24top=5"
```

### Performance Considerations for Multiple Expansions

| Expansion Count | Response Time | Recommendation |
|-----------------|---------------|----------------|
| 1-2 expansions | ~90-150ms |  Optimal |
| 3-4 expansions | ~200-400ms |   Monitor performance |
| 5+ expansions | ~500ms+ | L Consider multiple requests |

## Nested Relationship Expansion

Navigate through multiple levels of relationships:

### Two-Level Expansions (Most Common)

```bash
# Votes with politician biography information  
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktør&%24top=5"
# Note: Aktør includes biografi field directly

# Cases with actor relationships and actor details
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør&%24top=2"

# Cases with document relationships and document details
curl "https://oda.ft.dk/api/Sag?%24expand=SagDokument/Dokument&%24top=2"

# Voting sessions with individual votes and politicians
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme/Aktør&%24top=1"
```

### Three-Level Expansions (Maximum Depth)

```bash
# Documents with actor relationships and full actor details
curl "https://oda.ft.dk/api/Dokument?%24expand=DokumentAktør/Aktør/Aktørtype&%24top=1"

# Cases with steps and step documents
curl "https://oda.ft.dk/api/Sag?%24expand=Sagstrin/SagstrinDokument/Dokument&%24top=1"
```

!!! danger "Performance Warning"
    **Three-level expansions can be very slow** (~2+ seconds). Use sparingly and with small `$top` values.

## Junction Table Expansion Patterns

The Danish Parliament API uses junction tables extensively to model complex relationships. Master these patterns for effective data access.

### SagAktør (Case-Actor Junction)

The `SagAktør` entity connects cases to actors with 23 different role types:

```bash  
# Cases with all related actors and their roles
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør&%24top=2"

# Cases with actor details through junction table
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør&%24top=2"

# Cases with actor details AND role information
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør,SagAktør/SagAktørRolle&%24top=2"

# Direct junction table access with full expansion
curl "https://oda.ft.dk/api/SagAktør?%24expand=Sag,Aktør,SagAktørRolle&%24top=10"
```

### DokumentAktør (Document-Actor Junction)

The `DokumentAktør` entity connects documents to actors with 25 role types:

```bash
# Documents with all related actors  
curl "https://oda.ft.dk/api/Dokument?%24expand=DokumentAktør&%24top=3"

# Documents with actor details through junction
curl "https://oda.ft.dk/api/Dokument?%24expand=DokumentAktør/Aktør&%24top=3"

# Direct access to document-actor relationships
curl "https://oda.ft.dk/api/DokumentAktør?%24expand=Dokument,Aktør,DokumentAktørRolle&%24top=10"
```

### SagDokument (Case-Document Junction)

```bash
# Cases with all related documents
curl "https://oda.ft.dk/api/Sag?%24expand=SagDokument&%24top=2"

# Cases with full document details
curl "https://oda.ft.dk/api/Sag?%24expand=SagDokument/Dokument&%24top=2"

# Documents attached to cases with relationship info
curl "https://oda.ft.dk/api/SagDokument?%24expand=Sag,Dokument,SagDokumentRolle&%24top=10"
```

## Real-World Expansion Examples

### Political Analysis Expansions

#### Get Complete Politician Voting Records
```bash
# All votes by Frank Aaen with session details
curl "https://oda.ft.dk/api/Stemme?%24filter=Aktør/navn%20eq%20'Frank%20Aaen'&%24expand=Afstemning,Aktør&%24top=20"
```

#### Get Legislative Process Details  
```bash
# Climate legislation with complete process information
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)&%24expand=Sagstrin,SagAktør/Aktør&%24top=3"
```

#### Get Committee Work Overview
```bash
# Cases handled by specific committees with actor details
curl "https://oda.ft.dk/api/SagAktør?%24filter=substringof('udvalg',Aktør/navn)&%24expand=Sag,Aktør&%24top=10"
```

### Document Analysis Expansions

#### Get Complete Document Context
```bash
# Documents with authors and attached files
curl "https://oda.ft.dk/api/Dokument?%24expand=DokumentAktør/Aktør,Fil&%24top=5"
```

#### Get Parliamentary Meeting Records
```bash
# Meetings with agenda items and related documents
curl "https://oda.ft.dk/api/Møde?%24expand=Dagsordenspunkt&%24top=3"
```

### Voting Analysis Expansions  

#### Complete Voting Session Analysis
```bash
# Voting sessions with all individual votes and politicians
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme/Aktør&%24top=1"
```

!!! warning "Performance Impact"
    This query can take 2+ seconds due to the large number of individual votes per session.

#### Efficient Voting Analysis Alternative
```bash
# Get voting session details first
curl "https://oda.ft.dk/api/Afstemning?%24top=1&%24expand=Møde"

# Then get votes for specific session  
curl "https://oda.ft.dk/api/Stemme?%24filter=afstemningid%20eq%2012345&%24expand=Aktør&%24top=100"
```

## Error Handling in Expansions

### Valid vs. Invalid Expansion Names

#### Valid Expansions (HTTP 200)
```bash
# These work correctly
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=1"         # 
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør&%24top=1"       #   
curl "https://oda.ft.dk/api/Stemme?%24expand=Afstemning,Aktør&%24top=1"  # 
```

#### Invalid Expansions (HTTP 400)
```bash
# These return HTTP 400 Bad Request
curl -i "https://oda.ft.dk/api/Sag?%24expand=NonExistentRelation&%24top=1"     # L
curl -i "https://oda.ft.dk/api/Sag?%24expand=InvalidPath/BadEntity&%24top=1"   # L
```

### Error Response Format
```json
{
  "odata.error": {
    "code": "",
    "message": {
      "lang": "en-US", 
      "value": "Could not find a property named 'NonExistentRelation'..."
    }
  }
}
```

## Performance Optimization Strategies

### 1. Strategic Expansion Selection

```bash
# Efficient: Only expand what you need
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=10"

# Less efficient: Expanding everything
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori,Sagsstatus,Sagstype,SagAktør,SagDokument&%24top=10"
```

### 2. Filter Before Expansion

```bash
# Efficient: Filter first, then expand
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025&%24expand=SagAktør/Aktør&%24top=10"

# Less efficient: Expand first, filter gets applied to larger dataset
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør&%24filter=year(opdateringsdato)%20eq%202025&%24top=10"
```

### 3. Pagination with Expansion

```bash
# Efficient pattern for large expanded datasets
for skip in {0..500..50}; do  # Note: smaller batch size with expansion
    curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør&%24skip=$skip&%24top=50"
    sleep 0.2  # Rate limiting for complex queries
done
```

### 4. Alternative Multi-Request Strategy

Sometimes multiple simple requests are faster than complex expansions:

```python
# Python: Multi-request strategy for complex data
import requests

# Strategy 1: Single complex request (may be slow)
complex_url = "https://oda.ft.dk/api/Sag?$expand=SagAktør/Aktør,SagDokument/Dokument&$top=10"

# Strategy 2: Multiple simple requests (may be faster)
cases = requests.get("https://oda.ft.dk/api/Sag?$top=10").json()
for case in cases['value']:
    case_id = case['id']
    
    # Get actors for this case
    actors_url = f"https://oda.ft.dk/api/SagAktør?$filter=sagid eq {case_id}&$expand=Aktør"
    case['actors'] = requests.get(actors_url).json()['value']
    
    # Get documents for this case  
    docs_url = f"https://oda.ft.dk/api/SagDokument?$filter=sagid eq {case_id}&$expand=Dokument"
    case['documents'] = requests.get(docs_url).json()['value']
```

## Complete Entity Relationship Map

### Core Entities and Their Expansions

#### Sag (Cases) - 15+ Expandable Relationships
- `Sagskategori` - Case category
- `Sagsstatus` - Case status  
- `Sagstype` - Case type
- `Periode` - Parliamentary period
- `Sagstrin` - Case steps
- `SagAktør` - Related actors (junction)
- `SagDokument` - Related documents (junction)  
- `EmneordSag` - Keywords (junction)
- `DagsordenspunktSag` - Agenda items (junction)

#### Aktør (Actors) - 10+ Expandable Relationships
- `Aktørtype` - Actor type
- `AktørAktør` - Actor relationships (junction)
- `SagAktør` - Related cases (junction)
- `DokumentAktør` - Related documents (junction)  
- `MødeAktør` - Meeting participation (junction)
- `SagstrinAktør` - Case step participation (junction)

#### Dokument (Documents) - 8+ Expandable Relationships  
- `Dokumenttype` - Document type
- `Dokumentstatus` - Document status
- `Dokumentkategori` - Document category
- `Fil` - Attached files
- `DokumentAktør` - Related actors (junction)
- `SagDokument` - Related cases (junction)
- `EmneordDokument` - Keywords (junction)

## Advanced Expansion Patterns

### Conditional Expansion Based on Entity Type

```python
# Python: Smart expansion based on entity characteristics
def expand_entity_smartly(entity_name, record_id):
    """Apply optimal expansion strategy based on entity type"""
    
    expansion_strategies = {
        'Sag': 'Sagskategori,Sagsstatus',  # Core info only
        'Aktør': 'Aktørtype',  # Type information
        'Stemme': 'Afstemning,Aktør',  # Full voting context
        'Dokument': 'Dokumenttype,Fil',  # Type and files
        'Afstemning': 'Møde',  # Meeting context (not all votes - too slow)
    }
    
    expand = expansion_strategies.get(entity_name, '')
    url = f"https://oda.ft.dk/api/{entity_name}?$filter=id eq {record_id}"
    
    if expand:
        url += f"&$expand={expand}"
    
    return requests.get(url).json()
```

### Expansion-Aware Pagination

```python
# Python: Adjust pagination batch size based on expansion complexity
def get_expansion_batch_size(expansion_string):
    """Recommend batch size based on expansion complexity"""
    
    if not expansion_string:
        return 100  # No expansion: use maximum
    
    expansion_count = expansion_string.count(',') + 1
    nested_levels = expansion_string.count('/')
    
    # Reduce batch size for complex expansions
    if nested_levels >= 2:
        return 10  # Very complex: small batches
    elif expansion_count >= 3:
        return 25  # Multiple expansions: medium batches  
    else:
        return 50  # Simple expansion: standard batches

# Usage
expansion = "SagAktør/Aktør,SagDokument/Dokument"
batch_size = get_expansion_batch_size(expansion)  # Returns 10

url = f"https://oda.ft.dk/api/Sag?$expand={expansion}&$top={batch_size}"
```

## Best Practices Summary

1. **Use URL encoding** (`%24expand` not `$expand`)
2. **Start with simple expansions** and add complexity gradually  
3. **Filter before expanding** to reduce data processing
4. **Monitor response times** and adjust batch sizes accordingly
5. **Use junction tables strategically** to access relationship data
6. **Consider multi-request strategies** for very complex data needs
7. **Cache frequently accessed relationship data** to minimize API calls
8. **Test expansion paths** against metadata to avoid HTTP 400 errors

## Quick Reference

### Most Useful Expansion Patterns
```bash
# Cases with essential metadata
?%24expand=Sagskategori,Sagsstatus

# Complete voting context  
?%24expand=Afstemning,Aktør,Stemmetype

# Document with files and author
?%24expand=Fil,DokumentAktør/Aktør

# Junction table with full relationship context
?%24expand=Sag,Aktør,SagAktørRolle
```

### Performance Guidelines  
- **1-2 expansions**: ~90-150ms ( Optimal)
- **3+ expansions**: ~200ms+ (  Monitor)  
- **Nested expansions**: ~500ms+ (L Use carefully)
- **Voting with actors**: ~2s+ (L Paginate aggressively)

The Danish Parliament API's expansion capabilities provide powerful access to the complex relationships within parliamentary data. Master these patterns and you'll efficiently navigate the interconnected web of Danish democratic information.