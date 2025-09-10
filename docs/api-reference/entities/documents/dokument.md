# Dokument (Document) Entity

The `Dokument` entity represents legislative and administrative documents in the Danish Parliament system. This includes all official documents produced during parliamentary work, from inquiries and statements to committee reports and legislative proposals.

## Overview

- **Entity Name**: `Dokument`
- **Endpoint**: `https://oda.ft.dk/api/Dokument`
- **Total Records**: Hundreds of thousands of documents
- **Primary Key**: `id` (Int32)
- **Document Coverage**: October 2013 onwards
- **File Links**: Contains links to PDF files on ft.dk

## Field Reference

### Core Identification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | Int32 | Primary key, unique document identifier | `1` |
| `titel` | String | Document title | `"Spm. om formuefordelingen fordelt på både indkomst- og formuefordelingen i perioden 1997-2012..."` |

### Classification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `typeid` | Int32 | Document type ID (foreign key to Dokumenttype) | `13` |
| `kategoriid` | Int32 | Document category ID (foreign key to Dokumentkategori) | `36` |
| `statusid` | Int32 | Document status ID (foreign key to Dokumentstatus) | `1` |
| `offentlighedskode` | String | Public access code | `"O"` |

### Date and Timeline Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `dato` | DateTime | Document date | `"2014-08-08T00:00:00"` |
| `modtagelsesdato` | DateTime | Receipt date (nullable) | `null` |
| `frigivelsesdato` | DateTime | Release date (nullable) | `"2014-08-08T14:57:26"` |
| `opdateringsdato` | DateTime | Last update timestamp | `"2016-03-14T09:32:33.387"` |

### Content and Structure Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `paragraf` | String | Paragraph reference | `""` |
| `paragrafnummer` | String | Paragraph number | `""` |
| `procedurenummer` | String | Procedure number | `""` |
| `grundnotatstatus` | String | Base note status | `""` |
| `dagsordenudgavenummer` | Int16 | Agenda edition number (nullable) | `null` |

### Question-Related Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `spørgsmålsordlyd` | String | Question wording (nullable) | `null` |
| `spørgsmålstitel` | String | Question title (nullable) | `null` |
| `spørgsmålsid` | Int32 | Question ID (nullable) | `null` |

## Document Types Reference

Common document types in the Danish Parliament system:

| Type ID | Type Name | Danish | Description |
|---------|-----------|---------|-------------|
| 1 | Report | Redegørelse | Official statements and reports |
| 2 | Deputy Letter | Stedfortræderbrev | Deputy appointment letters |
| 3 | Ministerial Statement | Ministerredegørelse | Statements from ministers |
| 4 | Act Document | Aktstykke | Legislative act documents |
| 5 | Inquiry | Forespørgsel | Parliamentary inquiries |
| 6 | EU Note | EU-note | European Union related notes |
| 7 | Presentation Speech | Fremstillelsestale | Presentation speeches |
| 8 | Minutes | Referat | Meeting minutes and transcripts |
| 9 | Chairman's Announcement | Formandsmeddelelse | Official announcements |
| 10 | Memo | Notat | Internal memos and notes |

## Common Query Examples

### Basic Queries

```bash
# Get latest 5 documents
curl "https://oda.ft.dk/api/Dokument?%24top=5&%24orderby=opdateringsdato%20desc"

# Get specific document by ID
curl "https://oda.ft.dk/api/Dokument(1)"

# Count total documents
curl "https://oda.ft.dk/api/Dokument?%24inlinecount=allpages&%24top=1"
```

### Filter by Document Type

```bash
# Inquiries only (type 5)
curl "https://oda.ft.dk/api/Dokument?%24filter=typeid%20eq%205&%24top=10"

# Ministerial statements (type 3)
curl "https://oda.ft.dk/api/Dokument?%24filter=typeid%20eq%203&%24top=10"

# EU notes (type 6)
curl "https://oda.ft.dk/api/Dokument?%24filter=typeid%20eq%206&%24top=10"
```

### Filter by Public Access

```bash
# Public documents only
curl "https://oda.ft.dk/api/Dokument?%24filter=offentlighedskode%20eq%20'O'&%24top=10"

# Documents with specific access codes
curl "https://oda.ft.dk/api/Dokument?%24filter=offentlighedskode%20ne%20null&%24top=10"
```

### Recent Document Activity

```bash
# Today's documents
curl "https://oda.ft.dk/api/Dokument?%24filter=opdateringsdato%20gt%20datetime'2025-09-09T00:00:00'&%24orderby=opdateringsdato%20desc"

# This week's documents
curl "https://oda.ft.dk/api/Dokument?%24filter=opdateringsdato%20gt%20datetime'2025-09-02T00:00:00'&%24orderby=opdateringsdato%20desc"

# Recently released documents
curl "https://oda.ft.dk/api/Dokument?%24filter=frigivelsesdato%20gt%20datetime'2025-09-01T00:00:00'&%24orderby=frigivelsesdato%20desc"
```

