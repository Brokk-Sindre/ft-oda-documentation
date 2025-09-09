# Lawful Basis for Processing

This document provides comprehensive guidance on establishing and maintaining lawful basis for processing personal data from the Danish Parliament API under GDPR Article 6. It includes practical frameworks for assessing different lawful bases and implementing appropriate safeguards.

## GDPR Article 6 Analysis for Parliamentary Data

### Primary Lawful Basis: Public Task (Article 6(1)(e))

The most robust lawful basis for processing Danish Parliament API data is **Article 6(1)(e) - Public task**:

> Processing is necessary for the performance of a task carried out in the public interest or in the exercise of official authority vested in the data controller.

```python
class PublicTaskAssessment:
    def __init__(self):
        self.legal_framework = {
            'danish_constitution': 'Grundloven § 57 - Parliamentary transparency',
            'freedom_of_information': 'Offentlighedsloven - Right to public information',
            'eu_transparency': 'Article 15 TFEU - Transparency principle',
            'democratic_principles': 'UN ICCPR Article 25 - Democratic participation'
        }
    
    def assess_public_task_basis(self, processing_purpose, data_subject_role):
        """Assess whether public task basis applies"""
        
        if data_subject_role == 'elected_official':
            public_interest_factors = {
                'democratic_accountability': 'VERY_HIGH',
                'transparency_obligation': 'VERY_HIGH', 
                'voter_information_right': 'VERY_HIGH',
                'historical_record': 'HIGH',
                'academic_research': 'HIGH'
            }
        elif data_subject_role == 'civil_servant':
            public_interest_factors = {
                'democratic_accountability': 'HIGH',
                'transparency_obligation': 'MEDIUM',
                'administrative_oversight': 'HIGH'
            }
        else:
            public_interest_factors = {
                'general_transparency': 'MEDIUM'
            }
        
        # Assess processing purpose alignment
        purpose_alignment = self._assess_purpose_alignment(processing_purpose)
        
        return {
            'lawful_basis': 'Article 6(1)(e)',
            'confidence_level': 'HIGH' if purpose_alignment >= 3 else 'MEDIUM',
            'public_interest_factors': public_interest_factors,
            'legal_foundation': self.legal_framework,
            'recommendation': 'PROCEED' if purpose_alignment >= 2 else 'REVIEW_REQUIRED'
        }
    
    def _assess_purpose_alignment(self, purpose):
        """Score purpose alignment with public task (0-5 scale)"""
        purpose_scores = {
            'democratic_transparency': 5,
            'journalistic_investigation': 5,
            'academic_research': 4,
            'civic_engagement': 4,
            'government_oversight': 5,
            'historical_documentation': 4,
            'political_analysis': 3,
            'commercial_research': 1,
            'marketing': 0,
            'entertainment': 1
        }
        
        return purpose_scores.get(purpose, 2)
```

### Alternative Lawful Basis: Legitimate Interests (Article 6(1)(f))

When public task basis may be insufficient:

```python
class LegitimateInterestsAssessment:
    def __init__(self):
        self.balancing_factors = {
            'controller_interests': [
                'press_freedom',
                'academic_freedom', 
                'business_intelligence',
                'public_information'
            ],
            'data_subject_interests': [
                'privacy_expectation',
                'reputation_protection',
                'family_privacy',
                'professional_impact'
            ],
            'fundamental_rights': [
                'freedom_of_expression',
                'right_to_privacy',
                'family_life_protection',
                'democratic_participation'
            ]
        }
    
    def conduct_balancing_test(self, controller_interest, data_type, data_subject_role):
        """Conduct three-part balancing test for legitimate interests"""
        
        # Part 1: Legitimate interest test
        interest_assessment = self._assess_legitimate_interest(controller_interest)
        
        # Part 2: Necessity test  
        necessity_assessment = self._assess_necessity(controller_interest, data_type)
        
        # Part 3: Balancing test
        balancing_result = self._conduct_balancing(
            controller_interest, data_type, data_subject_role
        )
        
        overall_result = (
            interest_assessment['valid'] and 
            necessity_assessment['necessary'] and
            balancing_result['controller_interests_prevail']
        )
        
        return {
            'lawful_basis_valid': overall_result,
            'legitimate_interest': interest_assessment,
            'necessity': necessity_assessment,
            'balancing_test': balancing_result,
            'recommendation': 'PROCEED' if overall_result else 'USE_ALTERNATIVE_BASIS'
        }
    
    def _assess_legitimate_interest(self, interest):
        """Assess if interest is legitimate"""
        legitimate_interests = {
            'journalism': {
                'valid': True,
                'strength': 'VERY_HIGH',
                'legal_basis': 'Freedom of press, public interest'
            },
            'academic_research': {
                'valid': True,
                'strength': 'HIGH',
                'legal_basis': 'Academic freedom, scientific research'
            },
            'transparency_advocacy': {
                'valid': True,
                'strength': 'HIGH',
                'legal_basis': 'Democratic participation, public oversight'
            },
            'commercial_analysis': {
                'valid': True,
                'strength': 'MEDIUM',
                'legal_basis': 'Business intelligence, market research'
            },
            'political_opposition': {
                'valid': True,
                'strength': 'HIGH',
                'legal_basis': 'Democratic accountability, political debate'
            }
        }
        
        return legitimate_interests.get(interest, {
            'valid': False,
            'strength': 'NONE',
            'legal_basis': 'No recognized legitimate interest'
        })
    
    def _conduct_balancing(self, controller_interest, data_type, data_subject_role):
        """Conduct balancing test between competing interests"""
        
        # Weight factors for different data subjects
        privacy_expectations = {
            'elected_official': 0.3,  # Lower privacy expectation
            'candidate': 0.5,
            'civil_servant': 0.7,
            'private_person': 1.0
        }
        
        # Weight factors for different data types
        data_sensitivity = {
            'voting_records': 0.2,     # Low privacy impact, high public interest
            'basic_contact': 0.4,
            'biographical_basic': 0.6,
            'biographical_detailed': 0.8,
            'family_information': 1.0  # High privacy impact
        }
        
        privacy_weight = privacy_expectations.get(data_subject_role, 0.8)
        sensitivity_weight = data_sensitivity.get(data_type, 0.6)
        
        # Controller interest strength
        interest_strength = {
            'journalism': 0.9,
            'academic_research': 0.8,
            'transparency_advocacy': 0.8,
            'commercial_analysis': 0.4
        }
        
        controller_weight = interest_strength.get(controller_interest, 0.3)
        
        # Simple balancing calculation
        privacy_score = privacy_weight * sensitivity_weight
        controller_score = controller_weight
        
        return {
            'controller_interests_prevail': controller_score > privacy_score,
            'privacy_score': privacy_score,
            'controller_score': controller_score,
            'margin': abs(controller_score - privacy_score),
            'confidence': 'HIGH' if abs(controller_score - privacy_score) > 0.3 else 'LOW'
        }
```

## Lawful Basis Implementation Framework

### Documentation Requirements

