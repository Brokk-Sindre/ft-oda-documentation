# Entity Relationships

This document provides a comprehensive overview of all entity relationships in the Danish Parliament API. The API contains 50+ entities that model the complete parliamentary process from bill introduction to final voting.

## Overview

The Danish Parliament API models one of the world's most complex parliamentary systems through a rich relational structure. The data model captures:

- **Core Parliamentary Process**: Cases (Sag), Documents (Dokument), Meetings (Møde)
- **Democratic Participation**: Actors (Aktør), Voting Sessions (Afstemning), Individual Votes (Stemme)
- **Complex Relationships**: Junction tables modeling many-to-many relationships with semantic roles
- **Process Tracking**: Step-by-step progression through parliamentary procedures

## Entity Categories

### Core Entities

These entities represent the primary objects in the parliamentary system:

| Entity | Count | Description |
|--------|-------|-------------|
| **Sag** | 96,538+ | Cases - legislative bills, proposals, and parliamentary matters |
| **Aktør** | 18,139+ | Actors - politicians, committees, ministries, organizations |
| **Dokument** | Thousands | Documents - proposals, reports, statements, correspondence |
| **Møde** | Thousands | Meetings - parliamentary sessions and committee meetings |
| **Afstemning** | Thousands | Voting sessions - formal votes on cases and amendments |
| **Stemme** | Millions | Individual votes - how each politician voted |

### Junction Entities

These entities model complex many-to-many relationships with semantic meaning:

| Junction Entity | Purpose | Role Types |
|-----------------|---------|-----------|
| **SagAktør** | Case-Actor relationships | 23 role types |
| **DokumentAktør** | Document-Actor relationships | 25 role types |
| **SagDokument** | Case-Document relationships | Multiple roles |
| **SagstrinAktør** | Case Step-Actor relationships | Process roles |
| **MødeAktør** | Meeting-Actor relationships | Participation roles |

### Classification Entities

These entities provide type and status classifications:

| Classification Entity | Count | Purpose |
|----------------------|-------|----------|
| **Sagsstatus** | 68 | Case lifecycle status tracking |
| **Aktørtype** | 13 | Actor classification (Person, Committee, Ministry, etc.) |
| **Sagstype** | 13 | Case type classification |
| **Dokumenttype** | 28 | Document type classification |
| **Stemmetype** | 4 | Vote type (For, Against, Absent, Abstain) |
| **Afstemningstype** | 4 | Voting session type |

### Supporting Entities

Supporting entities that provide additional context and structure:

- **Periode** - Parliamentary periods/sessions
- **Sagstrin** - Case steps in the legislative process
- **Dagsordenspunkt** - Agenda items for meetings
- **Emneord** - Keywords and topics
- **Fil** - File attachments

## Relationship Patterns

### 1. Core Process Flow

```mermaid
graph TD
    A[Sag<br/>Case] --> B[SagDokument<br/>Case-Document]
    B --> C[Dokument<br/>Document]
    
    A --> D[Sagstrin<br/>Case Step]
    D --> E[SagstrinDokument<br/>Step-Document]
    E --> C
    
    A --> F[Afstemning<br/>Voting Session]
    F --> G[Stemme<br/>Individual Vote]
    G --> H[Aktør<br/>Actor/Person]
    
    A --> I[SagAktør<br/>Case-Actor]
    I --> H
```

### 2. Actor Participation Network

```mermaid
graph LR
    A[Aktør<br/>Actor] --> B[SagAktør<br/>Case Participation]
    A --> C[DokumentAktør<br/>Document Participation]
    A --> D[MødeAktør<br/>Meeting Participation]
    A --> E[SagstrinAktør<br/>Process Participation]
    A --> F[Stemme<br/>Voting Record]
    
    B --> G[Sag<br/>Case]
    C --> H[Dokument<br/>Document]
    D --> I[Møde<br/>Meeting]
    E --> J[Sagstrin<br/>Case Step]
    F --> K[Afstemning<br/>Voting Session]
```

