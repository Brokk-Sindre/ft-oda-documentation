# Real-Time Monitoring Guide

Build sophisticated real-time monitoring systems using the Danish Parliament API's exceptional data freshness, with updates reflected within hours of parliamentary activity and over 50 daily changes during active periods.

## Overview

The Danish Parliament API provides exceptional real-time capabilities through its `opdateringsdato` (update date) field, which enables:

- **Hours-Fresh Data** - Parliamentary activity reflected within 3-8 hours
- **50+ Daily Updates** - High-volume change detection during active periods
- **Business Hours Patterns** - Predictable update windows for optimization
- **Comprehensive Change Tracking** - Every entity supports temporal monitoring
- **Forward Planning Data** - Meeting schedules available months in advance

## Real-Time Data Characteristics

### Update Timing Patterns
Based on comprehensive analysis, the API exhibits consistent update patterns:

- **Morning Updates** (12:00-13:00) - Voting records from midday sessions
- **Afternoon Updates** (16:00-17:00) - Case processing and status changes  
- **Evening Updates** (17:00-18:00) - End-of-day batch processing
- **Same-Day Processing** - Parliamentary actions reflected within hours

### Data Freshness Metrics
- **Latest Case Updates** - Within 3 hours of investigation time
- **Voting Records** - Updated same day as parliamentary sessions
- **Actor Information** - Batch updates with identical timestamps
- **Future Meetings** - Available months in advance for calendar integration

## Implementation Framework

### Real-Time Change Monitor

