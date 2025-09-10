# Miscellaneous Role Systems

Beyond the primary [Case-Actor](case-actor-roles.md) and [Document-Actor](document-actor-roles.md) role systems, the Danish Parliamentary OData API includes several specialized role systems that govern other types of relationships in the parliamentary process. These systems handle inter-actor relationships, meeting participation, case step tracking, and administrative functions.

## Overview

The Danish Parliamentary system employs multiple sophisticated role systems to capture the full complexity of parliamentary operations. While the primary systems handle direct case and document relationships, these miscellaneous systems provide the semantic framework for:

- **Inter-Actor Relationships** via Akt�rAkt�rRolle
- **Meeting Participation** via M�deAkt�r
- **Legislative Process Steps** via SagstrinAkt�rRolle  
- **Administrative Functions** and procedural roles
- **Historical and Ceremonial** positions
- **International and Inter-Parliamentary** relationships

## Inter-Actor Role System (Akt�rAkt�rRolle)

The Akt�rAkt�r junction table with Akt�rAkt�rRolle defines relationships between different actors in the parliamentary system. This enables tracking of hierarchical relationships, substitutions, and collaborative arrangements.

### Key Relationship Types

**Substitution and Representation:**
- Substitute members (suppleanter) for committees
- Acting positions during absences
- Delegation of authority relationships
- Temporary role assignments

**Hierarchical Relationships:**
- Committee chairs and deputy chairs
- Parliamentary group leadership
- Ministry hierarchies and subordinate relationships
- Speaker succession and deputy arrangements

**Collaborative Networks:**
- Cross-party working group memberships
- Inter-parliamentary friendship groups
- Committee cooperation arrangements
- Joint initiative partnerships

### API Usage Examples

```python
import requests
import json

# Find all relationships for a specific actor
def get_actor_relationships(actor_id):
    """Get all inter-actor relationships for a given actor"""
    params = {
        '$filter': f'(akt�rid eq {actor_id} or akt�r2id eq {actor_id})',
        '$expand': 'Akt�r,Akt�r2,Akt�rAkt�rRolle',
        '$top': 100
    }
    
    response = requests.get('https://oda.ft.dk/api/Akt�rAkt�r', params=params)
    return response.json()

# Example: Find committee substitute relationships
def find_substitute_relationships():
    """Find substitute (suppleant) relationships"""
    params = {
        '$expand': 'Akt�r,Akt�r2,Akt�rAkt�rRolle',
        '$filter': "substringof('suppleant', Akt�rAkt�rRolle/rolle) or " +
                   "substringof('stedfortr�der', Akt�rAkt�rRolle/rolle)",
        '$top': 50
    }
    
    response = requests.get('https://oda.ft.dk/api/Akt�rAkt�r', params=params)
    return response.json()
```

### cURL Examples

```bash
# Get all relationships for actor ID 123
curl "https://oda.ft.dk/api/Akt�rAkt�r?%24filter=akt�rid%20eq%20123%20or%20akt�r2id%20eq%20123&%24expand=Akt�r,Akt�r2,Akt�rAkt�rRolle"

# Find leadership relationships
curl "https://oda.ft.dk/api/Akt�rAkt�r?%24expand=Akt�rAkt�rRolle&%24filter=substringof('formand',Akt�rAkt�rRolle/rolle)"
```

## Meeting Participation System (M�deAkt�r)

The M�deAkt�r entity tracks actor participation in parliamentary meetings, capturing attendance, roles during meetings, and participation patterns.

### Meeting Role Categories

**Presiding Roles:**
- Meeting chairs and co-chairs
- Session moderators
- Voting supervisors
- Procedural officers

**Participant Roles:**
- Committee members present
- Guest speakers and experts  
- Ministry representatives
- Observer status participants

**Administrative Roles:**
- Meeting secretaries
- Technical support staff
- Protocol officers
- Documentation coordinators

### API Usage Examples