### 3. Document Flow Architecture

```mermaid
graph TB
    A[Dokument<br/>Document] --> B[DokumentAktør<br/>Document-Actor<br/>25 Role Types]
    A --> C[SagDokument<br/>Case-Document]
    A --> D[SagstrinDokument<br/>Step-Document]
    A --> E[DagsordenspunktDokument<br/>Agenda-Document]
    A --> F[EmneordDokument<br/>Keyword-Document]
    A --> G[Fil<br/>File Attachment]
    
    B --> H[Aktør<br/>Actor]
    C --> I[Sag<br/>Case]
    D --> J[Sagstrin<br/>Case Step]
    E --> K[Dagsordenspunkt<br/>Agenda Item]
    F --> L[Emneord<br/>Keyword]
```

### 4. Complete Parliamentary System Overview

```mermaid
flowchart TD
    %% Core Parliamentary Process
    subgraph "Core Process"
        Sag[📄 Sag<br/>Cases<br/>96,538+]
        Dokument[📋 Dokument<br/>Documents<br/>Thousands]
        Møde[🏛️ Møde<br/>Meetings<br/>Thousands]
        Afstemning[🗳️ Afstemning<br/>Voting Sessions<br/>Thousands]
        Stemme[✅ Stemme<br/>Individual Votes<br/>Millions]
        Aktør[👤 Aktør<br/>Actors<br/>18,139+]
    end
    
    %% Junction Tables
    subgraph "Relationships"
        SagAktør[🔗 SagAktør<br/>Case-Actor<br/>23 Roles]
        DokumentAktør[🔗 DokumentAktør<br/>Doc-Actor<br/>25 Roles]
        SagDokument[🔗 SagDokument<br/>Case-Document]
        SagstrinAktør[🔗 SagstrinAktør<br/>Step-Actor]
        MødeAktør[🔗 MødeAktør<br/>Meeting-Actor]
    end
    
    %% Process Flow
    subgraph "Legislative Process"
        Sagstrin[⚖️ Sagstrin<br/>Case Steps]
        Dagsordenspunkt[📋 Dagsordenspunkt<br/>Agenda Items]
        Periode[📅 Periode<br/>Parliamentary Periods]
    end
    
    %% Classifications
    subgraph "Classifications"
        Sagsstatus[📊 Sagsstatus<br/>68 Status Types]
        Aktørtype[🏷️ Aktørtype<br/>13 Actor Types]
        Sagstype[🏷️ Sagstype<br/>13 Case Types]
        Dokumenttype[🏷️ Dokumenttype<br/>28 Doc Types]
        Stemmetype[🏷️ Stemmetype<br/>4 Vote Types]
    end
    
    %% Connections
    Sag --> SagAktør --> Aktør
    Dokument --> DokumentAktør --> Aktør
    Sag --> SagDokument --> Dokument
    Sag --> Sagstrin --> SagstrinAktør --> Aktør
    Møde --> MødeAktør --> Aktør
    Afstemning --> Stemme --> Aktør
    Møde --> Dagsordenspunkt
    Sag --> Afstemning
    
    %% Classifications
    Sag -.-> Sagsstatus
    Sag -.-> Sagstype
    Aktør -.-> Aktørtype
    Dokument -.-> Dokumenttype
    Stemme -.-> Stemmetype
```

### 5. Junction Table Role Systems