```python
import requests
import urllib.parse
from datetime import datetime, timedelta
from collections import defaultdict
import time
import threading

class RealTimeMonitor:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api/"
        self.last_check_times = {}
        self.change_callbacks = {}
        self.monitoring_active = False
        
    def setup_entity_monitoring(self, entity_name, check_interval_minutes=60):
        """Setup monitoring for a specific entity type"""
        self.last_check_times[entity_name] = datetime.now() - timedelta(hours=1)  # Start with 1 hour lookback
        
    def get_recent_changes(self, entity_name, hours_back=4):
        """Get all changes in the last N hours for an entity"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        cutoff_string = cutoff_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        params = {
            '$filter': f'opdateringsdato gt datetime\'{cutoff_string}\'',
            '$orderby': 'opdateringsdato desc',
            '$top': 200
        }
        
        # Add entity-specific expansions
        entity_expansions = {
            'Sag': 'Sagsstatus,Sagstype,Sagskategori',
            'Afstemning': 'Sag,Stemme',
            'Aktör': 'Aktørtype',
            'Dokument': 'Dokumenttype,Dokumentstatus',
            'Møde': 'Mødetype,Mødestatus'
        }
        
        if entity_name in entity_expansions:
            params['$expand'] = entity_expansions[entity_name]
        
        url = f"{self.base_url}{entity_name}?" + urllib.parse.urlencode(params)
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching changes for {entity_name}: {e}")
            return None
    
    def detect_incremental_changes(self, entity_name):
        """Detect changes since last check"""
        
        if entity_name not in self.last_check_times:
            self.setup_entity_monitoring(entity_name)
        
        last_check = self.last_check_times[entity_name]
        cutoff_string = last_check.strftime('%Y-%m-%dT%H:%M:%S')
        
        params = {
            '$filter': f'opdateringsdato gt datetime\'{cutoff_string}\'',
            '$orderby': 'opdateringsdato desc',
            '$top': 100
        }
        
        url = f"{self.base_url}{entity_name}?" + urllib.parse.urlencode(params)
        
        changes_detected = []
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get('value'):
                changes_detected = data['value']
                
                # Update last check time to most recent change
                if changes_detected:
                    latest_update = max(
                        datetime.fromisoformat(change['opdateringsdato'].replace('T', ' ').replace('Z', ''))
                        for change in changes_detected
                        if 'opdateringsdato' in change
                    )
                    self.last_check_times[entity_name] = latest_update
                else:
                    self.last_check_times[entity_name] = datetime.now()
            
        except Exception as e:
            print(f"Error detecting changes for {entity_name}: {e}")
        
        return changes_detected
    
    def analyze_change_patterns(self, entity_name, days_back=7):
        """Analyze update patterns over recent days"""
        
        pattern_analysis = {
            'entity_name': entity_name,
            'analysis_period_days': days_back,
            'total_changes': 0,
            'daily_distribution': defaultdict(int),
            'hourly_distribution': defaultdict(int),
            'change_velocity': {
                'changes_per_day': 0,
                'peak_hours': [],
                'quiet_periods': []
            },
            'recent_activity': []
        }
        
        # Get changes for analysis period
        changes_data = self.get_recent_changes(entity_name, days_back * 24)
        
        if changes_data and changes_data.get('value'):
            changes = changes_data['value']
            pattern_analysis['total_changes'] = len(changes)
            pattern_analysis['change_velocity']['changes_per_day'] = len(changes) / days_back
            
            hourly_counts = defaultdict(int)
            daily_counts = defaultdict(int)
            
            for change in changes:
                try:
                    update_time = datetime.fromisoformat(
                        change['opdateringsdato'].replace('T', ' ').replace('Z', '')
                    )
                    
                    day_key = update_time.strftime('%Y-%m-%d')
                    hour = update_time.hour
                    
                    pattern_analysis['daily_distribution'][day_key] += 1
                    pattern_analysis['hourly_distribution'][hour] += 1
                    hourly_counts[hour] += 1
                    daily_counts[day_key] += 1
                    
                    # Track recent activity (last 24 hours)
                    if (datetime.now() - update_time).total_seconds() < 86400:  # 24 hours
                        pattern_analysis['recent_activity'].append({
                            'id': change.get('id', 'Unknown'),
                            'title': change.get('titel', change.get('navn', 'Unknown')),
                            'update_time': change['opdateringsdato']
                        })
                        
                except ValueError:
                    pass  # Skip invalid timestamps
            
            # Identify peak hours (hours with above-average activity)
            if hourly_counts:
                avg_hourly = sum(hourly_counts.values()) / len(hourly_counts)
                pattern_analysis['change_velocity']['peak_hours'] = [
                    hour for hour, count in hourly_counts.items() 
                    if count > avg_hourly * 1.5
                ]
                
                pattern_analysis['change_velocity']['quiet_periods'] = [
                    hour for hour, count in hourly_counts.items() 
                    if count < avg_hourly * 0.5
                ]
        
        return pattern_analysis
```

### Advanced Real-Time Analytics

