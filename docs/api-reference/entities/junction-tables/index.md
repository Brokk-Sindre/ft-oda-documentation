# Junction Tables

Junction tables in the Danish Parliament API model the complex many-to-many relationships that exist throughout the parliamentary system. These tables don't just link entitiesthey provide rich semantic context through role-based relationships that capture the precise nature of each connection.

## Overview

The Danish Parliament API uses sophisticated junction table patterns that go beyond simple many-to-many relationships. Most junction tables include role identifiers that link to separate role definition tables, creating a three-dimensional relationship model that captures:

1. **Which entities** are related
2. **How they are related** (through role semantics)
3. **When the relationship** was established or updated

## Junction Table Architecture

### Pattern 1: Simple Junction Tables
Direct many-to-many relationships without additional semantic context.

**Structure:** `Entity1Id` ï¿½ï¿½ `Junction Table` ï¿½ï¿½ `Entity2Id`

Examples:
- **EmneordSag** - Keywords to Cases
- **EmneordDokument** - Keywords to Documents  
- **DagsordenspunktSag** - Agenda Items to Cases
- **DagsordenspunktDokument** - Agenda Items to Documents

### Pattern 2: Role-Based Junction Tables
Many-to-many relationships with semantic roles defining the nature of the relationship.

**Structure:** `Entity1Id` ï¿½ï¿½ `Junction Table` ï¿½ï¿½ `Entity2Id`
                                    ï¿½
                               `Role Table`

Examples:
- **SagAktï¿½r** ï¿½ **SagAktï¿½rRolle** (23 role types)
- **DokumentAktï¿½r** ï¿½ **DokumentAktï¿½rRolle** (25 role types)
- **SagstrinAktï¿½r** ï¿½ **SagstrinAktï¿½rRolle**
- **Aktï¿½rAktï¿½r** ï¿½ **Aktï¿½rAktï¿½rRolle**

### Pattern 3: Multi-Dimensional Junction Tables
Complex relationships with multiple classification dimensions.

**Structure:** Multiple classification tables provide context for junction relationships.

Examples:
- **SagDokument** ï¿½ **SagDokumentRolle**
- **SagstrinDokument** (with case step context)

## Junction Table Pattern Visualizations

### Pattern 1 Visualization: Simple Junction Tables

```mermaid
graph TD
    A[Entity 1] <--> B[Junction Table]
    B <--> C[Entity 2]
    
    subgraph "Simple Junction Examples"
        D[Emneord<br/>Keywords] <--> E[EmneordSag<br/>Junction]
        E <--> F[Sag<br/>Cases]
        
        G[Emneord<br/>Keywords] <--> H[EmneordDokument<br/>Junction]  
        H <--> I[Dokument<br/>Documents]
        
        J[Dagsordenspunkt<br/>Agenda Items] <--> K[DagsordenspunktSag<br/>Junction]
        K <--> L[Sag<br/>Cases]
    end
    
    style E fill:#e3f2fd
    style H fill:#e3f2fd
    style K fill:#e3f2fd
```

### Pattern 2 Visualization: Role-Based Junction Tables

```mermaid
graph TD
    subgraph "Role-Based Junction Pattern"
        A[Entity 1] <--> B[Junction Table<br/>with Role ID]
        B <--> C[Entity 2]
        B -.-> D[Role Definition<br/>Table]
        
        D --> E[Role 1<br/>Semantic Meaning]
        D --> F[Role 2<br/>Semantic Meaning]
        D --> G[Role N<br/>Semantic Meaning]
    end
    
    subgraph "SagAktÃ¸r Example - 23 Roles"
        H[Sag<br/>Cases] <--> I[SagAktÃ¸r<br/>Junction + rolleid]
        I <--> J[AktÃ¸r<br/>Actors]
        I -.-> K[SagAktÃ¸rRolle<br/>23 Role Types]
        
        K --> L[Minister<br/>ID: 14]
        K --> M[Forslagsstiller<br/>Proposer ID: 19]
        K --> N[SpÃ¸rger<br/>Questioner ID: 10]
        K --> O[... 20 more roles]
    end
    
    subgraph "DokumentAktÃ¸r Example - 25 Roles"
        P[Dokument<br/>Documents] <--> Q[DokumentAktÃ¸r<br/>Junction + rolleid]
        Q <--> R[AktÃ¸r<br/>Actors]
        Q -.-> S[DokumentAktÃ¸rRolle<br/>25 Role Types]
        
        S --> T[Afsender<br/>Sender ID: 1]
        S --> U[Til<br/>To ID: 8]
        S --> V[Minister<br/>Minister ID: 5]
        S --> W[Besvaret af<br/>Answered by ID: 4]
        S --> X[... 21 more roles]
    end
    
    style I fill:#fff3e0
    style Q fill:#fff3e0
    style K fill:#e1f5fe
    style S fill:#e1f5fe
```

