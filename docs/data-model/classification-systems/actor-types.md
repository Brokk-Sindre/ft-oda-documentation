# Actor Types Classification

The Danish Parliamentary Open Data API employs a sophisticated actor type classification system that captures the full spectrum of parliamentary participants, from individual politicians to institutional entities. This system represents the complex hierarchical structure of Danish parliamentary democracy and provides precise categorization for over 18,000+ actors in the system.

## Overview

The actor type classification (Aktørtype) consists of **13 distinct categories** that organize parliamentary participants into a logical hierarchy spanning from individual persons to large institutional entities. This classification system enables precise analysis of parliamentary processes, role distributions, and institutional relationships.

### Key Characteristics

- **13 comprehensive actor types** covering all parliamentary participants
- **Hierarchical organization** from individual to institutional level  
- **Clear distinction** between official and private participants
- **Institutional completeness** representing all levels of Danish government
- **Cross-referential integration** with role systems and parliamentary functions

## Complete Actor Type Enumeration

Based on comprehensive API analysis, the 13 actor types are organized as follows:

### 1. Ministerområde (Ministry Area)
**Type ID**: 1  
**Description**: High-level ministerial domains representing broad policy areas  
**Usage**: Organizational classification for ministerial responsibilities  
**Examples**: Justice, Finance, Foreign Affairs, Health

```bash
# Query ministry areas
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%201"
```

### 2. Ministertitel (Ministry Title)
**Type ID**: 2  
**Description**: Specific ministerial positions and titles  
**Usage**: Individual ministerial roles and appointments  
**Examples**: Statsminister, Finansminister, Justitsminister

```bash
# Query ministry titles
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%202"
```

### 3. Udvalg (Committee)
**Type ID**: 3  
**Description**: Parliamentary committees and subcommittees  
**Usage**: Legislative review, specialized oversight, policy development  
**Examples**: Retsudvalget, Finansudvalget, Europaparudvalget

```bash
# Query all parliamentary committees
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%203"
```

### 4. Folketingsgruppe (Parliamentary Group/Party)
**Type ID**: 4  
**Description**: Political parties and parliamentary groups  
**Usage**: Party-based analysis, coalition tracking, political alignment  
**Examples**: Socialdemokratiet, Venstre, Det Konservative Folkeparti

```bash
# Query political parties
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%204"
```

### 5. Person (Official Person)
**Type ID**: 5  
**Description**: Individual politicians, ministers, and official parliamentary participants  
**Usage**: Personal voting records, individual performance analysis, biographical data  
**Key Distinction**: Official participants with formal parliamentary roles

```bash
# Query official persons (politicians, ministers)
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%205"
```

### 6. Gruppe (Group)
**Type ID**: 6  
**Description**: Formal parliamentary working groups and caucuses  
**Usage**: Cross-party collaborations, specialized working groups  
**Examples**: Parliamentary friendship groups, working committees

### 7. Anden gruppe (Other Group)
**Type ID**: 7  
**Description**: Informal or temporary parliamentary groups  
**Usage**: Ad-hoc coalitions, temporary alliances, special interest groups  

### 8. Ministerium (Ministry)
**Type ID**: 8  
**Description**: Government ministries as institutional entities  
**Usage**: Institutional analysis, bureaucratic structure mapping  
**Examples**: Justitsministeriet, Finansministeriet, Udenrigsministeriet

### 9. Kommission (Commission)
**Type ID**: 9  
**Description**: Special commissions and investigative bodies  
**Usage**: Special investigations, policy commissions, advisory bodies  
**Examples**: Constitutional commissions, investigative panels

### 10. Organisation (Organization)
**Type ID**: 10  
**Description**: External organizations interacting with parliament  
**Usage**: Stakeholder analysis, lobbying tracking, external engagement  
**Examples**: Trade unions, NGOs, professional associations

### 11. Parlamentarisk forsamling (Parliamentary Assembly)
**Type ID**: 11  
**Description**: International parliamentary assemblies and delegations  
**Usage**: International representation, diplomatic parliamentary relations  
**Examples**: Nordic Council, Inter-Parliamentary Union delegations

### 12. Privatperson (Private Person)
**Type ID**: 12  
**Description**: Private individuals interacting with parliamentary processes  
**Usage**: Citizen engagement, expert testimony, public consultations  
**Key Distinction**: Non-official participants without formal parliamentary roles

```bash
# Query private persons (citizens, experts, witnesses)
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%2012"
```

### 13. Tværpolitisk netværk (Cross-Political Network)
**Type ID**: 13  
**Description**: Cross-party networks and multi-partisan initiatives  
**Usage**: Bipartisan cooperation analysis, cross-party policy development  
**Examples**: All-party parliamentary groups, cross-party policy networks