```python
# Find meeting participants for a specific meeting
def get_meeting_participants(meeting_id):
    """Get all participants for a specific meeting"""
    params = {
        '$filter': f'm�deid eq {meeting_id}',
        '$expand': 'Akt�r,M�de',
        '$orderby': 'Akt�r/navn'
    }
    
    response = requests.get('https://oda.ft.dk/api/M�deAkt�r', params=params)
    return response.json()

# Track actor meeting attendance patterns
def analyze_meeting_attendance(actor_id, start_date, end_date):
    """Analyze meeting attendance for an actor over time"""
    params = {
        '$filter': f'akt�rid eq {actor_id} and ' +
                   f'M�de/dato ge datetime\'{start_date}\' and ' +
                   f'M�de/dato le datetime\'{end_date}\'',
        '$expand': 'M�de',
        '$orderby': 'M�de/dato desc'
    }
    
    response = requests.get('https://oda.ft.dk/api/M�deAkt�r', params=params)
    return response.json()

# Find committee meeting chairs
def find_meeting_chairs(committee_id):
    """Find actors who chair meetings for a specific committee"""
    params = {
        '$filter': f'M�de/akt�rid eq {committee_id}',
        '$expand': 'Akt�r,M�de',
        '$top': 100
    }
    
    response = requests.get('https://oda.ft.dk/api/M�deAkt�r', params=params)
    return response.json()
```

## Case Step Role System (SagstrinAkt�rRolle)

The SagstrinAkt�rRolle system provides granular tracking of actor involvement at each step of the legislative process, enabling precise analysis of procedural participation.

### Legislative Process Roles

**Reading Stages:**
- First reading speakers
- Second reading participants  
- Third reading contributors
- Amendment proposers

**Committee Stages:**
- Rapporteurs (ordf�rere)
- Committee members present
- Expert witnesses
- Stakeholder representatives

**Voting Stages:**
- Vote collectors
- Absent excuse providers
- Voting observers
- Result announcers

### API Usage Examples

```python
# Track actor participation across case steps
def track_case_participation(case_id):
    """Track all actor participation across case steps"""
    params = {
        '$filter': f'Sagstrin/sagid eq {case_id}',
        '$expand': 'Akt�r,Sagstrin,SagstrinAkt�rRolle',
        '$orderby': 'Sagstrin/dato'
    }
    
    response = requests.get('https://oda.ft.dk/api/SagstrinAkt�r', params=params)
    return response.json()

# Analyze rapporteur (spokesperson) patterns
def analyze_rapporteur_patterns(committee_id):
    """Analyze which actors serve as rapporteurs for committee cases"""
    params = {
        '$filter': "substringof('ordf�rer', SagstrinAkt�rRolle/rolle)",
        '$expand': 'Akt�r,Sagstrin/Sag,SagstrinAkt�rRolle',
        '$top': 100
    }
    
    response = requests.get('https://oda.ft.dk/api/SagstrinAkt�r', params=params)
    return response.json()
```

## Administrative and Procedural Roles

### Parliamentary Administration

**Speaker's Office Roles:**
- Speaker (Formand)
- Deputy Speakers (N�stform�nd)
- Session chairs
- Protocol officers

**Committee Administration:**
- Committee chairs and deputy chairs
- Committee secretaries
- Administrative coordinators
- Technical advisors

**Parliamentary Services:**
- Library and research staff
- IT and technical support
- Security and building services
- Public relations officers

### API Queries for Administrative Roles

```bash
# Find all Speakers and Deputy Speakers
curl "https://oda.ft.dk/api/Akt�r?%24filter=substringof('formand',navn)%20or%20substringof('n�stformand',navn)"

# Get committee administrative structure
curl "https://oda.ft.dk/api/SagAkt�r?%24expand=Akt�r,SagAkt�rRolle&%24filter=substringof('formand',SagAkt�rRolle/rolle)"
```

## Historical and Ceremonial Roles

### Historical Positions

The API contains rich historical data spanning decades of Danish parliamentary history, including roles that have evolved or been discontinued:

**Legacy Roles:**
- Former committee structures
- Discontinued parliamentary positions
- Historical ministry arrangements
- Superseded procedural roles

**Ceremonial Functions:**
- State opening ceremony participants
- Royal visit protocols
- International reception committees  
- Anniversary and commemoration roles

### Evolution Tracking

```python
# Track role evolution over time
def analyze_role_evolution(role_name):
    """Analyze how a specific role has evolved over time"""
    params = {
        '$filter': f"substringof('{role_name}', SagAkt�rRolle/rolle)",
        '$expand': 'Sag,Akt�r,SagAkt�rRolle',
        '$orderby': 'Sag/opdateringsdato desc',
        '$top': 200
    }
    
    response = requests.get('https://oda.ft.dk/api/SagAkt�r', params=params)
    return response.json()

# Find historical vs current committee structures
def compare_committee_structures(old_period, new_period):
    """Compare committee structures between periods"""
    old_params = {
        '$filter': f'Sag/periodeid eq {old_period}',
        '$expand': 'Akt�r,SagAkt�rRolle',
        '$top': 100
    }
    
    new_params = {
        '$filter': f'Sag/periodeid eq {new_period}',
        '$expand': 'Akt�r,SagAkt�rRolle',
        '$top': 100
    }
    
    old_response = requests.get('https://oda.ft.dk/api/SagAkt�r', params=old_params)
    new_response = requests.get('https://oda.ft.dk/api/SagAkt�r', params=new_params)
    
    return {
        'historical': old_response.json(),
        'current': new_response.json()
    }
```