```python
class LawfulBasisDocumentation:
    def __init__(self):
        self.required_elements = [
            'lawful_basis_identified',
            'purpose_specification', 
            'necessity_assessment',
            'proportionality_analysis',
            'safeguards_implemented',
            'review_schedule'
        ]
    
    def generate_lawful_basis_record(self, processing_activity):
        """Generate comprehensive lawful basis documentation"""
        
        return {
            'processing_activity': {
                'name': processing_activity.get('name'),
                'description': processing_activity.get('description'),
                'data_controller': processing_activity.get('controller'),
                'start_date': processing_activity.get('start_date')
            },
            
            'personal_data': {
                'categories': processing_activity.get('data_categories'),
                'sensitivity_level': processing_activity.get('sensitivity'),
                'data_subjects': processing_activity.get('subject_categories'),
                'volume': processing_activity.get('estimated_volume')
            },
            
            'lawful_basis': {
                'article_6_basis': processing_activity.get('lawful_basis'),
                'justification': processing_activity.get('basis_justification'),
                'legal_framework': processing_activity.get('supporting_law'),
                'assessment_date': processing_activity.get('assessment_date'),
                'assessed_by': processing_activity.get('assessor')
            },
            
            'safeguards': {
                'technical_measures': processing_activity.get('technical_safeguards'),
                'organizational_measures': processing_activity.get('org_safeguards'),
                'data_minimization': processing_activity.get('minimization_measures'),
                'retention_policy': processing_activity.get('retention_schedule')
            },
            
            'review': {
                'next_review_date': processing_activity.get('next_review'),
                'review_frequency': processing_activity.get('review_frequency'),
                'review_triggers': processing_activity.get('review_triggers')
            }
        }
```

### Purpose Specification Framework

```python
class PurposeSpecification:
    def __init__(self):
        self.purpose_categories = {
            'democratic_accountability': {
                'description': 'Tracking elected officials\' performance and decisions',
                'compatible_purposes': [
                    'voting_analysis', 'performance_monitoring', 
                    'electoral_accountability', 'policy_tracking'
                ],
                'incompatible_purposes': [
                    'commercial_marketing', 'personal_harassment',
                    'entertainment', 'unrelated_research'
                ]
            },
            'journalistic_investigation': {
                'description': 'News reporting and investigative journalism',
                'compatible_purposes': [
                    'fact_checking', 'story_development',
                    'background_research', 'source_verification'
                ],
                'incompatible_purposes': [
                    'commercial_purposes', 'entertainment_gossip',
                    'personal_vendetta', 'harassment'
                ]
            },
            'academic_research': {
                'description': 'Scholarly research and educational purposes',
                'compatible_purposes': [
                    'political_science_research', 'historical_analysis',
                    'behavioral_studies', 'institutional_analysis'
                ],
                'incompatible_purposes': [
                    'commercial_application', 'political_campaigning',
                    'marketing_research', 'non_academic_use'
                ]
            }
        }
    
    def assess_purpose_compatibility(self, declared_purpose, actual_use):
        """Assess if actual use is compatible with declared purpose"""
        
        if declared_purpose not in self.purpose_categories:
            return {
                'compatible': False,
                'reason': 'Declared purpose not recognized'
            }
        
        purpose_spec = self.purpose_categories[declared_purpose]
        
        if actual_use in purpose_spec['compatible_purposes']:
            return {
                'compatible': True,
                'confidence': 'HIGH',
                'basis': 'Explicitly compatible purpose'
            }
        elif actual_use in purpose_spec['incompatible_purposes']:
            return {
                'compatible': False,
                'confidence': 'HIGH',
                'reason': 'Explicitly incompatible purpose'
            }
        else:
            return {
                'compatible': None,
                'confidence': 'LOW',
                'reason': 'Purpose compatibility requires individual assessment'
            }
```

## Special Considerations for Parliamentary Data

### Public Officials' Reduced Privacy Expectations

