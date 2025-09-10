# Voting Pattern Analysis

This guide demonstrates how to identify and analyze complex voting patterns in the Danish Parliamentary OData API, providing methodologies for temporal analysis, clustering, coalition tracking, and predictive modeling using machine learning techniques.

## Overview

Voting pattern analysis reveals the underlying political dynamics within the Danish Parliament (Folketing). By examining how politicians and parties vote across different issues, time periods, and procedural contexts, we can identify coalitions, predict outcomes, and understand the evolution of political alliances.

### Key Data Sources

| Entity | Purpose | Key Fields |
|--------|---------|------------|
| `Afstemning` | Voting sessions | `konklusion`, `vedtaget`, `mødeid`, `typeid` |
| `Stemme` | Individual votes | `typeid`, `aktorid`, `afstemningid` |
| `Aktør` | Politicians/Parties | `id`, `navn`, `gruppeid` |
| `Sag` | Legislative cases | `afgørelse`, `afstemningskonklusion`, `typeid` |
| `Møde` | Parliamentary meetings | `dato`, `nummer`, `periodeid` |

## Pattern Analysis Fundamentals

### 1. Basic Voting Data Retrieval

```python
import requests
import pandas as pd
from datetime import datetime
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

class VotingPatternAnalyzer:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api"
        self.voting_data = None
        self.actor_data = None
        self.meeting_data = None
    
    def fetch_voting_data(self, limit=1000):
        """Fetch comprehensive voting data with actor and meeting details"""
        url = f"{self.base_url}/Afstemning"
        params = {
            '$expand': 'Stemme($expand=Aktør),Møde',
            '$top': limit,
            '$orderby': 'id desc'
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return self.process_voting_data(data['value'])
        return None
    
    def process_voting_data(self, raw_data):
        """Process raw voting data into analysis-ready format"""
        processed = []
        
        for vote_session in raw_data:
            # Extract vote session info
            session_info = {
                'vote_id': vote_session['id'],
                'conclusion': vote_session['konklusion'],
                'passed': vote_session['vedtaget'],
                'meeting_id': vote_session['mødeid'],
                'type_id': vote_session['typeid'],
                'meeting_date': vote_session.get('Møde', {}).get('dato') if vote_session.get('Møde') else None
            }
            
            # Process individual votes
            if vote_session.get('Stemme'):
                for individual_vote in vote_session['Stemme']:
                    vote_record = session_info.copy()
                    vote_record.update({
                        'actor_id': individual_vote['aktorid'],
                        'vote_type': individual_vote['typeid'],
                        'actor_name': individual_vote.get('Aktør', {}).get('navn', ''),
                        'party_id': individual_vote.get('Aktør', {}).get('gruppeid')
                    })
                    processed.append(vote_record)
            else:
                # Session without individual votes
                processed.append(session_info)
        
        return pd.DataFrame(processed)

# Initialize analyzer
analyzer = VotingPatternAnalyzer()
voting_df = analyzer.fetch_voting_data(500)
print(f"Loaded {len(voting_df)} voting records")
```

### 2. Vote Type Classification

```python
def classify_vote_types(df):
    """Classify votes into different categories based on content analysis"""
    
    # Define voting type mappings (based on API data exploration)
    vote_type_mapping = {
        1: 'For',           # Stemme for
        2: 'Against',       # Stemme imod  
        3: 'Abstention',    # Hverken for eller imod
        4: 'Absent'         # Fraværende
    }
    
    df['vote_category'] = df['vote_type'].map(vote_type_mapping)
    
    # Procedural vs substantive classification
    df['is_procedural'] = df['conclusion'].str.contains(
        'forretningsorden|procedur|henvisning|udvalg',
        case=False, na=False
    )
    
    # Amendment vs main proposal
    df['is_amendment'] = df['conclusion'].str.contains(
        'ændringsforslag|amendment',
        case=False, na=False
    )
    
    return df

voting_df = classify_vote_types(voting_df)
```

## Temporal Voting Pattern Analysis

### 1. Time-Series Voting Trends