## Inter-Parliamentary and International Roles

### International Representation

**EU and European Roles:**
- European Affairs Committee members
- EU parliamentary delegation
- Council meeting representatives
- EU working group participants

**Nordic Cooperation:**
- Nordic Council representatives
- Inter-parliamentary Nordic committees
- Regional cooperation roles
- Joint Nordic initiatives

**Multilateral Organizations:**
- NATO Parliamentary Assembly
- Council of Europe participation
- UN committee representations
- International monitoring roles

### API Queries for International Roles

```python
# Find EU-related roles and participation
def find_eu_participation():
    """Find actors with EU-related roles"""
    params = {
        '$filter': "substringof('EU', SagAkt�rRolle/rolle) or " +
                   "substringof('Europa', SagAkt�rRolle/rolle)",
        '$expand': 'Akt�r,Sag,SagAkt�rRolle',
        '$top': 100
    }
    
    response = requests.get('https://oda.ft.dk/api/SagAkt�r', params=params)
    return response.json()

# Track international committee participation
def track_international_committees():
    """Track participation in international committees"""
    params = {
        '$filter': "substringof('international', Akt�r/navn) or " +
                   "substringof('nordisk', Akt�r/navn)",
        '$expand': 'SagAkt�r/SagAkt�rRolle',
        '$top': 50
    }
    
    response = requests.get('https://oda.ft.dk/api/Akt�r', params=params)
    return response.json()
```

## Temporary and Project-Specific Roles

### Ad-hoc Assignments

**Special Committees:**
- Temporary investigation committees
- Crisis response committees
- Special project teams
- Reform implementation groups

**Event-Specific Roles:**
- Conference organization committees
- Visit coordination teams
- Media response coordinators
- Special session organizers

### Tracking Temporary Roles

```python
# Find temporary and time-limited roles
def find_temporary_roles(start_date, end_date):
    """Find roles that were active only during specific periods"""
    params = {
        '$filter': f'Sag/opdateringsdato ge datetime\'{start_date}\' and ' +
                   f'Sag/opdateringsdato le datetime\'{end_date}\'',
        '$expand': 'Akt�r,Sag,SagAkt�rRolle',
        '$orderby': 'Sag/opdateringsdato',
        '$top': 100
    }
    
    response = requests.get('https://oda.ft.dk/api/SagAkt�r', params=params)
    return response.json()

# Identify project-specific committee formations
def analyze_special_committees():
    """Analyze formation of special committees"""
    params = {
        '$filter': "substringof('s�rlig', Akt�r/navn) or " +
                   "substringof('special', Akt�r/navn) or " +
                   "substringof('midlertidig', Akt�r/navn)",
        '$expand': 'SagAkt�r/SagAkt�rRolle',
        '$top': 100
    }
    
    response = requests.get('https://oda.ft.dk/api/Akt�r', params=params)
    return response.json()
```

## Integration Strategies

### Comprehensive Role Analysis

```python
class ComprehensiveRoleAnalyzer:
    """Comprehensive analysis tool for all role systems"""
    
    def __init__(self):
        self.base_url = 'https://oda.ft.dk/api/'
        
    def get_actor_complete_profile(self, actor_id):
        """Get complete role profile across all systems"""
        profile = {
            'case_roles': self._get_case_roles(actor_id),
            'document_roles': self._get_document_roles(actor_id),
            'inter_actor_relationships': self._get_actor_relationships(actor_id),
            'meeting_participation': self._get_meeting_roles(actor_id),
            'case_step_involvement': self._get_case_step_roles(actor_id)
        }
        return profile
        
    def _get_case_roles(self, actor_id):
        """Get SagAkt�r relationships"""
        params = {
            '$filter': f'akt�rid eq {actor_id}',
            '$expand': 'Sag,SagAkt�rRolle',
            '$top': 100
        }
        response = requests.get(f'{self.base_url}SagAkt�r', params=params)
        return response.json()
        
    def _get_document_roles(self, actor_id):
        """Get DokumentAkt�r relationships"""
        params = {
            '$filter': f'akt�rid eq {actor_id}',
            '$expand': 'Dokument,DokumentAkt�rRolle',
            '$top': 100
        }
        response = requests.get(f'{self.base_url}DokumentAkt�r', params=params)
        return response.json()
        
    def _get_actor_relationships(self, actor_id):
        """Get Akt�rAkt�r relationships"""
        params = {
            '$filter': f'akt�rid eq {actor_id} or akt�r2id eq {actor_id}',
            '$expand': 'Akt�r,Akt�r2,Akt�rAkt�rRolle',
            '$top': 100
        }
        response = requests.get(f'{self.base_url}Akt�rAkt�r', params=params)
        return response.json()
        
    def _get_meeting_roles(self, actor_id):
        """Get M�deAkt�r participation"""
        params = {
            '$filter': f'akt�rid eq {actor_id}',
            '$expand': 'M�de',
            '$top': 100
        }
        response = requests.get(f'{self.base_url}M�deAkt�r', params=params)
        return response.json()
        
    def _get_case_step_roles(self, actor_id):
        """Get SagstrinAkt�r involvement"""
        params = {
            '$filter': f'akt�rid eq {actor_id}',
            '$expand': 'Sagstrin,SagstrinAkt�rRolle',
            '$top': 100
        }
        response = requests.get(f'{self.base_url}SagstrinAkt�r', params=params)
        return response.json()

# Usage example
analyzer = ComprehensiveRoleAnalyzer()
complete_profile = analyzer.get_actor_complete_profile(123)
```

