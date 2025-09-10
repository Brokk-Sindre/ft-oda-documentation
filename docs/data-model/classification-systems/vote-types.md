# Vote Type Classifications (Stemmetype)

The Danish Parliamentary vote type system provides a complete and precise framework for recording individual voting behavior in parliamentary decisions. With **4 distinct vote classifications**, this system captures every possible voting choice available to members of parliament, including the critical distinction between absence and abstention.

## Overview

Each individual vote (Stemme) cast by a parliamentary actor is classified according to one of four standardized vote types. This classification system has remained stable since the API's inception, providing consistent categorization for voting analysis across all parliamentary periods.

**Key Characteristics:**
- **4 comprehensive vote types** - Complete coverage of all voting choices
- **Absence vs Abstention distinction** - Differentiates non-participation from deliberate abstention
- **Binary opposition structure** - Clear For/Against choices with neutral alternatives
- **Universal applicability** - Used across all voting procedures and session types
- **Historical consistency** - Stable classification since 2014

## Complete Stemmetype Reference

### 1. For (In Favor)
**ID:** 1  
**Danish:** For  
**English:** For/In Favor/Yes  
**Meaning:** Member voted in support of the proposal, motion, or question  
**Parliamentary Context:** Positive endorsement of the matter under consideration  
**Statistical Weight:** +1 in favor calculations

**Usage Patterns:**
- Primary choice for supporting legislation
- Endorsement of amendments and modifications  
- Agreement with committee recommendations
- Support for procedural motions

### 2. Imod (Against)
**ID:** 2  
**Danish:** Imod  
**English:** Against/Opposed/No  
**Meaning:** Member voted in opposition to the proposal, motion, or question  
**Parliamentary Context:** Explicit rejection or disagreement with the matter  
**Statistical Weight:** +1 in opposition calculations

**Usage Patterns:**
- Opposition to proposed legislation
- Rejection of amendments
- Disagreement with committee conclusions
- Opposition to procedural decisions

### 3. Fravær (Absence)
**ID:** 3  
**Danish:** Fravær  
**English:** Absence/Not Present  
**Meaning:** Member was not present during the voting session  
**Parliamentary Context:** Physical absence from the voting process  
**Statistical Weight:** Excluded from voting calculations

**Important Distinctions:**
- **Involuntary non-participation** - Member could not vote due to absence
- **Not counted in quorum** for vote validity calculations
- **Different from abstention** - No deliberate choice was made
- **Common causes:** Illness, travel, scheduling conflicts, other parliamentary duties

**Analysis Considerations:**
- High absence rates may indicate scheduling issues or strategic behavior
- Absence patterns can reveal member priorities and engagement levels
- Should be excluded from voting alignment analysis
- Important for quorum and participation rate calculations

### 4. Hverken for eller imod (Neither For Nor Against)
**ID:** 4  
**Danish:** Hverken for eller imod  
**English:** Neither For Nor Against/Abstain/Neutral  
**Meaning:** Member deliberately chose not to support either side  
**Parliamentary Context:** Conscious decision to remain neutral on the matter  
**Statistical Weight:** +1 in abstention calculations, excluded from For/Against ratios

**Abstention Motivations:**
- **Conflict of interest** - Personal or financial interests in the outcome
- **Insufficient information** - Need for more data before deciding
- **Partial agreement** - Support for some aspects but not others
- **Strategic positioning** - Political calculation for future negotiations
- **Conscience clause** - Personal moral or ethical reservations
- **Party discipline conflicts** - Personal disagreement with party position

**Parliamentary Procedures:**
- Counted as present for quorum purposes
- Recorded as deliberate choice in parliamentary records
- May be accompanied by explanatory statements
- Distinct parliamentary significance from absence

## Voting Session Types and Classification

### Standard Legislative Votes
The four vote types apply universally across all parliamentary voting procedures:

**First Reading Votes:**
- Initial consideration of proposed legislation
- Full vote type spectrum typically utilized
- High strategic value for party positioning

**Second Reading Votes:**
- Detailed consideration after committee review
- Amendment votes may show complex patterns
- Abstentions often indicate negotiation dynamics

