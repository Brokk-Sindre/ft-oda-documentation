# Interactive Query Builder

The Interactive Query Builder is a powerful visual tool for constructing and testing Danish Parliament API queries. Build complex OData queries without writing code, preview results in real-time, and export to your preferred programming language.

<div class="query-builder"></div>

## Overview

The Interactive Query Builder simplifies working with the Danish Parliament API by providing:

- **Visual Interface** - Point-and-click query construction
- **Real-time Validation** - Immediate feedback on query syntax
- **URL Encoding Handling** - Automatic %24 parameter encoding
- **Multi-language Export** - Generate code for Python, JavaScript, cURL
- **Live Testing** - Test queries directly from the browser
- **Query Templates** - Pre-built patterns for common use cases

### Key Features

#### = **Entity Selection**
Choose from 50+ parliamentary entities including cases (Sag), actors (Aktør), votes (Stemme), documents (Dokument), and meetings (Møde).

#### ¡ **Smart Autocompletion**
Field suggestions and validation based on the selected entity type with context-aware autocompletion for filters and expansions.

#### = **URL Generation**
Generates properly encoded API URLs with automatic %24 encoding for OData parameters - the critical requirement for the Danish Parliament API.

#### =Ê **Query Preview**
Real-time preview of generated queries with estimated result counts and performance indicators.

## Interface Components

### Basic Query Builder

The basic interface provides essential query construction tools:

#### Entity Selector
```
=Ä Sag (Cases) - 96,538+ records
=d Aktør (Actors) - 18,139+ records  
=ó Afstemning (Voting Sessions)
 Stemme (Individual Votes)
=Ë Dokument (Documents)
<Û Møde (Meetings)
```

#### Parameter Controls
- **Limit ($top)** - Number of records to return (max: 100)
- **Skip ($skip)** - Records to skip for pagination
- **Filter ($filter)** - OData filter expressions
- **Expand ($expand)** - Related entity expansion
- **Select ($select)** - Field selection for performance
- **Order By ($orderby)** - Result sorting
- **Include Count** - Total record count in results

### Advanced Query Builder

The advanced interface adds sophisticated query construction tools:

#### Filter Builder
Visual filter construction with:
- **Field Selection** - Choose from entity-specific fields
- **Operator Selection** - equals, contains, greater than, etc.
- **Value Input** - Type-aware value validation
- **Multiple Conditions** - AND/OR logic composition

#### Quick Filters
Pre-built filter templates:
- **Recent** - Updated in last 7 days
- **This Year** - Records from current year
- **Public Only** - Public documents only
- **Active Status** - Active parliamentary items

#### Response Format
Choose output format:
- **JSON** - Default structured data format
- **XML** - Alternative XML format

## Query Construction Guide

### 1. Basic Query Setup

**Step 1: Select Entity**
Choose the parliamentary entity you want to query:
```
Entity: Sag (Cases)
```

**Step 2: Set Limits**
Configure result pagination:
```
Limit: 10
Skip: 0
```

**Step 3: Add Filters (Optional)**
Filter results based on criteria:
```
Filter: year(opdateringsdato) eq 2025
```

### 2. Field Selection and Expansion

**Select Specific Fields**
Improve performance by selecting only needed fields:
```
Select: id,titel,opdateringsdato,statusid
```

**Expand Related Entities**
Include related data in a single request:
```
Expand: Sagsstatus,Sagstype,SagAktør
```

### 3. Sorting and Counting

**Order Results**
Sort by any field:
```
Order By: opdateringsdato desc
```

**Include Total Count**
Get the total available records:
```
 Include total count
```

## OData Parameter Reference

### Critical: URL Encoding

The Danish Parliament API requires proper URL encoding for all OData parameters:

```
 CORRECT: %24top=10&%24filter=year(opdateringsdato)%20eq%202025
L WRONG:   $top=10&$filter=year(opdateringsdato) eq 2025
```

The Query Builder automatically handles this encoding.

### Supported Parameters

#### $top - Result Limit
```
Description: Maximum number of records to return
Syntax: %24top=NUMBER
Example: %24top=50
Range: 1-100
```

#### $skip - Pagination Offset
```
Description: Number of records to skip
Syntax: %24skip=NUMBER  
Example: %24skip=100
Use: Pagination through large datasets
```

#### $filter - Query Filtering
```
Description: OData filter expressions
Syntax: %24filter=EXPRESSION
Examples:
  - %24filter=year(opdateringsdato)%20eq%202025
  - %24filter=substringof('klima',titel)
  - %24filter=statusid%20eq%2010
```