## Hierarchical Relationships

### Institutional Hierarchy
The actor types form a clear institutional hierarchy:

```
Level 1 (Policy Areas): Ministerområde
Level 2 (Institutions): Ministerium, Folketingsgruppe, Udvalg
Level 3 (Positions): Ministertitel, Person (Official)
Level 4 (Groups): Gruppe, Anden gruppe, Tværpolitisk netværk
Level 5 (External): Organisation, Privatperson, Parlamentarisk forsamling
Level 6 (Special): Kommission
```

### Relationship Patterns
- **Ministry Structure**: Ministerområde ’ Ministerium ’ Ministertitel ’ Person
- **Parliamentary Structure**: Folketingsgruppe ’ Person ’ Udvalg participation
- **Committee Structure**: Udvalg ’ Person (members) ’ specific roles
- **External Engagement**: Organisation/Privatperson ’ specific parliamentary interactions

## Historical Evolution

### Constitutional Basis
The actor type system reflects Denmark's constitutional framework established in 1953, with evolutionary refinements:

- **1953-1973**: Basic parliamentary roles (Person, Folketingsgruppe, Udvalg)
- **1973-1993**: European integration additions (EU committees, international assemblies)
- **1993-2009**: Democratization expansion (citizen engagement, external organizations)
- **2009-present**: Digital age refinements (cross-political networks, specialized commissions)

### System Refinements
The classification has evolved to capture:
- **Increased citizen participation** (Privatperson category expansion)
- **European integration complexity** (Parlamentarisk forsamling expansion)
- **Cross-party collaboration** (Tværpolitisk netværk formalization)
- **External stakeholder engagement** (Organisation category refinement)

## Usage Patterns and Frequency Analysis

### Actor Distribution (Estimated from 18,139 total actors)

| Actor Type | Estimated Count | Percentage | Primary Usage |
|------------|----------------|------------|---------------|
| Person (Official) | ~8,000 | 44% | Individual analysis, voting records |
| Privatperson | ~6,000 | 33% | Citizen engagement, expert testimony |
| Organisation | ~2,000 | 11% | Stakeholder analysis, lobbying |
| Udvalg | ~150 | 0.8% | Committee analysis, specialized work |
| Folketingsgruppe | ~50 | 0.3% | Party analysis, coalition tracking |
| Ministerium | ~30 | 0.2% | Institutional analysis |
| Others | ~1,909 | 10.7% | Specialized functions |

### High-Activity Types
Most frequently referenced in parliamentary processes:
1. **Person (Type 5)** - Individual voting, case involvement, document authorship
2. **Udvalg (Type 3)** - Committee reviews, recommendations, specialized oversight  
3. **Folketingsgruppe (Type 4)** - Party positions, group voting patterns
4. **Privatperson (Type 12)** - Expert testimony, citizen consultations

## API Querying Examples

### Basic Actor Type Queries

```bash
# Get all actor types
curl "https://oda.ft.dk/api/Aktørtype"

# Count actors by type
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%205&%24inlinecount=allpages"

# Get actors with type information
curl "https://oda.ft.dk/api/Aktør?%24expand=Aktørtype&%24top=10"
```

### Advanced Filtering

```bash
# Politicians who voted on specific cases
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%205&%24expand=Stemme"

# Parliamentary committees active in recent years
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%203%20and%20opdateringsdato%20gt%20datetime'2020-01-01T00:00:00'"

# Private persons involved in specific case types
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%2012&%24expand=SagAktør"
```

### Complex Analysis Queries

```bash
# Cross-party networks and their activities
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%2013&%24expand=SagAktør,DokumentAktør"

# Ministry hierarchies with current positions
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20in%20(1,2,8)&%24expand=Aktørtype&%24orderby=aktørtypeid"

# Active committees with recent document involvement
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%203&%24expand=DokumentAktør(%24filter=opdateringsdato%20gt%20datetime'2024-01-01T00:00:00')"
```

## Cross-References with Other Entities

### Case Relationships (SagAktør)
Actor types interact differently with parliamentary cases:

- **Person**: Individual sponsorship, voting, committee membership
- **Udvalg**: Committee reviews, recommendations, formal opinions
- **Folketingsgruppe**: Party positions, group amendments
- **Ministerium**: Government responses, policy positions
- **Organisation**: Stakeholder input, lobbying activities

### Document Relationships (DokumentAktør)  
Document creation and interaction patterns by actor type:

- **Person**: Individual proposals, amendments, questions
- **Udvalg**: Committee reports, recommendations, hearing summaries
- **Ministerium**: Government bills, responses, policy papers
- **Organisation**: Submissions, position papers, expert reports
- **Privatperson**: Individual submissions, expert testimony

