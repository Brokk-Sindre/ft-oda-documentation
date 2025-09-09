# Legislative Tracking Guide

Master the complexity of Danish parliamentary procedures by building sophisticated case lifecycle tracking systems using the API's comprehensive 68-status progression system and detailed document flow patterns.

## Overview

The Danish Parliament API provides unprecedented visibility into legislative processes through:

- **68 Detailed Status Types** - From initial proposal to final adoption
- **Case Step Tracking** - Granular progression through parliamentary stages  
- **Document Flow** - Complete paper trail of legislative documents
- **Committee Integration** - Track cases through committee processes
- **Timeline Reconstruction** - Build complete legislative histories

This enables building powerful applications for legislative monitoring, civic engagement, and government transparency.

## Key Entities for Legislative Tracking

### Core Legislative Process Flow
```
Sag (Case) → Sagstrin (Case Steps) → Afstemning (Voting) → Dokument (Documents)
     ↓              ↓                      ↓                    ↓
Sagsstatus    Sagstrinsstatus      Afstemningstype      Dokumenttype
(68 types)     (Step status)       (Vote types)         (28 types)
```

### Essential Fields for Tracking
- **opdateringsdato** - Track when status changes occur
- **statusid** - Current position in 68-status lifecycle  
- **titel** - Legislative proposal title and description
- **periodeid** - Parliamentary session context
- **typeid** - Legislative category (13 case types)

## Implementation Framework

### Basic Case Lifecycle Tracker

```python
import requests
import urllib.parse
from datetime import datetime, timedelta
from collections import defaultdict

class LegislativeTracker:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api/"
        self.status_cache = {}
        
    def get_case_with_full_context(self, case_id):
        """Get complete case information with status and relationships"""
        params = {
            '$expand': 'Sagsstatus,Sagstype,Sagskategori,Periode,SagDokument/Dokument,SagAktør/Aktør,Sagstrin',
            '$filter': f'id eq {case_id}'
        }
        
        url = f"{self.base_url}Sag?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        return response.json()
    
    def track_case_progression(self, case_id):
        """Track a case's progression through the legislative process"""
        # Get case steps ordered by date
        params = {
            '$expand': 'Sagstrinsstatus,Sagstrinstype,SagstrinDokument/Dokument,SagstrinAktør/Aktør',
            '$filter': f'sagid eq {case_id}',
            '$orderby': 'opdateringsdato asc'
        }
        
        url = f"{self.base_url}Sagstrin?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        if response.json().get('value'):
            steps = response.json()['value']
            
            progression = []
            for step in steps:
                step_info = {
                    'step_id': step['id'],
                    'date': step['opdateringsdato'],
                    'status': step.get('Sagstrinsstatus', {}).get('status', 'Unknown'),
                    'type': step.get('Sagstrinstype', {}).get('type', 'Unknown'),
                    'documents': [],
                    'actors': []
                }
                
                # Add associated documents
                if 'SagstrinDokument' in step:
                    for doc_rel in step['SagstrinDokument']:
                        if 'Dokument' in doc_rel:
                            step_info['documents'].append({
                                'title': doc_rel['Dokument'].get('titel', 'Unknown'),
                                'type': doc_rel['Dokument'].get('typeid', 0),
                                'date': doc_rel['Dokument'].get('dato', '')
                            })
                
                # Add involved actors
                if 'SagstrinAktør' in step:
                    for actor_rel in step['SagstrinAktør']:
                        if 'Aktør' in actor_rel:
                            step_info['actors'].append({
                                'name': actor_rel['Aktør'].get('navn', 'Unknown'),
                                'role_id': actor_rel.get('rolleid', 0)
                            })
                
                progression.append(step_info)
            
            return progression
        
        return []
    
    def get_status_definitions(self):
        """Get all 68 status definitions for reference"""
        if not self.status_cache:
            url = f"{self.base_url}Sagsstatus"
            response = requests.get(url)
            
            if response.json().get('value'):
                for status in response.json()['value']:
                    self.status_cache[status['id']] = status['status']
        
        return self.status_cache
    
    def analyze_case_timeline(self, case_id):
        """Analyze timing patterns in case progression"""
        progression = self.track_case_progression(case_id)
        
        if not progression:
            return None
        
        timeline_analysis = {
            'total_steps': len(progression),
            'first_step': progression[0]['date'] if progression else None,
            'last_step': progression[-1]['date'] if progression else None,
            'duration_days': 0,
            'step_intervals': [],
            'status_sequence': []
        }
        
        # Calculate duration
        if len(progression) >= 2:
            first_date = datetime.fromisoformat(progression[0]['date'].replace('T', ' ').replace('Z', ''))
            last_date = datetime.fromisoformat(progression[-1]['date'].replace('T', ' ').replace('Z', ''))
            timeline_analysis['duration_days'] = (last_date - first_date).days
        
        # Calculate step intervals
        for i in range(1, len(progression)):
            prev_date = datetime.fromisoformat(progression[i-1]['date'].replace('T', ' ').replace('Z', ''))
            curr_date = datetime.fromisoformat(progression[i]['date'].replace('T', ' ').replace('Z', ''))
            interval = (curr_date - prev_date).days
            timeline_analysis['step_intervals'].append(interval)
        
        # Build status sequence
        timeline_analysis['status_sequence'] = [step['status'] for step in progression]
        
        return timeline_analysis
```

