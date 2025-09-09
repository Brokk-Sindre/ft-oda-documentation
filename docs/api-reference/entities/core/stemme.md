# Stemme (Individual Votes) Entity

The `Stemme` entity represents individual votes cast by politicians in the Danish Parliament. Each record captures exactly how one politician voted in one voting session, enabling detailed analysis of voting patterns and political behavior. With potentially **hundreds of thousands of records**, this is the most granular level of democratic transparency data.

## Overview

- **Entity Name**: `Stemme`
- **Endpoint**: `https://oda.ft.dk/api/Stemme`
- **Total Records**: Hundreds of thousands (one per politician per voting session)
- **Primary Key**: `id` (Int32)
- **Vote Types**: 4 different vote choices

## Field Reference

### Core Identification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | Int32 | Primary key, unique vote record identifier | `53` |

### Vote Information

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `typeid` | Int32 | Vote type ID (foreign key to Stemmetype) | `1` |

### Relationship Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `afstemningid` | Int32 | Voting session ID (foreign key to Afstemning) | `1` |
| `aktørid` | Int32 | Politician ID (foreign key to Aktør) | `5` |

### Temporal Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `opdateringsdato` | DateTime | Last update timestamp | `"2014-09-09T09:05:59.653"` |

## Vote Types Reference

The API includes 4 different vote types (`Stemmetype`):

| Type ID | Name | Description | Usage |
|---------|------|-------------|-------|
| 1 | For | Yes/In favor | Politician supports the proposal |
| 2 | Imod | No/Against | Politician opposes the proposal |
| 3 | Fravær | Absent | Politician was absent during voting |
| 4 | Hverken for eller imod | Neither for nor against/Abstain | Politician abstained |

## Common Query Examples

### Basic Queries

```bash
# Get latest 5 individual votes
curl "https://oda.ft.dk/api/Stemme?%24top=5&%24orderby=opdateringsdato%20desc"

# Get specific vote by ID
curl "https://oda.ft.dk/api/Stemme(53)"

# Count total individual votes
curl "https://oda.ft.dk/api/Stemme?%24inlinecount=allpages&%24top=1"
```

### Filter by Vote Type

```bash
# All "Yes" votes
curl "https://oda.ft.dk/api/Stemme?%24filter=typeid%20eq%201&%24top=10"

# All "No" votes  
curl "https://oda.ft.dk/api/Stemme?%24filter=typeid%20eq%202&%24top=10"

# All abstentions
curl "https://oda.ft.dk/api/Stemme?%24filter=typeid%20eq%204&%24top=10"

# All absences
curl "https://oda.ft.dk/api/Stemme?%24filter=typeid%20eq%203&%24top=10"
```

### Politician-Specific Queries

```bash
# All votes by specific politician (by ID)
curl "https://oda.ft.dk/api/Stemme?%24filter=aktørid%20eq%205&%24top=100"

# Votes by politician name (requires expansion)
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktør&%24filter=Aktør/navn%20eq%20'Frank%20Aaen'&%24top=50"

# Yes votes by specific politician
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktør&%24filter=Aktør/navn%20eq%20'Frank%20Aaen'%20and%20typeid%20eq%201&%24top=50"
```

### Voting Session Analysis

```bash
# All votes from specific voting session
curl "https://oda.ft.dk/api/Stemme?%24filter=afstemningid%20eq%201&%24top=100"

# Votes from voting session with politician details
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktør&%24filter=afstemningid%20eq%201&%24select=typeid,Aktör/navn&%24top=100"
```

### Vote Distribution Analysis

```bash
# Count votes by type for specific session
curl "https://oda.ft.dk/api/Stemme?%24filter=afstemningid%20eq%201%20and%20typeid%20eq%201&%24inlinecount=allpages&%24top=1"  # Count Yes votes
curl "https://oda.ft.dk/api/Stemme?%24filter=afstemningid%20eq%201%20and%20typeid%20eq%202&%24inlinecount=allpages&%24top=1"  # Count No votes
```

## Relationship Expansion

### Core Relationships

```bash
# Vote with politician details
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktør&%24top=3"

# Vote with voting session details
curl "https://oda.ft.dk/api/Stemme?%24expand=Afstemning&%24top=3"

# Vote with vote type information
curl "https://oda.ft.dk/api/Stemme?%24expand=Stemmetype&%24top=3"
```

### Complete Vote Context

```bash
# Vote with full context (politician, voting session, and meeting)
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktör,Afstemning/Møde&%24top=1"

# Vote with voting session and detailed outcome
curl "https://oda.ft.dk/api/Stemme?%24expand=Afstemning&%24filter=afstemningid%20eq%201&%24select=typeid,Afstemning/konklusion&%24top=10"
```

!!! warning "Large Response Warning"
    Expanding `Aktør` returns extensive biographical data. Use field selection (`$select`) to limit response size when analyzing large datasets.