#### $expand - Related Data
```
Description: Include related entities
Syntax: %24expand=RELATIONS
Examples:
  - %24expand=Sagsstatus
  - %24expand=Sagsstatus,Sagstype
  - %24expand=SagAktør/Aktør
```

#### $select - Field Selection
```
Description: Choose specific fields
Syntax: %24select=FIELDS
Example: %24select=id,titel,opdateringsdato
Benefit: Reduces response size and improves performance
```

#### $orderby - Result Sorting
```
Description: Sort results by fields
Syntax: %24orderby=FIELD%20DIRECTION
Examples:
  - %24orderby=opdateringsdato%20desc
  - %24orderby=titel%20asc
  - %24orderby=id,titel
```

#### $inlinecount - Total Count
```
Description: Include total record count
Syntax: %24inlinecount=allpages
Result: Adds "odata.count" field to response
Use: Pagination calculations
```

#### $format - Response Format
```
Description: Output format selection
Syntax: %24format=FORMAT
Options: json (default), xml
Example: %24format=xml
```

## Filter Expression Guide

### Text Filtering

#### Substring Search
```
substringof('search_term', field_name)
Example: substringof('klima', titel)
Use Case: Find cases containing "klima"
```

#### Exact Match
```
field_name eq 'exact_value'
Example: titel eq 'Forslag til folketingsbeslutning om klima'
Use Case: Find exact title matches
```

#### Starts With
```
startswith(field_name, 'prefix')
Example: startswith(titel, 'Forslag')
Use Case: Find bills starting with "Forslag"
```

#### Ends With
```
endswith(field_name, 'suffix')
Example: endswith(titel, 'klima')
Use Case: Find titles ending with "klima"
```

### Numeric Filtering

#### Equality
```
field_name eq NUMBER
Example: statusid eq 10
Use Case: Find cases with specific status
```

#### Range Queries
```
field_name ge NUMBER and field_name le NUMBER
Example: id ge 100000 and id le 102000
Use Case: Find cases in ID range
```

#### Greater Than/Less Than
```
field_name gt NUMBER
field_name lt NUMBER
Example: id gt 100000
Use Case: Find recent cases (higher IDs)
```

### Date Filtering

#### Year Function
```
year(date_field) eq YEAR
Example: year(opdateringsdato) eq 2025
Use Case: Find records from specific year
```

#### Date Range
```
date_field ge datetime'YYYY-MM-DD'
Example: opdateringsdato ge datetime'2025-01-01'
Use Case: Find records after specific date
```

#### Recent Records
```
date_field ge datetime'YYYY-MM-DDTHH:MM:SS'
Example: opdateringsdato ge datetime'2025-01-01T00:00:00'
Use Case: Find very recent updates
```

### Logical Operators

#### AND Logic
```
condition1 and condition2
Example: year(opdateringsdato) eq 2025 and statusid eq 10
Use Case: Multiple conditions must be true
```

#### OR Logic
```
condition1 or condition2
Example: statusid eq 8 or statusid eq 10
Use Case: Either condition can be true
```

#### NOT Logic
```
not condition
Example: not substringof('privat', titel)
Use Case: Exclude certain conditions
```

## Entity-Specific Queries

### Cases (Sag) - 96,538+ Records

#### Common Fields
- `id` - Unique case identifier
- `titel` - Case title/description
- `offentlighedskode` - Publicity code (O=public, K=confidential)
- `opdateringsdato` - Last update timestamp
- `statusid` - Current case status
- `typeid` - Case type identifier

#### Common Expansions
- `Sagsstatus` - Case status details
- `Sagstype` - Case type information
- `Sagskategori` - Case category
- `SagAktør` - Related actors (politicians, parties)
- `Periode` - Parliamentary period

#### Example Queries
```
Recent public cases:
%24filter=offentlighedskode%20eq%20'O'%20and%20year(opdateringsdato)%20eq%202025&%24top=20

Climate-related legislation:
%24filter=substringof('klima',titel)&%24expand=Sagsstatus&%24top=10

Active government bills:
%24filter=statusid%20in%20(8,24,25,26)&%24expand=Sagstype&%24orderby=opdateringsdato%20desc
```

### Actors (Aktør) - 18,139+ Records

#### Common Fields
- `id` - Unique actor identifier
- `navn` - Actor name
- `typeid` - Actor type (5=politician, 6=party, etc.)
- `startdato` - Start date of role
- `slutdato` - End date of role (null if active)
- `opdateringsdato` - Last update

