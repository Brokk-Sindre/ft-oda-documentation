# GDPR Compliance Overview

The Danish Parliament API exposes extensive personal data about public officials and political actors. This section provides comprehensive guidance on GDPR compliance considerations, lawful basis for processing, and data subject rights when using the API.

## Personal Data Exposure Analysis

### Types of Personal Data Available

Based on comprehensive API investigation (Phase 22), the API exposes:

#### Biographical Information (Aktør Entity)
```json
{
  "id": 5,
  "biografi": "Frank Aaen (f. 1949) er...", // Extensive biographical details
  "efternavn": "Aaen",
  "fornavn": "Frank", 
  "navn": "Frank Aaen",
  "email": "frank.aaen@ft.dk",        // Direct email addresses
  "telefon": "+45 3337 5XXX",        // Office phone numbers  
  "adresse": "Christiansborg...",     // Office addresses
  "fødselsdato": "1949-XX-XX",       // Birth dates
  "ægteskabsstatus": "Gift med...",   // Marital status, spouse names
  "børn": "Har X børn...",           // Family information
  "uddannelse": "Cand.mag...",       // Educational background
  "erhverv": "Politiker, tidligere..." // Career history
}
```

#### Contact Information
- **Email addresses**: Direct parliamentary email contacts
- **Phone numbers**: Office phone numbers
- **Addresses**: Parliamentary office addresses
- **Photos**: High-resolution portrait images

#### Political Career Data
- **Voting records**: Individual voting decisions by politician
- **Committee memberships**: Current and historical positions
- **Speech transcripts**: Parliamentary debate participation
- **Document authorship**: Bills, amendments, and proposals

### Data Sensitivity Assessment

```python
def analyze_personal_data_exposure():
    """Analyze GDPR implications of exposed data"""
    
    personal_data_categories = {
        'basic_identification': {
            'fields': ['navn', 'fornavn', 'efternavn'],
            'sensitivity': 'LOW',
            'public_interest': 'HIGH',
            'gdpr_concern': 'MINIMAL'
        },
        'contact_information': {
            'fields': ['email', 'telefon', 'adresse'],
            'sensitivity': 'MEDIUM', 
            'public_interest': 'HIGH',
            'gdpr_concern': 'MODERATE'
        },
        'biographical_details': {
            'fields': ['biografi', 'fødselsdato', 'ægteskabsstatus'],
            'sensitivity': 'HIGH',
            'public_interest': 'MEDIUM',
            'gdpr_concern': 'SIGNIFICANT'
        },
        'family_information': {
            'fields': ['ægtefælle', 'børn'],
            'sensitivity': 'HIGH',
            'public_interest': 'LOW', 
            'gdpr_concern': 'HIGH'
        }
    }
    
    return personal_data_categories
```

## Lawful Basis for Processing

### Primary Lawful Basis: Public Task (Article 6(1)(e))

The most applicable lawful basis for processing Danish Parliament API data is **"public task"**:

> Processing is necessary for the performance of a task carried out in the public interest or in the exercise of official authority vested in the data controller.

#### Legal Framework
```python
class GDPRLawfulBasis:
    def __init__(self):
        self.primary_basis = "Article 6(1)(e) - Public task"
        self.supporting_arguments = [
            "Democratic transparency and accountability",
            "Public right to information about elected officials",
            "Parliamentary oversight and scrutiny functions",
            "Journalistic and academic research purposes",
            "Civic engagement and voter education"
        ]
    
    def assess_lawful_basis(self, data_type, processing_purpose):
        """Assess lawful basis for specific data processing"""
        if data_type in ['voting_records', 'speeches', 'committee_work']:
            return {
                'basis': 'Article 6(1)(e)',
                'confidence': 'HIGH',
                'justification': 'Core democratic transparency function'
            }
        elif data_type in ['contact_info', 'basic_bio']:
            return {
                'basis': 'Article 6(1)(e)',
                'confidence': 'MEDIUM',
                'justification': 'Facilitates democratic engagement'
            }
        elif data_type in ['family_details', 'private_life']:
            return {
                'basis': 'Article 6(1)(e)',
                'confidence': 'LOW',
                'justification': 'Public interest may not outweigh privacy rights'
            }
```