### Search by Content

```bash
# Search document titles
curl "https://oda.ft.dk/api/Dokument?%24filter=substringof('klimaaftale',titel)&%24top=10"

# Documents with questions
curl "https://oda.ft.dk/api/Dokument?%24filter=spørgsmålstitel%20ne%20null&%24top=10"

# Documents with procedure numbers
curl "https://oda.ft.dk/api/Dokument?%24filter=procedurenummer%20ne%20''&%24top=10"
```

### Field Selection

```bash
# Essential fields only
curl "https://oda.ft.dk/api/Dokument?%24select=id,titel,dato,typeid,opdateringsdato&%24top=10"

# Question-related fields
curl "https://oda.ft.dk/api/Dokument?%24select=titel,spørgsmålstitel,spørgsmålsordlyd&%24filter=spørgsmålstitel%20ne%20null&%24top=5"

# Date information only
curl "https://oda.ft.dk/api/Dokument?%24select=id,titel,dato,frigivelsesdato,opdateringsdato&%24top=10"
```

## Relationship Expansion

### Document Classification

```bash
# Document with type information
curl "https://oda.ft.dk/api/Dokument?%24expand=Dokumenttype&%24top=3"

# Document with category and status
curl "https://oda.ft.dk/api/Dokument?%24expand=Dokumentkategori,Dokumentstatus&%24top=3"
```

### Document Actors and Relationships

```bash
# Documents with associated actors
curl "https://oda.ft.dk/api/Dokument?%24expand=DokumentAktør&%24top=3"

# Documents with actor details
curl "https://oda.ft.dk/api/Dokument?%24expand=DokumentAktør/Aktør&%24top=1"
```

### Case and Legislative Process

```bash
# Documents with related cases
curl "https://oda.ft.dk/api/Dokument?%24expand=SagDokument&%24top=3"

# Documents with case and case step information
curl "https://oda.ft.dk/api/Dokument?%24expand=SagstrinDokument/Sagstrin&%24top=2"
```

### File Attachments

```bash
# Documents with attached files
curl "https://oda.ft.dk/api/Dokument?%24expand=Fil&%24top=5"

# Documents with file details
curl "https://oda.ft.dk/api/Dokument?%24expand=Fil&%24filter=Fil/any()&%24top=3"
```

!!! warning "Large Response Warning"
    Expanding relationships like `DokumentAktør/Aktør` can return extensive biographical data. Use `$top=1` for testing.

## Data Analysis Examples

### Document Production Analysis

```bash
# Most active document types
curl "https://oda.ft.dk/api/Dokument?%24expand=Dokumenttype&%24filter=dato%20gt%20datetime'2025-01-01T00:00:00'&%24top=50"

# Monthly document production
curl "https://oda.ft.dk/api/Dokument?%24filter=dato%20ge%20datetime'2025-09-01T00:00:00'%20and%20dato%20lt%20datetime'2025-10-01T00:00:00'&%24top=100"
```

### Question and Answer Analysis

```bash
# Parliamentary questions with answers
curl "https://oda.ft.dk/api/Dokument?%24expand=SvarDokumenter&%24filter=spørgsmålstitel%20ne%20null&%24top=10"

# Questions by specific topics
curl "https://oda.ft.dk/api/Dokument?%24filter=substringof('miljø',spørgsmålstitel)&%24top=10"
```

### Document Timeline Analysis

```bash
# Document processing time (release vs creation)
curl "https://oda.ft.dk/api/Dokument?%24filter=frigivelsesdato%20ne%20null%20and%20dato%20ne%20frigivelsesdato&%24select=titel,dato,frigivelsesdato&%24top=10"

# Recently updated older documents
curl "https://oda.ft.dk/api/Dokument?%24filter=opdateringsdato%20gt%20datetime'2025-09-01T00:00:00'%20and%20dato%20lt%20datetime'2025-01-01T00:00:00'&%24top=10"
```

## Performance Optimization

### Use Field Selection

```bash
# Good: Only request needed fields
curl "https://oda.ft.dk/api/Dokument?%24select=id,titel,dato,typeid&%24top=100"

# Avoid: Large text fields when not needed
curl "https://oda.ft.dk/api/Dokument?%24select=spørgsmålsordlyd&%24top=100"  # Can be very long text
```

### Efficient Pagination

```bash
# Paginate through documents by ID
curl "https://oda.ft.dk/api/Dokument?%24skip=0&%24top=100&%24orderby=id"
curl "https://oda.ft.dk/api/Dokument?%24skip=100&%24top=100&%24orderby=id"
```

### Smart Filtering

```bash
# Filter before expanding to reduce response size
curl "https://oda.ft.dk/api/Dokument?%24filter=typeid%20eq%205&%24expand=Dokumenttype&%24top=10"
```