```python
class AdvancedRealTimeAnalyzer(RealTimeMonitor):
    
    def create_parliamentary_activity_dashboard(self, refresh_interval_minutes=30):
        """Create real-time dashboard of current parliamentary activity"""
        
        dashboard = {
            'last_updated': datetime.now().isoformat(),
            'refresh_interval_minutes': refresh_interval_minutes,
            'current_activity': {},
            'today_summary': {},
            'upcoming_events': {},
            'trending_topics': []
        }
        
        # Get current activity (last 4 hours)
        current_entities = ['Sag', 'Afstemning', 'Aktör', 'Dokument', 'Møde']
        
        for entity in current_entities:
            recent_changes = self.get_recent_changes(entity, hours_back=4)
            
            if recent_changes and recent_changes.get('value'):
                changes = recent_changes['value']
                
                dashboard['current_activity'][entity] = {
                    'change_count': len(changes),
                    'latest_update': changes[0]['opdateringsdato'] if changes else None,
                    'recent_items': [
                        {
                            'id': change.get('id', 'Unknown'),
                            'title': change.get('titel', change.get('navn', 'Unknown'))[:100],
                            'update_time': change.get('opdateringsdato', '')
                        }
                        for change in changes[:5]  # Most recent 5
                    ]
                }
            else:
                dashboard['current_activity'][entity] = {
                    'change_count': 0,
                    'latest_update': None,
                    'recent_items': []
                }
        
        # Get today's summary
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_cutoff = today_start.strftime('%Y-%m-%dT%H:%M:%S')
        
        total_today_changes = 0
        for entity in current_entities:
            today_changes = self.get_recent_changes(entity, hours_back=24)  # Today's changes
            
            if today_changes and today_changes.get('value'):
                entity_changes = len(today_changes['value'])
                total_today_changes += entity_changes
                
                dashboard['today_summary'][entity] = entity_changes
        
        dashboard['today_summary']['total_changes'] = total_today_changes
        
        # Get upcoming meetings (next 7 days)
        future_cutoff = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        week_ahead = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S')
        
        params = {
            '$filter': f'dato gt datetime\'{future_cutoff}\' and dato lt datetime\'{week_ahead}\'',
            '$orderby': 'dato asc',
            '$expand': 'Mødetype',
            '$top': 10
        }
        
        url = f"{self.base_url}Møde?" + urllib.parse.urlencode(params)
        
        try:
            response = requests.get(url)
            meetings_data = response.json()
            
            if meetings_data.get('value'):
                dashboard['upcoming_events']['meetings'] = [
                    {
                        'id': meeting.get('id', 'Unknown'),
                        'title': meeting.get('titel', 'Unknown'),
                        'date': meeting.get('dato', ''),
                        'type': meeting.get('Mødetype', {}).get('type', 'Unknown'),
                        'location': meeting.get('lokale', '')
                    }
                    for meeting in meetings_data['value']
                ]
        except:
            dashboard['upcoming_events']['meetings'] = []
        
        # Identify trending topics (cases with recent high activity)
        trending_topics = self.identify_trending_topics()
        dashboard['trending_topics'] = trending_topics
        
        return dashboard
    
    def identify_trending_topics(self, lookback_hours=24, min_activity_threshold=3):
        """Identify topics/cases with unusually high recent activity"""
        
        trending_analysis = {
            'analysis_period_hours': lookback_hours,
            'trending_cases': [],
            'trending_keywords': [],
            'activity_threshold': min_activity_threshold
        }
        
        # Get recent case activity
        recent_cases = self.get_recent_changes('Sag', lookback_hours)
        
        if recent_cases and recent_cases.get('value'):
            # Count activity by case
            case_activity = defaultdict(int)
            case_details = {}
            
            for case_change in recent_cases['value']:
                case_id = case_change.get('id')
                case_activity[case_id] += 1
                case_details[case_id] = {
                    'title': case_change.get('titel', 'Unknown'),
                    'status': case_change.get('Sagsstatus', {}).get('status', 'Unknown') if case_change.get('Sagsstatus') else 'Unknown',
                    'last_update': case_change.get('opdateringsdato', '')
                }
            
            # Find cases with high activity
            for case_id, activity_count in case_activity.items():
                if activity_count >= min_activity_threshold:
                    trending_case = case_details[case_id].copy()
                    trending_case['case_id'] = case_id
                    trending_case['activity_count'] = activity_count
                    trending_analysis['trending_cases'].append(trending_case)
            
            # Sort by activity level
            trending_analysis['trending_cases'].sort(key=lambda x: x['activity_count'], reverse=True)
        
        return trending_analysis
    
    def monitor_specific_cases(self, case_ids, alert_callback=None):
        """Monitor specific cases for any changes"""
        
        monitoring_results = {
            'monitored_cases': case_ids,
            'last_check': datetime.now().isoformat(),
            'changes_detected': [],
            'alerts_triggered': []
        }
        
        for case_id in case_ids:
            # Check for recent changes to this specific case
            params = {
                '$filter': f'id eq {case_id}',
                '$expand': 'Sagsstatus,Sagstype,Sagskategori'
            }
            
            url = f"{self.base_url}Sag?" + urllib.parse.urlencode(params)
            
            try:
                response = requests.get(url)
                case_data = response.json()
                
                if case_data.get('value'):
                    case = case_data['value'][0]
                    last_update = datetime.fromisoformat(
                        case['opdateringsdato'].replace('T', ' ').replace('Z', '')
                    )
                    
                    # Check if updated in last hour
                    if (datetime.now() - last_update).total_seconds() < 3600:  # 1 hour
                        change_info = {
                            'case_id': case_id,
                            'case_title': case.get('titel', 'Unknown'),
                            'current_status': case.get('Sagsstatus', {}).get('status', 'Unknown'),
                            'last_update': case['opdateringsdato'],
                            'change_type': 'status_update'
                        }
                        
                        monitoring_results['changes_detected'].append(change_info)
                        
                        # Trigger alert callback if provided
                        if alert_callback:
                            try:
                                alert_callback(change_info)
                                monitoring_results['alerts_triggered'].append({
                                    'case_id': case_id,
                                    'alert_sent': True,
                                    'timestamp': datetime.now().isoformat()
                                })
                            except Exception as e:
                                monitoring_results['alerts_triggered'].append({
                                    'case_id': case_id,
                                    'alert_sent': False,
                                    'error': str(e)
                                })
                        
            except Exception as e:
                print(f"Error monitoring case {case_id}: {e}")
        
        return monitoring_results
```

