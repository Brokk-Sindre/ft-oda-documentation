# Fil (Files) Entity

The `Fil` entity represents file attachments in the Danish parliamentary system, providing direct access to downloadable documents such as PDFs, Word documents, and other file formats. Files are linked to their parent documents and can be downloaded directly without authentication.

## Overview

- **Entity Name**: `Fil`
- **Endpoint**: `https://oda.ft.dk/api/Fil`
- **Primary Key**: `id` (Int32)
- **Purpose**: File attachments for parliamentary documents
- **File Hosting**: Files stored on `www.ft.dk` domain
- **Access**: Direct download without authentication required

## Field Reference

### Core Identification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | Int32 | Primary key, unique file identifier | `158` |
| `dokumentid` | Int32 | Foreign key to parent document | `11432` |
| `titel` | String | File title/name (often includes extension) | `"Evaluering af lov om friplejeboliger_endelig vers.pdf"` |

### File Access Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `filurl` | String | Direct download URL hosted on www.ft.dk | `"https://www.ft.dk/samling/20131/almdel/BYB/bilag/89/1396405.pdf"` |
| `format` | String | File format type | `"PDF"`, `"DOCX"` |

### Temporal Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `opdateringsdato` | DateTime | Last update timestamp | `"2020-02-25T10:46:59.49"` |

## File Format Support

The API supports multiple file formats commonly used in parliamentary documentation:

| Format | Description | Common Use |
|--------|-------------|------------|
| **PDF** | Portable Document Format | Official documents, reports, legislation |
| **DOCX** | Microsoft Word Document | Draft documents, working papers |

!!! info "Format Accuracy"
    The `format` field in the API may not always match the actual file type. Some DOCX files may have PDF URLs or vice versa. Always verify the actual file format when processing downloads.

## Common Query Examples

### Basic File Queries

```bash
# Get latest 5 files
curl "https://oda.ft.dk/api/Fil?%24top=5&%24orderby=opdateringsdato%20desc"

# Get specific file by ID
curl "https://oda.ft.dk/api/Fil(158)"

# Count total files
curl "https://oda.ft.dk/api/Fil?%24inlinecount=allpages&%24top=1"
```

### Filter by Format

```bash
# Get all PDF files
curl "https://oda.ft.dk/api/Fil?%24filter=format%20eq%20'PDF'&%24top=10"

# Get all Word documents
curl "https://oda.ft.dk/api/Fil?%24filter=format%20eq%20'DOCX'&%24top=10"

# Files updated recently
curl "https://oda.ft.dk/api/Fil?%24filter=opdateringsdato%20gt%20datetime'2020-01-01T00:00:00'&%24top=10"
```

### Search by Title

```bash
# Find files with specific keywords in title
curl "https://oda.ft.dk/api/Fil?%24filter=substringof('budget',titel)&%24top=5"

# Search for evaluation reports
curl "https://oda.ft.dk/api/Fil?%24filter=substringof('evaluering',titel)&%24top=5"

# Find PDF files by title
curl "https://oda.ft.dk/api/Fil?%24filter=substringof('pdf',titel)%20and%20format%20eq%20'PDF'&%24top=5"
```

### Field Selection for Performance

```bash
# Only essential fields for file listings
curl "https://oda.ft.dk/api/Fil?%24select=id,titel,format,filurl&%24top=20"

# Get just download URLs
curl "https://oda.ft.dk/api/Fil?%24select=filurl&%24top=10"

# File metadata without URLs
curl "https://oda.ft.dk/api/Fil?%24select=titel,format,opdateringsdato&%24top=10"
```

## Relationship Expansion

### Document Integration

```bash
# Files with parent document information
curl "https://oda.ft.dk/api/Fil?%24expand=Dokument&%24top=3"

# Find files for specific document
curl "https://oda.ft.dk/api/Fil?%24filter=dokumentid%20eq%2011432&%24expand=Dokument"

# Files with document titles and types
curl "https://oda.ft.dk/api/Fil?%24expand=Dokument/Dokumenttype&%24select=titel,format,Dokument/titel,Dokument/Dokumenttype/type&%24top=5"
```

### Combined Document and File Search

```bash
# Find documents with file attachments by keyword
curl "https://oda.ft.dk/api/Dokument?%24expand=Fil&%24filter=substringof('budget',titel)&%24select=titel,Fil/filurl,Fil/format&%24top=5"

# Documents with PDF attachments only
curl "https://oda.ft.dk/api/Dokument?%24expand=Fil&%24filter=Fil/format%20eq%20'PDF'&%24top=3"
```

## File Download Examples

### Direct File Access

```bash
# Test file accessibility (headers only)
curl -I "https://www.ft.dk/samling/20131/almdel/BYB/bilag/89/1396405.pdf"

# Download file with progress
curl -L -o "document.pdf" "https://www.ft.dk/samling/20131/almdel/BYB/bilag/89/1396405.pdf"

# Get file size and download time
curl -w "%{size_download} bytes in %{time_total}s" -o /dev/null -s "https://www.ft.dk/samling/20131/almdel/BYB/bilag/89/1396405.pdf"
```

### Programmatic File Processing

```bash
# Extract file URLs for batch processing
curl -s "https://oda.ft.dk/api/Fil?%24filter=format%20eq%20'PDF'&%24select=filurl&%24top=10" | jq -r '.value[].filurl'

# Get file metadata for processing pipeline
curl -s "https://oda.ft.dk/api/Fil?%24select=id,titel,format,filurl,opdateringsdato&%24top=5" | jq '.value[]'
```

## Data Analysis Examples

### File Format Distribution

