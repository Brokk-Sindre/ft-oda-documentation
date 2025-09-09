# Committee Work Tracking

Build sophisticated tools to monitor committee activities, track case assignments, and analyze committee efficiency using the Danish Parliament API's comprehensive committee data structures.

## Overview

Parliamentary committees are central to the Danish legislative process. The API provides detailed tracking of:

- **Committee Assignments** - Which committees handle specific cases
- **Committee Roles** - 23 different role types in case processing
- **Workload Analysis** - Committee capacity and efficiency metrics
- **Member Participation** - Individual politician involvement in committee work
- **Committee Specializations** - Policy area expertise patterns

## Committee Data Architecture

### Key Relationships
```
Aktør (Committee) ←→ SagAktør ←→ Sag (Cases)
      ↓                ↓              ↓
 Aktørtype         SagAktørRolle  Sagskategori
 (Type 5)          (23 roles)     (Categories)
```

### Committee Identification
Committees are identified as `Aktør` entities with `typeid = 5`. They have distinct naming patterns and organizational structures that reflect their specialized functions.

## Implementation Framework

### Committee Activity Tracker

```python
import requests
import urllib.parse
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class CommitteeTracker:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api/"
        self.committee_cache = {}
        self.role_definitions = {}
        
    def load_all_committees(self):
        """Load all parliamentary committees"""
        if self.committee_cache:
            return self.committee_cache
            
        params = {
            '$filter': 'typeid eq 5',  # Committee actor type
            '$orderby': 'navn asc',
            '$top': 100
        }
        
        url = f"{self.base_url}Aktör?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        if response.json().get('value'):
            for committee in response.json()['value']:
                self.committee_cache[committee['id']] = {
                    'id': committee['id'],
                    'name': committee.get('navn', 'Unknown'),
                    'short_name': committee.get('gruppenavnkort', ''),
                    'biography': committee.get('biografi', ''),
                    'start_date': committee.get('startdato', ''),
                    'end_date': committee.get('slutdato', ''),
                    'active': not committee.get('slutdato', '')  # Active if no end date
                }
        
        return self.committee_cache
    
    def load_committee_role_definitions(self):
        """Load all 23 SagAktørRolle definitions"""
        if self.role_definitions:
            return self.role_definitions
            
        url = f"{self.base_url}SagAktørRolle"
        response = requests.get(url)
        
        if response.json().get('value'):
            for role in response.json()['value']:
                self.role_definitions[role['id']] = role['rolle']
        
        return self.role_definitions
    
    def get_committee_case_assignments(self, committee_id, months_back=12, include_details=True):
        """Get all cases assigned to a specific committee"""
        
        cutoff_date = (datetime.now() - timedelta(days=months_back*30)).strftime('%Y-%m-%dT00:00:00')
        
        params = {
            '$filter': f'aktørid eq {committee_id} and opdateringsdato gt datetime\'{cutoff_date}\'',
            '$orderby': 'opdateringsdato desc',
            '$top': 500
        }
        
        if include_details:
            params['$expand'] = 'Sag/Sagsstatus,Sag/Sagstype,Sag/Sagskategori,SagAktørRolle'
        
        url = f"{self.base_url}SagAktør?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        committee_assignments = []
        
        if response.json().get('value'):
            for assignment in response.json()['value']:
                assignment_info = {
                    'assignment_id': assignment['id'],
                    'case_id': assignment['sagid'],
                    'role': assignment.get('SagAktørRolle', {}).get('rolle', 'Unknown'),
                    'role_id': assignment.get('rolleid', 0),
                    'assignment_date': assignment.get('opdateringsdato', '')
                }
                
                if 'Sag' in assignment and assignment['Sag']:
                    case = assignment['Sag']
                    assignment_info.update({
                        'case_title': case.get('titel', 'Unknown'),
                        'case_status': case.get('Sagsstatus', {}).get('status', 'Unknown'),
                        'case_type': case.get('Sagstype', {}).get('type', 'Unknown'),
                        'case_category': case.get('Sagskategori', {}).get('kategori', 'Unknown'),
                        'case_last_update': case.get('opdateringsdato', '')
                    })
                
                committee_assignments.append(assignment_info)
        
        return committee_assignments
    
    def analyze_committee_workload(self, committee_id, analysis_period_months=6):
        """Comprehensive workload analysis for a committee"""
        
        assignments = self.get_committee_case_assignments(committee_id, analysis_period_months)
        committees = self.load_all_committees()
        roles = self.load_committee_role_definitions()
        
        committee_name = committees.get(committee_id, {}).get('name', f'Committee {committee_id}')
        
        workload_analysis = {
            'committee_id': committee_id,
            'committee_name': committee_name,
            'analysis_period_months': analysis_period_months,
            'total_assignments': len(assignments),
            'workload_metrics': {
                'cases_per_month': len(assignments) / analysis_period_months,
                'role_distribution': defaultdict(int),
                'case_type_distribution': defaultdict(int),
                'case_category_distribution': defaultdict(int),
                'status_distribution': defaultdict(int)
            },
            'temporal_patterns': {
                'monthly_volume': defaultdict(int),
                'recent_activity': []
            },
            'case_complexity_indicators': {
                'high_profile_cases': [],
                'long_running_cases': [],
                'multi_committee_cases': []
            }
        }
        
        # Analyze assignment patterns
        for assignment in assignments:
            # Role distribution
            role = assignment['role']
            workload_analysis['workload_metrics']['role_distribution'][role] += 1
            
            # Case type and category distribution
            case_type = assignment.get('case_type', 'Unknown')
            case_category = assignment.get('case_category', 'Unknown')
            workload_analysis['workload_metrics']['case_type_distribution'][case_type] += 1
            workload_analysis['workload_metrics']['case_category_distribution'][case_category] += 1
            
            # Status distribution
            status = assignment.get('case_status', 'Unknown')
            workload_analysis['workload_metrics']['status_distribution'][status] += 1
            
            # Temporal patterns
            try:
                assignment_date = datetime.fromisoformat(assignment['assignment_date'].replace('T', ' ').replace('Z', ''))
                month_key = f"{assignment_date.year}-{assignment_date.month:02d}"
                workload_analysis['temporal_patterns']['monthly_volume'][month_key] += 1
                
                # Recent activity (last 30 days)
                if (datetime.now() - assignment_date).days <= 30:
                    workload_analysis['temporal_patterns']['recent_activity'].append({
                        'case_id': assignment['case_id'],
                        'case_title': assignment.get('case_title', 'Unknown'),
                        'role': assignment['role'],
                        'date': assignment['assignment_date']
                    })
            except:
                pass
            
            # Identify high-profile or complex cases
            case_title = assignment.get('case_title', '').lower()
            
            # High-profile indicators
            high_profile_keywords = ['lovforslag', 'beslutning', 'redegørelse', 'beretning']
            if any(keyword in case_title for keyword in high_profile_keywords):
                workload_analysis['case_complexity_indicators']['high_profile_cases'].append({
                    'case_id': assignment['case_id'],
                    'case_title': assignment.get('case_title', 'Unknown'),
                    'role': assignment['role']
                })
        
        return workload_analysis
```