### Advanced Status Flow Analyzer

```python
class StatusFlowAnalyzer(LegislativeTracker):
    
    def map_complete_status_flows(self, sample_size=500):
        """Map common status progression patterns across many cases"""
        
        # Get recent cases with status information
        params = {
            '$expand': 'Sagsstatus',
            '$orderby': 'opdateringsdato desc',
            '$top': sample_size
        }
        
        url = f"{self.base_url}Sag?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        status_flows = defaultdict(lambda: defaultdict(int))
        status_definitions = self.get_status_definitions()
        
        if response.json().get('value'):
            for case in response.json()['value']:
                case_id = case['id']
                progression = self.track_case_progression(case_id)
                
                # Map status transitions
                for i in range(1, len(progression)):
                    prev_status = progression[i-1]['status']
                    curr_status = progression[i]['status']
                    status_flows[prev_status][curr_status] += 1
        
        return dict(status_flows), status_definitions
    
    def identify_common_pathways(self, min_occurrences=5):
        """Identify most common legislative pathways"""
        
        status_flows, status_definitions = self.map_complete_status_flows()
        
        common_pathways = []
        
        for from_status, transitions in status_flows.items():
            for to_status, count in transitions.items():
                if count >= min_occurrences:
                    common_pathways.append({
                        'from_status': from_status,
                        'to_status': to_status,
                        'frequency': count,
                        'pathway': f"{from_status} → {to_status}"
                    })
        
        return sorted(common_pathways, key=lambda x: x['frequency'], reverse=True)
    
    def analyze_bottlenecks(self, time_threshold_days=30):
        """Identify where cases commonly get stuck in the process"""
        
        # Get cases that have been in same status for extended periods
        cutoff_date = (datetime.now() - timedelta(days=time_threshold_days)).strftime('%Y-%m-%dT00:00:00')
        
        params = {
            '$expand': 'Sagsstatus',
            '$filter': f"opdateringsdato lt datetime'{cutoff_date}'",
            '$top': 200
        }
        
        url = f"{self.base_url}Sag?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        bottlenecks = defaultdict(list)
        
        if response.json().get('value'):
            for case in response.json()['value']:
                status_name = case.get('Sagsstatus', {}).get('status', 'Unknown')
                days_in_status = (datetime.now() - datetime.fromisoformat(
                    case['opdateringsdato'].replace('T', ' ').replace('Z', '')
                )).days
                
                if days_in_status >= time_threshold_days:
                    bottlenecks[status_name].append({
                        'case_id': case['id'],
                        'title': case.get('titel', 'Unknown'),
                        'days_in_status': days_in_status,
                        'last_update': case['opdateringsdato']
                    })
        
        # Sort bottlenecks by frequency and duration
        bottleneck_analysis = {}
        for status, cases in bottlenecks.items():
            bottleneck_analysis[status] = {
                'case_count': len(cases),
                'average_duration': sum(c['days_in_status'] for c in cases) / len(cases),
                'max_duration': max(c['days_in_status'] for c in cases),
                'cases': sorted(cases, key=lambda x: x['days_in_status'], reverse=True)[:10]  # Top 10 longest
            }
        
        return bottleneck_analysis
```

## Committee Tracking Implementation

### Committee Flow Analyzer