## Political Analysis Examples

### Individual Politician Analysis

```bash
# Get voting record for specific politician with context
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktør,Afstemning&%24filter=Aktör/navn%20eq%20'Nicolai%20Wammen'&%24select=typeid,Afstemning/nummer,Aktör/gruppenavnkort&%24top=20"

# Politician's Yes votes with voting session details
curl "https://oda.ft.dk/api/Stemme?%24expand=Afstemning&%24filter=aktörid%20eq%205%20and%20typeid%20eq%201&%24select=Afstemning/nummer,Afstemning/konklusion&%24top=20"
```

### Voting Pattern Analysis

```bash
# Find politicians who voted against the majority in specific session
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktör,Afstemning&%24filter=afstemningid%20eq%201%20and%20typeid%20eq%202&%24select=Aktör/navn,Aktör/gruppenavnkort"

# Analyze abstention patterns
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktör&%24filter=typeid%20eq%204&%24select=Aktör/navn,Aktör/gruppenavnkort&%24top=20"
```

### Party Voting Analysis

```bash
# All votes by Social Democrats (party analysis)
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktör&%24filter=Aktör/gruppenavnkort%20eq%20'S'&%24select=typeid&%24top=100"

# Compare party voting on specific session
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktör&%24filter=afstemningid%20eq%201&%24select=typeid,Aktör/gruppenavnkort&%24orderby=Aktör/gruppenavnkort"
```

### Cross-Party Analysis

```bash
# Find votes where parties split (mixed voting within party)
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktör&%24filter=afstemningid%20eq%201&%24select=typeid,Aktör/gruppenavnkort&%24orderby=Aktör/gruppenavnkort,typeid"
```

## Performance Optimization

### Use Field Selection

```bash
# Good: Only request essential fields
curl "https://oda.ft.dk/api/Stemme?%24select=typeid,aktörid,afstemningid&%24top=100"

# Avoid: Expanding full actor biographies for large datasets
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktör&%24top=1000"  # Very large response
```

### Efficient Politician Lookups

```bash
# Better: Use aktörid when known
curl "https://oda.ft.dk/api/Stemme?%24filter=aktörid%20eq%205&%24top=100"

# Less efficient: Filter by name (requires expansion)
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktör&%24filter=Aktör/navn%20eq%20'Name'&%24top=100"
```

### Smart Pagination

```bash
# Paginate through politician's voting record
curl "https://oda.ft.dk/api/Stemme?%24filter=aktörid%20eq%205&%24skip=0&%24top=100&%24orderby=id"
curl "https://oda.ft.dk/api/Stemme?%24filter=aktörid%20eq%205&%24skip=100&%24top=100&%24orderby=id"
```

## Common Use Cases

### 1. Politician Voting Profile

```python
def get_politician_voting_profile(politician_id):
    """Analyze politician's complete voting pattern"""
    
    # Get all votes by this politician
    all_votes = get_votes(filter_query=f"aktörid eq {politician_id}", top=1000)
    
    # Calculate voting statistics
    vote_counts = {}
    for vote in all_votes['value']:
        vote_type = vote['typeid']
        vote_counts[vote_type] = vote_counts.get(vote_type, 0) + 1
    
    return {
        'total_votes': len(all_votes['value']),
        'yes_votes': vote_counts.get(1, 0),
        'no_votes': vote_counts.get(2, 0), 
        'absences': vote_counts.get(3, 0),
        'abstentions': vote_counts.get(4, 0)
    }
```

### 2. Voting Session Analysis

```python
def analyze_voting_session(session_id):
    """Analyze how all politicians voted in a specific session"""
    
    votes = get_votes(
        filter_query=f"afstemningid eq {session_id}",
        expand="Aktör",
        select="typeid,Aktör/navn,Aktör/gruppenavnkort"
    )
    
    # Group by party and vote type
    party_votes = {}
    for vote in votes['value']:
        party = vote['Aktör']['gruppenavnkort']
        vote_type = vote['typeid']
        
        if party not in party_votes:
            party_votes[party] = {'for': 0, 'against': 0, 'absent': 0, 'abstain': 0}
        
        if vote_type == 1:
            party_votes[party]['for'] += 1
        elif vote_type == 2:
            party_votes[party]['against'] += 1
        elif vote_type == 3:
            party_votes[party]['absent'] += 1
        elif vote_type == 4:
            party_votes[party]['abstain'] += 1
    
    return party_votes
```

### 3. Party Loyalty Analysis

