---
title: API Reference - Complete Danish Parliament API Documentation
description: Comprehensive API reference for the Danish Parliament Open Data API (oda.ft.dk). Explore 50+ entities, OData protocols, error handling, and performance optimization.
keywords: danish parliament api reference, oda.ft.dk documentation, odata entities, api endpoints, parliamentary data reference
---

# API Reference

Complete technical reference for the Danish Parliament Open Data API (oda.ft.dk).

## Overview

The Danish Parliament API provides access to comprehensive parliamentary data through a RESTful OData 3.0 interface. This reference covers all available entities, query capabilities, error handling, and performance considerations.

## API Endpoints

- **Base URL**: `https://oda.ft.dk/api/`
- **Protocol**: OData 3.0
- **Authentication**: None required
- **Formats**: JSON (default), XML
- **Rate Limits**: Client-side throttling recommended

## Entity Categories

### Core Entities
- **[Sag (Cases)](entities/core/sag.md)** - 96,538+ legislative cases and bills
- **[Aktør (Actors)](entities/core/aktor.md)** - 18,139+ politicians, committees, and organizations
- **[Afstemning (Voting)](entities/core/afstemning.md)** - Parliamentary voting sessions
- **[Stemme (Individual Votes)](entities/core/stemme.md)** - Individual voting records

### Document Entities
- **[Dokument (Documents)](entities/documents/dokument.md)** - Parliamentary documents
- **[Fil (Files)](entities/documents/fil.md)** - File downloads and attachments

### Meeting Entities
- **[Møde (Meetings)](entities/meetings/mode.md)** - Parliamentary meetings and sessions

### Junction Tables
- **[SagAktør](entities/junction-tables/sag-aktor.md)** - Case-Actor relationships (23 role types)
- **[DokumentAktør](entities/junction-tables/dokument-aktor.md)** - Document-Actor relationships (25 role types)

## OData Protocol Support

- **[$filter](odata/filters.md)** - Query filtering with Danish text support
- **[$expand](odata/expansion.md)** - Include related data (2-level maximum)
- **[$top/$skip](odata/pagination.md)** - Pagination (100 record limit)
- **[$orderby](odata/ordering.md)** - Result sorting
- **[$select](odata/selection.md)** - Field selection for performance
- **[Unsupported Features](odata/unsupported.md)** - Limitations and workarounds

## Error Handling

- **[HTTP Status Codes](errors/http-codes.md)** - 400, 404, 501 response patterns
- **[Silent Failures](errors/silent-failures.md)** - Invalid filters return all data
- **[Troubleshooting](errors/troubleshooting.md)** - Diagnostic commands and solutions

## Performance

- **[Response Times](performance/response-times.md)** - 85ms to 2+ second benchmarks
- **[Query Limits](performance/query-limits.md)** - 100 record hard limit
- **[Optimization](performance/optimization.md)** - Best practices for efficient queries

## Quick Reference

| Parameter | Purpose | Example | Limit |
|-----------|---------|---------|-------|
| `$top` | Limit results | `$top=50` | Max 100 |
| `$skip` | Skip records | `$skip=100` | None |
| `$filter` | Filter data | `$filter=year(opdateringsdato) eq 2025` | Complex expressions |
| `$expand` | Include related | `$expand=Sagskategori` | 2 levels max |
| `$select` | Choose fields | `$select=id,titel` | Any fields |
| `$orderby` | Sort results | `$orderby=opdateringsdato desc` | Any sortable field |

!!! warning "Critical: URL Encoding"
    Always use `%24` instead of `$` in URLs. This is the most common developer mistake.

## Support

- **GitHub Issues**: Report problems and request features
- **Email**: folketinget@ft.dk (subject: "Åbne Data")
- **Official API**: https://oda.ft.dk/