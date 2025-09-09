# Personal Data Handling

This document provides detailed guidance on handling personal data exposed through the Danish Parliament API, including data classification, processing guidelines, and specific handling requirements for different types of personal information.

## Personal Data Classification

### High-Sensitivity Personal Data

#### Biographical Details (Biografi Field)
The `biografi` field contains extensive personal information:

```json
{
  "biografi": "Frank Aaen (f. 1949 i København) er cand.mag. i historie og samfundsfag fra Københavns Universitet (1975). Han var ansat som gymnasielærer indtil 1994. Frank Aaen har været gift med Anja siden 1973, og de har to voksne børn. Han var medlem af Danmarks Kommunistiske Parti fra 1968-1990..."
}
```

**Contains:**
- Birth dates and places
- Educational background  
- Career history
- Family information (spouse, children)
- Personal relationships
- Health information (occasionally)
- Financial information (occasionally)

**GDPR Considerations:**
```python
def handle_biographical_data(bio_text, processing_purpose):
    """Handle biographical data with GDPR compliance"""
    
    sensitive_patterns = {
        'health': r'(syg|sygdom|behandling|hospital|læge|medicin)',
        'family': r'(gift|ægtefælle|børn|familie|forældre)',
        'financial': r'(gæld|formue|løn|indtægt|økonomi)',
        'criminal': r'(dømt|straffet|sigte|kriminel)',
        'political_opinion': r'(medlem af|tilsluttet|støtter|modstander)'
    }
    
    risk_level = 'LOW'
    detected_categories = []
    
    for category, pattern in sensitive_patterns.items():
        if re.search(pattern, bio_text.lower()):
            detected_categories.append(category)
            risk_level = 'HIGH'
    
    return {
        'risk_level': risk_level,
        'sensitive_categories': detected_categories,
        'recommendation': get_handling_recommendation(risk_level, processing_purpose)
    }

def get_handling_recommendation(risk_level, purpose):
    """Get handling recommendations based on risk and purpose"""
    if risk_level == 'HIGH' and purpose not in ['journalism', 'historical_research']:
        return 'AVOID_PROCESSING'
    elif risk_level == 'HIGH':
        return 'ENHANCED_SAFEGUARDS'
    else:
        return 'STANDARD_PROCESSING'
```

### Medium-Sensitivity Personal Data

#### Contact Information
```python
contact_data_fields = {
    'email': {
        'sensitivity': 'MEDIUM',
        'type': 'Professional contact',
        'retention_recommendation': '2 years',
        'sharing_restrictions': 'Professional use only'
    },
    'telefon': {
        'sensitivity': 'MEDIUM', 
        'type': 'Office phone',
        'retention_recommendation': '2 years',
        'sharing_restrictions': 'Professional use only'
    },
    'adresse': {
        'sensitivity': 'LOW',
        'type': 'Office address',
        'retention_recommendation': '5 years',
        'sharing_restrictions': 'None (public information)'
    }
}
```

#### Voting Records and Political Activities
```python
def classify_political_data(data_type):
    """Classify political data sensitivity"""
    
    classifications = {
        'voting_record': {
            'sensitivity': 'MEDIUM',
            'public_interest': 'VERY_HIGH',
            'retention_justification': 'Historical record',
            'deletion_restrictions': 'Democratic accountability requires preservation'
        },
        'committee_membership': {
            'sensitivity': 'LOW',
            'public_interest': 'HIGH', 
            'retention_justification': 'Transparency',
            'deletion_restrictions': 'Public record'
        },
        'speech_transcripts': {
            'sensitivity': 'MEDIUM',
            'public_interest': 'HIGH',
            'retention_justification': 'Parliamentary record',
            'deletion_restrictions': 'Official proceedings'
        }
    }
    
    return classifications.get(data_type, {'sensitivity': 'UNKNOWN'})
```

## Processing Guidelines by Data Type

### Biographical Information Processing