```python
def analyze_party_loyalty(party_code, num_sessions=50):
    """Analyze how unified a party votes"""
    
    # Get recent voting sessions
    recent_sessions = get_voting_sessions(top=num_sessions, orderby="opdateringsdato desc")
    
    party_unity_scores = []
    
    for session in recent_sessions['value']:
        session_id = session['id']
        
        # Get party votes for this session
        party_votes = get_votes(
            filter_query=f"afstemningid eq {session_id} and Aktör/gruppenavnkort eq '{party_code}'",
            expand="Aktör"
        )
        
        # Calculate unity (most common vote / total votes)
        if party_votes['value']:
            vote_types = [v['typeid'] for v in party_votes['value']]
            most_common_count = max(vote_types.count(vt) for vt in set(vote_types))
            unity_score = most_common_count / len(vote_types)
            party_unity_scores.append(unity_score)
    
    return {
        'average_unity': sum(party_unity_scores) / len(party_unity_scores) if party_unity_scores else 0,
        'sessions_analyzed': len(party_unity_scores)
    }
```

### 4. Cross-Party Coalition Analysis

```python
def find_cross_party_coalitions(session_id):
    """Find which parties voted together in a specific session"""
    
    votes = get_votes(
        filter_query=f"afstemningid eq {session_id}",
        expand="Aktör",
        select="typeid,Aktör/gruppenavnkort"
    )
    
    # Group parties by how they voted
    coalitions = {'for': [], 'against': [], 'mixed': []}
    party_vote_distribution = {}
    
    # First, count votes by party
    for vote in votes['value']:
        party = vote['Aktör']['gruppenavnkort']
        vote_type = vote['typeid']
        
        if party not in party_vote_distribution:
            party_vote_distribution[party] = {'for': 0, 'against': 0, 'other': 0}
        
        if vote_type == 1:
            party_vote_distribution[party]['for'] += 1
        elif vote_type == 2:
            party_vote_distribution[party]['against'] += 1
        else:
            party_vote_distribution[party]['other'] += 1
    
    # Categorize parties by their majority vote
    for party, votes_count in party_vote_distribution.items():
        total = sum(votes_count.values())
        for_pct = votes_count['for'] / total
        against_pct = votes_count['against'] / total
        
        if for_pct > 0.8:  # 80% voted for
            coalitions['for'].append(party)
        elif against_pct > 0.8:  # 80% voted against
            coalitions['against'].append(party)
        else:
            coalitions['mixed'].append(party)
    
    return coalitions
```

## Important Notes

### Data Volume and Scale

- **Massive Dataset**: Each voting session can have 100+ individual vote records
- **Historical Depth**: Records going back many years
- **Growth Pattern**: New records created with each parliamentary vote
- **Typical Session**: 100-179 politicians voting = 100-179 `Stemme` records per `Afstemning`

### Performance Considerations

  **Large Dataset Warning**: This entity contains potentially hundreds of thousands of records. Always use appropriate filtering:

```bash
# L Dangerous: Could return massive dataset
curl "https://oda.ft.dk/api/Stemme?%24top=10000"

# ✅ Safe: Always filter by politician or voting session
curl "https://oda.ft.dk/api/Stemme?%24filter=aktörid%20eq%205&%24top=100"
curl "https://oda.ft.dk/api/Stemme?%24filter=afstemningid%20eq%201"
```

### Data Quality and Completeness

- **Complete Vote Records**: Every politician's vote in every session is recorded
- **No Partial Data**: If a politician was absent, it's recorded as `typeid=3` (Fravær)
- **Referential Integrity**: All `aktörid` values correspond to valid `Aktör` records
- **Consistent Timestamps**: All votes from same session have identical `opdateringsdato`

### Privacy and Transparency

✅ **Public Information**: All voting records are public information in Danish democracy
✅ **Democratic Transparency**: Citizens have the right to know how their representatives voted
✅ **Historical Record**: Complete voting history preserved for accountability

### Related Entities

The `Stemme` entity is central to the parliamentary voting system:

- **Aktör** - The politician who cast the vote
- **Afstemning** - The voting session where the vote was cast
- **Stemmetype** - The type of vote (For/Against/Absent/Abstain)
- **Møde** - Through `Afstemning`, connects to the meeting where voting occurred

### Example Records

**"Yes" Vote:**
```json
{
  "id": 53,
  "typeid": 1,
  "afstemningid": 1,
  "aktörid": 5,
  "opdateringsdato": "2014-09-09T09:05:59.653"
}
```

**"No" Vote:**
```json
{
  "id": 54,
  "typeid": 2,
  "afstemningid": 1,
  "aktörid": 6,
  "opdateringsdato": "2014-09-09T09:05:59.653"
}
```

**Abstention:**
```json
{
  "id": 55,
  "typeid": 4,
  "afstemningid": 1,
  "aktörid": 7,
  "opdateringsdato": "2014-09-09T09:05:59.653"
}
```

The `Stemme` entity provides the atomic unit of democratic decision-making in the Danish Parliament, enabling unprecedented analysis of how individual politicians vote and how democratic decisions are actually made at the most granular level.