```python
def analyze_temporal_patterns(df):
    """Analyze voting patterns over time"""
    
    # Convert meeting dates
    df['meeting_date'] = pd.to_datetime(df['meeting_date'])
    df['year'] = df['meeting_date'].dt.year
    df['month'] = df['meeting_date'].dt.month
    df['week'] = df['meeting_date'].dt.isocalendar().week
    
    # Calculate voting cohesion by time period
    temporal_cohesion = df.groupby(['year', 'month', 'party_id']).agg({
        'vote_type': lambda x: len(x[x == x.mode().iloc[0]]) / len(x) if len(x) > 0 else 0
    }).reset_index()
    temporal_cohesion.columns = ['year', 'month', 'party_id', 'cohesion_score']
    
    return temporal_cohesion

def detect_seasonal_patterns(df):
    """Identify seasonal voting behavior patterns"""
    
    # Parliamentary session periods (typically September to June)
    df['session_period'] = df['meeting_date'].apply(
        lambda x: 'autumn' if x.month in [9, 10, 11, 12] 
        else 'spring' if x.month in [1, 2, 3, 4, 5, 6]
        else 'summer_recess'
    )
    
    # Analyze voting intensity by period
    seasonal_analysis = df.groupby(['session_period', 'year']).agg({
        'vote_id': 'nunique',
        'passed': 'mean',
        'is_procedural': 'mean'
    }).reset_index()
    
    return seasonal_analysis

# Perform temporal analysis
temporal_patterns = analyze_temporal_patterns(voting_df)
seasonal_patterns = detect_seasonal_patterns(voting_df)
```

### 2. Parliamentary Cycle Analysis

```python
def analyze_electoral_cycles(df):
    """Analyze voting pattern changes across electoral cycles"""
    
    # Danish parliamentary elections typically every 4 years
    # Add electoral period classification
    electoral_periods = {
        2019: '2019-2023',
        2020: '2019-2023', 
        2021: '2019-2023',
        2022: '2019-2023',
        2023: '2023-2027',
        2024: '2023-2027',
        2025: '2023-2027'
    }
    
    df['electoral_period'] = df['year'].map(electoral_periods)
    
    # Analyze voting behavior changes by electoral phase
    df['days_since_election'] = (
        df['meeting_date'] - pd.to_datetime('2022-11-01')  # Last election
    ).dt.days
    
    # Categorize parliamentary phase
    df['parliamentary_phase'] = pd.cut(
        df['days_since_election'],
        bins=[-np.inf, 365, 730, 1095, np.inf],
        labels=['Year_1', 'Year_2', 'Year_3', 'Year_4+']
    )
    
    return df

voting_df = analyze_electoral_cycles(voting_df)
```

## Issue-Based Voting Clustering

### 1. Topic Clustering Analysis

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA

def perform_issue_clustering(df):
    """Cluster voting sessions by issue content"""
    
    # Prepare text data for clustering
    text_data = df['conclusion'].fillna('').astype(str)
    
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words=None,  # Danish stop words would be ideal
        ngram_range=(1, 2),
        min_df=3
    )
    
    tfidf_matrix = vectorizer.fit_transform(text_data)
    
    # DBSCAN clustering for topic identification
    clustering = DBSCAN(eps=0.3, min_samples=5, metric='cosine')
    clusters = clustering.fit_predict(tfidf_matrix.toarray())
    
    df['issue_cluster'] = clusters
    
    # Analyze cluster characteristics
    cluster_analysis = df.groupby('issue_cluster').agg({
        'vote_id': 'count',
        'passed': 'mean',
        'is_procedural': 'mean',
        'conclusion': lambda x: ' | '.join(x.head(3))  # Sample conclusions
    }).reset_index()
    
    return df, cluster_analysis

# Perform issue clustering
voting_df, issue_clusters = perform_issue_clustering(voting_df)
```

### 2. Voting Similarity Matrix

```python
def create_voting_similarity_matrix(df):
    """Create actor-to-actor voting similarity matrix"""
    
    # Create pivot table of actor votes
    vote_matrix = df.pivot_table(
        index='actor_id',
        columns='vote_id', 
        values='vote_type',
        fill_value=-1  # Use -1 for absent votes
    )
    
    # Calculate cosine similarity between actors
    from sklearn.metrics.pairwise import cosine_similarity
    
    similarity_matrix = cosine_similarity(vote_matrix.fillna(0))
    similarity_df = pd.DataFrame(
        similarity_matrix,
        index=vote_matrix.index,
        columns=vote_matrix.index
    )
    
    return similarity_df, vote_matrix

similarity_matrix, vote_pivot = create_voting_similarity_matrix(voting_df)
```

## Coalition Formation Analysis

### 1. Dynamic Coalition Detection

```python
def detect_voting_coalitions(df, time_window='6M'):
    """Detect coalitions using sliding time windows"""
    
    coalitions = []
    df_sorted = df.sort_values('meeting_date')
    
    # Create time windows
    start_date = df_sorted['meeting_date'].min()
    end_date = df_sorted['meeting_date'].max()
    
    current_date = start_date
    while current_date < end_date:
        window_end = current_date + pd.DateOffset(months=6)
        window_data = df_sorted[
            (df_sorted['meeting_date'] >= current_date) & 
            (df_sorted['meeting_date'] < window_end)
        ]
        
        if len(window_data) > 10:  # Minimum votes for analysis
            # Calculate agreement rates between parties
            party_agreements = calculate_party_agreements(window_data)
            coalition_groups = identify_coalition_groups(party_agreements)
            
            coalitions.append({
                'period_start': current_date,
                'period_end': window_end,
                'coalitions': coalition_groups,
                'vote_count': len(window_data)
            })
        
        current_date = window_end
    
    return coalitions