#### Common Expansions
- `Aktørtype` - Actor type details
- `Periode` - Parliamentary period
- `SagAktør` - Cases they're involved in
- `DokumentAktør` - Documents they've authored

#### Example Queries
```
Active politicians:
%24filter=typeid%20eq%205%20and%20slutdato%20eq%20null&%24top=50

Current ministers:
%24filter=substringof('minister',navn)%20and%20slutdato%20eq%20null&%24expand=Aktørtype

Parliamentary parties:
%24filter=typeid%20eq%206&%24orderby=navn&%24expand=Periode
```

### Voting Sessions (Afstemning)

#### Common Fields
- `id` - Voting session identifier
- `nummer` - Voting session number
- `konklusion` - Voting conclusion/result
- `vedtaget` - Whether adopted (true/false)
- `opdateringsdato` - Last update

#### Common Expansions
- `Stemme` - Individual votes in this session
- `Afstemningstype` - Type of voting session
- `Møde` - Meeting where voting occurred
- `Sag` - Case being voted on

#### Example Queries
```
Recent successful votes:
%24filter=vedtaget%20eq%20true%20and%20year(opdateringsdato)%20eq%202025&%24top=20

Close votes:
%24filter=substringof('vedtaget%20med',konklusion)&%24expand=Stemme&%24top=10
```

### Individual Votes (Stemme)

#### Common Fields
- `id` - Vote identifier
- `typeid` - Vote type (1=for, 2=against, 3=abstain)
- `afstemningid` - Voting session ID
- `aktørid` - Politician who cast the vote
- `opdateringsdato` - Last update

#### Common Expansions
- `Aktør` - Politician who voted
- `Afstemning` - Voting session details
- `Stemmetype` - Vote type description

#### Example Queries
```
Recent votes by politician:
%24filter=aktørid%20eq%20POLITICIAN_ID&%24expand=Afstemning&%24top=50

Against votes analysis:
%24filter=typeid%20eq%202&%24expand=Aktør,Afstemning&%24top=100
```

## Common Query Patterns

### Pattern 1: Recent Activity Monitor
Monitor recent parliamentary activity:

```
Entity: Sag
Filter: year(opdateringsdato) eq 2025
Order By: opdateringsdato desc
Expand: Sagsstatus
Limit: 20
```

Generated URL:
```
https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025&%24orderby=opdateringsdato%20desc&%24expand=Sagsstatus&%24top=20
```

### Pattern 2: Voting Analysis
Analyze voting patterns for specific topics:

```
Entity: Afstemning
Filter: substringof('klima', titel) or substringof('miljø', titel)
Expand: Stemme/Aktør
Order By: opdateringsdato desc
Include Count: true
```

### Pattern 3: Politician Activity
Track specific politician's involvement:

```
Entity: SagAktør
Filter: aktørid eq POLITICIAN_ID
Expand: Sag,Aktør
Order By: opdateringsdato desc
Limit: 50
```

### Pattern 4: Document Research
Search parliamentary documents:

```
Entity: Dokument
Filter: substringof('betænkning', titel) and year(dato) eq 2025
Expand: Dokumenttype,DokumentAktør/Aktør
Order By: dato desc
```

### Pattern 5: Committee Activity
Monitor committee work:

```
Entity: Møde
Filter: substringof('udvalg', titel) and year(dato) eq 2025
Expand: Mødetype,MødeAktør/Aktør
Order By: dato desc
```

## Performance Optimization

### Best Practices

#### 1. Use Field Selection
Always select only the fields you need:
```
Select: id,titel,opdateringsdato
Benefit: Reduces response size by 70-90%
```

#### 2. Limit Result Sets
Use appropriate limits:
```
Top: 50 (for exploration)
Top: 100 (maximum recommended)
Avoid: Requesting all records without pagination
```

#### 3. Efficient Filtering
Place most selective filters first:
```
Good: year(opdateringsdato) eq 2025 and substringof('klima', titel)
Better: statusid eq 10 and year(opdateringsdato) eq 2025
```

#### 4. Strategic Expansion
Only expand what you need:
```
Efficient: %24expand=Sagsstatus
Costly: %24expand=SagAktør/Aktør/SagAktør
```

### Performance Indicators

The Query Builder shows performance estimates:

- **=â Fast** - Response < 500ms
- **=á Medium** - Response 500ms-2s  
- **=à Slow** - Response > 2s
- **=4 Very Slow** - Response > 5s

## Error Handling and Validation

### Common Validation Errors

