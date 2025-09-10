# Møde (Meeting) Entity

The `Møde` entity represents parliamentary meetings and sessions in the Danish Parliament system, capturing both plenary sessions and committee meetings. Each meeting record includes detailed information about when, where, and what type of parliamentary activity took place.

## Overview

- **Entity Name**: `Møde`
- **Endpoint**: `https://oda.ft.dk/api/Møde`
- **Total Records**: Thousands of parliamentary meetings
- **Primary Key**: `id` (Int32)
- **Meeting Types**: Various (plenary sessions, committee meetings, etc.)

## Field Reference

### Core Identification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | Int32 | Primary key, unique meeting identifier | `17` |
| `nummer` | Int32 | Meeting number within the parliamentary period | `45` |
| `titel` | String | Meeting title or description | `"Folketingets møde nr. 45 torsdag den 15. december 2022, kl. 10:00"` |

### Meeting Details

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `dato` | DateTime | Meeting date and time | `"2022-12-15T10:00:00"` |
| `lokale` | String | Meeting room or venue | `"Folketingssalen"` |
| `dagsordenurl` | String | URL to the official agenda | `"https://www.ft.dk/samling/20221/agenda/..."` |

### Classification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `typeid` | Int32 | Meeting type ID (foreign key to Mødetype) | `1` |
| `statusid` | Int32 | Meeting status ID (foreign key to Mødestatus) | `3` |

### Relationship Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `periodeid` | Int32 | Parliamentary period ID (foreign key to Periode) | `32` |

### Temporal Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `opdateringsdato` | DateTime | Last update timestamp | `"2025-09-09T12:30:12.467"` |

## Entity Relationships

The `Møde` entity serves as a central hub connecting various parliamentary activities:

### Direct Relationships

- **Afstemning** (`mødeid`): Voting sessions held during the meeting
- **Dagsordenspunkt** (`mødeid`): Individual agenda items discussed
- **MødeAktør** (`mødeid`): Participants and attendees of the meeting
- **Mødetype** (`typeid`): Type classification of the meeting
- **Mødestatus** (`statusid`): Current status of the meeting
- **Periode** (`periodeid`): Parliamentary period during which the meeting occurred

### Indirect Relationships

Through related entities, meetings connect to:
- **Sag** (via Dagsordenspunkt): Cases discussed in the meeting
- **Aktør** (via MødeAktør): Politicians and other actors participating
- **Stemme** (via Afstemning): Individual votes cast during voting sessions

## Query Examples

### Basic Meeting Retrieval

```http
GET https://oda.ft.dk/api/Møde?%24top=10
```

Retrieves the 10 most recent meetings with basic information.

### Meeting with Voting Sessions

```http
GET https://oda.ft.dk/api/Møde?%24expand=Afstemning&%24top=5
```

Retrieves meetings with all associated voting sessions expanded.

### Meetings by Date Range

```http
GET https://oda.ft.dk/api/Møde?%24filter=dato%20ge%20datetime%272024-01-01%27%20and%20dato%20le%20datetime%272024-12-31%27
```

Retrieves all meetings from the year 2024.

### Committee Meetings vs Plenary Sessions

```http
GET https://oda.ft.dk/api/Møde?%24expand=Mødetype&%24filter=typeid%20eq%201
```

Retrieves meetings of a specific type (replace `1` with the desired type ID).

### Recent Meetings with Full Context

```http
GET https://oda.ft.dk/api/Møde?%24expand=Afstemning,Dagsordenspunkt,MødeAktør&%24orderby=dato%20desc&%24top=5
```

Retrieves the 5 most recent meetings with voting sessions, agenda items, and participants.

### Meetings in Specific Room

```http
GET https://oda.ft.dk/api/Møde?%24filter=substringof%28%27Folketingssalen%27%2Clokale%29
```

Finds meetings held in the main parliamentary chamber.

## Response Structure Example

```json
{
  "@odata.context": "https://oda.ft.dk/api/$metadata#Møde",
  "value": [
    {
      "id": 17,
      "nummer": 45,
      "titel": "Folketingets møde nr. 45 torsdag den 15. december 2022, kl. 10:00",
      "dato": "2022-12-15T10:00:00",
      "lokale": "Folketingssalen",
      "dagsordenurl": "https://www.ft.dk/samling/20221/agenda/R202200045/index.htm",
      "typeid": 1,
      "statusid": 3,
      "periodeid": 32,
      "opdateringsdato": "2022-12-15T15:30:45.123"
    }
  ]
}
```

## Common Use Cases

### Parliamentary Activity Tracking

Monitor ongoing parliamentary work by tracking meetings:

```http
GET https://oda.ft.dk/api/Møde?%24expand=Dagsordenspunkt&%24filter=dato%20ge%20datetime%27{TODAY}%27&%24orderby=dato
```

### Legislative Process Monitoring

Track specific legislation through committee meetings:

```http
GET https://oda.ft.dk/api/Møde?%24expand=Dagsordenspunkt(%24expand=Sag)&%24filter=Dagsordenspunkt/any(d:d/sagid%20eq%20{CASE_ID})
```

### Voting Analysis

Analyze parliamentary voting patterns by meeting:

```http
GET https://oda.ft.dk/api/Møde?%24expand=Afstemning(%24expand=Stemme)&%24filter=dato%20ge%20datetime%272024-01-01%27
```

### Meeting Attendance Analysis

Study participation patterns:

```http
GET https://oda.ft.dk/api/Møde?%24expand=MødeAktør(%24expand=Aktør)&%24filter=typeid%20eq%201
```

## Important Notes

### URL Encoding
Always use `%24` instead of `$` for OData parameters in URLs. This is crucial for proper API functionality.

### Meeting Types
Different meeting types (`typeid`) represent various parliamentary activities:
- Plenary sessions
- Committee meetings  
- Subcommittee meetings
- Hearing sessions
- Other specialized meetings

### Time Zones
All datetime fields use Danish local time. Consider time zone implications when filtering by dates.

### Data Freshness
Meeting data is typically updated within hours of the meeting conclusion, with voting results and attendance information added progressively.

## Danish Parliamentary Context

### Meeting Structure
Danish parliamentary meetings follow established procedures:
- **Plenary sessions**: Full parliament meetings in the main chamber
- **Committee meetings**: Specialized committee work on specific policy areas
- **Hearing sessions**: Expert testimony and stakeholder input

### Agenda System
Each meeting has a formal agenda (`dagsordenurl`) linking to official parliamentary documentation, providing context for all discussion items and voting sessions.

### Legislative Integration
Meetings are integral to the Danish legislative process, serving as venues for:
- First, second, and third readings of bills
- Committee deliberations
- Question periods and interpellations
- Voting on legislative proposals

Understanding meeting data is essential for comprehensive analysis of Danish parliamentary democracy and legislative processes.