**Third Reading Votes:**
- Final passage votes on legislation
- Typically highest participation rates
- Clearest For/Against divisions

### Amendment and Procedural Votes
Vote type usage patterns differ for procedural matters:

**Amendment Votes:**
- More frequent abstentions due to complexity
- Tactical voting behaviors more common
- Coalition dynamics clearly visible

**Procedural Motions:**
- Often unanimous or near-unanimous
- Absence patterns may indicate informal agreement
- Quick voting procedures with limited debate

## Vote Aggregation and Statistical Analysis

### Basic Vote Statistics

```python
# Calculate basic voting statistics for a specific voting session
import requests

def analyze_voting_session(afstemning_id):
    """Analyze vote distribution for a specific voting session."""
    
    # Fetch all votes for the session
    response = requests.get(
        f"https://oda.ft.dk/api/Stemme?%24filter=afstemningid%20eq%20{afstemning_id}&%24expand=Stemmetype"
    )
    votes = response.json()['value']
    
    # Count votes by type
    vote_counts = {
        'For': 0,
        'Imod': 0, 
        'Fravær': 0,
        'Hverken for eller imod': 0
    }
    
    for vote in votes:
        vote_type = vote['Stemmetype']['type']
        vote_counts[vote_type] += 1
    
    # Calculate percentages and participation
    total_votes = sum(vote_counts.values())
    participating_votes = total_votes - vote_counts['Fravær']
    
    results = {
        'total_members': total_votes,
        'participation_rate': (participating_votes / total_votes) * 100,
        'for_percentage': (vote_counts['For'] / participating_votes) * 100 if participating_votes > 0 else 0,
        'against_percentage': (vote_counts['Imod'] / participating_votes) * 100 if participating_votes > 0 else 0,
        'abstention_rate': (vote_counts['Hverken for eller imod'] / total_votes) * 100,
        'absence_rate': (vote_counts['Fravær'] / total_votes) * 100,
        'vote_counts': vote_counts
    }
    
    return results

# Example usage
session_stats = analyze_voting_session(4249)
print(f"Participation Rate: {session_stats['participation_rate']:.1f}%")
print(f"Support Level: {session_stats['for_percentage']:.1f}%") 
print(f"Opposition Level: {session_stats['against_percentage']:.1f}%")
```

### Advanced Voting Pattern Analysis

```python
def analyze_member_voting_patterns(aktor_id, period_id=None):
    """Analyze voting patterns for a specific parliamentary member."""
    
    # Build query with optional period filter
    query = f"https://oda.ft.dk/api/Stemme?%24filter=aktørid%20eq%20{aktor_id}"
    if period_id:
        query += f"%20and%20Afstemning/periodeid%20eq%20{period_id}"
    query += "&%24expand=Stemmetype,Afstemning(%24expand=Sag)"
    
    response = requests.get(query)
    votes = response.json()['value']
    
    # Analyze voting behavior
    patterns = {
        'total_votes': len(votes),
        'vote_distribution': {},
        'participation_rate': 0,
        'alignment_scores': {},
        'case_types': {}
    }
    
    # Count vote types
    for vote in votes:
        vote_type = vote['Stemmetype']['type']
        patterns['vote_distribution'][vote_type] = patterns['vote_distribution'].get(vote_type, 0) + 1
        
        # Analyze by case type
        if 'Afstemning' in vote and 'Sag' in vote['Afstemning']:
            case_type = vote['Afstemning']['Sag']['typeid']
            if case_type not in patterns['case_types']:
                patterns['case_types'][case_type] = {'For': 0, 'Imod': 0, 'Abstain': 0, 'Absent': 0}
            
            if vote_type == 'For':
                patterns['case_types'][case_type]['For'] += 1
            elif vote_type == 'Imod':
                patterns['case_types'][case_type]['Against'] += 1
            elif vote_type == 'Hverken for eller imod':
                patterns['case_types'][case_type]['Abstain'] += 1
            else:
                patterns['case_types'][case_type]['Absent'] += 1
    
    # Calculate participation rate
    absent_votes = patterns['vote_distribution'].get('Fravær', 0)
    patterns['participation_rate'] = ((patterns['total_votes'] - absent_votes) / patterns['total_votes']) * 100
    
    return patterns

# Example: Analyze voting patterns for a specific member
member_patterns = analyze_member_voting_patterns(5, period_id=20)
print(f"Member Participation Rate: {member_patterns['participation_rate']:.1f}%")
print("Vote Distribution:", member_patterns['vote_distribution'])
```