```python
class BiographicalDataProcessor:
    def __init__(self):
        self.redaction_patterns = {
            'family_details': r'(gift med \w+|børn|familie)',
            'health_info': r'(syg|behandling|hospital)',
            'financial_details': r'(gæld|formue|indtægt)',
            'addresses': r'(bor i|adresse|hjemme)'
        }
    
    def process_for_purpose(self, biography, purpose):
        """Process biographical data based on intended purpose"""
        
        if purpose == 'political_analysis':
            # Focus on political career, education, professional experience
            return self._extract_professional_info(biography)
            
        elif purpose == 'contact_directory':
            # Minimal processing - name and basic role only
            return self._extract_basic_info(biography)
            
        elif purpose == 'historical_research':
            # May include more details but with enhanced safeguards
            return self._process_with_safeguards(biography)
            
        elif purpose == 'journalistic':
            # Broader processing allowed but with editorial responsibility
            return biography  # With appropriate editorial guidelines
        
        else:
            raise ValueError(f"Purpose '{purpose}' not supported")
    
    def _extract_professional_info(self, biography):
        """Extract only professional/educational information"""
        professional_keywords = [
            'uddannelse', 'universitet', 'cand.', 'lærer', 'ansat',
            'minister', 'formand', 'medlem af', 'politiker'
        ]
        
        sentences = biography.split('.')
        professional_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in professional_keywords):
                # Remove family references
                cleaned = re.sub(self.redaction_patterns['family_details'], '[FAMILY INFO REDACTED]', sentence)
                professional_sentences.append(cleaned)
        
        return '. '.join(professional_sentences)
    
    def _apply_redaction(self, biography, redaction_level='STANDARD'):
        """Apply redaction based on sensitivity level"""
        if redaction_level == 'MINIMAL':
            return biography
        elif redaction_level == 'STANDARD':
            redacted = biography
            for category, pattern in self.redaction_patterns.items():
                redacted = re.sub(pattern, f'[{category.upper()} REDACTED]', redacted)
            return redacted
        elif redaction_level == 'STRICT':
            return self._extract_professional_info(biography)
```

### Contact Information Handling

```python
class ContactDataHandler:
    def __init__(self):
        self.data_retention_periods = {
            'email': 730,  # 2 years in days
            'telefon': 730,
            'adresse': 1825  # 5 years
        }
    
    def validate_contact_usage(self, contact_data, intended_use):
        """Validate appropriate use of contact information"""
        
        acceptable_uses = {
            'email': [
                'official_correspondence',
                'interview_requests',
                'information_requests',
                'constituent_services'
            ],
            'telefon': [
                'urgent_media_contact',
                'official_business',
                'constituent_emergency'
            ]
        }
        
        unacceptable_uses = [
            'marketing',
            'commercial_solicitation', 
            'personal_use',
            'harassment',
            'automated_bulk_contact'
        ]
        
        if intended_use in unacceptable_uses:
            return {'valid': False, 'reason': 'Prohibited use case'}
        
        for field, data in contact_data.items():
            if field in acceptable_uses:
                if intended_use not in acceptable_uses[field]:
                    return {
                        'valid': False,
                        'reason': f'{intended_use} not acceptable for {field}'
                    }
        
        return {'valid': True}
    
    def apply_contact_safeguards(self, contact_data):
        """Apply safeguards to contact information"""
        safeguarded_data = {}
        
        for field, value in contact_data.items():
            if field == 'email':
                # Validate email is parliamentary domain
                if '@ft.dk' not in value:
                    safeguarded_data[field] = '[NON-OFFICIAL EMAIL REDACTED]'
                else:
                    safeguarded_data[field] = value
            
            elif field == 'telefon':
                # Ensure only office numbers (starting with +45 33)
                if not value.startswith('+45 33'):
                    safeguarded_data[field] = '[PERSONAL NUMBER REDACTED]'
                else:
                    safeguarded_data[field] = value
            
            else:
                safeguarded_data[field] = value
        
        return safeguarded_data
```