#### Invalid Filter Syntax
```
Error: "Invalid filter expression"
Fix: Check parentheses and operator syntax
Example: year(opdateringsdato) eq 2025 (not =)
```

#### Unknown Field Names
```
Error: "Unknown field 'fieldname'"
Fix: Use entity-specific field suggestions
Check: Available fields in the dropdown
```

#### Invalid Operators
```
Error: "Invalid operator"
Fix: Use OData-compatible operators (eq, ne, gt, lt, etc.)
Avoid: SQL operators (=, !=, >, <)
```

#### URL Encoding Issues
```
Error: "Bad Request" or 400 status
Fix: Ensure %24 encoding for $ parameters
Check: Generated URL uses %24, not $
```

### HTTP Error Codes

The Query Builder handles and explains common errors:

#### 400 Bad Request
- **Cause**: Invalid OData syntax or missing %24 encoding
- **Solution**: Check filter syntax and URL encoding
- **Example**: Wrong operator or malformed date

#### 404 Not Found
- **Cause**: Invalid entity name or endpoint
- **Solution**: Select entity from provided list
- **Example**: Typo in entity name

#### 500 Internal Server Error
- **Cause**: Server-side processing error
- **Solution**: Simplify query or try again later
- **Example**: Very complex filter expressions

## Export and Integration

### Code Generation

The Query Builder generates ready-to-use code in multiple languages:

#### Python Example
```python
import requests

def query_parliament_api():
    url = "https://oda.ft.dk/api/Sag"
    params = {
        '$top': 10,
        '$filter': "year(opdateringsdato) eq 2025",
        '$orderby': "opdateringsdato desc",
        '$expand': "Sagsstatus"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"Found {len(data['value'])} cases:")
        for case in data['value']:
            print(f"  {case['titel'][:60]}...")
            
    except requests.RequestException as e:
        print(f"API error: {e}")

# Run the query
query_parliament_api()
```

#### JavaScript Example
```javascript
async function queryParliamentAPI() {
    const baseUrl = 'https://oda.ft.dk/api/Sag';
    const params = new URLSearchParams({
        '$top': '10',
        '$filter': 'year(opdateringsdato) eq 2025',
        '$orderby': 'opdateringsdato desc',
        '$expand': 'Sagsstatus'
    });
    
    try {
        const response = await fetch(`${baseUrl}?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        console.log(`Found ${data.value.length} cases:`);
        data.value.forEach(case => {
            console.log(`  ${case.titel.substring(0, 60)}...`);
        });
        
    } catch (error) {
        console.error('API error:', error.message);
    }
}

// Run the query
queryParliamentAPI();
```

#### cURL Example
```bash
#!/bin/bash

# Query Danish Parliament API
curl -s "https://oda.ft.dk/api/Sag?\$top=10&\$filter=year(opdateringsdato)%20eq%202025&\$orderby=opdateringsdato%20desc&\$expand=Sagsstatus" \
  | jq -r '.value[] | "\(.id): \(.titel[0:60])..."'

# Alternative with proper URL encoding
curl -s "https://oda.ft.dk/api/Sag?%24top=10&%24filter=year(opdateringsdato)%20eq%202025&%24orderby=opdateringsdato%20desc&%24expand=Sagsstatus" \
  | jq '.value | length'
```

#### TypeScript Example
```typescript
interface Case {
    id: number;
    titel: string;
    opdateringsdato: string;
    statusid: number;
    Sagsstatus?: {
        status: string;
    };
}

interface APIResponse<T> {
    value: T[];
    'odata.count'?: string;
}

