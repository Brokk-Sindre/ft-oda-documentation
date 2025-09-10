# Committee Work Tracking

This guide provides comprehensive coverage of tracking committee activities and work patterns using the Danish Parliamentary OData API. Committees are the backbone of Danish parliamentary work, and the API provides rich data for monitoring their structure, activities, meetings, and decision-making processes.

## Overview

Danish parliamentary committees handle the detailed examination of legislation, conduct hearings, produce reports, and make recommendations to the full parliament. The API offers multiple entry points for analyzing committee work:

- **Committee structure and membership tracking**
- **Meeting scheduling and attendance monitoring**
- **Case assignment and workload analysis**
- **Document production and publication patterns**
- **Member participation and activity metrics**
- **Decision-making process tracking**
- **Inter-committee collaboration analysis**
- **Performance metrics and reporting**

## 1. Committee Structure and Organization Tracking

### Committee Types and Hierarchy

The API categorizes committees using the `Aktørtype` entity where type ID 3 represents "Udvalg" (Committee):

```python
import requests
import pandas as pd
from datetime import datetime, timedelta

# Get all committees
def get_committees():
    """Fetch all parliamentary committees"""
    url = "https://oda.ft.dk/api/Aktør"
    params = {
        '$filter': 'typeid eq 3',  # Committee type
        '$select': 'id,navn,startdato,slutdato,opdateringsdato',
        '$orderby': 'navn'
    }
    
    response = requests.get(url, params=params)
    committees = response.json()['value']
    
    return pd.DataFrame(committees)

# Get committee details with current membership
def get_committee_membership(committee_id):
    """Get current members of a specific committee"""
    url = "https://oda.ft.dk/api/Aktør"
    params = {
        '$filter': f'id eq {committee_id}',
        '$expand': 'AktørAktørRolle($expand=Aktør)',
        '$select': 'id,navn,AktørAktørRolle'
    }
    
    response = requests.get(url, params=params)
    return response.json()['value'][0]

# Example: Get Financial Committee (FIU) structure
committees_df = get_committees()
fiu_committee = committees_df[committees_df['navn'].str.contains('Finansudvalget', case=False)]
print("Financial Committee (FIU):", fiu_committee.iloc[0]['navn'])
```

### Committee Organizational Analysis

```python
def analyze_committee_structure():
    """Analyze the overall committee structure"""
    committees = get_committees()
    
    analysis = {
        'total_committees': len(committees),
        'active_committees': len(committees[committees['slutdato'].isna()]),
        'committee_names': committees['navn'].tolist(),
        'most_recent_updates': committees.nlargest(5, 'opdateringsdato')[['navn', 'opdateringsdato']]
    }
    
    return analysis

# Get committee structure overview
structure = analyze_committee_structure()
print(f"Total committees: {structure['total_committees']}")
print(f"Active committees: {structure['active_committees']}")
```

## 2. Committee Meeting Scheduling and Attendance

### Meeting Schedule Tracking

Committees follow regular meeting schedules that can be tracked and analyzed:

```python
def get_committee_meetings(committee_name=None, days_ahead=60):
    """Get upcoming committee meetings"""
    base_url = "https://oda.ft.dk/api/Møde"
    
    # Calculate date filter
    start_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    end_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%dT%H:%M:%S')
    
    params = {
        '$filter': f"dato gt datetime'{start_date}' and dato lt datetime'{end_date}'",
        '$expand': 'MødeAktør($expand=Aktør)',
        '$select': 'id,titel,dato,lokale,nummer,MødeAktør',
        '$orderby': 'dato'
    }
    
    # Add committee filter if specified
    if committee_name:
        params['$filter'] += f" and substringof('{committee_name}', titel)"
    
    response = requests.get(base_url, params=params)
    return response.json()['value']

# Example: Track Europaudvalget (European Affairs Committee) meetings
eu_meetings = get_committee_meetings('Europa')
print(f"Upcoming EU Committee meetings: {len(eu_meetings)}")

for meeting in eu_meetings[:3]:  # Show first 3
    print(f"Date: {meeting['dato']}, Location: {meeting['lokale']}")
```

### Meeting Attendance Analysis

```python
def analyze_meeting_attendance(committee_meetings):
    """Analyze attendance patterns for committee meetings"""
    attendance_data = []
    
    for meeting in committee_meetings:
        meeting_info = {
            'meeting_id': meeting['id'],
            'date': meeting['dato'],
            'title': meeting['titel'],
            'attendees': []
        }
        
        if 'MødeAktør' in meeting:
            for attendee in meeting['MødeAktør']:
                if 'Aktør' in attendee:
                    meeting_info['attendees'].append({
                        'name': attendee['Aktør']['navn'],
                        'actor_id': attendee['Aktør']['id']
                    })
        
        attendance_data.append(meeting_info)
    
    return attendance_data

# Get detailed attendance for recent meetings
recent_meetings = get_committee_meetings(days_ahead=7)  # Next week
attendance = analyze_meeting_attendance(recent_meetings)
```

## 3. Case Assignment to Committees and Workload Tracking

### Committee Case Assignment

Track which cases are assigned to which committees and monitor workload distribution:

```python
def get_committee_cases(committee_id=None, status_filter=None):
    """Get cases assigned to committees"""
    base_url = "https://oda.ft.dk/api/Sag"
    
    params = {
        '$expand': 'SagAktør($expand=Aktør)',
        '$filter': 'SagAktør/any(sa: sa/Aktør/typeid eq 3)',  # Cases with committee involvement
        '$select': 'id,titel,typeid,statusid,opdateringsdato,periodeid,SagAktør',
        '$orderby': 'opdateringsdato desc'
    }
    
    if committee_id:
        params['$filter'] += f' and SagAktør/any(sa: sa/aktørid eq {committee_id})'
    
    if status_filter:
        params['$filter'] += f' and statusid eq {status_filter}'
    
    response = requests.get(base_url, params=params)
    return response.json()['value']

def analyze_committee_workload():
    """Analyze workload distribution across committees"""
    # Get all recent committee cases
    cases = get_committee_cases()
    
    committee_workload = {}
    
    for case in cases:
        for actor_relation in case.get('SagAktør', []):
            if actor_relation.get('Aktør', {}).get('typeid') == 3:  # Committee
                committee_name = actor_relation['Aktør']['navn']
                if committee_name not in committee_workload:
                    committee_workload[committee_name] = {
                        'total_cases': 0,
                        'recent_updates': 0,
                        'case_titles': []
                    }
                
                committee_workload[committee_name]['total_cases'] += 1
                committee_workload[committee_name]['case_titles'].append(case['titel'])
                
                # Count recent updates (last 30 days)
                update_date = datetime.fromisoformat(case['opdateringsdato'].replace('Z', '+00:00'))
                if (datetime.now(update_date.tzinfo) - update_date).days <= 30:
                    committee_workload[committee_name]['recent_updates'] += 1
    
    return committee_workload

# Analyze current workload
workload = analyze_committee_workload()
print("Committee Workload Analysis:")
for committee, stats in sorted(workload.items(), key=lambda x: x[1]['total_cases'], reverse=True)[:5]:
    print(f"{committee}: {stats['total_cases']} cases, {stats['recent_updates']} recent updates")
```

### Case Processing Timeline

Track how long cases spend in committee review:

```python
def track_case_processing_times(committee_name):
    """Track processing times for cases in committee"""
    base_url = "https://oda.ft.dk/api/Sag"
    
    params = {
        '$expand': 'SagAktør($expand=Aktør),Sagsstatus',
        '$filter': f"SagAktør/any(sa: sa/Aktør/typeid eq 3 and substringof('{committee_name}', sa/Aktør/navn))",
        '$select': 'id,titel,statusid,opdateringsdato,SagAktør,Sagsstatus'
    }
    
    response = requests.get(base_url, params=params)
    cases = response.json()['value']
    
    processing_times = []
    
    for case in cases:
        # Calculate time in committee (simplified - would need more detailed status tracking)
        case_info = {
            'case_id': case['id'],
            'title': case['titel'],
            'status': case.get('Sagsstatus', {}).get('status', 'Unknown'),
            'last_update': case['opdateringsdato']
        }
        processing_times.append(case_info)
    
    return processing_times
```

## 4. Committee Document Production and Publication

### Document Production Tracking

Monitor committee document output and publication patterns:

```python
def get_committee_documents(committee_id, document_type=None):
    """Get documents produced by a committee"""
    base_url = "https://oda.ft.dk/api/Dokument"
    
    params = {
        '$expand': 'DokumentAktør($expand=Aktør)',
        '$filter': f'DokumentAktør/any(da: da/aktørid eq {committee_id})',
        '$select': 'id,titel,dokumenttypeid,dato,offentlighedskode,DokumentAktør',
        '$orderby': 'dato desc'
    }
    
    if document_type:
        params['$filter'] += f' and dokumenttypeid eq {document_type}'
    
    response = requests.get(base_url, params=params)
    return response.json()['value']

def analyze_document_production(committee_id):
    """Analyze document production patterns for a committee"""
    documents = get_committee_documents(committee_id)
    
    # Group by document type
    doc_types = {}
    monthly_production = {}
    
    for doc in documents:
        doc_type = doc['dokumenttypeid']
        doc_date = datetime.fromisoformat(doc['dato'])
        month_key = doc_date.strftime('%Y-%m')
        
        # Count by type
        if doc_type not in doc_types:
            doc_types[doc_type] = 0
        doc_types[doc_type] += 1
        
        # Count by month
        if month_key not in monthly_production:
            monthly_production[month_key] = 0
        monthly_production[month_key] += 1
    
    return {
        'total_documents': len(documents),
        'by_type': doc_types,
        'by_month': monthly_production,
        'recent_documents': documents[:10]  # Most recent 10
    }

# Example: Analyze Financial Committee document production
fiu_id = 1  # Financial Committee ID from earlier example
fiu_docs = analyze_document_production(fiu_id)
print(f"FIU produced {fiu_docs['total_documents']} documents")
```

### Publication Timeline Analysis

```python
def track_publication_delays(committee_id):
    """Track delays between document creation and publication"""
    documents = get_committee_documents(committee_id)
    
    delays = []
    
    for doc in documents:
        # Compare creation vs publication dates (simplified)
        doc_info = {
            'document_id': doc['id'],
            'title': doc['titel'],
            'date': doc['dato'],
            'public': doc['offentlighedskode'] == 'O'  # Open to public
        }
        delays.append(doc_info)
    
    return delays
```

## 5. Member Participation and Activity Analysis

### Individual Member Activity

Track individual member participation in committee work:

```python
def analyze_member_activity(member_id, committee_context=True):
    """Analyze a member's committee activity"""
    
    # Get member's committee memberships
    base_url = "https://oda.ft.dk/api/AktørAktørRolle"
    params = {
        '$filter': f'aktørid eq {member_id}',
        '$expand': 'Aktør,AktørRolle',
        '$select': 'rolleid,startdato,slutdato,Aktør,AktørRolle'
    }
    
    response = requests.get(base_url, params=params)
    memberships = response.json()['value']
    
    # Get member's meeting attendance
    meeting_params = {
        '$filter': f'MødeAktør/any(ma: ma/aktørid eq {member_id})',
        '$expand': 'MødeAktør($expand=Aktør)',
        '$select': 'id,titel,dato,MødeAktør',
        '$orderby': 'dato desc'
    }
    
    meeting_response = requests.get("https://oda.ft.dk/api/Møde", params=meeting_params)
    meetings = meeting_response.json()['value']
    
    return {
        'committee_memberships': len(memberships),
        'meeting_attendance': len(meetings),
        'recent_meetings': meetings[:5],
        'membership_details': memberships
    }

# Example: Analyze specific member's activity
member_activity = analyze_member_activity(12)  # Nicolai Wammen from earlier example
print(f"Member attends {member_activity['meeting_attendance']} meetings")
```

### Committee Member Engagement Metrics

```python
def calculate_engagement_metrics(committee_id, period_days=90):
    """Calculate engagement metrics for committee members"""
    
    # Get committee meetings in period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)
    
    base_url = "https://oda.ft.dk/api/Møde"
    params = {
        '$filter': f"MødeAktør/any(ma: ma/aktørid eq {committee_id}) and dato gt datetime'{start_date.strftime('%Y-%m-%dT%H:%M:%S')}'",
        '$expand': 'MødeAktør($expand=Aktør)',
        '$select': 'id,dato,MødeAktør'
    }
    
    response = requests.get(base_url, params=params)
    meetings = response.json()['value']
    
    # Calculate member attendance rates
    member_attendance = {}
    total_meetings = len(meetings)
    
    for meeting in meetings:
        for attendee in meeting.get('MødeAktør', []):
            if 'Aktør' in attendee:
                member_name = attendee['Aktør']['navn']
                if member_name not in member_attendance:
                    member_attendance[member_name] = 0
                member_attendance[member_name] += 1
    
    # Calculate attendance rates
    engagement_metrics = {}
    for member, count in member_attendance.items():
        engagement_metrics[member] = {
            'meetings_attended': count,
            'total_meetings': total_meetings,
            'attendance_rate': count / total_meetings if total_meetings > 0 else 0
        }
    
    return engagement_metrics
```

## 6. Committee Decision-Making Process Tracking

### Voting Pattern Analysis

Track how committees vote on recommendations and amendments:

```python
def analyze_committee_voting_patterns(committee_id):
    """Analyze voting patterns for committee recommendations"""
    
    # Get committee voting sessions
    base_url = "https://oda.ft.dk/api/Afstemning"
    params = {
        '$filter': f'mødeid ne null and konklusion ne null',
        '$expand': 'Møde,Stemme($expand=Aktør)',
        '$select': 'id,konklusion,vedtaget,afstemningstype,Møde,Stemme'
    }
    
    response = requests.get(base_url, params=params)
    votes = response.json()['value']
    
    # Filter for committee-related votes
    committee_votes = []
    for vote in votes:
        if 'Møde' in vote and vote['Møde']:
            # Check if meeting involves the committee
            if any(str(committee_id) in str(vote['Møde'].get('titel', ''))):
                committee_votes.append(vote)
    
    # Analyze patterns
    patterns = {
        'total_votes': len(committee_votes),
        'passed_votes': len([v for v in committee_votes if v.get('vedtaget', False)]),
        'vote_types': {}
    }
    
    for vote in committee_votes:
        vote_type = vote.get('afstemningstype')
        if vote_type not in patterns['vote_types']:
            patterns['vote_types'][vote_type] = 0
        patterns['vote_types'][vote_type] += 1
    
    return patterns

# Analyze committee recommendation patterns
def track_recommendation_outcomes():
    """Track outcomes of committee recommendations"""
    base_url = "https://oda.ft.dk/api/Afstemning"
    params = {
        '$filter': 'afstemningstype eq 2',  # Committee recommendation type
        '$expand': 'Stemme($expand=Aktør)',
        '$select': 'id,konklusion,vedtaget,Stemme',
        '$orderby': 'id desc',
        '$top': 100
    }
    
    response = requests.get(base_url, params=params)
    recommendations = response.json()['value']
    
    outcomes = {
        'total_recommendations': len(recommendations),
        'adopted_recommendations': len([r for r in recommendations if r.get('vedtaget', False)]),
        'rejection_rate': 0
    }
    
    if outcomes['total_recommendations'] > 0:
        outcomes['rejection_rate'] = (outcomes['total_recommendations'] - outcomes['adopted_recommendations']) / outcomes['total_recommendations']
    
    return outcomes
```

### Decision Timeline Tracking

```python
def track_decision_timeline(case_id):
    """Track the decision timeline for a specific case through committee"""
    
    # Get case voting history
    base_url = "https://oda.ft.dk/api/Afstemning"
    params = {
        '$filter': f'sagid eq {case_id}',
        '$expand': 'Stemme($expand=Aktør),Møde',
        '$select': 'id,dato,afstemningstype,konklusion,vedtaget,Møde,Stemme',
        '$orderby': 'dato'
    }
    
    response = requests.get(base_url, params=params)
    votes = response.json()['value']
    
    timeline = []
    for vote in votes:
        timeline_entry = {
            'date': vote.get('dato'),
            'type': vote.get('afstemningstype'),
            'outcome': vote.get('konklusion'),
            'passed': vote.get('vedtaget', False),
            'meeting': vote.get('Møde', {}).get('titel', 'Unknown')
        }
        timeline.append(timeline_entry)
    
    return timeline
```

## 7. Inter-Committee Collaboration Patterns

### Committee Collaboration Analysis

Track cases that involve multiple committees:

```python
def analyze_inter_committee_collaboration():
    """Analyze collaboration patterns between committees"""
    
    # Get cases with multiple committee involvement
    base_url = "https://oda.ft.dk/api/Sag"
    params = {
        '$expand': 'SagAktør($expand=Aktør)',
        '$filter': 'SagAktør/$count gt 1',  # Cases with multiple actors
        '$select': 'id,titel,SagAktør'
    }
    
    response = requests.get(base_url, params=params)
    cases = response.json()['value']
    
    collaborations = {}
    
    for case in cases:
        committees_involved = []
        for actor_relation in case.get('SagAktør', []):
            if actor_relation.get('Aktør', {}).get('typeid') == 3:  # Committee
                committees_involved.append(actor_relation['Aktør']['navn'])
        
        # Track collaboration patterns
        if len(committees_involved) > 1:
            committees_involved.sort()  # Ensure consistent ordering
            collab_key = ' + '.join(committees_involved)
            
            if collab_key not in collaborations:
                collaborations[collab_key] = {
                    'count': 0,
                    'cases': []
                }
            
            collaborations[collab_key]['count'] += 1
            collaborations[collab_key]['cases'].append({
                'id': case['id'],
                'title': case['titel']
            })
    
    return collaborations

def identify_collaboration_networks():
    """Identify committee collaboration networks"""
    collaborations = analyze_inter_committee_collaboration()
    
    # Build network graph data
    network_data = []
    for collab, data in collaborations.items():
        committees = collab.split(' + ')
        if len(committees) == 2:  # Simple pairwise collaboration
            network_data.append({
                'committee1': committees[0],
                'committee2': committees[1],
                'collaboration_count': data['count']
            })
    
    return network_data
```

### Joint Meeting Analysis

```python
def analyze_joint_meetings():
    """Analyze joint committee meetings"""
    
    # Get meetings with multiple committee representation
    base_url = "https://oda.ft.dk/api/Møde"
    params = {
        '$expand': 'MødeAktør($expand=Aktør)',
        '$filter': 'MødeAktør/$count gt 5',  # Meetings with many participants
        '$select': 'id,titel,dato,MødeAktør'
    }
    
    response = requests.get(base_url, params=params)
    meetings = response.json()['value']
    
    joint_meetings = []
    
    for meeting in meetings:
        committees_present = []
        for participant in meeting.get('MødeAktør', []):
            if participant.get('Aktør', {}).get('typeid') == 3:  # Committee
                committees_present.append(participant['Aktør']['navn'])
        
        if len(committees_present) > 1:
            joint_meetings.append({
                'meeting_id': meeting['id'],
                'title': meeting['titel'],
                'date': meeting['dato'],
                'committees': committees_present
            })
    
    return joint_meetings
```

## 8. Committee Performance Metrics and Analysis

### Performance Dashboard Metrics

Create comprehensive performance metrics for committees:

```python
class CommitteePerformanceDashboard:
    def __init__(self, committee_id):
        self.committee_id = committee_id
        self.committee_name = self.get_committee_name()
    
    def get_committee_name(self):
        """Get committee name"""
        url = "https://oda.ft.dk/api/Aktør"
        params = {'$filter': f'id eq {self.committee_id}', '$select': 'navn'}
        response = requests.get(url, params=params)
        return response.json()['value'][0]['navn']
    
    def get_performance_metrics(self, period_days=90):
        """Generate comprehensive performance metrics"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        metrics = {
            'committee_name': self.committee_name,
            'period': f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}',
            'meeting_frequency': self.calculate_meeting_frequency(start_date, end_date),
            'case_processing': self.calculate_case_processing_metrics(start_date, end_date),
            'document_output': self.calculate_document_metrics(start_date, end_date),
            'member_engagement': self.calculate_member_engagement(start_date, end_date),
            'decision_efficiency': self.calculate_decision_efficiency(start_date, end_date)
        }
        
        return metrics
    
    def calculate_meeting_frequency(self, start_date, end_date):
        """Calculate meeting frequency metrics"""
        url = "https://oda.ft.dk/api/Møde"
        params = {
            '$filter': f"MødeAktør/any(ma: ma/aktørid eq {self.committee_id}) and dato gt datetime'{start_date.strftime('%Y-%m-%dT%H:%M:%S')}' and dato lt datetime'{end_date.strftime('%Y-%m-%dT%H:%M:%S')}'",
            '$select': 'id,dato',
            '$orderby': 'dato'
        }
        
        response = requests.get(url, params=params)
        meetings = response.json()['value']
        
        total_days = (end_date - start_date).days
        meeting_count = len(meetings)
        
        return {
            'total_meetings': meeting_count,
            'meetings_per_week': (meeting_count * 7) / total_days if total_days > 0 else 0,
            'average_days_between_meetings': total_days / meeting_count if meeting_count > 0 else 0
        }
    
    def calculate_case_processing_metrics(self, start_date, end_date):
        """Calculate case processing efficiency"""
        # Get cases the committee has worked on
        url = "https://oda.ft.dk/api/Sag"
        params = {
            '$filter': f"SagAktør/any(sa: sa/aktørid eq {self.committee_id}) and opdateringsdato gt datetime'{start_date.strftime('%Y-%m-%dT%H:%M:%S')}'",
            '$select': 'id,statusid,opdateringsdato'
        }
        
        response = requests.get(url, params=params)
        cases = response.json()['value']
        
        return {
            'cases_processed': len(cases),
            'cases_per_week': (len(cases) * 7) / ((end_date - start_date).days) if (end_date - start_date).days > 0 else 0
        }
    
    def calculate_document_metrics(self, start_date, end_date):
        """Calculate document production metrics"""
        url = "https://oda.ft.dk/api/Dokument"
        params = {
            '$filter': f"DokumentAktør/any(da: da/aktørid eq {self.committee_id}) and dato gt datetime'{start_date.strftime('%Y-%m-%dT%H:%M:%S')}'",
            '$select': 'id,dato,dokumenttypeid'
        }
        
        response = requests.get(url, params=params)
        documents = response.json()['value']
        
        return {
            'documents_produced': len(documents),
            'documents_per_week': (len(documents) * 7) / ((end_date - start_date).days) if (end_date - start_date).days > 0 else 0
        }
    
    def calculate_member_engagement(self, start_date, end_date):
        """Calculate member engagement metrics"""
        # This would require more complex queries to track individual member participation
        # Simplified version returning basic metrics
        return {
            'average_attendance_rate': 0.85,  # Placeholder - would need actual calculation
            'active_members': 12  # Placeholder - would need actual calculation
        }
    
    def calculate_decision_efficiency(self, start_date, end_date):
        """Calculate decision-making efficiency"""
        # Get voting sessions
        url = "https://oda.ft.dk/api/Afstemning"
        params = {
            '$filter': f"dato gt datetime'{start_date.strftime('%Y-%m-%dT%H:%M:%S')}'",
            '$select': 'id,vedtaget,afstemningstype'
        }
        
        response = requests.get(url, params=params)
        votes = response.json()['value']
        
        total_votes = len(votes)
        passed_votes = len([v for v in votes if v.get('vedtaget', False)])
        
        return {
            'total_decisions': total_votes,
            'success_rate': passed_votes / total_votes if total_votes > 0 else 0,
            'decisions_per_week': (total_votes * 7) / ((end_date - start_date).days) if (end_date - start_date).days > 0 else 0
        }

# Example usage
dashboard = CommitteePerformanceDashboard(1)  # Financial Committee
metrics = dashboard.get_performance_metrics()
print(f"Performance metrics for {metrics['committee_name']}:")
print(f"Meeting frequency: {metrics['meeting_frequency']['meetings_per_week']:.2f} per week")
print(f"Case processing: {metrics['case_processing']['cases_per_week']:.2f} per week")
```

