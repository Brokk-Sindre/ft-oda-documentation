# Data Mining Parliamentary Data

This guide demonstrates advanced data mining techniques for analyzing Denmark's parliamentary data using the OData API. With 96,538+ cases, 18,139+ political actors, and comprehensive document archives, the API provides rich opportunities for extracting insights through machine learning and statistical analysis.

## Overview of Data Mining Opportunities

The Danish Parliamentary API offers several data mining opportunities:

- **Legislative Pattern Analysis**: Identify trends in bill types, success rates, and processing times
- **Voting Behavior Clustering**: Group politicians by voting patterns and party alignment
- **Document Classification**: Automatically categorize parliamentary documents by topic or type
- **Actor Influence Mining**: Discover key actors and their influence networks
- **Temporal Pattern Recognition**: Analyze how parliamentary processes evolve over time
- **Text Mining**: Extract insights from speeches, proposals, and committee reports

## Text Mining Parliamentary Documents

### Document Preprocessing Pipeline

```python
import pandas as pd
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from collections import Counter

class ParliamentaryTextProcessor:
    """Text preprocessing for Danish parliamentary documents"""
    
    def __init__(self):
        # Danish stopwords (extend with parliamentary-specific terms)
        self.danish_stopwords = set([
            'og', 'i', 'at', 'det', 'en', 'den', 'til', 'er', 'som', 'på',
            'de', 'med', 'han', 'af', 'for', 'ikke', 'der', 'var', 'mig',
            'sig', 'men', 'et', 'har', 'om', 'vi', 'min', 'havde', 'ham',
            'hun', 'nu', 'over', 'da', 'fra', 'du', 'ud', 'sin', 'dem',
            # Parliamentary-specific stopwords
            'folketinget', 'folketingsmedlem', 'minister', 'regering',
            'lovforslag', 'forslag', 'udvalg', 'møde', 'sag', 'punkt'
        ])
    
    def clean_text(self, text):
        """Clean and normalize Danish parliamentary text"""
        if pd.isna(text):
            return ""
        
        # Remove HTML tags and special characters
        text = re.sub(r'<[^>]+>', '', str(text))
        text = re.sub(r'[^\w\sæøåÆØÅ]', ' ', text)
        
        # Convert to lowercase and tokenize
        tokens = text.lower().split()
        
        # Remove stopwords and short tokens
        tokens = [t for t in tokens if len(t) > 2 and t not in self.danish_stopwords]
        
        return ' '.join(tokens)
    
    def extract_key_terms(self, documents, max_features=1000):
        """Extract key terms using TF-IDF"""
        cleaned_docs = [self.clean_text(doc) for doc in documents]
        
        vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.8
        )
        
        tfidf_matrix = vectorizer.fit_transform(cleaned_docs)
        feature_names = vectorizer.get_feature_names_out()
        
        return tfidf_matrix, feature_names, vectorizer

# Usage example
def analyze_document_topics():
    """Fetch and analyze parliamentary document topics"""
    
    # Fetch documents with text content
    url = "https://oda.ft.dk/api/Dokument"
    params = {
        '$filter': "resumé ne null and length(resumé) gt 50",
        '$select': 'id,titel,resumé,typeid,dato',
        '$top': 1000
    }
    
    response = requests.get(url, params=params)
    documents = response.json()['value']
    
    # Initialize text processor
    processor = ParliamentaryTextProcessor()
    
    # Extract document summaries
    texts = [doc.get('resumé', '') for doc in documents]
    titles = [doc.get('titel', '') for doc in documents]
    
    # Perform TF-IDF analysis
    tfidf_matrix, features, vectorizer = processor.extract_key_terms(texts)
    
    # Cluster documents by topic
    n_clusters = 10
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(tfidf_matrix)
    
    # Analyze cluster characteristics
    results = []
    for i in range(n_clusters):
        cluster_docs = [j for j, label in enumerate(cluster_labels) if label == i]
        cluster_center = kmeans.cluster_centers_[i]
        
        # Get top terms for this cluster
        top_indices = cluster_center.argsort()[-10:][::-1]
        top_terms = [features[idx] for idx in top_indices]
        
        results.append({
            'cluster': i,
            'doc_count': len(cluster_docs),
            'top_terms': top_terms,
            'sample_titles': [titles[j] for j in cluster_docs[:3]]
        })
    
    return results

# Example output analysis
topic_results = analyze_document_topics()
for result in topic_results:
    print(f"Cluster {result['cluster']}: {result['doc_count']} documents")
    print(f"Key terms: {', '.join(result['top_terms'][:5])}")
    print(f"Sample: {result['sample_titles'][0]}")
    print("---")
```

### Named Entity Recognition for Politicians

```python
import spacy
from collections import defaultdict
import networkx as nx

class PoliticalEntityExtractor:
    """Extract and analyze political entities from parliamentary text"""
    
    def __init__(self):
        # Load Danish language model (install with: python -m spacy download da_core_news_sm)
        try:
            self.nlp = spacy.load("da_core_news_sm")
        except OSError:
            # Fallback to English model
            self.nlp = spacy.load("en_core_web_sm")
    
    def extract_entities(self, text):
        """Extract named entities from parliamentary text"""
        doc = self.nlp(text)
        entities = {
            'PERSON': [],
            'ORG': [],
            'GPE': [],  # Geopolitical entities
            'LAW': [],
            'EVENT': []
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        
        return entities
    
    def build_cooccurrence_network(self, documents):
        """Build network of co-occurring political entities"""
        entity_cooccurrence = defaultdict(int)
        all_entities = set()
        
        for doc in documents:
            entities = self.extract_entities(doc)
            persons = set(entities['PERSON'])
            all_entities.update(persons)
            
            # Count co-occurrences
            for p1 in persons:
                for p2 in persons:
                    if p1 != p2:
                        pair = tuple(sorted([p1, p2]))
                        entity_cooccurrence[pair] += 1
        
        # Build network graph
        G = nx.Graph()
        G.add_nodes_from(all_entities)
        
        for (p1, p2), weight in entity_cooccurrence.items():
            if weight > 1:  # Only include frequently co-occurring entities
                G.add_edge(p1, p2, weight=weight)
        
        return G
    
    def analyze_political_discourse(self, case_id):
        """Analyze political discourse for a specific case"""
        
        # Fetch case documents
        url = f"https://oda.ft.dk/api/Sag({case_id})/Dokument"
        params = {'$select': 'id,titel,resumé,dokumenthtml'}
        
        response = requests.get(url, params=params)
        documents = response.json()['value']
        
        discourse_analysis = {
            'total_documents': len(documents),
            'key_entities': defaultdict(int),
            'sentiment_distribution': [],
            'topic_evolution': []
        }
        
        for doc in documents:
            # Extract text content
            text = doc.get('resumé', '') + ' ' + doc.get('dokumenthtml', '')
            
            if text.strip():
                entities = self.extract_entities(text)
                
                # Count entity mentions
                for entity_type, entity_list in entities.items():
                    for entity in entity_list:
                        discourse_analysis['key_entities'][entity] += 1
        
        return discourse_analysis

# Example usage
extractor = PoliticalEntityExtractor()

# Analyze specific case
case_analysis = extractor.analyze_political_discourse(20221)
print(f"Most mentioned entities:")
for entity, count in sorted(case_analysis['key_entities'].items(), 
                           key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {entity}: {count} mentions")
```

## Pattern Recognition in Legislative Processes

### Legislative Success Pattern Analysis

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import seaborn as sns

