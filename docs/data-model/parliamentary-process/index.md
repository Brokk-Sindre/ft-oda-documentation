# Parliamentary Process Data Model

## Overview

The Danish Parliamentary Open Data API provides comprehensive access to the legislative process through a sophisticated data model that mirrors the actual parliamentary procedures of the Folketinget. This section introduces the core entities and relationships that enable tracking of legislation from initial proposal through final decision.

The parliamentary process data model captures the complete lifecycle of legislative activity, including case management, committee workflows, voting procedures, and document flow. With over **96,538 parliamentary cases** and extensive historical data dating back to 1995, the API enables detailed analysis of democratic processes.

## Core Process Entities

### Primary Legislative Entities

**Sag (Case)**
: The fundamental unit of parliamentary business, representing individual pieces of legislation, inquiries, administrative matters, and other parliamentary proceedings. Each case has:
- **Unique Identification**: Numerical ID and human-readable titles
- **Lifecycle Tracking**: Status progression from proposal to completion
- **Temporal Data**: Creation, modification, and decision timestamps
- **Categorization**: Types include Lovforslag (Bills), Beslutningsforslag (Resolutions), Forespørgsel (Inquiries)

**Sagstrin (Case Step)**
: Individual stages within a case's progression through parliament, providing granular tracking of the legislative process:
- **Sequential Processing**: Ordered steps from introduction to final decision
- **Status Management**: Current state tracking for each procedural stage
- **Actor Participation**: Who participates at each step through SagstrinAktør relationships

**Afstemning (Voting)**
: Formal voting sessions that determine the outcome of parliamentary decisions:
- **Decision Recording**: Vote counts, outcomes, and procedural details
- **Temporal Precision**: Date and time of voting sessions
- **Case Linkage**: Direct connection to the cases being decided

**Stemme (Individual Vote)**
: Individual voting records for each parliamentarian in formal votes:
- **Personal Accountability**: How each politician voted on specific issues
- **Vote Types**: For/Against/Abstain with detailed categorization
- **Historical Analysis**: Complete voting history enabling pattern analysis

## Legislative Process Flow

### 1. Case Initiation

The legislative process begins when a **Sag (Case)** is introduced to parliament. Cases are categorized by **Sagstype** with 13 distinct types:

- **Lovforslag** - Legislative bills proposing new laws
- **Beslutningsforslag** - Parliamentary resolutions
- **Forespørgsel** - Parliamentary inquiries to ministers
- **§ 20-spørgsmål** - Question time inquiries
- **Aktstykke** - Administrative matters requiring parliamentary approval

Each case is assigned a unique identifier and progresses through a defined workflow tracked via **Sagsstatus** (68 detailed status types).

### 2. Committee Processing

Cases are typically referred to parliamentary committees (**Udvalg**) for detailed examination:

**Committee Structure**
: Specialized committees handle different policy areas (Finance, Legal Affairs, Environment, etc.)

**Committee Workflow**
: Documents are reviewed, hearings conducted, and recommendations prepared for the full parliament

**Actor Participation**
: Committee members, ministers, and other stakeholders participate through **SagAktør** relationships with specific roles

### 3. Parliamentary Deliberation

**Møde (Meeting)** entities capture formal parliamentary sessions where cases are debated:

- **Structured Agenda**: **Dagsordenspunkt** (Agenda Items) organize session content
- **Document Integration**: **DagsordenspunktDokument** links relevant documents to agenda items
- **Case Discussion**: **DagsordenspunktSag** connects cases to agenda items

### 4. Voting and Decision

Formal decisions are recorded through the voting system:

**Vote Management**
: **Afstemning** entities capture voting sessions with outcomes and procedural details

**Individual Records**
: **Stemme** entities record how each parliamentarian voted, enabling accountability analysis

**Decision Implementation**
: Final case status reflects parliamentary decision (adopted, rejected, withdrawn, etc.)

## Committee System Integration

### Committee Structure

The Danish Parliament operates through a comprehensive committee system represented in the data model:

**Committee Types**
: Standing committees, special committees, and joint committees with the EU

**Membership Tracking**
: **MødeAktør** relationships track committee participation and attendance

**Workflow Integration**
: Cases flow through committees via **SagAktør** relationships specifying committee handling

### Committee Workflow Patterns

1. **Referral Phase**: Cases assigned to relevant committees based on subject matter
2. **Examination Phase**: Detailed review, hearings, and stakeholder consultation
3. **Reporting Phase**: Committee recommendations prepared for parliamentary consideration
4. **Decision Phase**: Parliament votes on committee recommendations

## Voting Procedures and Decision-Making

### Voting System Architecture

**Formal Votes**
: **Afstemning** entities capture official parliamentary votes with complete metadata:
- Vote timing and procedural context
- Vote counts (for/against/abstain)
- Connection to specific cases and case steps

**Individual Voting Records**
: **Stemme** entities provide granular voting data:
- Each parliamentarian's vote on each issue
- Vote type classification (7 distinct vote types)
- Historical voting pattern analysis capabilities

**Vote Types Available**
: The system tracks various vote categories including standard votes, procedural votes, and abstentions

### Decision-Making Process

Decisions flow through a structured process:

1. **Proposal Stage**: Initial case introduction and referral
2. **Committee Stage**: Detailed examination and recommendation
3. **Parliamentary Stage**: Debate and formal consideration
4. **Voting Stage**: Formal decision-making through recorded votes
5. **Implementation Stage**: Final status recording and follow-up

