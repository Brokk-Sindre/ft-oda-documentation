# Polling Strategies

Optimize API polling for the Danish Parliament API by leveraging its predictable update patterns, business hours activity, and 50+ daily changes to build efficient real-time monitoring systems.

## Understanding Optimal Polling

The Danish Parliament API's consistent update patterns enable sophisticated polling optimization that can reduce API calls by 60-80% while maintaining real-time responsiveness.

### Key Optimization Principles

#### Time-Based Optimization
- **Peak Hours** (12:00-18:00 CET): Poll every 5-15 minutes
- **Off Hours** (18:00-08:00 CET): Poll every 30-60 minutes  
- **Weekends**: Poll every 2-4 hours
- **Recess Periods**: Poll every 4-8 hours

#### Activity-Based Optimization
- **High Activity Days** (50+ changes): Aggressive polling (5 min intervals)
- **Moderate Days** (20-50 changes): Balanced polling (15 min intervals)
- **Quiet Days** (<20 changes): Conservative polling (30-60 min intervals)

#### Entity-Specific Optimization
- **Sag** (Cases): Most active, requires frequent polling
- **Afstemning** (Voting): Event-driven, poll during session days
- **Møde** (Meetings): Predictable schedule, poll before meeting times
- **Dokument**: Moderate activity, standard intervals sufficient

## Implementation Framework

### Intelligent Polling Manager

