# Case Progress Tracking

Master the 68-status progression system to build sophisticated case lifecycle monitoring tools that provide unprecedented visibility into Danish legislative processes.

## Understanding the 68-Status System

The Danish Parliament API uses an exceptionally detailed 68-status classification system that tracks every stage of the legislative process from initial proposal to final resolution.

### Status Categories Overview

The 68 statuses can be grouped into major lifecycle phases:

#### Proposal Phase
- **Fremsat** (Proposed) - Initial proposal submission
- **Anmeldt** (Announced) - Formal announcement of proposal
- **Modtaget** (Received) - Official reception acknowledgment

#### Committee Phase  
- **Henvist til udvalg** (Referred to committee) - Assignment to relevant committee
- **Udvalgsbehandling** (Committee processing) - Active committee review
- **Betænkning afgivet** (Report submitted) - Committee report completion

#### Parliamentary Readings
- **1. behandling** (1st reading) - First parliamentary debate
- **2. behandling** (2nd reading) - Second parliamentary debate  
- **3. behandling** (3rd reading) - Final parliamentary debate

#### Final Resolution
- **Vedtaget** (Adopted) - Successfully passed into law
- **Forkastet** (Rejected) - Defeated in vote
- **Bortfaldet** (Lapsed) - Expired without resolution

## Implementation Framework

### Status Progression Tracker

```python
import requests
import urllib.parse
from datetime import datetime, timedelta
from collections import defaultdict, OrderedDict

class CaseProgressTracker:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api/"
        self.status_hierarchy = {}
        self.status_categories = {
            'proposal': ['fremsat', 'anmeldt', 'modtaget'],
            'committee': ['henvist', 'udvalg', 'betænkning'],
            'readings': ['1. behandling', '2. behandling', '3. behandling'],
            'resolution': ['vedtaget', 'forkastet', 'bortfaldet']
        }
        
    def load_all_status_definitions(self):
        """Load and categorize all 68 status definitions"""
        url = f"{self.base_url}Sagsstatus"
        response = requests.get(url)
        
        status_map = {}
        
        if response.json().get('value'):
            for status in response.json()['value']:
                status_info = {
                    'id': status['id'],
                    'name': status['status'],
                    'category': self.categorize_status(status['status']),
                    'phase_order': self.determine_phase_order(status['status'])
                }
                status_map[status['id']] = status_info
        
        return status_map
    
    def categorize_status(self, status_name):
        """Categorize status into major phase groups"""
        status_lower = status_name.lower()
        
        for category, keywords in self.status_categories.items():
            if any(keyword in status_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def determine_phase_order(self, status_name):
        """Determine rough ordering within legislative process"""
        phase_keywords = {
            1: ['fremsat', 'anmeldt', 'modtaget'],
            2: ['henvist', 'til udvalg'],
            3: ['udvalgsbehandling', 'betænkning'],
            4: ['1. behandling'],
            5: ['2. behandling'],
            6: ['3. behandling'],
            7: ['afstemning', 'vedtagelse'],
            8: ['vedtaget', 'forkastet', 'bortfaldet']
        }
        
        status_lower = status_name.lower()
        
        for order, keywords in phase_keywords.items():
            if any(keyword in status_lower for keyword in keywords):
                return order
        
        return 99  # Unknown/other
    
    def track_case_status_history(self, case_id):
        """Track complete status history for a case using Sagstrin"""
        params = {
            '$expand': 'Sagstrinsstatus,Sagstrinstype',
            '$filter': f'sagid eq {case_id}',
            '$orderby': 'opdateringsdato asc'
        }
        
        url = f"{self.base_url}Sagstrin?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        status_history = []
        
        if response.json().get('value'):
            for step in response.json()['value']:
                step_info = {
                    'step_id': step['id'],
                    'date': step['opdateringsdato'],
                    'status': step.get('Sagstrinsstatus', {}).get('status', 'Unknown'),
                    'status_id': step.get('statusid', 0),
                    'step_type': step.get('Sagstrinstype', {}).get('type', 'Unknown'),
                    'step_type_id': step.get('typeid', 0)
                }
                
                status_history.append(step_info)
        
        return status_history
    
    def analyze_progression_patterns(self, case_id):
        """Analyze progression patterns and identify anomalies"""
        status_history = self.track_case_status_history(case_id)
        status_definitions = self.load_all_status_definitions()
        
        if not status_history:
            return None
        
        analysis = {
            'total_steps': len(status_history),
            'duration_days': 0,
            'progression_pattern': [],
            'phase_transitions': [],
            'anomalies': [],
            'current_phase': None,
            'estimated_completion': None
        }
        
        # Calculate duration
        if len(status_history) >= 2:
            first_date = datetime.fromisoformat(status_history[0]['date'].replace('T', ' ').replace('Z', ''))
            last_date = datetime.fromisoformat(status_history[-1]['date'].replace('T', ' ').replace('Z', ''))
            analysis['duration_days'] = (last_date - first_date).days
        
        # Build progression pattern with phases
        previous_phase_order = 0
        
        for i, step in enumerate(status_history):
            status_id = step['status_id']
            
            if status_id in status_definitions:
                status_info = status_definitions[status_id]
                phase_order = status_info['phase_order']
                category = status_info['category']
                
                step_analysis = {
                    'step_number': i + 1,
                    'status': step['status'],
                    'category': category,
                    'phase_order': phase_order,
                    'date': step['date']
                }
                
                analysis['progression_pattern'].append(step_analysis)
                
                # Detect phase transitions
                if phase_order != previous_phase_order:
                    transition = {
                        'from_phase': previous_phase_order,
                        'to_phase': phase_order,
                        'date': step['date'],
                        'is_backward': phase_order < previous_phase_order
                    }
                    analysis['phase_transitions'].append(transition)
                    
                    # Flag backward transitions as anomalies
                    if transition['is_backward']:
                        analysis['anomalies'].append({
                            'type': 'backward_progression',
                            'description': f"Moved from phase {previous_phase_order} to {phase_order}",
                            'date': step['date'],
                            'status': step['status']
                        })
                
                previous_phase_order = phase_order
        
        # Determine current phase
        if status_history:
            last_step = status_history[-1]
            last_status_id = last_step['status_id']
            if last_status_id in status_definitions:
                analysis['current_phase'] = status_definitions[last_status_id]['category']
        
        return analysis
```