```python
class CommitteeTracker(LegislativeTracker):
    
    def track_committee_assignments(self, case_id):
        """Track which committees handle a case"""
        
        # Get case-actor relationships to find committee involvement
        params = {
            '$expand': 'Aktør,SagAktørRolle',
            '$filter': f'sagid eq {case_id} and Aktør/typeid eq 5'  # Type 5 = Committee
        }
        
        url = f"{self.base_url}SagAktør?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        committee_involvement = []
        
        if response.json().get('value'):
            for involvement in response.json()['value']:
                if 'Aktør' in involvement:
                    committee_info = {
                        'committee_name': involvement['Aktör'].get('navn', 'Unknown'),
                        'committee_id': involvement['aktørid'],
                        'role': involvement.get('SagAktørRolle', {}).get('rolle', 'Unknown'),
                        'role_id': involvement.get('rolleid', 0)
                    }
                    committee_involvement.append(committee_info)
        
        return committee_involvement
    
    def analyze_committee_workload(self, committee_id, months_back=6):
        """Analyze committee's case workload and processing patterns"""
        
        cutoff_date = (datetime.now() - timedelta(days=months_back*30)).strftime('%Y-%m-%dT00:00:00')
        
        params = {
            '$expand': 'Sag/Sagsstatus,SagAktørRolle',
            '$filter': f'aktørid eq {committee_id} and opdateringsdato gt datetime\'{cutoff_date}\'',
            '$orderby': 'opdateringsdato desc',
            '$top': 500
        }
        
        url = f"{self.base_url}SagAktør?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        workload_analysis = {
            'total_cases': 0,
            'cases_by_status': defaultdict(int),
            'cases_by_month': defaultdict(int),
            'processing_times': [],
            'role_distribution': defaultdict(int)
        }
        
        if response.json().get('value'):
            cases = response.json()['value']
            workload_analysis['total_cases'] = len(cases)
            
            for case_involvement in cases:
                # Status distribution
                if 'Sag' in case_involvement and case_involvement['Sag']:
                    status = case_involvement['Sag'].get('Sagsstatus', {}).get('status', 'Unknown')
                    workload_analysis['cases_by_status'][status] += 1
                
                # Monthly distribution
                update_date = datetime.fromisoformat(case_involvement['opdateringsdato'].replace('T', ' ').replace('Z', ''))
                month_key = f"{update_date.year}-{update_date.month:02d}"
                workload_analysis['cases_by_month'][month_key] += 1
                
                # Role distribution
                role = case_involvement.get('SagAktørRolle', {}).get('rolle', 'Unknown')
                workload_analysis['role_distribution'][role] += 1
        
        return workload_analysis
    
    def find_committee_specializations(self):
        """Find which committees specialize in which types of legislation"""
        
        # Get all committee-case relationships with case categories
        params = {
            '$expand': 'Aktør,Sag/Sagskategori,SagAktørRolle',
            '$filter': 'Aktør/typeid eq 5',  # Committees only
            '$top': 2000
        }
        
        url = f"{self.base_url}SagAktør?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        committee_specializations = defaultdict(lambda: defaultdict(int))
        
        if response.json().get('value'):
            for involvement in response.json()['value']:
                if 'Aktør' in involvement and 'Sag' in involvement:
                    committee_name = involvement['Aktör'].get('navn', 'Unknown')
                    
                    if involvement['Sag'] and 'Sagskategori' in involvement['Sag']:
                        category = involvement['Sag']['Sagskategori'].get('kategori', 'Unknown')
                        committee_specializations[committee_name][category] += 1
        
        # Calculate specialization percentages
        specialization_analysis = {}
        for committee, categories in committee_specializations.items():
            total_cases = sum(categories.values())
            category_percentages = {
                cat: (count / total_cases * 100) for cat, count in categories.items()
            }
            
            specialization_analysis[committee] = {
                'total_cases': total_cases,
                'primary_specialization': max(category_percentages.items(), key=lambda x: x[1]),
                'category_distribution': category_percentages
            }
        
        return specialization_analysis
```

## Document Flow Tracking

### Document Lifecycle Manager