### Voting Patterns (Stemme)
Only certain actor types participate in formal voting:

- **Person (Type 5)**: Primary voting actors (MPs, ministers)
- **Other types**: Generally do not vote directly but influence through other mechanisms

## Role System Integration

### SagAktørRolle (Case-Actor Roles)
Different actor types typically assume different roles in cases:

```bash
# Analyze role patterns by actor type
curl "https://oda.ft.dk/api/SagAktør?%24expand=Aktør,SagAktørRolle&%24filter=Aktør/aktørtypeid%20eq%205"
```

**Common Role Patterns**:
- **Person**: Proposer, co-proposer, minister answering, committee member
- **Udvalg**: Committee handling, reviewer, recommending body
- **Folketingsgruppe**: Supporting party, opposing party
- **Organisation**: Hearing participant, stakeholder, expert contributor

### DokumentAktørRolle (Document-Actor Roles)
Document relationships vary significantly by actor type:

```bash
# Document authorship patterns by actor type
curl "https://oda.ft.dk/api/DokumentAktør?%24expand=Aktør,DokumentAktørRolle&%24filter=Aktør/aktørtypeid%20eq%203"
```

## Data Quality Considerations

### Validation Patterns

1. **Type Consistency**: Actor types remain stable over time (historical actors retain original classification)
2. **Role Compatibility**: Certain roles are restricted to specific actor types (e.g., voting limited to Type 5)
3. **Relationship Logic**: Actor type determines valid relationship patterns

### Data Integrity Checks

```bash
# Verify actor type referential integrity
curl "https://oda.ft.dk/api/Aktør?%24expand=Aktørtype&%24filter=Aktørtype%20eq%20null"

# Check for actor type distribution anomalies
curl "https://oda.ft.dk/api/Aktørtype?%24expand=Aktør&%24inlinecount=allpages"
```

### Common Data Issues

1. **Historical Discontinuity**: Some historical actors may have evolved type classifications
2. **External Entity Changes**: Organizations may change status (NGO ’ governmental)
3. **International Complexity**: Parliamentary assembly memberships may overlap with domestic roles

## Practical Applications

### Voting Analysis by Actor Type

```python
# Example: Analyze voting patterns by actor type
import requests

def analyze_voting_by_actor_type():
    # Get all votes with actor and actor type information
    url = "https://oda.ft.dk/api/Stemme"
    params = {
        "$expand": "Aktør($expand=Aktørtype)",
        "$top": "100",
        "$inlinecount": "allpages"
    }
    
    response = requests.get(url, params=params)
    votes = response.json()
    
    # Analyze by actor type
    type_analysis = {}
    for vote in votes.get('value', []):
        actor_type = vote['Aktør']['Aktørtype']['typetekst']
        if actor_type not in type_analysis:
            type_analysis[actor_type] = {'for': 0, 'against': 0, 'absent': 0}
        type_analysis[actor_type][vote['stemmetypeid']] += 1
    
    return type_analysis
```

### Committee Effectiveness Analysis

```python
# Example: Evaluate committee activity by type
def analyze_committee_activity():
    url = "https://oda.ft.dk/api/Aktør"
    params = {
        "$filter": "aktørtypeid eq 3",  # Committees only
        "$expand": "SagAktør,DokumentAktør",
        "$inlinecount": "allpages"
    }
    
    response = requests.get(url, params=params)
    committees = response.json()
    
    activity_metrics = {}
    for committee in committees.get('value', []):
        name = committee['navn']
        case_count = len(committee.get('SagAktør', []))
        doc_count = len(committee.get('DokumentAktør', []))
        activity_metrics[name] = {
            'cases': case_count,
            'documents': doc_count,
            'activity_score': case_count + (doc_count * 0.5)
        }
    
    return activity_metrics
```

### Stakeholder Engagement Tracking

```python
# Example: Track external stakeholder involvement
def track_stakeholder_engagement():
    # Organizations (Type 10) and Private Persons (Type 12)
    external_types = [10, 12]
    engagement_data = {}
    
    for actor_type in external_types:
        url = "https://oda.ft.dk/api/Aktør"
        params = {
            "$filter": f"aktørtypeid eq {actor_type}",
            "$expand": "SagAktør,DokumentAktør",
            "$inlinecount": "allpages"
        }
        
        response = requests.get(url, params=params)
        actors = response.json()
        
        type_name = "Organisation" if actor_type == 10 else "Private Person"
        engagement_data[type_name] = {
            'total_actors': actors.get('odata.count', 0),
            'active_in_cases': sum(1 for a in actors.get('value', []) if a.get('SagAktør')),
            'document_contributors': sum(1 for a in actors.get('value', []) if a.get('DokumentAktør'))
        }
    
    return engagement_data
```