## Historical Voting Behavior Analysis

### Temporal Voting Trends

```python
def analyze_voting_trends_over_time(start_date, end_date):
    """Analyze how voting behavior patterns change over time."""
    
    query = f"""https://oda.ft.dk/api/Afstemning?%24filter=dato%20ge%20datetime'{start_date}'%20and%20dato%20le%20datetime'{end_date}'&%24expand=Stemme(%24expand=Stemmetype)&%24orderby=dato"""
    
    response = requests.get(query)
    sessions = response.json()['value']
    
    monthly_trends = {}
    
    for session in sessions:
        date = session['dato'][:7]  # YYYY-MM format
        
        if date not in monthly_trends:
            monthly_trends[date] = {
                'total_sessions': 0,
                'avg_participation': 0,
                'avg_abstention': 0,
                'vote_types': {'For': 0, 'Imod': 0, 'Fravær': 0, 'Hverken for eller imod': 0}
            }
        
        monthly_trends[date]['total_sessions'] += 1
        
        # Calculate session statistics
        if 'Stemme' in session:
            votes = session['Stemme']
            total_votes = len(votes)
            
            session_counts = {'For': 0, 'Imod': 0, 'Fravær': 0, 'Hverken for eller imod': 0}
            for vote in votes:
                vote_type = vote['Stemmetype']['type']
                session_counts[vote_type] += 1
                monthly_trends[date]['vote_types'][vote_type] += 1
            
            # Update averages
            absent = session_counts['Fravær']
            abstain = session_counts['Hverken for eller imod']
            
            participation = ((total_votes - absent) / total_votes) * 100 if total_votes > 0 else 0
            abstention = (abstain / total_votes) * 100 if total_votes > 0 else 0
            
            # Running average calculation
            sessions_count = monthly_trends[date]['total_sessions']
            monthly_trends[date]['avg_participation'] = (
                (monthly_trends[date]['avg_participation'] * (sessions_count - 1) + participation) / sessions_count
            )
            monthly_trends[date]['avg_abstention'] = (
                (monthly_trends[date]['avg_abstention'] * (sessions_count - 1) + abstention) / sessions_count
            )
    
    return monthly_trends

# Example: Analyze trends from 2020 to present
trends = analyze_voting_trends_over_time('2020-01-01T00:00:00', '2024-12-31T23:59:59')
```

### Party Voting Cohesion Analysis

```python
def analyze_party_voting_cohesion(party_id, afstemning_id):
    """Calculate party voting cohesion for a specific vote."""
    
    # Get all party members who voted
    query = f"""https://oda.ft.dk/api/Stemme?%24filter=afstemningid%20eq%20{afstemning_id}&%24expand=Aktør(%24filter=typeid%20eq%205%20and%20Partier/any(p:%20p/id%20eq%20{party_id})),Stemmetype"""
    
    response = requests.get(query)
    votes = response.json()['value']
    
    # Filter to only party member votes
    party_votes = [v for v in votes if 'Aktør' in v and v['Aktør']]
    
    if not party_votes:
        return {'cohesion_score': 0, 'vote_distribution': {}, 'unity_type': 'no_data'}
    
    # Count vote types (excluding absences from cohesion calculation)
    vote_counts = {'For': 0, 'Imod': 0, 'Hverken for eller imod': 0}
    total_participating = 0
    
    for vote in party_votes:
        vote_type = vote['Stemmetype']['type']
        if vote_type != 'Fravær':
            vote_counts[vote_type] += 1
            total_participating += 1
    
    if total_participating == 0:
        return {'cohesion_score': 0, 'vote_distribution': vote_counts, 'unity_type': 'all_absent'}
    
    # Calculate cohesion score
    max_agreement = max(vote_counts.values())
    cohesion_score = (max_agreement / total_participating) * 100
    
    # Determine unity type
    if cohesion_score == 100:
        unity_type = 'unanimous'
    elif cohesion_score >= 90:
        unity_type = 'high_cohesion'
    elif cohesion_score >= 75:
        unity_type = 'moderate_cohesion'
    elif cohesion_score >= 50:
        unity_type = 'low_cohesion'
    else:
        unity_type = 'divided'
    
    return {
        'cohesion_score': cohesion_score,
        'vote_distribution': vote_counts,
        'unity_type': unity_type,
        'participating_members': total_participating,
        'total_members': len(party_votes)
    }
```