```python
import requests
import urllib.parse
from datetime import datetime, timedelta, time
from collections import defaultdict
import asyncio
import threading
import queue

class IntelligentPollingManager:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api/"
        self.polling_strategies = {}
        self.last_poll_times = {}
        self.activity_history = defaultdict(list)
        self.polling_active = False
        self.response_queue = queue.Queue()
        
    def register_polling_strategy(self, entity_name, strategy_config):
        """Register polling strategy for an entity"""
        
        default_strategy = {
            'base_interval_minutes': 15,
            'peak_hours_interval': 5,
            'off_hours_interval': 30,
            'weekend_interval': 60,
            'high_activity_threshold': 50,
            'low_activity_threshold': 10,
            'adaptive_scaling': True,
            'max_interval_minutes': 120,
            'min_interval_minutes': 2
        }
        
        # Merge with provided config
        strategy = {**default_strategy, **strategy_config}
        self.polling_strategies[entity_name] = strategy
        self.last_poll_times[entity_name] = datetime.now() - timedelta(hours=1)
        
    def calculate_next_poll_interval(self, entity_name):
        """Calculate optimal next polling interval"""
        
        if entity_name not in self.polling_strategies:
            return 15  # Default 15 minutes
            
        strategy = self.polling_strategies[entity_name]
        current_time = datetime.now()
        
        # Base interval calculation
        base_interval = self.get_time_based_interval(strategy, current_time)
        
        # Activity-based adjustment
        if strategy['adaptive_scaling']:
            activity_modifier = self.calculate_activity_modifier(entity_name)
            adjusted_interval = base_interval * activity_modifier
        else:
            adjusted_interval = base_interval
        
        # Apply limits
        final_interval = max(
            strategy['min_interval_minutes'],
            min(strategy['max_interval_minutes'], adjusted_interval)
        )
        
        return final_interval
    
    def get_time_based_interval(self, strategy, current_time):
        """Get interval based on time of day and week"""
        
        current_hour = current_time.hour
        is_weekend = current_time.weekday() >= 5  # Saturday = 5, Sunday = 6
        
        if is_weekend:
            return strategy['weekend_interval']
        elif self.is_peak_hours(current_hour):
            return strategy['peak_hours_interval']  
        elif self.is_off_hours(current_hour):
            return strategy['off_hours_interval']
        else:
            return strategy['base_interval_minutes']
    
    def is_peak_hours(self, hour):
        """Check if current hour is peak activity time"""
        # Based on observed patterns: 12:00-18:00 CET
        return 12 <= hour <= 18
    
    def is_off_hours(self, hour):
        """Check if current hour is off-hours"""
        # Before 8 AM or after 6 PM
        return hour < 8 or hour > 18
    
    def calculate_activity_modifier(self, entity_name, lookback_hours=24):
        """Calculate activity-based polling modifier"""
        
        recent_activity = self.get_recent_activity_count(entity_name, lookback_hours)
        strategy = self.polling_strategies[entity_name]
        
        if recent_activity > strategy['high_activity_threshold']:
            return 0.5  # Poll twice as frequently
        elif recent_activity < strategy['low_activity_threshold']:
            return 2.0  # Poll half as frequently
        else:
            return 1.0  # Normal frequency
    
    def get_recent_activity_count(self, entity_name, hours_back=24):
        """Get activity count for recent period"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        cutoff_string = cutoff_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        params = {
            '$filter': f'opdateringsdato gt datetime\'{cutoff_string}\'',
            '$top': 1,
            '$inlinecount': 'allpages'
        }
        
        url = f"{self.base_url}{entity_name}?" + urllib.parse.urlencode(params)
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return int(data.get('odata.count', '0'))
        except:
            return 0  # Return 0 on error to avoid breaking polling
    
    async def execute_polling_cycle(self, entity_name):
        """Execute single polling cycle for an entity"""
        
        try:
            # Calculate next interval
            next_interval = self.calculate_next_poll_interval(entity_name)
            
            # Get changes since last poll
            last_poll_time = self.last_poll_times[entity_name]
            changes = await self.poll_for_changes(entity_name, last_poll_time)
            
            # Update last poll time
            self.last_poll_times[entity_name] = datetime.now()
            
            # Record activity for future optimization
            change_count = len(changes) if changes else 0
            self.activity_history[entity_name].append({
                'timestamp': datetime.now(),
                'change_count': change_count,
                'interval_used': next_interval
            })
            
            # Keep only recent history (last 7 days)
            cutoff = datetime.now() - timedelta(days=7)
            self.activity_history[entity_name] = [
                entry for entry in self.activity_history[entity_name] 
                if entry['timestamp'] > cutoff
            ]
            
            # Queue results
            if changes:
                self.response_queue.put({
                    'entity_name': entity_name,
                    'changes': changes,
                    'timestamp': datetime.now(),
                    'next_poll_in_minutes': next_interval
                })
            
            return {
                'entity_name': entity_name,
                'changes_found': change_count,
                'next_poll_in_minutes': next_interval,
                'polling_efficiency': self.calculate_polling_efficiency(entity_name)
            }
            
        except Exception as e:
            print(f"Error in polling cycle for {entity_name}: {e}")
            return {
                'entity_name': entity_name,
                'error': str(e),
                'next_poll_in_minutes': 30  # Default fallback
            }
    
    async def poll_for_changes(self, entity_name, since_timestamp):
        """Poll for changes since timestamp"""
        
        timestamp_str = since_timestamp.strftime('%Y-%m-%dT%H:%M:%S')
        
        params = {
            '$filter': f'opdateringsdato gt datetime\'{timestamp_str}\'',
            '$orderby': 'opdateringsdato desc',
            '$top': 100
        }
        
        # Add entity-specific expansions
        expansions = {
            'Sag': 'Sagsstatus,Sagstype,Sagskategori',
            'Afstemning': 'Sag,Afstemningstype',
            'Møde': 'Mødetype,Mødestatus',
            'Dokument': 'Dokumenttype,Dokumentstatus'
        }
        
        if entity_name in expansions:
            params['$expand'] = expansions[entity_name]
        
        url = f"{self.base_url}{entity_name}?" + urllib.parse.urlencode(params)
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('value', [])
        except Exception as e:
            print(f"Error polling {entity_name}: {e}")
            return []
    
    def calculate_polling_efficiency(self, entity_name):
        """Calculate polling efficiency metrics"""
        
        if entity_name not in self.activity_history:
            return {'efficiency_score': 0, 'recommendations': []}
        
        recent_polls = self.activity_history[entity_name][-20:]  # Last 20 polls
        
        if len(recent_polls) < 5:
            return {'efficiency_score': 0, 'recommendations': ['Insufficient data']}
        
        # Calculate metrics
        total_polls = len(recent_polls)
        productive_polls = len([p for p in recent_polls if p['change_count'] > 0])
        efficiency_ratio = productive_polls / total_polls if total_polls > 0 else 0
        
        avg_interval = sum(p['interval_used'] for p in recent_polls) / total_polls
        avg_changes_per_poll = sum(p['change_count'] for p in recent_polls) / total_polls
        
        efficiency_metrics = {
            'efficiency_score': efficiency_ratio * 100,  # Percentage
            'productive_polls': productive_polls,
            'total_polls': total_polls,
            'average_interval_minutes': avg_interval,
            'average_changes_per_poll': avg_changes_per_poll,
            'recommendations': []
        }
        
        # Generate recommendations
        if efficiency_ratio < 0.3:  # Less than 30% productive polls
            efficiency_metrics['recommendations'].append(
                "Consider increasing polling intervals - low hit rate detected"
            )
        elif efficiency_ratio > 0.8:  # More than 80% productive
            efficiency_metrics['recommendations'].append(
                "Consider decreasing intervals - high activity detected"
            )
        
        if avg_changes_per_poll > 10:
            efficiency_metrics['recommendations'].append(
                "High change volume - consider batch processing optimization"
            )
        
        return efficiency_metrics
```