### Committee Efficiency Analyzer

```python
class CommitteeEfficiencyAnalyzer(CommitteeTracker):
    
    def compare_committee_performance(self, committee_ids, analysis_period_months=12):
        """Compare performance across multiple committees"""
        
        committee_comparison = {
            'analysis_period_months': analysis_period_months,
            'committees_analyzed': len(committee_ids),
            'comparative_metrics': {},
            'efficiency_rankings': {},
            'specialization_analysis': {}
        }
        
        committee_performances = {}
        
        for committee_id in committee_ids:
            workload = self.analyze_committee_workload(committee_id, analysis_period_months)
            
            # Calculate efficiency metrics
            efficiency_metrics = {
                'cases_per_month': workload['workload_metrics']['cases_per_month'],
                'role_diversity': len(workload['workload_metrics']['role_distribution']),
                'case_type_diversity': len(workload['workload_metrics']['case_type_distribution']),
                'recent_activity_level': len(workload['temporal_patterns']['recent_activity']),
                'primary_specialization': None,
                'specialization_focus': 0
            }
            
            # Determine primary specialization
            if workload['workload_metrics']['case_category_distribution']:
                primary_cat = max(
                    workload['workload_metrics']['case_category_distribution'].items(),
                    key=lambda x: x[1]
                )
                efficiency_metrics['primary_specialization'] = primary_cat[0]
                total_cases = sum(workload['workload_metrics']['case_category_distribution'].values())
                efficiency_metrics['specialization_focus'] = (primary_cat[1] / total_cases * 100) if total_cases > 0 else 0
            
            committee_performances[committee_id] = {
                'workload': workload,
                'efficiency_metrics': efficiency_metrics
            }
        
        # Create comparative analysis
        if committee_performances:
            cases_per_month_values = [p['efficiency_metrics']['cases_per_month'] for p in committee_performances.values()]
            
            committee_comparison['comparative_metrics'] = {
                'average_cases_per_month': sum(cases_per_month_values) / len(cases_per_month_values),
                'median_cases_per_month': sorted(cases_per_month_values)[len(cases_per_month_values)//2],
                'most_active_committee': max(committee_performances.items(), key=lambda x: x[1]['efficiency_metrics']['cases_per_month']),
                'most_specialized_committee': max(committee_performances.items(), key=lambda x: x[1]['efficiency_metrics']['specialization_focus'])
            }
        
        committee_comparison['efficiency_rankings'] = committee_performances
        
        return committee_comparison
    
    def identify_committee_bottlenecks(self, committee_id, bottleneck_threshold_days=60):
        """Identify potential bottlenecks in committee processing"""
        
        assignments = self.get_committee_case_assignments(committee_id, 12)  # 12 months of data
        
        bottleneck_analysis = {
            'committee_id': committee_id,
            'analysis_threshold_days': bottleneck_threshold_days,
            'potential_bottlenecks': [],
            'bottleneck_patterns': {
                'status_bottlenecks': defaultdict(list),
                'case_type_bottlenecks': defaultdict(list),
                'role_bottlenecks': defaultdict(list)
            },
            'resolution_suggestions': []
        }
        
        current_date = datetime.now()
        
        for assignment in assignments:
            try:
                case_last_update = datetime.fromisoformat(
                    assignment.get('case_last_update', '1900-01-01').replace('T', ' ').replace('Z', '')
                )
                days_since_update = (current_date - case_last_update).days
                
                if days_since_update >= bottleneck_threshold_days:
                    bottleneck_case = {
                        'case_id': assignment['case_id'],
                        'case_title': assignment.get('case_title', 'Unknown'),
                        'case_status': assignment.get('case_status', 'Unknown'),
                        'case_type': assignment.get('case_type', 'Unknown'),
                        'committee_role': assignment['role'],
                        'days_stalled': days_since_update,
                        'last_update': assignment.get('case_last_update', '')
                    }
                    
                    bottleneck_analysis['potential_bottlenecks'].append(bottleneck_case)
                    
                    # Categorize bottlenecks
                    status = bottleneck_case['case_status']
                    case_type = bottleneck_case['case_type']
                    role = bottleneck_case['committee_role']
                    
                    bottleneck_analysis['bottleneck_patterns']['status_bottlenecks'][status].append(bottleneck_case)
                    bottleneck_analysis['bottleneck_patterns']['case_type_bottlenecks'][case_type].append(bottleneck_case)
                    bottleneck_analysis['bottleneck_patterns']['role_bottlenecks'][role].append(bottleneck_case)
                    
            except:
                pass  # Skip invalid dates
        
        # Generate suggestions based on patterns
        for status, cases in bottleneck_analysis['bottleneck_patterns']['status_bottlenecks'].items():
            if len(cases) >= 3:  # Multiple cases stuck at same status
                bottleneck_analysis['resolution_suggestions'].append({
                    'type': 'status_bottleneck',
                    'issue': f"Multiple cases ({len(cases)}) stalled at status: {status}",
                    'suggestion': f"Review committee procedures for {status} processing",
                    'affected_cases': len(cases)
                })
        
        return bottleneck_analysis
    
    def analyze_committee_collaboration_patterns(self, primary_committee_id):
        """Analyze how committees collaborate on shared cases"""
        
        # Get cases handled by the primary committee
        primary_assignments = self.get_committee_case_assignments(primary_committee_id, 12)
        
        collaboration_analysis = {
            'primary_committee_id': primary_committee_id,
            'collaboration_partners': defaultdict(int),
            'shared_cases': [],
            'collaboration_patterns': {
                'most_frequent_partners': [],
                'case_type_collaborations': defaultdict(lambda: defaultdict(int)),
                'role_based_collaborations': defaultdict(lambda: defaultdict(int))
            }
        }
        
        # For each case handled by primary committee, find other committees involved
        for assignment in primary_assignments:
            case_id = assignment['case_id']
            
            # Get all committee assignments for this case
            params = {
                '$expand': 'Aktör,SagAktørRolle',
                '$filter': f'sagid eq {case_id} and Aktör/typeid eq 5'  # Committees only
            }
            
            url = f"{self.base_url}SagAktör?" + urllib.parse.urlencode(params)
            response = requests.get(url)
            
            if response.json().get('value'):
                case_committees = response.json()['value']
                
                other_committees = []
                for committee_assignment in case_committees:
                    committee_id = committee_assignment['aktørid']
                    
                    if committee_id != primary_committee_id:
                        other_committees.append({
                            'committee_id': committee_id,
                            'committee_name': committee_assignment.get('Aktör', {}).get('navn', 'Unknown'),
                            'role': committee_assignment.get('SagAktörRolle', {}).get('rolle', 'Unknown')
                        })
                        
                        collaboration_analysis['collaboration_partners'][committee_id] += 1
                        
                        # Track collaboration by case type and role
                        case_type = assignment.get('case_type', 'Unknown')
                        primary_role = assignment['role']
                        other_role = committee_assignment.get('SagAktørRolle', {}).get('rolle', 'Unknown')
                        
                        collaboration_analysis['collaboration_patterns']['case_type_collaborations'][case_type][committee_id] += 1
                        collaboration_analysis['collaboration_patterns']['role_based_collaborations'][primary_role][other_role] += 1
                
                if other_committees:
                    collaboration_analysis['shared_cases'].append({
                        'case_id': case_id,
                        'case_title': assignment.get('case_title', 'Unknown'),
                        'case_type': assignment.get('case_type', 'Unknown'),
                        'primary_role': assignment['role'],
                        'collaborating_committees': other_committees
                    })
        
        # Identify most frequent collaboration partners
        if collaboration_analysis['collaboration_partners']:
            sorted_partners = sorted(
                collaboration_analysis['collaboration_partners'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            committees = self.load_all_committees()
            
            for committee_id, collaboration_count in sorted_partners[:5]:  # Top 5 partners
                committee_name = committees.get(committee_id, {}).get('name', f'Committee {committee_id}')
                collaboration_analysis['collaboration_patterns']['most_frequent_partners'].append({
                    'committee_id': committee_id,
                    'committee_name': committee_name,
                    'shared_cases_count': collaboration_count
                })
        
        return collaboration_analysis
```

