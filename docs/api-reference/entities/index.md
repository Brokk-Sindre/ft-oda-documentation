# API Reference - Entities

## Overview

Entities are the core data structures in the Danish Parliament's Open Data API (ODA). Each entity represents a specific type of parliamentary information, from legislative cases and voting records to actors and documents. The API provides access to **50 distinct entity types** that together form a comprehensive model of Denmark's parliamentary processes.

All entities are accessible via the base URL pattern: `https://oda.ft.dk/api/[EntityName]`

## Entity Categories

The 50 entities are organized into logical categories based on their role in the parliamentary system:

### Core Parliamentary Entities

These are the primary entities that represent the fundamental elements of legislative work:

| Entity | Danish Name | Description | Records |
|--------|-------------|-------------|---------|
| [Sag](core/sag.md) | Sag | Legislative cases and proceedings | 96,538+ |
| [Aktør](core/aktor.md) | Aktør | Politicians, ministers, and other parliamentary actors | 18,139+ |
| [Afstemning](core/afstemning.md) | Afstemning | Voting sessions and results | 15,000+ |
| [Stemme](core/stemme.md) | Stemme | Individual votes cast by actors | 500,000+ |

### Document Management

Entities that handle parliamentary documents and files:

| Entity | Danish Name | Description |
|--------|-------------|-------------|
| [Dokument](documents/dokument.md) | Dokument | Parliamentary documents and publications |
| [Fil](documents/fil.md) | Fil | File attachments and downloads |
| Dokumentkategori | Dokumentkategori | Document category classifications |
| Dokumentstatus | Dokumentstatus | Document status tracking |
| Dokumenttype | Dokumenttype | Document type definitions |
| Omtryk | Omtryk | Document reprints and versions |

### Meeting Management

Entities that structure parliamentary meetings and agenda items:

| Entity | Danish Name | Description |
|--------|-------------|-------------|
| [Møde](meetings/mode.md) | Møde | Parliamentary meetings and sessions |
| Dagsordenspunkt | Dagsordenspunkt | Agenda items within meetings |
| Mødestatus | Mødestatus | Meeting status classifications |
| Mødetype | Mødetype | Types of parliamentary meetings |
| Debat | Debat | Debate records (EU/foreign affairs) |

### Legislative Process

Entities that track the progression of cases through parliament:

| Entity | Danish Name | Description |
|--------|-------------|-------------|
| Sagstrin | Sagstrin | Case steps/stages in legislative process |
| Sagstrinsstatus | Sagstrinsstatus | Status of case steps |
| Sagstrinstype | Sagstrinstype | Types of case steps |
| Forslag | Forslag | Proposals and amendments |
| Aktstykke | Aktstykke | Act pieces and legal documents |

### Classification Systems

Support entities that provide categorization and typing:

| Entity | Danish Name | Description |
|--------|-------------|-------------|
| Aktørtype | Aktørtype | Types of parliamentary actors |
| Afstemningstype | Afstemningstype | Types of voting procedures |
| Sagskategori | Sagskategori | Case category classifications |
| Sagsstatus | Sagsstatus | Case status tracking |
| Sagstype | Sagstype | Types of legislative cases |
| Stemmetype | Stemmetype | Vote type classifications |

### Relationship Tables (Junction Tables)

Entities that manage many-to-many relationships between core entities:

| Entity | Danish Name | Description |
|--------|-------------|-------------|
| [SagAktør](junction-tables/sag-aktor.md) | SagAktør | Case-Actor relationships |
| [DokumentAktør](junction-tables/dokument-aktor.md) | DokumentAktør | Document-Actor relationships |
| SagAktørRolle | SagAktørRolle | Roles in case-actor relationships |
| DokumentAktørRolle | DokumentAktørRolle | Roles in document-actor relationships |
| SagDokument | SagDokument | Case-Document relationships |
| SagDokumentRolle | SagDokumentRolle | Roles in case-document relationships |
| SagstrinAktør | SagstrinAktør | Case step-Actor relationships |
| SagstrinAktørRolle | SagstrinAktørRolle | Roles in case step-actor relationships |
| SagstrinDokument | SagstrinDokument | Case step-Document relationships |
| DagsordenspunktDokument | DagsordenspunktDokument | Agenda item-Document relationships |
| DagsordenspunktSag | DagsordenspunktSag | Agenda item-Case relationships |
| MødeAktør | MødeAktør | Meeting-Actor relationships |
| AktørAktør | AktørAktør | Actor-Actor relationships |
| AktørAktørRolle | AktørAktørRolle | Roles in actor-actor relationships |

