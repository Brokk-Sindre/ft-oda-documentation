# Document-Actor Role System (DokumentAktørRolle)

The DokumentAktørRolle system defines the semantic relationships between documents (Dokument) and actors (Aktør) in the Danish Parliament. This comprehensive role system captures every aspect of document creation, distribution, and interaction within the parliamentary process.

## Overview

The DokumentAktør junction table connects documents to actors, with the specific nature of the relationship defined by the DokumentAktørRolle entity. This system models the complex communication patterns and document workflows that drive parliamentary democracy.

**Key Statistics:**
- **25 distinct role types** covering all document-actor interactions
- **Comprehensive coverage** of parliamentary communication workflows
- **Historical consistency** across decades of parliamentary documentation

## Complete DokumentAktørRolle Reference

### 1. Afsender (Sender)
**Danish:** Afsender  
**English:** Sender  
**Context:** Actor who sends or originates the document  
**Usage:** Primary attribution for document creation and transmission  
**Note:** Appears twice in API (IDs 1 and 14) - may indicate different sender contexts  

### 2. Kopi til (Copy To)
**Danish:** Kopi til  
**English:** Copy to  
**Context:** Actor receives a copy of the document for information  
**Usage:** Tracks document distribution for transparency and information sharing  
**Note:** Appears twice in API (IDs 2 and 15) - may indicate different copy contexts  

### 3. Stiller/MFU
**Danish:** Stiller/MFU  
**English:** Submitter/MFU (Miljø- og Fødevareudvalget)  
**Context:** Specialized role for Environment and Food Committee submissions  
**Usage:** Committee-specific document submission role  

### 4. Besvaret af (Answered By)
**Danish:** Besvaret af  
**English:** Answered by  
**Context:** Actor who provides official response to document/inquiry  
**Usage:** Links questions to their official answers - crucial for accountability tracking  

### 5. Minister
**Danish:** Minister  
**English:** Minister  
**Context:** Government minister associated with the document  
**Usage:** Links documents to responsible government ministers for accountability  

### 6. Spørger (Questioner)
**Danish:** Spørger  
**English:** Questioner  
**Context:** Actor who asks questions in the document  
**Usage:** Essential for parliamentary question-answer tracking  

### 7. Medspørger (Co-questioner)
**Danish:** Medspørger  
**English:** Co-questioner  
**Context:** Additional questioner supporting the primary questioner  
**Usage:** Tracks collaborative questioning in parliamentary inquiries  

### 8. Til (To)
**Danish:** Til  
**English:** To  
**Context:** Primary recipient of the document  
**Usage:** Direct addressing in parliamentary correspondence  

### 9. Ministerområde (Ministry Area)
**Danish:** Ministerområde  
**English:** Ministry area  
**Context:** Document relates to this ministry's area of responsibility  
**Usage:** Links documents to government department jurisdiction  

### 10. Adressat (Addressee)
**Danish:** Adressat  
**English:** Addressee  
**Context:** Formal addressee of official communications  
**Usage:** Official recipient designation in formal parliamentary documents  

### 11. Modtager (Recipient)
**Danish:** Modtager  
**English:** Recipient  
**Context:** Actor who receives the document  
**Usage:** General recipient role for document distribution tracking  

### 12. Stiller (Submitter)
**Danish:** Stiller  
**English:** Submitter  
**Context:** Actor who formally submits the document  
**Usage:** Attribution for document submission in parliamentary procedures  

### 13. Relevant for (Relevant For)
**Danish:** Relevant for  
**English:** Relevant for  
**Context:** Document is relevant to this actor's interests or responsibilities  
**Usage:** Broad relevance tagging for interested parties  

### 16. Afgivet af (Submitted By)
**Danish:** Afgivet af  
**English:** Submitted by  
**Context:** Actor who formally submits or delivers the document  
**Usage:** Formal submission attribution in parliamentary processes  

### 17. BCC (Blind Carbon Copy)
**Danish:** BCC  
**English:** Blind Carbon Copy  
**Context:** Actor receives blind copy - other recipients unaware  
**Usage:** Confidential document distribution tracking  