```python
class DocumentFlowTracker(LegislativeTracker):
    
    def trace_document_history(self, case_id):
        """Trace complete document history for a case"""
        
        params = {
            '$expand': 'Dokument/Dokumenttype,Dokument/Dokumentstatus,SagDokumentRolle',
            '$filter': f'sagid eq {case_id}',
            '$orderby': 'Dokument/dato asc'
        }
        
        url = f"{self.base_url}SagDokument?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        document_timeline = []
        
        if response.json().get('value'):
            for doc_relation in response.json()['value']:
                if 'Dokument' in doc_relation:
                    doc = doc_relation['Dokument']
                    
                    doc_info = {
                        'document_id': doc['id'],
                        'title': doc.get('titel', 'Unknown'),
                        'date': doc.get('dato', ''),
                        'type': doc.get('Dokumenttype', {}).get('type', 'Unknown'),
                        'status': doc.get('Dokumentstatus', {}).get('status', 'Unknown'),
                        'role_in_case': doc_relation.get('SagDokumentRolle', {}).get('rolle', 'Unknown'),
                        'url': doc.get('dokumenturl', ''),
                        'update_date': doc.get('opdateringsdato', '')
                    }
                    
                    document_timeline.append(doc_info)
        
        return document_timeline
    
    def analyze_document_patterns(self, case_type_filter=None):
        """Analyze common document patterns in legislative processes"""
        
        params = {
            '$expand': 'Sag/Sagstype,Dokument/Dokumenttype,SagDokumentRolle',
            '$orderby': 'opdateringsdato desc',
            '$top': 1000
        }
        
        if case_type_filter:
            params['$filter'] = f'Sag/typeid eq {case_type_filter}'
        
        url = f"{self.base_url}SagDokument?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        document_patterns = {
            'common_sequences': defaultdict(int),
            'document_type_frequency': defaultdict(int),
            'role_frequency': defaultdict(int),
            'timing_patterns': defaultdict(list)
        }
        
        if response.json().get('value'):
            # Group by case for sequence analysis
            case_documents = defaultdict(list)
            
            for doc_rel in response.json()['value']:
                case_id = doc_rel['sagid']
                
                if 'Dokument' in doc_rel:
                    doc_info = {
                        'type': doc_rel['Dokument'].get('Dokumenttype', {}).get('type', 'Unknown'),
                        'role': doc_rel.get('SagDokumentRolle', {}).get('rolle', 'Unknown'),
                        'date': doc_rel['Dokument'].get('dato', '')
                    }
                    
                    case_documents[case_id].append(doc_info)
                    document_patterns['document_type_frequency'][doc_info['type']] += 1
                    document_patterns['role_frequency'][doc_info['role']] += 1
            
            # Analyze sequences
            for case_id, docs in case_documents.items():
                if len(docs) > 1:
                    # Sort by date
                    sorted_docs = sorted(docs, key=lambda x: x['date'] or '1900-01-01')
                    
                    # Build sequence of document types
                    type_sequence = ' → '.join([doc['type'] for doc in sorted_docs])
                    document_patterns['common_sequences'][type_sequence] += 1
        
        return document_patterns
```

## Real-World Implementation Examples

### 1. Legislative Dashboard

```python
def create_legislative_dashboard(case_ids):
    """Create comprehensive legislative tracking dashboard"""
    
    tracker = StatusFlowAnalyzer()
    committee_tracker = CommitteeTracker()
    doc_tracker = DocumentFlowTracker()
    
    dashboard = {
        'cases': {},
        'summary_statistics': {
            'total_cases': len(case_ids),
            'status_distribution': defaultdict(int),
            'average_duration': 0,
            'committee_involvement': defaultdict(int)
        },
        'generated_at': datetime.now().isoformat()
    }
    
    durations = []
    
    for case_id in case_ids:
        try:
            # Get complete case context
            case_data = tracker.get_case_with_full_context(case_id)
            
            if case_data.get('value'):
                case = case_data['value'][0]
                
                # Timeline analysis
                timeline = tracker.analyze_case_timeline(case_id)
                
                # Committee tracking
                committees = committee_tracker.track_committee_assignments(case_id)
                
                # Document history
                documents = doc_tracker.trace_document_history(case_id)
                
                case_summary = {
                    'id': case_id,
                    'title': case.get('titel', 'Unknown'),
                    'current_status': case.get('Sagsstatus', {}).get('status', 'Unknown'),
                    'timeline': timeline,
                    'committees': committees,
                    'document_count': len(documents),
                    'last_update': case.get('opdateringsdato', '')
                }
                
                dashboard['cases'][case_id] = case_summary
                
                # Update summary statistics
                status = case_summary['current_status']
                dashboard['summary_statistics']['status_distribution'][status] += 1
                
                if timeline and timeline['duration_days'] > 0:
                    durations.append(timeline['duration_days'])
                
                for committee in committees:
                    dashboard['summary_statistics']['committee_involvement'][committee['committee_name']] += 1
        
        except Exception as e:
            print(f"Error processing case {case_id}: {e}")
    
    # Calculate average duration
    if durations:
        dashboard['summary_statistics']['average_duration'] = sum(durations) / len(durations)
    
    return dashboard
```

### 2. Legislative Process Monitor

