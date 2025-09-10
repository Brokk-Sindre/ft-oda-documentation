# Voting Procedures in the Danish Parliament

This document provides a comprehensive guide to understanding voting procedures in the Danish Parliament as modeled in the OData API. The Danish Parliament (Folketinget) operates under a sophisticated voting system that ensures democratic participation, transparency, and accountability.

## Overview

The Danish Parliamentary voting system is built around several key principles:

- **Transparency**: All votes are recorded and publicly accessible
- **Individual Accountability**: Each politician's vote is tracked separately
- **Democratic Process**: Multiple voting types support different stages of legislation
- **Procedural Integrity**: Quorum requirements and voting procedures are strictly followed
- **Historical Record**: Complete voting history is preserved for analysis

The API models this system through three core entities:
- **Afstemning** - Voting sessions (collective decisions)
- **Stemme** - Individual votes (personal decisions)
- **Afstemningstype** - Voting session types (procedural categories)

## Danish Parliamentary Voting Types

### 1. Voting Session Types (Afstemningstype)

The Danish Parliament uses 4 distinct voting session types that correspond to different stages of the legislative process:

| Type ID | Name | Description | Legislative Stage |
|---------|------|-------------|-------------------|
| 1 | **Endelig vedtagelse** | Final Adoption | Final vote on legislation - the ultimate decision |
| 2 | **Udvalgsindstilling** | Committee Recommendation | Committee's formal recommendation to parliament |
| 3 | **Forslag til vedtagelse** | Adoption Proposal | Initial proposal for adoption - preliminary voting |
| 4 | **Ændringsforslag** | Amendment | Votes on specific amendments to legislation |

#### Usage Patterns by Type

**Final Adoption (Type 1)** - The most critical votes:
```bash
# Get recent final adoption votes
curl "https://oda.ft.dk/api/Afstemning?%24filter=typeid%20eq%201&%24orderby=opdateringsdato%20desc&%24top=10"
```

**Committee Recommendations (Type 2)** - Expert committee guidance:
```bash
# Analyze committee recommendation patterns
curl "https://oda.ft.dk/api/Afstemning?%24filter=typeid%20eq%202&%24expand=Møde&%24top=20"
```

**Amendment Votes (Type 4)** - Legislative refinements:
```bash
# Track amendment voting activity
curl "https://oda.ft.dk/api/Afstemning?%24filter=typeid%20eq%204&%24select=nummer,konklusion,vedtaget&%24top=15"
```

### 2. Individual Vote Types (Stemmetype)

Each politician can cast one of 4 vote types in any voting session:

| Type ID | Name | English | Democratic Meaning |
|---------|------|---------|-------------------|
| 1 | **For** | Yes/In Favor | Politician supports the proposal |
| 2 | **Imod** | No/Against | Politician opposes the proposal |
| 3 | **Fravær** | Absent | Politician was not present for voting |
| 4 | **Hverken for eller imod** | Neither for nor against | Politician abstains from voting |

#### Vote Distribution Analysis

```bash
# Analyze vote type distribution across recent sessions
curl "https://oda.ft.dk/api/Stemme?%24filter=afstemningid%20eq%201&%24select=typeid&%24inlinecount=allpages&%24top=1"
```

## Parliamentary Voting Procedures

### Standard Voting Process

1. **Proposal Presentation**: Legislation or motions are formally presented
2. **Committee Review**: Relevant committees analyze and provide recommendations
3. **Parliamentary Debate**: Open discussion on the chamber floor
4. **Voting Session Call**: Formal call for voting initiated
5. **Vote Registration**: Individual politicians register their votes
6. **Result Calculation**: Votes are tallied and outcome determined
7. **Result Announcement**: Official announcement and recording

### Quorum and Participation Requirements

The Danish Parliament operates under specific quorum rules:

- **Minimum Attendance**: At least 90 members must be present for valid voting
- **Vote Recording**: All present members must cast a vote (For/Against/Abstain)
- **Absence Tracking**: Absent members are specifically recorded
- **Participation Rates**: Typically 100-179 members participate in voting sessions

```bash
# Analyze participation rates in recent votes
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme&%24filter=id%20eq%201&%24select=Stemme/typeid"
```

### Voting Timeline and Scheduling