### 18. Kontakt (Contact)
**Danish:** Kontakt  
**English:** Contact  
**Context:** Actor serves as contact person for the document  
**Usage:** Designated contact for follow-up or inquiries about the document  

### 19. Deltager (Participant)
**Danish:** Deltager  
**English:** Participant  
**Context:** Actor participates in document creation or process  
**Usage:** Collaborative document development and participation tracking  

### 20. Behandles i (Processed In)
**Danish:** Behandles i  
**English:** Processed in  
**Context:** Document is processed or considered by this committee/body  
**Usage:** Committee workflow and document processing tracking  

### 21. Forslagsstiller (Proposer)
**Danish:** Forslagsstiller  
**English:** Proposer  
**Context:** Actor who proposes or initiates the document/proposal  
**Usage:** Primary attribution for legislative and policy proposals  

### 22. Ordfører for forslagsstillerne (Spokesperson for Proposers)
**Danish:** Ordfører for forslagsstillerne  
**English:** Spokesperson for proposers  
**Context:** Designated spokesperson representing all document proposers  
**Usage:** Key communication role for multi-party proposals  

### 23. Ordfører for forespørgerne (Spokesperson for Inquirers)
**Danish:** Ordfører for forespørgerne  
**English:** Spokesperson for inquirers  
**Context:** Representative voice for multiple inquiring parties  
**Usage:** Coordinated inquiry representation in parliamentary questions  

### 24. Ordfører (Spokesperson)
**Danish:** Ordfører  
**English:** Spokesperson  
**Context:** General spokesperson role for the document  
**Usage:** Primary representative voice for document content or position  

### 25. Taler (Speaker)
**Danish:** Taler  
**English:** Speaker  
**Context:** Actor who speaks about or presents the document content  
**Usage:** Links documents to their verbal presentation in parliamentary proceedings  

## Role Categories

### Communication Roles
- **Afsender** - Sender
- **Til** - To
- **Adressat** - Addressee
- **Modtager** - Recipient
- **Kopi til** - Copy to
- **BCC** - Blind Carbon Copy

### Submission Roles
- **Stiller** - Submitter
- **Stiller/MFU** - Committee-specific submitter
- **Afgivet af** - Submitted by
- **Forslagsstiller** - Proposer

### Response Roles
- **Spørger** - Questioner
- **Medspørger** - Co-questioner
- **Besvaret af** - Answered by

### Representation Roles
- **Ordfører** - Spokesperson
- **Ordfører for forslagsstillerne** - Spokesperson for proposers
- **Ordfører for forespørgerne** - Spokesperson for inquirers
- **Taler** - Speaker

### Administrative Roles
- **Minister** - Minister
- **Ministerområde** - Ministry area
- **Kontakt** - Contact
- **Behandles i** - Processed in

### Participation Roles
- **Deltager** - Participant
- **Relevant for** - Relevant for

## Document Workflow Patterns

### Question-Answer Flow

```mermaid
graph LR
    A[Spørger creates question] --> B[Document created]
    B --> C[Til Ministry/Minister]
    C --> D[Minister receives]
    D --> E[Besvaret af Minister]
    E --> F[Response document]
    F --> G[Kopi til original questioner]
```

### Legislative Proposal Flow

```mermaid
graph LR
    A[Forslagsstiller proposes] --> B[Document created]
    B --> C[Ordfører appointed]
    C --> D[Document distributed]
    D --> E[Kopi til stakeholders]
    E --> F[Behandles i committee]
```

### Committee Communication Flow

```mermaid
graph LR
    A[Stiller submits to committee] --> B[Document created]
    B --> C[Behandles i committee]
    C --> D[Committee processes]
    D --> E[Response/Report]
    E --> F[Afsender committee response]
```

## Usage Statistics and Patterns

### Most Common Roles

1. **Afsender** - Most frequent role - appears in nearly all documents
2. **Til** - Very common - primary recipient designation
3. **Minister** - Frequent in government-related documents
4. **Kopi til** - Common for information distribution
5. **Besvaret af** - Regular in question-answer documentation

### Role Combinations

Common multi-role patterns for single documents:
- **Spørger + Minister + Besvaret af** (Question-answer cycle)
- **Forslagsstiller + Ordfører + Kopi til** (Legislative proposal)
- **Afsender + Til + Kopi til** (Standard communication)