async function queryParliamentAPI(): Promise<Case[]> {
    const baseUrl = 'https://oda.ft.dk/api/Sag';
    const params = new URLSearchParams({
        '$top': '10',
        '$filter': 'year(opdateringsdato) eq 2025',
        '$orderby': 'opdateringsdato desc',
        '$expand': 'Sagsstatus'
    });
    
    try {
        const response = await fetch(`${baseUrl}?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data: APIResponse<Case> = await response.json();
        
        console.log(`Found ${data.value.length} cases:`);
        data.value.forEach(case => {
            console.log(`  ${case.id}: ${case.titel.substring(0, 60)}...`);
            if (case.Sagsstatus) {
                console.log(`    Status: ${case.Sagsstatus.status}`);
            }
        });
        
        return data.value;
        
    } catch (error) {
        console.error('API error:', error);
        throw error;
    }
}

// Run the query
queryParliamentAPI().then(cases => {
    console.log('Query completed successfully');
}).catch(error => {
    console.error('Query failed:', error);
});
```

## Advanced Features

### Query Sharing
Share constructed queries with colleagues:
- **URL Generation** - Shareable URLs with embedded parameters
- **QR Code** - Mobile-friendly query sharing
- **Email Integration** - Send queries via email

### Query History
Track your query construction:
- **Recent Queries** - Last 10 constructed queries
- **Favorites** - Save frequently used patterns
- **Export History** - Download query history

### Batch Operations
Test multiple related queries:
- **Query Templates** - Pre-built query sets
- **Comparative Analysis** - Run similar queries
- **Result Comparison** - Side-by-side results

## Integration Examples

### Jupyter Notebook Integration
```python
# In Jupyter cell
from IPython.display import IFrame

# Display the Query Builder
IFrame('https://your-docs-site.github.io/query-builder/', width=800, height=600)
```

### VS Code Integration
```json
{
    "name": "Danish Parliament API",
    "scope": "window",
    "command": "workbench.action.openSettings",
    "args": "query-builder.url"
}
```

### REST Client Integration
Save generated queries as `.http` files:
```http
### Recent Parliamentary Cases
GET https://oda.ft.dk/api/Sag?%24top=10&%24filter=year(opdateringsdato)%20eq%202025&%24orderby=opdateringsdato%20desc

### Voting Analysis
GET https://oda.ft.dk/api/Afstemning?%24expand=Stemme&%24top=20&%24filter=vedtaget%20eq%20true
```

## Tips and Tricks

### 1. Quick Start Patterns
Use these patterns to get started quickly:

**Today's Activity**
```
Filter: year(opdateringsdato) eq 2025 and month(opdateringsdato) eq 1 and day(opdateringsdato) eq 10
```

**Public Documents Only**
```
Filter: offentlighedskode eq 'O'
```

**Recent Major Votes**
```
Entity: Afstemning
Filter: vedtaget eq true and year(opdateringsdato) eq 2025
Expand: Sag
```

### 2. Performance Shortcuts
- Start with small limits (10-20) during exploration
- Add specific filters before expanding
- Use field selection for large datasets

### 3. Debugging Queries
- Check the "Test" button for immediate validation
- Use the browser's network tab to see raw requests
- Start simple and add complexity gradually

### 4. Common Gotchas
- **Date Formats**: Use `datetime'YYYY-MM-DD'` format
- **Text Search**: Use `substringof()` function, not LIKE
- **Boolean Values**: Use `true`/`false`, not `1`/`0`
- **Null Values**: Use `field eq null`, not `field = null`

## Troubleshooting

### Query Builder Not Loading
```
Symptom: Interface doesn't appear
Causes:
  - JavaScript disabled in browser
  - Network connectivity issues
  - Content security policy restrictions

Solutions:
  - Enable JavaScript
  - Check browser console for errors
  - Try refreshing the page
```

### Generated URLs Don't Work
```
Symptom: API returns 400 Bad Request
Causes:
  - Missing %24 encoding
  - Invalid OData syntax
  - Unsupported operators

Solutions:
  - Copy URL from Query Builder (pre-encoded)
  - Test in Query Builder first
  - Check filter syntax
```

### Slow Performance
```
Symptom: Queries take > 5 seconds
Causes:
  - Large result sets without pagination
  - Complex expansions
  - Unfiltered queries on large entities

Solutions:
  - Add specific filters
  - Reduce expansion scope
  - Use field selection
  - Implement pagination
```

### No Results Returned
```
Symptom: Empty result set
Causes:
  - Overly restrictive filters
  - Incorrect date formats
  - Wrong field names

Solutions:
  - Simplify filters
  - Check field suggestions
  - Verify date format syntax
```

## Related Tools

### Query Validation
- **[OData Validator](http://validator.odata.org/)** - Validate OData syntax
- **[JSON Validator](https://jsonlint.com/)** - Validate API responses
- **[URL Decoder](https://www.urldecoder.org/)** - Decode generated URLs

### API Testing
- **[Postman](https://www.postman.com/)** - Full-featured API client
- **[Insomnia](https://insomnia.rest/)** - Lightweight REST client
- **[HTTPie](https://httpie.io/)** - Command-line HTTP client

### Data Analysis
- **[jq](https://stedolan.github.io/jq/)** - Command-line JSON processor
- **[Pandas](https://pandas.pydata.org/)** - Python data analysis
- **[Observable](https://observablehq.com/)** - Interactive data notebooks

Start building your queries now with the Interactive Query Builder above!