class LegislativePatternAnalyzer:
    """Analyze patterns in legislative success and failure"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_columns = []
    
    def fetch_legislative_data(self, limit=5000):
        """Fetch comprehensive case data for pattern analysis"""
        
        url = "https://oda.ft.dk/api/Sag"
        params = {
            '$select': 'id,titel,typeid,statusid,periode,afgørelsesdato,fremsatdato',
            '$expand': 'Sagstrin($select=titel,dato,typeid),SagAktør($select=aktørid,rolleid)',
            '$filter': 'statusid ne null and fremsatdato ne null',
            '$top': limit
        }
        
        response = requests.get(url, params=params)
        return response.json()['value']
    
    def engineer_features(self, cases):
        """Engineer features for legislative success prediction"""
        
        features_data = []
        
        for case in cases:
            # Basic case information
            features = {
                'case_id': case['id'],
                'case_type': case.get('typeid', 0),
                'period': case.get('periode', 0),
                'status': case.get('statusid', 0)
            }
            
            # Time-based features
            if case.get('fremsatdato') and case.get('afgørelsesdato'):
                from datetime import datetime
                start_date = datetime.fromisoformat(case['fremsatdato'].replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(case['afgørelsesdato'].replace('Z', '+00:00'))
                features['processing_days'] = (end_date - start_date).days
                features['start_month'] = start_date.month
                features['start_year'] = start_date.year
            else:
                features['processing_days'] = None
                features['start_month'] = None
                features['start_year'] = None
            
            # Sagstrin (case steps) analysis
            sagstrin = case.get('Sagstrin', [])
            features['num_steps'] = len(sagstrin)
            features['step_types'] = list(set([s.get('typeid') for s in sagstrin if s.get('typeid')]))
            features['num_unique_steps'] = len(features['step_types'])
            
            # Actor analysis
            actors = case.get('SagAktør', [])
            features['num_actors'] = len(actors)
            features['actor_roles'] = list(set([a.get('rolleid') for a in actors if a.get('rolleid')]))
            features['num_roles'] = len(features['actor_roles'])
            
            # Success indicator (status-based)
            # Adjust these status IDs based on actual API values
            success_statuses = [3, 4, 5]  # Example: approved/enacted statuses
            features['is_successful'] = 1 if case.get('statusid') in success_statuses else 0
            
            features_data.append(features)
        
        return pd.DataFrame(features_data)
    
    def train_success_predictor(self, df):
        """Train model to predict legislative success"""
        
        # Prepare features for modeling
        feature_cols = ['case_type', 'period', 'processing_days', 'start_month', 
                       'num_steps', 'num_unique_steps', 'num_actors', 'num_roles']
        
        # Handle missing values
        df_model = df[feature_cols + ['is_successful']].copy()
        df_model = df_model.dropna()
        
        X = df_model[feature_cols]
        y = df_model['is_successful']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Train model
        self.model.fit(X_train, y_train)
        self.feature_columns = feature_cols
        
        # Evaluate
        predictions = self.model.predict(X_test)
        print("Legislative Success Prediction Results:")
        print(classification_report(y_test, predictions))
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return feature_importance
    
    def analyze_temporal_patterns(self, df):
        """Analyze temporal patterns in legislative activity"""
        
        # Success rate by period
        period_success = df.groupby('period').agg({
            'is_successful': ['count', 'sum', 'mean']
        }).round(3)
        
        # Processing time analysis
        processing_stats = df.groupby('is_successful')['processing_days'].describe()
        
        # Seasonal patterns
        seasonal_patterns = df.groupby('start_month').agg({
            'is_successful': ['count', 'mean'],
            'processing_days': 'mean'
        }).round(3)
        
        return {
            'period_success': period_success,
            'processing_stats': processing_stats,
            'seasonal_patterns': seasonal_patterns
        }

# Usage example
analyzer = LegislativePatternAnalyzer()

# Fetch and analyze data
print("Fetching legislative data...")
cases = analyzer.fetch_legislative_data(limit=2000)
df = analyzer.engineer_features(cases)

print(f"Analyzing {len(df)} cases...")

# Train success predictor
feature_importance = analyzer.train_success_predictor(df)
print("\nMost Important Features for Legislative Success:")
print(feature_importance.head(10))

# Analyze temporal patterns
temporal_analysis = analyzer.analyze_temporal_patterns(df)
print("\nSeasonal Success Patterns (by month):")
print(temporal_analysis['seasonal_patterns'])
```

## Voting Behavior Analysis and Clustering

### Political Alignment Analysis

```python
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.metrics.pairwise import cosine_similarity

class VotingBehaviorAnalyzer:
    """Analyze voting patterns and political alignments"""
    
    def __init__(self):
        self.voting_matrix = None
        self.politician_clusters = None
    
    def fetch_voting_data(self, limit=10000):
        """Fetch comprehensive voting data"""
        
        url = "https://oda.ft.dk/api/Stemme"
        params = {
            '$select': 'id,aktørid,afstemningid,typeid',
            '$expand': 'Aktør($select=id,navn,typeid),Afstemning($select=id,sagid,titel)',
            '$top': limit
        }
        
        response = requests.get(url, params=params)
        return response.json()['value']
    
    def create_voting_matrix(self, votes):
        """Create politician x vote matrix"""
        
        # Extract voting data
        voting_records = []
        for vote in votes:
            if vote.get('Aktør') and vote.get('Afstemning'):
                voting_records.append({
                    'politiker_id': vote['aktørid'],
                    'politiker_navn': vote['Aktør']['navn'],
                    'afstemning_id': vote['afstemningid'],
                    'vote_type': vote['typeid'],
                    'sag_id': vote['Afstemning'].get('sagid')
                })
        
        df_votes = pd.DataFrame(voting_records)
        
        # Create pivot table (politiker x afstemning)
        voting_matrix = df_votes.pivot_table(
            index='politiker_id',
            columns='afstemning_id',
            values='vote_type',
            fill_value=0
        )
        
        # Add politician names for reference
        politician_names = df_votes.groupby('politiker_id')['politiker_navn'].first()
        
        return voting_matrix, politician_names
    
    def calculate_agreement_scores(self, voting_matrix):
        """Calculate pairwise agreement scores between politicians"""
        
        # Convert to binary voting (1 for yes/positive votes, 0 otherwise)
        binary_votes = (voting_matrix > 0).astype(int)
        
        # Calculate cosine similarity (agreement)
        agreement_matrix = cosine_similarity(binary_votes)
        agreement_df = pd.DataFrame(
            agreement_matrix,
            index=voting_matrix.index,
            columns=voting_matrix.index
        )
        
        return agreement_df
    
    def perform_political_clustering(self, voting_matrix, n_clusters=8):
        """Cluster politicians based on voting behavior"""
        
        # Prepare data for clustering
        binary_votes = (voting_matrix > 0).astype(int)
        
        # Hierarchical clustering
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            linkage='ward'
        )
        
        cluster_labels = clustering.fit_predict(binary_votes)
        
        # Create cluster analysis
        cluster_results = pd.DataFrame({
            'politiker_id': voting_matrix.index,
            'cluster': cluster_labels
        })
        
        return cluster_results, clustering
    
    def analyze_cluster_characteristics(self, voting_matrix, cluster_results, politician_names):
        """Analyze characteristics of each political cluster"""
        
        cluster_analysis = {}
        
        for cluster_id in sorted(cluster_results['cluster'].unique()):
            cluster_politicians = cluster_results[
                cluster_results['cluster'] == cluster_id
            ]['politiker_id'].tolist()
            
            # Get voting patterns for this cluster
            cluster_votes = voting_matrix.loc[cluster_politicians]
            
            # Calculate cluster statistics
            cluster_stats = {
                'size': len(cluster_politicians),
                'politicians': [politician_names.get(pid, f'ID:{pid}') 
                              for pid in cluster_politicians[:5]],  # Top 5 for display
                'avg_participation': (cluster_votes > 0).sum(axis=1).mean(),
                'most_common_positions': {}
            }
            
            # Find most characteristic votes for this cluster
            cluster_means = cluster_votes.mean(axis=0)
            other_means = voting_matrix.loc[
                ~voting_matrix.index.isin(cluster_politicians)
            ].mean(axis=0)
            
            # Votes where this cluster differs most from others
            vote_differences = (cluster_means - other_means).abs()
            distinctive_votes = vote_differences.nlargest(10)
            
            cluster_stats['distinctive_votes'] = distinctive_votes.to_dict()
            cluster_analysis[cluster_id] = cluster_stats
        
        return cluster_analysis
    
    def visualize_political_landscape(self, voting_matrix, cluster_results):
        """Create 2D visualization of political landscape using PCA"""
        
        # Prepare binary voting data
        binary_votes = (voting_matrix > 0).astype(int)
        
        # Apply PCA for 2D visualization
        pca = PCA(n_components=2)
        pca_coords = pca.fit_transform(binary_votes)
        
        # Create visualization dataframe
        viz_df = pd.DataFrame({
            'pc1': pca_coords[:, 0],
            'pc2': pca_coords[:, 1],
            'politiker_id': voting_matrix.index,
            'cluster': cluster_results.set_index('politiker_id').loc[voting_matrix.index, 'cluster']
        })
        
        # Plotting code (matplotlib/seaborn)
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(viz_df['pc1'], viz_df['pc2'], 
                            c=viz_df['cluster'], cmap='tab10', alpha=0.7)
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
        plt.title('Political Landscape: Voting Behavior Clusters')
        plt.colorbar(scatter, label='Cluster')
        
        return viz_df, pca

# Usage example
voting_analyzer = VotingBehaviorAnalyzer()

print("Fetching voting data...")
votes = voting_analyzer.fetch_voting_data(limit=5000)

print("Creating voting matrix...")
voting_matrix, politician_names = voting_analyzer.create_voting_matrix(votes)

print(f"Analyzing voting patterns for {len(voting_matrix)} politicians...")

# Perform clustering analysis
cluster_results, clustering_model = voting_analyzer.perform_political_clustering(voting_matrix)

# Analyze cluster characteristics
cluster_analysis = voting_analyzer.analyze_cluster_characteristics(
    voting_matrix, cluster_results, politician_names
)

print("Political Clusters Identified:")
for cluster_id, stats in cluster_analysis.items():
    print(f"\nCluster {cluster_id}: {stats['size']} politicians")
    print(f"Sample members: {', '.join(stats['politicians'][:3])}")
    print(f"Average participation: {stats['avg_participation']:.1f} votes")
```

## Document Classification and Categorization

### Automated Document Type Classification

```python
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
import joblib

class DocumentClassifier:
    """Classify parliamentary documents by type and topic"""
    
    def __init__(self):
        self.classifier = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        self.label_encoder = None
    
    def fetch_training_data(self, limit=3000):
        """Fetch documents with known types for training"""
        
        url = "https://oda.ft.dk/api/Dokument"
        params = {
            '$select': 'id,titel,resumé,typeid',
            '$filter': 'typeid ne null and resumé ne null and length(resumé) gt 50',
            '$top': limit
        }
        
        response = requests.get(url, params=params)
        documents = response.json()['value']
        
        # Prepare training data
        texts = []
        labels = []
        
        for doc in documents:
            # Combine title and summary for classification
            text = (doc.get('titel', '') + ' ' + doc.get('resumé', '')).strip()
            if text and doc.get('typeid'):
                texts.append(text)
                labels.append(doc['typeid'])
        
        return texts, labels
    
    def train_classifier(self, texts, labels):
        """Train document type classifier"""
        
        # Encode labels
        from sklearn.preprocessing import LabelEncoder
        self.label_encoder = LabelEncoder()
        encoded_labels = self.label_encoder.fit_transform(labels)
        
        # Train classifier
        self.classifier.fit(texts, encoded_labels)
        
        # Evaluate with cross-validation
        cv_scores = cross_val_score(self.classifier, texts, encoded_labels, cv=5)
        
        print(f"Document Classification Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Feature importance analysis
        feature_names = self.classifier.named_steps['tfidf'].get_feature_names_out()
        feature_weights = self.classifier.named_steps['classifier'].feature_log_prob_
        
        return cv_scores
    
    def classify_documents(self, texts):
        """Classify new documents"""
        if not self.label_encoder:
            raise ValueError("Classifier must be trained first")
        
        predictions = self.classifier.predict(texts)
        probabilities = self.classifier.predict_proba(texts)
        
        # Decode labels back to original types
        decoded_predictions = self.label_encoder.inverse_transform(predictions)
        
        results = []
        for i, text in enumerate(texts):
            results.append({
                'text': text[:100] + '...',
                'predicted_type': decoded_predictions[i],
                'confidence': probabilities[i].max(),
                'top_probabilities': dict(zip(
                    self.label_encoder.inverse_transform(
                        probabilities[i].argsort()[-3:][::-1]
                    ),
                    sorted(probabilities[i], reverse=True)[:3]
                ))
            })
        
        return results
    
    def topic_modeling_with_lda(self, texts, n_topics=10):
        """Perform topic modeling using Latent Dirichlet Allocation"""
        from sklearn.decomposition import LatentDirichletAllocation
        from sklearn.feature_extraction.text import CountVectorizer
        
        # Prepare text data
        processor = ParliamentaryTextProcessor()
        cleaned_texts = [processor.clean_text(text) for text in texts]
        
        # Vectorize for LDA
        vectorizer = CountVectorizer(
            max_features=1000,
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2)
        )
        
        doc_term_matrix = vectorizer.fit_transform(cleaned_texts)
        
        # Fit LDA model
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            max_iter=20,
            random_state=42
        )
        
        lda.fit(doc_term_matrix)
        
        # Extract topics
        feature_names = vectorizer.get_feature_names_out()
        topics = []
        
        for topic_idx, topic in enumerate(lda.components_):
            top_words_idx = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            topics.append({
                'topic_id': topic_idx,
                'keywords': top_words,
                'weight_sum': topic[top_words_idx].sum()
            })
        
        # Get document-topic distributions
        doc_topic_dist = lda.transform(doc_term_matrix)
        
        return topics, doc_topic_dist, vectorizer, lda

# Example usage
classifier = DocumentClassifier()

print("Fetching training data...")
texts, labels = classifier.fetch_training_data(limit=2000)

print(f"Training classifier on {len(texts)} documents...")
cv_scores = classifier.train_classifier(texts, labels)

# Topic modeling example
print("\nPerforming topic modeling...")
topics, doc_topics, vectorizer, lda_model = classifier.topic_modeling_with_lda(texts, n_topics=8)

print("Discovered Topics:")
for topic in topics:
    print(f"Topic {topic['topic_id']}: {', '.join(topic['keywords'][:5])}")

# Save trained models
joblib.dump(classifier, 'parliamentary_document_classifier.pkl')
joblib.dump(lda_model, 'parliamentary_topic_model.pkl')
```

## Temporal Pattern Mining

### Parliamentary Activity Cycle Analysis

```python
from datetime import datetime, timedelta
from scipy import signal
import numpy as np

class TemporalPatternMiner:
    """Mine temporal patterns in parliamentary activity"""
    
    def __init__(self):
        self.activity_data = None
        self.trend_analysis = None
    
    def fetch_temporal_data(self, start_year=2010, end_year=2023):
        """Fetch time-series data for analysis"""
        
        # Fetch cases by year
        all_data = []
        
        for year in range(start_year, end_year + 1):
            url = "https://oda.ft.dk/api/Sag"
            params = {
                '$select': 'id,titel,typeid,statusid,periode,fremsatdato,afgørelsesdato',
                '$filter': f"year(fremsatdato) eq {year}",
                '$top': 5000
            }
            
            try:
                response = requests.get(url, params=params)
                yearly_data = response.json()['value']
                
                for case in yearly_data:
                    if case.get('fremsatdato'):
                        case['year'] = year
                        all_data.append(case)
                
                print(f"Fetched {len(yearly_data)} cases for {year}")
                
            except Exception as e:
                print(f"Error fetching data for {year}: {e}")
        
        return all_data
    
    def analyze_activity_cycles(self, cases):
        """Analyze cyclical patterns in parliamentary activity"""
        
        # Convert to DataFrame
        df = pd.DataFrame(cases)
        df['fremsatdato'] = pd.to_datetime(df['fremsatdato'])
        df['month'] = df['fremsatdato'].dt.month
        df['quarter'] = df['fremsatdato'].dt.quarter
        df['week'] = df['fremsatdato'].dt.isocalendar().week
        
        # Monthly activity patterns
        monthly_activity = df.groupby(['year', 'month']).size().reset_index(name='case_count')
        monthly_avg = df.groupby('month').size().sort_index()
        
        # Quarterly patterns
        quarterly_activity = df.groupby(['year', 'quarter']).size().reset_index(name='case_count')
        quarterly_avg = df.groupby('quarter').size().sort_index()
        
        # Weekly patterns (within year)
        weekly_activity = df.groupby(['year', 'week']).size().reset_index(name='case_count')
        weekly_avg = df.groupby('week').size().sort_index()
        
        # Case type temporal distribution
        type_temporal = df.groupby(['typeid', 'month']).size().unstack(fill_value=0)
        
        return {
            'monthly_activity': monthly_activity,
            'monthly_avg': monthly_avg,
            'quarterly_activity': quarterly_activity,
            'quarterly_avg': quarterly_avg,
            'weekly_activity': weekly_activity,
            'weekly_avg': weekly_avg,
            'type_temporal': type_temporal
        }
    
    def detect_anomalies(self, activity_series, window_size=12):
        """Detect anomalies in parliamentary activity using statistical methods"""
        
        # Calculate rolling statistics
        rolling_mean = activity_series.rolling(window=window_size, center=True).mean()
        rolling_std = activity_series.rolling(window=window_size, center=True).std()
        
        # Define anomaly thresholds (2 standard deviations)
        upper_bound = rolling_mean + (2 * rolling_std)
        lower_bound = rolling_mean - (2 * rolling_std)
        
        # Identify anomalies
        anomalies = []
        for i, value in enumerate(activity_series):
            if pd.notna(upper_bound.iloc[i]) and pd.notna(lower_bound.iloc[i]):
                if value > upper_bound.iloc[i] or value < lower_bound.iloc[i]:
                    anomalies.append({
                        'index': i,
                        'value': value,
                        'expected_range': (lower_bound.iloc[i], upper_bound.iloc[i]),
                        'severity': abs(value - rolling_mean.iloc[i]) / rolling_std.iloc[i]
                    })
        
        return anomalies
    
    def election_impact_analysis(self, cases):
        """Analyze impact of elections on parliamentary activity"""
        
        # Danish election years (approximate)
        election_years = [2011, 2015, 2019, 2022]
        
        df = pd.DataFrame(cases)
        df['fremsatdato'] = pd.to_datetime(df['fremsatdato'])
        df['year'] = df['fremsatdato'].dt.year
        
        election_analysis = {}
        
        for election_year in election_years:
            # Activity in election year vs. non-election years
            election_activity = df[df['year'] == election_year].shape[0]
            
            # Pre-election period (6 months before)
            pre_election = df[
                (df['year'] == election_year) & 
                (df['fremsatdato'].dt.month <= 6)
            ].shape[0]
            
            # Post-election period (6 months after)
            post_election = df[
                (df['year'] == election_year) & 
                (df['fremsatdato'].dt.month > 6)
            ].shape[0]
            
            # Compare with adjacent non-election years
            prev_year_activity = df[df['year'] == election_year - 1].shape[0]
            next_year_activity = df[df['year'] == election_year + 1].shape[0]
            
            election_analysis[election_year] = {
                'total_activity': election_activity,
                'pre_election_activity': pre_election,
                'post_election_activity': post_election,
                'previous_year': prev_year_activity,
                'next_year': next_year_activity,
                'election_effect': (election_activity - ((prev_year_activity + next_year_activity) / 2))
            }
        
        return election_analysis
    
    def legislative_processing_time_trends(self, cases):
        """Analyze trends in legislative processing times"""
        
        df = pd.DataFrame(cases)
        
        # Filter cases with both start and end dates
        complete_cases = df[
            (df['fremsatdato'].notna()) & 
            (df['afgørelsesdato'].notna())
        ].copy()
        
        if complete_cases.empty:
            return None
        
        complete_cases['fremsatdato'] = pd.to_datetime(complete_cases['fremsatdato'])
        complete_cases['afgørelsesdato'] = pd.to_datetime(complete_cases['afgørelsesdato'])
        
        # Calculate processing time in days
        complete_cases['processing_days'] = (
            complete_cases['afgørelsesdato'] - complete_cases['fremsatdato']
        ).dt.days
        
        # Filter out negative processing times (data errors)
        complete_cases = complete_cases[complete_cases['processing_days'] >= 0]
        
        # Yearly processing time trends
        yearly_processing = complete_cases.groupby(
            complete_cases['fremsatdato'].dt.year
        )['processing_days'].agg(['mean', 'median', 'std', 'count']).round(2)
        
        # Processing time by case type
        type_processing = complete_cases.groupby('typeid')['processing_days'].agg([
            'mean', 'median', 'count'
        ]).round(2)
        
        # Seasonal processing patterns
        complete_cases['start_quarter'] = complete_cases['fremsatdato'].dt.quarter
        quarterly_processing = complete_cases.groupby('start_quarter')['processing_days'].agg([
            'mean', 'median'
        ]).round(2)
        
        return {
            'yearly_trends': yearly_processing,
            'type_patterns': type_processing,
            'seasonal_patterns': quarterly_processing,
            'overall_stats': complete_cases['processing_days'].describe()
        }

# Usage example
temporal_miner = TemporalPatternMiner()

print("Fetching temporal data...")
cases = temporal_miner.fetch_temporal_data(start_year=2015, end_year=2023)

print("Analyzing activity cycles...")
activity_patterns = temporal_miner.analyze_activity_cycles(cases)

print("Monthly Activity Averages:")
print(activity_patterns['monthly_avg'])

print("\nQuarterly Activity Averages:")
print(activity_patterns['quarterly_avg'])

# Anomaly detection
monthly_series = activity_patterns['monthly_activity'].set_index(['year', 'month'])['case_count']
anomalies = temporal_miner.detect_anomalies(monthly_series)

print(f"\nDetected {len(anomalies)} activity anomalies")
for anomaly in anomalies[:5]:  # Show top 5
    print(f"  Index {anomaly['index']}: {anomaly['value']} cases (severity: {anomaly['severity']:.2f})")

# Election impact analysis
election_impact = temporal_miner.election_impact_analysis(cases)
print("\nElection Year Impact Analysis:")
for year, impact in election_impact.items():
    print(f"  {year}: {impact['election_effect']:.0f} case difference vs. adjacent years")

# Processing time trends
processing_trends = temporal_miner.legislative_processing_time_trends(cases)
if processing_trends:
    print("\nAverage Processing Times by Year:")
    print(processing_trends['yearly_trends'][['mean', 'count']].tail())
```

## Actor Relationship Mining and Influence Analysis

### Political Network Analysis

```python
import networkx as nx
from scipy.stats import pearsonr
import community  # python-louvain package

class PoliticalNetworkAnalyzer:
    """Analyze relationships and influence networks among political actors"""
    
    def __init__(self):
        self.network = nx.Graph()
        self.actor_data = {}
    
    def fetch_actor_relationships(self, limit=5000):
        """Fetch actor relationship data"""
        
        # Fetch cases with multiple actors (collaboration indicators)
        url = "https://oda.ft.dk/api/Sag"
        params = {
            '$select': 'id,titel,typeid,periode',
            '$expand': 'SagAktør($select=aktørid,rolleid;$expand=Aktør($select=id,navn,typeid))',
            '$filter': 'SagAktør/$count gt 1',  # Cases with multiple actors
            '$top': limit
        }
        
        response = requests.get(url, params=params)
        cases = response.json()['value']
        
        # Build relationship network
        actor_collaborations = {}
        
        for case in cases:
            actors_in_case = []
            for sag_aktor in case.get('SagAktør', []):
                if sag_aktor.get('Aktør'):
                    actor_info = {
                        'id': sag_aktor['aktørid'],
                        'name': sag_aktor['Aktør']['navn'],
                        'type': sag_aktor['Aktør']['typeid'],
                        'role': sag_aktor['rolleid']
                    }
                    actors_in_case.append(actor_info)
                    
                    # Store actor data
                    if actor_info['id'] not in self.actor_data:
                        self.actor_data[actor_info['id']] = actor_info
            
            # Create collaboration edges between actors in same case
            for i, actor1 in enumerate(actors_in_case):
                for actor2 in actors_in_case[i+1:]:
                    pair = tuple(sorted([actor1['id'], actor2['id']]))
                    
                    if pair not in actor_collaborations:
                        actor_collaborations[pair] = {
                            'count': 0,
                            'case_types': set(),
                            'roles': set()
                        }
                    
                    actor_collaborations[pair]['count'] += 1
                    actor_collaborations[pair]['case_types'].add(case['typeid'])
                    actor_collaborations[pair]['roles'].add((actor1['role'], actor2['role']))
        
        return actor_collaborations
    
    def build_influence_network(self, collaborations, min_collaborations=2):
        """Build network graph with influence weights"""
        
        # Add nodes (actors)
        for actor_id, actor_info in self.actor_data.items():
            self.network.add_node(actor_id, **actor_info)
        
        # Add edges (collaborations) with weights
        for (actor1, actor2), collab_data in collaborations.items():
            if collab_data['count'] >= min_collaborations:
                self.network.add_edge(
                    actor1, actor2,
                    weight=collab_data['count'],
                    case_types=len(collab_data['case_types']),
                    role_combinations=len(collab_data['roles'])
                )
        
        # Calculate network metrics
        self.calculate_influence_metrics()
        
        return self.network
    
    def calculate_influence_metrics(self):
        """Calculate various influence and centrality metrics"""
        
        # Degree centrality (number of connections)
        degree_centrality = nx.degree_centrality(self.network)
        
        # Betweenness centrality (broker position)
        betweenness_centrality = nx.betweenness_centrality(self.network)
        
        # Closeness centrality (closeness to all other nodes)
        closeness_centrality = nx.closeness_centrality(self.network)
        
        # Eigenvector centrality (influence of connections)
        try:
            eigenvector_centrality = nx.eigenvector_centrality(self.network, max_iter=1000)
        except:
            eigenvector_centrality = {}
        
        # PageRank (influence propagation)
        pagerank = nx.pagerank(self.network)
        
        # Store metrics in node attributes
        for node in self.network.nodes():
            self.network.nodes[node].update({
                'degree_centrality': degree_centrality.get(node, 0),
                'betweenness_centrality': betweenness_centrality.get(node, 0),
                'closeness_centrality': closeness_centrality.get(node, 0),
                'eigenvector_centrality': eigenvector_centrality.get(node, 0),
                'pagerank': pagerank.get(node, 0)
            })
        
        return {
            'degree': degree_centrality,
            'betweenness': betweenness_centrality,
            'closeness': closeness_centrality,
            'eigenvector': eigenvector_centrality,
            'pagerank': pagerank
        }
    
    def detect_political_communities(self):
        """Detect communities/clusters in the political network"""
        
        # Use Louvain algorithm for community detection
        try:
            communities = community.best_partition(self.network)
            
            # Analyze community characteristics
            community_analysis = {}
            for node, comm_id in communities.items():
                if comm_id not in community_analysis:
                    community_analysis[comm_id] = {
                        'members': [],
                        'size': 0,
                        'avg_influence': 0,
                        'internal_density': 0
                    }
                
                community_analysis[comm_id]['members'].append({
                    'id': node,
                    'name': self.network.nodes[node].get('name', f'Actor {node}'),
                    'pagerank': self.network.nodes[node].get('pagerank', 0)
                })
                community_analysis[comm_id]['size'] += 1
            
            # Calculate community metrics
            for comm_id, comm_data in community_analysis.items():
                # Average influence (PageRank) in community
                avg_influence = np.mean([
                    member['pagerank'] for member in comm_data['members']
                ])
                community_analysis[comm_id]['avg_influence'] = avg_influence
                
                # Sort members by influence
                comm_data['members'].sort(key=lambda x: x['pagerank'], reverse=True)
            
            return communities, community_analysis
            
        except ImportError:
            print("Community detection requires python-louvain package")
            return None, None
    
    def identify_key_influencers(self, top_n=20):
        """Identify most influential actors across different metrics"""
        
        influence_rankings = {}
        metrics = ['pagerank', 'betweenness_centrality', 'eigenvector_centrality']
        
        for metric in metrics:
            ranking = sorted(
                self.network.nodes(data=True),
                key=lambda x: x[1].get(metric, 0),
                reverse=True
            )[:top_n]
            
            influence_rankings[metric] = [
                {
                    'id': node_id,
                    'name': data.get('name', f'Actor {node_id}'),
                    'score': data.get(metric, 0),
                    'type': data.get('type', 'Unknown')
                }
                for node_id, data in ranking
            ]
        
        # Combined influence score
        combined_scores = {}
        for node in self.network.nodes():
            score = (
                self.network.nodes[node].get('pagerank', 0) * 0.4 +
                self.network.nodes[node].get('betweenness_centrality', 0) * 0.3 +
                self.network.nodes[node].get('eigenvector_centrality', 0) * 0.3
            )
            combined_scores[node] = score
        
        # Top combined influencers
        top_combined = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        influence_rankings['combined'] = [
            {
                'id': node_id,
                'name': self.network.nodes[node_id].get('name', f'Actor {node_id}'),
                'score': score,
                'type': self.network.nodes[node_id].get('type', 'Unknown')
            }
            for node_id, score in top_combined
        ]
        
        return influence_rankings
    
    def analyze_influence_patterns(self):
        """Analyze patterns in political influence"""
        
        # Network statistics
        network_stats = {
            'total_actors': self.network.number_of_nodes(),
            'total_collaborations': self.network.number_of_edges(),
            'network_density': nx.density(self.network),
            'average_clustering': nx.average_clustering(self.network),
            'connected_components': nx.number_connected_components(self.network)
        }
        
        # Degree distribution
        degrees = [d for n, d in self.network.degree()]
        degree_stats = {
            'mean_degree': np.mean(degrees),
            'median_degree': np.median(degrees),
            'max_degree': max(degrees),
            'degree_distribution': np.histogram(degrees, bins=10)[0].tolist()
        }
        
        # Influence correlation analysis
        metrics = ['pagerank', 'betweenness_centrality', 'eigenvector_centrality']
        correlations = {}
        
        for i, metric1 in enumerate(metrics):
            for metric2 in metrics[i+1:]:
                values1 = [self.network.nodes[n].get(metric1, 0) for n in self.network.nodes()]
                values2 = [self.network.nodes[n].get(metric2, 0) for n in self.network.nodes()]
                
                if len(values1) > 1:
                    corr, p_value = pearsonr(values1, values2)
                    correlations[f"{metric1}_vs_{metric2}"] = {
                        'correlation': corr,
                        'p_value': p_value
                    }
        
        return {
            'network_stats': network_stats,
            'degree_stats': degree_stats,
            'influence_correlations': correlations
        }

# Usage example
network_analyzer = PoliticalNetworkAnalyzer()

print("Fetching actor relationship data...")
collaborations = network_analyzer.fetch_actor_relationships(limit=2000)

print(f"Building influence network from {len(collaborations)} collaborations...")
network = network_analyzer.build_influence_network(collaborations)

print(f"Network created with {network.number_of_nodes()} actors and {network.number_of_edges()} collaborations")

# Identify key influencers
influencers = network_analyzer.identify_key_influencers(top_n=15)

print("\nTop Influencers by PageRank:")
for influencer in influencers['pagerank'][:10]:
    print(f"  {influencer['name']}: {influencer['score']:.4f}")

# Community detection
communities, community_analysis = network_analyzer.detect_political_communities()
if communities:
    print(f"\nDetected {len(set(communities.values()))} political communities")
    for comm_id, analysis in list(community_analysis.items())[:5]:
        print(f"  Community {comm_id}: {analysis['size']} members, avg influence: {analysis['avg_influence']:.4f}")
        top_members = analysis['members'][:3]
        print(f"    Key members: {', '.join([m['name'] for m in top_members])}")

# Network analysis
patterns = network_analyzer.analyze_influence_patterns()
print(f"\nNetwork Analysis:")
print(f"  Density: {patterns['network_stats']['network_density']:.4f}")
print(f"  Average clustering: {patterns['network_stats']['average_clustering']:.4f}")
print(f"  Mean degree: {patterns['degree_stats']['mean_degree']:.1f}")
```

## Machine Learning Applications

### Parliamentary Outcome Prediction

```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import xgboost as xgb

class ParliamentaryMLPredictor:
    """Advanced ML applications for parliamentary data analysis"""
    
    def __init__(self):
        self.models = {
            'gradient_boosting': GradientBoostingClassifier(random_state=42),
            'xgboost': xgb.XGBClassifier(random_state=42),
            'neural_network': None  # Will be initialized if tensorflow available
        }
        self.feature_engineering_pipeline = None
    
    def fetch_comprehensive_data(self, limit=5000):
        """Fetch comprehensive case data with all related entities"""
        
        url = "https://oda.ft.dk/api/Sag"
        params = {
            '$select': 'id,titel,typeid,statusid,periode,fremsatdato,afgørelsesdato',
            '$expand': '''
                Sagstrin($select=titel,dato,typeid),
                SagAktør($select=aktørid,rolleid;$expand=Aktør($select=id,navn,typeid)),
                Dokument($select=id,titel,typeid,dato,resumé),
                Afstemning($select=id,titel,vedtaget)
            ''',
            '$top': limit
        }
        
        response = requests.get(url, params=params)
        return response.json()['value']
    
    def advanced_feature_engineering(self, cases):
        """Create sophisticated features for ML models"""
        
        features_data = []
        
        for case in cases:
            features = {
                'case_id': case['id'],
                'case_type': case.get('typeid', 0),
                'period': case.get('periode', 0),
                'status': case.get('statusid', 0)
            }
            
            # Time-based features
            if case.get('fremsatdato'):
                from datetime import datetime
                start_date = datetime.fromisoformat(case['fremsatdato'].replace('Z', '+00:00'))
                features.update({
                    'start_year': start_date.year,
                    'start_month': start_date.month,
                    'start_quarter': (start_date.month - 1) // 3 + 1,
                    'start_day_of_year': start_date.timetuple().tm_yday,
                    'start_weekday': start_date.weekday()
                })
                
                if case.get('afgørelsesdato'):
                    end_date = datetime.fromisoformat(case['afgørelsesdato'].replace('Z', '+00:00'))
                    features['processing_days'] = (end_date - start_date).days
                    features['processing_months'] = features['processing_days'] / 30.44
                else:
                    features['processing_days'] = None
                    features['processing_months'] = None
            
            # Complexity features from Sagstrin
            sagstrin = case.get('Sagstrin', [])
            if sagstrin:
                step_types = [s.get('typeid') for s in sagstrin if s.get('typeid')]
                features.update({
                    'num_steps': len(sagstrin),
                    'unique_step_types': len(set(step_types)),
                    'step_diversity': len(set(step_types)) / len(sagstrin) if sagstrin else 0,
                    'most_common_step': max(set(step_types), key=step_types.count) if step_types else 0
                })
                
                # Step timing patterns
                step_dates = [s.get('dato') for s in sagstrin if s.get('dato')]
                if len(step_dates) > 1:
                    step_dates_parsed = [datetime.fromisoformat(d.replace('Z', '+00:00')) for d in step_dates]
                    step_dates_parsed.sort()
                    
                    step_intervals = [(step_dates_parsed[i+1] - step_dates_parsed[i]).days 
                                    for i in range(len(step_dates_parsed)-1)]
                    
                    features.update({
                        'avg_step_interval': np.mean(step_intervals),
                        'median_step_interval': np.median(step_intervals),
                        'step_interval_variance': np.var(step_intervals)
                    })
            else:
                features.update({
                    'num_steps': 0, 'unique_step_types': 0, 'step_diversity': 0,
                    'most_common_step': 0, 'avg_step_interval': 0,
                    'median_step_interval': 0, 'step_interval_variance': 0
                })
            
            # Actor features
            actors = case.get('SagAktör', [])
            if actors:
                actor_types = [a.get('Aktør', {}).get('typeid') for a in actors if a.get('Aktør')]
                actor_roles = [a.get('rolleid') for a in actors if a.get('rolleid')]
                
                features.update({
                    'num_actors': len(actors),
                    'unique_actor_types': len(set(actor_types)),
                    'unique_actor_roles': len(set(actor_roles)),
                    'actor_diversity': len(set(actor_types)) / len(actors) if actors else 0,
                    'role_diversity': len(set(actor_roles)) / len(actors) if actors else 0
                })
            else:
                features.update({
                    'num_actors': 0, 'unique_actor_types': 0, 'unique_actor_roles': 0,
                    'actor_diversity': 0, 'role_diversity': 0
                })
            
            # Document features
            documents = case.get('Dokument', [])
            if documents:
                doc_types = [d.get('typeid') for d in documents if d.get('typeid')]
                doc_lengths = [len(d.get('resumé', '')) for d in documents if d.get('resumé')]
                
                features.update({
                    'num_documents': len(documents),
                    'unique_doc_types': len(set(doc_types)),
                    'avg_doc_length': np.mean(doc_lengths) if doc_lengths else 0,
                    'total_doc_length': sum(doc_lengths),
                    'doc_complexity': len(set(doc_types)) / len(documents) if documents else 0
                })
            else:
                features.update({
                    'num_documents': 0, 'unique_doc_types': 0, 'avg_doc_length': 0,
                    'total_doc_length': 0, 'doc_complexity': 0
                })
            
            # Voting features
            votes = case.get('Afstemning', [])
            if votes:
                vote_results = [v.get('vedtaget') for v in votes if v.get('vedtaget') is not None]
                features.update({
                    'num_votes': len(votes),
                    'votes_passed': sum(vote_results),
                    'votes_failed': len(vote_results) - sum(vote_results),
                    'vote_success_rate': sum(vote_results) / len(vote_results) if vote_results else 0
                })
            else:
                features.update({
                    'num_votes': 0, 'votes_passed': 0, 'votes_failed': 0, 'vote_success_rate': 0
                })
            
            # Target variable (success indicator)
            success_statuses = [3, 4, 5]  # Adjust based on actual status meanings
            features['is_successful'] = 1 if case.get('statusid') in success_statuses else 0
            
            features_data.append(features)
        
        return pd.DataFrame(features_data)
    
    def build_ensemble_model(self, df):
        """Build ensemble model for parliamentary outcome prediction"""
        
        # Prepare features
        feature_cols = [col for col in df.columns 
                       if col not in ['case_id', 'status', 'is_successful']]
        
        # Handle missing values and infinite values
        df_clean = df[feature_cols + ['is_successful']].copy()
        df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
        df_clean = df_clean.fillna(df_clean.median(numeric_only=True))
        
        X = df_clean[feature_cols]
        y = df_clean['is_successful']
        
        # Create preprocessing pipeline
        preprocessor = Pipeline([
            ('scaler', StandardScaler())
        ])
        
        # Grid search for best hyperparameters
        param_grids = {
            'gradient_boosting': {
                'n_estimators': [100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.2]
            },
            'xgboost': {
                'n_estimators': [100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.2]
            }
        }
        
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        best_models = {}
        
        for model_name, param_grid in param_grids.items():
            print(f"Training {model_name}...")
            
            grid_search = GridSearchCV(
                self.models[model_name],
                param_grid,
                cv=cv,
                scoring='f1',
                n_jobs=-1
            )
            
            grid_search.fit(X, y)
            best_models[model_name] = grid_search.best_estimator_
            
            print(f"Best {model_name} score: {grid_search.best_score_:.4f}")
            print(f"Best parameters: {grid_search.best_params_}")
        
        # Feature importance analysis
        feature_importance_analysis = {}
        for name, model in best_models.items():
            if hasattr(model, 'feature_importances_'):
                importance_df = pd.DataFrame({
                    'feature': feature_cols,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)
                
                feature_importance_analysis[name] = importance_df
                
                print(f"\nTop features for {name}:")
                print(importance_df.head(10))
        
        return best_models, feature_importance_analysis
    
    def parliamentary_trend_prediction(self, df, time_column='start_year'):
        """Predict future trends in parliamentary activity"""
        
        # Time series analysis of parliamentary activity
        trend_data = df.groupby(time_column).agg({
            'is_successful': ['count', 'sum', 'mean'],
            'processing_days': 'mean',
            'num_actors': 'mean',
            'num_documents': 'mean'
        }).round(4)
        
        # Flatten column names
        trend_data.columns = ['_'.join(col).strip() for col in trend_data.columns]
        trend_data = trend_data.reset_index()
        
        # Simple trend prediction using linear regression
        from sklearn.linear_model import LinearRegression
        
        predictions = {}
        
        for metric in ['is_successful_mean', 'processing_days_mean', 'num_actors_mean']:
            if metric in trend_data.columns:
                # Prepare data for prediction
                X = trend_data[[time_column]].values
                y = trend_data[metric].values
                
                # Remove any NaN values
                valid_indices = ~np.isnan(y)
                X_clean = X[valid_indices]
                y_clean = y[valid_indices]
                
                if len(X_clean) > 2:  # Need at least 3 points for prediction
                    model = LinearRegression()
                    model.fit(X_clean, y_clean)
                    
                    # Predict next 3 years
                    future_years = np.array([[X_clean.max() + i] for i in range(1, 4)])
                    future_predictions = model.predict(future_years)
                    
                    predictions[metric] = {
                        'trend_slope': model.coef_[0],
                        'current_value': y_clean[-1],
                        'predictions': dict(zip(
                            [int(x[0]) for x in future_years],
                            future_predictions
                        ))
                    }
        
        return trend_data, predictions

# Usage example
ml_predictor = ParliamentaryMLPredictor()

print("Fetching comprehensive data for ML analysis...")
cases = ml_predictor.fetch_comprehensive_data(limit=3000)

print("Engineering advanced features...")
df = ml_predictor.advanced_feature_engineering(cases)
print(f"Created {len(df.columns)} features for {len(df)} cases")

# Build ensemble models
print("Building ensemble models...")
best_models, feature_analysis = ml_predictor.build_ensemble_model(df)

# Trend prediction
print("Analyzing parliamentary trends...")
trend_data, trend_predictions = ml_predictor.parliamentary_trend_prediction(df)

print("\nParliamentary Trend Predictions:")
for metric, prediction in trend_predictions.items():
    print(f"\n{metric.replace('_', ' ').title()}:")
    print(f"  Current value: {prediction['current_value']:.4f}")
    print(f"  Trend slope: {prediction['trend_slope']:.6f} per year")
    for year, pred_value in prediction['predictions'].items():
        print(f"  {year}: {pred_value:.4f}")

# Save models
import joblib
for name, model in best_models.items():
    joblib.dump(model, f'parliamentary_{name}_model.pkl')
    
print("\nModels saved for future use!")
```

## Python Libraries and Tools

### Essential Data Mining Stack

```python
# Core data manipulation and analysis
import pandas as pd              # Data manipulation and analysis
import numpy as np               # Numerical computing
import requests                  # API interactions

# Machine Learning
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA, LatentDirichletAllocation
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, silhouette_score
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Natural Language Processing
import spacy                     # Advanced NLP (install da_core_news_sm for Danish)
import nltk                      # Natural Language Toolkit
from textblob import TextBlob    # Simple NLP tasks

# Network Analysis
import networkx as nx            # Network analysis and graph algorithms
import community                 # Community detection (python-louvain)

# Time Series and Statistical Analysis
from scipy import stats, signal  # Statistical functions
from statsmodels.tsa import seasonal_decompose  # Time series decomposition

# Visualization
import matplotlib.pyplot as plt  # Basic plotting
import seaborn as sns           # Statistical visualization
import plotly.graph_objects as go  # Interactive visualizations
import plotly.express as px     # Express plotting

# Advanced ML (optional)
import xgboost as xgb           # Gradient boosting
# import tensorflow as tf       # Deep learning (if needed)

# Utilities
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
import json
import joblib                   # Model persistence

class DataMiningToolkit:
    """Comprehensive toolkit for parliamentary data mining"""
    
    def __init__(self):
        self.initialize_nlp()
    
    def initialize_nlp(self):
        """Initialize NLP tools"""
        try:
            # Try to load Danish language model
            import spacy
            self.nlp = spacy.load("da_core_news_sm")
            print("Loaded Danish NLP model")
        except OSError:
            try:
                # Fallback to English
                self.nlp = spacy.load("en_core_web_sm")
                print("Loaded English NLP model (Danish not available)")
            except OSError:
                self.nlp = None
                print("No spaCy model available - install with:")
                print("python -m spacy download da_core_news_sm")
    
    @staticmethod
    def install_requirements():
        """Generate requirements.txt for parliamentary data mining"""
        
        requirements = """