#### Daily Voting Patterns

Based on API data analysis, voting sessions follow predictable patterns:

- **Morning Sessions**: Committee work (08:30-12:00)
- **Midday Voting**: Major decisions (12:00-14:00)
- **Afternoon Sessions**: Continued debate and amendments (14:00-18:00)
- **Evening Votes**: Final adoption votes often occur in late afternoon

```bash
# Track daily voting activity patterns
curl "https://oda.ft.dk/api/Afstemning?%24expand=Møde&%24filter=opdateringsdato%20gt%20datetime'2025-09-09T00:00:00'&%24select=nummer,opdateringsdato,Møde/dato"
```

#### Weekly Parliamentary Schedule

The Danish Parliament follows a structured weekly schedule:

- **Tuesday-Thursday**: Primary voting days
- **Wednesday**: Major legislative votes typically occur
- **Friday**: Committee work and administrative votes
- **Monday**: Preparation and procedural votes

### Committee vs Plenary Voting Differences

#### Committee Voting Procedures

**Characteristics:**
- Smaller group participation (15-25 members)
- Detailed technical discussions
- Expert recommendations generated
- Less formal voting procedures
- Focus on legislative improvement

```bash
# Identify committee voting sessions
curl "https://oda.ft.dk/api/Afstemning?%24filter=typeid%20eq%202&%24expand=Møde&%24select=nummer,Møde/titel&%24top=10"
```

#### Plenary Voting Procedures

**Characteristics:**
- Full parliament participation (100+ members)
- Formal voting protocols
- Public gallery attendance
- Media coverage
- Final decision-making authority

```bash
# Track full plenary voting sessions
curl "https://oda.ft.dk/api/Afstemning?%24filter=typeid%20eq%201&%24expand=Stemme&%24top=5"
```

## Vote Outcome Determination and Reporting

### Result Calculation Methods

The Danish Parliament uses simple majority voting with specific rules:

1. **Majority Requirement**: More than 50% of votes cast
2. **Abstention Handling**: Abstentions do not count toward majority
3. **Absence Impact**: Absences reduce the total voting pool
4. **Tie Breaking**: Rare; specific procedures apply

### Outcome Reporting Format

Vote results are reported in the `konklusion` field with standardized format:

```
Vedtaget

108 stemmer for forslaget (V, S, DF, RV, SF, EL, LA, KF, UFG)

0 stemmer imod forslaget
```

**Format Elements:**
- **Outcome**: `Vedtaget` (Adopted) or `Forkastet` (Rejected)
- **For Votes**: Count + participating party abbreviations
- **Against Votes**: Count + opposing party abbreviations  
- **Abstentions**: `X hverken for eller imod` (when present)

#### Party Abbreviation Reference

| Code | Danish Name | English Name | Political Position |
|------|-------------|--------------|-------------------|
| V | Venstre | Liberal Party | Center-right liberal |
| S | Socialdemokratiet | Social Democrats | Center-left social democratic |
| DF | Dansk Folkeparti | Danish People's Party | Right-wing populist |
| RV | Radikale Venstre | Social Liberals | Center-left liberal |
| SF | Socialistisk Folkeparti | Socialist People's Party | Left-wing democratic socialist |
| EL | Enhedslisten | Red-Green Alliance | Far-left socialist |
| LA | Liberal Alliance | Liberal Alliance | Right-wing liberal |
| KF | Konservative Folkeparti | Conservative Party | Center-right conservative |
| UFG | Uden for folketingsgrupperne | Independent | Non-party affiliated |

```bash
# Analyze party voting patterns in recent decisions
curl "https://oda.ft.dk/api/Afstemning?%24filter=substringof('Socialdemokratiet',konklusion)&%24select=nummer,konklusion,vedtaget&%24top=5"
```

## Special Voting Procedures and Exceptions

### Constitutional Amendment Voting

- **Special Majority**: Requires 2/3 majority
- **Multiple Readings**: Must pass through multiple voting stages
- **Referendum Requirement**: Some changes require public referendum
- **Extended Timeline**: Longer deliberation periods

### Emergency Legislation

- **Accelerated Process**: Shortened debate periods
- **Special Sessions**: Can be called outside normal schedule
- **Reduced Committee Review**: Streamlined committee processes
- **Same-Day Voting**: All stages can occur in single session