def calculate_party_agreements(df):
    """Calculate agreement rates between all party pairs"""
    
    agreements = {}
    parties = df['party_id'].dropna().unique()
    
    for party1 in parties:
        for party2 in parties:
            if party1 != party2:
                # Get votes where both parties participated
                both_voted = df[
                    df['party_id'].isin([party1, party2]) & 
                    df['vote_type'].notna()
                ]
                
                if len(both_voted) > 0:
                    # Calculate agreement rate
                    vote_pairs = both_voted.groupby('vote_id')['vote_type'].apply(list)
                    agreements_count = sum(
                        1 for votes in vote_pairs 
                        if len(set(votes)) == 1  # All voted the same way
                    )
                    
                    agreement_rate = agreements_count / len(vote_pairs)
                    agreements[(party1, party2)] = agreement_rate
    
    return agreements

def identify_coalition_groups(agreements, threshold=0.7):
    """Identify coalition groups based on agreement thresholds"""
    
    import networkx as nx
    
    # Create graph of party relationships
    G = nx.Graph()
    
    for (party1, party2), agreement in agreements.items():
        if agreement >= threshold:
            G.add_edge(party1, party2, weight=agreement)
    
    # Find connected components (coalitions)
    coalitions = list(nx.connected_components(G))
    
    return [list(coalition) for coalition in coalitions]

# Detect coalitions
coalition_history = detect_voting_coalitions(voting_df)
```

### 2. Coalition Stability Analysis

```python
def analyze_coalition_stability(coalition_history):
    """Analyze stability and evolution of coalitions over time"""
    
    stability_metrics = []
    
    for i, current_period in enumerate(coalition_history[1:], 1):
        previous_period = coalition_history[i-1]
        
        # Calculate Jaccard similarity for coalition persistence
        current_coalitions = set(
            tuple(sorted(coalition)) 
            for coalition in current_period['coalitions']
        )
        previous_coalitions = set(
            tuple(sorted(coalition)) 
            for coalition in previous_period['coalitions']
        )
        
        if len(current_coalitions) > 0 or len(previous_coalitions) > 0:
            jaccard_similarity = len(current_coalitions & previous_coalitions) / \
                               len(current_coalitions | previous_coalitions)
        else:
            jaccard_similarity = 1.0
        
        stability_metrics.append({
            'period': current_period['period_start'],
            'stability_score': jaccard_similarity,
            'coalition_count': len(current_period['coalitions']),
            'vote_count': current_period['vote_count']
        })
    
    return pd.DataFrame(stability_metrics)

stability_analysis = analyze_coalition_stability(coalition_history)
```

## Voting Bloc Identification

### 1. Hierarchical Clustering of Voting Patterns

```python
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist

def identify_voting_blocs(similarity_matrix):
    """Identify voting blocs using hierarchical clustering"""
    
    # Convert similarity to distance matrix
    distance_matrix = 1 - similarity_matrix
    
    # Perform hierarchical clustering
    condensed_distances = pdist(distance_matrix, metric='precomputed')
    linkage_matrix = linkage(condensed_distances, method='ward')
    
    # Create dendrogram
    plt.figure(figsize=(15, 8))
    dendrogram(linkage_matrix, labels=similarity_matrix.index)
    plt.title('Voting Pattern Dendrogram')
    plt.xlabel('Actor ID')
    plt.ylabel('Distance')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    # Extract clusters at different heights
    from scipy.cluster.hierarchy import fcluster
    
    bloc_assignments = {}
    for n_clusters in [3, 5, 7, 10]:
        clusters = fcluster(linkage_matrix, n_clusters, criterion='maxclust')
        bloc_assignments[f'{n_clusters}_blocs'] = dict(zip(similarity_matrix.index, clusters))
    
    return bloc_assignments