### Advanced Progress Analytics

```python
class ProgressAnalytics(CaseProgressTracker):
    
    def benchmark_case_against_similar(self, case_id, similarity_criteria=None):
        """Benchmark case progress against similar cases"""
        
        # Get current case information
        case_data = self.get_case_basic_info(case_id)
        case_progress = self.analyze_progression_patterns(case_id)
        
        if not case_data or not case_progress:
            return None
        
        # Build filter for similar cases
        similarity_filter = []
        
        if similarity_criteria:
            if 'case_type' in similarity_criteria:
                similarity_filter.append(f"typeid eq {case_data.get('typeid', 0)}")
            if 'case_category' in similarity_criteria:
                similarity_filter.append(f"kategoriid eq {case_data.get('kategoriid', 0)}")
        else:
            # Default: same case type
            similarity_filter.append(f"typeid eq {case_data.get('typeid', 0)}")
        
        # Get similar cases from recent years
        two_years_ago = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%dT00:00:00')
        similarity_filter.append(f"opdateringsdato gt datetime'{two_years_ago}'")
        
        filter_query = ' and '.join(similarity_filter)
        
        params = {
            '$filter': filter_query,
            '$select': 'id,titel,statusid,opdateringsdato',
            '$top': 200
        }
        
        url = f"{self.base_url}Sag?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        benchmark_data = {
            'current_case': {
                'id': case_id,
                'duration_days': case_progress['duration_days'],
                'steps_completed': case_progress['total_steps'],
                'current_phase': case_progress['current_phase']
            },
            'similar_cases_analyzed': 0,
            'benchmarks': {
                'average_duration': 0,
                'median_duration': 0,
                'average_steps': 0,
                'faster_than_percent': 0,
                'typical_next_steps': []
            }
        }
        
        if response.json().get('value'):
            similar_cases = response.json()['value']
            benchmark_data['similar_cases_analyzed'] = len(similar_cases)
            
            similar_durations = []
            similar_step_counts = []
            
            for similar_case in similar_cases:
                similar_id = similar_case['id']
                
                if similar_id != case_id:  # Don't include the case itself
                    similar_progress = self.analyze_progression_patterns(similar_id)
                    
                    if similar_progress:
                        similar_durations.append(similar_progress['duration_days'])
                        similar_step_counts.append(similar_progress['total_steps'])
            
            if similar_durations:
                # Calculate benchmarks
                benchmark_data['benchmarks']['average_duration'] = sum(similar_durations) / len(similar_durations)
                benchmark_data['benchmarks']['median_duration'] = sorted(similar_durations)[len(similar_durations)//2]
                benchmark_data['benchmarks']['average_steps'] = sum(similar_step_counts) / len(similar_step_counts)
                
                # Calculate percentile ranking
                faster_count = len([d for d in similar_durations if d > case_progress['duration_days']])
                benchmark_data['benchmarks']['faster_than_percent'] = (faster_count / len(similar_durations)) * 100
        
        return benchmark_data
    
    def predict_next_status_transitions(self, case_id):
        """Predict likely next status transitions based on historical patterns"""
        
        case_progress = self.analyze_progression_patterns(case_id)
        
        if not case_progress or not case_progress['progression_pattern']:
            return None
        
        current_step = case_progress['progression_pattern'][-1]
        current_status = current_step['status']
        current_phase = current_step['category']
        
        # Get historical transition patterns from similar cases
        transition_patterns = self.analyze_status_transition_patterns(current_status)
        
        predictions = {
            'current_status': current_status,
            'current_phase': current_phase,
            'likely_next_transitions': [],
            'estimated_timeframes': {},
            'confidence_level': 'medium'
        }
        
        if transition_patterns:
            # Sort transitions by frequency
            sorted_transitions = sorted(
                transition_patterns['next_statuses'].items(), 
                key=lambda x: x[1]['frequency'], 
                reverse=True
            )
            
            total_transitions = sum(t[1]['frequency'] for t in sorted_transitions)
            
            for next_status, data in sorted_transitions[:5]:  # Top 5 most likely
                probability = (data['frequency'] / total_transitions) * 100
                
                prediction = {
                    'status': next_status,
                    'probability_percent': probability,
                    'average_days_to_transition': data['average_days'],
                    'frequency_observed': data['frequency']
                }
                
                predictions['likely_next_transitions'].append(prediction)
        
        return predictions
    
    def analyze_status_transition_patterns(self, current_status, sample_size=500):
        """Analyze historical patterns for transitions from current status"""
        
        # This would require building transition matrices from historical data
        # For brevity, showing the structure - full implementation would involve:
        # 1. Querying all cases that had this status
        # 2. Finding their next status transitions
        # 3. Calculating frequencies and timing patterns
        
        transition_data = {
            'current_status': current_status,
            'total_cases_analyzed': 0,
            'next_statuses': {},
            'average_transition_time': 0
        }
        
        # Implementation would query historical case progressions
        # and build statistical models of transition patterns
        
        return transition_data
    
    def identify_stalled_cases_by_pattern(self, threshold_days=30):
        """Identify cases that appear stalled based on progression patterns"""
        
        # Get recent cases that haven't been updated
        cutoff_date = (datetime.now() - timedelta(days=threshold_days)).strftime('%Y-%m-%dT00:00:00')
        
        params = {
            '$expand': 'Sagsstatus',
            '$filter': f'opdateringsdato lt datetime\'{cutoff_date}\'',
            '$orderby': 'opdateringsdato desc',
            '$top': 200
        }
        
        url = f"{self.base_url}Sag?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        stalled_analysis = {
            'analysis_date': datetime.now().isoformat(),
            'threshold_days': threshold_days,
            'stalled_cases': [],
            'patterns': {
                'most_common_stall_statuses': defaultdict(int),
                'stall_duration_distribution': [],
                'case_type_patterns': defaultdict(int)
            }
        }
        
        if response.json().get('value'):
            cases = response.json()['value']
            
            for case in cases:
                last_update = datetime.fromisoformat(case['opdateringsdato'].replace('T', ' ').replace('Z', ''))
                days_stalled = (datetime.now() - last_update).days
                
                if days_stalled >= threshold_days:
                    case_analysis = self.analyze_progression_patterns(case['id'])
                    
                    stalled_case = {
                        'case_id': case['id'],
                        'title': case.get('titel', 'Unknown'),
                        'current_status': case.get('Sagsstatus', {}).get('status', 'Unknown'),
                        'days_stalled': days_stalled,
                        'last_update': case['opdateringsdato'],
                        'progression_analysis': case_analysis
                    }
                    
                    stalled_analysis['stalled_cases'].append(stalled_case)
                    
                    # Update patterns
                    current_status = stalled_case['current_status']
                    stalled_analysis['patterns']['most_common_stall_statuses'][current_status] += 1
                    stalled_analysis['patterns']['stall_duration_distribution'].append(days_stalled)
        
        return stalled_analysis
```