### Alternative Lawful Bases

#### Legitimate Interests (Article 6(1)(f))
```python
def assess_legitimate_interests(processing_purpose):
    """Assess legitimate interests basis"""
    
    legitimate_interests = {
        'journalism': {
            'interest': 'Press freedom and public interest reporting',
            'necessity': 'HIGH',
            'balancing_test': 'Usually favors processing'
        },
        'academic_research': {
            'interest': 'Scientific research and education',
            'necessity': 'MEDIUM',
            'balancing_test': 'Depends on research scope'
        },
        'civic_engagement': {
            'interest': 'Informed citizenship and democracy',
            'necessity': 'MEDIUM', 
            'balancing_test': 'Generally acceptable'
        },
        'commercial_analysis': {
            'interest': 'Business intelligence and consulting',
            'necessity': 'LOW',
            'balancing_test': 'Likely fails balancing test'
        }
    }
    
    return legitimate_interests.get(processing_purpose)
```

## Data Subject Rights Implementation

### Rights of Public Officials

Public officials have **limited but not eliminated** privacy rights:

```python
class PublicOfficialRights:
    def __init__(self):
        self.standard_rights = [
            'right_to_information',
            'right_of_access', 
            'right_to_rectification',
            'right_to_erasure',
            'right_to_restrict_processing',
            'right_to_data_portability',
            'right_to_object'
        ]
    
    def assess_right_applicability(self, right, data_type):
        """Assess if right applies to public officials"""
        
        if data_type == 'official_duties':
            # Limited rights for official parliamentary activities
            limited_rights = {
                'right_to_erasure': 'RESTRICTED - Historical record preservation',
                'right_to_restrict_processing': 'RESTRICTED - Public interest',
                'right_to_object': 'RESTRICTED - Democratic transparency'
            }
            return limited_rights.get(right, 'FULL_RIGHTS')
        
        elif data_type == 'private_life':
            # Full rights for purely private information
            return 'FULL_RIGHTS'
        
        else:
            # Mixed assessment needed
            return 'CASE_BY_CASE'
```

### Right to Rectification Implementation

```python
class DataRectificationHandler:
    def __init__(self):
        self.contact_email = "folketinget@ft.dk"
        self.subject_line = "Åbne Data - Data Rectification Request"
    
    def handle_rectification_request(self, politician_name, incorrect_data, correct_data):
        """Process data rectification request"""
        
        request_template = f"""
        Subject: {self.subject_line}
        
        Dear Danish Parliament Data Team,
        
        I am requesting rectification of personal data in the Open Data API (oda.ft.dk) 
        under Article 16 of the GDPR.
        
        Data Subject: {politician_name}
        Incorrect Data: {incorrect_data}
        Correct Data: {correct_data}
        
        Legal Basis for Request:
        - Article 16 GDPR (Right to rectification)
        - Data accuracy obligation under Article 5(1)(d)
        
        Please confirm receipt and expected correction timeline.
        
        Best regards,
        [Your name and contact information]
        """
        
        return {
            'template': request_template,
            'contact': self.contact_email,
            'expected_response': '30 days (Article 12(3))'
        }
```

## Compliance Best Practices

### For API Consumers

#### Data Minimization Principles

