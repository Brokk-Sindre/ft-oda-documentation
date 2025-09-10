# Network Analysis with Danish Parliamentary Data

## Overview

The Danish Parliamentary Open Data API provides an exceptional foundation for network analysis with its rich relationship data spanning 18,139+ political actors across 30+ years of parliamentary activity. This guide demonstrates how to construct and analyze various network types using the parliamentary data to uncover patterns of collaboration, influence, and political dynamics.

## Network Analysis Opportunities

The OData API offers several network analysis opportunities through its comprehensive junction tables and relationship entities:

### Available Network Types

1. **Actor-to-Actor Networks** - Direct relationships via `AktørAktør` entity
2. **Co-sponsorship Networks** - Shared case participation via `SagAktør`
3. **Voting Alignment Networks** - Shared voting patterns via `Afstemning` and `Stemme`
4. **Committee Collaboration Networks** - Shared committee work via `MødeAktør`
5. **Document Authorship Networks** - Co-authorship via `DokumentAktør`
6. **Case Participation Networks** - Multi-actor case involvement
7. **Temporal Evolution Networks** - Network changes across parliamentary periods

### Key Junction Tables for Network Analysis

| Junction Table | Purpose | Network Type |
|---------------|---------|--------------|
| `SagAktør` | Case-Actor relationships | Co-sponsorship, case participation |
| `DokumentAktør` | Document-Actor relationships | Authorship, communication |
| `MødeAktør` | Meeting-Actor relationships | Committee collaboration |
| `SagstrinAktør` | Case Step-Actor relationships | Legislative process participation |
| `AktørAktør` | Direct Actor-Actor relationships | Direct connections |
| `Afstemning/Stemme` | Voting records | Voting alignment networks |

## Setting Up the Environment

### Required Libraries

```python
# Install required packages
pip install networkx pandas requests matplotlib seaborn
pip install python-igraph plotly community-detection
```

### Import Libraries

```python
import networkx as nx
import pandas as pd
import requests
from urllib.parse import quote
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from community import community_louvain
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
```

## Data Fetching Infrastructure

### API Client Class

```python
class ParliamentaryNetworkAPI:
    """Client for fetching Danish Parliamentary data for network analysis."""
    
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api"
        self.session = requests.Session()
        
    def fetch_data(self, entity, params=None, expand=None):
        """Fetch data from OData API with proper URL encoding."""
        url = f"{self.base_url}/{entity}"
        
        # Build query parameters with proper encoding
        query_params = []
        if params:
            for key, value in params.items():
                if key.startswith('$'):
                    # URL encode dollar signs for OData parameters
                    encoded_key = key.replace('$', '%24')
                    query_params.append(f"{encoded_key}={quote(str(value))}")
                else:
                    query_params.append(f"{key}={quote(str(value))}")
        
        if expand:
            query_params.append(f"%24expand={quote(expand)}")
            
        if query_params:
            url += "?" + "&".join(query_params)
            
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def fetch_all_pages(self, entity, params=None, expand=None, max_records=None):
        """Fetch all pages of data using pagination."""
        all_data = []
        skip = 0
        top = 1000  # Max batch size for performance
        
        while True:
            current_params = dict(params) if params else {}
            current_params['$top'] = top
            current_params['$skip'] = skip
            current_params['$inlinecount'] = 'allpages'
            
            data = self.fetch_data(entity, current_params, expand)
            
            if not data or not data.get('value'):
                break
                
            batch = data['value']
            all_data.extend(batch)
            
            print(f"Fetched {len(all_data)} records from {entity}")
            
            # Check if we've reached the end or hit max_records limit
            if len(batch) < top or (max_records and len(all_data) >= max_records):
                break
                
            skip += top
            
        return all_data[:max_records] if max_records else all_data

# Initialize API client
api = ParliamentaryNetworkAPI()
```

## 1. Actor-to-Actor Relationship Networks

### Direct Actor Relationships

```python
def build_actor_actor_network():
    """Build network of direct actor-to-actor relationships."""
    
    # Fetch actor-actor relationships with role information
    print("Fetching actor-actor relationships...")
    relationships = api.fetch_all_pages(
        'AktørAktør',
        expand='Aktør1,Aktør2,AktørAktørRolle',
        max_records=10000
    )
    
    # Create directed graph
    G = nx.DiGraph()
    
    for rel in relationships:
        if rel.get('Aktør1') and rel.get('Aktør2'):
            actor1 = rel['Aktør1']
            actor2 = rel['Aktør2']
            role = rel.get('AktørAktørRolle', {}).get('rolle', 'Unknown')
            
            # Add nodes with attributes
            G.add_node(actor1['id'], 
                      name=actor1.get('navn', ''),
                      type=actor1.get('typeid', 0),
                      party=actor1.get('gruppenavnkort', ''))
            
            G.add_node(actor2['id'],
                      name=actor2.get('navn', ''),
                      type=actor2.get('typeid', 0),
                      party=actor2.get('gruppenavnkort', ''))
            
            # Add edge with relationship type
            G.add_edge(actor1['id'], actor2['id'],
                      relationship_type=role,
                      weight=1)
    
    print(f"Built actor-actor network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G

# Build the network
actor_network = build_actor_actor_network()
```

### Network Analysis Metrics

```python
def analyze_actor_network(G):
    """Analyze basic network properties."""
    
    metrics = {}
    
    # Basic network properties
    metrics['nodes'] = G.number_of_nodes()
    metrics['edges'] = G.number_of_edges()
    metrics['density'] = nx.density(G)
    metrics['is_connected'] = nx.is_strongly_connected(G)
    
    # Convert to undirected for some metrics
    G_undirected = G.to_undirected()
    
    # Centrality measures
    print("Calculating centrality measures...")
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G_undirected, k=1000)  # Sample for performance
    closeness_centrality = nx.closeness_centrality(G_undirected)
    eigenvector_centrality = nx.eigenvector_centrality(G_undirected, max_iter=1000)
    
    # Find most central actors
    top_degree = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    top_betweenness = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    top_closeness = sorted(closeness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("\nTop 10 actors by degree centrality:")
    for actor_id, centrality in top_degree:
        actor_name = G.nodes[actor_id].get('name', f'Actor {actor_id}')
        print(f"  {actor_name}: {centrality:.3f}")
    
    print("\nTop 10 actors by betweenness centrality:")
    for actor_id, centrality in top_betweenness:
        actor_name = G.nodes[actor_id].get('name', f'Actor {actor_id}')
        print(f"  {actor_name}: {centrality:.3f}")
    
    return {
        'metrics': metrics,
        'centrality': {
            'degree': degree_centrality,
            'betweenness': betweenness_centrality,
            'closeness': closeness_centrality,
            'eigenvector': eigenvector_centrality
        }
    }

# Analyze the network
analysis = analyze_actor_network(actor_network)
```

