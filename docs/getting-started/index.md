---
title: Getting Started with Danish Parliament API - Quick Setup Guide
description: Learn how to use the Danish Parliament API (oda.ft.dk) with this comprehensive getting started guide. No authentication required, OData 3.0 protocol, access to 96,538+ cases.
keywords: danish parliament api tutorial, oda.ft.dk getting started, odata api guide, parliamentary data access, no authentication api
---

# Getting Started

The Danish Parliament API (oda.ft.dk) provides unprecedented access to Denmark's parliamentary data. This guide will get you up and running in minutes.

## Prerequisites

- Basic understanding of REST APIs
- Familiarity with JSON
- HTTP client (curl, browser, or programming language)

## Key Concepts

### No Authentication Required
The API is completely open - no API keys, tokens, or registration required. Simply start making requests!

### OData Protocol
The API uses OData 3.0, providing powerful querying capabilities:

- `$top` - Limit number of records (max 100)
- `$skip` - Skip records for pagination  
- `$filter` - Filter records by conditions
- `$expand` - Include related data
- `$select` - Choose specific fields
- `$orderby` - Sort results
- `$inlinecount` - Get total counts

### Danish Language
All content is in Danish. Key terms:

- **Sag** = Case/Bill
- **Aktør** = Actor/Person  
- **Afstemning** = Voting session
- **Stemme** = Individual vote
- **Dokument** = Document
- **Møde** = Meeting

## Your First Query

Let's start with a simple query to get 5 recent cases:

```bash
curl "https://oda.ft.dk/api/Sag?%24top=5"
```

!!! warning "URL Encoding Critical"
    **Always use `%24` instead of `$`** in URLs. This is the #1 mistake developers make.
    
    L Wrong: `?$top=5`
    
     Correct: `?%24top=5`

## Response Structure

```json
{
  "odata.metadata": "https://oda.ft.dk/api/$metadata#Sag",
  "value": [
    {
      "id": 102903,
      "titel": "Kommissionsmeddelelse om...",
      "offentlighedskode": "O",
      "opdateringsdato": "2025-09-09T17:49:11.87",
      "periodeid": 32,
      "statsbudgetsag": true,
      "statusid": 11,
      "typeid": 5
    }
  ]
}
```

## Common Query Patterns

### Filter by Date
```bash
# Cases updated today
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025&%24top=5"
```

### Search by Text
```bash
# Climate-related cases
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)&%24top=5"
```

### Include Related Data
```bash
# Cases with category information
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=3"
```

### Pagination
```bash
# Get next page of results
curl "https://oda.ft.dk/api/Sag?%24skip=100&%24top=100"
```

### Field Selection for Performance
```bash
# Only get specific fields
curl "https://oda.ft.dk/api/Sag?%24select=id,titel,opdateringsdato&%24top=5"
```

## Understanding the Data

### Entity Types
The API contains 50 different entity types organized into logical groups:

- **Core Entities**: Sag (Cases), Aktør (Actors), Afstemning (Voting), Stemme (Votes)
- **Documents**: Dokument, Fil (Files)
- **Meetings**: Møde, Dagsordenspunkt
- **Relationships**: Junction tables connecting entities
- **Classifications**: Status, Type, and Category entities

### Data Freshness
The API provides exceptionally fresh data:
- Updates within hours of parliamentary activity
- Latest example: 2025-09-09T17:49:11.87
- 50+ daily updates across all entities

## Try It Yourself - Interactive Query Builder

<div class="query-builder"></div>

## Next Steps

1. **[First Query](first-query.md)** - Step-by-step first API call
2. **[URL Encoding](url-encoding.md)** - Master the critical encoding rules  
3. **[No Authentication](no-auth.md)** - Understanding open access
4. **[Common Mistakes](common-mistakes.md)** - Avoid these pitfalls

## Quick Reference

| Purpose | Endpoint | Example |
|---------|----------|---------|
| Cases | `/api/Sag` | Legislative bills and proposals |
| Actors | `/api/Aktør` | Politicians, committees, ministries |
| Votes | `/api/Afstemning` | Voting sessions |
| Individual Votes | `/api/Stemme` | How each politician voted |
| Documents | `/api/Dokument` | Parliamentary documents |
| Meetings | `/api/Møde` | Parliamentary meetings |

## Performance Tips

1. **Use `$select`** - Only request fields you need
2. **Limit results** - Maximum 100 records per request
3. **Filter early** - Apply filters before expansions
4. **Cache wisely** - Use `opdateringsdato` for change detection

## Need Help?

- **[Troubleshooting](../production/troubleshooting/)** - Common problems and solutions
- **[Code Examples](../code-examples/)** - Ready-to-use client libraries
- **[API Reference](../api-reference/)** - Complete technical documentation
- **Contact**: folketinget@ft.dk (subject: "øbne Data")