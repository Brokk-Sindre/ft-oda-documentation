# Aktør (Actors) Entity

The `Aktør` entity represents all actors in the Danish parliamentary system, including politicians, committees, ministries, parliamentary groups, and other institutional actors. With **18,139+ records**, it provides comprehensive coverage of Danish political actors.

## Overview

- **Entity Name**: `Aktør`
- **Endpoint**: `https://oda.ft.dk/api/Aktør` (also accessible as `https://oda.ft.dk/api/Akt%C3%B8r`)
- **Total Records**: 18,139+ (as of September 2025)
- **Primary Key**: `id` (Int32)
- **Types**: 13 different actor types (individuals to institutions)

## Field Reference

### Core Identification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | Int32 | Primary key, unique actor identifier | `12` |
| `navn` | String | Full name | `"Nicolai Wammen"` |
| `fornavn` | String | First name | `"Nicolai"` |
| `efternavn` | String | Last name | `"Wammen"` |
| `gruppenavnkort` | String | Short group name | `"S"` |

### Classification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `typeid` | Int32 | Actor type ID (foreign key to Aktørtype) | `5` |

### Temporal Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `opdateringsdato` | DateTime | Last update timestamp | `"2025-09-09T17:29:09.407"` |
| `startdato` | DateTime | Start date | `"2019-06-05T00:00:00"` |
| `slutdato` | DateTime | End date | `"2023-06-05T00:00:00"` |
| `periodeid` | Int32 | Parliamentary period ID | `32` |

### Biographical Information

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `biografi` | String | Detailed biography (HTML format) | `"<div>Born 1971...</div>"` |

!!! warning "Personal Data"
    The `biografi` field contains extensive personal information including birth dates, family details, contact information, and career history. Use responsibly and consider GDPR implications.

## Actor Types Reference

The API includes 13 different actor types (`Aktørtype`):

| Type ID | Name | Description | Examples |
|---------|------|-------------|----------|
| 1 | Ministerområde | Ministry Area | `"Finansministeriet"` |
| 2 | Ministertitel | Ministry Title | `"finansminister finansministeren"` |
| 3 | Udvalg | Committee | `"FIU Finansudvalget"` |
| 4 | Folketingsgruppe | Parliamentary Group/Party | `"Socialdemokratiet"` |
| 5 | Person | Person (Official) | `"Nicolai Wammen"` |
| 6 | Gruppe | Group | Various working groups |
| 7 | Anden gruppe | Other Group | Miscellaneous groups |
| 8 | Ministerium | Ministry | Full ministry entities |
| 9 | Kommission | Commission | Parliamentary commissions |
| 10 | Organisation | Organization | External organizations |
| 11 | Parlamentarisk forsamling | Parliamentary Assembly | International assemblies |
| 12 | Privatperson | Private Person | Non-official individuals |
| 13 | Tværpolitisk netværk | Cross-Political Network | Cross-party initiatives |

## Common Query Examples

### Basic Queries

```bash
# Get latest 5 actors
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24top=5&%24orderby=opdateringsdato%20desc"

# Get specific actor by ID
curl "https://oda.ft.dk/api/Akt%C3%B8r(12)"

# Count total actors
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24inlinecount=allpages&%24top=1"
```

### Filter by Actor Type

```bash
# Get all politicians (Person type)
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=typeid%20eq%205&%24top=10"

# Get all committees (Udvalg type)
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=typeid%20eq%203&%24top=10"

# Get all parliamentary groups/parties
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=typeid%20eq%204&%24top=10"

# Get all ministries
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=typeid%20eq%208&%24top=10"
```

### Search by Name

```bash
# Find specific politician
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=navn%20eq%20'Nicolai%20Wammen'"

# Search for names containing specific text
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=substringof('Wammen',navn)&%24top=5"

# Search by first name
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=substringof('Nicolai',fornavn)&%24top=5"

# Search for names with Danish characters
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=substringof('%C3%B8',navn)&%24top=5"
```

### Time-Based Queries

```bash
# Actors updated today
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=opdateringsdato%20gt%20datetime'2025-09-09T00:00:00'"

# Active actors (no end date)
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=slutdato%20eq%20null&%24top=10"

# Actors from specific period
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=periodeid%20eq%2032&%24top=10"
```

### Field Selection

```bash
# Only essential fields
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24select=id,navn,typeid,opdateringsdato&%24top=10"

# Names only
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24select=navn&%24filter=typeid%20eq%205&%24top=10"
```

## Relationship Expansion

### Core Relationships

```bash
# Actor with type information
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24expand=Aktørtype&%24top=3"

# Actor with period information
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24expand=Periode&%24top=3"
```

### Case Relationships

```bash
# Actors involved in cases (may be large response)
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24expand=SagAktør/Sag&%24top=1"

# Actor roles in cases
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24expand=SagAktør/SagAktørRolle&%24top=3"
```

### Voting Relationships

```bash
# Actor voting records (use carefully - can be very large)
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24expand=Stemme&%24filter=typeid%20eq%205&%24top=1"
```

### Document Relationships

```bash
# Actors involved in documents
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24expand=DokumentAktør/Dokument&%24top=3"
```

## Data Analysis Examples

### Political Analysis