### Complete Junction Table Network

```mermaid
flowchart TD
    %% Core Entities
    subgraph "Core Entities"
        Sag[ð Sag<br/>Cases]
        AktÃ¸r[ð¤ AktÃ¸r<br/>Actors]
        Dokument[ð Dokument<br/>Documents]
        MÃ¸de[ðï¸ MÃ¸de<br/>Meetings]
        Sagstrin[âï¸ Sagstrin<br/>Case Steps]
        Emneord[ð·ï¸ Emneord<br/>Keywords]
        Dagsordenspunkt[ð Dagsordenspunkt<br/>Agenda Items]
    end
    
    %% Junction Tables
    subgraph "Junction Tables with Roles"
        SagAktÃ¸r[ð SagAktÃ¸r<br/>Case-Actor<br/>23 Roles]
        DokumentAktÃ¸r[ð DokumentAktÃ¸r<br/>Doc-Actor<br/>25 Roles]
        SagstrinAktÃ¸r[ð SagstrinAktÃ¸r<br/>Step-Actor<br/>Process Roles]
        MÃ¸deAktÃ¸r[ð MÃ¸deAktÃ¸r<br/>Meeting-Actor<br/>Participation Roles]
        AktÃ¸rAktÃ¸r[ð AktÃ¸rAktÃ¸r<br/>Actor-Actor<br/>Relationship Roles]
    end
    
    subgraph "Junction Tables without Roles"
        SagDokument[ð SagDokument<br/>Case-Document]
        SagstrinDokument[ð SagstrinDokument<br/>Step-Document]
        EmneordSag[ð EmneordSag<br/>Keyword-Case]
        EmneordDokument[ð EmneordDokument<br/>Keyword-Document]
        DagsordenspunktSag[ð DagsordenspunktSag<br/>Agenda-Case]
        DagsordenspunktDokument[ð DagsordenspunktDokument<br/>Agenda-Document]
    end
    
    %% Role Tables
    subgraph "Role Definition Tables"
        SagAktÃ¸rRolle[ð SagAktÃ¸rRolle<br/>Case-Actor Roles]
        DokumentAktÃ¸rRolle[ð DokumentAktÃ¸rRolle<br/>Doc-Actor Roles]
        SagstrinAktÃ¸rRolle[ð SagstrinAktÃ¸rRolle<br/>Step-Actor Roles]
        SagDokumentRolle[ð SagDokumentRolle<br/>Case-Doc Roles]
        AktÃ¸rAktÃ¸rRolle[ð AktÃ¸rAktÃ¸rRolle<br/>Actor-Actor Roles]
    end
    
    %% Core Entity Connections
    Sag <--> SagAktÃ¸r <--> AktÃ¸r
    Dokument <--> DokumentAktÃ¸r <--> AktÃ¸r
    Sagstrin <--> SagstrinAktÃ¸r <--> AktÃ¸r
    MÃ¸de <--> MÃ¸deAktÃ¸r <--> AktÃ¸r
    AktÃ¸r <--> AktÃ¸rAktÃ¸r <--> AktÃ¸r
    
    Sag <--> SagDokument <--> Dokument
    Sagstrin <--> SagstrinDokument <--> Dokument
    
    Emneord <--> EmneordSag <--> Sag
    Emneord <--> EmneordDokument <--> Dokument
    
    Dagsordenspunkt <--> DagsordenspunktSag <--> Sag
    Dagsordenspunkt <--> DagsordenspunktDokument <--> Dokument
    
    %% Role Connections
    SagAktÃ¸r -.-> SagAktÃ¸rRolle
    DokumentAktÃ¸r -.-> DokumentAktÃ¸rRolle
    SagstrinAktÃ¸r -.-> SagstrinAktÃ¸rRolle
    SagDokument -.-> SagDokumentRolle
    AktÃ¸rAktÃ¸r -.-> AktÃ¸rAktÃ¸rRolle
    
    %% Styling
    style SagAktÃ¸r fill:#fff3e0
    style DokumentAktÃ¸r fill:#fff3e0
    style SagstrinAktÃ¸r fill:#fff3e0
    style MÃ¸deAktÃ¸r fill:#fff3e0
    style AktÃ¸rAktÃ¸r fill:#fff3e0
    
    style SagDokument fill:#e3f2fd
    style SagstrinDokument fill:#e3f2fd
    style EmneordSag fill:#e3f2fd
    style EmneordDokument fill:#e3f2fd
    style DagsordenspunktSag fill:#e3f2fd
    style DagsordenspunktDokument fill:#e3f2fd
    
    style SagAktÃ¸rRolle fill:#e1f5fe
    style DokumentAktÃ¸rRolle fill:#e1f5fe
    style SagstrinAktÃ¸rRolle fill:#e1f5fe
    style SagDokumentRolle fill:#e1f5fe
    style AktÃ¸rAktÃ¸rRolle fill:#e1f5fe
```