voting_blocs = identify_voting_blocs(similarity_matrix)
```

### 2. Bloc Evolution Tracking

```python
def track_bloc_evolution(df, bloc_assignments):
    """Track how voting blocs evolve over time"""
    
    evolution_data = []
    
    # Add bloc assignments to main dataframe
    for bloc_config, assignments in bloc_assignments.items():
        df[f'bloc_{bloc_config}'] = df['actor_id'].map(assignments)
    
    # Analyze bloc voting patterns by time period
    df['quarter'] = df['meeting_date'].dt.to_period('Q')
    
    for bloc_config in bloc_assignments.keys():
        bloc_col = f'bloc_{bloc_config}'
        
        quarterly_patterns = df.groupby(['quarter', bloc_col]).agg({
            'vote_type': lambda x: x.mode().iloc[0] if len(x) > 0 else None,
            'passed': 'mean',
            'is_procedural': 'mean',
            'actor_id': 'nunique'
        }).reset_index()
        
        quarterly_patterns['bloc_config'] = bloc_config
        evolution_data.append(quarterly_patterns)
    
    return pd.concat(evolution_data, ignore_index=True)

bloc_evolution = track_bloc_evolution(voting_df, voting_blocs)
```

## Procedural vs Substantive Voting Analysis

### 1. Voting Behavior Classification

```python
def analyze_procedural_vs_substantive(df):
    """Compare voting patterns for procedural vs substantive votes"""
    
    comparison_metrics = []
    
    for vote_type in ['procedural', 'substantive']:
        subset = df[df['is_procedural'] == (vote_type == 'procedural')]
        
        if len(subset) > 0:
            metrics = {
                'vote_type': vote_type,
                'total_votes': len(subset),
                'pass_rate': subset['passed'].mean(),
                'unanimity_rate': calculate_unanimity_rate(subset),
                'party_cohesion': calculate_average_party_cohesion(subset),
                'cross_party_agreement': calculate_cross_party_agreement(subset)
            }
            comparison_metrics.append(metrics)
    
    return pd.DataFrame(comparison_metrics)

def calculate_unanimity_rate(df):
    """Calculate rate of unanimous votes"""
    vote_distributions = df.groupby('vote_id')['vote_type'].nunique()
    unanimous_votes = (vote_distributions == 1).sum()
    return unanimous_votes / len(vote_distributions) if len(vote_distributions) > 0 else 0

def calculate_average_party_cohesion(df):
    """Calculate average party cohesion across votes"""
    cohesion_scores = []
    
    for party in df['party_id'].dropna().unique():
        party_votes = df[df['party_id'] == party]
        party_cohesion = party_votes.groupby('vote_id').apply(
            lambda x: len(x[x['vote_type'] == x['vote_type'].mode().iloc[0]]) / len(x) 
            if len(x) > 0 else 0
        ).mean()
        cohesion_scores.append(party_cohesion)
    
    return np.mean(cohesion_scores) if cohesion_scores else 0

procedural_analysis = analyze_procedural_vs_substantive(voting_df)
```

## Predictive Modeling for Voting Outcomes

### 1. Machine Learning Model Development

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix

def build_voting_prediction_model(df):
    """Build ML model to predict voting outcomes"""
    
    # Feature engineering
    features_df = create_prediction_features(df)
    
    # Prepare target variable
    target = features_df['passed'].astype(int)
    
    # Select features
    feature_columns = [
        'vote_type_encoded', 'party_id_encoded', 'is_procedural',
        'is_amendment', 'meeting_month', 'meeting_weekday',
        'days_since_election', 'historical_pass_rate_actor',
        'historical_pass_rate_party', 'coalition_size'
    ]
    
    X = features_df[feature_columns].fillna(0)
    y = target
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    # Train Random Forest model
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42
    )
    
    rf_model.fit(X_train, y_train)
    
    # Evaluate model
    train_score = rf_model.score(X_train, y_train)
    test_score = rf_model.score(X_test, y_test)
    
    # Cross-validation
    cv_scores = cross_val_score(rf_model, X_train, y_train, cv=5)
    
    # Predictions
    y_pred = rf_model.predict(X_test)
    
    results = {
        'model': rf_model,
        'train_score': train_score,
        'test_score': test_score,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'classification_report': classification_report(y_test, y_pred),
        'feature_importance': dict(zip(feature_columns, rf_model.feature_importances_))
    }
    
    return results

def create_prediction_features(df):
    """Create features for prediction model"""
    
    features = df.copy()
    
    # Encode categorical variables
    features['vote_type_encoded'] = pd.Categorical(features['vote_type']).codes
    features['party_id_encoded'] = pd.Categorical(features['party_id']).codes
    
    # Time-based features
    features['meeting_month'] = features['meeting_date'].dt.month
    features['meeting_weekday'] = features['meeting_date'].dt.weekday
    
    # Historical performance features
    features['historical_pass_rate_actor'] = features.groupby('actor_id')['passed'].transform(
        lambda x: x.expanding().mean().shift(1)
    )
    
    features['historical_pass_rate_party'] = features.groupby('party_id')['passed'].transform(
        lambda x: x.expanding().mean().shift(1)
    )
    
    # Coalition size feature (placeholder - would need party seat data)
    features['coalition_size'] = features.groupby('vote_id')['party_id'].transform('nunique')
    
    return features

# Build prediction model
prediction_results = build_voting_prediction_model(voting_df)
print(f"Model Accuracy: {prediction_results['test_score']:.3f}")
print(f"Cross-validation: {prediction_results['cv_mean']:.3f} (±{prediction_results['cv_std']:.3f})")
```