### Keywords and Metadata

Entities for tagging, categorization, and system metadata:

| Entity | Danish Name | Description |
|--------|-------------|-------------|
| Emneord | Emneord | Keywords and topic tags |
| EmneordDokument | EmneordDokument | Keyword-Document relationships |
| EmneordSag | EmneordSag | Keyword-Case relationships |
| Emneordstype | Emneordstype | Keyword type classifications |
| Periode | Periode | Parliamentary periods and sessions |
| Almdel | Almdel | General parliamentary business |

### System Metadata

Technical entities that describe the API structure:

| Entity | Danish Name | Description |
|--------|-------------|-------------|
| EntitetBeskrivelse | EntitetBeskrivelse | Entity descriptions and metadata |
| KolloneBeskrivelse | KolloneBeskrivelse | Column descriptions for entities |

### Empty/Placeholder Entities

These entities exist in the schema but contain no data:

| Entity | Danish Name | Description | Status |
|--------|-------------|-------------|--------|
| [EUsag](empty-entities/eusag.md) | EUsag | EU cases | Empty (0 records) |
| [Sambehandlinger](empty-entities/sambehandlinger.md) | Sambehandlinger | Joint case treatments | Empty (0 records) |

## Common Entity Patterns

All entities in the ODA API follow consistent patterns:

### Standard Fields

Every entity includes these common fields:

- **id** (Int32): Unique identifier and primary key
- **opdateringsdato** (DateTime): Last update timestamp
- Type-specific fields for core data

### Relationship Fields

Foreign key fields follow the naming pattern `[entityname]id`:
- `sagid` - References Sag entity
- `aktørid` - References Aktør entity  
- `mødeid` - References Møde entity
- And so on...

### Navigation Properties

Entities support OData navigation properties for related data:
- Use `$expand` to include related entity data
- Supports up to 2 levels of expansion (e.g., `Sag/Aktør/Aktørtype`)
- Bidirectional relationships where applicable

## Key Relationships

The entities form several important relationship chains:

### Core Legislative Flow
**Sag**  **Sagstrin**  **Afstemning**  **Stemme**  **Aktør**

This represents how a case progresses through legislative steps, gets voted on, with individual votes cast by actors.

### Document Management Flow  
**Dokument**  **SagDokument**  **Sag**  **DokumentAktør**  **Aktør**

This shows how documents relate to cases and actors in the parliamentary process.

### Meeting Structure
**Møde**  **Dagsordenspunkt**  **DagsordenspunktSag**  **Sag**

This represents how meetings contain agenda items that reference specific cases.

### Actor Networks
**Aktør**  **AktørAktør**  **AktørAktørRolle**

This enables complex modeling of relationships between parliamentary actors.

## Usage Examples

### Basic Entity Access
```
https://oda.ft.dk/api/Sag
https://oda.ft.dk/api/Aktør
https://oda.ft.dk/api/Afstemning
```

### With Relationships
```
https://oda.ft.dk/api/Sag?%24expand=Aktør
https://oda.ft.dk/api/Afstemning?%24expand=Stemme/Aktør
```

### Filtered Access
```
https://oda.ft.dk/api/Sag?%24filter=typeid%20eq%201
https://oda.ft.dk/api/Aktør?%24filter=startswith(navn,'Lars')
```

## Performance Characteristics

Entity access performance varies by size:

- **Small entities** (d100 records): ~100-150ms
- **Medium entities** (1,000 records): ~300-500ms  
- **Large entities** (10,000+ records): ~2-3 seconds

For optimal performance, use:
- Pagination with `$top` and `$skip`
- Field selection with `$select`
- Strategic expansion with `$expand`

## Error Handling

Common entity-related errors:

- **404 Not Found**: Invalid entity name or ID
- **400 Bad Request**: Malformed OData query
- **200 OK with empty result**: Valid query with no matches

**Important**: Invalid field names in filters return all data instead of errors. Always validate field names against entity schemas.

## Next Steps

- Browse individual [entity documentation](core/sag.md) for detailed field schemas
- Learn about [OData operations](../odata/index.md) for querying entities
- Explore [relationship patterns](../odata/expansion.md) for complex data access
- Review [performance guidelines](../performance/index.md) for production usage