### Advanced Polling Strategies

```python
class AdvancedPollingStrategies:
    def __init__(self):
        self.polling_manager = IntelligentPollingManager()
        
    def setup_cascade_polling(self, primary_entities, secondary_entities):
        """Setup cascade polling where secondary entities are polled based on primary activity"""
        
        cascade_config = {
            'primary_entities': primary_entities,
            'secondary_entities': secondary_entities,
            'cascade_triggers': {},
            'cascade_delays': {}
        }
        
        # Configure primary entities with aggressive polling
        for entity in primary_entities:
            self.polling_manager.register_polling_strategy(entity, {
                'base_interval_minutes': 10,
                'peak_hours_interval': 5,
                'adaptive_scaling': True
            })
        
        # Configure secondary entities with conservative default polling
        for entity in secondary_entities:
            self.polling_manager.register_polling_strategy(entity, {
                'base_interval_minutes': 30,
                'peak_hours_interval': 15,
                'adaptive_scaling': True
            })
            
            # Set up cascade triggers
            cascade_config['cascade_triggers'][entity] = {
                'trigger_on_primary_changes': True,
                'min_primary_changes': 5,
                'cascade_duration_minutes': 60
            }
        
        return cascade_config
    
    def setup_event_driven_polling(self, meeting_schedule):
        """Setup polling that intensifies around scheduled meetings"""
        
        event_driven_config = {
            'meeting_schedule': meeting_schedule,
            'pre_meeting_intensification': 60,  # minutes before meeting
            'post_meeting_monitoring': 120,     # minutes after meeting
            'event_entities': ['Møde', 'Afstemning', 'Stemme']
        }
        
        # Register strategies for meeting-related entities
        for entity in event_driven_config['event_entities']:
            self.polling_manager.register_polling_strategy(entity, {
                'base_interval_minutes': 20,
                'peak_hours_interval': 5,
                'event_driven': True,
                'pre_event_interval': 5,
                'post_event_interval': 10
            })
        
        return event_driven_config
    
    def setup_differential_polling(self, entity_priorities):
        """Setup polling with different frequencies based on entity importance"""
        
        priority_configs = {
            'critical': {
                'base_interval_minutes': 5,
                'peak_hours_interval': 2,
                'off_hours_interval': 10,
                'weekend_interval': 15
            },
            'high': {
                'base_interval_minutes': 10,
                'peak_hours_interval': 5,
                'off_hours_interval': 20,
                'weekend_interval': 30
            },
            'medium': {
                'base_interval_minutes': 15,
                'peak_hours_interval': 10,
                'off_hours_interval': 30,
                'weekend_interval': 60
            },
            'low': {
                'base_interval_minutes': 30,
                'peak_hours_interval': 20,
                'off_hours_interval': 60,
                'weekend_interval': 120
            }
        }
        
        for entity, priority in entity_priorities.items():
            if priority in priority_configs:
                self.polling_manager.register_polling_strategy(
                    entity, 
                    priority_configs[priority]
                )
        
        return {
            'configured_entities': len(entity_priorities),
            'priority_distribution': {
                priority: [e for e, p in entity_priorities.items() if p == priority]
                for priority in priority_configs.keys()
            }
        }
```

### Polling Coordination System