```python
class GDPRCompliantAPIClient:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api"
        self.data_retention_policy = {
            'voting_records': 365,  # days
            'contact_info': 90,
            'biographical_data': 30,
            'family_info': 0  # Don't store
        }
    
    def get_politician_minimal_data(self, name, purpose):
        """Get only necessary data for stated purpose"""
        
        field_mappings = {
            'voting_analysis': 'id,navn,startdato,slutdato',
            'contact_directory': 'id,navn,email,telefon',
            'basic_profile': 'id,navn,typeid,startdato',
            'research': 'id,navn,biografi,startdato,slutdato'
        }
        
        select_fields = field_mappings.get(purpose, 'id,navn')
        
        response = requests.get(
            f"{self.base_url}/Aktør",
            params={
                '$filter': f"navn eq '{name}'",
                '$select': select_fields
            }
        )
        
        return self.apply_data_retention(response.json(), purpose)
    
    def apply_data_retention(self, data, purpose):
        """Apply data retention policies"""
        # Implementation would include automatic data deletion
        # based on retention policies and purpose limitation
        pass
```

#### Purpose Limitation Implementation

```python
class PurposeLimitationController:
    VALID_PURPOSES = [
        'journalistic_research',
        'academic_study', 
        'civic_engagement',
        'transparency_monitoring',
        'historical_analysis'
    ]
    
    def __init__(self, declared_purpose):
        if declared_purpose not in self.VALID_PURPOSES:
            raise ValueError(f"Purpose {declared_purpose} not recognized")
        
        self.purpose = declared_purpose
        self.allowed_data_types = self._get_allowed_data_types()
    
    def _get_allowed_data_types(self):
        """Determine allowed data types based on purpose"""
        purpose_mappings = {
            'journalistic_research': ['all'],
            'academic_study': ['voting_records', 'speeches', 'basic_info'],
            'civic_engagement': ['voting_records', 'contact_info', 'basic_info'],
            'transparency_monitoring': ['voting_records', 'committee_work', 'documents'],
            'historical_analysis': ['all_except_current_contact']
        }
        
        return purpose_mappings.get(self.purpose, ['basic_info'])
    
    def filter_data_by_purpose(self, raw_data):
        """Filter data based on declared purpose"""
        if 'all' in self.allowed_data_types:
            return raw_data
        
        filtered_data = {}
        for key, value in raw_data.items():
            data_type = self._classify_data_type(key)
            if data_type in self.allowed_data_types:
                filtered_data[key] = value
        
        return filtered_data
```

### Privacy Impact Assessment

```python
def conduct_privacy_impact_assessment(project_scope):
    """Conduct PIA for Danish Parliament API usage"""
    
    pia_framework = {
        'data_types': {
            'high_risk': ['biografi', 'family_info', 'personal_contact'],
            'medium_risk': ['voting_records', 'committee_membership'],
            'low_risk': ['basic_identification', 'official_roles']
        },
        
        'processing_activities': {
            'collection': 'Automated API data retrieval',
            'storage': 'Local database or file system',
            'analysis': 'Statistical or research analysis',
            'publication': 'Public reporting or visualization'
        },
        
        'risk_mitigation': {
            'data_minimization': 'Only collect necessary fields',
            'storage_security': 'Encrypt sensitive data at rest',
            'access_control': 'Limit access to authorized personnel',
            'retention_limits': 'Delete data when no longer needed',
            'anonymization': 'Remove direct identifiers when possible'
        }
    }
    
    return pia_framework
```

## Legal Compliance Framework

### Documentation Requirements

```python
class GDPRDocumentationFramework:
    def __init__(self):
        self.required_documentation = [
            'privacy_notice',
            'lawful_basis_assessment', 
            'data_retention_policy',
            'security_measures',
            'data_subject_procedures',
            'privacy_impact_assessment'
        ]
    
    def generate_privacy_notice(self, organization):
        """Generate privacy notice template"""
        template = f"""
        PRIVACY NOTICE - Danish Parliament API Data Processing
        
        Organization: {organization}
        Data Controller: {organization}
        
        Data Sources: Danish Parliament Open Data API (oda.ft.dk)
        
        Categories of Personal Data:
        - Names and basic identification of public officials
        - Professional contact information
        - Parliamentary voting records  
        - Committee membership information
        - Biographical information (limited processing)
        
        Lawful Basis: Article 6(1)(e) GDPR - Public task
        
        Processing Purposes:
        - Democratic transparency and accountability
        - Research and analysis of parliamentary activities
        - Public information and civic engagement
        
        Data Retention: [Specify retention periods by data category]
        
        Your Rights:
        - Right of access to your personal data
        - Right to rectification of inaccurate data
        - Right to object to processing (limited for public officials)
        - Right to complain to supervisory authority
        
        Contact: [Your organization's DPO/contact details]
        Supervisory Authority: Datatilsynet (Danish Data Protection Agency)
        """
        return template
```

