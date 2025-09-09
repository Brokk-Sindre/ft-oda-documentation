# Document Flow Tracking

Master the complete legislative document lifecycle through the Danish Parliament API's comprehensive document tracking system with 28 document types and detailed relationship mapping.

## Overview

The Danish Parliament API provides exhaustive document tracking capabilities through interconnected entities that map every document's role in the legislative process:

- **28 Document Types** - From proposals to final laws
- **Document-Actor Relationships** - Who creates, receives, and processes documents
- **Case-Document Links** - How documents connect to legislative cases
- **File Downloads** - Direct access to PDF documents
- **Document Status Tracking** - Current state in processing workflow

## Core Document Architecture

### Key Entities for Document Tracking
```
Dokument (Documents) ←→ SagDokument ←→ Sag (Cases)
     ↓                      ↓
DokumentAktør ←→ Aktør    SagDokumentRolle
     ↓                      ↓
DokumentAktørRolle    (Document role in case)
     ↓
Fil (Files) - PDF downloads
```

### Essential Document Fields
- **titel** - Document title and description
- **dato** - Document creation/submission date
- **typeid** - Document type (1-28 classification)
- **statusid** - Current processing status
- **dokumenturl** - Direct link to official document
- **filurl** - PDF download link (via Fil entity)
- **opdateringsdato** - Last modification timestamp

## Implementation Framework

### Comprehensive Document Tracker

