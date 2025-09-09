# Afstemning (Voting Sessions) Entity

The `Afstemning` entity represents voting sessions in the Danish Parliament, capturing when and how parliamentary votes were conducted. Each voting session contains detailed results and connects to individual vote records through the `Stemme` entity.

## Overview

- **Entity Name**: `Afstemning`
- **Endpoint**: `https://oda.ft.dk/api/Afstemning`
- **Total Records**: Thousands of voting sessions
- **Primary Key**: `id` (Int32)
- **Voting Types**: 4 different session types

## Field Reference

### Core Identification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | Int32 | Primary key, unique voting session identifier | `1` |
| `nummer` | Int32 | Voting session number | `411` |

### Results and Outcome

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `konklusion` | String | Detailed voting conclusion with party breakdown | `"Vedtaget\n\n108 stemmer for forslaget (V, S, DF...)\n\n0 stemmer imod forslaget"` |
| `vedtaget` | Boolean | Whether the proposal was adopted | `true` |

### Classification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `typeid` | Int32 | Voting type ID (foreign key to Afstemningstype) | `2` |

### Relationship Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `mødeid` | Int32 | Meeting ID (foreign key to Møde) | `17` |
| `sagstrinid` | Int32 | Case step ID (foreign key to Sagstrin) | `null` |

### Temporal Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `opdateringsdato` | DateTime | Last update timestamp | `"2025-09-09T12:30:12.467"` |

## Voting Types Reference

The API includes 4 different voting session types (`Afstemningstype`):

| Type ID | Name | Description | Purpose |
|---------|------|-------------|---------|
| 1 | Endelig vedtagelse | Final Adoption | Final vote on legislation |
| 2 | Udvalgsindstilling | Committee Recommendation | Committee recommendations |
| 3 | Forslag til vedtagelse | Adoption Proposal | Proposal adoption votes |
| 4 | Ændringsforslag | Amendment | Amendment votes |

## Common Query Examples

### Basic Queries

```bash
# Get latest 5 voting sessions
curl "https://oda.ft.dk/api/Afstemning?%24top=5&%24orderby=opdateringsdato%20desc"

# Get specific voting session by ID
curl "https://oda.ft.dk/api/Afstemning(1)"

# Count total voting sessions
curl "https://oda.ft.dk/api/Afstemning?%24inlinecount=allpages&%24top=1"
```

### Filter by Voting Type

```bash
# Final adoption votes only
curl "https://oda.ft.dk/api/Afstemning?%24filter=typeid%20eq%201&%24top=10"

# Committee recommendations
curl "https://oda.ft.dk/api/Afstemning?%24filter=typeid%20eq%202&%24top=10"

# Amendment votes
curl "https://oda.ft.dk/api/Afstemning?%24filter=typeid%20eq%204&%24top=10"
```

### Filter by Outcome

```bash
# Adopted proposals only
curl "https://oda.ft.dk/api/Afstemning?%24filter=vedtaget%20eq%20true&%24top=10"

# Rejected proposals
curl "https://oda.ft.dk/api/Afstemning?%24filter=vedtaget%20eq%20false&%24top=10"
```

### Recent Voting Activity

```bash
# Today's votes
curl "https://oda.ft.dk/api/Afstemning?%24filter=opdateringsdato%20gt%20datetime'2025-09-09T00:00:00'&%24orderby=opdateringsdato%20desc"

# This week's votes
curl "https://oda.ft.dk/api/Afstemning?%24filter=opdateringsdato%20gt%20datetime'2025-09-02T00:00:00'&%24orderby=opdateringsdato%20desc"
```

### Search by Voting Number

```bash
# Specific voting session number
curl "https://oda.ft.dk/api/Afstemning?%24filter=nummer%20eq%20532"

# Recent voting session numbers
curl "https://oda.ft.dk/api/Afstemning?%24filter=nummer%20gt%20530&%24orderby=nummer%20desc"
```

### Field Selection

```bash
# Only essential fields
curl "https://oda.ft.dk/api/Afstemning?%24select=id,nummer,vedtaget,opdateringsdato&%24top=10"

# Voting results only
curl "https://oda.ft.dk/api/Afstemning?%24select=nummer,konklusion,vedtaget&%24top=5"
```

## Relationship Expansion

### Core Relationships