```bash
# Get all current politicians
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=typeid%20eq%205%20and%20slutdato%20eq%20null&%24orderby=navn&%24select=navn,gruppenavnkort"

# Politicians by party (group)
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=gruppenavnkort%20eq%20'S'&%24select=navn,fornavn,efternavn"

# Committee membership analysis
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=typeid%20eq%203&%24select=navn&%24orderby=navn"
```

### Institutional Analysis

```bash
# All ministry entities
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=typeid%20eq%201%20or%20typeid%20eq%208&%24select=navn,typeid&%24orderby=navn"

# Parliamentary committees
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=typeid%20eq%203&%24select=navn&%24orderby=navn"

# Political parties/groups
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=typeid%20eq%204&%24select=navn&%24orderby=navn"
```

### Historical Analysis

```bash
# Former actors (with end dates)
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=slutdato%20ne%20null&%24select=navn,startdato,slutdato&%24top=10"

# Actors by period
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24expand=Periode&%24filter=periodeid%20eq%2031&%24select=navn,Periode/titel&%24top=10"
```

## Performance Optimization

### Use Field Selection

```bash
# Good: Only request needed fields
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24select=navn,typeid&%24top=100"

# Avoid: Requesting biography field unnecessarily (very large HTML content)
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24select=biografi&%24top=10"  # Can be 10KB+ per record
```

### Efficient Actor Lookups

```bash
# Fast politician lookup by exact name
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=navn%20eq%20'Nicolai%20Wammen'&%24top=1"

# Efficient type-based filtering
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=typeid%20eq%205&%24select=navn&%24top=100"
```

### Pagination for Large Sets

```bash
# Paginate through all politicians
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=typeid%20eq%205&%24skip=0&%24top=100"
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=typeid%20eq%205&%24skip=100&%24top=100"
```

## Common Use Cases

### 1. Politician Directory

```python
def get_current_politicians():
    """Get all current politicians with party affiliation"""
    filter_query = "typeid eq 5 and slutdato eq null"
    fields = "navn,fornavn,efternavn,gruppenavnkort"
    return get_actors(filter_query=filter_query, select=fields, orderby="efternavn")
```

### 2. Committee Analysis

```python
def get_committees():
    """Get all parliamentary committees"""
    filter_query = "typeid eq 3"
    return get_actors(filter_query=filter_query, select="navn", orderby="navn")
```

### 3. Ministry Mapping

```python
def get_ministries():
    """Get all ministry entities"""
    filter_query = "(typeid eq 1 or typeid eq 8)"
    return get_actors(filter_query=filter_query, select="navn,typeid", orderby="navn")
```

### 4. Voting Record Analysis

```python
def get_politician_votes(politician_name):
    """Get voting records for specific politician"""
    # First get the actor ID
    actor = get_actors(filter_query=f"navn eq '{politician_name}'", top=1)
    if actor['value']:
        actor_id = actor['value'][0]['id']
        # Then get their votes
        return get_votes(filter_query=f"aktørid eq {actor_id}", expand="Afstemning")
```

## Important Notes

### Data Freshness
- **Real-time Updates**: Actor records updated within hours
- **Batch Updates**: Multiple actors often updated simultaneously (same timestamp)
- **Latest Example**: 2025-09-09T17:29:09.407 (multiple politicians updated together)

### Privacy and GDPR Considerations

  **Personal Data Warning**: The `biografi` field contains extensive personal information:
- Birth dates and places
- Family information (spouse names, children)
- Direct contact information (emails, phone numbers)
- Home addresses in some cases
- Complete career histories

**Recommendations:**
- Use biographical data responsibly
- Consider data minimization principles
- Implement appropriate data retention policies
- Be aware of data subject rights under GDPR

### Danish Character Support

 **Perfect UTF-8 Support**: The API handles Danish characters (ø, å, æ) flawlessly:

```bash
# These work perfectly
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=substringof('ø',navn)&%24top=3"
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=substringof('å',navn)&%24top=3"
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=substringof('æ',navn)&%24top=3"
```

### Data Volume Considerations

- **Total Records**: 18,139+ actors (growing)
- **Large Biographical Data**: Biography fields can be 10KB+ per record
- **Pagination Limit**: Maximum 100 records per request
- **Relationship Expansions**: Can significantly increase response size

### Related Entities

The `Aktør` entity connects to many other entities:

- **Aktørtype** - Actor type classifications
- **SagAktør** - Actor roles in cases (23 different role types)
- **DokumentAktør** - Actor roles in documents (25 different role types)
- **Stemme** - Individual voting records
- **MødeAktør** - Meeting participation
- **Periode** - Parliamentary periods

### Example Actor Records

**Politician (typeid=5):**
```json
{
  "id": 12,
  "navn": "Nicolai Wammen",
  "fornavn": "Nicolai", 
  "efternavn": "Wammen",
  "gruppenavnkort": "S",
  "typeid": 5,
  "biografi": "<div>Born 1971...</div>",
  "opdateringsdato": "2025-09-09T17:29:09.407"
}
```

**Committee (typeid=3):**
```json
{
  "id": 1,
  "navn": "FIU Finansudvalget",
  "typeid": 3,
  "opdateringsdato": "2014-09-30T14:56:24.673"
}
```

**Ministry (typeid=8):**
```json
{
  "id": 2,
  "navn": "Finansministeriet",
  "typeid": 8,
  "opdateringsdato": "2014-09-30T14:56:24.673"
}
```

This rich actor data enables comprehensive analysis of Danish parliamentary actors, their roles, relationships, and activities across the entire political system.