## API Querying Strategies

### Basic Vote Type Queries

```bash
# Get all vote types
curl "https://oda.ft.dk/api/Stemmetype"

# Get specific vote type details
curl "https://oda.ft.dk/api/Stemmetype(1)"

# Get all votes of a specific type
curl "https://oda.ft.dk/api/Stemme?%24filter=typeid%20eq%201&%24top=100"
```

### Advanced Filtering by Vote Type

```bash
# Get all "For" votes in recent voting sessions
curl "https://oda.ft.dk/api/Stemme?%24filter=typeid%20eq%201%20and%20Afstemning/dato%20ge%20datetime'2024-01-01'&%24expand=Afstemning,Aktør&%24top=1000"

# Find all abstentions (Hverken for eller imod) for a specific case
curl "https://oda.ft.dk/api/Stemme?%24filter=typeid%20eq%204%20and%20Afstemning/sagid%20eq%201234&%24expand=Aktør,Stemmetype"

# Analyze absence patterns for a specific period
curl "https://oda.ft.dk/api/Stemme?%24filter=typeid%20eq%203%20and%20Afstemning/periodeid%20eq%2020&%24expand=Aktør&%24top=5000"
```

### Complex Vote Analysis Queries

```bash
# Compare voting patterns between parties
curl "https://oda.ft.dk/api/Stemme?%24filter=afstemningid%20eq%204249&%24expand=Aktør(%24expand=Partier),Stemmetype&%24top=200"

# Find cases with high abstention rates
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme(%24expand=Stemmetype)&%24filter=Stemme/any(s:%20s/typeid%20eq%204)&%24top=100"

# Analyze individual member voting consistency
curl "https://oda.ft.dk/api/Stemme?%24filter=aktørid%20eq%205&%24expand=Stemmetype,Afstemning(%24expand=Sag)&%24orderby=Afstemning/dato%20desc&%24top=500"
```

## Cross-References with Related Entities

### Voting Sessions (Afstemning)
Each vote is linked to a specific voting session through `afstemningid`:

```python
# Get vote type distribution for a specific voting session
def get_session_vote_breakdown(afstemning_id):
    query = f"https://oda.ft.dk/api/Afstemning({afstemning_id})?%24expand=Stemme(%24expand=Stemmetype)"
    response = requests.get(query)
    session = response.json()
    
    breakdown = {}
    for vote in session.get('Stemme', []):
        vote_type = vote['Stemmetype']['type']
        breakdown[vote_type] = breakdown.get(vote_type, 0) + 1
    
    return breakdown
```

### Parliamentary Actors (Aktør)
Vote types reveal individual and institutional voting behavior:

```python
# Analyze an actor's voting type preferences
def actor_vote_preferences(aktor_id, limit=1000):
    query = f"https://oda.ft.dk/api/Stemme?%24filter=aktørid%20eq%20{aktor_id}&%24expand=Stemmetype&%24top={limit}"
    response = requests.get(query)
    votes = response.json()['value']
    
    preferences = {}
    for vote in votes:
        vote_type = vote['Stemmetype']['type']
        preferences[vote_type] = preferences.get(vote_type, 0) + 1
    
    return preferences
```

### Cases and Legislation (Sag)
Vote type patterns reveal case complexity and controversy:

```python
# Analyze vote type patterns by case type
def case_voting_patterns(sag_id):
    query = f"https://oda.ft.dk/api/Afstemning?%24filter=sagid%20eq%20{sag_id}&%24expand=Stemme(%24expand=Stemmetype)"
    response = requests.get(query)
    sessions = response.json()['value']
    
    case_patterns = {
        'total_sessions': len(sessions),
        'vote_evolution': [],
        'overall_distribution': {'For': 0, 'Imod': 0, 'Fravær': 0, 'Hverken for eller imod': 0}
    }
    
    for session in sessions:
        session_breakdown = {}
        for vote in session.get('Stemme', []):
            vote_type = vote['Stemmetype']['type']
            session_breakdown[vote_type] = session_breakdown.get(vote_type, 0) + 1
            case_patterns['overall_distribution'][vote_type] += 1
        
        case_patterns['vote_evolution'].append({
            'date': session['dato'],
            'votes': session_breakdown
        })
    
    return case_patterns
```

## Vote Type Validation and Data Quality

### Data Integrity Checks

```python
def validate_vote_type_data():
    """Perform comprehensive vote type data validation."""
    
    # Check vote type enumeration completeness
    response = requests.get("https://oda.ft.dk/api/Stemmetype")
    vote_types = response.json()['value']
    
    validation_results = {
        'vote_type_count': len(vote_types),
        'expected_types': ['For', 'Imod', 'Fravær', 'Hverken for eller imod'],
        'missing_types': [],
        'unexpected_types': [],
        'id_consistency': True,
        'orphaned_votes': 0
    }
    
    # Validate expected vote types exist
    actual_types = [vt['type'] for vt in vote_types]
    for expected in validation_results['expected_types']:
        if expected not in actual_types:
            validation_results['missing_types'].append(expected)
    
    for actual in actual_types:
        if actual not in validation_results['expected_types']:
            validation_results['unexpected_types'].append(actual)
    
    # Check for consistent ID mapping
    expected_ids = {1: 'For', 2: 'Imod', 3: 'Fravær', 4: 'Hverken for eller imod'}
    for vote_type in vote_types:
        expected_type = expected_ids.get(vote_type['id'])
        if expected_type != vote_type['type']:
            validation_results['id_consistency'] = False
    
    # Check for orphaned votes (votes with invalid type IDs)
    response = requests.get("https://oda.ft.dk/api/Stemme?%24filter=typeid%20gt%204%20or%20typeid%20lt%201&%24top=100")
    orphaned = response.json()['value']
    validation_results['orphaned_votes'] = len(orphaned)
    
    return validation_results
```

### Quality Metrics and Monitoring

```python
def calculate_vote_quality_metrics(period_id=None):
    """Calculate data quality metrics for vote type data."""
    
    query = "https://oda.ft.dk/api/Stemme?%24expand=Stemmetype,Afstemning"
    if period_id:
        query += f"&%24filter=Afstemning/periodeid%20eq%20{period_id}"
    query += "&%24top=10000"
    
    response = requests.get(query)
    votes = response.json()['value']
    
    metrics = {
        'total_votes': len(votes),
        'valid_type_assignments': 0,
        'missing_type_data': 0,
        'participation_rates': [],
        'abstention_rates': [],
        'data_completeness': 0
    }
    
    session_stats = {}
    
    for vote in votes:
        # Check vote type data validity
        if 'Stemmetype' in vote and vote['Stemmetype']:
            metrics['valid_type_assignments'] += 1
        else:
            metrics['missing_type_data'] += 1
        
        # Group by voting session for participation analysis
        session_id = vote['afstemningid']
        if session_id not in session_stats:
            session_stats[session_id] = {'total': 0, 'absent': 0, 'abstain': 0}
        
        session_stats[session_id]['total'] += 1
        
        if vote['Stemmetype']['type'] == 'Fravær':
            session_stats[session_id]['absent'] += 1
        elif vote['Stemmetype']['type'] == 'Hverken for eller imod':
            session_stats[session_id]['abstain'] += 1
    
    # Calculate session-level metrics
    for session in session_stats.values():
        participation_rate = ((session['total'] - session['absent']) / session['total']) * 100
        abstention_rate = (session['abstain'] / session['total']) * 100
        
        metrics['participation_rates'].append(participation_rate)
        metrics['abstention_rates'].append(abstention_rate)
    
    # Calculate overall data completeness
    metrics['data_completeness'] = (metrics['valid_type_assignments'] / metrics['total_votes']) * 100
    
    # Calculate statistical summaries
    if metrics['participation_rates']:
        metrics['avg_participation'] = sum(metrics['participation_rates']) / len(metrics['participation_rates'])
        metrics['avg_abstention'] = sum(metrics['abstention_rates']) / len(metrics['abstention_rates'])
    
    return metrics
```