# Core Data Science Stack
pandas>=1.5.0
numpy>=1.21.0
scipy>=1.9.0
requests>=2.28.0

# Machine Learning
scikit-learn>=1.1.0
xgboost>=1.6.0

# Natural Language Processing
spacy>=3.4.0
nltk>=3.7
textblob>=0.17.0

# Network Analysis
networkx>=2.8.0
python-louvain>=0.16.0

# Time Series Analysis
statsmodels>=0.13.0

# Visualization
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.10.0

# Utilities
joblib>=1.2.0
tqdm>=4.64.0

# Optional: Deep Learning
# tensorflow>=2.9.0
# torch>=1.12.0

# Danish Language Model (install separately)
# python -m spacy download da_core_news_sm
"""
        
        with open('requirements_datamining.txt', 'w', encoding='utf-8') as f:
            f.write(requirements.strip())
        
        print("Requirements saved to requirements_datamining.txt")
        print("Install with: pip install -r requirements_datamining.txt")
    
    def setup_danish_nlp(self):
        """Setup guide for Danish NLP"""
        
        setup_guide = """
# Danish NLP Setup Guide

## 1. Install spaCy Danish Model
```bash
python -m spacy download da_core_news_sm
```

## 2. Danish Stopwords
```python
danish_stopwords = {
    # Common words
    'og', 'i', 'at', 'det', 'en', 'den', 'til', 'er', 'som', 'på',
    'de', 'med', 'han', 'af', 'for', 'ikke', 'der', 'var', 'mig',
    'sig', 'men', 'et', 'har', 'om', 'vi', 'min', 'havde', 'ham',
    'hun', 'nu', 'over', 'da', 'fra', 'du', 'ud', 'sin', 'dem',
    
    # Parliamentary specific
    'folketinget', 'folketingsmedlem', 'minister', 'regering',
    'lovforslag', 'forslag', 'udvalg', 'møde', 'sag', 'punkt',
    'beslutningsforslag', 'redegørelse', 'beretning', 'samråd'
}
```