## Specialized Committee Analysis Tools

### Committee Member Participation Tracker

```python
class CommitteeMemberTracker(CommitteeTracker):
    
    def analyze_member_participation(self, committee_id, include_voting_records=True):
        """Analyze individual member participation in committee work"""
        
        # Get committee member information
        # Note: This requires identifying individual politicians who are committee members
        # Implementation would query SagAktör for individual actors with roles related to committee work
        
        member_participation = {
            'committee_id': committee_id,
            'analysis_period': 'last_12_months',
            'members': [],
            'participation_metrics': {
                'average_case_involvement': 0,
                'most_active_member': None,
                'participation_distribution': {}
            }
        }
        
        # Implementation would involve:
        # 1. Identifying committee members through actor relationships
        # 2. Tracking their involvement in committee cases
        # 3. Analyzing voting patterns if available
        # 4. Measuring activity levels and specializations
        
        return member_participation
    
    def track_member_expertise_development(self, member_id, committee_id):
        """Track how a member's expertise develops over time in committee work"""
        
        expertise_development = {
            'member_id': member_id,
            'committee_id': committee_id,
            'expertise_timeline': [],
            'specialization_evolution': {},
            'case_complexity_progression': []
        }
        
        # Implementation would analyze:
        # 1. Types of cases member has worked on over time
        # 2. Roles taken in different cases
        # 3. Progression from simple to complex cases
        # 4. Development of policy area specializations
        
        return expertise_development
```