## 2. Co-sponsorship Networks

### Building Co-sponsorship Networks

```python
def build_cosponsorship_network(min_shared_cases=2):
    """Build network based on shared case participation (co-sponsorship)."""
    
    print("Fetching case-actor relationships...")
    
    # Fetch case-actor relationships with roles
    case_actors = api.fetch_all_pages(
        'SagAktør',
        expand='Sag,Aktør,SagAktørRolle',
        max_records=50000  # Large dataset for comprehensive analysis
    )
    
    # Group actors by case
    cases_to_actors = defaultdict(list)
    actor_info = {}
    
    for ca in case_actors:
        if ca.get('Sag') and ca.get('Aktør'):
            case_id = ca['Sag']['id']
            actor = ca['Aktør']
            role = ca.get('SagAktørRolle', {}).get('rolle', 'Unknown')
            
            cases_to_actors[case_id].append({
                'id': actor['id'],
                'name': actor.get('navn', ''),
                'party': actor.get('gruppenavnkort', ''),
                'role': role
            })
            
            # Store actor info
            actor_info[actor['id']] = {
                'name': actor.get('navn', ''),
                'party': actor.get('gruppenavnkort', ''),
                'type': actor.get('typeid', 0)
            }
    
    # Build co-sponsorship network
    G = nx.Graph()  # Undirected for co-sponsorship
    
    # Count shared case participation
    actor_pairs = defaultdict(int)
    
    for case_id, actors in cases_to_actors.items():
        # Create edges between all pairs of actors in the same case
        for i, actor1 in enumerate(actors):
            for actor2 in actors[i+1:]:
                pair = tuple(sorted([actor1['id'], actor2['id']]))
                actor_pairs[pair] += 1
    
    # Add nodes and edges to graph
    for (actor1_id, actor2_id), shared_cases in actor_pairs.items():
        if shared_cases >= min_shared_cases:
            # Add nodes
            if actor1_id in actor_info:
                G.add_node(actor1_id, **actor_info[actor1_id])
            if actor2_id in actor_info:
                G.add_node(actor2_id, **actor_info[actor2_id])
            
            # Add edge with weight = number of shared cases
            G.add_edge(actor1_id, actor2_id, 
                      weight=shared_cases,
                      shared_cases=shared_cases)
    
    print(f"Built co-sponsorship network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print(f"Minimum shared cases: {min_shared_cases}")
    
    return G

# Build co-sponsorship network
cosponsorship_network = build_cosponsorship_network(min_shared_cases=3)
```

### Analyzing Co-sponsorship Patterns

```python
def analyze_cosponsorship_patterns(G):
    """Analyze co-sponsorship collaboration patterns."""
    
    # Party-based analysis
    party_collaboration = defaultdict(lambda: defaultdict(int))
    
    for edge in G.edges(data=True):
        actor1, actor2, data = edge
        party1 = G.nodes[actor1].get('party', 'Unknown')
        party2 = G.nodes[actor2].get('party', 'Unknown')
        weight = data['weight']
        
        if party1 and party2:
            # Count cross-party vs within-party collaboration
            if party1 == party2:
                party_collaboration[party1]['within_party'] += weight
            else:
                party_collaboration[party1]['cross_party'] += weight
                party_collaboration[party2]['cross_party'] += weight
    
    # Calculate collaboration ratios
    print("Party Collaboration Analysis:")
    print("-" * 50)
    for party, collab in party_collaboration.items():
        within = collab.get('within_party', 0)
        cross = collab.get('cross_party', 0)
        total = within + cross
        
        if total > 0:
            within_ratio = within / total
            cross_ratio = cross / total
            print(f"{party:15} | Within: {within_ratio:.2%} | Cross: {cross_ratio:.2%} | Total: {total}")
    
    # Find strongest collaborations
    strongest_edges = sorted(G.edges(data=True), 
                           key=lambda x: x[2]['weight'], 
                           reverse=True)[:10]
    
    print("\nStrongest Collaborations:")
    print("-" * 50)
    for actor1, actor2, data in strongest_edges:
        name1 = G.nodes[actor1].get('name', f'Actor {actor1}')
        name2 = G.nodes[actor2].get('name', f'Actor {actor2}')
        party1 = G.nodes[actor1].get('party', '')
        party2 = G.nodes[actor2].get('party', '')
        weight = data['weight']
        
        print(f"{name1} ({party1}) ” {name2} ({party2}): {weight} shared cases")
    
    return party_collaboration

# Analyze co-sponsorship patterns
cosponsorship_analysis = analyze_cosponsorship_patterns(cosponsorship_network)
```

## 3. Voting Alignment Networks

### Building Voting Alignment Networks