```mermaid
graph TB
    subgraph "Case-Actor Relationships (23 Roles)"
        SagAktør2[SagAktør Junction]
        SagAktør2 --> R1[Minister]
        SagAktør2 --> R2[Spørger/Questioner]
        SagAktør2 --> R3[Forslagsstiller/Proposer]
        SagAktør2 --> R4[Ordfører/Speaker]
        SagAktør2 --> R5[Udvalgsordfører]
        SagAktør2 --> R6[... 18 more roles]
    end
    
    subgraph "Document-Actor Relationships (25 Roles)"
        DokumentAktør2[DokumentAktør Junction]
        DokumentAktør2 --> D1[Afsender/Sender]
        DokumentAktør2 --> D2[Modtager/Recipient]
        DokumentAktør2 --> D3[Stiller/Submitter]
        DokumentAktør2 --> D4[Underskriver/Signatory]
        DokumentAktør2 --> D5[Redaktør/Editor]
        DokumentAktør2 --> D6[... 20 more roles]
    end
    
    subgraph "Meeting-Actor Relationships"
        MødeAktør2[MødeAktør Junction]
        MødeAktør2 --> M1[Ordstyrer/Chairperson]
        MødeAktør2 --> M2[Deltager/Participant]
        MødeAktør2 --> M3[Referent/Secretary]
        MødeAktør2 --> M4[Observatør/Observer]
    end
```

## Complete Entity List

### All 50+ Entities

1. **Afstemning** - Voting sessions
2. **Afstemningstype** - Voting session types
3. **Aktstykke** - Act pieces (special administrative cases)
4. **Aktør** - Actors (people, organizations, committees)
5. **AktørAktør** - Actor-to-actor relationships
6. **AktørAktørRolle** - Actor-to-actor relationship roles
7. **Aktørtype** - Actor classification types
8. **Almdel** - General affairs cases
9. **Dagsordenspunkt** - Meeting agenda items
10. **DagsordenspunktDokument** - Agenda item to document mapping
11. **DagsordenspunktSag** - Agenda item to case mapping
12. **Debat** - Parliamentary debates
13. **Dokument** - Documents of all types
14. **DokumentAktør** - Document to actor relationships
15. **DokumentAktørRolle** - Document-actor relationship roles
16. **Dokumentkategori** - Document categories
17. **Dokumentstatus** - Document status lifecycle
18. **Dokumenttype** - Document type classification
19. **Emneord** - Keywords and topics
20. **EmneordDokument** - Keyword to document mapping
21. **EmneordSag** - Keyword to case mapping
22. **Emneordstype** - Keyword type classification
23. **EntitetBeskrivelse** - Entity descriptions (metadata)
24. **EUsag** - EU-related cases (dormant)
25. **Fil** - File attachments
26. **Forslag** - Formal proposals
27. **KolloneBeskrivelse** - Column descriptions (metadata)
28. **Møde** - Parliamentary and committee meetings
29. **MødeAktør** - Meeting participation
30. **Mødestatus** - Meeting status
31. **Mødetype** - Meeting type classification
32. **Omtryk** - Reprints and corrections
33. **Periode** - Parliamentary periods/sessions
34. **Sag** - Cases (bills, proposals, matters)
35. **SagAktør** - Case to actor relationships
36. **SagAktørRolle** - Case-actor relationship roles
37. **SagDokument** - Case to document relationships
38. **SagDokumentRolle** - Case-document relationship roles
39. **Sagskategori** - Case categories
40. **Sagsstatus** - Case status (68 detailed statuses)
41. **Sagstrin** - Case steps in the legislative process
42. **SagstrinAktør** - Case step actor participation
43. **SagstrinAktørRolle** - Case step actor roles
44. **SagstrinDokument** - Case step documents
45. **Sagstrinsstatus** - Case step status
46. **Sagstrinstype** - Case step types
47. **Sagstype** - Case type classification
48. **Sambehandlinger** - Joint case treatments (non-functional)
49. **Stemme** - Individual voting records
50. **Stemmetype** - Vote types (For, Against, Absent, Abstain)

## Key Relationship Types

### 1. Participation Relationships

**SagAktør (Case-Actor Relationships)**
- Links cases to participating actors
- 23 different role types define the nature of participation
- Examples: Minister (Minister), Spørger (Questioner), Forslagsstiller (Proposer)