```python
class LegislativeProcessMonitor:
    def __init__(self):
        self.tracker = StatusFlowAnalyzer()
        self.alerts = []
        
    def setup_monitoring_rules(self, rules):
        """Setup rules for legislative process monitoring"""
        self.monitoring_rules = rules
        
    def check_stalled_cases(self, max_days_in_status=60):
        """Check for cases that may be stalled"""
        bottlenecks = self.tracker.analyze_bottlenecks(max_days_in_status)
        
        stalled_alerts = []
        
        for status, analysis in bottlenecks.items():
            if analysis['case_count'] > 5:  # Multiple cases stalled
                stalled_alerts.append({
                    'type': 'stalled_cases',
                    'status': status,
                    'case_count': analysis['case_count'],
                    'average_duration': analysis['average_duration'],
                    'severity': 'high' if analysis['average_duration'] > 90 else 'medium'
                })
        
        return stalled_alerts
    
    def monitor_unusual_patterns(self):
        """Monitor for unusual patterns in legislative process"""
        status_flows, _ = self.tracker.map_complete_status_flows(sample_size=200)
        
        unusual_patterns = []
        
        # Check for status reversions (unusual backward movement)
        normal_progression_keywords = ['fremsat', 'vedtaget', 'behandling', 'udvalg']
        
        for from_status, transitions in status_flows.items():
            for to_status, count in transitions.items():
                # Simple heuristic: if going from "later" to "earlier" status
                from_later = any(keyword in from_status.lower() for keyword in ['vedtaget', 'slutbehandling'])
                to_earlier = any(keyword in to_status.lower() for keyword in ['fremsat', 'modtaget'])
                
                if from_later and to_earlier and count > 2:
                    unusual_patterns.append({
                        'type': 'status_reversion',
                        'from_status': from_status,
                        'to_status': to_status,
                        'frequency': count,
                        'note': 'Cases moving backward in process'
                    })
        
        return unusual_patterns
    
    def generate_weekly_report(self):
        """Generate weekly legislative activity report"""
        
        # Get recent activity
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT00:00:00')
        
        params = {
            '$expand': 'Sagsstatus,Sagstype',
            '$filter': f"opdateringsdato gt datetime'{week_ago}'",
            '$orderby': 'opdateringsdato desc',
            '$top': 200
        }
        
        url = f"{self.tracker.base_url}Sag?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        weekly_report = {
            'period': f'{week_ago} to {datetime.now().isoformat()}',
            'total_activity': 0,
            'new_cases': 0,
            'status_changes': 0,
            'active_statuses': defaultdict(int),
            'case_types': defaultdict(int),
            'alerts': []
        }
        
        if response.json().get('value'):
            cases = response.json()['value']
            weekly_report['total_activity'] = len(cases)
            
            for case in cases:
                status = case.get('Sagsstatus', {}).get('status', 'Unknown')
                case_type = case.get('Sagstype', {}).get('type', 'Unknown')
                
                weekly_report['active_statuses'][status] += 1
                weekly_report['case_types'][case_type] += 1
                
                # Simple heuristics for categorization
                if 'fremsat' in status.lower() or 'modtaget' in status.lower():
                    weekly_report['new_cases'] += 1
                else:
                    weekly_report['status_changes'] += 1
        
        # Add alerts
        weekly_report['alerts'].extend(self.check_stalled_cases())
        weekly_report['alerts'].extend(self.monitor_unusual_patterns())
        
        return weekly_report
```

## Performance Considerations

### Efficient Bulk Processing

```python
class OptimizedLegislativeTracker:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api/"
        self.cache = {}
        self.batch_size = 100
    
    def bulk_track_cases(self, case_ids):
        """Efficiently track multiple cases"""
        results = {}
        
        # Process in batches to avoid overwhelming the API
        for i in range(0, len(case_ids), self.batch_size):
            batch = case_ids[i:i + self.batch_size]
            
            # Build batch filter
            id_filter = ' or '.join([f'id eq {case_id}' for case_id in batch])
            
            params = {
                '$expand': 'Sagsstatus,Sagstype,Sagskategori',
                '$filter': id_filter,
                '$top': self.batch_size
            }
            
            url = f"{self.base_url}Sag?" + urllib.parse.urlencode(params)
            response = requests.get(url)
            
            if response.json().get('value'):
                for case in response.json()['value']:
                    results[case['id']] = case
        
        return results
    
    def cache_status_definitions(self):
        """Cache status and type definitions for faster lookup"""
        if not hasattr(self, 'status_definitions'):
            # Cache all status types
            url = f"{self.base_url}Sagsstatus"
            response = requests.get(url)
            self.status_definitions = {s['id']: s for s in response.json().get('value', [])}
            
            # Cache case types
            url = f"{self.base_url}Sagstype"
            response = requests.get(url)
            self.case_types = {t['id']: t for t in response.json().get('value', [])}
```

This comprehensive legislative tracking framework provides the tools needed to build sophisticated applications for monitoring Danish parliamentary processes, enabling transparency, civic engagement, and democratic accountability through detailed legislative lifecycle tracking.