```python
class PublicOfficialPrivacyAnalysis:
    def __init__(self):
        self.privacy_tiers = {
            'head_of_government': {
                'privacy_expectation': 'VERY_LOW',
                'public_interest': 'MAXIMUM',
                'data_categories_acceptable': 'MOST',
                'special_considerations': [
                    'National security implications',
                    'Diplomatic considerations'
                ]
            },
            'minister': {
                'privacy_expectation': 'LOW',
                'public_interest': 'VERY_HIGH',
                'data_categories_acceptable': 'EXTENSIVE',
                'special_considerations': [
                    'Portfolio-related activities',
                    'Decision-making transparency'
                ]
            },
            'member_of_parliament': {
                'privacy_expectation': 'LOW',
                'public_interest': 'HIGH',
                'data_categories_acceptable': 'BROAD',
                'special_considerations': [
                    'Voting record transparency',
                    'Committee participation'
                ]
            },
            'local_official': {
                'privacy_expectation': 'MEDIUM',
                'public_interest': 'MEDIUM',
                'data_categories_acceptable': 'LIMITED',
                'special_considerations': [
                    'Proportionate to role',
                    'Local relevance'
                ]
            }
        }
    
    def assess_processing_legitimacy(self, official_level, data_category, processing_purpose):
        """Assess legitimacy of processing for public officials"""
        
        official_profile = self.privacy_tiers.get(official_level)
        if not official_profile:
            return {'assessment': 'UNKNOWN', 'reason': 'Official level not recognized'}
        
        # High public interest + low privacy expectation = strong lawful basis
        if (official_profile['public_interest'] in ['MAXIMUM', 'VERY_HIGH'] and
            processing_purpose in ['democratic_accountability', 'transparency']):
            return {
                'assessment': 'STRONG_BASIS',
                'confidence': 'HIGH',
                'lawful_basis': 'Article 6(1)(e) - Public task',
                'additional_safeguards_required': False
            }
        
        # Medium scenarios require balancing
        elif official_profile['privacy_expectation'] == 'MEDIUM':
            return {
                'assessment': 'BALANCING_REQUIRED',
                'confidence': 'MEDIUM',
                'lawful_basis': 'Article 6(1)(f) - Legitimate interests',
                'additional_safeguards_required': True,
                'balancing_test_required': True
            }
        
        else:
            return {
                'assessment': 'WEAK_BASIS',
                'confidence': 'LOW',
                'recommendation': 'SEEK_ALTERNATIVE_BASIS_OR_AVOID'
            }
```

### Historical vs. Current Data Considerations

```python
class TemporalProcessingAnalysis:
    def __init__(self):
        self.temporal_factors = {
            'current_officials': {
                'public_interest': 'MAXIMUM',
                'privacy_expectation': 'MINIMUM',
                'processing_justification': 'Active democratic accountability',
                'recommended_basis': 'Article 6(1)(e)'
            },
            'recent_former_officials': {  # Last 5 years
                'public_interest': 'HIGH',
                'privacy_expectation': 'LOW',
                'processing_justification': 'Ongoing public interest, recent decisions',
                'recommended_basis': 'Article 6(1)(e) or 6(1)(f)'
            },
            'historical_officials': {  # 5+ years ago
                'public_interest': 'MEDIUM',
                'privacy_expectation': 'MEDIUM',
                'processing_justification': 'Historical record, research purposes',
                'recommended_basis': 'Article 6(1)(f) with safeguards'
            },
            'deceased_officials': {
                'public_interest': 'MEDIUM',
                'privacy_expectation': 'LOW',  # GDPR doesn't apply to deceased
                'processing_justification': 'Historical record, family privacy considerations',
                'recommended_basis': 'No GDPR restriction, ethical considerations apply'
            }
        }
    
    def assess_temporal_lawfulness(self, official_status, processing_purpose):
        """Assess lawfulness considering temporal factors"""
        
        temporal_profile = self.temporal_factors.get(official_status)
        if not temporal_profile:
            return {'assessment': 'REQUIRES_INDIVIDUAL_ANALYSIS'}
        
        return {
            'temporal_classification': official_status,
            'public_interest_level': temporal_profile['public_interest'],
            'privacy_expectation': temporal_profile['privacy_expectation'],
            'recommended_lawful_basis': temporal_profile['recommended_basis'],
            'justification': temporal_profile['processing_justification']
        }
```

## Practical Implementation Examples

### Lawful Basis Assessment Tool