### Budget and Finance Votes

- **Annual Schedule**: Predictable timeline (autumn sessions)
- **Committee Priority**: Finance Committee central role
- **Sequential Voting**: Multiple related voting sessions
- **Amendment Procedures**: Special rules for budget amendments

```bash
# Track emergency or special legislation patterns
curl "https://oda.ft.dk/api/Afstemning?%24filter=substringof('hastesag',konklusion)&%24top=5"
```

## API Data Model for Voting Analysis

### Core Relationships

```
Møde (Meeting)
  
Dagsordenspunkt (Agenda Item)
  
Afstemning (Voting Session)
  
Stemme (Individual Vote)  Aktör (Politician)
```

### Multi-level Data Analysis

#### 1. Individual Vote Tracking

```python
def track_politician_votes(politician_name, session_limit=50):
    """Track individual politician voting patterns"""
    
    # Get politician's recent votes with context
    query = f"""
    https://oda.ft.dk/api/Stemme?
    %24expand=Aktør,Afstemning&
    %24filter=Aktør/navn eq '{politician_name}'&
    %24select=typeid,Afstemning/nummer,Afstemning/konklusion,Aktör/gruppenavnkort&
    %24top={session_limit}&
    %24orderby=opdateringsdato desc
    """
    
    return fetch_api_data(query)

# Usage example
votes = track_politician_votes("Nicolai Wammen", 30)
```

#### 2. Voting Session Analysis

```python
def analyze_voting_session(session_id):
    """Complete analysis of a specific voting session"""
    
    # Get full voting session with all individual votes
    query = f"""
    https://oda.ft.dk/api/Afstemning?
    %24expand=Stemme/Aktör,Møde,Afstemningstype&
    %24filter=id eq {session_id}
    """
    
    response = fetch_api_data(query)
    session = response['value'][0]
    
    # Analyze vote distribution
    vote_breakdown = {
        'total_votes': len(session['Stemme']),
        'for_votes': len([v for v in session['Stemme'] if v['typeid'] == 1]),
        'against_votes': len([v for v in session['Stemme'] if v['typeid'] == 2]),
        'abstentions': len([v for v in session['Stemme'] if v['typeid'] == 4]),
        'absences': len([v for v in session['Stemme'] if v['typeid'] == 3])
    }
    
    # Party breakdown
    party_votes = {}
    for vote in session['Stemme']:
        party = vote['Aktör']['gruppenavnkort']
        if party not in party_votes:
            party_votes[party] = {'for': 0, 'against': 0, 'abstain': 0, 'absent': 0}
        
        vote_type = vote['typeid']
        if vote_type == 1:
            party_votes[party]['for'] += 1
        elif vote_type == 2:
            party_votes[party]['against'] += 1
        elif vote_type == 3:
            party_votes[party]['absent'] += 1
        elif vote_type == 4:
            party_votes[party]['abstain'] += 1
    
    return {
        'session_info': {
            'number': session['nummer'],
            'outcome': session['vedtaget'],
            'type': session['Afstemningstype']['navn'],
            'meeting': session['Møde']['titel']
        },
        'vote_breakdown': vote_breakdown,
        'party_breakdown': party_votes
    }
```

#### 3. Cross-Party Coalition Analysis