### Committee Performance Dashboard

```python
class CommitteePerformanceDashboard:
    
    def __init__(self):
        self.analyzer = CommitteeEfficiencyAnalyzer()
        
    def create_comprehensive_committee_dashboard(self, committee_id):
        """Create comprehensive performance dashboard for a committee"""
        
        dashboard = {
            'committee_id': committee_id,
            'generated_at': datetime.now().isoformat(),
            'dashboard_sections': {}
        }
        
        try:
            # Basic workload analysis
            workload = self.analyzer.analyze_committee_workload(committee_id, 12)
            dashboard['dashboard_sections']['workload_analysis'] = workload
            
            # Bottleneck analysis
            bottlenecks = self.analyzer.identify_committee_bottlenecks(committee_id)
            dashboard['dashboard_sections']['bottleneck_analysis'] = bottlenecks
            
            # Collaboration analysis
            collaboration = self.analyzer.analyze_committee_collaboration_patterns(committee_id)
            dashboard['dashboard_sections']['collaboration_analysis'] = collaboration
            
            # Performance summary
            dashboard['dashboard_sections']['performance_summary'] = {
                'overall_activity_level': 'high' if workload['workload_metrics']['cases_per_month'] > 10 else 'medium' if workload['workload_metrics']['cases_per_month'] > 5 else 'low',
                'specialization_focus': workload.get('case_complexity_indicators', {}).get('primary_specialization', 'General'),
                'bottleneck_risk': 'high' if len(bottlenecks['potential_bottlenecks']) > 10 else 'medium' if len(bottlenecks['potential_bottlenecks']) > 5 else 'low',
                'collaboration_level': 'high' if len(collaboration['collaboration_partners']) > 5 else 'medium' if len(collaboration['collaboration_partners']) > 2 else 'low'
            }
            
        except Exception as e:
            dashboard['error'] = str(e)
        
        return dashboard
    
    def generate_committee_efficiency_report(self, committee_ids):
        """Generate efficiency comparison report across committees"""
        
        comparison = self.analyzer.compare_committee_performance(committee_ids, 12)
        
        report = {
            'report_type': 'committee_efficiency_comparison',
            'generated_at': datetime.now().isoformat(),
            'committees_analyzed': len(committee_ids),
            'executive_summary': {},
            'detailed_analysis': comparison,
            'recommendations': []
        }
        
        if comparison['comparative_metrics']:
            # Generate executive summary
            most_active = comparison['comparative_metrics']['most_active_committee']
            most_specialized = comparison['comparative_metrics']['most_specialized_committee']
            
            report['executive_summary'] = {
                'most_active_committee': {
                    'name': most_active[1]['workload']['committee_name'],
                    'cases_per_month': most_active[1]['efficiency_metrics']['cases_per_month']
                },
                'most_specialized_committee': {
                    'name': most_specialized[1]['workload']['committee_name'],
                    'specialization': most_specialized[1]['efficiency_metrics']['primary_specialization'],
                    'focus_percentage': most_specialized[1]['efficiency_metrics']['specialization_focus']
                },
                'average_activity_level': comparison['comparative_metrics']['average_cases_per_month']
            }
            
            # Generate recommendations
            avg_activity = comparison['comparative_metrics']['average_cases_per_month']
            
            for committee_id, performance in comparison['efficiency_rankings'].items():
                committee_name = performance['workload']['committee_name']
                activity_level = performance['efficiency_metrics']['cases_per_month']
                
                if activity_level < avg_activity * 0.5:  # Significantly below average
                    report['recommendations'].append({
                        'committee': committee_name,
                        'type': 'workload_optimization',
                        'issue': 'Below average activity level',
                        'suggestion': 'Review case assignment procedures and capacity utilization'
                    })
        
        return report
```