```python
import requests
import urllib.parse
from datetime import datetime, timedelta
from collections import defaultdict
import os

class DocumentFlowTracker:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api/"
        self.document_types = {}
        self.document_statuses = {}
        
    def load_document_classifications(self):
        """Load all document types and statuses for reference"""
        
        # Load document types (28 types)
        url = f"{self.base_url}Dokumenttype"
        response = requests.get(url)
        
        if response.json().get('value'):
            for doc_type in response.json()['value']:
                self.document_types[doc_type['id']] = doc_type['type']
        
        # Load document statuses
        url = f"{self.base_url}Dokumentstatus"
        response = requests.get(url)
        
        if response.json().get('value'):
            for status in response.json()['value']:
                self.document_statuses[status['id']] = status['status']
    
    def trace_complete_document_lifecycle(self, case_id):
        """Trace all documents associated with a legislative case"""
        
        params = {
            '$expand': 'Dokument/Dokumenttype,Dokument/Dokumentstatus,Dokument/Fil,SagDokumentRolle',
            '$filter': f'sagid eq {case_id}',
            '$orderby': 'Dokument/dato asc'
        }
        
        url = f"{self.base_url}SagDokument?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        document_lifecycle = []
        
        if response.json().get('value'):
            for doc_relation in response.json()['value']:
                if 'Dokument' in doc_relation and doc_relation['Dokument']:
                    doc = doc_relation['Dokument']
                    
                    document_info = {
                        'document_id': doc['id'],
                        'title': doc.get('titel', 'Unknown'),
                        'date': doc.get('dato', ''),
                        'type': doc.get('Dokumenttype', {}).get('type', 'Unknown'),
                        'type_id': doc.get('typeid', 0),
                        'status': doc.get('Dokumentstatus', {}).get('status', 'Unknown'),
                        'status_id': doc.get('statusid', 0),
                        'role_in_case': doc_relation.get('SagDokumentRolle', {}).get('rolle', 'Unknown'),
                        'official_url': doc.get('dokumenturl', ''),
                        'pdf_files': [],
                        'creation_date': doc.get('dato', ''),
                        'last_updated': doc.get('opdateringsdato', ''),
                        'page_count': doc.get('sidetal', 0),
                        'actors_involved': []
                    }
                    
                    # Get associated PDF files
                    if 'Fil' in doc and doc['Fil']:
                        for file_info in doc['Fil']:
                            document_info['pdf_files'].append({
                                'file_id': file_info['id'],
                                'title': file_info.get('titel', 'Unknown'),
                                'url': file_info.get('filurl', ''),
                                'format': file_info.get('format', 'Unknown'),
                                'size_kb': file_info.get('størrelse', 0)
                            })
                    
                    document_lifecycle.append(document_info)
        
        return document_lifecycle
    
    def map_document_actor_relationships(self, document_id):
        """Map all actors involved with a specific document"""
        
        params = {
            '$expand': 'Aktör,DokumentAktørRolle',
            '$filter': f'dokumentid eq {document_id}'
        }
        
        url = f"{self.base_url}DokumentAktör?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        actor_relationships = []
        
        if response.json().get('value'):
            for relation in response.json()['value']:
                if 'Aktör' in relation and relation['Aktör']:
                    actor_info = {
                        'actor_id': relation['aktørid'],
                        'actor_name': relation['Aktör'].get('navn', 'Unknown'),
                        'actor_type': relation['Aktör'].get('typeid', 0),
                        'role': relation.get('DokumentAktörRolle', {}).get('rolle', 'Unknown'),
                        'role_id': relation.get('rolleid', 0),
                        'relationship_date': relation.get('opdateringsdato', '')
                    }
                    
                    actor_relationships.append(actor_info)
        
        return actor_relationships
    
    def analyze_document_flow_patterns(self, case_type_filter=None, months_back=12):
        """Analyze common document flow patterns in legislative process"""
        
        cutoff_date = (datetime.now() - timedelta(days=months_back*30)).strftime('%Y-%m-%dT00:00:00')
        
        params = {
            '$expand': 'Sag/Sagstype,Dokument/Dokumenttype,SagDokumentRolle',
            '$filter': f'opdateringsdato gt datetime\'{cutoff_date}\'',
            '$orderby': 'Dokument/dato asc',
            '$top': 2000
        }
        
        if case_type_filter:
            params['$filter'] += f' and Sag/typeid eq {case_type_filter}'
        
        url = f"{self.base_url}SagDokument?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        flow_patterns = {
            'document_type_sequences': defaultdict(int),
            'type_frequency': defaultdict(int),
            'role_patterns': defaultdict(int),
            'timing_analysis': defaultdict(list),
            'case_type_patterns': defaultdict(lambda: defaultdict(int))
        }
        
        if response.json().get('value'):
            # Group documents by case for sequence analysis
            case_documents = defaultdict(list)
            
            for doc_relation in response.json()['value']:
                case_id = doc_relation['sagid']
                
                if 'Dokument' in doc_relation and doc_relation['Dokument']:
                    doc_info = {
                        'type': doc_relation['Dokument'].get('Dokumenttype', {}).get('type', 'Unknown'),
                        'type_id': doc_relation['Dokument'].get('typeid', 0),
                        'date': doc_relation['Dokument'].get('dato', ''),
                        'role': doc_relation.get('SagDokumentRolle', {}).get('rolle', 'Unknown'),
                        'case_type': doc_relation.get('Sag', {}).get('Sagstype', {}).get('type', 'Unknown') if doc_relation.get('Sag') else 'Unknown'
                    }
                    
                    case_documents[case_id].append(doc_info)
                    
                    # Track individual document statistics
                    flow_patterns['type_frequency'][doc_info['type']] += 1
                    flow_patterns['role_patterns'][doc_info['role']] += 1
                    flow_patterns['case_type_patterns'][doc_info['case_type']][doc_info['type']] += 1
            
            # Analyze document sequences within cases
            for case_id, documents in case_documents.items():
                if len(documents) > 1:
                    # Sort by date
                    sorted_docs = sorted(documents, key=lambda x: x['date'] or '1900-01-01')
                    
                    # Create sequence of document types
                    type_sequence = ' → '.join([doc['type'] for doc in sorted_docs])
                    flow_patterns['document_type_sequences'][type_sequence] += 1
                    
                    # Analyze timing between documents
                    for i in range(1, len(sorted_docs)):
                        try:
                            prev_date = datetime.fromisoformat(sorted_docs[i-1]['date'] or '1900-01-01')
                            curr_date = datetime.fromisoformat(sorted_docs[i]['date'] or '1900-01-01')
                            days_between = (curr_date - prev_date).days
                            
                            transition_key = f"{sorted_docs[i-1]['type']} → {sorted_docs[i]['type']}"
                            flow_patterns['timing_analysis'][transition_key].append(days_between)
                        except:
                            pass  # Skip invalid dates
        
        return flow_patterns
```

### Advanced Document Analytics