## Status Transition Visualization

### Progress Timeline Generator

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

class ProgressVisualizer:
    
    def create_case_timeline(self, case_id, title="Case Progress Timeline"):
        """Create visual timeline of case progression"""
        
        tracker = CaseProgressTracker()
        progress = tracker.analyze_progression_patterns(case_id)
        
        if not progress or not progress['progression_pattern']:
            print(f"No progression data available for case {case_id}")
            return
        
        # Prepare data for visualization
        dates = []
        statuses = []
        phases = []
        
        for step in progress['progression_pattern']:
            date_obj = datetime.fromisoformat(step['date'].replace('T', ' ').replace('Z', ''))
            dates.append(date_obj)
            statuses.append(step['status'])
            phases.append(step['category'])
        
        # Create timeline plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        fig.suptitle(f"{title} (Case ID: {case_id})", fontsize=16)
        
        # Main timeline
        phase_colors = {
            'proposal': 'blue',
            'committee': 'orange', 
            'readings': 'green',
            'resolution': 'red',
            'other': 'gray'
        }
        
        colors = [phase_colors.get(phase, 'gray') for phase in phases]
        
        ax1.scatter(dates, range(len(dates)), c=colors, s=100, alpha=0.7)
        
        # Add status labels
        for i, (date, status) in enumerate(zip(dates, statuses)):
            ax1.annotate(status[:30] + ('...' if len(status) > 30 else ''), 
                        (date, i), 
                        xytext=(10, 0), 
                        textcoords='offset points',
                        fontsize=8,
                        ha='left')
        
        ax1.set_ylabel('Progression Steps')
        ax1.set_title('Status Progression')
        ax1.grid(True, alpha=0.3)
        
        # Format dates on x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Phase distribution
        phase_counts = {}
        for phase in phases:
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        ax2.bar(phase_counts.keys(), phase_counts.values(), 
                color=[phase_colors.get(p, 'gray') for p in phase_counts.keys()])
        ax2.set_title('Steps by Phase')
        ax2.set_ylabel('Number of Steps')
        
        plt.tight_layout()
        plt.show()
        
        return progress
    
    def create_status_flow_diagram(self, status_transitions):
        """Create diagram showing status transition flows"""
        
        # This would create a network-style diagram showing
        # how statuses connect to each other
        # Implementation would use networkx and matplotlib
        pass
    
    def compare_case_progressions(self, case_ids, titles=None):
        """Compare progression timelines for multiple cases"""
        
        tracker = CaseProgressTracker()
        
        fig, axes = plt.subplots(len(case_ids), 1, figsize=(15, 4*len(case_ids)))
        if len(case_ids) == 1:
            axes = [axes]
        
        for i, case_id in enumerate(case_ids):
            progress = tracker.analyze_progression_patterns(case_id)
            
            if progress and progress['progression_pattern']:
                dates = []
                phase_orders = []
                
                for step in progress['progression_pattern']:
                    date_obj = datetime.fromisoformat(step['date'].replace('T', ' ').replace('Z', ''))
                    dates.append(date_obj)
                    phase_orders.append(step['phase_order'])
                
                axes[i].plot(dates, phase_orders, marker='o', linewidth=2, markersize=6)
                axes[i].set_title(f"Case {case_id}" + (f": {titles[i]}" if titles and i < len(titles) else ""))
                axes[i].set_ylabel('Phase Order')
                axes[i].grid(True, alpha=0.3)
                axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                plt.setp(axes[i].xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.show()
```

## Real-World Applications

### Legislative Process Monitor

```python
class LegislativeMonitor:
    def __init__(self):
        self.tracker = CaseProgressTracker()
        self.analytics = ProgressAnalytics()
        
    def create_progress_dashboard(self, case_ids, update_frequency='daily'):
        """Create comprehensive progress monitoring dashboard"""
        
        dashboard = {
            'last_updated': datetime.now().isoformat(),
            'update_frequency': update_frequency,
            'cases': {},
            'summary': {
                'total_cases': len(case_ids),
                'active_cases': 0,
                'stalled_cases': 0,
                'average_duration': 0,
                'phase_distribution': defaultdict(int)
            }
        }
        
        durations = []
        
        for case_id in case_ids:
            try:
                progress = self.analytics.analyze_progression_patterns(case_id)
                benchmark = self.analytics.benchmark_case_against_similar(case_id)
                predictions = self.analytics.predict_next_status_transitions(case_id)
                
                case_dashboard = {
                    'case_id': case_id,
                    'current_status': progress['progression_pattern'][-1]['status'] if progress['progression_pattern'] else 'Unknown',
                    'current_phase': progress['current_phase'],
                    'duration_days': progress['duration_days'],
                    'total_steps': progress['total_steps'],
                    'anomalies_count': len(progress['anomalies']),
                    'benchmark_performance': 'faster' if benchmark and benchmark['benchmarks']['faster_than_percent'] > 50 else 'slower',
                    'predicted_next_status': predictions['likely_next_transitions'][0]['status'] if predictions and predictions['likely_next_transitions'] else 'Unknown',
                    'last_activity': progress['progression_pattern'][-1]['date'] if progress['progression_pattern'] else 'Unknown'
                }
                
                dashboard['cases'][case_id] = case_dashboard
                
                # Update summary statistics
                if progress['duration_days'] > 0:
                    durations.append(progress['duration_days'])
                    
                # Check if case is active (updated within 30 days)
                if progress['progression_pattern']:
                    last_update = datetime.fromisoformat(
                        progress['progression_pattern'][-1]['date'].replace('T', ' ').replace('Z', '')
                    )
                    days_since_update = (datetime.now() - last_update).days
                    
                    if days_since_update <= 30:
                        dashboard['summary']['active_cases'] += 1
                    else:
                        dashboard['summary']['stalled_cases'] += 1
                
                # Update phase distribution
                if progress['current_phase']:
                    dashboard['summary']['phase_distribution'][progress['current_phase']] += 1
                    
            except Exception as e:
                print(f"Error processing case {case_id}: {e}")
        
        # Calculate average duration
        if durations:
            dashboard['summary']['average_duration'] = sum(durations) / len(durations)
        
        return dashboard
    
    def setup_automated_alerts(self, alert_rules):
        """Setup automated alerting for case progress issues"""
        
        alerts = []
        
        # Check for stalled cases
        if 'stalled_threshold_days' in alert_rules:
            stalled_analysis = self.analytics.identify_stalled_cases_by_pattern(
                alert_rules['stalled_threshold_days']
            )
            
            if stalled_analysis['stalled_cases']:
                alerts.append({
                    'type': 'stalled_cases',
                    'count': len(stalled_analysis['stalled_cases']),
                    'severity': 'high' if len(stalled_analysis['stalled_cases']) > 10 else 'medium',
                    'details': stalled_analysis['stalled_cases'][:5]  # Top 5 most concerning
                })
        
        # Check for unusual progression patterns
        if 'anomaly_detection' in alert_rules and alert_rules['anomaly_detection']:
            # Implementation would check for unusual status transitions
            pass
        
        return alerts
```

This comprehensive case progress tracking system provides deep insight into the Danish legislative process, enabling sophisticated monitoring applications that support democratic transparency and civic engagement through detailed 68-status progression analysis.