## Automated Monitoring Systems

### Continuous Monitoring Service

```python
class ContinuousMonitoringService:
    
    def __init__(self):
        self.analyzer = AdvancedRealTimeAnalyzer()
        self.monitoring_thread = None
        self.stop_monitoring = False
        self.alert_handlers = []
        
    def add_alert_handler(self, handler_function):
        """Add custom alert handler function"""
        self.alert_handlers.append(handler_function)
        
    def start_continuous_monitoring(self, entities_to_monitor, check_interval_minutes=15):
        """Start continuous monitoring in background thread"""
        
        self.stop_monitoring = False
        
        def monitoring_loop():
            while not self.stop_monitoring:
                try:
                    # Check each entity for changes
                    for entity_name in entities_to_monitor:
                        changes = self.analyzer.detect_incremental_changes(entity_name)
                        
                        if changes:
                            # Process detected changes
                            self.process_detected_changes(entity_name, changes)
                    
                    # Sleep until next check
                    time.sleep(check_interval_minutes * 60)
                    
                except Exception as e:
                    print(f"Error in monitoring loop: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        print(f"Started continuous monitoring for: {entities_to_monitor}")
        
    def stop_continuous_monitoring(self):
        """Stop continuous monitoring"""
        self.stop_monitoring = True
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        print("Stopped continuous monitoring")
        
    def process_detected_changes(self, entity_name, changes):
        """Process and alert on detected changes"""
        
        change_summary = {
            'entity': entity_name,
            'change_count': len(changes),
            'timestamp': datetime.now().isoformat(),
            'changes': []
        }
        
        for change in changes:
            change_info = {
                'id': change.get('id', 'Unknown'),
                'title': change.get('titel', change.get('navn', 'Unknown')),
                'update_time': change.get('opdateringsdato', ''),
                'change_significance': self.assess_change_significance(entity_name, change)
            }
            
            change_summary['changes'].append(change_info)
        
        # Send alerts through registered handlers
        for handler in self.alert_handlers:
            try:
                handler(change_summary)
            except Exception as e:
                print(f"Alert handler error: {e}")
    
    def assess_change_significance(self, entity_name, change):
        """Assess the significance of a detected change"""
        
        # Simple significance assessment based on entity type and content
        significance_indicators = {
            'Sag': {
                'high': ['vedtaget', 'forkastet', 'slutbehandling'],
                'medium': ['behandling', 'udvalg', 'betænkning'],
                'low': []
            },
            'Afstemning': {
                'high': ['vedtaget', 'afsluttet'],
                'medium': ['igangværende'],
                'low': []
            }
        }
        
        if entity_name in significance_indicators:
            title_lower = change.get('titel', '').lower()
            
            for level, keywords in significance_indicators[entity_name].items():
                if any(keyword in title_lower for keyword in keywords):
                    return level
        
        return 'medium'  # Default significance
```