### Cross-Border Transfer Considerations

```python
def assess_international_transfers(recipient_country):
    """Assess GDPR compliance for international data transfers"""
    
    adequacy_decisions = [
        'Andorra', 'Argentina', 'Canada', 'Faroe Islands', 'Guernsey',
        'Israel', 'Isle of Man', 'Japan', 'Jersey', 'New Zealand',
        'South Korea', 'Switzerland', 'United Kingdom', 'Uruguay'
    ]
    
    if recipient_country in adequacy_decisions:
        return {
            'transfer_mechanism': 'Adequacy Decision',
            'additional_safeguards': 'None required',
            'compliance_status': 'COMPLIANT'
        }
    elif recipient_country == 'United States':
        return {
            'transfer_mechanism': 'Standard Contractual Clauses or equivalent',
            'additional_safeguards': 'Transfer Impact Assessment required',
            'compliance_status': 'REQUIRES_SAFEGUARDS'
        }
    else:
        return {
            'transfer_mechanism': 'Standard Contractual Clauses',
            'additional_safeguards': 'Transfer Impact Assessment required',
            'compliance_status': 'REQUIRES_SAFEGUARDS'
        }
```

## Supervisory Authority Contact

### Danish Data Protection Agency (Datatilsynet)

```python
SUPERVISORY_AUTHORITY = {
    'name': 'Datatilsynet',
    'website': 'https://www.datatilsynet.dk/',
    'email': 'dt@datatilsynet.dk',
    'phone': '+45 3319 3200',
    'address': 'Carl Jacobsens Vej 35, 2500 Valby',
    'complaint_form': 'https://www.datatilsynet.dk/english/complaint',
    'guidance': 'https://www.datatilsynet.dk/english/general-conditions/guidelines'
}
```

## Practical Compliance Checklist

### Pre-Processing Checklist

- [ ] **Lawful Basis Identified**: Document lawful basis for each processing activity
- [ ] **Purpose Defined**: Clearly define and document processing purposes  
- [ ] **Data Minimization**: Only collect necessary data fields
- [ ] **Retention Policy**: Define retention periods for each data category
- [ ] **Security Measures**: Implement appropriate technical and organizational measures
- [ ] **Privacy Notice**: Create privacy notice if processing affects individuals
- [ ] **Rights Procedures**: Establish procedures for data subject rights requests
- [ ] **PIA Completed**: Conduct Privacy Impact Assessment for high-risk processing

### Ongoing Compliance

- [ ] **Regular Reviews**: Periodically review processing activities and compliance
- [ ] **Data Accuracy**: Monitor and correct inaccurate data
- [ ] **Security Updates**: Maintain security measures and respond to breaches
- [ ] **Staff Training**: Train staff on GDPR compliance requirements
- [ ] **Vendor Management**: Ensure third-party processors are compliant
- [ ] **Incident Response**: Have procedures for data breach response

## Integration with Other Documentation

- **[Security Measures](../production/security/)**: Technical safeguards for personal data
- **[Data Quality](./data-quality/)**: Data accuracy and integrity requirements  
- **[API Reference](../api-reference/)**: Understanding what personal data is available

## Disclaimer

This guidance is for informational purposes only and does not constitute legal advice. Organizations processing personal data from the Danish Parliament API should consult with qualified legal counsel to ensure compliance with applicable data protection laws and regulations.

The GDPR compliance landscape for government transparency data involves complex balancing between privacy rights and democratic transparency. While public officials have reduced privacy expectations, organizations must still implement appropriate safeguards and respect fundamental data protection principles.