## Key Junction Tables

### 1. SagAktï¿½r (Case-Actor Relationships)

**Purpose:** Links cases to participating actors with semantic roles  
**Scale:** Millions of relationships across parliamentary history  
**Role System:** 23 distinct role types via SagAktï¿½rRolle

**Key Fields:**
- `id` - Unique relationship identifier
- `sagid` - References Sag entity
- `aktï¿½rid` - References Aktï¿½r entity
- `rolleid` - References SagAktï¿½rRolle entity
- `opdateringsdato` - Last update timestamp

**Common Roles:**
- Minister (ID 14) - Government minister responsible
- Forslagsstiller (ID 19) - Proposer of legislation
- Spï¿½rger (ID 10) - Questioner in parliamentary inquiries
- Henvist til (ID 11) - Committee or body referred to

**Query Example:**
```bash
# Find all actors involved in a specific case
curl "https://oda.ft.dk/api/SagAktï¿½r?%24filter=sagid%20eq%20102903&%24expand=Aktï¿½r,SagAktï¿½rRolle"
```

### 2. DokumentAktï¿½r (Document-Actor Relationships)

**Purpose:** Links documents to participating actors with communication roles  
**Scale:** Extensive coverage of all parliamentary documents  
**Role System:** 25 distinct role types via DokumentAktï¿½rRolle

**Key Fields:**
- `id` - Unique relationship identifier
- `dokumentid` - References Dokument entity
- `aktï¿½rid` - References Aktï¿½r entity
- `rolleid` - References DokumentAktï¿½rRolle entity
- `opdateringsdato` - Last update timestamp

**Common Roles:**
- Afsender (ID 1) - Document sender
- Til (ID 8) - Primary recipient
- Minister (ID 5) - Government minister involved
- Besvaret af (ID 4) - Who provided the answer
- Kopi til (ID 2) - Copy recipient

**Query Example:**
```bash
# Find all documents by a specific actor
curl "https://oda.ft.dk/api/DokumentAktï¿½r?%24filter=aktï¿½rid%20eq%2012345&%24expand=Dokument,DokumentAktï¿½rRolle"
```

### 3. SagDokument (Case-Document Relationships)

**Purpose:** Links cases to their associated documents  
**Scale:** Multiple documents per case across legislative process  
**Role System:** SagDokumentRolle provides document function context

**Key Fields:**
- `id` - Unique relationship identifier
- `sagid` - References Sag entity
- `dokumentid` - References Dokument entity
- `rolleid` - References SagDokumentRolle entity
- `opdateringsdato` - Last update timestamp

**Query Example:**
```bash
# Find all documents for a specific case
curl "https://oda.ft.dk/api/SagDokument?%24filter=sagid%20eq%20102903&%24expand=Dokument,SagDokumentRolle"
```

## Performance Considerations

### Indexing Strategy
- Junction tables are well-indexed on foreign key relationships
- Role-based queries are optimized for common role types
- Compound indexes support multi-field filtering

### Query Optimization Tips
1. **Use specific filters** - Junction tables can be very large
2. **Limit expansions** - Avoid expanding large related entities unnecessarily
3. **Use pagination** - All junction queries subject to 100-record limit
4. **Filter by role** - Role-based filtering is well-optimized

## Conclusion

The junction table system in the Danish Parliament API represents one of the most sophisticated relationship modeling systems in any government API. The combination of simple junction tables for basic relationships and role-based junction tables for complex semantic relationships enables:

- **Precise relationship semantics** through role-based modeling
- **Complete process transparency** via comprehensive relationship tracking  
- **Flexible querying** supporting both simple and complex analytical needs
- **Historical preservation** maintaining relationship integrity across decades
- **Real-time currency** with immediate updates as parliamentary work progresses

This junction table architecture makes the Danish Parliament API invaluable for researchers studying democratic processes, network analysis of political relationships, and detailed tracking of legislative workflows.