```bash
# Count files by format
curl "https://oda.ft.dk/api/Fil?%24filter=format%20eq%20'PDF'&%24inlinecount=allpages&%24top=1"
curl "https://oda.ft.dk/api/Fil?%24filter=format%20eq%20'DOCX'&%24inlinecount=allpages&%24top=1"

# Get format statistics
curl "https://oda.ft.dk/api/Fil?%24select=format&%24top=1000" | jq '[.value[].format] | group_by(.) | map({format: .[0], count: length})'
```

### Document Attachment Analysis

```bash
# Documents with multiple file attachments
curl "https://oda.ft.dk/api/Dokument?%24expand=Fil&%24filter=Fil/id%20ne%20null&%24select=titel,Fil/titel,Fil/format&%24top=10"

# Recent file uploads
curl "https://oda.ft.dk/api/Fil?%24filter=opdateringsdato%20gt%20datetime'2020-01-01T00:00:00'&%24orderby=opdateringsdato%20desc&%24top=20"
```

### Content Analysis Preparation

```bash
# Get PDF files for text analysis
curl "https://oda.ft.dk/api/Fil?%24filter=format%20eq%20'PDF'%20and%20substringof('rapport',titel)&%24select=titel,filurl&%24top=10"

# Find evaluation documents
curl "https://oda.ft.dk/api/Fil?%24filter=substringof('evaluering',titel)&%24expand=Dokument&%24select=titel,filurl,Dokument/titel&%24top=10"
```

## Common Use Cases

### 1. Document Archive System

```python
def download_parliamentary_files(document_keywords, file_format="PDF"):
    """Download files related to specific parliamentary topics"""
    filter_query = f"format eq '{file_format}' and substringof('{document_keywords}',titel)"
    files = get_files(filter_query=filter_query, select="titel,filurl", top=100)
    
    for file in files['value']:
        download_url = file['filurl']
        filename = file['titel']
        # Download logic here
```

### 2. File Format Migration Analysis

```python
def analyze_file_formats():
    """Analyze distribution of file formats in the system"""
    all_files = get_files(select="format", top=1000)
    format_counts = {}
    
    for file in all_files['value']:
        fmt = file.get('format', 'Unknown')
        format_counts[fmt] = format_counts.get(fmt, 0) + 1
    
    return format_counts
```

### 3. Content Extraction Pipeline

```python
def setup_content_extraction():
    """Get files ready for text extraction and analysis"""
    pdf_files = get_files(
        filter_query="format eq 'PDF'",
        expand="Dokument",
        select="titel,filurl,Dokument/titel,Dokument/dokumenttypeid",
        top=500
    )
    
    # Process files for content extraction
    return pdf_files
```

### 4. Document Completeness Check

```python
def check_document_attachments():
    """Find documents that should have file attachments"""
    documents_with_files = get_documents(
        expand="Fil",
        filter_query="Fil/id ne null",
        select="titel,Fil/format"
    )
    
    # Analyze attachment patterns
    return documents_with_files
```

## Performance Optimization

### Efficient File Queries

```bash
# Good: Request only needed fields
curl "https://oda.ft.dk/api/Fil?%24select=filurl,format&%24top=100"

# Good: Filter by format first, then other criteria
curl "https://oda.ft.dk/api/Fil?%24filter=format%20eq%20'PDF'%20and%20substringof('budget',titel)&%24top=20"

# Avoid: Requesting all fields when only URLs needed
curl "https://oda.ft.dk/api/Fil?%24top=100"  # Returns unnecessary data
```

### Batch File Processing

```bash
# Process files in batches for better performance
curl "https://oda.ft.dk/api/Fil?%24select=filurl&%24skip=0&%24top=100"
curl "https://oda.ft.dk/api/Fil?%24select=filurl&%24skip=100&%24top=100"
```

## Important Notes

### File Access Characteristics

- **No Authentication**: Files can be downloaded directly without API keys or authentication
- **Direct URLs**: All file URLs point to `www.ft.dk` domain (different from API domain)
- **URL Stability**: File URLs appear to be permanent and don't expire
- **File Sizes**: Parliamentary documents typically range from ~1MB to 1.5MB+

### Download Considerations

!!! warning "File Size and Bandwidth"
    Parliamentary documents can be large (1MB+). Consider implementing:
    - Concurrent download limits
    - Progress tracking for large files
    - Retry logic for failed downloads
    - Local caching to avoid repeated downloads

### Data Quality Notes

- **Format Field Accuracy**: The `format` field may not always match the actual file type
- **Title Consistency**: File titles may include version information and Danish characters
- **Update Frequency**: Files have update dates but are generally static once published

### Danish Language Support

 **Full UTF-8 Support**: File titles and content support Danish characters (æ, ø, å):

```bash
# Search for files with Danish characters
curl "https://oda.ft.dk/api/Fil?%24filter=substringof('ø',titel)&%24top=5"
curl "https://oda.ft.dk/api/Fil?%24filter=substringof('evaluering',titel)&%24top=5"
```

### Integration with Document Workflow

The `Fil` entity is tightly integrated with the parliamentary document workflow:

1. **Document Creation**: Documents are created in the `Dokument` entity
2. **File Attachment**: Related files are added to the `Fil` entity with `dokumentid` foreign key
3. **Publication**: Files become accessible via direct download URLs
4. **Updates**: Files can be updated (reflected in `opdateringsdato`)

### Example File Record

```json
{
  "id": 158,
  "dokumentid": 11432,
  "titel": "Evaluering af lov om friplejeboliger_endelig vers.pdf",
  "filurl": "https://www.ft.dk/samling/20131/almdel/BYB/bilag/89/1396405.pdf",
  "format": "PDF",
  "opdateringsdato": "2020-02-25T10:46:59.49"
}
```

This file entity enables direct access to the rich document archive of the Danish Parliament, supporting everything from automated document analysis to public transparency initiatives.