# Politician Voting Behavior Analysis

## Overview

The Danish Parliamentary Open Data API provides comprehensive individual voting records for detailed analysis of politician behavior patterns. This guide covers advanced techniques for analyzing individual political decision-making, career evolution, and voting consistency using the rich dataset available through the API.

The API tracks individual votes through the `Stemme` (Vote) entity, linked to specific politicians (`Aktør`) and voting sessions (`Afstemning`). This enables sophisticated behavioral analysis including party loyalty measurement, voting pattern prediction, and influence network mapping.

## Individual Politician Voting Analysis Fundamentals

### Core Data Structure

Individual voting analysis relies on three primary entities:

- **`Stemme`** (Individual Votes): Records each politician's vote on each issue
- **`Afstemning`** (Voting Sessions): Parliamentary voting sessions with outcomes  
- **`Aktør`** (Politicians): Individual politicians with biographical data

### Basic Vote Retrieval

```python
import requests
import urllib.parse
from datetime import datetime, timedelta

class PoliticianVotingAnalyzer:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api/"
        
    def get_politician_votes(self, politician_name, limit=1000):
        """Retrieve all votes by a specific politician"""
        filter_expr = f"Aktør/navn eq '{politician_name}'"
        params = {
            '$filter': filter_expr,
            '$expand': 'Afstemning,Aktør',
            '$top': limit,
            '$orderby': 'Afstemning/dato desc'
        }
        
        url = f"{self.base_url}Stemme?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
        
    def get_voting_session_details(self, voting_id):
        """Get complete voting session with all individual votes"""
        params = {
            '$filter': f'id eq {voting_id}',
            '$expand': 'Stemme/Aktør,Møde'
        }
        
        url = f"{self.base_url}Afstemning?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        return response.json()

# Example usage
analyzer = PoliticianVotingAnalyzer()
frank_votes = analyzer.get_politician_votes("Frank Aaen")
print(f"Retrieved {len(frank_votes['value'])} votes")
```

### Understanding Vote Types

The API uses `typeid` to classify individual votes:

1. **For** (typeid=1): Yes vote
2. **Imod** (typeid=2): No vote  
3. **Hverken for eller imod** (typeid=3): Abstention
4. **Fravær** (typeid=4): Absence (didn't vote)

```python
def categorize_vote_behavior(votes_data):
    """Analyze voting behavior patterns"""
    vote_counts = {'yes': 0, 'no': 0, 'abstain': 0, 'absent': 0}
    vote_mapping = {1: 'yes', 2: 'no', 3: 'abstain', 4: 'absent'}
    
    for vote in votes_data['value']:
        vote_type = vote_mapping.get(vote['typeid'], 'unknown')
        vote_counts[vote_type] += 1
    
    total_votes = sum(vote_counts.values())
    if total_votes == 0:
        return vote_counts
        
    # Calculate percentages
    behavior_profile = {
        'participation_rate': (total_votes - vote_counts['absent']) / total_votes,
        'yes_rate': vote_counts['yes'] / total_votes,
        'no_rate': vote_counts['no'] / total_votes,
        'abstention_rate': vote_counts['abstain'] / total_votes,
        'absence_rate': vote_counts['absent'] / total_votes
    }
    
    return behavior_profile
```

## Voting History Tracking and Career Analysis

### Career Timeline Construction

```python
def build_career_voting_timeline(politician_name, period_months=12):
    """Build chronological voting history with career periods"""
    votes = analyzer.get_politician_votes(politician_name, limit=10000)
    
    # Group votes by time periods
    timeline = {}
    for vote in votes['value']:
        if 'Afstemning' in vote and vote['Afstemning']:
            vote_date = datetime.fromisoformat(vote['Afstemning']['dato'])
            period_key = vote_date.strftime(f"%Y-{(vote_date.month-1)//period_months + 1}")
            
            if period_key not in timeline:
                timeline[period_key] = {'votes': [], 'yes': 0, 'no': 0, 'abstain': 0, 'absent': 0}
            
            timeline[period_key]['votes'].append(vote)
            vote_type = {1: 'yes', 2: 'no', 3: 'abstain', 4: 'absent'}.get(vote['typeid'], 'unknown')
            if vote_type != 'unknown':
                timeline[period_key][vote_type] += 1
    
    return timeline

def detect_voting_pattern_changes(timeline):
    """Detect significant changes in voting behavior over time"""
    periods = sorted(timeline.keys())
    changes = []
    
    for i in range(1, len(periods)):
        prev_period = timeline[periods[i-1]]
        curr_period = timeline[periods[i]]
        
        prev_total = sum([prev_period[t] for t in ['yes', 'no', 'abstain', 'absent']])
        curr_total = sum([curr_period[t] for t in ['yes', 'no', 'abstain', 'absent']])
        
        if prev_total > 0 and curr_total > 0:
            prev_yes_rate = prev_period['yes'] / prev_total
            curr_yes_rate = curr_period['yes'] / curr_total
            
            if abs(prev_yes_rate - curr_yes_rate) > 0.2:  # 20% threshold
                changes.append({
                    'period': periods[i],
                    'prev_yes_rate': prev_yes_rate,
                    'curr_yes_rate': curr_yes_rate,
                    'change_magnitude': curr_yes_rate - prev_yes_rate
                })
    
    return changes
```

### Committee vs Plenary Voting Analysis

```python
def analyze_committee_vs_plenary_voting(politician_name):
    """Compare voting behavior in committee vs plenary sessions"""
    votes = analyzer.get_politician_votes(politician_name, limit=5000)
    
    committee_votes = {'yes': 0, 'no': 0, 'abstain': 0, 'absent': 0}
    plenary_votes = {'yes': 0, 'no': 0, 'abstain': 0, 'absent': 0}
    
    for vote in votes['value']:
        if 'Afstemning' in vote and vote['Afstemning']:
            # Determine if committee or plenary based on voting type
            voting_type = vote['Afstemning'].get('typeid', 0)
            vote_category = 'committee' if voting_type == 2 else 'plenary'  # typeid 2 = Committee recommendation
            
            vote_type = {1: 'yes', 2: 'no', 3: 'abstain', 4: 'absent'}.get(vote['typeid'], None)
            if vote_type:
                if vote_category == 'committee':
                    committee_votes[vote_type] += 1
                else:
                    plenary_votes[vote_type] += 1
    
    return {
        'committee_behavior': committee_votes,
        'plenary_behavior': plenary_votes,
        'differences': calculate_behavioral_differences(committee_votes, plenary_votes)
    }

def calculate_behavioral_differences(committee_votes, plenary_votes):
    """Calculate behavioral differences between committee and plenary voting"""
    committee_total = sum(committee_votes.values())
    plenary_total = sum(plenary_votes.values())
    
    if committee_total == 0 or plenary_total == 0:
        return None
    
    committee_yes_rate = committee_votes['yes'] / committee_total
    plenary_yes_rate = plenary_votes['yes'] / plenary_total
    
    return {
        'yes_rate_difference': committee_yes_rate - plenary_yes_rate,
        'committee_participation': (committee_total - committee_votes['absent']) / committee_total,
        'plenary_participation': (plenary_total - plenary_votes['absent']) / plenary_total
    }
```

## Party Loyalty vs Independent Voting Analysis

### Party Line Deviation Detection

```python
def analyze_party_loyalty(politician_name, party_name=None):
    """Analyze how often a politician votes against their party line"""
    votes = analyzer.get_politician_votes(politician_name, limit=5000)
    
    party_deviations = []
    loyalty_metrics = {'total_votes': 0, 'party_line_votes': 0, 'deviations': 0}
    
    for vote in votes['value']:
        if 'Afstemning' in vote and vote['Afstemning']:
            voting_session = vote['Afstemning']
            politician_vote = vote['typeid']
            
            # Get all votes from the same session
            session_details = analyzer.get_voting_session_details(voting_session['id'])
            
            if session_details['value']:
                all_session_votes = session_details['value'][0].get('Stemme', [])
                party_vote_pattern = calculate_party_consensus(all_session_votes, party_name)
                
                is_deviation = detect_party_deviation(politician_vote, party_vote_pattern)
                
                loyalty_metrics['total_votes'] += 1
                if is_deviation:
                    loyalty_metrics['deviations'] += 1
                    party_deviations.append({
                        'voting_session_id': voting_session['id'],
                        'vote_date': voting_session.get('dato'),
                        'politician_vote': politician_vote,
                        'party_consensus': party_vote_pattern,
                        'case_id': voting_session.get('sagstrinid')
                    })
                else:
                    loyalty_metrics['party_line_votes'] += 1
    
    loyalty_rate = loyalty_metrics['party_line_votes'] / loyalty_metrics['total_votes'] if loyalty_metrics['total_votes'] > 0 else 0
    
    return {
        'loyalty_rate': loyalty_rate,
        'total_deviations': len(party_deviations),
        'deviation_details': party_deviations[:10],  # Top 10 most recent
        'metrics': loyalty_metrics
    }

def calculate_party_consensus(all_votes, party_name):
    """Calculate the dominant voting pattern for a party"""
    party_votes = {'yes': 0, 'no': 0, 'abstain': 0, 'absent': 0}
    vote_mapping = {1: 'yes', 2: 'no', 3: 'abstain', 4: 'absent'}
    
    for vote in all_votes:
        if 'Aktør' in vote and vote['Aktør']:
            # Filter by party affiliation if provided
            if party_name and party_name in vote['Aktør'].get('gruppenavnkort', ''):
                vote_type = vote_mapping.get(vote['typeid'], 'unknown')
                if vote_type != 'unknown':
                    party_votes[vote_type] += 1
    
    # Return dominant vote type
    if party_votes:
        return max(party_votes.items(), key=lambda x: x[1])[0]
    return None

def detect_party_deviation(politician_vote, party_consensus):
    """Determine if politician voted against party line"""
    vote_mapping = {1: 'yes', 2: 'no', 3: 'abstain', 4: 'absent'}
    politician_vote_type = vote_mapping.get(politician_vote, 'unknown')
    
    return politician_vote_type != party_consensus and party_consensus is not None
```

## Cross-Party Voting and Rebel Behavior Detection

### Coalition Analysis Across Party Lines

```python
def analyze_cross_party_voting_patterns(politician_name, min_coalition_size=3):
    """Identify patterns of cross-party collaboration"""
    votes = analyzer.get_politician_votes(politician_name, limit=2000)
    
    cross_party_coalitions = []
    
    for vote in votes['value']:
        if 'Afstemning' in vote and vote['Afstemning']:
            session_id = vote['Afstemning']['id']
            politician_vote = vote['typeid']
            
            # Get all votes from the same session
            session_details = analyzer.get_voting_session_details(session_id)
            
            if session_details['value']:
                all_votes = session_details['value'][0].get('Stemme', [])
                coalition_partners = find_voting_coalition(politician_vote, all_votes, min_coalition_size)
                
                if coalition_partners:
                    cross_party_coalitions.append({
                        'session_id': session_id,
                        'vote_type': politician_vote,
                        'coalition_size': len(coalition_partners),
                        'partners': coalition_partners[:10],  # Limit for readability
                        'date': vote['Afstemning'].get('dato')
                    })
    
    return analyze_coalition_patterns(cross_party_coalitions)

def find_voting_coalition(target_vote, all_votes, min_size):
    """Find politicians who voted the same way"""
    coalition = []
    
    for vote in all_votes:
        if vote['typeid'] == target_vote and 'Aktør' in vote and vote['Aktør']:
            coalition.append({
                'name': vote['Aktør'].get('navn', 'Unknown'),
                'party': vote['Aktør'].get('gruppenavnkort', 'Unknown'),
                'actor_id': vote['aktørid']
            })
    
    return coalition if len(coalition) >= min_size else []

def analyze_coalition_patterns(coalitions):
    """Analyze recurring cross-party coalition patterns"""
    partner_frequency = {}
    party_collaboration = {}
    
    for coalition in coalitions:
        for partner in coalition['partners']:
            partner_name = partner['name']
            party_name = partner['party']
            
            if partner_name not in partner_frequency:
                partner_frequency[partner_name] = 0
            partner_frequency[partner_name] += 1
            
            if party_name not in party_collaboration:
                party_collaboration[party_name] = 0
            party_collaboration[party_name] += 1
    
    # Find most frequent collaborators
    top_partners = sorted(partner_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    top_parties = sorted(party_collaboration.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        'total_cross_party_votes': len(coalitions),
        'top_individual_partners': top_partners,
        'top_party_collaborations': top_parties,
        'recent_coalitions': coalitions[-5:]  # Most recent
    }
```

### Rebel Behavior Scoring

```python
def calculate_rebel_score(politician_name, party_name):
    """Calculate a comprehensive rebel behavior score"""
    loyalty_analysis = analyze_party_loyalty(politician_name, party_name)
    cross_party_analysis = analyze_cross_party_voting_patterns(politician_name)
    
    # Scoring components
    base_loyalty = loyalty_analysis['loyalty_rate']
    deviation_frequency = loyalty_analysis['total_deviations'] / loyalty_analysis['metrics']['total_votes']
    cross_party_frequency = len(cross_party_analysis.get('recent_coalitions', [])) / 100  # Normalize
    
    # Weight different rebel behaviors
    rebel_score = (
        (1 - base_loyalty) * 0.5 +  # 50% weight to party line deviations
        deviation_frequency * 0.3 +  # 30% weight to deviation frequency
        min(cross_party_frequency, 1.0) * 0.2  # 20% weight to cross-party voting
    )
    
    # Categorize rebel behavior
    if rebel_score >= 0.7:
        category = "High Rebel"
    elif rebel_score >= 0.4:
        category = "Moderate Rebel"
    elif rebel_score >= 0.2:
        category = "Occasional Rebel"
    else:
        category = "Party Loyalist"
    
    return {
        'rebel_score': rebel_score,
        'category': category,
        'loyalty_rate': base_loyalty,
        'deviation_count': loyalty_analysis['total_deviations'],
        'cross_party_instances': len(cross_party_analysis.get('recent_coalitions', []))
    }
```

## Voting Consistency and Prediction Modeling

### Consistency Pattern Analysis

```python
import numpy as np
from collections import defaultdict

def analyze_voting_consistency(politician_name, topic_keywords=None):
    """Analyze consistency in voting patterns across similar issues"""
    votes = analyzer.get_politician_votes(politician_name, limit=3000)
    
    # Group votes by topic if keywords provided
    if topic_keywords:
        topic_votes = filter_votes_by_topic(votes, topic_keywords)
    else:
        topic_votes = votes
    
    consistency_metrics = calculate_consistency_scores(topic_votes)
    trend_analysis = analyze_consistency_trends(topic_votes)
    
    return {
        'overall_consistency': consistency_metrics['overall_score'],
        'topic_consistency': consistency_metrics.get('topic_scores', {}),
        'trend_direction': trend_analysis['direction'],
        'consistency_change_rate': trend_analysis['change_rate'],
        'predictability_score': calculate_predictability(topic_votes)
    }

def calculate_consistency_scores(votes_data):
    """Calculate various consistency metrics"""
    if not votes_data.get('value'):
        return {'overall_score': 0}
    
    votes = votes_data['value']
    vote_sequence = [vote['typeid'] for vote in votes if vote['typeid'] in [1, 2]]  # Only yes/no votes
    
    if len(vote_sequence) < 2:
        return {'overall_score': 0}
    
    # Calculate consistency as inverse of vote changes
    changes = sum(1 for i in range(1, len(vote_sequence)) if vote_sequence[i] != vote_sequence[i-1])
    consistency_score = 1 - (changes / (len(vote_sequence) - 1))
    
    return {'overall_score': consistency_score}

def calculate_predictability(votes_data):
    """Calculate how predictable a politician's voting is"""
    if not votes_data.get('value'):
        return 0
    
    votes = [vote['typeid'] for vote in votes_data['value'] if vote['typeid'] in [1, 2, 3, 4]]
    vote_counts = defaultdict(int)
    
    for vote in votes:
        vote_counts[vote] += 1
    
    total_votes = len(votes)
    if total_votes == 0:
        return 0
    
    # Calculate entropy-based predictability
    probabilities = [count / total_votes for count in vote_counts.values()]
    entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
    max_entropy = np.log2(len(vote_counts))
    
    # Predictability is inverse of normalized entropy
    predictability = 1 - (entropy / max_entropy if max_entropy > 0 else 0)
    
    return predictability

def build_voting_prediction_model(politician_name, feature_window=10):
    """Build a simple prediction model based on voting history"""
    votes = analyzer.get_politician_votes(politician_name, limit=1000)
    
    if not votes.get('value') or len(votes['value']) < feature_window + 1:
        return None
    
    # Prepare training data
    vote_sequence = [vote['typeid'] for vote in reversed(votes['value'])]  # Chronological order
    
    training_features = []
    training_labels = []
    
    for i in range(len(vote_sequence) - feature_window):
        features = vote_sequence[i:i+feature_window]  # Previous votes as features
        label = vote_sequence[i+feature_window]  # Next vote as label
        
        training_features.append(features)
        training_labels.append(label)
    
    # Simple pattern-based prediction
    pattern_accuracy = evaluate_pattern_prediction(training_features, training_labels)
    
    return {
        'model_type': 'pattern_based',
        'training_samples': len(training_features),
        'accuracy_estimate': pattern_accuracy,
        'feature_window': feature_window,
        'most_recent_pattern': vote_sequence[-feature_window:] if len(vote_sequence) >= feature_window else vote_sequence
    }

def evaluate_pattern_prediction(features, labels):
    """Evaluate simple pattern-based prediction accuracy"""
    if not features:
        return 0
    
    correct_predictions = 0
    
    for i in range(len(features)):
        # Simple prediction: most common vote in recent history
        feature_votes = [vote for vote in features[i] if vote in [1, 2]]  # Only yes/no
        if feature_votes:
            predicted_vote = max(set(feature_votes), key=feature_votes.count)
            if predicted_vote == labels[i]:
                correct_predictions += 1
    
    return correct_predictions / len(features) if features else 0
```

## Absence and Abstention Pattern Analysis

### Attendance Pattern Recognition

```python
from datetime import datetime, timedelta

def analyze_attendance_patterns(politician_name, period_days=30):
    """Analyze attendance and absence patterns"""
    votes = analyzer.get_politician_votes(politician_name, limit=2000)
    
    if not votes.get('value'):
        return {'error': 'No voting data found'}
    
    attendance_data = []
    absence_patterns = {'by_day': defaultdict(int), 'by_month': defaultdict(int), 'by_season': defaultdict(int)}
    
    for vote in votes['value']:
        if 'Afstemning' in vote and vote['Afstemning']:
            vote_date = datetime.fromisoformat(vote['Afstemning']['dato'])
            is_absent = vote['typeid'] == 4  # Fravær (absence)
            
            attendance_data.append({
                'date': vote_date,
                'present': not is_absent,
                'vote_type': vote['typeid']
            })
            
            if is_absent:
                absence_patterns['by_day'][vote_date.strftime('%A')] += 1
                absence_patterns['by_month'][vote_date.strftime('%B')] += 1
                
                # Season classification
                month = vote_date.month
                if month in [12, 1, 2]:
                    season = 'Winter'
                elif month in [3, 4, 5]:
                    season = 'Spring'
                elif month in [6, 7, 8]:
                    season = 'Summer'
                else:
                    season = 'Fall'
                absence_patterns['by_season'][season] += 1
    
    return analyze_attendance_trends(attendance_data, absence_patterns)

def analyze_attendance_trends(attendance_data, absence_patterns):
    """Analyze trends in attendance patterns"""
    total_votes = len(attendance_data)
    present_votes = sum(1 for vote in attendance_data if vote['present'])
    
    attendance_rate = present_votes / total_votes if total_votes > 0 else 0
    
    # Find peak absence periods
    peak_absence_day = max(absence_patterns['by_day'].items(), key=lambda x: x[1], default=('None', 0))
    peak_absence_month = max(absence_patterns['by_month'].items(), key=lambda x: x[1], default=('None', 0))
    peak_absence_season = max(absence_patterns['by_season'].items(), key=lambda x: x[1], default=('None', 0))
    
    # Recent trend (last 90 days)
    recent_cutoff = datetime.now() - timedelta(days=90)
    recent_attendance = [vote for vote in attendance_data if vote['date'] >= recent_cutoff]
    recent_rate = sum(1 for vote in recent_attendance if vote['present']) / len(recent_attendance) if recent_attendance else 0
    
    return {
        'overall_attendance_rate': attendance_rate,
        'total_voting_opportunities': total_votes,
        'absences': total_votes - present_votes,
        'peak_absence_day': peak_absence_day,
        'peak_absence_month': peak_absence_month,
        'peak_absence_season': peak_absence_season,
        'recent_attendance_rate': recent_rate,
        'attendance_trend': 'improving' if recent_rate > attendance_rate else 'declining' if recent_rate < attendance_rate else 'stable'
    }

def analyze_strategic_abstentions(politician_name):
    """Analyze patterns in abstention voting (strategic non-commitment)"""
    votes = analyzer.get_politician_votes(politician_name, limit=2000)
    
    abstention_analysis = {'total_abstentions': 0, 'contexts': [], 'timing_patterns': defaultdict(int)}
    
    for vote in votes['value']:
        if vote['typeid'] == 3:  # Hverken for eller imod (abstention)
            abstention_analysis['total_abstentions'] += 1
            
            if 'Afstemning' in vote and vote['Afstemning']:
                vote_date = datetime.fromisoformat(vote['Afstemning']['dato'])
                
                # Get voting session context
                session_details = analyzer.get_voting_session_details(vote['Afstemning']['id'])
                
                context = {
                    'date': vote_date.isoformat(),
                    'session_id': vote['Afstemning']['id'],
                    'outcome': vote['Afstemning'].get('vedtaget', 'unknown'),
                    'margin_analysis': analyze_vote_margin(session_details) if session_details.get('value') else None
                }
                
                abstention_analysis['contexts'].append(context)
                
                # Timing patterns
                abstention_analysis['timing_patterns'][vote_date.strftime('%Y-%m')] += 1
    
    return {
        'abstention_rate': abstention_analysis['total_abstentions'] / len(votes['value']) if votes.get('value') else 0,
        'total_abstentions': abstention_analysis['total_abstentions'],
        'recent_abstentions': abstention_analysis['contexts'][-5:],  # Most recent
        'monthly_patterns': dict(abstention_analysis['timing_patterns']),
        'strategic_assessment': assess_strategic_abstention(abstention_analysis)
    }

def analyze_vote_margin(session_details):
    """Analyze the margin of victory/defeat in a voting session"""
    if not session_details.get('value') or not session_details['value']:
        return None
    
    all_votes = session_details['value'][0].get('Stemme', [])
    vote_counts = {'yes': 0, 'no': 0, 'abstain': 0, 'absent': 0}
    vote_mapping = {1: 'yes', 2: 'no', 3: 'abstain', 4: 'absent'}
    
    for vote in all_votes:
        vote_type = vote_mapping.get(vote['typeid'], 'unknown')
        if vote_type != 'unknown':
            vote_counts[vote_type] += 1
    
    total_participating = vote_counts['yes'] + vote_counts['no']
    margin = abs(vote_counts['yes'] - vote_counts['no'])
    
    return {
        'margin': margin,
        'total_participating': total_participating,
        'margin_percentage': (margin / total_participating) if total_participating > 0 else 0,
        'closeness': 'close' if margin <= 5 else 'decisive',
        'vote_breakdown': vote_counts
    }
```

## Politician Influence and Voting Network Analysis

### Influence Measurement

```python
def calculate_politician_influence(politician_name, influence_window=100):
    """Calculate various measures of political influence"""
    votes = analyzer.get_politician_votes(politician_name, limit=influence_window)
    
    influence_metrics = {
        'voting_alignment_influence': 0,
        'swing_vote_instances': 0,
        'coalition_leadership': 0,
        'agenda_setting_power': 0
    }
    
    swing_votes = []
    
    for vote in votes['value']:
        if 'Afstemning' in vote and vote['Afstemning']:
            session_details = analyzer.get_voting_session_details(vote['Afstemning']['id'])
            
            if session_details.get('value'):
                margin_analysis = analyze_vote_margin(session_details)
                
                # Identify swing vote situations
                if margin_analysis and margin_analysis['closeness'] == 'close':
                    swing_votes.append({
                        'session_id': vote['Afstemning']['id'],
                        'politician_vote': vote['typeid'],
                        'margin': margin_analysis['margin'],
                        'outcome': vote['Afstemning'].get('vedtaget')
                    })
                    influence_metrics['swing_vote_instances'] += 1
    
    # Calculate alignment influence (how often others vote the same way)
    alignment_score = calculate_voting_alignment_influence(politician_name, votes)
    influence_metrics['voting_alignment_influence'] = alignment_score
    
    return {
        'influence_score': calculate_composite_influence_score(influence_metrics),
        'swing_vote_count': len(swing_votes),
        'alignment_influence': alignment_score,
        'recent_swing_votes': swing_votes[-3:],  # Most recent swing votes
        'influence_category': categorize_influence_level(influence_metrics)
    }

def calculate_voting_alignment_influence(politician_name, politician_votes):
    """Measure how often other politicians align with this politician's votes"""
    alignment_scores = []
    
    for vote in politician_votes['value'][:20]:  # Sample recent votes
        if 'Afstemning' in vote and vote['Afstemning']:
            session_details = analyzer.get_voting_session_details(vote['Afstemning']['id'])
            
            if session_details.get('value'):
                all_votes = session_details['value'][0].get('Stemme', [])
                politician_vote_type = vote['typeid']
                
                # Count how many others voted the same way
                same_vote_count = sum(1 for v in all_votes if v['typeid'] == politician_vote_type)
                total_votes = len([v for v in all_votes if v['typeid'] in [1, 2]])  # Only yes/no
                
                if total_votes > 1:
                    alignment_ratio = (same_vote_count - 1) / (total_votes - 1)  # Exclude self
                    alignment_scores.append(alignment_ratio)
    
    return sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0

def calculate_composite_influence_score(metrics):
    """Calculate composite influence score from various metrics"""
    swing_weight = min(metrics['swing_vote_instances'] / 20, 1.0) * 0.4  # Max 40%
    alignment_weight = metrics['voting_alignment_influence'] * 0.6  # Max 60%
    
    return swing_weight + alignment_weight

def categorize_influence_level(metrics):
    """Categorize politician's influence level"""
    composite_score = calculate_composite_influence_score(metrics)
    
    if composite_score >= 0.8:
        return "High Influence"
    elif composite_score >= 0.6:
        return "Moderate Influence"
    elif composite_score >= 0.4:
        return "Limited Influence"
    else:
        return "Low Influence"
```

### Network Analysis and Coalition Mapping

```python
def build_voting_network(politicians_list, sample_size=50):
    """Build a network of voting relationships between politicians"""
    network = {}
    
    for politician in politicians_list:
        votes = analyzer.get_politician_votes(politician, limit=sample_size)
        network[politician] = {}
        
        # For each vote, find who else voted the same way
        for vote in votes['value'][:sample_size]:  # Limit for performance
            if 'Afstemning' in vote and vote['Afstemning']:
                session_details = analyzer.get_voting_session_details(vote['Afstemning']['id'])
                
                if session_details.get('value'):
                    all_votes = session_details['value'][0].get('Stemme', [])
                    politician_vote_type = vote['typeid']
                    
                    # Find alignment with other politicians
                    for other_vote in all_votes:
                        if other_vote['typeid'] == politician_vote_type and 'Aktør' in other_vote:
                            other_name = other_vote['Aktör'].get('navn', 'Unknown')
                            
                            if other_name != politician and other_name in politicians_list:
                                if other_name not in network[politician]:
                                    network[politician][other_name] = 0
                                network[politician][other_name] += 1
    
    return analyze_network_patterns(network)

def analyze_network_patterns(network):
    """Analyze patterns in the voting network"""
    network_metrics = {}
    
    for politician, connections in network.items():
        if connections:
            strongest_ally = max(connections.items(), key=lambda x: x[1])
            total_alignments = sum(connections.values())
            unique_connections = len(connections)
            
            network_metrics[politician] = {
                'strongest_ally': strongest_ally,
                'total_alignments': total_alignments,
                'unique_allies': unique_connections,
                'avg_alignment_strength': total_alignments / unique_connections if unique_connections > 0 else 0
            }
    
    return {
        'individual_metrics': network_metrics,
        'network_clusters': identify_voting_clusters(network),
        'cross_party_bridges': find_cross_party_bridges(network)
    }

def identify_voting_clusters(network):
    """Identify clusters of politicians who frequently vote together"""
    clusters = []
    processed = set()
    
    for politician, connections in network.items():
        if politician in processed:
            continue
            
        # Find politicians with high mutual alignment
        cluster = {politician}
        for ally, strength in connections.items():
            if strength >= 10:  # Threshold for strong alignment
                cluster.add(ally)
                processed.add(ally)
        
        if len(cluster) > 1:
            clusters.append(list(cluster))
            processed.update(cluster)
    
    return clusters[:10]  # Top 10 clusters

def find_cross_party_bridges(network):
    """Identify politicians who frequently vote across party lines"""
    # This would require party affiliation data from the Aktør entity
    # Simplified implementation focusing on high cross-connection politicians
    bridge_politicians = {}
    
    for politician, connections in network.items():
        if connections:
            connection_count = len(connections)
            total_strength = sum(connections.values())
            
            # High connection diversity suggests cross-party voting
            if connection_count >= 5 and total_strength >= 20:
                bridge_politicians[politician] = {
                    'connection_diversity': connection_count,
                    'total_alignments': total_strength,
                    'bridge_score': connection_count * (total_strength / connection_count)
                }
    
    return sorted(bridge_politicians.items(), key=lambda x: x[1]['bridge_score'], reverse=True)[:5]
```

## Comparative Politician Analysis and Ranking Systems

### Multi-Dimensional Politician Comparison

```python
def compare_politicians(politician_names, comparison_metrics=None):
    """Comprehensive comparison across multiple politicians"""
    if comparison_metrics is None:
        comparison_metrics = ['voting_frequency', 'party_loyalty', 'influence', 'consistency', 'attendance']
    
    comparison_results = {}
    
    for politician in politician_names:
        politician_profile = build_comprehensive_politician_profile(politician)
        comparison_results[politician] = politician_profile
    
    # Generate rankings for each metric
    rankings = {}
    for metric in comparison_metrics:
        rankings[metric] = rank_politicians_by_metric(comparison_results, metric)
    
    return {
        'individual_profiles': comparison_results,
        'metric_rankings': rankings,
        'overall_ranking': calculate_overall_ranking(comparison_results, comparison_metrics),
        'comparative_analysis': generate_comparative_insights(comparison_results)
    }

def build_comprehensive_politician_profile(politician_name):
    """Build a complete profile for politician comparison"""
    votes = analyzer.get_politician_votes(politician_name, limit=1000)
    
    profile = {
        'name': politician_name,
        'total_votes': len(votes['value']) if votes.get('value') else 0,
        'voting_frequency': calculate_voting_frequency(votes),
        'party_loyalty': analyze_party_loyalty(politician_name, None)['loyalty_rate'],
        'influence_score': calculate_politician_influence(politician_name)['influence_score'],
        'consistency_score': analyze_voting_consistency(politician_name)['overall_consistency'],
        'attendance_rate': analyze_attendance_patterns(politician_name)['overall_attendance_rate'],
        'rebel_score': calculate_rebel_score(politician_name, None)['rebel_score'],
        'cross_party_activity': len(analyze_cross_party_voting_patterns(politician_name).get('recent_coalitions', [])),
        'abstention_rate': analyze_strategic_abstentions(politician_name)['abstention_rate']
    }
    
    return profile

def rank_politicians_by_metric(comparison_results, metric):
    """Rank politicians by a specific metric"""
    politicians_with_metric = [(name, data.get(metric, 0)) for name, data in comparison_results.items()]
    
    # Sort by metric value (descending for positive metrics)
    if metric in ['rebel_score', 'abstention_rate']:
        ranked = sorted(politicians_with_metric, key=lambda x: x[1])  # Ascending for negative metrics
    else:
        ranked = sorted(politicians_with_metric, key=lambda x: x[1], reverse=True)  # Descending for positive metrics
    
    return [(i+1, name, score) for i, (name, score) in enumerate(ranked)]

def calculate_overall_ranking(comparison_results, metrics):
    """Calculate overall ranking using weighted combination of metrics"""
    metric_weights = {
        'voting_frequency': 0.15,
        'party_loyalty': 0.20,
        'influence_score': 0.25,
        'consistency_score': 0.15,
        'attendance_rate': 0.15,
        'rebel_score': -0.05,  # Negative weight (lower is better for extremes)
        'cross_party_activity': 0.10,
        'abstention_rate': -0.05  # Negative weight
    }
    
    overall_scores = {}
    
    for politician, profile in comparison_results.items():
        weighted_score = 0
        for metric, weight in metric_weights.items():
            if metric in profile:
                weighted_score += profile[metric] * weight
        overall_scores[politician] = weighted_score
    
    return sorted(overall_scores.items(), key=lambda x: x[1], reverse=True)

def generate_comparative_insights(comparison_results):
    """Generate insights from politician comparisons"""
    insights = []
    
    # Find extremes
    most_loyal = max(comparison_results.items(), key=lambda x: x[1].get('party_loyalty', 0))
    most_rebel = max(comparison_results.items(), key=lambda x: x[1].get('rebel_score', 0))
    most_influential = max(comparison_results.items(), key=lambda x: x[1].get('influence_score', 0))
    most_consistent = max(comparison_results.items(), key=lambda x: x[1].get('consistency_score', 0))
    
    insights.extend([
        f"Most party-loyal: {most_loyal[0]} ({most_loyal[1]['party_loyalty']:.2%})",
        f"Biggest rebel: {most_rebel[0]} (score: {most_rebel[1]['rebel_score']:.2f})",
        f"Most influential: {most_influential[0]} (score: {most_influential[1]['influence_score']:.2f})",
        f"Most consistent: {most_consistent[0]} ({most_consistent[1]['consistency_score']:.2%})"
    ])
    
    return insights

# Example usage for comparative analysis
def run_comparative_analysis():
    """Run a complete comparative analysis"""
    politicians = ["Frank Aaen", "Nicolai Wammen", "Lars Løkke Rasmussen"]  # Example politicians
    
    comparison = compare_politicians(politicians)
    
    print("=== POLITICIAN COMPARATIVE ANALYSIS ===")
    print("\nOverall Rankings:")
    for rank, (politician, score) in enumerate(comparison['overall_ranking'], 1):
        print(f"{rank}. {politician}: {score:.3f}")
    
    print("\nKey Insights:")
    for insight in comparison['comparative_analysis']:
        print(f"" {insight}")
    
    return comparison
```

## Advanced Usage Examples

### Complete Politician Analysis Pipeline

```python
def complete_politician_analysis(politician_name, output_format='detailed'):
    """Run comprehensive analysis on a single politician"""
    print(f"Running complete analysis for: {politician_name}")
    
    analyses = {
        'basic_profile': build_comprehensive_politician_profile(politician_name),
        'voting_patterns': analyze_voting_consistency(politician_name),
        'party_relationships': analyze_party_loyalty(politician_name, None),
        'cross_party_behavior': analyze_cross_party_voting_patterns(politician_name),
        'attendance_patterns': analyze_attendance_patterns(politician_name),
        'influence_metrics': calculate_politician_influence(politician_name),
        'rebel_analysis': calculate_rebel_score(politician_name, None),
        'abstention_analysis': analyze_strategic_abstentions(politician_name),
        'career_evolution': build_career_voting_timeline(politician_name)
    }
    
    if output_format == 'summary':
        return generate_politician_summary(analyses)
    else:
        return analyses

def generate_politician_summary(analyses):
    """Generate executive summary of politician analysis"""
    basic = analyses['basic_profile']
    
    summary = f"""
    POLITICIAN ANALYSIS SUMMARY: {basic['name']}
    ==========================================
    
    Overall Activity:
    " Total votes recorded: {basic['total_votes']}
    " Attendance rate: {basic['attendance_rate']:.1%}
    " Voting frequency: {basic['voting_frequency']:.2f} votes/period
    
    Political Behavior:
    " Party loyalty rate: {basic['party_loyalty']:.1%}
    " Rebel score: {basic['rebel_score']:.2f} ({analyses['rebel_analysis']['category']})
    " Consistency score: {basic['consistency_score']:.1%}
    " Abstention rate: {basic['abstention_rate']:.1%}
    
    Influence & Impact:
    " Influence score: {basic['influence_score']:.2f} ({analyses['influence_metrics']['influence_category']})
    " Cross-party collaborations: {basic['cross_party_activity']} instances
    " Swing vote participation: {analyses['influence_metrics']['swing_vote_count']} occasions
    
    Attendance Patterns:
    " Recent attendance trend: {analyses['attendance_patterns']['attendance_trend']}
    " Peak absence period: {analyses['attendance_patterns']['peak_absence_season'][0]}
    """
    
    return summary

# Example: Complete analysis workflow
if __name__ == "__main__":
    # Single politician deep dive
    politician_analysis = complete_politician_analysis("Frank Aaen", "summary")
    print(politician_analysis)
    
    # Multi-politician comparison
    comparative_analysis = run_comparative_analysis()
    
    # Network analysis
    politicians_for_network = ["Frank Aaen", "Nicolai Wammen", "Lars Løkke Rasmussen"]
    network_analysis = build_voting_network(politicians_for_network)
    
    print("\nVoting Network Clusters:")
    for i, cluster in enumerate(network_analysis['network_clusters'], 1):
        print(f"Cluster {i}: {', '.join(cluster)}")
```

## Best Practices and Performance Considerations

### Efficient Data Retrieval

```python
def optimize_data_retrieval():
    """Best practices for efficient API usage"""
    
    # Use appropriate pagination for large datasets
    def get_paginated_votes(politician_name, max_records=5000):
        all_votes = []
        skip = 0
        batch_size = 100  # API optimal batch size
        
        while len(all_votes) < max_records:
            params = {
                '$filter': f"Aktør/navn eq '{politician_name}'",
                '$expand': 'Afstemning,Aktør',
                '$top': batch_size,
                '$skip': skip,
                '$orderby': 'opdateringsdato desc'
            }
            
            url = f"{analyzer.base_url}Stemme?" + urllib.parse.urlencode(params)
            response = requests.get(url)
            
            if response.status_code != 200:
                break
                
            batch_data = response.json()
            if not batch_data.get('value'):
                break
                
            all_votes.extend(batch_data['value'])
            skip += batch_size
            
            # Rate limiting for API courtesy
            time.sleep(0.1)
        
        return {'value': all_votes[:max_records]}
    
    return get_paginated_votes

# Caching strategy for repeated analysis
from functools import lru_cache
import pickle
import os

class CachedPoliticianAnalyzer:
    def __init__(self, cache_dir='politician_cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.analyzer = PoliticianVotingAnalyzer()
    
    def get_cached_votes(self, politician_name, max_age_hours=24):
        """Get votes with local caching"""
        cache_file = os.path.join(self.cache_dir, f"{politician_name.replace(' ', '_')}_votes.pkl")
        
        # Check if cache exists and is fresh
        if os.path.exists(cache_file):
            cache_age = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))).total_seconds() / 3600
            if cache_age < max_age_hours:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        
        # Fetch fresh data
        votes = self.analyzer.get_politician_votes(politician_name, limit=2000)
        
        # Cache the results
        with open(cache_file, 'wb') as f:
            pickle.dump(votes, f)
        
        return votes
```

## Troubleshooting Common Issues

### Data Quality and Edge Cases

```python
def handle_data_quality_issues():
    """Common data quality issues and solutions"""
    
    def clean_politician_name(raw_name):
        """Standardize politician names for consistent querying"""
        # Remove extra whitespace, handle special characters
        cleaned = raw_name.strip()
        cleaned = cleaned.replace('"', '').replace("'", '')
        return cleaned
    
    def validate_voting_data(votes_data):
        """Validate and clean voting data"""
        if not votes_data.get('value'):
            return {'value': [], 'issues': ['No vote data found']}
        
        issues = []
        cleaned_votes = []
        
        for vote in votes_data['value']:
            # Check for required fields
            if not vote.get('typeid') or vote['typeid'] not in [1, 2, 3, 4]:
                issues.append(f"Invalid vote type: {vote.get('typeid')}")
                continue
            
            if not vote.get('aktørid'):
                issues.append("Missing actor ID")
                continue
            
            # Handle missing Afstemning data
            if not vote.get('Afstemning'):
                issues.append(f"Missing voting session data for vote {vote.get('id')}")
                # Still include the vote but mark as incomplete
                vote['_incomplete'] = True
            
            cleaned_votes.append(vote)
        
        return {'value': cleaned_votes, 'issues': issues}
    
    def handle_api_errors(func):
        """Decorator for handling API errors gracefully"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                print(f"API request failed: {e}")
                return {'error': str(e), 'value': []}
            except ValueError as e:
                print(f"Data parsing error: {e}")
                return {'error': str(e), 'value': []}
        return wrapper
    
    return {
        'clean_name': clean_politician_name,
        'validate_data': validate_voting_data,
        'error_handler': handle_api_errors
    }
```

This comprehensive guide provides the foundation for sophisticated analysis of individual politician voting behavior using the Danish Parliamentary Open Data API. The techniques covered enable deep insights into political decision-making patterns, career evolution, and democratic representation effectiveness.

Remember to always URL-encode parameters using `%24` instead of `$` when constructing API queries, and consider implementing caching for repeated analysis to optimize performance and reduce API load.