## 3. Danish Text Preprocessing
```python
def preprocess_danish_text(text):
    # Handle Danish characters properly
    text = text.lower()
    
    # Remove special characters but keep Danish letters
    text = re.sub(r'[^\\w\\s\\æøåÆØÅ]', ' ', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text
```
"""
        
        print(setup_guide)
    
    def create_analysis_pipeline(self):
        """Create reusable analysis pipeline template"""
        
        pipeline_template = '''
from parliamentary_datamining import DataMiningToolkit

class CustomParliamentaryAnalysis:
    """Template for custom parliamentary analysis"""
    
    def __init__(self):
        self.toolkit = DataMiningToolkit()
        self.data = None
        self.results = {}
    
    def fetch_data(self, query_params):
        """Fetch data from API"""
        # Implement your data fetching logic
        pass
    
    def preprocess_data(self):
        """Preprocess and clean data"""
        # Implement preprocessing
        pass
    
    def analyze(self):
        """Main analysis method"""
        # 1. Data fetching
        self.fetch_data()
        
        # 2. Preprocessing  
        self.preprocess_data()
        
        # 3. Analysis steps
        # Add your analysis methods here
        
        # 4. Results compilation
        self.compile_results()
    
    def compile_results(self):
        """Compile and save results"""
        # Save results, create visualizations, etc.
        pass
    
    def export_results(self, format='json'):
        """Export analysis results"""
        if format == 'json':
            import json
            with open('analysis_results.json', 'w') as f:
                json.dump(self.results, f, indent=2)
        elif format == 'csv':
            # Export to CSV
            pass

# Usage
analyzer = CustomParliamentaryAnalysis()
analyzer.analyze()
analyzer.export_results()
'''
        
        with open('analysis_pipeline_template.py', 'w', encoding='utf-8') as f:
            f.write(pipeline_template)
        
        print("Analysis pipeline template saved to analysis_pipeline_template.py")

# Initialize toolkit
toolkit = DataMiningToolkit()

# Generate requirements file
# toolkit.install_requirements()
```

## Performance Optimization for Large-Scale Operations

### Efficient Data Processing Strategies

```python
import concurrent.futures
from functools import lru_cache
import asyncio
import aiohttp
from tqdm import tqdm

class PerformanceOptimizer:
    """Performance optimization techniques for large-scale parliamentary data mining"""
    
    def __init__(self):
        self.cache_size = 1000
        self.batch_size = 100
        self.max_workers = 4
    
    @lru_cache(maxsize=1000)
    def cached_api_call(self, url_params_tuple):
        """Cache API calls to avoid redundant requests"""
        url, params = url_params_tuple
        response = requests.get(url, params=dict(params))
        return response.json()
    
    def batch_process_cases(self, case_ids, process_function, batch_size=None):
        """Process cases in batches to manage memory"""
        
        if batch_size is None:
            batch_size = self.batch_size
        
        results = []
        total_batches = (len(case_ids) + batch_size - 1) // batch_size
        
        for i in tqdm(range(0, len(case_ids), batch_size), 
                     desc="Processing batches", total=total_batches):
            batch = case_ids[i:i + batch_size]
            batch_results = process_function(batch)
            results.extend(batch_results)
            
            # Optional: garbage collection for large datasets
            if i % (batch_size * 10) == 0:
                import gc
                gc.collect()
        
        return results
    
    def parallel_data_fetching(self, urls_and_params, max_workers=None):
        """Fetch multiple API endpoints in parallel"""
        
        if max_workers is None:
            max_workers = self.max_workers
        
        def fetch_single(url_params):
            url, params = url_params
            try:
                response = requests.get(url, params=params, timeout=30)
                return response.json()
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                return None
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(fetch_single, up) for up in urls_and_params]
            
            for future in tqdm(concurrent.futures.as_completed(futures), 
                             total=len(futures), desc="Fetching data"):
                result = future.result()
                if result:
                    results.append(result)
        
        return results
    
    async def async_data_fetching(self, urls_and_params):
        """Asynchronous data fetching for better performance"""
        
        async def fetch_async(session, url, params):
            try:
                async with session.get(url, params=params) as response:
                    return await response.json()
            except Exception as e:
                print(f"Async error for {url}: {e}")
                return None
        
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_async(session, url, params) 
                    for url, params in urls_and_params]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
        # Filter out exceptions and None results
        return [r for r in results if r and not isinstance(r, Exception)]
    
    def optimize_dataframe_memory(self, df):
        """Optimize DataFrame memory usage"""
        
        # Downcast numeric types
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        # Convert object columns to category if beneficial
        for col in df.select_dtypes(include=['object']).columns:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.5:  # If less than 50% unique values
                df[col] = df[col].astype('category')
        
        return df
    
    def incremental_data_processing(self, data_source, chunk_size=1000):
        """Process data incrementally to handle large datasets"""
        
        class DataProcessor:
            def __init__(self):
                self.aggregated_results = {
                    'total_processed': 0,
                    'running_statistics': {},
                    'sample_data': []
                }
            
            def process_chunk(self, chunk):
                # Process individual chunk
                chunk_results = {
                    'count': len(chunk),
                    'average_processing_time': np.mean([
                        case.get('processing_days', 0) for case in chunk
                        if case.get('processing_days')
                    ])
                }
                
                # Update aggregated results
                self.aggregated_results['total_processed'] += chunk_results['count']
                
                return chunk_results
            
            def finalize_processing(self):
                # Final calculations and cleanup
                return self.aggregated_results
        
        processor = DataProcessor()
        
        # Process in chunks
        for i in range(0, len(data_source), chunk_size):
            chunk = data_source[i:i + chunk_size]
            processor.process_chunk(chunk)
        
        return processor.finalize_processing()
    
    def create_efficient_ml_pipeline(self, feature_columns, target_column):
        """Create memory-efficient ML pipeline for large datasets"""
        
        from sklearn.pipeline import Pipeline
        from sklearn.compose import ColumnTransformer
        from sklearn.preprocessing import StandardScaler, OneHotEncoder
        from sklearn.feature_selection import SelectKBest, f_classif
        from sklearn.ensemble import RandomForestClassifier
        
        # Identify numeric and categorical columns
        numeric_features = []
        categorical_features = []
        
        for col in feature_columns:
            # This is a simplified check - adjust based on your data
            if col.endswith('_id') or col in ['typeid', 'statusid']:
                categorical_features.append(col)
            else:
                numeric_features.append(col)
        
        # Create preprocessing pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse=False), 
                 categorical_features)
            ]
        )
        
        # Create full pipeline with feature selection
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('feature_selection', SelectKBest(f_classif, k=50)),  # Select top 50 features
            ('classifier', RandomForestClassifier(
                n_estimators=100,
                max_depth=10,  # Limit depth for memory efficiency
                min_samples_split=10,  # Require more samples for splits
                n_jobs=-1
            ))
        ])
        
        return pipeline
    
    def monitor_performance(self, func):
        """Decorator to monitor function performance"""
        
        def wrapper(*args, **kwargs):
            import time
            import psutil
            import os
            
            # Get initial memory usage
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Time the function
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            print(f"Function {func.__name__} Performance:")
            print(f"  Execution time: {end_time - start_time:.2f} seconds")
            print(f"  Memory usage: {initial_memory:.1f} MB -> {final_memory:.1f} MB")
            print(f"  Memory change: {final_memory - initial_memory:.1f} MB")
            
            return result
        
        return wrapper

# Usage examples for performance optimization

def efficient_large_scale_analysis():
    """Example of efficient large-scale analysis"""
    
    optimizer = PerformanceOptimizer()
    
    # 1. Efficient data fetching
    print("Step 1: Efficient data fetching")
    
    # Prepare API calls
    base_url = "https://oda.ft.dk/api/Sag"
    urls_and_params = []
    
    # Fetch data for multiple years in parallel
    for year in range(2010, 2024):
        params = {
            '$filter': f"year(fremsatdato) eq {year}",
            '$select': 'id,titel,typeid,statusid,periode,fremsatdato',
            '$top': 1000
        }
        urls_and_params.append((base_url, params))
    
    # Parallel fetching
    all_data = optimizer.parallel_data_fetching(urls_and_params)
    
    # 2. Memory-efficient data processing
    print("Step 2: Memory-efficient processing")
    
    # Flatten the data
    all_cases = []
    for year_data in all_data:
        if year_data and 'value' in year_data:
            all_cases.extend(year_data['value'])
    
    # Convert to DataFrame and optimize memory
    df = pd.DataFrame(all_cases)
    df = optimizer.optimize_dataframe_memory(df)
    
    print(f"Processed {len(df)} cases with optimized memory usage")
    
    # 3. Batch processing for analysis
    print("Step 3: Batch processing")
    
    def analyze_batch(batch_cases):
        """Analyze a batch of cases"""
        batch_df = pd.DataFrame(batch_cases)
        
        # Perform batch analysis
        analysis_results = {
            'total_cases': len(batch_df),
            'case_types': batch_df['typeid'].value_counts().to_dict(),
            'status_distribution': batch_df['statusid'].value_counts().to_dict()
        }
        
        return analysis_results
    
    # Process in batches
    batch_results = optimizer.batch_process_cases(
        all_cases, 
        lambda batch: [analyze_batch(batch)],
        batch_size=500
    )
    
    print(f"Completed batch analysis with {len(batch_results)} batches")
    
    return df, batch_results

# Example usage with performance monitoring
optimizer = PerformanceOptimizer()

@optimizer.monitor_performance
def example_analysis():
    """Example analysis with performance monitoring"""
    # Simulate data processing
    data = list(range(10000))
    processed = [x * 2 for x in data]
    return len(processed)

# Run the monitored function
result = example_analysis()

# Tips for optimization
optimization_tips = """
# Performance Optimization Tips for Parliamentary Data Mining