## Query Examples

### Find All Actors for a Specific Document

```bash
# Get all actor relationships for document ID 12345
curl "https://oda.ft.dk/api/DokumentAktør?%24filter=dokumentid%20eq%2012345&%24expand=Aktør,DokumentAktørRolle"
```

### Find Documents by Role Type

```bash
# Find all documents where someone is a "Minister"
curl "https://oda.ft.dk/api/DokumentAktør?%24filter=rolleid%20eq%205&%24expand=Dokument,Aktør"

# Find all documents with specific questioner
curl "https://oda.ft.dk/api/DokumentAktør?%24filter=rolleid%20eq%206%20and%20aktørid%20eq%2012345"
```

### Communication Pattern Analysis

```bash
# Find all documents sent to a specific ministry
curl "https://oda.ft.dk/api/DokumentAktør?%24filter=rolleid%20eq%208%20and%20aktørid%20eq%20[ministry_id]"

# Find all documents answered by a specific minister
curl "https://oda.ft.dk/api/DokumentAktør?%24filter=rolleid%20eq%204%20and%20aktørid%20eq%20[minister_id]"
```

## API Implementation Notes

### Role ID Mapping

The `rolleid` field in DokumentAktør maps to the `id` field in DokumentAktørRolle:

```json
{
  "id": 789012,
  "dokumentid": 54321,
  "aktørid": 12345,
  "rolleid": 5,  // Maps to Minister role
  "opdateringsdato": "2025-09-09T15:30:00"
}
```

### Duplicate Role IDs

Note that roles 1/14 (Afsender) and 2/15 (Kopi til) appear to be duplicates in the API. This may represent:
- Different contexts for the same semantic role
- Historical legacy from system evolution
- Functional distinction not apparent in role names

### Performance Optimization

```bash
# Efficient queries using specific role filters
curl "https://oda.ft.dk/api/DokumentAktør?%24filter=rolleid%20in%20(1,14)&%24select=dokumentid,aktørid"

# Avoid expansion on large result sets
curl "https://oda.ft.dk/api/DokumentAktør?%24top=100&%24select=dokumentid,aktørid,rolleid"
```

## Historical Analysis Applications

### Communication Network Analysis

The role system enables sophisticated analysis:

```bash
# Map minister-parliament communication patterns
curl "https://oda.ft.dk/api/DokumentAktør?%24filter=rolleid%20eq%205&%24expand=Aktør"

# Track parliamentary questioning patterns
curl "https://oda.ft.dk/api/DokumentAktør?%24filter=rolleid%20in%20(6,7)&%24expand=Aktør,Dokument"
```

### Democratic Accountability Tracking

```bash
# Find all ministerial responses
curl "https://oda.ft.dk/api/DokumentAktør?%24filter=rolleid%20eq%204&%24expand=Aktør,Dokument"

# Track government transparency via document distribution
curl "https://oda.ft.dk/api/DokumentAktør?%24filter=rolleid%20in%20(2,15)&%24expand=Dokument"
```

## Data Quality Considerations

### Relationship Completeness

- **High coverage**: Most documents have multiple role relationships
- **Historical consistency**: Role semantics maintained across time periods
- **Real-time updates**: New relationships created as documents are processed

### Role Usage Patterns

- **Mandatory roles**: Afsender appears in virtually all documents
- **Conditional roles**: Minister only for government-related documents
- **Collaborative roles**: Medspørger only when multiple questioners present

## Conclusion

The DokumentAktørRolle system with its 25 distinct roles represents the most comprehensive document-actor relationship model in any parliamentary API. It captures the full spectrum of parliamentary communication, from formal legislative proposals to informal information sharing.

This role system enables detailed analysis of:

- **Democratic communication patterns**
- **Government accountability mechanisms**
- **Parliamentary question-answer effectiveness** 
- **Information distribution transparency**
- **Collaborative legislative processes**
- **Committee workflow efficiency**

The granular nature of these roles makes the Danish Parliament API invaluable for researchers studying democratic transparency, government responsiveness, and parliamentary communication effectiveness. The system provides unprecedented insight into how democratic institutions actually communicate and interact in practice.