### Cross-System Role Correlation

```python
# Analyze role correlations across systems
def analyze_role_correlations(actor_id):
    """Analyze how roles correlate across different systems"""
    
    # Get primary roles from case system
    case_roles = requests.get('https://oda.ft.dk/api/SagAkt�r', {
        '$filter': f'akt�rid eq {actor_id}',
        '$expand': 'SagAkt�rRolle',
        '$top': 100
    }).json()
    
    # Get document handling roles
    doc_roles = requests.get('https://oda.ft.dk/api/DokumentAkt�r', {
        '$filter': f'akt�rid eq {actor_id}',
        '$expand': 'DokumentAkt�rRolle',
        '$top': 100
    }).json()
    
    # Get meeting participation
    meeting_roles = requests.get('https://oda.ft.dk/api/M�deAkt�r', {
        '$filter': f'akt�rid eq {actor_id}',
        '$top': 100
    }).json()
    
    # Analyze patterns
    correlation_analysis = {
        'case_role_frequency': analyze_frequency([r['SagAkt�rRolle']['rolle'] for r in case_roles['value']]),
        'document_role_frequency': analyze_frequency([r['DokumentAkt�rRolle']['rolle'] for r in doc_roles['value']]),
        'meeting_participation_count': len(meeting_roles['value']),
        'role_combinations': find_common_combinations(case_roles, doc_roles)
    }
    
    return correlation_analysis
```

## Best Practices

### Query Optimization

1. **Use Specific Filters:** Always filter by relevant IDs or date ranges
2. **Expand Strategically:** Only expand necessary navigation properties
3. **Batch Related Queries:** Group related API calls when possible
4. **Cache Role References:** Role lookup tables change infrequently

### Data Analysis Approaches

1. **Temporal Analysis:** Track role changes over parliamentary periods
2. **Network Analysis:** Map inter-actor relationships and influences
3. **Pattern Recognition:** Identify recurring role assignment patterns
4. **Comparative Studies:** Compare role distributions across parties/committees

### Error Handling

```python
# Robust error handling for role queries
def safe_role_query(endpoint, params):
    """Execute API query with comprehensive error handling"""
    try:
        response = requests.get(f'https://oda.ft.dk/api/{endpoint}', params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle empty results
        if 'value' not in data or not data['value']:
            return {'value': [], 'count': 0}
            
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## Related Resources

- [Case-Actor Role System](case-actor-roles.md) - Primary legislative roles
- [Document-Actor Role System](document-actor-roles.md) - Document handling roles  
- [Entity Relationships](../entity-relationships.md) - Complete relationship mapping
- [Parliamentary Process](../parliamentary-process/index.md) - Process context for roles

## Summary

The miscellaneous role systems in the Danish Parliamentary OData API provide comprehensive coverage of all non-primary actor relationships. These systems enable sophisticated analysis of parliamentary networks, administrative structures, and procedural participation. Understanding these role systems is essential for:

- **Complete Actor Profiling** across all parliamentary activities
- **Network Analysis** of inter-parliamentary relationships  
- **Process Tracking** at granular legislative steps
- **Historical Research** into evolving parliamentary structures
- **Administrative Analysis** of parliamentary operations

The rich semantic information captured by these role systems makes the API uniquely powerful for detailed parliamentary research and analysis.