## 1. Data Fetching
- Use parallel/async requests for multiple API calls
- Implement caching for repeated queries
- Use OData $select to fetch only needed fields
- Batch API calls when possible

## 2. Memory Management
- Process data in chunks for large datasets
- Use appropriate data types (category for strings with few unique values)
- Clear unused variables with `del variable_name`
- Use generators for large data iterations

## 3. Computational Efficiency
- Vectorize operations with pandas/numpy
- Use appropriate algorithms (e.g., approximate algorithms for very large data)
- Consider sampling for exploratory analysis
- Use multi-processing for CPU-intensive tasks

## 4. Database/Storage Optimization
- Consider using databases (SQLite, PostgreSQL) for large datasets
- Use parquet format for efficient storage
- Index frequently queried columns
- Implement data partitioning strategies

## 5. Machine Learning Optimization
- Use feature selection to reduce dimensionality
- Consider online/incremental learning algorithms
- Use cross-validation strategically
- Implement early stopping for iterative algorithms

## Example: Efficient API Query
```python
# Instead of multiple small queries
for case_id in case_ids:
    response = requests.get(f"api/Sag({case_id})")

# Use batch query with expansion
case_ids_str = ','.join(map(str, case_ids[:50]))  # Batch of 50
response = requests.get(f"api/Sag", params={
    '$filter': f"id in ({case_ids_str})",
    '$expand': 'SagAktør,Dokument,Afstemning'
})
```
"""

print(optimization_tips)
```

## Conclusion

This comprehensive guide provides the foundation for advanced data mining on Denmark's parliamentary data. The techniques cover:

1. **Text Mining**: Extract insights from Danish parliamentary documents using NLP
2. **Pattern Recognition**: Identify trends in legislative processes and outcomes
3. **Voting Analysis**: Cluster politicians and analyze political alignments
4. **Document Classification**: Automatically categorize parliamentary documents
5. **Temporal Mining**: Discover cyclical patterns and temporal trends
6. **Network Analysis**: Map political relationships and influence networks
7. **Machine Learning**: Predict legislative outcomes and parliamentary trends
8. **Performance Optimization**: Handle large-scale data efficiently

The provided code examples use production-ready techniques with proper error handling, memory management, and scalability considerations. All examples are designed to work with the actual Danish Parliamentary API structure and data characteristics.

For researchers and analysts working with parliamentary data, these techniques provide a solid foundation for extracting meaningful insights from the rich dataset available through the OData API.

Remember to:
- Always respect API rate limits and terms of service
- Validate your findings with domain experts
- Consider the political and cultural context of Danish parliamentary processes
- Use appropriate statistical methods for your research questions
- Document your methodology for reproducibility

The combination of these techniques enables comprehensive analysis of democratic processes, legislative effectiveness, and political behavior patterns in the Danish Parliament.