### Comparative Performance Analysis

```python
def compare_committee_performance(committee_ids, period_days=90):
    """Compare performance across multiple committees"""
    comparison_data = []
    
    for committee_id in committee_ids:
        dashboard = CommitteePerformanceDashboard(committee_id)
        metrics = dashboard.get_performance_metrics(period_days)
        
        comparison_data.append({
            'committee': metrics['committee_name'],
            'meetings_per_week': metrics['meeting_frequency']['meetings_per_week'],
            'cases_per_week': metrics['case_processing']['cases_per_week'],
            'documents_per_week': metrics['document_output']['documents_per_week'],
            'decision_success_rate': metrics['decision_efficiency']['success_rate']
        })
    
    return pd.DataFrame(comparison_data)

# Example: Compare top 5 committees
top_committees = [1, 2, 3, 4, 5]  # Committee IDs
comparison = compare_committee_performance(top_committees)
print("Committee Performance Comparison:")
print(comparison.to_string(index=False))
```

## 9. Automated Committee Work Monitoring

### Real-time Monitoring System

Set up automated monitoring for committee activities:

```python
import schedule
import time
from datetime import datetime, timedelta

class CommitteeMonitor:
    def __init__(self):
        self.last_check = datetime.now() - timedelta(hours=1)
        
    def check_new_meetings(self):
        """Check for newly scheduled meetings"""
        url = "https://oda.ft.dk/api/Møde"
        params = {
            '$filter': f"opdateringsdato gt datetime'{self.last_check.strftime('%Y-%m-%dT%H:%M:%S')}'",
            '$expand': 'MødeAktør($expand=Aktør)',
            '$select': 'id,titel,dato,lokale,MødeAktør'
        }
        
        response = requests.get(url, params=params)
        new_meetings = response.json()['value']
        
        for meeting in new_meetings:
            self.alert_new_meeting(meeting)
        
        self.last_check = datetime.now()
        return new_meetings
    
    def check_case_updates(self):
        """Check for case updates in committees"""
        url = "https://oda.ft.dk/api/Sag"
        params = {
            '$filter': f"SagAktør/any(sa: sa/Aktør/typeid eq 3) and opdateringsdato gt datetime'{self.last_check.strftime('%Y-%m-%dT%H:%M:%S')}'",
            '$expand': 'SagAktør($expand=Aktør)',
            '$select': 'id,titel,statusid,opdateringsdato,SagAktør'
        }
        
        response = requests.get(url, params=params)
        updated_cases = response.json()['value']
        
        for case in updated_cases:
            self.alert_case_update(case)
        
        return updated_cases
    
    def check_new_documents(self):
        """Check for new committee documents"""
        url = "https://oda.ft.dk/api/Dokument"
        params = {
            '$filter': f"DokumentAktør/any(da: da/Aktør/typeid eq 3) and opdateringsdato gt datetime'{self.last_check.strftime('%Y-%m-%dT%H:%M:%S')}'",
            '$expand': 'DokumentAktør($expand=Aktør)',
            '$select': 'id,titel,dato,dokumenttypeid,DokumentAktør'
        }
        
        response = requests.get(url, params=params)
        new_documents = response.json()['value']
        
        for document in new_documents:
            self.alert_new_document(document)
        
        return new_documents
    
    def alert_new_meeting(self, meeting):
        """Handle new meeting alert"""
        print(f"=Ó New meeting scheduled: {meeting['titel']} at {meeting['dato']}")
        # Could send email, Slack notification, etc.
    
    def alert_case_update(self, case):
        """Handle case update alert"""
        print(f"=Ë Case updated: {case['titel']} (ID: {case['id']})")
        # Could send detailed notification with committee information
    
    def alert_new_document(self, document):
        """Handle new document alert"""
        print(f"=Ä New document: {document['titel']} ({document['dato']})")
        # Could download document, analyze content, etc.
    
    def run_monitoring_cycle(self):
        """Run complete monitoring cycle"""
        print(f"= Running monitoring cycle at {datetime.now()}")
        
        new_meetings = self.check_new_meetings()
        updated_cases = self.check_case_updates()
        new_documents = self.check_new_documents()
        
        print(f"Found: {len(new_meetings)} new meetings, {len(updated_cases)} case updates, {len(new_documents)} new documents")

# Set up automated monitoring
monitor = CommitteeMonitor()

# Schedule monitoring every hour during business hours
schedule.every().hour.do(monitor.run_monitoring_cycle)

# Run monitoring loop
# while True:
#     schedule.run_pending()
#     time.sleep(60)  # Check every minute
```