```python
def analyze_cross_party_coalitions(days_back=30):
    """Identify cross-party voting coalitions"""
    
    from datetime import datetime, timedelta
    
    # Get recent voting sessions
    since_date = (datetime.now() - timedelta(days=days_back)).isoformat()
    query = f"""
    https://oda.ft.dk/api/Afstemning?
    %24expand=Stemme/Aktör&
    %24filter=opdateringsdato gt datetime'{since_date}'&
    %24orderby=opdateringsdato desc&
    %24top=20
    """
    
    sessions = fetch_api_data(query)
    
    coalition_patterns = {}
    
    for session in sessions['value']:
        session_id = session['id']
        
        # Group parties by vote type
        party_positions = {}
        for vote in session['Stemme']:
            party = vote['Aktör']['gruppenavnkort']
            vote_type = vote['typeid']
            
            if party not in party_positions:
                party_positions[party] = []
            party_positions[party].append(vote_type)
        
        # Determine party majority positions
        party_stances = {}
        for party, votes in party_positions.items():
            most_common_vote = max(set(votes), key=votes.count)
            party_stances[party] = most_common_vote
        
        # Group parties by their stance
        coalitions = {'for': [], 'against': [], 'mixed': []}
        for party, stance in party_stances.items():
            if stance == 1:  # For
                coalitions['for'].append(party)
            elif stance == 2:  # Against
                coalitions['against'].append(party)
            else:
                coalitions['mixed'].append(party)
        
        # Store coalition pattern
        coalition_key = f"for:{sorted(coalitions['for'])}|against:{sorted(coalitions['against'])}"
        if coalition_key not in coalition_patterns:
            coalition_patterns[coalition_key] = 0
        coalition_patterns[coalition_key] += 1
    
    return sorted(coalition_patterns.items(), key=lambda x: x[1], reverse=True)
```

### 4. Voting System Performance Analysis

```python
def analyze_voting_system_performance():
    """Analyze overall parliamentary voting system performance"""
    
    # Get recent voting activity
    query = """
    https://oda.ft.dk/api/Afstemning?
    %24expand=Stemme&
    %24orderby=opdateringsdato desc&
    %24top=100
    """
    
    sessions = fetch_api_data(query)
    
    performance_metrics = {
        'total_sessions': len(sessions['value']),
        'average_participation': 0,
        'vote_efficiency': 0,
        'session_outcomes': {'adopted': 0, 'rejected': 0},
        'participation_by_session': []
    }
    
    total_participation = 0
    
    for session in sessions['value']:
        # Count participation
        total_votes = len(session['Stemme'])
        active_votes = len([v for v in session['Stemme'] if v['typeid'] in [1, 2, 4]])
        
        performance_metrics['participation_by_session'].append({
            'session_number': session['nummer'],
            'total_votes': total_votes,
            'active_participation': active_votes,
            'participation_rate': active_votes / total_votes if total_votes > 0 else 0
        })
        
        total_participation += total_votes
        
        # Track outcomes
        if session['vedtaget']:
            performance_metrics['session_outcomes']['adopted'] += 1
        else:
            performance_metrics['session_outcomes']['rejected'] += 1
    
    performance_metrics['average_participation'] = total_participation / len(sessions['value'])
    
    return performance_metrics
```

### 5. Building Voting Analysis Systems

#### Real-time Voting Monitor

```javascript
class ParliamentaryVotingMonitor {
    constructor(baseUrl = 'https://oda.ft.dk/api/') {
        this.baseUrl = baseUrl;
        this.updateInterval = 300000; // 5 minutes
        this.lastCheck = new Date();
    }
    
    async getRecentVotingActivity(hoursBack = 24) {
        const since = new Date(Date.now() - hoursBack * 60 * 60 * 1000);
        const sinceISO = since.toISOString();
        
        const params = new URLSearchParams({
            '$filter': `opdateringsdato gt datetime'${sinceISO}'`,
            '$expand': 'Stemme/Aktör,Møde',
            '$orderby': 'opdateringsdato desc',
            '$top': '20'
        });
        
        const response = await fetch(`${this.baseUrl}Afstemning?${params}`);
        return await response.json();
    }
    
    async analyzeVotingTrends(sessionCount = 50) {
        const params = new URLSearchParams({
            '$expand': 'Stemme',
            '$orderby': 'opdateringsdato desc',
            '$top': sessionCount.toString(),
            '$select': 'nummer,vedtaget,opdateringsdato,Stemme/typeid'
        });
        
        const response = await fetch(`${this.baseUrl}Afstemning?${params}`);
        const data = await response.json();
        
        // Analyze trends
        const trends = {
            adoption_rate: 0,
            average_participation: 0,
            voting_frequency: 0,
            recent_activity: []
        };
        
        let adopted_count = 0;
        let total_votes = 0;
        
        for (const session of data.value) {
            if (session.vedtaget) adopted_count++;
            total_votes += session.Stemme.length;
            
            trends.recent_activity.push({
                session: session.nummer,
                adopted: session.vedtaget,
                votes: session.Stemme.length,
                date: session.opdateringsdato
            });
        }
        
        trends.adoption_rate = adopted_count / data.value.length;
        trends.average_participation = total_votes / data.value.length;
        
        return trends;
    }
    
    startMonitoring(callback) {
        setInterval(async () => {
            try {
                const activity = await this.getRecentVotingActivity(1); // Last hour
                if (activity.value.length > 0) {
                    callback(activity);
                }
            } catch (error) {
                console.error('Monitoring error:', error);
            }
        }, this.updateInterval);
    }
}

// Usage
const monitor = new ParliamentaryVotingMonitor();
monitor.startMonitoring((activity) => {
    console.log(`New voting activity: ${activity.value.length} sessions`);
    activity.value.forEach(session => {
        console.log(`Session ${session.nummer}: ${session.vedtaget ? 'Adopted' : 'Rejected'}`);
    });
});
```