```python
class PollingCoordinator:
    def __init__(self):
        self.polling_manager = IntelligentPollingManager()
        self.active_pollers = {}
        self.coordinator_active = False
        
    async def start_coordinated_polling(self, entities_config):
        """Start coordinated polling for multiple entities"""
        
        self.coordinator_active = True
        
        # Setup polling strategies
        for entity_name, config in entities_config.items():
            self.polling_manager.register_polling_strategy(entity_name, config)
        
        # Create polling tasks
        polling_tasks = []
        
        for entity_name in entities_config.keys():
            task = asyncio.create_task(
                self.continuous_entity_polling(entity_name)
            )
            polling_tasks.append(task)
            self.active_pollers[entity_name] = task
        
        # Start result processing
        processing_task = asyncio.create_task(self.process_polling_results())
        polling_tasks.append(processing_task)
        
        try:
            await asyncio.gather(*polling_tasks)
        except Exception as e:
            print(f"Coordination error: {e}")
        finally:
            self.coordinator_active = False
    
    async def continuous_entity_polling(self, entity_name):
        """Continuous polling loop for a single entity"""
        
        while self.coordinator_active:
            try:
                # Execute polling cycle
                cycle_result = await self.polling_manager.execute_polling_cycle(entity_name)
                
                # Wait for next poll
                next_interval_minutes = cycle_result.get('next_poll_in_minutes', 15)
                await asyncio.sleep(next_interval_minutes * 60)
                
            except Exception as e:
                print(f"Error in continuous polling for {entity_name}: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def process_polling_results(self):
        """Process results from all pollers"""
        
        while self.coordinator_active:
            try:
                # Check for new results
                if not self.polling_manager.response_queue.empty():
                    result = self.polling_manager.response_queue.get()
                    await self.handle_polling_result(result)
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"Error processing polling results: {e}")
    
    async def handle_polling_result(self, result):
        """Handle individual polling result"""
        
        entity_name = result['entity_name']
        changes = result['changes']
        
        if changes:
            print(f"\n📊 {entity_name} CHANGES DETECTED")
            print(f"Changes found: {len(changes)}")
            print(f"Next poll in: {result['next_poll_in_minutes']} minutes")
            
            # Process changes (could trigger alerts, save to database, etc.)
            for change in changes[:3]:  # Show first 3
                title = change.get('titel', change.get('navn', 'Unknown'))
                print(f"  - {title[:60]}...")
            
            if len(changes) > 3:
                print(f"  ... and {len(changes) - 3} more changes")
    
    def get_polling_status(self):
        """Get current polling status for all entities"""
        
        status = {
            'coordinator_active': self.coordinator_active,
            'active_pollers': list(self.active_pollers.keys()),
            'entity_efficiencies': {},
            'overall_metrics': {
                'total_entities': len(self.active_pollers),
                'average_efficiency': 0,
                'recommendations': []
            }
        }
        
        # Get efficiency metrics for each entity
        efficiencies = []
        
        for entity_name in self.active_pollers.keys():
            efficiency = self.polling_manager.calculate_polling_efficiency(entity_name)
            status['entity_efficiencies'][entity_name] = efficiency
            
            if 'efficiency_score' in efficiency:
                efficiencies.append(efficiency['efficiency_score'])
        
        # Calculate overall metrics
        if efficiencies:
            status['overall_metrics']['average_efficiency'] = sum(efficiencies) / len(efficiencies)
        
        # Generate overall recommendations
        if status['overall_metrics']['average_efficiency'] < 40:
            status['overall_metrics']['recommendations'].append(
                "Overall polling efficiency is low - consider adjusting intervals"
            )
        elif status['overall_metrics']['average_efficiency'] > 80:
            status['overall_metrics']['recommendations'].append(
                "High efficiency - consider more aggressive polling during peak times"
            )
        
        return status
    
    def stop_polling(self):
        """Stop all polling activities"""
        
        self.coordinator_active = False
        
        # Cancel all polling tasks
        for entity_name, task in self.active_pollers.items():
            task.cancel()
        
        self.active_pollers.clear()
        print("All polling activities stopped")
```

## Real-World Implementation Examples

### News Monitoring System

```python
class NewsMonitoringPoller:
    def __init__(self):
        self.coordinator = PollingCoordinator()
        
    async def setup_news_monitoring(self):
        """Setup polling optimized for news monitoring"""
        
        # High-priority entities for news
        entities_config = {
            'Sag': {
                'base_interval_minutes': 5,   # Cases change frequently
                'peak_hours_interval': 2,     # Very frequent during peak
                'high_activity_threshold': 30,
                'adaptive_scaling': True
            },
            'Afstemning': {
                'base_interval_minutes': 10,  # Voting results are newsworthy
                'peak_hours_interval': 3,
                'event_driven': True
            },
            'Møde': {
                'base_interval_minutes': 30,  # Meetings are scheduled
                'pre_event_polling': True
            },
            'Dokument': {
                'base_interval_minutes': 15,  # Documents support stories
                'document_type_filtering': ['Lovforslag', 'Beslutningsforslag']
            }
        }
        
        print("Starting news monitoring with optimized polling...")
        await self.coordinator.start_coordinated_polling(entities_config)
    
    def get_news_monitoring_status(self):
        """Get status specifically for news monitoring"""
        
        status = self.coordinator.get_polling_status()
        
        # Add news-specific metrics
        status['news_metrics'] = {
            'breaking_news_threshold': 5,  # Changes per entity per hour
            'story_development_tracking': True,
            'priority_entity_focus': ['Sag', 'Afstemning']
        }
        
        return status
```