### Alert Configuration System

```python
class CommitteeAlertSystem:
    def __init__(self):
        self.subscriptions = {}
        
    def subscribe_to_committee(self, committee_id, alert_types=['meetings', 'cases', 'documents']):
        """Subscribe to alerts for a specific committee"""
        if committee_id not in self.subscriptions:
            self.subscriptions[committee_id] = {
                'committee_name': self.get_committee_name(committee_id),
                'alert_types': alert_types,
                'last_check': datetime.now()
            }
    
    def get_committee_name(self, committee_id):
        """Get committee name for subscription"""
        url = "https://oda.ft.dk/api/Aktør"
        params = {'$filter': f'id eq {committee_id}', '$select': 'navn'}
        response = requests.get(url, params=params)
        return response.json()['value'][0]['navn']
    
    def check_committee_alerts(self, committee_id):
        """Check for alerts for specific committee"""
        subscription = self.subscriptions.get(committee_id, {})
        alerts = []
        
        if 'meetings' in subscription.get('alert_types', []):
            # Check meeting alerts
            meeting_alerts = self.check_meeting_alerts(committee_id, subscription['last_check'])
            alerts.extend(meeting_alerts)
        
        if 'cases' in subscription.get('alert_types', []):
            # Check case alerts
            case_alerts = self.check_case_alerts(committee_id, subscription['last_check'])
            alerts.extend(case_alerts)
        
        if 'documents' in subscription.get('alert_types', []):
            # Check document alerts
            document_alerts = self.check_document_alerts(committee_id, subscription['last_check'])
            alerts.extend(document_alerts)
        
        # Update last check time
        self.subscriptions[committee_id]['last_check'] = datetime.now()
        
        return alerts
    
    def check_meeting_alerts(self, committee_id, since_date):
        """Check for new meeting alerts"""
        # Implementation similar to CommitteeMonitor but filtered by committee
        return []  # Placeholder
    
    def check_case_alerts(self, committee_id, since_date):
        """Check for case alerts"""
        # Implementation similar to CommitteeMonitor but filtered by committee
        return []  # Placeholder
    
    def check_document_alerts(self, committee_id, since_date):
        """Check for document alerts"""
        # Implementation similar to CommitteeMonitor but filtered by committee
        return []  # Placeholder

# Example usage
alert_system = CommitteeAlertSystem()
alert_system.subscribe_to_committee(1, ['meetings', 'cases'])  # Financial Committee
alert_system.subscribe_to_committee(3, ['documents'])  # Another committee

# Check alerts for all subscribed committees
for committee_id in alert_system.subscriptions.keys():
    alerts = alert_system.check_committee_alerts(committee_id)
    if alerts:
        committee_name = alert_system.subscriptions[committee_id]['committee_name']
        print(f"Alerts for {committee_name}: {len(alerts)}")
```

## 10. Reporting and Dashboard Creation for Committee Activities

### Committee Activity Report Generator

Create comprehensive reports for committee activities:

```python
class CommitteeReportGenerator:
    def __init__(self, committee_id):
        self.committee_id = committee_id
        self.committee_name = self.get_committee_name()
    
    def get_committee_name(self):
        """Get committee name"""
        url = "https://oda.ft.dk/api/Aktør"
        params = {'$filter': f'id eq {self.committee_id}', '$select': 'navn'}
        response = requests.get(url, params=params)
        return response.json()['value'][0]['navn']
    
    def generate_monthly_report(self, year, month):
        """Generate comprehensive monthly activity report"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        report = {
            'committee': self.committee_name,
            'period': f"{start_date.strftime('%B %Y')}",
            'meetings': self.get_meeting_summary(start_date, end_date),
            'cases': self.get_case_summary(start_date, end_date),
            'documents': self.get_document_summary(start_date, end_date),
            'voting': self.get_voting_summary(start_date, end_date),
            'performance': self.get_performance_summary(start_date, end_date)
        }
        
        return report
    
    def get_meeting_summary(self, start_date, end_date):
        """Get meeting summary for period"""
        url = "https://oda.ft.dk/api/Møde"
        params = {
            '$filter': f"MødeAktør/any(ma: ma/aktørid eq {self.committee_id}) and dato ge datetime'{start_date.strftime('%Y-%m-%dT%H:%M:%S')}' and dato lt datetime'{end_date.strftime('%Y-%m-%dT%H:%M:%S')}'",
            '$expand': 'MødeAktør($expand=Aktør)',
            '$select': 'id,titel,dato,lokale,MødeAktør',
            '$orderby': 'dato'
        }
        
        response = requests.get(url, params=params)
        meetings = response.json()['value']
        
        # Calculate attendance statistics
        total_attendees = sum(len(meeting.get('MødeAktør', [])) for meeting in meetings)
        avg_attendance = total_attendees / len(meetings) if meetings else 0
        
        return {
            'total_meetings': len(meetings),
            'average_attendance': avg_attendance,
            'meeting_details': meetings
        }
    
    def get_case_summary(self, start_date, end_date):
        """Get case processing summary"""
        url = "https://oda.ft.dk/api/Sag"
        params = {
            '$filter': f"SagAktør/any(sa: sa/aktørid eq {self.committee_id}) and opdateringsdato ge datetime'{start_date.strftime('%Y-%m-%dT%H:%M:%S')}' and opdateringsdato lt datetime'{end_date.strftime('%Y-%m-%dT%H:%M:%S')}'",
            '$expand': 'SagAktør($expand=Aktør)',
            '$select': 'id,titel,typeid,statusid,opdateringsdato'
        }
        
        response = requests.get(url, params=params)
        cases = response.json()['value']
        
        # Group by status
        status_counts = {}
        for case in cases:
            status = case.get('statusid', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_cases': len(cases),
            'by_status': status_counts,
            'case_details': cases
        }
    
    def get_document_summary(self, start_date, end_date):
        """Get document production summary"""
        url = "https://oda.ft.dk/api/Dokument"
        params = {
            '$filter': f"DokumentAktør/any(da: da/aktørid eq {self.committee_id}) and dato ge datetime'{start_date.strftime('%Y-%m-%dT%H:%M:%S')}' and dato lt datetime'{end_date.strftime('%Y-%m-%dT%H:%M:%S')}'",
            '$expand': 'DokumentAktør($expand=Aktør)',
            '$select': 'id,titel,dokumenttypeid,dato'
        }
        
        response = requests.get(url, params=params)
        documents = response.json()['value']
        
        # Group by document type
        type_counts = {}
        for doc in documents:
            doc_type = doc.get('dokumenttypeid', 'Unknown')
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        return {
            'total_documents': len(documents),
            'by_type': type_counts,
            'document_details': documents
        }
    
    def get_voting_summary(self, start_date, end_date):
        """Get voting activity summary"""
        # Simplified implementation - would need more complex filtering
        return {
            'total_votes': 0,  # Placeholder
            'success_rate': 0.0  # Placeholder
        }
    
    def get_performance_summary(self, start_date, end_date):
        """Get performance metrics summary"""
        days_in_period = (end_date - start_date).days
        
        meetings = self.get_meeting_summary(start_date, end_date)
        cases = self.get_case_summary(start_date, end_date)
        documents = self.get_document_summary(start_date, end_date)
        
        return {
            'meeting_frequency': meetings['total_meetings'] / (days_in_period / 7) if days_in_period > 0 else 0,
            'case_processing_rate': cases['total_cases'] / (days_in_period / 7) if days_in_period > 0 else 0,
            'document_production_rate': documents['total_documents'] / (days_in_period / 7) if days_in_period > 0 else 0,
            'productivity_index': self.calculate_productivity_index(meetings, cases, documents)
        }
    
    def calculate_productivity_index(self, meetings, cases, documents):
        """Calculate overall productivity index"""
        # Weighted combination of activities
        meeting_weight = 0.3
        case_weight = 0.4
        document_weight = 0.3
        
        meeting_score = min(meetings['total_meetings'] / 10, 1.0)  # Normalize to 0-1
        case_score = min(cases['total_cases'] / 20, 1.0)  # Normalize to 0-1
        document_score = min(documents['total_documents'] / 15, 1.0)  # Normalize to 0-1
        
        productivity_index = (
            meeting_score * meeting_weight +
            case_score * case_weight +
            document_score * document_weight
        )
        
        return productivity_index
    
    def format_report(self, report):
        """Format report for display"""
        formatted_report = f"""
# {report['committee']} - Monthly Activity Report
## {report['period']}

### Meeting Activity
- **Total Meetings:** {report['meetings']['total_meetings']}
- **Average Attendance:** {report['meetings']['average_attendance']:.1f}
- **Meeting Frequency:** {report['performance']['meeting_frequency']:.1f} per week

### Case Processing
- **Total Cases:** {report['cases']['total_cases']}
- **Processing Rate:** {report['performance']['case_processing_rate']:.1f} per week

### Document Production
- **Total Documents:** {report['documents']['total_documents']}
- **Production Rate:** {report['performance']['document_production_rate']:.1f} per week

### Performance Summary
- **Productivity Index:** {report['performance']['productivity_index']:.2f} / 1.0
- **Overall Assessment:** {'Excellent' if report['performance']['productivity_index'] > 0.8 else 'Good' if report['performance']['productivity_index'] > 0.6 else 'Average' if report['performance']['productivity_index'] > 0.4 else 'Below Average'}
"""
        return formatted_report

# Example: Generate report for Financial Committee
report_gen = CommitteeReportGenerator(1)
monthly_report = report_gen.generate_monthly_report(2025, 9)
formatted_report = report_gen.format_report(monthly_report)
print(formatted_report)
```

### Interactive Dashboard Creation