```python
class LawfulBasisAssessmentTool:
    def __init__(self):
        self.assessment_framework = {
            'data_categories': [
                'basic_identification', 'contact_information', 'voting_records',
                'biographical_summary', 'biographical_detailed', 'family_information'
            ],
            'processing_purposes': [
                'democratic_accountability', 'journalistic_investigation', 'academic_research',
                'transparency_advocacy', 'historical_documentation', 'commercial_analysis'
            ],
            'data_subject_roles': [
                'current_mp', 'former_mp', 'minister', 'candidate', 'civil_servant'
            ]
        }
    
    def conduct_assessment(self, processing_scenario):
        """Conduct comprehensive lawful basis assessment"""
        
        # Extract scenario components
        data_category = processing_scenario.get('data_category')
        purpose = processing_scenario.get('purpose')
        subject_role = processing_scenario.get('subject_role')
        controller_type = processing_scenario.get('controller_type')
        
        # Run assessments
        public_task_result = self._assess_public_task(purpose, subject_role)
        legitimate_interest_result = self._assess_legitimate_interests(
            purpose, data_category, subject_role, controller_type
        )
        
        # Determine strongest basis
        recommended_basis = self._select_strongest_basis([
            public_task_result, legitimate_interest_result
        ])
        
        return {
            'scenario': processing_scenario,
            'assessments': {
                'public_task': public_task_result,
                'legitimate_interests': legitimate_interest_result
            },
            'recommended_approach': recommended_basis,
            'implementation_guidance': self._generate_implementation_guidance(recommended_basis)
        }
    
    def _select_strongest_basis(self, assessment_results):
        """Select the strongest available lawful basis"""
        
        # Prioritize public task if available
        for result in assessment_results:
            if (result.get('lawful_basis') == 'Article 6(1)(e)' and 
                result.get('confidence_level') == 'HIGH'):
                return result
        
        # Fall back to legitimate interests if strong
        for result in assessment_results:
            if (result.get('lawful_basis') == 'Article 6(1)(f)' and
                result.get('balancing_test', {}).get('controller_interests_prevail')):
                return result
        
        # No strong basis found
        return {
            'lawful_basis': 'NONE_IDENTIFIED',
            'recommendation': 'SEEK_LEGAL_ADVICE',
            'alternative_approaches': [
                'Narrow processing scope',
                'Seek explicit consent',
                'Use anonymized data only'
            ]
        }
```

### Consent Alternative Analysis

```python
class ConsentAnalysis:
    """Analysis of consent as alternative lawful basis"""
    
    def __init__(self):
        self.consent_feasibility = {
            'current_officials': {
                'feasible': False,
                'reason': 'Conflicts with democratic transparency requirements',
                'alternative': 'Public task basis more appropriate'
            },
            'former_officials': {
                'feasible': True,
                'conditions': [
                    'Clear consent mechanism',
                    'Easy withdrawal process', 
                    'No adverse consequences for refusal'
                ],
                'considerations': 'May limit transparency objectives'
            },
            'candidates': {
                'feasible': True,
                'conditions': [
                    'Voluntary participation',
                    'Clear information about use',
                    'Withdrawal rights respected'
                ],
                'considerations': 'Democratic participation may constitute legitimate interest'
            }
        }
    
    def assess_consent_viability(self, subject_category, processing_context):
        """Assess whether consent is viable alternative"""
        
        feasibility = self.consent_feasibility.get(subject_category)
        if not feasibility:
            return {
                'viable': False,
                'reason': 'Subject category not analyzed'
            }
        
        if not feasibility['feasible']:
            return {
                'viable': False,
                'reason': feasibility['reason'],
                'alternative_recommendation': feasibility.get('alternative')
            }
        
        # Assess GDPR consent requirements
        consent_requirements_met = self._assess_consent_requirements(processing_context)
        
        return {
            'viable': feasibility['feasible'] and consent_requirements_met['compliant'],
            'conditions': feasibility.get('conditions', []),
            'gdpr_compliance': consent_requirements_met,
            'practical_considerations': feasibility.get('considerations')
        }
    
    def _assess_consent_requirements(self, context):
        """Assess if consent would meet GDPR requirements"""
        
        # GDPR Article 7 requirements
        requirements = {
            'freely_given': context.get('no_adverse_consequences', False),
            'specific': context.get('specific_purposes_defined', False),
            'informed': context.get('clear_information_provided', False),
            'unambiguous': context.get('clear_consent_mechanism', False),
            'withdrawable': context.get('withdrawal_mechanism_available', False)
        }
        
        return {
            'compliant': all(requirements.values()),
            'requirements_analysis': requirements,
            'missing_requirements': [
                req for req, met in requirements.items() if not met
            ]
        }
```