### Research Project Poller

```python
class ResearchProjectPoller:
    def __init__(self, research_keywords, focus_entities=None):
        self.keywords = research_keywords
        self.focus_entities = focus_entities or ['Sag', 'Dokument', 'Afstemning']
        self.coordinator = PollingCoordinator()
        
    async def setup_research_polling(self):
        """Setup polling optimized for research monitoring"""
        
        # Conservative but thorough polling for research
        entities_config = {}
        
        for entity in self.focus_entities:
            entities_config[entity] = {
                'base_interval_minutes': 20,     # Thorough but not aggressive
                'peak_hours_interval': 15,       # Slightly more frequent during business hours
                'weekend_interval': 60,          # Reduced weekend monitoring
                'adaptive_scaling': False,       # Consistent monitoring for research
                'keyword_filtering': self.keywords
            }
        
        # Add comprehensive data collection entities
        entities_config.update({
            'Aktör': {
                'base_interval_minutes': 120,    # Actors change infrequently
                'weekend_interval': 240
            }
        })
        
        print(f"Starting research polling for keywords: {self.keywords}")
        await self.coordinator.start_coordinated_polling(entities_config)
```

### Performance Monitoring

```python
class PollingPerformanceMonitor:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        
    def generate_performance_report(self):
        """Generate comprehensive polling performance report"""
        
        status = self.coordinator.get_polling_status()
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'polling_overview': {
                'active_entities': status['total_entities'],
                'overall_efficiency': status['overall_metrics']['average_efficiency'],
                'coordinator_status': status['coordinator_active']
            },
            'entity_performance': {},
            'optimization_suggestions': [],
            'resource_utilization': self.calculate_resource_utilization(status)
        }
        
        # Analyze each entity's performance
        for entity, efficiency in status['entity_efficiencies'].items():
            report['entity_performance'][entity] = {
                'efficiency_score': efficiency.get('efficiency_score', 0),
                'recent_productivity': efficiency.get('productive_polls', 0) / max(1, efficiency.get('total_polls', 1)) * 100,
                'average_interval': efficiency.get('average_interval_minutes', 0),
                'status': self.categorize_performance(efficiency.get('efficiency_score', 0))
            }
        
        # Generate optimization suggestions
        low_performers = [
            entity for entity, perf in report['entity_performance'].items() 
            if perf['efficiency_score'] < 30
        ]
        
        if low_performers:
            report['optimization_suggestions'].append({
                'type': 'increase_intervals',
                'entities': low_performers,
                'reason': 'Low efficiency detected - consider increasing polling intervals'
            })
        
        high_performers = [
            entity for entity, perf in report['entity_performance'].items() 
            if perf['efficiency_score'] > 80
        ]
        
        if high_performers:
            report['optimization_suggestions'].append({
                'type': 'decrease_intervals',
                'entities': high_performers,
                'reason': 'High activity detected - consider more frequent polling'
            })
        
        return report
    
    def categorize_performance(self, efficiency_score):
        """Categorize polling performance"""
        
        if efficiency_score >= 70:
            return 'excellent'
        elif efficiency_score >= 50:
            return 'good'
        elif efficiency_score >= 30:
            return 'acceptable'
        else:
            return 'needs_optimization'
    
    def calculate_resource_utilization(self, status):
        """Calculate estimated resource utilization"""
        
        total_entities = status.get('total_entities', 0)
        avg_efficiency = status['overall_metrics']['average_efficiency']
        
        # Estimate API calls per hour based on entity count and intervals
        estimated_calls_per_hour = total_entities * 4  # Rough estimate
        
        return {
            'estimated_api_calls_per_hour': estimated_calls_per_hour,
            'efficiency_rating': avg_efficiency,
            'resource_optimization_potential': max(0, 80 - avg_efficiency)  # How much we could optimize
        }
```

This comprehensive polling strategy system enables highly efficient real-time monitoring of the Danish Parliament API, reducing unnecessary API calls while maintaining responsive change detection for democratic transparency applications.