```python
def build_voting_alignment_network(min_shared_votes=10):
    """Build network based on voting alignment patterns."""
    
    print("Fetching voting records...")
    
    # Fetch voting records with actor information
    votes = api.fetch_all_pages(
        'Stemme',
        expand='Aktør,Afstemning',
        params={'$filter': 'typeid ne null'},  # Filter out null vote types
        max_records=100000  # Large sample for statistical significance
    )
    
    # Group votes by voting session
    voting_sessions = defaultdict(list)
    actor_info = {}
    
    for vote in votes:
        if vote.get('Aktør') and vote.get('Afstemning'):
            afstemning_id = vote['Afstemning']['id']
            actor = vote['Aktør']
            vote_type = vote.get('typeid', 0)
            
            voting_sessions[afstemning_id].append({
                'actor_id': actor['id'],
                'vote_type': vote_type,
                'name': actor.get('navn', ''),
                'party': actor.get('gruppenavnkort', '')
            })
            
            # Store actor info
            actor_info[actor['id']] = {
                'name': actor.get('navn', ''),
                'party': actor.get('gruppenavnkort', ''),
                'type': actor.get('typeid', 0)
            }
    
    # Calculate voting alignment between actors
    print("Calculating voting alignment...")
    
    actor_vote_records = defaultdict(dict)
    
    # Build vote history for each actor
    for session_id, session_votes in voting_sessions.items():
        for vote in session_votes:
            actor_id = vote['actor_id']
            vote_type = vote['vote_type']
            actor_vote_records[actor_id][session_id] = vote_type
    
    # Calculate pairwise alignment
    G = nx.Graph()
    alignment_pairs = {}
    
    actor_ids = list(actor_vote_records.keys())
    
    for i, actor1_id in enumerate(actor_ids):
        if i % 100 == 0:
            print(f"Processing actor {i+1}/{len(actor_ids)}")
            
        for actor2_id in actor_ids[i+1:]:
            # Find shared voting sessions
            sessions1 = set(actor_vote_records[actor1_id].keys())
            sessions2 = set(actor_vote_records[actor2_id].keys())
            shared_sessions = sessions1 & sessions2
            
            if len(shared_sessions) >= min_shared_votes:
                # Calculate alignment percentage
                agreements = 0
                for session in shared_sessions:
                    if (actor_vote_records[actor1_id][session] == 
                        actor_vote_records[actor2_id][session]):
                        agreements += 1
                
                alignment_score = agreements / len(shared_sessions)
                
                # Add to graph if high alignment
                if alignment_score > 0.7:  # 70% alignment threshold
                    pair = (actor1_id, actor2_id)
                    alignment_pairs[pair] = {
                        'alignment': alignment_score,
                        'shared_votes': len(shared_sessions),
                        'agreements': agreements
                    }
    
    # Build network graph
    for (actor1_id, actor2_id), data in alignment_pairs.items():
        if actor1_id in actor_info and actor2_id in actor_info:
            G.add_node(actor1_id, **actor_info[actor1_id])
            G.add_node(actor2_id, **actor_info[actor2_id])
            
            G.add_edge(actor1_id, actor2_id,
                      weight=data['alignment'],
                      alignment=data['alignment'],
                      shared_votes=data['shared_votes'],
                      agreements=data['agreements'])
    
    print(f"Built voting alignment network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G

# Build voting alignment network
voting_network = build_voting_alignment_network(min_shared_votes=20)
```

### Voting Bloc Analysis

```python
def analyze_voting_blocs(G, resolution=1.0):
    """Identify voting blocs using community detection."""
    
    # Community detection using Louvain algorithm
    print("Detecting voting communities...")
    communities = community_louvain.best_partition(G, resolution=resolution)
    
    # Analyze communities
    community_stats = defaultdict(lambda: {
        'members': [],
        'parties': defaultdict(int),
        'avg_alignment': 0.0,
        'internal_edges': 0
    })
    
    # Group by communities
    for node, community_id in communities.items():
        actor_info = G.nodes[node]
        community_stats[community_id]['members'].append({
            'id': node,
            'name': actor_info.get('name', ''),
            'party': actor_info.get('party', '')
        })
        
        party = actor_info.get('party', 'Unknown')
        community_stats[community_id]['parties'][party] += 1
    
    # Calculate internal community statistics
    for edge in G.edges(data=True):
        actor1, actor2, data = edge
        comm1 = communities[actor1]
        comm2 = communities[actor2]
        
        if comm1 == comm2:  # Same community
            community_stats[comm1]['internal_edges'] += 1
            community_stats[comm1]['avg_alignment'] += data.get('alignment', 0)
    
    # Finalize average alignment scores
    for comm_id, stats in community_stats.items():
        if stats['internal_edges'] > 0:
            stats['avg_alignment'] /= stats['internal_edges']
    
    # Print community analysis
    print(f"\nDetected {len(community_stats)} voting communities:")
    print("=" * 80)
    
    for comm_id, stats in sorted(community_stats.items(), 
                                key=lambda x: len(x[1]['members']), 
                                reverse=True)[:10]:  # Top 10 largest
        
        print(f"\nCommunity {comm_id} ({len(stats['members'])} members):")
        print(f"  Average internal alignment: {stats['avg_alignment']:.1%}")
        print(f"  Internal edges: {stats['internal_edges']}")
        print("  Party composition:")
        
        for party, count in sorted(stats['parties'].items(), 
                                 key=lambda x: x[1], 
                                 reverse=True)[:5]:  # Top 5 parties
            percentage = count / len(stats['members']) * 100
            print(f"    {party}: {count} members ({percentage:.1f}%)")
        
        print("  Sample members:")
        for member in stats['members'][:5]:  # Show first 5 members
            print(f"    {member['name']} ({member['party']})")
    
    return communities, community_stats

# Analyze voting blocs
communities, community_stats = analyze_voting_blocs(voting_network)
```

## 4. Committee Network Analysis

### Building Committee Collaboration Networks

```python
def build_committee_network():
    """Build network based on committee meeting participation."""
    
    print("Fetching meeting-actor relationships...")
    
    # Fetch meeting participation data
    meeting_actors = api.fetch_all_pages(
        'MødeAktør',
        expand='Møde,Aktør',
        max_records=50000
    )
    
    # Group actors by meetings
    meetings_to_actors = defaultdict(list)
    actor_info = {}
    meeting_info = {}
    
    for ma in meeting_actors:
        if ma.get('Møde') and ma.get('Aktør'):
            meeting_id = ma['Møde']['id']
            actor = ma['Aktør']
            meeting = ma['Møde']
            
            meetings_to_actors[meeting_id].append({
                'id': actor['id'],
                'name': actor.get('navn', ''),
                'party': actor.get('gruppenavnkort', '')
            })
            
            # Store info
            actor_info[actor['id']] = {
                'name': actor.get('navn', ''),
                'party': actor.get('grupgenavnkort', ''),
                'type': actor.get('typeid', 0)
            }
            
            meeting_info[meeting_id] = {
                'title': meeting.get('titel', ''),
                'date': meeting.get('dato', ''),
                'type': meeting.get('typeid', 0)
            }
    
    # Build committee collaboration network
    G = nx.Graph()
    
    # Count shared meeting participation
    actor_pairs = defaultdict(lambda: {
        'meetings': set(),
        'count': 0
    })
    
    for meeting_id, actors in meetings_to_actors.items():
        # Create edges between all pairs of actors in the same meeting
        for i, actor1 in enumerate(actors):
            for actor2 in actors[i+1:]:
                pair = tuple(sorted([actor1['id'], actor2['id']]))
                actor_pairs[pair]['meetings'].add(meeting_id)
                actor_pairs[pair]['count'] += 1
    
    # Add nodes and edges to graph
    for (actor1_id, actor2_id), data in actor_pairs.items():
        shared_meetings = len(data['meetings'])
        
        if shared_meetings >= 3:  # Minimum 3 shared meetings
            # Add nodes
            if actor1_id in actor_info:
                G.add_node(actor1_id, **actor_info[actor1_id])
            if actor2_id in actor_info:
                G.add_node(actor2_id, **actor_info[actor2_id])
            
            # Add edge
            G.add_edge(actor1_id, actor2_id,
                      weight=shared_meetings,
                      shared_meetings=shared_meetings,
                      meeting_ids=list(data['meetings']))
    
    print(f"Built committee network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G, meeting_info

# Build committee network
committee_network, meeting_info = build_committee_network()
```