## Access Control and Public Information

### Public Access Codes

The `offentlighedskode` field indicates document accessibility:

- **"O"** - Offentlig (Public) - Freely accessible
- **null** - May have restricted access or special handling requirements

### File Access

Documents link to PDF files through the `Fil` navigation property:
- Files are hosted on ft.dk
- Direct PDF access requires appropriate permissions
- File metadata includes size, format, and timestamps

## Common Use Cases

### 1. Recent Parliamentary Documents Monitor

```python
def get_recent_documents(hours_back=24, doc_type=None):
    """Get documents updated in last 24 hours"""
    since = (datetime.now() - timedelta(hours=hours_back)).isoformat()
    filter_parts = [f"opdateringsdato gt datetime'{since}'"]
    
    if doc_type:
        filter_parts.append(f"typeid eq {doc_type}")
    
    filter_query = " and ".join(filter_parts)
    return get_documents(
        filter_query=filter_query,
        expand="Dokumenttype",
        select="titel,dato,frigivelsesdato,Dokumenttype/type",
        orderby="opdateringsdato desc"
    )
```

### 2. Parliamentary Question Tracker

```python
def track_parliamentary_questions(topic_keyword=None):
    """Track parliamentary questions and their answers"""
    filter_parts = ["spørgsmålstitel ne null"]
    
    if topic_keyword:
        filter_parts.append(f"substringof('{topic_keyword}', spørgsmålstitel)")
    
    filter_query = " and ".join(filter_parts)
    return get_documents(
        filter_query=filter_query,
        expand="SvarDokumenter,DokumentAktør/Aktør",
        select="titel,spørgsmålstitel,dato,SvarDokumenter/titel",
        orderby="dato desc"
    )
```

### 3. Minister Activity Analysis

```python
def analyze_ministerial_documents(start_date, end_date):
    """Analyze ministerial document production"""
    filter_query = f"typeid eq 3 and dato ge datetime'{start_date}' and dato le datetime'{end_date}'"
    return get_documents(
        filter_query=filter_query,
        expand="DokumentAktør/Aktør",
        select="titel,dato,DokumentAktør/Aktør/navn",
        orderby="dato"
    )
```

### 4. Document File Access

```python
def get_documents_with_files():
    """Get documents that have attached files"""
    filter_query = "Fil/any()"  # Documents with at least one file
    return get_documents(
        filter_query=filter_query,
        expand="Fil",
        select="titel,dato,Fil/titel,Fil/filurl",
        top=20
    )
```

## Important Notes

### Data Coverage and Freshness
- **Historical Coverage**: Documents from October 2013 onwards
- **Real-time Updates**: New documents appear within hours of publication
- **Update Frequency**: Most active during parliamentary session periods
- **Business Hours**: Primary activity during Danish government working hours

### Document Processing Workflow
- **Creation**: Document created with `dato` timestamp
- **Processing**: Internal processing may update various fields
- **Release**: Document made public with `frigivelsesdato` timestamp
- **Updates**: Ongoing updates tracked via `opdateringsdato`

### Text Content Considerations
- **Language**: All content is in Danish
- **Encoding**: UTF-8 encoding for Danish characters (æ, ø, å)
- **Length**: Title and question fields can be very long
- **Format**: Formal parliamentary language and terminology

### Related Entities

The `Dokument` entity connects to:

- **Dokumenttype** - Document classification (13+ types)
- **Dokumentkategori** - Document categories
- **Dokumentstatus** - Processing status
- **DokumentAktør** - Associated politicians and actors
- **SagDokument** - Related parliamentary cases
- **SagstrinDokument** - Specific case steps
- **Fil** - Attached PDF files and documents
- **SvarDokumenter** - Answer documents (for questions)
- **EmneordDokument** - Subject keywords
- **DagsordenspunktDokument** - Agenda items

### Example Records

**Parliamentary Inquiry:**
```json
{
  "id": 1,
  "typeid": 13,
  "kategoriid": 36,
  "statusid": 1,
  "offentlighedskode": "O",
  "titel": "Spm. om formuefordelingen fordelt på både indkomst- og formuefordelingen i perioden 1997-2012...",
  "dato": "2014-08-08T00:00:00",
  "frigivelsesdato": "2014-08-08T14:57:26",
  "opdateringsdato": "2016-03-14T09:32:33.387"
}
```

**EU Note:**
```json
{
  "id": 150000,
  "typeid": 6,
  "titel": "EU-note vedrørende forordning om klimatilpasning",
  "dato": "2025-09-01T00:00:00",
  "offentlighedskode": "O",
  "frigivelsesdato": "2025-09-01T10:30:00"
}
```

The `Dokument` entity serves as the central repository for all parliamentary documentation, providing transparency into the Danish democratic process and enabling comprehensive analysis of legislative activity.