```bash
# Voting session with meeting details
curl "https://oda.ft.dk/api/Afstemning?%24expand=Møde&%24top=3"

# Voting session with type information
curl "https://oda.ft.dk/api/Afstemning?%24expand=Afstemningstype&%24top=3"

# Voting session with case step
curl "https://oda.ft.dk/api/Afstemning?%24expand=Sagstrin&%24top=3"
```

### Individual Vote Analysis

```bash
# Voting session with all individual votes
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme&%24top=1"

# Voting session with individual votes and politician details
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme/Aktør&%24top=1"
```

!!! warning "Large Response Warning"
    Expanding `Stemme/Aktør` returns extensive biographical data for each politician who voted. Use carefully with small `$top` values.

### Meeting Context

```bash
# Full meeting context with agenda
curl "https://oda.ft.dk/api/Afstemning?%24expand=Møde/Dagsordenspunkt&%24top=2"
```

## Data Analysis Examples

### Voting Pattern Analysis

```bash
# Unanimous votes (all adopted)
curl "https://oda.ft.dk/api/Afstemning?%24filter=vedtaget%20eq%20true%20and%20substringof('0%20stemmer%20imod',konklusion)&%24top=10"

# Close votes (controversial decisions)
curl "https://oda.ft.dk/api/Afstemning?%24filter=substringof('stemmer%20imod',konklusion)%20and%20not%20substringof('0%20stemmer%20imod',konklusion)&%24top=10"
```

### Party Voting Analysis

```bash
# Search for specific party involvement in voting conclusions
curl "https://oda.ft.dk/api/Afstemning?%24filter=substringof('Socialdemokratiet',konklusion)&%24top=5"

# Find votes with abstentions
curl "https://oda.ft.dk/api/Afstemning?%24filter=substringof('hverken%20for',konklusion)&%24top=5"
```

### Legislative Process Analysis

```bash
# Final adoption votes with individual vote details
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme&%24filter=typeid%20eq%201&%24top=3"

# Track amendment voting patterns
curl "https://oda.ft.dk/api/Afstemning?%24filter=typeid%20eq%204&%24select=nummer,konklusion,vedtaget&%24top=10"
```

### Meeting-Based Analysis

```bash
# All votes from specific meeting
curl "https://oda.ft.dk/api/Afstemning?%24expand=Møde&%24filter=mødeid%20eq%2017&%24select=nummer,konklusion,Møde/titel"
```

## Performance Optimization

### Use Field Selection

```bash
# Good: Only request needed fields
curl "https://oda.ft.dk/api/Afstemning?%24select=id,nummer,vedtaget&%24top=100"

# Avoid: Large konklusion field when not needed
curl "https://oda.ft.dk/api/Afstemning?%24select=konklusion&%24top=100"  # Can be large text blocks
```

### Efficient Pagination

```bash
# Paginate through voting sessions
curl "https://oda.ft.dk/api/Afstemning?%24skip=0&%24top=100&%24orderby=id"
curl "https://oda.ft.dk/api/Afstemning?%24skip=100&%24top=100&%24orderby=id"
```

### Smart Expansion

```bash
# Only expand when you need the relationship data
curl "https://oda.ft.dk/api/Afstemning?%24expand=Møde&%24filter=mødeid%20eq%2017&%24top=5"
```

## Understanding Voting Results

### Konklusion Field Format

The `konklusion` field contains detailed voting breakdowns in Danish:

```
Vedtaget

108 stemmer for forslaget (V, S, DF, RV, SF, EL, LA, KF, UFG)

0 stemmer imod forslaget
```

**Format elements:**
- **Outcome**: `Vedtaget` (Adopted) or `Forkastet` (Rejected)
- **For votes**: `X stemmer for forslaget` + party abbreviations
- **Against votes**: `Y stemmer imod forslaget` + party abbreviations
- **Abstentions**: `Z hverken for eller imod` (when present)

### Party Abbreviations

Common Danish parliamentary party abbreviations found in voting conclusions:

- **V** - Venstre (Liberal Party)
- **S** - Socialdemokratiet (Social Democrats)
- **DF** - Dansk Folkeparti (Danish People's Party)
- **RV** - Radikale Venstre (Social Liberals)
- **SF** - Socialistisk Folkeparti (Socialist People's Party)
- **EL** - Enhedslisten (Red-Green Alliance)
- **LA** - Liberal Alliance
- **KF** - Konservative Folkeparti (Conservative Party)
- **UFG** - Uden for folketingsgrupperne (Independent)

## Common Use Cases

### 1. Recent Parliamentary Activity Monitor

```python
def get_recent_votes(hours_back=24):
    """Get voting sessions from last 24 hours"""
    since = (datetime.now() - timedelta(hours=hours_back)).isoformat()
    filter_query = f"opdateringsdato gt datetime'{since}'"
    return get_voting_sessions(
        filter_query=filter_query, 
        select="nummer,konklusion,vedtaget,opdateringsdato",
        orderby="opdateringsdato desc"
    )
```

### 2. Voting Pattern Analysis

```python
def analyze_voting_patterns(politician_name):
    """Analyze how a politician votes"""
    # Get voting sessions with this politician's votes
    filter_query = f"Stemme/any(s: s/Aktør/navn eq '{politician_name}')"
    return get_voting_sessions(
        filter_query=filter_query,
        expand="Stemme/Aktør",
        top=50
    )
```

### 3. Controversial Vote Finder

```python
def find_controversial_votes():
    """Find close/controversial votes"""
    # Look for votes that mention opposition
    filter_query = "substringof('stemmer imod', konklusion) and not substringof('0 stemmer imod', konklusion)"
    return get_voting_sessions(
        filter_query=filter_query,
        select="nummer,konklusion,vedtaget",
        orderby="opdateringsdato desc"
    )
```

### 4. Meeting Voting Summary

```python
def get_meeting_votes(meeting_id):
    """Get all votes from a specific meeting"""
    filter_query = f"mødeid eq {meeting_id}"
    return get_voting_sessions(
        filter_query=filter_query,
        expand="Møde",
        select="nummer,konklusion,vedtaget,Møde/titel",
        orderby="nummer"
    )
```

## Important Notes

### Data Freshness
- **Real-time Updates**: Voting sessions updated within hours of parliamentary activity
- **Latest Example**: 2025-09-09T12:30:12.467 (session #532, same day)
- **Business Hours**: Most updates during parliamentary session times

### Voting Session Numbers
- **Sequential**: Session numbers increment sequentially (e.g., 530, 531, 532)
- **Unique**: Each voting session has a unique number within the parliamentary system
- **Historical**: Numbers continue across parliamentary periods

### Individual Vote Tracking
Each `Afstemning` connects to multiple `Stemme` records:
- One `Stemme` record per politician who voted
- Vote types: For (1), Against (2), Absent (3), Abstain (4)
- Full politician biographical data available through expansion

### Performance Considerations
- **Large Expansions**: `Stemme/Aktør` expansion can return 100+ records with full biographical data
- **Pagination**: Use `$top` and `$skip` for large result sets
- **Field Selection**: `konklusion` field can be large text blocks

### Related Entities

The `Afstemning` entity connects to:

- **Afstemningstype** - Voting session types (4 types)
- **Stemme** - Individual vote records (one per politician)
- **Møde** - Parliamentary meetings where votes occurred
- **Sagstrin** - Case steps (when vote relates to specific legislation)
- **Aktør** - Through `Stemme` entity, connects to all voting politicians

### Example Records

**Final Adoption Vote:**
```json
{
  "id": 10377,
  "nummer": 532,
  "konklusion": "Vedtaget\n\n108 stemmer for forslaget (V, S, DF, RV, SF, EL, LA, KF, UFG)\n\n0 stemmer imod forslaget",
  "vedtaget": true,
  "mødeid": 17,
  "typeid": 1,
  "opdateringsdato": "2025-09-09T12:30:12.467"
}
```

**Committee Recommendation:**
```json
{
  "id": 1,
  "nummer": 411,
  "konklusion": "Vedtaget\n\n108 stemmer for forslaget (V, S, DF, RV, SF, EL, LA, KF, UFG)\n\n0 stemmer imod forslaget",
  "vedtaget": true,
  "mødeid": 17,
  "typeid": 2,
  "sagstrinid": null,
  "opdateringsdato": "2014-09-09T09:05:59.653"
}
```

The `Afstemning` entity provides the foundation for analyzing Danish parliamentary democracy in action, showing how decisions are made and which actors participate in the democratic process.