### Voting Record Processing

```python
class VotingDataProcessor:
    def __init__(self):
        self.public_interest_threshold = 'VERY_HIGH'
    
    def process_voting_records(self, voting_data, analysis_scope):
        """Process voting records with appropriate safeguards"""
        
        if analysis_scope == 'individual_accountability':
            # High public interest - minimal restrictions
            return self._full_voting_analysis(voting_data)
        
        elif analysis_scope == 'party_analysis':
            # May anonymize individual votes while preserving party data
            return self._anonymized_party_analysis(voting_data)
        
        elif analysis_scope == 'statistical_research':
            # Aggregate data only, no individual identification
            return self._aggregate_voting_statistics(voting_data)
    
    def _full_voting_analysis(self, voting_data):
        """Full voting record analysis for accountability purposes"""
        return {
            'processing_basis': 'Article 6(1)(e) - Public task',
            'data_subjects_notified': False,  # Public officials, public data
            'retention_period': 'Indefinite - historical record',
            'sharing_restrictions': 'None - public accountability data',
            'data': voting_data
        }
    
    def _anonymized_party_analysis(self, voting_data):
        """Party-level analysis with individual anonymization"""
        anonymized_records = []
        
        for record in voting_data:
            anonymized_record = {
                'party': record.get('parti'),
                'vote': record.get('typeid'),
                'case_id': record.get('sagid'),
                'date': record.get('opdateringsdato'),
                # Remove individual identifiers
                'politician_id': None,
                'politician_name': '[ANONYMIZED]'
            }
            anonymized_records.append(anonymized_record)
        
        return {
            'processing_basis': 'Article 6(1)(f) - Legitimate interest',
            'anonymization_applied': True,
            'data': anonymized_records
        }
```

## Data Minimization Strategies

### Selective Field Processing

```python
class DataMinimizationController:
    def __init__(self):
        self.purpose_field_mappings = {
            'voting_transparency': [
                'id', 'navn', 'startdato', 'slutdato', 'typeid'
            ],
            'contact_directory': [
                'id', 'navn', 'email', 'telefon'  
            ],
            'research_basic': [
                'id', 'navn', 'typeid', 'periodeid'
            ],
            'comprehensive_research': [
                'id', 'navn', 'biografi', 'startdato', 'slutdato', 
                'typeid', 'periodeid'
            ]
        }
    
    def get_minimal_dataset(self, purpose, politician_filter=None):
        """Get minimal dataset for specific purpose"""
        
        if purpose not in self.purpose_field_mappings:
            raise ValueError(f"Purpose '{purpose}' not defined")
        
        fields = self.purpose_field_mappings[purpose]
        select_clause = ','.join(fields)
        
        params = {'$select': select_clause}
        
        if politician_filter:
            params['$filter'] = f"substringof('{politician_filter}', navn)"
        
        # Make API request with minimal fields
        response = requests.get(
            'https://oda.ft.dk/api/Aktør',
            params=params
        )
        
        return {
            'purpose': purpose,
            'fields_requested': fields,
            'data_minimization_applied': True,
            'records': response.json().get('value', [])
        }
```

### Automated Redaction Tools