**DokumentAktør (Document-Actor Relationships)**  
- Links documents to participating actors
- 25 different role types define the relationship
- Examples: Afsender (Sender), Modtager (Recipient), Stiller (Submitter)

### 2. Process Flow Relationships

**SagDokument (Case-Document Relationships)**
- Links cases to their associated documents
- Tracks document flow through the legislative process
- Multiple documents per case at different stages

**Sagstrin (Case Steps)**
- Represents stages in the parliamentary process
- Links to SagstrinDokument for step-specific documents
- Links to SagstrinAktør for step-specific actor participation

### 3. Meeting and Voting Relationships

**Afstemning ø Stemme**
- One voting session contains multiple individual votes
- Each Stemme record shows how one actor voted

**Møde ø Dagsordenspunkt ø Cases/Documents**
- Meetings have agenda items
- Agenda items link to specific cases and documents

## Junction Table Patterns

### Pattern 1: Simple Junction
**Entity1** øø **JunctionTable** øø **Entity2**

Example: EmneordSag (Keyword-Case)
- Simple many-to-many relationship
- No additional semantic roles

### Pattern 2: Role-Based Junction  
**Entity1** øø **JunctionTable** øø **Entity2**
                     ø
               **RoleTable**

Example: SagAktør ø SagAktørRolle
- Junction table has `rolleid` field
- Role table provides semantic meaning
- Enables complex relationship modeling

### Pattern 3: Multi-Dimensional Junction
**Entity1** øø **JunctionTable** øø **Entity2**
                     ø              ø
               **RoleTable**   **StatusTable**

Example: SagstrinAktør ø SagstrinAktørRolle
- Multiple classification dimensions
- Rich semantic context for relationships

## Data Quality and Referential Integrity

### Foreign Key Relationships

The API maintains strict referential integrity:

- All junction tables properly link to parent entities
- Orphaned records are extremely rare
- Historical data preserved even when entities are updated

### Relationship Coverage

- **Complete Coverage**: All major parliamentary processes modeled
- **Historical Consistency**: Relationships maintained across 70+ years
- **Real-time Updates**: New relationships created as parliamentary work progresses

## Query Patterns for Relationships

### Expanding Related Data

```bash
# Get case with category information
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=5"

# Get voting session with individual votes
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme&%24top=1"

# Two-level expansion: votes with actor information  
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme/Aktør&%24top=1"
```

### Junction Table Queries

```bash
# Find all actors involved in a specific case
curl "https://oda.ft.dk/api/SagAktør?%24filter=sagid%20eq%20102903&%24expand=Aktør,SagAktørRolle"

# Find all documents by a specific actor
curl "https://oda.ft.dk/api/DokumentAktør?%24filter=aktørid%20eq%2012345&%24expand=Dokument,DokumentAktørRolle"
```

## Architecture Insights

### Why This Model Works

1. **Semantic Richness**: Role-based junction tables provide meaning beyond simple links
2. **Process Modeling**: Multi-step relationships track complex parliamentary procedures  
3. **Historical Preservation**: Immutable relationship records maintain historical accuracy
4. **Query Flexibility**: OData expansion enables efficient relationship traversal
5. **Real-world Complexity**: Models actual Danish parliamentary complexity without oversimplification

### Performance Considerations

- **Relationship Expansion**: Limited to 2 levels to maintain performance
- **Junction Table Size**: Some junction tables contain millions of records
- **Index Strategy**: Foreign key relationships are well-indexed for query performance
- **Pagination**: All relationship queries subject to 100-record limit

## Conclusion

The Danish Parliament API's entity relationship model represents one of the most sophisticated government data models in the world. Its combination of core entities, semantic junction tables, and comprehensive classification systems enables detailed analysis of democratic processes while maintaining data integrity and query performance.

The 50+ entity model captures the full complexity of parliamentary democracy, from individual citizen petitions to complex legislative procedures, making it an invaluable resource for researchers, journalists, and civic technology developers.