### 2. Deep Learning Approach

```python
import tensorflow as tf
from tensorflow.keras import layers, models

def build_neural_network_predictor(df, sequence_length=10):
    """Build LSTM model for sequential voting prediction"""
    
    # Prepare sequential data
    actor_sequences = []
    outcomes = []
    
    for actor_id in df['actor_id'].unique():
        actor_data = df[df['actor_id'] == actor_id].sort_values('meeting_date')
        
        if len(actor_data) >= sequence_length:
            for i in range(len(actor_data) - sequence_length):
                sequence = actor_data.iloc[i:i+sequence_length]
                next_vote = actor_data.iloc[i+sequence_length]
                
                # Create feature sequence
                features = sequence[['vote_type', 'is_procedural', 'party_id_encoded']].values
                outcome = next_vote['passed']
                
                actor_sequences.append(features)
                outcomes.append(outcome)
    
    X = np.array(actor_sequences)
    y = np.array(outcomes)
    
    # Build LSTM model
    model = models.Sequential([
        layers.LSTM(64, return_sequences=True, input_shape=(sequence_length, 3)),
        layers.Dropout(0.2),
        layers.LSTM(32),
        layers.Dropout(0.2),
        layers.Dense(16, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    # Train model
    history = model.fit(
        X, y,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        verbose=1
    )
    
    return model, history

# Build neural network predictor
nn_model, training_history = build_neural_network_predictor(voting_df)
```

## Advanced Pattern Recognition

### 1. Anomaly Detection in Voting Patterns

```python
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def detect_voting_anomalies(df):
    """Detect unusual voting patterns using isolation forest"""
    
    # Create features for anomaly detection
    actor_features = df.groupby('actor_id').agg({
        'vote_type': lambda x: pd.Series(x).value_counts().to_dict(),
        'passed': 'mean',
        'is_procedural': 'mean',
        'party_id': 'first'
    }).reset_index()
    
    # Expand vote_type dictionary into separate columns
    vote_type_expanded = pd.json_normalize(actor_features['vote_type']).fillna(0)
    
    # Combine features
    features = pd.concat([
        actor_features[['actor_id', 'passed', 'is_procedural']],
        vote_type_expanded
    ], axis=1)
    
    # Standardize features
    scaler = StandardScaler()
    feature_matrix = scaler.fit_transform(features.select_dtypes(include=[np.number]))
    
    # Apply Isolation Forest
    isolation_forest = IsolationForest(
        contamination=0.1,
        random_state=42
    )
    
    anomaly_labels = isolation_forest.fit_predict(feature_matrix)
    
    # Add anomaly scores
    features['is_anomaly'] = anomaly_labels == -1
    features['anomaly_score'] = isolation_forest.score_samples(feature_matrix)
    
    return features

anomaly_results = detect_voting_anomalies(voting_df)
```

### 2. Network Analysis of Voting Relationships

```python
import networkx as nx

def create_voting_network(df, agreement_threshold=0.8):
    """Create network graph of voting relationships"""
    
    # Calculate pairwise agreement rates
    actors = df['actor_id'].unique()
    
    G = nx.Graph()
    
    for actor1 in actors:
        for actor2 in actors:
            if actor1 != actor2:
                # Find common votes
                votes1 = df[df['actor_id'] == actor1]
                votes2 = df[df['actor_id'] == actor2]
                
                common_votes = pd.merge(
                    votes1[['vote_id', 'vote_type']], 
                    votes2[['vote_id', 'vote_type']], 
                    on='vote_id',
                    suffixes=('_1', '_2')
                )
                
                if len(common_votes) > 5:  # Minimum common votes
                    agreement_rate = (
                        common_votes['vote_type_1'] == common_votes['vote_type_2']
                    ).mean()
                    
                    if agreement_rate >= agreement_threshold:
                        G.add_edge(actor1, actor2, weight=agreement_rate)
    
    return G

def analyze_network_properties(G):
    """Analyze network properties and identify communities"""
    
    # Basic network metrics
    metrics = {
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'avg_clustering': nx.average_clustering(G),
        'components': nx.number_connected_components(G)
    }
    
    # Community detection
    if len(G.nodes) > 0:
        communities = nx.community.greedy_modularity_communities(G)
        metrics['communities'] = len(communities)
        metrics['modularity'] = nx.community.modularity(G, communities)
    
    return metrics, communities

# Create and analyze voting network
voting_network = create_voting_network(voting_df)
network_metrics, communities = analyze_network_properties(voting_network)
```