```python
class AdvancedDocumentAnalyzer(DocumentFlowTracker):
    
    def track_document_amendments_and_revisions(self, base_document_id):
        """Track amendments and revisions to a base document"""
        
        # Get base document information
        params = {
            '$expand': 'Dokumenttype,Dokumentstatus',
            '$filter': f'id eq {base_document_id}'
        }
        
        url = f"{self.base_url}Dokument?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        base_doc_info = None
        if response.json().get('value'):
            base_doc_info = response.json()['value'][0]
        
        # Find related documents (amendments, revisions)
        revision_tracking = {
            'base_document': base_doc_info,
            'amendments': [],
            'revisions': [],
            'related_documents': [],
            'revision_timeline': []
        }
        
        if base_doc_info:
            base_title = base_doc_info.get('titel', '')
            
            # Search for documents with similar titles or explicit amendment references
            params = {
                '$expand': 'Dokumenttype,Dokumentstatus',
                '$filter': f"substringof('ændring', titel) and substringof('{base_title[:20]}', titel)",
                '$orderby': 'dato asc',
                '$top': 50
            }
            
            url = f"{self.base_url}Dokument?" + urllib.parse.urlencode(params)
            response = requests.get(url)
            
            if response.json().get('value'):
                for related_doc in response.json()['value']:
                    if related_doc['id'] != base_document_id:
                        doc_type = related_doc.get('Dokumenttype', {}).get('type', '').lower()
                        
                        if 'ændring' in doc_type or 'amendment' in doc_type:
                            revision_tracking['amendments'].append(related_doc)
                        elif 'revision' in doc_type or 'rettelse' in doc_type:
                            revision_tracking['revisions'].append(related_doc)
                        else:
                            revision_tracking['related_documents'].append(related_doc)
                        
                        # Add to timeline
                        revision_tracking['revision_timeline'].append({
                            'date': related_doc.get('dato', ''),
                            'type': doc_type,
                            'title': related_doc.get('titel', ''),
                            'document_id': related_doc['id']
                        })
            
            # Sort timeline by date
            revision_tracking['revision_timeline'].sort(key=lambda x: x['date'] or '1900-01-01')
        
        return revision_tracking
    
    def analyze_document_processing_efficiency(self, document_type_filter=None):
        """Analyze efficiency of document processing workflows"""
        
        params = {
            '$expand': 'Dokumenttype,Dokumentstatus',
            '$orderby': 'opdateringsdato desc',
            '$top': 1000
        }
        
        if document_type_filter:
            params['$filter'] = f'typeid eq {document_type_filter}'
        
        url = f"{self.base_url}Dokument?" + urllib.parse.urlencode(params)
        response = requests.get(url)
        
        efficiency_analysis = {
            'total_documents_analyzed': 0,
            'processing_times': {
                'average_days': 0,
                'median_days': 0,
                'distribution': defaultdict(int)
            },
            'status_bottlenecks': defaultdict(list),
            'type_efficiency': defaultdict(list)
        }
        
        processing_times = []
        
        if response.json().get('value'):
            documents = response.json()['value']
            efficiency_analysis['total_documents_analyzed'] = len(documents)
            
            for doc in documents:
                # Calculate processing time (creation to last update)
                try:
                    creation_date = datetime.fromisoformat(doc.get('dato', '1900-01-01'))
                    update_date = datetime.fromisoformat(doc.get('opdateringsdato', '1900-01-01'))
                    processing_days = (update_date - creation_date).days
                    
                    if processing_days >= 0:  # Valid time span
                        processing_times.append(processing_days)
                        
                        doc_type = doc.get('Dokumenttype', {}).get('type', 'Unknown')
                        efficiency_analysis['type_efficiency'][doc_type].append(processing_days)
                        
                        # Categorize processing time
                        if processing_days <= 7:
                            efficiency_analysis['processing_times']['distribution']['1-7 days'] += 1
                        elif processing_days <= 30:
                            efficiency_analysis['processing_times']['distribution']['8-30 days'] += 1
                        elif processing_days <= 90:
                            efficiency_analysis['processing_times']['distribution']['31-90 days'] += 1
                        else:
                            efficiency_analysis['processing_times']['distribution']['90+ days'] += 1
                            
                            # Flag as potential bottleneck
                            status = doc.get('Dokumentstatus', {}).get('status', 'Unknown')
                            efficiency_analysis['status_bottlenecks'][status].append({
                                'document_id': doc['id'],
                                'title': doc.get('titel', 'Unknown'),
                                'processing_days': processing_days
                            })
                            
                except:
                    pass  # Skip documents with invalid dates
            
            # Calculate averages
            if processing_times:
                efficiency_analysis['processing_times']['average_days'] = sum(processing_times) / len(processing_times)
                efficiency_analysis['processing_times']['median_days'] = sorted(processing_times)[len(processing_times)//2]
        
        return efficiency_analysis
    
    def identify_document_dependency_chains(self, case_id):
        """Identify chains of document dependencies within a case"""
        
        documents = self.trace_complete_document_lifecycle(case_id)
        
        dependency_analysis = {
            'case_id': case_id,
            'total_documents': len(documents),
            'dependency_chains': [],
            'critical_path': [],
            'parallel_tracks': []
        }
        
        if documents:
            # Sort documents by date to understand sequence
            sorted_docs = sorted(documents, key=lambda x: x['date'] or '1900-01-01')
            
            # Identify potential dependencies based on document types and timing
            type_dependencies = {
                'Lovforslag': ['Betænkning', 'Ændringsforslag'],
                'Forslag til folketingsbeslutning': ['Betænkning'],
                'Spørgsmål': ['Svar'],
                'Redegørelse': ['Betænkning', 'Beslutning']
            }
            
            dependency_chains = []
            current_chain = []
            
            for i, doc in enumerate(sorted_docs):
                doc_type = doc['type']
                
                # Check if this document type depends on previous types
                if doc_type in type_dependencies:
                    # Look for prerequisite documents
                    prerequisites = []
                    for prev_doc in sorted_docs[:i]:
                        if prev_doc['type'] in type_dependencies.get(doc_type, []):
                            prerequisites.append(prev_doc)
                    
                    if prerequisites:
                        dependency_chains.append({
                            'dependent_document': doc,
                            'prerequisites': prerequisites,
                            'chain_length': len(prerequisites) + 1
                        })
            
            dependency_analysis['dependency_chains'] = dependency_chains
            
            # Identify critical path (longest dependency chain)
            if dependency_chains:
                critical_chain = max(dependency_chains, key=lambda x: x['chain_length'])
                dependency_analysis['critical_path'] = critical_chain
        
        return dependency_analysis
```