## Applications in Political Analysis and Research

### Legislative Opposition Analysis

```python
def analyze_opposition_voting_patterns(opposition_party_ids, period_id):
    """Analyze how opposition parties use different vote types strategically."""
    
    results = {}
    
    for party_id in opposition_party_ids:
        # Get all votes by party members in the period
        query = f"""https://oda.ft.dk/api/Stemme?%24filter=Afstemning/periodeid%20eq%20{period_id}&%24expand=Aktør(%24filter=Partier/any(p:%20p/id%20eq%20{party_id})),Stemmetype,Afstemning(%24expand=Sag)&%24top=5000"""
        
        response = requests.get(query)
        votes = [v for v in response.json()['value'] if v.get('Aktør')]
        
        # Analyze strategic voting patterns
        patterns = {
            'total_votes': len(votes),
            'strategic_abstentions': 0,  # Abstentions on government proposals
            'protest_absences': 0,       # High absence rates on controversial votes
            'unified_opposition': 0,     # Cases where opposition voted together
            'vote_distribution': {'For': 0, 'Imod': 0, 'Fravær': 0, 'Hverken for eller imod': 0}
        }
        
        for vote in votes:
            vote_type = vote['Stemmetype']['type']
            patterns['vote_distribution'][vote_type] += 1
            
            # Identify strategic patterns
            if vote_type == 'Hverken for eller imod':
                # Check if this was on a government proposal
                case = vote.get('Afstemning', {}).get('Sag', {})
                if case.get('typeid') in [3, 5]:  # Government bill types
                    patterns['strategic_abstentions'] += 1
        
        results[party_id] = patterns
    
    return results
```

### Voting Behavior Research Applications

```python
def research_voting_consistency(research_question="party_discipline"):
    """Generate datasets for political science research questions."""
    
    if research_question == "party_discipline":
        # Measure party voting discipline using vote type consistency
        return analyze_party_discipline_by_vote_type()
    
    elif research_question == "issue_salience":
        # Use abstention rates to measure issue salience and controversy
        return analyze_issue_salience_via_abstentions()
    
    elif research_question == "coalition_stability":
        # Track coalition voting patterns through vote type evolution
        return analyze_coalition_stability_patterns()

def analyze_party_discipline_by_vote_type():
    """Measure party discipline using vote type distribution analysis."""
    
    # Get recent legislative votes with party information
    query = """https://oda.ft.dk/api/Afstemning?%24filter=dato%20ge%20datetime'2023-01-01'%20and%20Sag/typeid%20eq%203&%24expand=Stemme(%24expand=Aktør(%24expand=Partier),Stemmetype),Sag&%24top=100"""
    
    response = requests.get(query)
    sessions = response.json()['value']
    
    discipline_scores = {}
    
    for session in sessions:
        votes = session.get('Stemme', [])
        party_votes = {}
        
        # Group votes by party
        for vote in votes:
            actor = vote.get('Aktør')
            if not actor or not actor.get('Partier'):
                continue
                
            party_id = actor['Partier'][0]['id']  # Primary party
            vote_type = vote['Stemmetype']['type']
            
            if party_id not in party_votes:
                party_votes[party_id] = []
            party_votes[party_id].append(vote_type)
        
        # Calculate discipline for each party
        for party_id, votes in party_votes.items():
            if len(votes) < 3:  # Minimum sample size
                continue
                
            # Exclude absences from discipline calculation
            active_votes = [v for v in votes if v != 'Fravær']
            
            if len(active_votes) == 0:
                continue
            
            # Calculate unity (most common vote type percentage)
            vote_counts = {}
            for vote in active_votes:
                vote_counts[vote] = vote_counts.get(vote, 0) + 1
            
            max_agreement = max(vote_counts.values())
            discipline_score = (max_agreement / len(active_votes)) * 100
            
            if party_id not in discipline_scores:
                discipline_scores[party_id] = []
            discipline_scores[party_id].append(discipline_score)
    
    # Calculate average discipline scores
    avg_discipline = {}
    for party_id, scores in discipline_scores.items():
        avg_discipline[party_id] = sum(scores) / len(scores)
    
    return avg_discipline
```