## 5. Document Authorship Networks

### Building Document Co-authorship Networks

```python
def build_document_authorship_network():
    """Build network based on document co-authorship patterns."""
    
    print("Fetching document-actor relationships...")
    
    # Focus on authorship roles
    authorship_roles = [
        'Forslagsstiller',
        'Afsender',
        'Stiller',
        'Ordfører',
        'Medspørger'
    ]
    
    # Fetch document-actor relationships
    doc_actors = api.fetch_all_pages(
        'DokumentAktør',
        expand='Dokument,Aktør,DokumentAktørRolle',
        max_records=50000
    )
    
    # Group by documents and filter for authorship roles
    docs_to_authors = defaultdict(list)
    actor_info = {}
    
    for da in doc_actors:
        if (da.get('Dokument') and da.get('Aktør') and 
            da.get('DokumentAktørRolle')):
            
            role = da['DokumentAktørRolle'].get('rolle', '')
            
            if role in authorship_roles:
                doc_id = da['Dokument']['id']
                actor = da['Aktør']
                
                docs_to_authors[doc_id].append({
                    'id': actor['id'],
                    'name': actor.get('navn', ''),
                    'party': actor.get('gruppenavnkort', ''),
                    'role': role
                })
                
                # Store actor info
                actor_info[actor['id']] = {
                    'name': actor.get('navn', ''),
                    'party': actor.get('gruppenavnkort', ''),
                    'type': actor.get('typeid', 0)
                }
    
    # Build co-authorship network
    G = nx.Graph()
    
    # Count shared document authorship
    actor_pairs = defaultdict(lambda: {
        'documents': set(),
        'roles': defaultdict(int)
    })
    
    for doc_id, authors in docs_to_authors.items():
        if len(authors) > 1:  # Only multi-author documents
            for i, author1 in enumerate(authors):
                for author2 in authors[i+1:]:
                    pair = tuple(sorted([author1['id'], author2['id']]))
                    actor_pairs[pair]['documents'].add(doc_id)
                    actor_pairs[pair]['roles'][f"{author1['role']}-{author2['role']}"] += 1
    
    # Build graph
    for (actor1_id, actor2_id), data in actor_pairs.items():
        shared_docs = len(data['documents'])
        
        if shared_docs >= 2:  # Minimum 2 shared documents
            # Add nodes
            if actor1_id in actor_info and actor2_id in actor_info:
                G.add_node(actor1_id, **actor_info[actor1_id])
                G.add_node(actor2_id, **actor_info[actor2_id])
                
                # Most common role combination
                top_role_combo = max(data['roles'].items(), 
                                   key=lambda x: x[1])
                
                G.add_edge(actor1_id, actor2_id,
                          weight=shared_docs,
                          shared_documents=shared_docs,
                          document_ids=list(data['documents']),
                          primary_role_combo=top_role_combo[0],
                          role_combo_count=top_role_combo[1])
    
    print(f"Built authorship network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G

# Build authorship network
authorship_network = build_document_authorship_network()
```

## 6. Temporal Network Evolution

### Building Time-Series Networks

```python
def build_temporal_networks(network_type='cosponsorship', time_window_months=12):
    """Build network snapshots across different time periods."""
    
    print(f"Building temporal {network_type} networks...")
    
    # Fetch data with timestamps
    if network_type == 'cosponsorship':
        entity = 'SagAktør'
        expand = 'Sag,Aktør,SagAktørRolle'
        date_field = 'opdateringsdato'
    elif network_type == 'voting':
        entity = 'Stemme'
        expand = 'Afstemning/Møde,Aktør'
        date_field = 'opdateringsdato'
    
    # Fetch all data with timestamps
    data = api.fetch_all_pages(
        entity,
        expand=expand,
        max_records=50000
    )
    
    # Group by time windows
    temporal_data = defaultdict(list)
    
    for record in data:
        timestamp_str = record.get(date_field, '')
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                
                # Assign to time window (by year-month)
                window_key = f"{timestamp.year}-{timestamp.month:02d}"
                temporal_data[window_key].append(record)
                
            except (ValueError, AttributeError):
                continue
    
    # Build network for each time window
    temporal_networks = {}
    
    for window, window_data in temporal_data.items():
        print(f"Building network for {window} ({len(window_data)} records)")
        
        if network_type == 'cosponsorship':
            G = build_cosponsorship_network_from_data(window_data)
        elif network_type == 'voting':
            G = build_voting_network_from_data(window_data)
        
        if G.number_of_nodes() > 10:  # Only keep substantial networks
            temporal_networks[window] = G
    
    return temporal_networks

def analyze_network_evolution(temporal_networks):
    """Analyze how network structure changes over time."""
    
    evolution_metrics = {}
    
    for window, G in temporal_networks.items():
        metrics = {
            'nodes': G.number_of_nodes(),
            'edges': G.number_of_edges(),
            'density': nx.density(G),
            'avg_clustering': nx.average_clustering(G),
            'components': nx.number_connected_components(G)
        }
        
        evolution_metrics[window] = metrics
    
    # Create time series DataFrame
    df = pd.DataFrame(evolution_metrics).T
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    
    # Plot evolution
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Network Evolution Over Time', fontsize=16)
    
    # Nodes and edges
    axes[0, 0].plot(df.index, df['nodes'], marker='o', label='Nodes')
    axes[0, 0].plot(df.index, df['edges'], marker='s', label='Edges')
    axes[0, 0].set_title('Network Size')
    axes[0, 0].legend()
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Density
    axes[0, 1].plot(df.index, df['density'], marker='o', color='green')
    axes[0, 1].set_title('Network Density')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Clustering
    axes[1, 0].plot(df.index, df['avg_clustering'], marker='o', color='red')
    axes[1, 0].set_title('Average Clustering Coefficient')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Components
    axes[1, 1].plot(df.index, df['components'], marker='o', color='purple')
    axes[1, 1].set_title('Connected Components')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    return df

# Build temporal networks (example for co-sponsorship)
temporal_networks = build_temporal_networks('cosponsorship')
evolution_df = analyze_network_evolution(temporal_networks)
```