```python
import re
from typing import Dict, List

class PersonalDataRedactor:
    def __init__(self):
        self.redaction_rules = {
            'phone_numbers': {
                'pattern': r'\+45\s?\d{8}',
                'replacement': '[PHONE REDACTED]',
                'exceptions': [r'\+45\s?33\d{6}']  # Parliament numbers OK
            },
            'email_addresses': {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'replacement': '[EMAIL REDACTED]',
                'exceptions': [r'@ft\.dk']  # Parliament emails OK
            },
            'family_names': {
                'pattern': r'(gift med|ægtefælle|hustru|kone|mand)\s+[\w\s]+',
                'replacement': '[FAMILY INFO REDACTED]',
                'exceptions': []
            },
            'addresses': {
                'pattern': r'\b\d{4}\s+[A-ZÆØÅ][a-zæøå]+\b',
                'replacement': '[ADDRESS REDACTED]',
                'exceptions': ['Christiansborg']  # Parliament address OK
            }
        }
    
    def redact_text(self, text: str, redaction_level: str = 'STANDARD') -> Dict:
        """Redact personal data from text"""
        
        original_text = text
        redacted_text = text
        redactions_applied = []
        
        for rule_name, rule in self.redaction_rules.items():
            pattern = rule['pattern']
            replacement = rule['replacement']
            exceptions = rule.get('exceptions', [])
            
            # Find all matches
            matches = re.finditer(pattern, redacted_text)
            
            for match in matches:
                matched_text = match.group()
                
                # Check if match is in exceptions
                is_exception = any(
                    re.search(exc_pattern, matched_text) 
                    for exc_pattern in exceptions
                )
                
                if not is_exception:
                    redacted_text = redacted_text.replace(matched_text, replacement)
                    redactions_applied.append({
                        'rule': rule_name,
                        'original': matched_text,
                        'redacted': replacement,
                        'position': match.span()
                    })
        
        return {
            'original_text': original_text,
            'redacted_text': redacted_text,
            'redactions_applied': redactions_applied,
            'redaction_count': len(redactions_applied)
        }
    
    def bulk_redact_dataset(self, dataset: List[Dict], text_fields: List[str]) -> List[Dict]:
        """Apply redaction to entire dataset"""
        redacted_dataset = []
        
        for record in dataset:
            redacted_record = record.copy()
            
            for field in text_fields:
                if field in record and record[field]:
                    redaction_result = self.redact_text(record[field])
                    redacted_record[field] = redaction_result['redacted_text']
                    redacted_record[f'{field}_redacted'] = redaction_result['redaction_count'] > 0
            
            redacted_dataset.append(redacted_record)
        
        return redacted_dataset
```

## Storage and Retention Guidelines

### Data Classification-Based Retention

```python
class PersonalDataRetentionManager:
    def __init__(self):
        self.retention_policies = {
            'HIGH_SENSITIVITY': {
                'biographical_details': 90,  # days
                'family_information': 30,
                'health_information': 30,
                'financial_information': 30
            },
            'MEDIUM_SENSITIVITY': {
                'contact_information': 730,  # 2 years
                'voting_records': 'INDEFINITE',  # Public accountability
                'speech_transcripts': 'INDEFINITE'
            },
            'LOW_SENSITIVITY': {
                'basic_identification': 1825,  # 5 years
                'official_positions': 'INDEFINITE',
                'committee_memberships': 'INDEFINITE'
            }
        }
    
    def get_retention_period(self, data_type, sensitivity_level):
        """Get retention period for specific data type"""
        policy = self.retention_policies.get(sensitivity_level, {})
        return policy.get(data_type, 365)  # Default 1 year
    
    def schedule_deletion(self, data_record, data_type, sensitivity_level):
        """Schedule automatic deletion based on retention policy"""
        retention_days = self.get_retention_period(data_type, sensitivity_level)
        
        if retention_days == 'INDEFINITE':
            return {
                'deletion_scheduled': False,
                'reason': 'Public accountability requires indefinite retention',
                'review_date': None
            }
        
        from datetime import datetime, timedelta
        deletion_date = datetime.now() + timedelta(days=retention_days)
        
        return {
            'deletion_scheduled': True,
            'deletion_date': deletion_date.isoformat(),
            'retention_period_days': retention_days,
            'data_type': data_type,
            'sensitivity_level': sensitivity_level
        }
```

### Secure Storage Implementation