## Visualization and Reporting

### Committee Activity Visualizations

```python
import matplotlib.pyplot as plt
import seaborn as sns

class CommitteeVisualizer:
    
    def create_workload_comparison_chart(self, committee_comparison_data):
        """Create visual comparison of committee workloads"""
        
        committees = []
        workloads = []
        
        for committee_id, performance in committee_comparison_data['efficiency_rankings'].items():
            committees.append(performance['workload']['committee_name'])
            workloads.append(performance['efficiency_metrics']['cases_per_month'])
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(committees, workloads)
        
        # Color bars based on activity level
        avg_workload = sum(workloads) / len(workloads) if workloads else 0
        
        for bar, workload in zip(bars, workloads):
            if workload > avg_workload * 1.2:
                bar.set_color('green')  # High activity
            elif workload < avg_workload * 0.8:
                bar.set_color('red')    # Low activity
            else:
                bar.set_color('blue')   # Average activity
        
        plt.title('Committee Workload Comparison (Cases per Month)')
        plt.ylabel('Cases per Month')
        plt.xticks(rotation=45, ha='right')
        plt.axhline(y=avg_workload, color='gray', linestyle='--', label=f'Average ({avg_workload:.1f})')
        plt.legend()
        plt.tight_layout()
        plt.show()
    
    def create_collaboration_network_diagram(self, collaboration_data):
        """Create network diagram showing committee collaboration patterns"""
        
        # This would use networkx to create a network diagram
        # showing how committees collaborate on shared cases
        pass
```

This comprehensive committee work tracking system enables sophisticated analysis of parliamentary committee operations, supporting better resource allocation, process optimization, and democratic oversight through detailed committee performance monitoring.