## 7. Centrality Measures and Influence Ranking

### Comprehensive Centrality Analysis

```python
def comprehensive_centrality_analysis(G, top_n=20):
    """Calculate multiple centrality measures and create influence rankings."""
    
    print("Calculating comprehensive centrality measures...")
    
    # Calculate all centrality measures
    centrality_measures = {}
    
    # Degree centrality (local influence)
    centrality_measures['degree'] = nx.degree_centrality(G)
    
    # Betweenness centrality (broker power)
    print("  Computing betweenness centrality...")
    centrality_measures['betweenness'] = nx.betweenness_centrality(G, k=min(1000, G.number_of_nodes()))
    
    # Closeness centrality (access to information)
    print("  Computing closeness centrality...")
    centrality_measures['closeness'] = nx.closeness_centrality(G)
    
    # Eigenvector centrality (connected to important nodes)
    print("  Computing eigenvector centrality...")
    try:
        centrality_measures['eigenvector'] = nx.eigenvector_centrality(G, max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        print("    Eigenvector centrality failed to converge, using approximation")
        centrality_measures['eigenvector'] = nx.eigenvector_centrality(G, max_iter=100, tol=1e-3)
    
    # PageRank (Google's algorithm adapted to networks)
    print("  Computing PageRank...")
    centrality_measures['pagerank'] = nx.pagerank(G, max_iter=1000)
    
    # Create comprehensive ranking DataFrame
    rankings_data = []
    
    for node in G.nodes():
        node_data = {
            'actor_id': node,
            'name': G.nodes[node].get('name', f'Actor {node}'),
            'party': G.nodes[node].get('party', 'Unknown'),
            'degree_centrality': centrality_measures['degree'][node],
            'betweenness_centrality': centrality_measures['betweenness'][node],
            'closeness_centrality': centrality_measures['closeness'][node],
            'eigenvector_centrality': centrality_measures['eigenvector'][node],
            'pagerank': centrality_measures['pagerank'][node]
        }
        rankings_data.append(node_data)
    
    # Create DataFrame and calculate composite influence score
    df = pd.DataFrame(rankings_data)
    
    # Normalize all centrality measures to 0-1 scale
    centrality_cols = ['degree_centrality', 'betweenness_centrality', 
                      'closeness_centrality', 'eigenvector_centrality', 'pagerank']
    
    for col in centrality_cols:
        df[f'{col}_norm'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
    
    # Calculate composite influence score (weighted average)
    weights = {
        'degree_centrality_norm': 0.2,
        'betweenness_centrality_norm': 0.25,
        'closeness_centrality_norm': 0.15,
        'eigenvector_centrality_norm': 0.2,
        'pagerank_norm': 0.2
    }
    
    df['composite_influence'] = sum(df[col] * weight for col, weight in weights.items())
    
    # Sort by composite influence
    df = df.sort_values('composite_influence', ascending=False)
    
    # Display top influencers
    print(f"\nTop {top_n} Most Influential Actors (Composite Score):")
    print("=" * 100)
    print(f"{'Rank':<4} {'Name':<30} {'Party':<15} {'Composite':<10} {'Degree':<8} {'Between':<8} {'Close':<8} {'Eigen':<8} {'PageRank':<8}")
    print("-" * 100)
    
    for i, (_, row) in enumerate(df.head(top_n).iterrows(), 1):
        print(f"{i:<4} {row['name'][:29]:<30} {row['party'][:14]:<15} "
              f"{row['composite_influence']:.3f}     "
              f"{row['degree_centrality']:.3f}    "
              f"{row['betweenness_centrality']:.3f}    "
              f"{row['closeness_centrality']:.3f}    "
              f"{row['eigenvector_centrality']:.3f}    "
              f"{row['pagerank']:.3f}")
    
    return df, centrality_measures

# Analyze centrality for co-sponsorship network
influence_rankings, centrality_data = comprehensive_centrality_analysis(cosponsorship_network)
```

### Party-Level Influence Analysis

```python
def analyze_party_influence(influence_df):
    """Analyze influence patterns by political party."""
    
    # Group by party and calculate statistics
    party_stats = influence_df.groupby('party').agg({
        'composite_influence': ['count', 'mean', 'median', 'std', 'sum'],
        'degree_centrality': 'mean',
        'betweenness_centrality': 'mean',
        'closeness_centrality': 'mean',
        'eigenvector_centrality': 'mean',
        'pagerank': 'mean'
    }).round(3)
    
    # Flatten column names
    party_stats.columns = ['_'.join(col).strip() for col in party_stats.columns]
    party_stats = party_stats.rename(columns={'composite_influence_count': 'member_count'})
    
    # Sort by total party influence
    party_stats = party_stats.sort_values('composite_influence_sum', ascending=False)
    
    print("\nParty Influence Analysis:")
    print("=" * 120)
    print(f"{'Party':<20} {'Members':<8} {'Avg Influence':<12} {'Total Influence':<14} {'Top Degree':<10} {'Top Between':<11}")
    print("-" * 120)
    
    for party, row in party_stats.head(10).iterrows():
        print(f"{party[:19]:<20} {int(row['member_count']):<8} "
              f"{row['composite_influence_mean']:.3f}        "
              f"{row['composite_influence_sum']:.3f}         "
              f"{row['degree_centrality_mean']:.3f}      "
              f"{row['betweenness_centrality_mean']:.3f}")
    
    # Visualize party influence distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Top parties by total influence
    top_parties = party_stats.head(8)
    ax1.barh(range(len(top_parties)), top_parties['composite_influence_sum'])
    ax1.set_yticks(range(len(top_parties)))
    ax1.set_yticklabels([party[:15] for party in top_parties.index])
    ax1.set_xlabel('Total Party Influence')
    ax1.set_title('Total Influence by Party')
    
    # Average influence vs member count
    ax2.scatter(party_stats['member_count'], party_stats['composite_influence_mean'])
    ax2.set_xlabel('Number of Members in Network')
    ax2.set_ylabel('Average Member Influence')
    ax2.set_title('Party Size vs Average Member Influence')
    
    # Add party labels for interesting points
    for party, row in party_stats.iterrows():
        if row['composite_influence_mean'] > party_stats['composite_influence_mean'].quantile(0.8):
            ax2.annotate(party[:10], 
                        (row['member_count'], row['composite_influence_mean']),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    plt.tight_layout()
    plt.show()
    
    return party_stats

# Analyze party influence
party_influence = analyze_party_influence(influence_rankings)
```