## Document Download and Processing

### File Management System

```python
import os
from urllib.parse import urlparse

class DocumentDownloadManager(DocumentFlowTracker):
    
    def __init__(self, download_directory="./downloads"):
        super().__init__()
        self.download_dir = download_directory
        os.makedirs(download_directory, exist_ok=True)
    
    def download_case_documents(self, case_id, document_types=None):
        """Download all documents for a case"""
        
        documents = self.trace_complete_document_lifecycle(case_id)
        download_results = {
            'case_id': case_id,
            'total_documents': len(documents),
            'downloaded_files': [],
            'failed_downloads': [],
            'total_size_mb': 0
        }
        
        for doc in documents:
            # Filter by document type if specified
            if document_types and doc['type'] not in document_types:
                continue
            
            # Download PDF files
            for pdf_file in doc['pdf_files']:
                if pdf_file['url']:
                    try:
                        download_result = self.download_pdf_file(
                            pdf_file['url'], 
                            pdf_file['title'], 
                            case_id
                        )
                        
                        if download_result['success']:
                            download_results['downloaded_files'].append({
                                'document_title': doc['title'],
                                'file_title': pdf_file['title'],
                                'local_path': download_result['local_path'],
                                'size_mb': download_result['size_mb']
                            })
                            download_results['total_size_mb'] += download_result['size_mb']
                        else:
                            download_results['failed_downloads'].append({
                                'document_title': doc['title'],
                                'file_title': pdf_file['title'],
                                'url': pdf_file['url'],
                                'error': download_result['error']
                            })
                    
                    except Exception as e:
                        download_results['failed_downloads'].append({
                            'document_title': doc['title'],
                            'file_title': pdf_file['title'],
                            'url': pdf_file['url'],
                            'error': str(e)
                        })
        
        return download_results
    
    def download_pdf_file(self, file_url, file_title, case_id):
        """Download individual PDF file"""
        
        try:
            import requests
            
            response = requests.get(file_url, stream=True)
            response.raise_for_status()
            
            # Create safe filename
            safe_filename = self.create_safe_filename(file_title, case_id)
            local_path = os.path.join(self.download_dir, safe_filename)
            
            # Download file
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Get file size
            file_size_mb = os.path.getsize(local_path) / (1024 * 1024)
            
            return {
                'success': True,
                'local_path': local_path,
                'size_mb': file_size_mb
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_safe_filename(self, title, case_id, max_length=200):
        """Create safe filename for document download"""
        
        # Remove invalid characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_. "
        safe_title = ''.join(c for c in title if c in safe_chars)
        
        # Truncate if too long
        if len(safe_title) > max_length - 20:  # Leave room for case_id and extension
            safe_title = safe_title[:max_length - 20]
        
        return f"case_{case_id}_{safe_title}.pdf"
    
    def organize_downloads_by_type(self):
        """Organize downloaded files into subdirectories by document type"""
        
        # Implementation would move files into type-based subdirectories
        pass
```