## Ongoing Compliance Management

### Regular Basis Review

```python
class LawfulBasisReviewManager:
    def __init__(self):
        self.review_triggers = [
            'purpose_change',
            'data_category_expansion', 
            'legal_framework_change',
            'subject_role_change',
            'time_based_review',
            'complaint_received',
            'supervisory_guidance'
        ]
    
    def schedule_review(self, processing_activity, trigger_type):
        """Schedule lawful basis review"""
        
        urgency_levels = {
            'purpose_change': 'IMMEDIATE',
            'legal_framework_change': 'IMMEDIATE',
            'complaint_received': 'URGENT',  # 7 days
            'supervisory_guidance': 'URGENT',
            'data_category_expansion': 'STANDARD',  # 30 days
            'time_based_review': 'ROUTINE',  # Scheduled
            'subject_role_change': 'STANDARD'
        }
        
        urgency = urgency_levels.get(trigger_type, 'STANDARD')
        
        return {
            'processing_activity': processing_activity,
            'review_trigger': trigger_type,
            'urgency_level': urgency,
            'review_deadline': self._calculate_deadline(urgency),
            'review_scope': self._determine_review_scope(trigger_type),
            'reviewer_required': self._determine_reviewer_level(urgency)
        }
    
    def _calculate_deadline(self, urgency):
        """Calculate review deadline based on urgency"""
        from datetime import datetime, timedelta
        
        deadlines = {
            'IMMEDIATE': timedelta(days=1),
            'URGENT': timedelta(days=7),
            'STANDARD': timedelta(days=30),
            'ROUTINE': timedelta(days=90)
        }
        
        return (datetime.now() + deadlines.get(urgency, timedelta(days=30))).isoformat()
```

## Best Practices Summary

### Lawful Basis Selection Hierarchy

1. **Primary Option**: Article 6(1)(e) - Public task
   - For democratic accountability purposes
   - When processing official parliamentary activities
   - For transparency and oversight functions

2. **Secondary Option**: Article 6(1)(f) - Legitimate interests
   - For journalistic purposes
   - For academic research
   - For commercial applications (with strong safeguards)

3. **Fallback Option**: Article 6(1)(a) - Consent
   - When other bases are insufficient
   - For former officials (limited scenarios)
   - For non-essential data processing

### Implementation Checklist

- [ ] **Lawful Basis Identified**: Clear identification of Article 6 basis
- [ ] **Documentation Complete**: Comprehensive basis documentation
- [ ] **Purpose Specified**: Clear, specific purpose definition
- [ ] **Proportionality Assessed**: Processing proportionate to purpose
- [ ] **Safeguards Implemented**: Appropriate technical/organizational measures
- [ ] **Review Scheduled**: Regular basis review scheduled
- [ ] **Staff Trained**: Staff understand lawful basis requirements
- [ ] **Records Maintained**: Comprehensive processing records kept

The selection and maintenance of appropriate lawful basis is fundamental to GDPR compliance when processing Danish Parliament API data. The unique nature of parliamentary transparency creates strong public task justifications, but organizations must still implement appropriate safeguards and conduct regular reviews to ensure ongoing compliance.