## 8. Community Detection in Political Networks

### Advanced Community Detection

```python
def advanced_community_detection(G):
    """Apply multiple community detection algorithms and compare results."""
    
    print("Applying multiple community detection algorithms...")
    
    community_results = {}
    
    # 1. Louvain Algorithm (modularity optimization)
    print("  Running Louvain algorithm...")
    louvain_communities = community_louvain.best_partition(G)
    community_results['louvain'] = louvain_communities
    
    # 2. Greedy Modularity Communities
    print("  Running greedy modularity algorithm...")
    greedy_communities = list(nx.community.greedy_modularity_communities(G))
    greedy_dict = {}
    for i, community in enumerate(greedy_communities):
        for node in community:
            greedy_dict[node] = i
    community_results['greedy'] = greedy_dict
    
    # 3. Label Propagation
    print("  Running label propagation algorithm...")
    label_communities = list(nx.community.label_propagation_communities(G))
    label_dict = {}
    for i, community in enumerate(label_communities):
        for node in community:
            label_dict[node] = i
    community_results['label_propagation'] = label_dict
    
    # Calculate modularity scores
    modularities = {}
    for algorithm, communities in community_results.items():
        # Convert to list of sets format for modularity calculation
        community_sets = defaultdict(set)
        for node, comm_id in communities.items():
            community_sets[comm_id].add(node)
        community_list = list(community_sets.values())
        
        modularity = nx.community.modularity(G, community_list)
        modularities[algorithm] = modularity
        
        print(f"  {algorithm.title()}: {len(community_list)} communities, modularity = {modularity:.3f}")
    
    # Choose best algorithm based on modularity
    best_algorithm = max(modularities.keys(), key=lambda x: modularities[x])
    best_communities = community_results[best_algorithm]
    
    print(f"\nBest algorithm: {best_algorithm.title()} (modularity = {modularities[best_algorithm]:.3f})")
    
    return best_communities, community_results, modularities

def analyze_political_communities(G, communities):
    """Analyze the political composition of detected communities."""
    
    # Group nodes by community
    community_groups = defaultdict(list)
    for node, comm_id in communities.items():
        community_groups[comm_id].append(node)
    
    # Analyze each community
    community_analysis = {}
    
    for comm_id, members in community_groups.items():
        if len(members) < 3:  # Skip very small communities
            continue
            
        # Collect member information
        member_info = []
        party_counts = defaultdict(int)
        
        for member in members:
            node_data = G.nodes[member]
            name = node_data.get('name', f'Actor {member}')
            party = node_data.get('party', 'Unknown')
            
            member_info.append({
                'id': member,
                'name': name,
                'party': party
            })
            
            party_counts[party] += 1
        
        # Calculate community statistics
        total_members = len(members)
        dominant_party = max(party_counts.items(), key=lambda x: x[1])
        party_diversity = len(party_counts)
        homogeneity = dominant_party[1] / total_members
        
        # Calculate internal vs external edges
        internal_edges = 0
        external_edges = 0
        
        for member in members:
            for neighbor in G.neighbors(member):
                if communities[neighbor] == comm_id:
                    internal_edges += 1
                else:
                    external_edges += 1
        
        internal_edges //= 2  # Each edge counted twice
        
        community_analysis[comm_id] = {
            'size': total_members,
            'members': member_info,
            'party_composition': dict(party_counts),
            'dominant_party': dominant_party,
            'party_diversity': party_diversity,
            'homogeneity': homogeneity,
            'internal_edges': internal_edges,
            'external_edges': external_edges,
            'cohesion': internal_edges / (internal_edges + external_edges) if (internal_edges + external_edges) > 0 else 0
        }
    
    # Sort communities by size
    sorted_communities = sorted(community_analysis.items(), 
                              key=lambda x: x[1]['size'], 
                              reverse=True)
    
    # Display analysis
    print(f"\nPolitical Community Analysis:")
    print("=" * 100)
    print(f"{'Comm':<4} {'Size':<6} {'Dominant Party':<20} {'Homog':<8} {'Diversity':<10} {'Cohesion':<8}")
    print("-" * 100)
    
    for comm_id, analysis in sorted_communities[:15]:  # Show top 15
        dominant_party_name = analysis['dominant_party'][0][:19]
        dominant_party_count = analysis['dominant_party'][1]
        
        print(f"{comm_id:<4} {analysis['size']:<6} "
              f"{dominant_party_name} ({dominant_party_count})  "
              f"{analysis['homogeneity']:.1%}      "
              f"{analysis['party_diversity']:<10} "
              f"{analysis['cohesion']:.3f}")
    
    # Detailed analysis for largest communities
    print(f"\nDetailed Analysis of Largest Communities:")
    print("=" * 80)
    
    for comm_id, analysis in sorted_communities[:5]:
        print(f"\nCommunity {comm_id} ({analysis['size']} members):")
        print(f"  Cohesion: {analysis['cohesion']:.1%} ({analysis['internal_edges']} internal, {analysis['external_edges']} external edges)")
        print(f"  Party composition:")
        
        for party, count in sorted(analysis['party_composition'].items(), 
                                 key=lambda x: x[1], 
                                 reverse=True)[:5]:
            percentage = count / analysis['size'] * 100
            print(f"    {party}: {count} members ({percentage:.1f}%)")
        
        print(f"  Sample members:")
        for member in analysis['members'][:8]:  # Show up to 8 members
            print(f"    {member['name']} ({member['party']})")
    
    return community_analysis

# Apply community detection
communities, all_results, modularities = advanced_community_detection(cosponsorship_network)
community_analysis = analyze_political_communities(cosponsorship_network, communities)
```