#### Historical Voting Analysis System

```python
class HistoricalVotingAnalyzer:
    def __init__(self, base_url="https://oda.ft.dk/api/"):
        self.base_url = base_url
        
    def analyze_politician_evolution(self, politician_id, years_back=5):
        """Track how a politician's voting patterns have evolved"""
        
        from datetime import datetime, timedelta
        
        # Get historical voting data
        since_date = (datetime.now() - timedelta(days=years_back*365)).isoformat()
        
        query_params = {
            '$expand': 'Afstemning',
            '$filter': f"aktørid eq {politician_id} and opdateringsdato gt datetime'{since_date}'",
            '$select': 'typeid,opdateringsdato,Afstemning/vedtaget,Afstemning/typeid',
            '$orderby': 'opdateringsdato asc',
            '$top': '1000'
        }
        
        votes = self.fetch_data('Stemme', query_params)
        
        # Analyze evolution by year
        yearly_patterns = {}
        
        for vote in votes['value']:
            vote_year = vote['opdateringsdato'][:4]
            
            if vote_year not in yearly_patterns:
                yearly_patterns[vote_year] = {
                    'total_votes': 0,
                    'yes_votes': 0,
                    'no_votes': 0,
                    'abstentions': 0,
                    'majority_agreement': 0  # Voted with majority
                }
            
            patterns = yearly_patterns[vote_year]
            patterns['total_votes'] += 1
            
            vote_type = vote['typeid']
            if vote_type == 1:
                patterns['yes_votes'] += 1
            elif vote_type == 2:
                patterns['no_votes'] += 1
            elif vote_type == 4:
                patterns['abstentions'] += 1
            
            # Check if voted with majority
            session_adopted = vote['Afstemning']['vedtaget']
            if (vote_type == 1 and session_adopted) or (vote_type == 2 and not session_adopted):
                patterns['majority_agreement'] += 1
        
        # Calculate evolution metrics
        evolution_data = []
        for year, patterns in yearly_patterns.items():
            if patterns['total_votes'] > 0:
                evolution_data.append({
                    'year': year,
                    'participation_rate': patterns['total_votes'],
                    'yes_rate': patterns['yes_votes'] / patterns['total_votes'],
                    'no_rate': patterns['no_votes'] / patterns['total_votes'],
                    'abstention_rate': patterns['abstentions'] / patterns['total_votes'],
                    'majority_agreement_rate': patterns['majority_agreement'] / patterns['total_votes']
                })
        
        return evolution_data
    
    def analyze_legislative_success_rates(self, session_type=1, months_back=12):
        """Analyze success rates for different types of legislation"""
        
        from datetime import datetime, timedelta
        
        since_date = (datetime.now() - timedelta(days=months_back*30)).isoformat()
        
        query_params = {
            '$expand': 'Stemme',
            '$filter': f"typeid eq {session_type} and opdateringsdato gt datetime'{since_date}'",
            '$select': 'nummer,vedtaget,opdateringsdato,Stemme/typeid',
            '$orderby': 'opdateringsdato desc',
            '$top': '200'
        }
        
        sessions = self.fetch_data('Afstemning', query_params)
        
        success_metrics = {
            'total_sessions': len(sessions['value']),
            'adopted': 0,
            'rejected': 0,
            'close_votes': 0,
            'unanimous_votes': 0,
            'average_participation': 0
        }
        
        total_participation = 0
        
        for session in sessions['value']:
            total_votes = len(session['Stemme'])
            yes_votes = len([v for v in session['Stemme'] if v['typeid'] == 1])
            no_votes = len([v for v in session['Stemme'] if v['typeid'] == 2])
            
            total_participation += total_votes
            
            if session['vedtaget']:
                success_metrics['adopted'] += 1
            else:
                success_metrics['rejected'] += 1
            
            # Identify close votes (within 10% margin)
            if total_votes > 0:
                margin = abs(yes_votes - no_votes) / total_votes
                if margin < 0.1:
                    success_metrics['close_votes'] += 1
                
                # Identify unanimous votes
                if no_votes == 0:
                    success_metrics['unanimous_votes'] += 1
        
        success_metrics['average_participation'] = total_participation / len(sessions['value'])
        success_metrics['success_rate'] = success_metrics['adopted'] / success_metrics['total_sessions']
        
        return success_metrics
```