### Democratic Participation Analysis

```python
def analyze_democratic_participation_metrics():
    """Comprehensive analysis of democratic participation using vote types."""
    
    # Get recent voting data
    query = """https://oda.ft.dk/api/Afstemning?%24filter=dato%20ge%20datetime'2023-01-01'&%24expand=Stemme(%24expand=Stemmetype)&%24top=500"""
    
    response = requests.get(query)
    sessions = response.json()['value']
    
    participation_metrics = {
        'total_sessions': len(sessions),
        'avg_participation_rate': 0,
        'engagement_quality': {},
        'democratic_responsiveness': {},
        'participation_trends': []
    }
    
    session_participation = []
    
    for session in sessions:
        votes = session.get('Stemme', [])
        if not votes:
            continue
        
        # Calculate session participation metrics
        total_eligible = len(votes)
        absent = len([v for v in votes if v['Stemmetype']['type'] == 'Fravær'])
        abstaining = len([v for v in votes if v['Stemmetype']['type'] == 'Hverken for eller imod'])
        active_voters = total_eligible - absent - abstaining
        
        participation_rate = ((total_eligible - absent) / total_eligible) * 100
        engagement_rate = (active_voters / total_eligible) * 100
        
        session_participation.append(participation_rate)
        
        participation_metrics['participation_trends'].append({
            'date': session['dato'],
            'participation_rate': participation_rate,
            'engagement_rate': engagement_rate,
            'abstention_rate': (abstaining / total_eligible) * 100
        })
    
    # Calculate overall metrics
    if session_participation:
        participation_metrics['avg_participation_rate'] = sum(session_participation) / len(session_participation)
    
    return participation_metrics
```

## Advanced Research Applications

### Temporal Voting Evolution Analysis

```python
def analyze_temporal_voting_evolution(start_year, end_year):
    """Track how voting behavior patterns evolve over time using vote types."""
    
    yearly_patterns = {}
    
    for year in range(start_year, end_year + 1):
        query = f"""https://oda.ft.dk/api/Afstemning?%24filter=year(dato)%20eq%20{year}&%24expand=Stemme(%24expand=Stemmetype)&%24top=1000"""
        
        response = requests.get(query)
        sessions = response.json()['value']
        
        year_stats = {
            'total_sessions': len(sessions),
            'vote_type_evolution': {'For': 0, 'Imod': 0, 'Fravær': 0, 'Hverken for eller imod': 0},
            'polarization_index': 0,
            'engagement_score': 0
        }
        
        total_votes = 0
        for session in sessions:
            for vote in session.get('Stemme', []):
                vote_type = vote['Stemmetype']['type']
                year_stats['vote_type_evolution'][vote_type] += 1
                total_votes += 1
        
        if total_votes > 0:
            # Calculate polarization (For + Against vs Abstentions + Absences)
            decisive_votes = year_stats['vote_type_evolution']['For'] + year_stats['vote_type_evolution']['Imod']
            non_decisive = year_stats['vote_type_evolution']['Fravær'] + year_stats['vote_type_evolution']['Hverken for eller imod']
            
            year_stats['polarization_index'] = (decisive_votes / total_votes) * 100
            year_stats['engagement_score'] = ((total_votes - year_stats['vote_type_evolution']['Fravær']) / total_votes) * 100
            
            # Convert to percentages
            for vote_type in year_stats['vote_type_evolution']:
                year_stats['vote_type_evolution'][vote_type] = (year_stats['vote_type_evolution'][vote_type] / total_votes) * 100
        
        yearly_patterns[year] = year_stats
    
    return yearly_patterns
```

This comprehensive vote type classification system provides the foundation for sophisticated parliamentary analysis, enabling researchers and developers to build powerful tools for understanding democratic processes, party dynamics, and individual legislator behavior in the Danish Parliament.