### Alert and Notification System

```python
class AlertSystem:
    
    def __init__(self):
        self.alert_channels = []
        
    def add_email_alerts(self, email_config):
        """Add email alert capability"""
        def email_handler(change_summary):
            # Email implementation would go here
            print(f"EMAIL ALERT: {change_summary['change_count']} changes in {change_summary['entity']}")
            
        self.alert_channels.append(email_handler)
    
    def add_webhook_alerts(self, webhook_url):
        """Add webhook alert capability"""
        def webhook_handler(change_summary):
            try:
                import requests
                response = requests.post(webhook_url, json=change_summary, timeout=10)
                response.raise_for_status()
                print(f"Webhook sent successfully for {change_summary['entity']} changes")
            except Exception as e:
                print(f"Webhook failed: {e}")
                
        self.alert_channels.append(webhook_handler)
    
    def add_console_alerts(self):
        """Add console logging alerts"""
        def console_handler(change_summary):
            print(f"\n=== PARLIAMENTARY ACTIVITY ALERT ===")
            print(f"Entity: {change_summary['entity']}")
            print(f"Changes detected: {change_summary['change_count']}")
            print(f"Time: {change_summary['timestamp']}")
            
            for change in change_summary['changes'][:3]:  # Show top 3
                print(f"  - {change['title'][:80]}...")
                print(f"    Significance: {change['change_significance']}")
                print(f"    Updated: {change['update_time']}")
            
            if len(change_summary['changes']) > 3:
                print(f"  ... and {len(change_summary['changes']) - 3} more changes")
                
            print("=" * 50)
                
        self.alert_channels.append(console_handler)
    
    def trigger_alerts(self, change_summary):
        """Trigger all configured alert channels"""
        for alert_channel in self.alert_channels:
            try:
                alert_channel(change_summary)
            except Exception as e:
                print(f"Alert channel error: {e}")
```

## Real-World Implementation Examples

### Parliamentary News Monitor

```python
class ParliamentaryNewsMonitor:
    
    def __init__(self):
        self.monitoring_service = ContinuousMonitoringService()
        self.alert_system = AlertSystem()
        
    def setup_news_monitoring(self):
        """Setup monitoring for newsworthy parliamentary activity"""
        
        # Configure alerts
        self.alert_system.add_console_alerts()
        # self.alert_system.add_email_alerts(email_config)
        # self.alert_system.add_webhook_alerts("https://your-news-system.com/webhook")
        
        # Add alert handlers to monitoring service
        self.monitoring_service.add_alert_handler(
            lambda changes: self.filter_newsworthy_changes(changes)
        )
        
        # Start monitoring key entities
        entities_to_monitor = ['Sag', 'Afstemning', 'Møde']
        self.monitoring_service.start_continuous_monitoring(
            entities_to_monitor, 
            check_interval_minutes=10  # Check every 10 minutes
        )
        
    def filter_newsworthy_changes(self, change_summary):
        """Filter changes for newsworthiness and alert accordingly"""
        
        newsworthy_changes = []
        
        for change in change_summary['changes']:
            # Criteria for newsworthy items
            title_lower = change['title'].lower()
            significance = change['change_significance']
            
            is_newsworthy = (
                significance == 'high' or
                any(keyword in title_lower for keyword in ['lovforslag', 'beslutning', 'vedtaget', 'forkastet']) or
                'minister' in title_lower
            )
            
            if is_newsworthy:
                newsworthy_changes.append(change)
        
        if newsworthy_changes:
            news_alert = {
                'entity': change_summary['entity'],
                'change_count': len(newsworthy_changes),
                'timestamp': change_summary['timestamp'],
                'changes': newsworthy_changes,
                'alert_type': 'newsworthy_activity'
            }
            
            self.alert_system.trigger_alerts(news_alert)
```

### Research Project Monitor