## 9. Network Visualization Techniques

### Interactive Network Visualization with Plotly

```python
def create_interactive_network_visualization(G, communities=None, layout='spring', 
                                           node_size_attr='degree_centrality', 
                                           edge_width_attr='weight'):
    """Create interactive network visualization using Plotly."""
    
    import plotly.graph_objects as go
    import plotly.express as px
    from math import sqrt
    
    # Calculate layout positions
    if layout == 'spring':
        pos = nx.spring_layout(G, k=1, iterations=50)
    elif layout == 'circular':
        pos = nx.circular_layout(G)
    elif layout == 'kamada_kawai':
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G)
    
    # Prepare edge traces
    edge_x = []
    edge_y = []
    edge_info = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # Edge info for hover
        node1_name = G.nodes[edge[0]].get('name', f'Actor {edge[0]}')
        node2_name = G.nodes[edge[1]].get('name', f'Actor {edge[1]}')
        weight = edge[2].get(edge_width_attr, 1)
        edge_info.append(f"{node1_name} ” {node2_name}<br>Weight: {weight}")
    
    edge_trace = go.Scatter(x=edge_x, y=edge_y,
                           line=dict(width=0.5, color='#888'),
                           hoverinfo='none',
                           mode='lines')
    
    # Prepare node traces
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    node_hover = []
    
    # Calculate node sizes
    if node_size_attr in ['degree_centrality', 'betweenness_centrality']:
        # Calculate centrality if not already available
        if node_size_attr == 'degree_centrality':
            centrality = nx.degree_centrality(G)
        else:
            centrality = nx.betweenness_centrality(G, k=min(1000, G.number_of_nodes()))
    else:
        centrality = {node: G.degree(node) for node in G.nodes()}
    
    max_centrality = max(centrality.values()) if centrality.values() else 1
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Node information
        node_data = G.nodes[node]
        name = node_data.get('name', f'Actor {node}')
        party = node_data.get('party', 'Unknown')
        
        node_text.append(name[:20])  # Truncate long names
        
        # Color by community or party
        if communities and node in communities:
            node_color.append(communities[node])
        else:
            # Color by party (hash-based coloring)
            node_color.append(hash(party) % 20)
        
        # Size by centrality
        centrality_score = centrality.get(node, 0)
        size = 10 + 30 * (centrality_score / max_centrality)
        node_size.append(size)
        
        # Hover information
        degree = G.degree(node)
        hover_text = f"<b>{name}</b><br>"
        hover_text += f"Party: {party}<br>"
        hover_text += f"Degree: {degree}<br>"
        hover_text += f"Centrality: {centrality_score:.3f}"
        if communities and node in communities:
            hover_text += f"<br>Community: {communities[node]}"
        
        node_hover.append(hover_text)
    
    node_trace = go.Scatter(x=node_x, y=node_y,
                           mode='markers+text',
                           hoverinfo='text',
                           hovertext=node_hover,
                           text=node_text,
                           textposition="middle center",
                           textfont=dict(size=8),
                           marker=dict(size=node_size,
                                     color=node_color,
                                     colorscale='Viridis',
                                     showscale=True,
                                     colorbar=dict(title="Community" if communities else "Party"),
                                     line=dict(width=2, color='white')))
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title=f'Parliamentary Network Visualization ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)',
                       titlefont_size=16,
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       annotations=[ dict(
                           text="Hover over nodes for details. Node size = centrality, color = community/party",
                           showarrow=False,
                           xref="paper", yref="paper",
                           x=0.005, y=-0.002,
                           xanchor='left', yanchor='bottom',
                           font=dict(color="gray", size=12)
                       )],
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       width=1200,
                       height=800))
    
    return fig

# Create interactive visualization
fig = create_interactive_network_visualization(
    cosponsorship_network, 
    communities=communities,
    node_size_attr='degree_centrality'
)

# Show the plot
fig.show()

# Save as HTML file
fig.write_html("/tmp/parliamentary_network.html")
print("Interactive visualization saved as parliamentary_network.html")
```

### Static Network Visualization with NetworkX

```python
def create_static_network_visualization(G, communities=None, figsize=(20, 16)):
    """Create high-quality static network visualization."""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
    
    # 1. Basic network layout
    pos = nx.spring_layout(G, k=1, iterations=50, seed=42)
    
    # Color nodes by party
    parties = [G.nodes[node].get('party', 'Unknown') for node in G.nodes()]
    unique_parties = list(set(parties))
    party_colors = plt.cm.Set3(np.linspace(0, 1, len(unique_parties)))
    party_color_map = dict(zip(unique_parties, party_colors))
    node_colors = [party_color_map[party] for party in parties]
    
    # Node sizes by degree
    node_sizes = [G.degree(node) * 20 for node in G.nodes()]
    
    nx.draw(G, pos, ax=ax1, node_color=node_colors, node_size=node_sizes,
            edge_color='gray', alpha=0.7, with_labels=False)
    ax1.set_title('Network by Party Affiliation')
    
    # 2. Community-colored network
    if communities:
        community_colors = [communities[node] for node in G.nodes()]
        nx.draw(G, pos, ax=ax2, node_color=community_colors, node_size=node_sizes,
                cmap=plt.cm.viridis, edge_color='gray', alpha=0.7, with_labels=False)
        ax2.set_title('Network by Detected Communities')
    
    # 3. Degree distribution
    degrees = [G.degree(node) for node in G.nodes()]
    ax3.hist(degrees, bins=30, alpha=0.7, edgecolor='black')
    ax3.set_xlabel('Degree')
    ax3.set_ylabel('Frequency')
    ax3.set_title('Degree Distribution')
    ax3.grid(True, alpha=0.3)
    
    # 4. Centrality comparison for top nodes
    degree_centrality = nx.degree_centrality(G)
    top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:15]
    
    node_names = [G.nodes[node].get('name', f'Actor {node}')[:20] for node, _ in top_nodes]
    centrality_values = [centrality for _, centrality in top_nodes]
    
    y_pos = np.arange(len(node_names))
    ax4.barh(y_pos, centrality_values)
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(node_names, fontsize=10)
    ax4.set_xlabel('Degree Centrality')
    ax4.set_title('Top 15 Most Central Actors')
    ax4.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.show()

# Create static visualization
create_static_network_visualization(cosponsorship_network, communities)
```