## Real-World Applications

### Legislative Document Portal

```python
class DocumentPortal:
    def __init__(self):
        self.tracker = AdvancedDocumentAnalyzer()
        self.downloader = DocumentDownloadManager()
        
    def create_case_document_package(self, case_id, include_downloads=False):
        """Create comprehensive document package for a case"""
        
        package = {
            'case_id': case_id,
            'generated_at': datetime.now().isoformat(),
            'document_lifecycle': self.tracker.trace_complete_document_lifecycle(case_id),
            'dependency_analysis': self.tracker.identify_document_dependency_chains(case_id),
            'actor_involvement': {},
            'download_package': None
        }
        
        # Add actor involvement for each document
        for doc in package['document_lifecycle']:
            doc_id = doc['document_id']
            actors = self.tracker.map_document_actor_relationships(doc_id)
            package['actor_involvement'][doc_id] = actors
        
        # Create download package if requested
        if include_downloads:
            package['download_package'] = self.downloader.download_case_documents(case_id)
        
        return package
    
    def generate_document_summary_report(self, case_ids):
        """Generate summary report of documents across multiple cases"""
        
        report = {
            'analysis_date': datetime.now().isoformat(),
            'total_cases': len(case_ids),
            'document_statistics': {
                'total_documents': 0,
                'documents_by_type': defaultdict(int),
                'documents_by_status': defaultdict(int),
                'average_documents_per_case': 0
            },
            'efficiency_metrics': {},
            'common_patterns': {}
        }
        
        all_documents = []
        
        for case_id in case_ids:
            case_docs = self.tracker.trace_complete_document_lifecycle(case_id)
            all_documents.extend(case_docs)
            
            # Update statistics
            for doc in case_docs:
                report['document_statistics']['documents_by_type'][doc['type']] += 1
                report['document_statistics']['documents_by_status'][doc['status']] += 1
        
        report['document_statistics']['total_documents'] = len(all_documents)
        report['document_statistics']['average_documents_per_case'] = len(all_documents) / len(case_ids) if case_ids else 0
        
        # Add efficiency analysis
        report['efficiency_metrics'] = self.tracker.analyze_document_processing_efficiency()
        
        # Add pattern analysis
        report['common_patterns'] = self.tracker.analyze_document_flow_patterns()
        
        return report
```

### Document Change Monitor

```python
class DocumentChangeMonitor:
    def __init__(self):
        self.tracker = DocumentFlowTracker()
        self.last_check = {}
        
    def monitor_document_updates(self, case_ids, check_interval_hours=24):
        """Monitor documents for updates"""
        
        cutoff_time = datetime.now() - timedelta(hours=check_interval_hours)
        cutoff_string = cutoff_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        updates_found = {
            'check_time': datetime.now().isoformat(),
            'cutoff_time': cutoff_string,
            'cases_checked': len(case_ids),
            'updates': []
        }
        
        for case_id in case_ids:
            # Check for document updates in this case
            params = {
                '$expand': 'Dokument/Dokumenttype,Dokument/Dokumentstatus',
                '$filter': f'sagid eq {case_id} and Dokument/opdateringsdato gt datetime\'{cutoff_string}\'',
                '$orderby': 'Dokument/opdateringsdato desc'
            }
            
            url = f"{self.tracker.base_url}SagDokument?" + urllib.parse.urlencode(params)
            response = requests.get(url)
            
            if response.json().get('value'):
                for doc_relation in response.json()['value']:
                    if 'Dokument' in doc_relation:
                        doc = doc_relation['Dokument']
                        
                        update_info = {
                            'case_id': case_id,
                            'document_id': doc['id'],
                            'document_title': doc.get('titel', 'Unknown'),
                            'document_type': doc.get('Dokumenttype', {}).get('type', 'Unknown'),
                            'update_time': doc.get('opdateringsdato', ''),
                            'current_status': doc.get('Dokumentstatus', {}).get('status', 'Unknown')
                        }
                        
                        updates_found['updates'].append(update_info)
        
        return updates_found
```

This comprehensive document flow tracking system provides complete visibility into the legislative document lifecycle, enabling sophisticated applications for legal research, compliance monitoring, and democratic transparency through detailed document relationship mapping and automated change detection.