```python
from cryptography.fernet import Fernet
import json

class SecurePersonalDataStorage:
    def __init__(self, encryption_key=None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def store_personal_data(self, data, sensitivity_classification):
        """Store personal data with appropriate security measures"""
        
        if sensitivity_classification in ['HIGH_SENSITIVITY']:
            # Encrypt high-sensitivity data
            encrypted_data = self.cipher_suite.encrypt(
                json.dumps(data).encode()
            )
            return {
                'data': encrypted_data.decode(),
                'encrypted': True,
                'sensitivity': sensitivity_classification,
                'storage_date': datetime.now().isoformat()
            }
        
        else:
            # Store medium/low sensitivity data with access logging
            return {
                'data': data,
                'encrypted': False,
                'sensitivity': sensitivity_classification,
                'storage_date': datetime.now().isoformat(),
                'access_log': []
            }
    
    def retrieve_personal_data(self, stored_record, requester_id, access_purpose):
        """Retrieve personal data with access logging"""
        
        # Log the access
        access_entry = {
            'timestamp': datetime.now().isoformat(),
            'requester': requester_id,
            'purpose': access_purpose
        }
        
        if stored_record['encrypted']:
            # Decrypt and return
            decrypted_data = self.cipher_suite.decrypt(
                stored_record['data'].encode()
            )
            data = json.loads(decrypted_data.decode())
        else:
            data = stored_record['data']
            stored_record['access_log'].append(access_entry)
        
        return {
            'data': data,
            'access_logged': True,
            'access_entry': access_entry
        }
```

## Compliance Monitoring

### Automated Compliance Checks

```python
class PersonalDataComplianceMonitor:
    def __init__(self):
        self.compliance_rules = {
            'data_minimization': self._check_data_minimization,
            'retention_limits': self._check_retention_compliance,
            'purpose_limitation': self._check_purpose_compliance,
            'security_measures': self._check_security_compliance
        }
    
    def run_compliance_audit(self, processing_activities):
        """Run comprehensive compliance audit"""
        audit_results = {}
        
        for rule_name, check_function in self.compliance_rules.items():
            try:
                result = check_function(processing_activities)
                audit_results[rule_name] = result
            except Exception as e:
                audit_results[rule_name] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
        
        return {
            'audit_timestamp': datetime.now().isoformat(),
            'overall_compliance': all(
                r.get('status') == 'COMPLIANT' 
                for r in audit_results.values() 
                if isinstance(r, dict)
            ),
            'detailed_results': audit_results
        }
    
    def _check_data_minimization(self, activities):
        """Check if data minimization principles are followed"""
        violations = []
        
        for activity in activities:
            fields_collected = activity.get('fields_collected', [])
            purpose = activity.get('purpose')
            necessary_fields = self._get_necessary_fields_for_purpose(purpose)
            
            unnecessary_fields = set(fields_collected) - set(necessary_fields)
            if unnecessary_fields:
                violations.append({
                    'activity': activity.get('name'),
                    'unnecessary_fields': list(unnecessary_fields)
                })
        
        return {
            'status': 'COMPLIANT' if not violations else 'NON_COMPLIANT',
            'violations': violations
        }
```

## Best Practices Summary

### Personal Data Handling Checklist

- [ ] **Data Classification**: Classify all personal data by sensitivity level
- [ ] **Purpose Definition**: Clearly define processing purposes before collection
- [ ] **Data Minimization**: Only process necessary fields for stated purpose
- [ ] **Consent vs. Legitimate Interest**: Assess lawful basis appropriately
- [ ] **Retention Policies**: Implement automatic deletion schedules
- [ ] **Security Measures**: Encrypt high-sensitivity data
- [ ] **Access Logging**: Log all access to personal data
- [ ] **Regular Audits**: Monitor compliance with data protection principles
- [ ] **Staff Training**: Train staff on personal data handling procedures
- [ ] **Incident Response**: Have procedures for data breaches

The Danish Parliament API's extensive personal data exposure requires careful handling to balance democratic transparency with privacy rights. Organizations must implement appropriate technical and organizational measures to ensure GDPR compliance while preserving the public accountability function of parliamentary data.