```python
def create_committee_dashboard_data(committee_ids, period_days=90):
    """Create data structure for interactive dashboard"""
    dashboard_data = {
        'committees': [],
        'summary_stats': {},
        'activity_timeline': [],
        'performance_comparison': [],
        'collaboration_network': []
    }
    
    for committee_id in committee_ids:
        # Get committee performance data
        dashboard = CommitteePerformanceDashboard(committee_id)
        metrics = dashboard.get_performance_metrics(period_days)
        
        committee_data = {
            'id': committee_id,
            'name': metrics['committee_name'],
            'metrics': metrics,
            'recent_activity': get_recent_activity(committee_id, 7)  # Last week
        }
        
        dashboard_data['committees'].append(committee_data)
    
    # Calculate summary statistics
    dashboard_data['summary_stats'] = calculate_summary_statistics(dashboard_data['committees'])
    
    # Generate collaboration network data
    dashboard_data['collaboration_network'] = identify_collaboration_networks()
    
    return dashboard_data

def get_recent_activity(committee_id, days=7):
    """Get recent activity summary for dashboard"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    activity = {
        'meetings': 0,
        'cases_updated': 0,
        'documents_published': 0,
        'votes_held': 0
    }
    
    # Get recent meetings
    url = "https://oda.ft.dk/api/Møde"
    params = {
        '$filter': f"MødeAktør/any(ma: ma/aktørid eq {committee_id}) and dato ge datetime'{start_date.strftime('%Y-%m-%dT%H:%M:%S')}'",
        '$select': 'id'
    }
    response = requests.get(url, params=params)
    activity['meetings'] = len(response.json()['value'])
    
    # Get recent case updates
    url = "https://oda.ft.dk/api/Sag"
    params = {
        '$filter': f"SagAktør/any(sa: sa/aktørid eq {committee_id}) and opdateringsdato ge datetime'{start_date.strftime('%Y-%m-%dT%H:%M:%S')}'",
        '$select': 'id'
    }
    response = requests.get(url, params=params)
    activity['cases_updated'] = len(response.json()['value'])
    
    # Get recent documents
    url = "https://oda.ft.dk/api/Dokument"
    params = {
        '$filter': f"DokumentAktør/any(da: da/aktørid eq {committee_id}) and dato ge datetime'{start_date.strftime('%Y-%m-%dT%H:%M:%S')}'",
        '$select': 'id'
    }
    response = requests.get(url, params=params)
    activity['documents_published'] = len(response.json()['value'])
    
    return activity

def calculate_summary_statistics(committees):
    """Calculate overall summary statistics"""
    if not committees:
        return {}
    
    total_meetings = sum(c['recent_activity']['meetings'] for c in committees)
    total_cases = sum(c['recent_activity']['cases_updated'] for c in committees)
    total_documents = sum(c['recent_activity']['documents_published'] for c in committees)
    
    avg_productivity = sum(c['metrics']['decision_efficiency']['success_rate'] for c in committees) / len(committees)
    
    return {
        'total_committees': len(committees),
        'total_meetings_this_week': total_meetings,
        'total_cases_updated': total_cases,
        'total_documents_published': total_documents,
        'average_productivity': avg_productivity
    }

# Example: Create dashboard for top 5 committees
top_committee_ids = [1, 2, 3, 4, 5]
dashboard_data = create_committee_dashboard_data(top_committee_ids)

# Output dashboard summary
print("=Ê Committee Dashboard Summary:")
print(f"Committees monitored: {dashboard_data['summary_stats']['total_committees']}")
print(f"Meetings this week: {dashboard_data['summary_stats']['total_meetings_this_week']}")
print(f"Cases updated: {dashboard_data['summary_stats']['total_cases_updated']}")
print(f"Documents published: {dashboard_data['summary_stats']['total_documents_published']}")
print(f"Average productivity: {dashboard_data['summary_stats']['average_productivity']:.1%}")
```

## Best Practices and Considerations

### API Usage Optimization

1. **Use URL Encoding**: Always use `%24` instead of `$` in OData parameters
2. **Batch Requests**: Combine related queries when possible
3. **Filter Early**: Use `$filter` to reduce response sizes
4. **Select Specific Fields**: Use `$select` to minimize data transfer
5. **Implement Caching**: Cache frequently accessed committee data

### Data Quality and Validation

1. **Handle Missing Data**: Committee data may have gaps or null values
2. **Validate Relationships**: Ensure actor relationships are correctly interpreted
3. **Time Zone Awareness**: All timestamps are in Danish time zone
4. **Regular Updates**: Committee structures and memberships change over time

### Performance Considerations

1. **Rate Limiting**: Implement appropriate delays between API calls
2. **Error Handling**: Handle API timeouts and server errors gracefully
3. **Data Pagination**: Use `$top` and `$skip` for large datasets
4. **Monitoring Frequency**: Balance timeliness with API load

### Security and Compliance

1. **No Authentication Required**: API is public but respect usage guidelines
2. **Data Privacy**: Be mindful of personal information in actor data
3. **Attribution**: Properly attribute data source when publishing analyses
4. **GDPR Compliance**: Consider data protection requirements for stored data

## Conclusion

The Danish Parliamentary OData API provides comprehensive access to committee work data, enabling sophisticated tracking and analysis of parliamentary processes. This guide demonstrates how to build robust monitoring systems that can track everything from basic committee activities to complex inter-committee collaboration patterns.

Key takeaways:

- **Comprehensive Coverage**: The API covers all aspects of committee work from meetings to final decisions
- **Real-time Data**: Near real-time updates enable current activity monitoring
- **Rich Relationships**: Entity relationships provide deep insights into parliamentary processes
- **Flexible Querying**: OData query capabilities support complex analytical requirements
- **Performance Metrics**: Multiple dimensions of committee performance can be measured and compared

By implementing the patterns and techniques outlined in this guide, developers and researchers can create powerful tools for understanding and monitoring the work of Danish parliamentary committees, contributing to democratic transparency and governmental accountability.