```python
class ResearchProjectMonitor:
    
    def __init__(self, research_keywords, monitored_case_ids=None):
        self.research_keywords = research_keywords
        self.monitored_case_ids = monitored_case_ids or []
        self.analyzer = AdvancedRealTimeAnalyzer()
        
    def setup_research_monitoring(self):
        """Setup monitoring for specific research interests"""
        
        monitoring_config = {
            'keywords': self.research_keywords,
            'case_ids': self.monitored_case_ids,
            'last_check': datetime.now().isoformat(),
            'findings_log': []
        }
        
        return monitoring_config
    
    def check_for_research_relevant_changes(self):
        """Check for changes relevant to research project"""
        
        research_findings = {
            'check_time': datetime.now().isoformat(),
            'keyword_matches': [],
            'monitored_case_updates': [],
            'new_relevant_cases': []
        }
        
        # Check for keyword matches in recent cases
        recent_cases = self.analyzer.get_recent_changes('Sag', hours_back=24)
        
        if recent_cases and recent_cases.get('value'):
            for case in recent_cases['value']:
                case_title = case.get('titel', '').lower()
                
                matched_keywords = []
                for keyword in self.research_keywords:
                    if keyword.lower() in case_title:
                        matched_keywords.append(keyword)
                
                if matched_keywords:
                    research_findings['keyword_matches'].append({
                        'case_id': case.get('id'),
                        'case_title': case.get('titel', 'Unknown'),
                        'matched_keywords': matched_keywords,
                        'last_update': case.get('opdateringsdato', ''),
                        'status': case.get('Sagsstatus', {}).get('status', 'Unknown') if case.get('Sagsstatus') else 'Unknown'
                    })
        
        # Check monitored cases for updates
        if self.monitored_case_ids:
            case_monitoring = self.analyzer.monitor_specific_cases(self.monitored_case_ids)
            research_findings['monitored_case_updates'] = case_monitoring['changes_detected']
        
        return research_findings
```

## Performance Optimization

### Efficient Polling Strategies

```python
class OptimizedPollingStrategy:
    
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api/"
        
    def calculate_optimal_polling_intervals(self, entity_name, analysis_days=7):
        """Calculate optimal polling interval based on historical activity patterns"""
        
        analyzer = RealTimeMonitor()
        patterns = analyzer.analyze_change_patterns(entity_name, analysis_days)
        
        optimization_analysis = {
            'entity': entity_name,
            'recommended_intervals': {},
            'activity_based_scheduling': [],
            'efficiency_metrics': {}
        }
        
        if patterns['total_changes'] > 0:
            changes_per_hour = patterns['total_changes'] / (analysis_days * 24)
            
            # Calculate different polling strategies
            strategies = {
                'aggressive': max(5, int(60 / max(1, changes_per_hour * 2))),  # Poll when expecting changes
                'balanced': max(15, int(60 / max(1, changes_per_hour))),       # Poll at average rate
                'conservative': max(30, int(120 / max(1, changes_per_hour)))   # Poll less frequently
            }
            
            optimization_analysis['recommended_intervals'] = strategies
            
            # Activity-based scheduling
            peak_hours = patterns['change_velocity']['peak_hours']
            quiet_hours = patterns['change_velocity']['quiet_periods']
            
            optimization_analysis['activity_based_scheduling'] = [
                {
                    'time_period': 'peak_hours',
                    'hours': peak_hours,
                    'recommended_interval_minutes': strategies['aggressive']
                },
                {
                    'time_period': 'quiet_hours', 
                    'hours': quiet_hours,
                    'recommended_interval_minutes': strategies['conservative']
                },
                {
                    'time_period': 'normal_hours',
                    'hours': [h for h in range(24) if h not in peak_hours and h not in quiet_hours],
                    'recommended_interval_minutes': strategies['balanced']
                }
            ]
        
        return optimization_analysis
```

This comprehensive real-time monitoring framework leverages the Danish Parliament API's exceptional data freshness to build sophisticated applications for news monitoring, research tracking, and democratic engagement through timely parliamentary activity notifications.