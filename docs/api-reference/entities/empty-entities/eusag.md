# EUsag (EU Cases) Entity

The `EUsag` entity is designed to represent EU-related parliamentary cases and matters handled by the Danish Parliament. This entity is currently **dormant** with no data records, but maintains a complete schema ready for future EU case processing workflows.

## Overview

- **Entity Name**: `EUsag`
- **Endpoint**: `https://oda.ft.dk/api/EUsag`
- **Total Records**: 0 (empty/dormant entity)
- **Primary Key**: `id` (Int32)
- **Status**: Schema ready, no data population
- **Purpose**: Specialized EU case processing (planned but unused)

## Current Status

!!! warning "Empty Entity"
    The EUsag entity currently contains **no data records**. All EU-related cases are handled through the regular [Sag entity](/api-reference/entities/core/sag/) instead. This entity exists as a placeholder for potential future EU-specific case workflows.

## Entity Schema

The EUsag entity shares an identical structure with the main Sag entity, suggesting it was designed for specialized EU case processing:

### Core Identification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | Int32 | Primary key, unique case identifier | `1` |
| `titel` | String | Case title | `"EU Directive implementation"` |
| `titelkort` | String | Short title | `"EU Dir. 2024/123"` |
| `nummer` | String | Case number | `"EU 123"` |

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

### Content Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `resume` | String | Case summary | `"Implementation of EU directive..."` |
| `afgørelse` | String | Decision text | `"Vedtaget"` |
| `baggrundsmateriale` | String | Background material | `"EU Commission doc 2024/123"` |
| `begrundelse` | String | Justification | `"Jævnfør EU-direktiv..."` |

## Testing the Entity

### Basic Queries

```bash
# Check if entity contains any data
curl "https://oda.ft.dk/api/EUsag?%24inlinecount=allpages&%24top=1"

# Expected response:
{
  "odata.metadata": "https://oda.ft.dk/api/$metadata#EUsag",
  "odata.count": "0",
  "value": []
}
```

### Schema Inspection

```bash
# View entity metadata structure
curl "https://oda.ft.dk/api/\$metadata" | grep -A10 "EntityType Name=\"EUsag\""
```

## Current EU Case Alternative

Since EUsag contains no data, EU-related cases are handled through the main Sag entity:

### Finding EU Cases in Sag Entity

```bash
# Search for EU-related cases
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('eu',titel)&%24top=10"

# Search for EU directives
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('direktiv',titel)&%24top=10"

# Search for European Commission communications
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('kommissionsmeddelelse',titel)&%24top=10"

# Search for EU regulations
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('forordning',titel)&%24top=10"
```

### Examples of EU Cases in Regular Sag Entity

```bash
# Recent EU-related legislation
curl "https://oda.ft.dk/api/Sag?%24filter=(substringof('eu',titel)%20or%20substringof('europæ',titel))%20and%20year(opdateringsdato)%20eq%202025&%24top=5"

# EU Green Deal related cases
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('grønne%20pagt',titel)&%24top=5"
```

## Potential Future Use Cases

If the EUsag entity becomes active, it would likely handle:

### 1. EU Directive Implementation Tracking

```python
# Hypothetical future usage
def track_eu_directive_implementation():
    """Track EU directive implementation cases"""
    filter_query = "substringof('direktiv',titel)"
    return get_eu_cases(filter_query=filter_query, expand="Sagsstatus")
```

### 2. EU Regulation Monitoring

```python
# Hypothetical future usage
def monitor_eu_regulations():
    """Monitor EU regulation cases"""
    filter_query = "substringof('forordning',titel)"
    return get_eu_cases(filter_query=filter_query, orderby="opdateringsdato desc")
```

### 3. European Commission Communications

```python
# Hypothetical future usage
def track_commission_communications():
    """Track EU Commission communication cases"""
    filter_query = "substringof('kommissionsmeddelelse',titel)"
    return get_eu_cases(filter_query=filter_query, expand="SagAktør")
```

## Danish/EU Context

### Parliamentary EU Process

The Danish Parliament (Folketinget) handles EU matters through:

1. **EU Information Procedure**: Parliamentary scrutiny of EU proposals
2. **Implementation of Directives**: National legislation implementing EU directives
3. **EU Coordination**: Cross-party coordination on EU positions
4. **European Affairs Committee**: Specialized committee for EU matters

### Types of EU Cases

EU-related cases typically include:

- **EU Directives**: Requiring national implementation
- **EU Regulations**: Directly applicable EU law
- **Commission Communications**: Policy documents and strategies
- **Council Decisions**: EU institutional decisions
- **European Green Deal**: Climate and environmental legislation
- **Digital Single Market**: Digital policy initiatives

## Related Entities

The EUsag entity would likely connect to:

- **Sag** - Main case entity (current location of EU cases)
- **SagAktør** - Case-actor relationships
- **SagDokument** - Case-document relationships  
- **Sagstrin** - Case processing steps
- **Dokument** - Related EU documents
- **Aktør** - Parliamentary actors involved

## Development Recommendations

### For API Consumers

1. **Skip EUsag Queries**: Entity contains no data
2. **Use Sag Entity**: Search regular Sag entity for EU cases
3. **Monitor for Changes**: Watch for future activation
4. **Error Handling**: Account for empty responses

### Query Strategy

```python
def get_eu_related_cases():
    """
    Current recommended approach for EU cases
    """
    # Use main Sag entity instead of empty EUsag
    eu_keywords = ['eu', 'europæ', 'direktiv', 'forordning', 'kommissionsmeddelelse']
    
    for keyword in eu_keywords:
        filter_query = f"substringof('{keyword}',titel)"
        cases = get_sag_data(filter_query=filter_query)
        # Process EU-related cases from main Sag entity
```

## Important Notes

### Entity Classification
- **Status**: Dormant/Ready (complete schema, no data)
- **Response Type**: Proper empty response (`count: "0"`, `value: []`)
- **Comparison**: Different from truly non-functional entities like Sambehandlinger

### Future Activation Monitoring
- The entity may be activated for specialized EU case workflows
- Schema is complete and functional
- Would enable separation of EU cases from national cases
- Could provide EU-specific metadata and processing

### Current Workaround
Since EUsag is empty, use the main Sag entity with EU-related filters to find:
- EU directive implementation cases
- European Commission communications
- EU regulation discussions
- European Green Deal legislation
- Digital Single Market initiatives

The EUsag entity represents planned functionality for EU case management that may be activated in future versions of the Danish Parliament API.