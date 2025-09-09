# Compliance & Legal

Legal, regulatory, and quality compliance information for using the Danish Parliament API. Understand your obligations and the API's commitments to data quality and privacy.

## Compliance Areas

### = [GDPR Compliance](gdpr/)
Personal data handling under European data protection regulations.

- **[Personal Data](gdpr/personal-data.md)** - What personal information is exposed
- **[Data Subject Rights](gdpr/data-subject-rights.md)** - Rights of individuals in the data
- **[Lawful Basis](gdpr/lawful-basis.md)** - Legal grounds for data processing

### =Ü [Licensing](licensing/)
Terms of use and attribution requirements.

- **[Terms of Service](licensing/terms-of-service.md)** - API usage terms
- **[Attribution](licensing/attribution.md)** - How to properly credit data sources

###  [Data Quality](data-quality/)
API data quality guarantees and limitations.

- **[Freshness](data-quality/freshness.md)** - How current is the data
- **[Completeness](data-quality/completeness.md)** - Data coverage and gaps
- **[Integrity](data-quality/integrity.md)** - Data accuracy and consistency

## Key Compliance Principles

### Open Data Philosophy
The Danish Parliament API embodies Denmark's commitment to transparency:
- **Public by Default** - All parliamentary data is public
- **No Restrictions** - No API keys or rate limits
- **Universal Access** - Available to everyone globally
- **Democratic Transparency** - Supporting informed citizenship

### GDPR Considerations

#### Personal Data Exposure
The API contains extensive personal information about public officials:
```json
{
  "navn": "Anders Fogh Rasmussen",
  "biografi": "Født 26-01-1953. Cand.polit...",
  "email": "example@ft.dk",
  "telefon": "+45 33 37 55 00"
}
```

#### Lawful Basis
Processing is justified under GDPR Article 6(1):
- **(e) Public Interest** - Democratic transparency
- **(f) Legitimate Interests** - Public accountability
- **Article 86** - Official documents exception

#### Your Responsibilities
When using personal data from the API:
1. **Purpose Limitation** - Use only for stated purposes
2. **Data Minimization** - Don't collect unnecessary data
3. **Storage Limitation** - Don't retain longer than needed
4. **Security** - Protect any stored personal data
5. **Transparency** - Inform users about data usage

### Attribution Requirements

While the API is free to use, proper attribution is expected:

#### Minimum Attribution
```
Data source: Danish Parliament (Folketinget) - oda.ft.dk
```

#### Recommended Attribution
```
Data provided by the Danish Parliament Open Data API (oda.ft.dk)
Retrieved: 2025-09-09
```

#### Academic Citation
```
Danish Parliament. (2025). Open Data API [Data set]. 
Retrieved from https://oda.ft.dk/api/
```

## Data Quality Commitments

### Freshness Guarantee
- **Real-time Updates** - During parliamentary sessions
- **Daily Synchronization** - For most entities
- **Historical Accuracy** - Past data is immutable

### Completeness Levels
| Period | Completeness | Notes |
|--------|--------------|-------|
| 2000-Present | 95-100% | Near complete coverage |
| 1990-1999 | 80-95% | Good coverage, some gaps |
| 1980-1989 | 60-80% | Moderate coverage |
| Pre-1980 | Variable | Significant gaps possible |

### Data Integrity
- **Referential Integrity** - Foreign keys are valid
- **Temporal Consistency** - Dates are logical
- **UTF-8 Encoding** - Proper character representation
- **Validation** - Data follows documented schemas

## Compliance Checklist

Before using the API in production:

### Legal Review
- [ ] Understand GDPR obligations for your use case
- [ ] Review Terms of Service compatibility
- [ ] Implement proper attribution
- [ ] Document lawful basis for processing
- [ ] Consider data subject rights

### Technical Implementation
- [ ] Handle personal data securely
- [ ] Implement data minimization
- [ ] Set appropriate retention periods
- [ ] Log data access for accountability
- [ ] Encrypt sensitive data at rest

### Organizational Measures
- [ ] Appoint data protection officer (if required)
- [ ] Create privacy policy for users
- [ ] Implement data breach procedures
- [ ] Train staff on data protection
- [ ] Document processing activities

## Special Considerations

### Journalistic Use
Enhanced protections under GDPR Article 85:
- Broader lawful basis for processing
- Public interest in transparency
- Freedom of expression considerations

### Research Use
Specific provisions under GDPR Article 89:
- Scientific research exemptions
- Appropriate safeguards required
- Pseudonymization where possible

### Commercial Use
No restrictions on commercial use, but:
- Must comply with all GDPR requirements
- Consider competitive fairness
- Respect individual privacy rights

## Risk Assessment

### Low Risk Uses
- Aggregated statistics
- Public policy analysis
- Historical research
- Educational purposes

### Medium Risk Uses
- Individual voting tracking
- Political profiling
- Behavioral analysis
- Predictive modeling

### High Risk Uses
- Automated decision-making
- Systematic monitoring
- Large-scale processing
- Sensitive data combinations

## Getting Help

### Legal Questions
- **GDPR**: Contact your data protection authority
- **Terms**: Email folketinget@ft.dk
- **Attribution**: See [Licensing](licensing/)

### Technical Issues
- **Data Quality**: Report to API maintainers
- **Encoding Problems**: Check UTF-8 handling
- **Missing Data**: See [Completeness](data-quality/completeness.md)

## Updates and Changes

This compliance framework is subject to change:
- Monitor for Terms of Service updates
- Watch for GDPR guidance changes
- Check for new data quality commitments
- Review attribution requirements periodically

Last Updated: September 2025