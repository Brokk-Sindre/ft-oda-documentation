# SagAktør (Case-Actor Junction)

The SagAktør entity serves as a junction table that establishes many-to-many relationships between parliamentary cases (Sag) and political actors (Aktør). This entity is fundamental for tracking political involvement and analyzing patterns of participation in the Danish Parliament.

## Entity Overview

**Base Endpoint:** `https://oda.ft.dk/api/SagAktør`

**Purpose:** Links cases to actors with specific roles, enabling analysis of who is involved in which parliamentary matters and in what capacity.

**Relationship Type:** Many-to-many junction table

## Data Structure

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | Integer | Unique identifier for the relationship | `12345` |
| `sagid` | Integer | Foreign key reference to Sag entity | `45678` |
| `aktørid` | Integer | Foreign key reference to Aktør entity | `98765` |
| `rolleid` | Integer | Foreign key to SagAktørRolle (defines role type) | `3` |
| `opdateringsdato` | DateTime | Last update timestamp | `2024-01-15T10:30:00` |

## Related Entities

### Primary Relationships

- **Sag**: The parliamentary case or matter
- **Aktør**: The political actor (politician, committee, ministry, etc.)
- **SagAktørRolle**: Defines the specific role the actor plays in the case

### Navigation Properties

When expanding the entity, you can include:
- `Sag` - Full case details
- `Aktør` - Complete actor information
- `SagAktørRolle` - Role definition and description

## Common Actor Roles

The `rolleid` field references various role types that actors can have in relation to cases:

- **Proposer (Forslagsstiller)**: The actor who proposed the case
- **Committee Member**: Member of the committee handling the case
- **Minister Responsible**: The minister responsible for the policy area
- **Rapporteur**: Committee member responsible for reporting on the case
- **Supporting Actor**: Actor who supports or co-sponsors the case

## Query Examples

### Basic Queries

#### Get all actor-case relationships
```
GET https://oda.ft.dk/api/SagAktør
```

#### Find specific relationship by ID
```
GET https://oda.ft.dk/api/SagAktør(12345)
```

### Expanded Queries

#### Get relationships with full case and actor details
```
GET https://oda.ft.dk/api/SagAktør?%24expand=Sag,Aktør,SagAktørRolle
```

#### Find all actors involved in a specific case
```
GET https://oda.ft.dk/api/SagAktør?%24filter=sagid eq 45678&%24expand=Aktør,SagAktørRolle
```

#### Find all cases for a specific politician
```
GET https://oda.ft.dk/api/SagAktør?%24filter=aktørid eq 98765&%24expand=Sag,SagAktørRolle
```

#### Filter by role type (e.g., only proposers)
```
GET https://oda.ft.dk/api/SagAktør?%24filter=rolleid eq 1&%24expand=Sag,Aktør
```

### Advanced Analysis Queries

#### Find all cases where a politician was the proposer
```
GET https://oda.ft.dk/api/SagAktør?%24filter=aktørid eq 98765 and rolleid eq 1&%24expand=Sag
```

#### Get recent involvement (last 6 months)
```
GET https://oda.ft.dk/api/SagAktør?%24filter=opdateringsdato gt 2024-06-01T00:00:00&%24expand=Sag,Aktør,SagAktørRolle
```

#### Count involvement by actor
```
GET https://oda.ft.dk/api/SagAktør?%24filter=aktørid eq 98765&%24count=true
```

## Practical Use Cases

### Political Analysis

1. **Participation Tracking**: Monitor how active specific politicians are in proposing or supporting legislation
2. **Cross-Party Collaboration**: Identify cases where actors from different parties collaborate
3. **Committee Workload**: Analyze the distribution of cases across different committees
4. **Ministerial Responsibility**: Track which ministers are responsible for which policy areas

### Research Applications

1. **Legislative Networks**: Map relationships between actors through shared case involvement
2. **Policy Influence**: Identify key players in specific policy domains
3. **Political Careers**: Track how politicians' involvement patterns change over time
4. **Institutional Analysis**: Study how different types of actors (individuals, committees, ministries) interact

### Data Journalism

1. **Political Accountability**: Track politician involvement in campaign promises
2. **Influence Mapping**: Identify who drives specific policy initiatives
3. **Committee Analysis**: Examine the effectiveness of parliamentary committees
4. **Timeline Analysis**: Follow the progression of involvement in long-running cases

## Important Considerations

### URL Encoding
Always use `%24` instead of `$` in OData parameters when making HTTP requests:
-  Correct: `%24filter=sagid eq 45678`
- L Incorrect: `$filter=sagid eq 45678`

### Data Quality
- The `opdateringsdato` field indicates when the relationship was last modified
- Some historical relationships may have incomplete role information
- Cross-reference with the main Sag and Aktør entities for complete context

### Performance Tips
- Use `$select` to limit fields when you don't need all relationship details
- Consider pagination for large result sets
- Expand related entities selectively to avoid large payloads

## Response Example

```json
{
  "value": [
    {
      "id": 12345,
      "sagid": 45678,
      "aktørid": 98765,
      "rolleid": 1,
      "opdateringsdato": "2024-01-15T10:30:00",
      "Sag": {
        "id": 45678,
        "titel": "Forslag til lov om...",
        "typeid": 3,
        "statusid": 4
      },
      "Aktør": {
        "id": 98765,
        "navn": "Jane Doe",
        "typeid": 5
      },
      "SagAktørRolle": {
        "id": 1,
        "rolle": "Forslagsstiller"
      }
    }
  ]
}
```

## Error Handling

Common issues when working with SagAktør:

- **404 Not Found**: Relationship ID doesn't exist
- **Invalid Filter**: Check foreign key references exist
- **Encoding Issues**: Ensure proper URL encoding of OData parameters

## Related Documentation

- [Sag Entity](../core/sag.md) - Parliamentary cases
- [Aktør Entity](../core/aktor.md) - Political actors
- [Entity Relationships](../../../data-model/entity-relationships.md) - Complete relationship mapping
- [Junction Tables Overview](index.md) - All junction table entities