## Document Flow Through Legislative Process

### Document Architecture

**Dokument (Document)**
: Parliamentary documents are central to the legislative process:
- **Rich Metadata**: Document types, statuses, and categorization
- **Full-Text Content**: Complete document text when available
- **File Attachments**: **Fil** entities provide downloadable PDFs and other formats

**Document-Case Integration**
: **SagDokument** relationships connect documents to specific cases with role-based semantics

**Document-Actor Relationships**
: **DokumentAktør** connections specify who authored, received, or processed each document

### Document Workflow

Parliamentary documents follow a structured workflow:

1. **Creation**: Authors draft proposals, responses, or administrative documents
2. **Submission**: Documents formally submitted to parliamentary administration
3. **Distribution**: Documents distributed to relevant committees and stakeholders
4. **Processing**: Documents reviewed, amended, and processed through committees
5. **Archival**: Final documents archived with complete metadata and relationships

## Actor Roles and Responsibilities

### Role-Based Process Participation

The parliamentary process involves multiple types of actors with specific roles:

**Actor Types (13 categories)**
: Including politicians, committees, ministries, and external organizations

**Case Actor Roles (23 types)**
: Specific roles actors play in case processing:
- **Forslagsstiller** (Proposer) - Initiates legislation
- **Ordfører** (Spokesperson) - Committee representative
- **Minister** - Government representative
- **Taler** (Speaker) - Parliamentary speaker

**Document Actor Roles (25 types)**
: Communication and document handling roles:
- **Afsender** (Sender) - Document author
- **Modtager** (Recipient) - Document recipient
- **BCC** - Blind copy recipient

### Responsibility Patterns

Roles define specific responsibilities within the parliamentary process:

- **Legislative Initiative**: Who can propose legislation and under what circumstances
- **Review Authority**: Which committees and actors have review responsibilities
- **Decision Authority**: Who can make binding decisions at different process stages
- **Communication Flow**: How documents and information flow between actors

## Process Timing and Scheduling

### Temporal Patterns

Parliamentary processes follow structured timing patterns:

**Parliamentary Periods**
: **Periode** entities define parliamentary sessions with precise start/end dates

**Meeting Scheduling**
: **Møde** entities capture scheduled parliamentary sessions with advance planning

**Real-Time Updates**
: API data reflects current parliamentary activity with near real-time updates (within hours)

### Scheduling Analysis

The temporal data enables analysis of:

- **Processing Duration**: Time from case introduction to final decision
- **Committee Efficiency**: How quickly committees process referred cases
- **Seasonal Patterns**: Parliamentary activity patterns throughout the year
- **Workflow Bottlenecks**: Where cases experience delays in processing

## Navigation to Detailed Process Documentation

This overview provides the foundation for understanding the parliamentary process data model. Detailed documentation is available in the following sections:

### [Legislative Flow](legislative-flow.md)
Comprehensive guide to how legislation moves through the parliamentary system, from initial proposal through final enactment. Covers the complete case lifecycle with detailed process maps.

### [Committee System](committee-system.md)
Detailed examination of the parliamentary committee structure, including committee types, membership patterns, workflow processes, and inter-committee relationships.

### [Voting Procedures](voting-procedures.md)
Complete guide to parliamentary voting mechanisms, including vote types, procedures, recording systems, and analysis techniques for voting pattern research.

## Best Practices for Parliamentary Workflow Modeling

### Data Model Understanding

**Start with Core Entities**
: Focus on **Sag**, **Afstemning**, **Stemme**, and **Aktør** for 80% of analytical value

**Leverage Relationships**
: Use junction tables (SagAktør, DokumentAktør, etc.) to understand process participation

**Temporal Analysis**
: Utilize timestamp fields for process timing and efficiency analysis

### Query Optimization Patterns

**Expand Strategically**
: Use `$expand` to retrieve related data efficiently:
```
/api/Sag?$expand=SagAktør/Aktør&$filter=substringof('klima',titel)
```

**Filter Early**
: Apply filters before expansions to reduce processing overhead:
```
/api/Afstemning?$filter=year(opdateringsdato) eq 2025&$expand=Stemme/Aktør
```

**Select Appropriately**
: Use `$select` to retrieve only necessary fields for large datasets:
```
/api/Sag?$select=titel,sagsstatus,opdateringsdato&$orderby=opdateringsdato desc
```

### Process Analysis Techniques

**Case Flow Analysis**
: Track cases through their complete lifecycle using Sagstrin and status progression

**Actor Network Analysis**
: Analyze collaboration patterns through SagAktør and DokumentAktør relationships

**Temporal Trend Analysis**
: Use historical data to identify patterns in parliamentary activity and decision-making

**Voting Pattern Analysis**
: Combine Afstemning and Stemme data to analyze political alignment and voting behavior

### Performance Considerations

**Pagination Strategy**
: Use `$top` and `$skip` for large datasets (max 1,000 records per request recommended)

**Concurrent Processing**
: API supports concurrent requests for parallel data retrieval

**Change Detection**
: Use `opdateringsdato` timestamps for efficient change monitoring and data synchronization

The Danish Parliamentary API provides unprecedented access to democratic processes through a well-structured data model that enables sophisticated analysis of legislative activity, political behavior, and institutional effectiveness.