## Visualization and Reporting

### 1. Comprehensive Voting Dashboard

```python
def create_voting_dashboard(df, save_path='voting_dashboard.html'):
    """Create interactive dashboard for voting pattern analysis"""
    
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.express as px
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Voting Outcomes Over Time',
            'Party Agreement Heatmap', 
            'Coalition Stability',
            'Vote Type Distribution',
            'Seasonal Patterns',
            'Prediction Accuracy'
        ),
        specs=[
            [{"secondary_y": True}, {"type": "xy"}],
            [{"type": "xy"}, {"type": "xy"}],
            [{"type": "xy"}, {"type": "xy"}]
        ]
    )
    
    # 1. Voting outcomes over time
    monthly_outcomes = df.groupby(df['meeting_date'].dt.to_period('M')).agg({
        'passed': 'mean',
        'vote_id': 'count'
    }).reset_index()
    
    fig.add_trace(
        go.Scatter(
            x=monthly_outcomes['meeting_date'].astype(str),
            y=monthly_outcomes['passed'],
            name='Pass Rate',
            line=dict(color='blue')
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=monthly_outcomes['meeting_date'].astype(str),
            y=monthly_outcomes['vote_id'],
            name='Vote Count',
            yaxis='y2',
            line=dict(color='red')
        ),
        row=1, col=1, secondary_y=True
    )
    
    # 2. Party agreement heatmap
    party_agreement = calculate_party_agreement_matrix(df)
    
    fig.add_trace(
        go.Heatmap(
            z=party_agreement.values,
            x=party_agreement.columns,
            y=party_agreement.index,
            colorscale='RdYlBu',
            name='Agreement Rate'
        ),
        row=1, col=2
    )
    
    # 3. Coalition stability
    fig.add_trace(
        go.Scatter(
            x=stability_analysis['period'],
            y=stability_analysis['stability_score'],
            mode='lines+markers',
            name='Coalition Stability'
        ),
        row=2, col=1
    )
    
    # 4. Vote type distribution
    vote_dist = df['vote_category'].value_counts()
    
    fig.add_trace(
        go.Pie(
            labels=vote_dist.index,
            values=vote_dist.values,
            name='Vote Types'
        ),
        row=2, col=2
    )
    
    # 5. Seasonal patterns
    seasonal_data = df.groupby('session_period')['passed'].mean()
    
    fig.add_trace(
        go.Bar(
            x=seasonal_data.index,
            y=seasonal_data.values,
            name='Seasonal Pass Rates'
        ),
        row=3, col=1
    )
    
    # 6. Prediction accuracy (if model exists)
    if 'prediction_results' in globals():
        feature_importance = prediction_results['feature_importance']
        
        fig.add_trace(
            go.Bar(
                x=list(feature_importance.keys()),
                y=list(feature_importance.values()),
                name='Feature Importance'
            ),
            row=3, col=2
        )
    
    # Update layout
    fig.update_layout(
        title='Danish Parliament Voting Pattern Analysis Dashboard',
        showlegend=True,
        height=1000
    )
    
    # Save dashboard
    fig.write_html(save_path)
    return fig

def calculate_party_agreement_matrix(df):
    """Calculate agreement matrix between parties"""
    
    parties = df['party_id'].dropna().unique()
    agreement_matrix = pd.DataFrame(index=parties, columns=parties)
    
    for party1 in parties:
        for party2 in parties:
            if party1 == party2:
                agreement_matrix.loc[party1, party2] = 1.0
            else:
                # Calculate agreement rate between parties
                votes1 = df[df['party_id'] == party1]
                votes2 = df[df['party_id'] == party2]
                
                common_votes = pd.merge(
                    votes1[['vote_id', 'vote_type']], 
                    votes2[['vote_id', 'vote_type']], 
                    on='vote_id'
                )
                
                if len(common_votes) > 0:
                    agreement_rate = (
                        common_votes['vote_type_x'] == common_votes['vote_type_y']
                    ).mean()
                    agreement_matrix.loc[party1, party2] = agreement_rate
                else:
                    agreement_matrix.loc[party1, party2] = 0.5
    
    return agreement_matrix.astype(float)

# Create dashboard
dashboard = create_voting_dashboard(voting_df)
```

### 2. Automated Report Generation