## 10. Network Analysis Tools and Recommendations

### Recommended Python Libraries

```python
# Essential network analysis libraries
NETWORK_LIBRARIES = {
    'networkx': 'General-purpose network analysis and algorithms',
    'igraph': 'High-performance network analysis with C backend', 
    'graph-tool': 'Very fast analysis for large networks',
    'networkit': 'High-performance analysis for massive networks',
    'networkx': 'Most comprehensive and user-friendly',
}

# Visualization libraries
VISUALIZATION_LIBRARIES = {
    'plotly': 'Interactive web-based visualizations',
    'bokeh': 'Interactive visualizations with zoom/pan',
    'matplotlib': 'Static high-quality publication graphics',
    'seaborn': 'Statistical visualization built on matplotlib',
    'pyvis': 'Simple interactive network visualization',
    'gephi': 'Standalone network visualization software (not Python)',
}

# Community detection libraries
COMMUNITY_LIBRARIES = {
    'python-louvain': 'Louvain algorithm for modularity optimization',
    'community': 'Multiple community detection algorithms',
    'networkx.algorithms.community': 'Built-in NetworkX community detection',
    'cdlib': 'Comprehensive community detection library',
    'scikit-network': 'Network analysis with scikit-learn style API',
}
```

### Performance Optimization Tips

```python
def optimize_network_analysis():
    """Tips for optimizing network analysis performance."""
    
    tips = {
        'data_fetching': [
            'Use pagination ($top/$skip) to avoid memory issues',
            'Filter data early with $filter to reduce transfer',
            'Use $select to get only needed fields',
            'Cache frequently used data locally',
            'Implement retry logic for network failures'
        ],
        
        'network_construction': [
            'Use appropriate data structures (dict for fast lookups)',
            'Pre-filter relationships before building networks',
            'Consider edge weight thresholds to reduce noise',
            'Use sparse representations for large networks',
            'Build networks incrementally when possible'
        ],
        
        'algorithm_optimization': [
            'Sample large networks for expensive computations',
            'Use approximate algorithms for large networks',
            'Parallelize independent computations',
            'Cache centrality calculations',
            'Use efficient community detection algorithms'
        ],
        
        'memory_management': [
            'Process data in chunks for large datasets',
            'Use generators instead of lists when possible',
            'Clear unused variables and call gc.collect()',
            'Monitor memory usage with memory_profiler',
            'Consider using graph databases for very large networks'
        ]
    }
    
    return tips

# Print optimization tips
optimization_tips = optimize_network_analysis()
for category, tip_list in optimization_tips.items():
    print(f"\n{category.replace('_', ' ').title()}:")
    for tip in tip_list:
        print(f"  " {tip}")
```

### Complete Analysis Workflow

```python
def complete_network_analysis_workflow():
    """Complete workflow for parliamentary network analysis."""
    
    workflow = {
        '1_data_preparation': [
            'Identify relevant entities and relationships',
            'Fetch data using pagination and proper URL encoding',
            'Clean and validate data quality',
            'Handle missing values and inconsistencies',
            'Create unified actor/node identifier system'
        ],
        
        '2_network_construction': [
            'Define edge criteria (shared cases, voting alignment, etc.)',
            'Set appropriate thresholds for edge inclusion',
            'Add node attributes (party, type, biographical info)',
            'Add edge attributes (weights, relationship types)',
            'Validate network connectivity and size'
        ],
        
        '3_descriptive_analysis': [
            'Calculate basic network statistics (nodes, edges, density)',
            'Analyze degree distribution and network topology',
            'Identify connected components',
            'Calculate clustering coefficients',
            'Generate summary statistics by party/group'
        ],
        
        '4_centrality_analysis': [
            'Calculate multiple centrality measures',
            'Identify most influential actors',
            'Analyze party-level influence patterns',
            'Create composite influence rankings',
            'Validate results with domain knowledge'
        ],
        
        '5_community_detection': [
            'Apply multiple community detection algorithms',
            'Compare results and select best approach',
            'Analyze community composition by party',
            'Identify cross-party communities',
            'Assess community stability over time'
        ],
        
        '6_temporal_analysis': [
            'Build networks for different time periods',
            'Analyze network evolution over time',
            'Track changes in actor influence',
            'Identify emerging and declining communities',
            'Correlate changes with political events'
        ],
        
        '7_visualization': [
            'Create interactive network visualizations',
            'Generate publication-quality static plots',
            'Develop dashboards for exploration',
            'Export networks for external tools (Gephi)',
            'Create summary infographics'
        ],
        
        '8_interpretation': [
            'Contextualize findings within political science',
            'Validate results with parliamentary experts',
            'Identify limitations and biases',
            'Generate actionable insights',
            'Document methodology and assumptions'
        ]
    }
    
    return workflow

# Print complete workflow
workflow = complete_network_analysis_workflow()
for phase, steps in workflow.items():
    print(f"\n{phase.replace('_', ' ').title()}:")
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")
```

## Conclusion

This guide provides a comprehensive framework for conducting network analysis using the Danish Parliamentary Open Data API. The rich relationship data available through junction tables like `SagAktør`, `DokumentAktør`, and `MødeAktør` enables sophisticated analysis of:

- **Political collaboration patterns** through co-sponsorship networks
- **Voting alignment and opposition** through voting networks  
- **Information flow and communication** through document networks
- **Institutional influence** through committee networks
- **Temporal evolution** of political relationships
- **Community structure** within the parliamentary system

The Danish Parliament's transparent data infrastructure, with 18,139+ actors and comprehensive relationship tracking, provides an exceptional foundation for understanding democratic processes through network analysis. By following these methodologies, researchers can uncover hidden patterns of influence, collaboration, and political dynamics that shape legislative outcomes.

### Key Success Factors

1. **Proper OData handling**: Always use `%24` instead of `$` in URL parameters
2. **Efficient data fetching**: Use pagination and filtering to manage large datasets  
3. **Appropriate thresholds**: Set meaningful minimum criteria for network edges
4. **Multiple algorithms**: Compare different approaches for robust results
5. **Domain validation**: Contextualize findings within political science knowledge
6. **Performance optimization**: Use sampling and approximation for large networks
7. **Comprehensive documentation**: Track methodology and assumptions throughout

This network analysis framework opens new possibilities for understanding parliamentary democracy, political influence, and legislative collaboration patterns in one of the world's most transparent political systems.