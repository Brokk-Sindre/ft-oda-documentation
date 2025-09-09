# Data Model

Comprehensive overview of the Danish Parliament API data structure, relationships, and classification systems. Understanding the data model is essential for effective API usage.

## Core Concepts

The Danish Parliament API represents the complete parliamentary ecosystem through interconnected entities:

### 📋 Parliamentary Entities
- **Sag** (Cases) - Legislative bills, proposals, and matters
- **Aktør** (Actors) - Politicians, committees, ministries
- **Afstemning** (Voting) - Parliamentary voting sessions
- **Møde** (Meetings) - Parliamentary and committee meetings
- **Dokument** (Documents) - Official parliamentary documents

### 🔗 Relationships
- Junction tables connect entities with semantic roles
- Role-based relationships define participation types
- Temporal relationships track changes over time
- Hierarchical structures represent organizational units

## Data Model Components

### 📜 [Entity Relationships](entity-relationships.md)
Visual diagrams and detailed explanations of how entities connect:
- Core entity relationships
- Junction table patterns
- Hierarchical structures
- Temporal relationships

### 📋 [Classification Systems](classification-systems/)
Standardized categorization used throughout the API:

- **[Actor Types](classification-systems/actor-types.md)** - 17 types including Person, Udvalg, Ministerium
- **[Case Types](classification-systems/case-types.md)** - 13 types from Lovforslag to Alm. del
- **[Case Status](classification-systems/case-status.md)** - 68 different status codes
- **[Vote Types](classification-systems/vote-types.md)** - For, Imod, Hverken for eller imod, Fravørende
- **[Document Types](classification-systems/document-types.md)** - Various document classifications

### 📁 [Role Systems](role-systems/)
Semantic roles defining relationships between entities:

- **[Case-Actor Roles](role-systems/case-actor-roles.md)** - 23 roles including Forslagsstiller, Minister
- **[Document-Actor Roles](role-systems/document-actor-roles.md)** - 25 roles including Afsender, Modtager
- **[Other Roles](role-systems/other-roles.md)** - Additional role types across the system

### 📋 [Parliamentary Process](parliamentary-process/)
How the data model represents Danish parliamentary procedures:

- **[Legislative Flow](parliamentary-process/legislative-flow.md)** - From proposal to law
- **[Committee System](parliamentary-process/committee-system.md)** - Committee structures and work
- **[Voting Procedures](parliamentary-process/voting-procedures.md)** - Voting types and processes

## Key Design Principles

### 1. Temporal Integrity
Every entity includes `opdateringsdato` for tracking changes:
```json
{
  "id": 102903,
  "titel": "Example Case",
  "opdateringsdato": "2025-09-09T17:49:11.87"
}
```

### 2. Semantic Relationships
Relationships carry meaning through role systems:
```
Sag --[Forslagsstiller]--> Aktør
     --[Minister]--> Aktør
     --[Udvalg]--> Aktør
```

### 3. Classification Consistency
Standardized type systems across all entities:
- Type IDs are consistent and never change
- Classifications are comprehensive and mutually exclusive
- Historical classifications are preserved

### 4. Open Data Principles
- All data is publicly accessible
- No authentication required
- Complete historical records preserved
- UTF-8 encoding throughout

## Understanding Junction Tables

Junction tables are the key to understanding relationships:

### Simple Junction Pattern
```
Entity1 <--> JunctionTable <--> Entity2
```
Example: `EmneordSag` connects keywords to cases

### Role-Based Junction Pattern
```
Entity1 <--> JunctionTable <--> Entity2
                  |
                Role
```
Example: `SagAktør` connects cases to actors with specific roles

## Data Volume and Scale

| Entity | Record Count | Update Frequency |
|--------|--------------|------------------|
| Sag | 96,538+ | Daily |
| Aktør | 18,139+ | Weekly |
| Dokument | Large | Daily |
| Afstemning | Thousands | During sessions |
| Stemme | Millions | During sessions |

## Historical Coverage

- **Start Date**: 1952 (varies by entity)
- **Coverage**: 74+ years of parliamentary history
- **Completeness**: More comprehensive from 1990s onward
- **Future Data**: Some entities contain scheduled future events

## Working with the Data Model

### Essential Queries

1. **Find all relationships for an entity**:
```bash
# All actors involved in a case
curl "https://oda.ft.dk/api/SagAktør?$filter=sagid eq 102903&$expand=Aktør,SagAktørRolle"
```

2. **Navigate hierarchies**:
```bash
# Committee members
curl "https://oda.ft.dk/api/Aktør?$filter=typeid eq 4&$expand=AktørAktør"
```

3. **Track temporal changes**:
```bash
# Recent updates
curl "https://oda.ft.dk/api/Sag?$filter=opdateringsdato gt datetime'2025-09-01'&$orderby=opdateringsdato desc"
```

## Best Practices

1. **Understand relationships before querying** - Review junction tables
2. **Use appropriate expansions** - Don't over-fetch data
3. **Leverage classifications** - Filter by type IDs for efficiency
4. **Respect temporal data** - Use opdateringsdato for change detection
5. **Handle Danish characters** - Ensure proper UTF-8 encoding

## Next Steps

- Explore **[Entity Relationships](entity-relationships.md)** for visual understanding
- Review **[Classification Systems](classification-systems/)** for data categorization
- Study **[Role Systems](role-systems/)** for relationship semantics
- Learn **[Parliamentary Process](parliamentary-process/)** for context