## Performance Optimization for Voting Analysis

### Efficient Data Retrieval

```bash
#  Good: Target specific voting sessions
curl "https://oda.ft.dk/api/Afstemning?%24filter=typeid%20eq%201&%24top=20"

#  Good: Use field selection for large datasets  
curl "https://oda.ft.dk/api/Stemme?%24filter=aktørid%20eq%205&%24select=typeid,afstemningid&%24top=100"

# L Avoid: Expanding large biographical data unnecessarily
curl "https://oda.ft.dk/api/Stemme?%24expand=Aktör&%24top=1000"
```

### Smart Pagination Strategy

```python
def paginate_voting_data(entity, filter_query, page_size=100):
    """Efficiently paginate through large voting datasets"""
    
    all_results = []
    skip = 0
    
    while True:
        query_params = {
            '$filter': filter_query,
            '$skip': str(skip),
            '$top': str(page_size),
            '$orderby': 'id'
        }
        
        page_data = fetch_data(entity, query_params)
        
        if not page_data['value']:
            break
            
        all_results.extend(page_data['value'])
        skip += page_size
        
        # Safety break for very large datasets
        if len(all_results) > 10000:
            break
    
    return all_results
```

### Caching Strategy for Analysis

```python
import json
from datetime import datetime, timedelta

class VotingDataCache:
    def __init__(self, cache_duration_hours=1):
        self.cache = {}
        self.cache_duration = timedelta(hours=cache_duration_hours)
    
    def get_cached_or_fetch(self, cache_key, fetch_function):
        """Get from cache or fetch fresh data"""
        
        now = datetime.now()
        
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if now - cached_time < self.cache_duration:
                return cached_data
        
        # Fetch fresh data
        fresh_data = fetch_function()
        self.cache[cache_key] = (now, fresh_data)
        
        return fresh_data
    
    def clear_expired_cache(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = []
        
        for key, (cached_time, _) in self.cache.items():
            if now - cached_time >= self.cache_duration:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
```

## Common Analysis Scenarios

### 1. Government vs Opposition Analysis

```python
def analyze_government_opposition_voting(government_parties, days_back=30):
    """Compare voting patterns between government and opposition"""
    
    # Get recent voting sessions
    since_date = (datetime.now() - timedelta(days=days_back)).isoformat()
    
    sessions = fetch_api_data(f"""
    https://oda.ft.dk/api/Afstemning?
    %24expand=Stemme/Aktör&
    %24filter=opdateringsdato gt datetime'{since_date}'&
    %24top=50
    """)
    
    analysis = {
        'government_unity': [],
        'opposition_unity': [],
        'cross_party_votes': 0,
        'party_line_votes': 0
    }
    
    for session in sessions['value']:
        gov_votes = {'for': 0, 'against': 0, 'other': 0}
        opp_votes = {'for': 0, 'against': 0, 'other': 0}
        
        for vote in session['Stemme']:
            party = vote['Aktör']['gruppenavnkort']
            vote_type = vote['typeid']
            
            vote_category = 'for' if vote_type == 1 else 'against' if vote_type == 2 else 'other'
            
            if party in government_parties:
                gov_votes[vote_category] += 1
            else:
                opp_votes[vote_category] += 1
        
        # Calculate unity scores
        gov_total = sum(gov_votes.values())
        opp_total = sum(opp_votes.values())
        
        if gov_total > 0:
            gov_unity = max(gov_votes.values()) / gov_total
            analysis['government_unity'].append(gov_unity)
        
        if opp_total > 0:
            opp_unity = max(opp_votes.values()) / opp_total
            analysis['opposition_unity'].append(opp_unity)
        
        # Check for cross-party coalitions
        gov_majority_position = max(gov_votes.keys(), key=lambda k: gov_votes[k])
        opp_majority_position = max(opp_votes.keys(), key=lambda k: opp_votes[k])
        
        if gov_majority_position == opp_majority_position:
            analysis['cross_party_votes'] += 1
        else:
            analysis['party_line_votes'] += 1
    
    return analysis
```