```python
def generate_voting_analysis_report(df, output_file='voting_analysis_report.md'):
    """Generate comprehensive markdown report"""
    
    report = []
    report.append("# Danish Parliament Voting Pattern Analysis Report\n")
    report.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**Data Period:** {df['meeting_date'].min()} to {df['meeting_date'].max()}\n")
    report.append(f"**Total Voting Records:** {len(df):,}\n\n")
    
    # Executive Summary
    report.append("## Executive Summary\n")
    
    overall_pass_rate = df['passed'].mean()
    report.append(f"- **Overall Pass Rate:** {overall_pass_rate:.1%}\n")
    
    procedural_pass_rate = df[df['is_procedural']]['passed'].mean()
    substantive_pass_rate = df[~df['is_procedural']]['passed'].mean()
    
    report.append(f"- **Procedural Vote Pass Rate:** {procedural_pass_rate:.1%}\n")
    report.append(f"- **Substantive Vote Pass Rate:** {substantive_pass_rate:.1%}\n")
    
    unique_actors = df['actor_id'].nunique()
    report.append(f"- **Active Politicians:** {unique_actors}\n")
    
    unique_parties = df['party_id'].nunique()
    report.append(f"- **Political Parties Represented:** {unique_parties}\n\n")
    
    # Temporal Analysis
    report.append("## Temporal Patterns\n")
    
    yearly_summary = df.groupby('year').agg({
        'vote_id': 'count',
        'passed': 'mean',
        'is_procedural': 'mean'
    }).round(3)
    
    report.append("### Yearly Voting Summary\n")
    report.append(yearly_summary.to_markdown())
    report.append("\n\n")
    
    # Coalition Analysis
    report.append("## Coalition Analysis\n")
    
    if coalition_history:
        avg_coalition_count = np.mean([
            len(period['coalitions']) 
            for period in coalition_history
        ])
        report.append(f"- **Average Coalition Count:** {avg_coalition_count:.1f}\n")
        
        stability_mean = stability_analysis['stability_score'].mean()
        report.append(f"- **Average Coalition Stability:** {stability_mean:.3f}\n\n")
    
    # Top Findings
    report.append("## Key Findings\n")
    
    # Most cohesive party
    party_cohesion = df.groupby('party_id').apply(
        lambda x: calculate_average_party_cohesion(x)
    ).sort_values(ascending=False)
    
    if len(party_cohesion) > 0:
        most_cohesive_party = party_cohesion.index[0]
        report.append(f"- **Most Cohesive Party:** {most_cohesive_party} ({party_cohesion.iloc[0]:.3f})\n")
    
    # Anomalous voting patterns
    if 'anomaly_results' in globals():
        anomaly_count = anomaly_results['is_anomaly'].sum()
        report.append(f"- **Anomalous Voting Patterns Detected:** {anomaly_count}\n")
    
    # Prediction accuracy
    if 'prediction_results' in globals():
        accuracy = prediction_results['test_score']
        report.append(f"- **Vote Outcome Prediction Accuracy:** {accuracy:.1%}\n")
    
    report.append("\n")
    
    # Recommendations
    report.append("## Recommendations for Further Analysis\n")
    report.append("1. **Investigate Anomalous Patterns:** Deep dive into unusual voting behaviors\n")
    report.append("2. **Cross-reference Policy Topics:** Map voting patterns to specific policy areas\n")
    report.append("3. **Electoral Impact Analysis:** Correlate patterns with election outcomes\n")
    report.append("4. **International Comparisons:** Compare with other parliamentary systems\n")
    report.append("5. **Real-time Monitoring:** Implement live coalition tracking system\n\n")
    
    # Write report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    
    return ''.join(report)

# Generate report
analysis_report = generate_voting_analysis_report(voting_df)
print("Analysis report generated successfully!")
```

## Best Practices and Optimization

### 1. Performance Optimization

```python
def optimize_api_queries(batch_size=100, max_concurrent=5):
    """Optimize API queries for large-scale analysis"""
    
    import asyncio
    import aiohttp
    from concurrent.futures import ThreadPoolExecutor
    
    async def fetch_voting_batch(session, offset, limit):
        """Fetch voting data batch asynchronously"""
        url = f"{analyzer.base_url}/Afstemning"
        params = {
            '$expand': 'Stemme($expand=Aktør),Møde',
            '$skip': offset,
            '$top': limit,
            '$orderby': 'id desc'
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            return None
    
    async def fetch_all_voting_data(total_records=5000):
        """Fetch all voting data efficiently"""
        
        connector = aiohttp.TCPConnector(limit=max_concurrent)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(
            connector=connector, 
            timeout=timeout
        ) as session:
            
            tasks = []
            for offset in range(0, total_records, batch_size):
                task = fetch_voting_batch(session, offset, batch_size)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            all_data = []
            for result in results:
                if result and isinstance(result, dict) and 'value' in result:
                    all_data.extend(result['value'])
            
            return all_data
    
    # Run async data fetching
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        raw_data = loop.run_until_complete(fetch_all_voting_data())
        return analyzer.process_voting_data(raw_data)
    finally:
        loop.close()

# Use optimized fetching for large datasets
# optimized_df = optimize_api_queries()
```