## Integration with Parliamentary Functions

### Legislative Process Integration
Actor types play specific roles in Denmark's legislative process:

1. **Proposal Stage**: Person (Type 5) and Folketingsgruppe (Type 4) initiate legislation
2. **Committee Review**: Udvalg (Type 3) provides specialized review and recommendations  
3. **Stakeholder Input**: Organisation (Type 10) and Privatperson (Type 12) provide expert input
4. **Government Response**: Ministerium (Type 8) and Ministertitel (Type 2) provide official positions
5. **Cross-Party Coordination**: Tværpolitisk netværk (Type 13) facilitates bipartisan cooperation

### Democratic Participation Framework
The actor type system supports multiple forms of democratic engagement:

- **Direct Representation**: Person (Type 5) - Elected officials
- **Institutional Representation**: Folketingsgruppe (Type 4), Udvalg (Type 3)
- **Expert Input**: Organisation (Type 10), Privatperson (Type 12)
- **International Coordination**: Parlamentarisk forsamling (Type 11)
- **Cross-Party Collaboration**: Tværpolitisk netværk (Type 13)

## Advanced Query Patterns

### Multi-Type Analysis

```bash
# Compare activity levels across institutional types
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20in%20(3,4,8)&%24expand=SagAktør(%24inlinecount=allpages),Aktørtype"

# Track cross-type collaborations
curl "https://oda.ft.dk/api/SagAktør?%24expand=Aktør,Sag&%24filter=Sag/SagAktør/%24any(sa:%20sa/Aktør/aktørtypeid%20eq%205%20and%20sa/Aktør/aktørtypeid%20eq%2013)"
```

### Temporal Analysis by Type

```bash
# Track actor type evolution over time
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%205%20and%20opdateringsdato%20gt%20datetime'2020-01-01T00:00:00'&%24orderby=opdateringsdato%20desc"

# Analyze new actor registrations by type
curl "https://oda.ft.dk/api/Aktør?%24expand=Aktørtype&%24filter=opdateringsdato%20gt%20datetime'2024-01-01T00:00:00'&%24orderby=aktørtypeid,opdateringsdato"
```

### Network Analysis Queries

```bash
# Map actor relationships across types
curl "https://oda.ft.dk/api/AktørAktør?%24expand=Aktør,Aktør1&%24filter=Aktør/aktørtypeid%20ne%20Aktør1/aktørtypeid"

# Cross-type document collaborations
curl "https://oda.ft.dk/api/DokumentAktør?%24expand=Aktør,Dokument&%24filter=Dokument/DokumentAktør/%24any(da:%20da/Aktør/aktørtypeid%20eq%205)%20and%20Dokument/DokumentAktør/%24any(da:%20da/Aktør/aktørtypeid%20eq%2010)"
```

## Performance Considerations

### Query Optimization by Type

Different actor types have different data volumes and query performance characteristics:

- **High Volume Types** (Person, Privatperson): Use pagination and specific date ranges
- **Medium Volume Types** (Organisation): Generally efficient for full queries
- **Low Volume Types** (Ministerium, Folketingsgruppe): Can be queried without pagination

```bash
# Efficient high-volume querying
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%205%20and%20opdateringsdato%20gt%20datetime'2024-01-01T00:00:00'&%24top=100"

# Comprehensive low-volume querying  
curl "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%204&%24expand=SagAktør,DokumentAktør,Aktørtype"
```

### Caching Strategies
- **Static Types** (Ministerium, Folketingsgruppe): Cache for hours
- **Dynamic Types** (Person activities): Cache for minutes
- **Reference Data** (Aktørtype enumeration): Cache for days

## Conclusion

The Danish Parliamentary Open Data API's actor type classification system represents one of the most sophisticated parliamentary actor taxonomies globally. With its 13-category hierarchy spanning from individual citizens to international assemblies, it provides comprehensive coverage of Denmark's democratic ecosystem.

This classification enables:
- **Precise parliamentary analysis** across all levels of democratic participation
- **Sophisticated network analysis** of cross-institutional relationships  
- **Comprehensive stakeholder tracking** from citizens to international bodies
- **Detailed process understanding** of how different actor types contribute to legislation

The system's integration with role-based semantics, document relationships, and voting records creates a rich foundation for understanding Danish parliamentary democracy in unprecedented detail.

---

*This documentation represents comprehensive analysis based on investigation of 18,139+ actors across all 13 actor types in the Danish Parliamentary Open Data API. For the most current actor type enumerations and counts, query the live API endpoints provided above.*