### 2. Voting Predictability Analysis

```python
def analyze_voting_predictability(politician_id, lookback_sessions=100):
    """Analyze how predictable a politician's voting behavior is"""
    
    votes = fetch_api_data(f"""
    https://oda.ft.dk/api/Stemme?
    %24expand=Afstemning&
    %24filter=aktørid eq {politician_id}&
    %24select=typeid,Afstemning/vedtaget&
    %24orderby=opdateringsdato desc&
    %24top={lookback_sessions}
    """)
    
    predictability_metrics = {
        'votes_with_majority': 0,
        'votes_against_majority': 0,
        'abstention_rate': 0,
        'absence_rate': 0,
        'consistency_score': 0
    }
    
    for vote in votes['value']:
        vote_type = vote['typeid']
        session_outcome = vote['Afstemning']['vedtaget']
        
        # Check if voted with majority
        if (vote_type == 1 and session_outcome) or (vote_type == 2 and not session_outcome):
            predictability_metrics['votes_with_majority'] += 1
        elif vote_type in [1, 2]:  # Only count actual votes
            predictability_metrics['votes_against_majority'] += 1
        elif vote_type == 4:
            predictability_metrics['abstention_rate'] += 1
        elif vote_type == 3:
            predictability_metrics['absence_rate'] += 1
    
    total_votes = len(votes['value'])
    if total_votes > 0:
        predictability_metrics['consistency_score'] = (
            predictability_metrics['votes_with_majority'] / 
            (predictability_metrics['votes_with_majority'] + predictability_metrics['votes_against_majority'])
        ) if (predictability_metrics['votes_with_majority'] + predictability_metrics['votes_against_majority']) > 0 else 0
        
        predictability_metrics['abstention_rate'] /= total_votes
        predictability_metrics['absence_rate'] /= total_votes
    
    return predictability_metrics
```

## Important Considerations

### Data Freshness and Updates

The Danish Parliamentary API provides exceptionally fresh voting data:

- **Same-day Updates**: Voting sessions updated within hours
- **Real-time Tracking**: Individual votes recorded immediately
- **Business Hours**: Most updates occur during parliamentary sessions
- **Batch Processing**: Some data updated in synchronized batches

### Privacy and Transparency

 **Public Democratic Data**: All voting records are constitutionally public
 **Transparency Requirement**: Citizens have right to know representative voting
 **Historical Accountability**: Complete voting history preserved
 **Open Government**: API promotes democratic transparency

### Performance and Scale

- **Large Dataset**: Hundreds of thousands of individual vote records
- **Complex Relationships**: Multi-level entity connections
- **Real-time Growth**: New records created with every parliamentary session
- **API Limits**: 100-record response limit requires pagination

## Conclusion

The Danish Parliamentary voting system, as modeled in the OData API, provides unprecedented insight into democratic decision-making processes. The combination of individual vote tracking, comprehensive session documentation, and real-time data updates creates a powerful foundation for analyzing parliamentary democracy in action.

Key capabilities include:

1. **Individual Accountability**: Track every politician's vote on every issue
2. **Procedural Analysis**: Understand different voting types and their purposes  
3. **Coalition Mapping**: Identify cross-party cooperation patterns
4. **Historical Trends**: Analyze how voting patterns evolve over time
5. **Real-time Monitoring**: Track parliamentary activity as it happens

This system exemplifies democratic transparency and provides researchers, journalists, and citizens with the tools needed to understand how their parliament functions and hold their representatives accountable.