### 2. Data Quality Validation

```python
def validate_voting_data_quality(df):
    """Comprehensive data quality validation"""
    
    quality_report = {
        'total_records': len(df),
        'missing_values': {},
        'data_consistency': {},
        'temporal_coverage': {},
        'relationship_integrity': {}
    }
    
    # Missing value analysis
    for column in df.columns:
        missing_count = df[column].isnull().sum()
        missing_percentage = (missing_count / len(df)) * 100
        quality_report['missing_values'][column] = {
            'count': missing_count,
            'percentage': missing_percentage
        }
    
    # Data consistency checks
    quality_report['data_consistency']['vote_outcome_consistency'] = (
        df['passed'].notna().sum() / len(df)
    )
    
    quality_report['data_consistency']['actor_party_consistency'] = (
        df.groupby('actor_id')['party_id'].nunique().max() == 1
    )
    
    # Temporal coverage
    date_range = df['meeting_date'].max() - df['meeting_date'].min()
    quality_report['temporal_coverage']['range_days'] = date_range.days
    quality_report['temporal_coverage']['earliest_date'] = str(df['meeting_date'].min())
    quality_report['temporal_coverage']['latest_date'] = str(df['meeting_date'].max())
    
    # Relationship integrity
    quality_report['relationship_integrity']['votes_with_actors'] = (
        df['actor_id'].notna().sum() / len(df)
    )
    
    quality_report['relationship_integrity']['votes_with_meetings'] = (
        df['meeting_id'].notna().sum() / len(df)
    )
    
    return quality_report

data_quality = validate_voting_data_quality(voting_df)
```

## Production Deployment

### 1. Automated Analysis Pipeline

```python
class VotingPatternPipeline:
    """Production-ready voting pattern analysis pipeline"""
    
    def __init__(self, config):
        self.config = config
        self.logger = self.setup_logging()
        
    def setup_logging(self):
        import logging
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def run_full_analysis(self):
        """Run complete voting pattern analysis"""
        
        try:
            self.logger.info("Starting voting pattern analysis...")
            
            # 1. Data Collection
            self.logger.info("Fetching voting data...")
            voting_data = self.fetch_data()
            
            # 2. Data Processing
            self.logger.info("Processing voting data...")
            processed_data = self.process_data(voting_data)
            
            # 3. Pattern Analysis
            self.logger.info("Analyzing voting patterns...")
            patterns = self.analyze_patterns(processed_data)
            
            # 4. Predictive Modeling
            self.logger.info("Building predictive models...")
            models = self.build_models(processed_data)
            
            # 5. Report Generation
            self.logger.info("Generating reports...")
            self.generate_reports(patterns, models)
            
            self.logger.info("Analysis completed successfully!")
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            raise
    
    def fetch_data(self):
        """Fetch voting data with error handling"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                analyzer = VotingPatternAnalyzer()
                return analyzer.fetch_voting_data(self.config.get('data_limit', 1000))
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
    
    def process_data(self, data):
        """Process and validate data"""
        processed = classify_vote_types(data)
        processed = analyze_electoral_cycles(processed)
        
        # Data quality validation
        quality_report = validate_voting_data_quality(processed)
        self.logger.info(f"Data quality score: {quality_report}")
        
        return processed
    
    def analyze_patterns(self, data):
        """Perform pattern analysis"""
        return {
            'temporal_patterns': analyze_temporal_patterns(data),
            'coalitions': detect_voting_coalitions(data),
            'voting_blocs': identify_voting_blocs(create_voting_similarity_matrix(data)[0]),
            'anomalies': detect_voting_anomalies(data)
        }
    
    def build_models(self, data):
        """Build predictive models"""
        return {
            'random_forest': build_voting_prediction_model(data),
            'neural_network': build_neural_network_predictor(data)
        }
    
    def generate_reports(self, patterns, models):
        """Generate analysis reports"""
        generate_voting_analysis_report(voting_df)
        create_voting_dashboard(voting_df)

# Configuration
pipeline_config = {
    'data_limit': 2000,
    'output_directory': './voting_analysis_results/',
    'report_formats': ['html', 'pdf', 'json']
}

# Run pipeline
pipeline = VotingPatternPipeline(pipeline_config)
# pipeline.run_full_analysis()
```

This comprehensive guide provides the foundation for sophisticated voting pattern analysis using the Danish Parliamentary OData API. The methodologies and code examples can be adapted for various research questions and scaled for production use.