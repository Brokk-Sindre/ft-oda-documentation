# Terms of Service

Comprehensive terms governing the use of Denmark's Parliamentary Open Data API (oda.ft.dk) and associated data services.

## Overview and Scope

### Service Definition
These Terms of Service govern access to and use of the Danish Parliament Open Data API ("the Service"), provided by the Danish Parliament (Folketinget) through the domain oda.ft.dk. The Service provides structured access to parliamentary data including:

- Parliamentary cases (Sager) and proceedings
- Political actor information (Aktører) 
- Voting records (Stemmer) and patterns
- Parliamentary documents (Dokumenter)
- Committee activities (Møder) and decisions
- Historical parliamentary data dating back to 1953

### Legal Framework
This Service operates under Danish law and EU regulations, including:
- Danish Freedom of Information Act (Offentlighedsloven)
- EU General Data Protection Regulation (GDPR)
- Danish Data Protection Act
- Public Sector Information Directive (PSI Directive)
- Open Data Initiative guidelines

### Geographic Scope
While the Service is accessible globally, these terms are governed by Danish law. Users accessing the Service from outside Denmark must comply with both these terms and their local applicable laws.

## Acceptable Use Policies

### Permitted Uses
The Service is provided to support democratic transparency and accountability. Permitted uses include:

#### Public Interest Activities
- **Journalistic Research**: News reporting and investigative journalism
- **Academic Research**: Scholarly analysis of parliamentary activities
- **Civic Engagement**: Public education and democratic participation
- **Policy Analysis**: Government transparency and accountability research
- **Historical Documentation**: Archival and preservation activities

#### Commercial Applications
- **Media Services**: News platforms and information services
- **Analytics Platforms**: Political analysis and reporting tools
- **Educational Products**: Civic education and training materials
- **Research Services**: Consulting and policy analysis services
- **Technology Development**: API clients and integration tools

#### Personal Use
- **Individual Research**: Personal study of parliamentary activities
- **Educational Projects**: Student assignments and learning
- **Civic Monitoring**: Personal tracking of political representatives
- **App Development**: Personal or open-source applications

### Prohibited Activities
The following activities are strictly prohibited:

#### Malicious Use
- **System Disruption**: Attempts to overload, disable, or impair the Service
- **Security Breaches**: Unauthorized access attempts or vulnerability exploitation
- **Data Scraping**: Automated harvesting that violates fair use principles
- **Infrastructure Attacks**: DDoS attacks or similar malicious activities

#### Illegal Activities
- **Harassment**: Using personal data to harass or threaten individuals
- **Defamation**: Knowingly spreading false information about public officials
- **Identity Theft**: Misusing personal information for fraudulent purposes
- **Discrimination**: Using data to discriminate against protected groups

#### Misrepresentation
- **False Attribution**: Misrepresenting data sources or API responses
- **Data Manipulation**: Altering data to misrepresent parliamentary activities
- **Service Impersonation**: Presenting yourself as affiliated with Folketinget
- **Misleading Claims**: False statements about data accuracy or currency

## API Usage Limitations and Fair Use

### Technical Limitations
The Service operates without authentication or explicit rate limits, but users must observe fair use principles:

#### Request Volume Guidelines
- **Reasonable Frequency**: Avoid excessive simultaneous requests
- **Batch Processing**: Use appropriate pagination for large datasets
- **Caching**: Implement reasonable caching to reduce redundant requests
- **Off-Peak Usage**: Schedule heavy processing during off-peak hours (22:00-06:00 CET)

#### Performance Considerations
- **Response Time**: Expect 85ms-2s response times under normal conditions
- **Timeout Handling**: Implement proper timeout handling (recommend 30-60 seconds)
- **Error Handling**: Handle HTTP 5xx errors gracefully with exponential backoff
- **Connection Limits**: Use connection pooling appropriately

### Data Usage Guidelines

#### Storage and Retention
- **Minimal Storage**: Store only data necessary for your specific use case
- **Regular Updates**: Refresh cached data periodically to maintain accuracy
- **Secure Storage**: Implement appropriate security measures for stored personal data
- **Retention Limits**: Delete unnecessary data according to your stated purposes

#### Processing Limitations
- **Purpose Limitation**: Use data only for declared and legitimate purposes
- **Data Minimization**: Process only the minimum data necessary
- **Accuracy Maintenance**: Ensure processed data remains accurate and current
- **Transparent Processing**: Clearly document how you process API data

## Data Usage Rights and Restrictions

### Rights Granted
Under these terms, you are granted a non-exclusive, worldwide, royalty-free license to:

#### Access and Retrieve
- **API Access**: Query the Service using standard OData protocols
- **Data Download**: Retrieve parliamentary data for permitted purposes
- **Real-time Access**: Monitor live parliamentary activities through the API
- **Historical Access**: Query historical parliamentary data back to 1953

#### Use and Process
- **Analysis Rights**: Analyze data for legitimate research and reporting
- **Republication Rights**: Republish data with proper attribution
- **Derivative Works**: Create derived datasets and analyses
- **Integration Rights**: Integrate data into applications and services

### Restrictions and Limitations

#### Personal Data Restrictions
The API contains extensive personal information about public officials. You must:

- **GDPR Compliance**: Follow all applicable data protection regulations
- **Purpose Limitation**: Use personal data only for stated purposes
- **Rights Respect**: Honor data subject rights requests where applicable
- **Security Measures**: Implement appropriate technical and organizational measures

#### Commercial Restrictions
While commercial use is permitted, you must:

- **Fair Competition**: Ensure commercial use doesn't create unfair market advantages
- **Attribution Maintenance**: Maintain proper attribution in commercial products
- **Transparency**: Be transparent about data sources in commercial applications
- **Revenue Sharing**: No requirement for revenue sharing, but consider ethical implications

#### Technical Restrictions
- **No Reverse Engineering**: Don't attempt to reverse engineer the API infrastructure
- **Metadata Respect**: Follow metadata and schema definitions provided
- **Format Integrity**: Maintain data format integrity when republishing
- **Version Compatibility**: Handle API version changes appropriately

## User Responsibilities and Obligations

### Data Protection Compliance
As a user processing personal data from the API, you must:

#### Legal Compliance
- **GDPR Compliance**: Implement full GDPR compliance measures
- **Local Law Compliance**: Follow applicable local data protection laws
- **Documentation**: Maintain records of processing activities
- **Legal Basis**: Establish and document lawful basis for processing

#### Technical Safeguards
- **Security Measures**: Implement appropriate security controls
- **Access Controls**: Limit access to personal data on need-to-know basis
- **Encryption**: Use encryption for data in transit and at rest
- **Audit Trails**: Maintain logs of data access and processing

#### Privacy Rights
- **Privacy Policy**: Publish clear privacy policies for end users
- **Consent Management**: Obtain necessary consents where required
- **Rights Requests**: Handle data subject rights requests appropriately
- **Breach Notification**: Implement data breach notification procedures

### Attribution Requirements

#### Minimum Attribution
For any use of API data, provide:
```
Data source: Danish Parliament (Folketinget) - oda.ft.dk
```

#### Standard Attribution
For published works and applications:
```
Data provided by the Danish Parliament Open Data API (oda.ft.dk)
Retrieved: [Date]
License: Open Data under Danish Freedom of Information Act
```

#### Academic Attribution
For scholarly works:
```
Danish Parliament. (2025). Open Data API [Data set]. 
Retrieved [Date] from https://oda.ft.dk/api/
```

### Quality Assurance Responsibilities

#### Data Accuracy
- **Verification**: Verify data accuracy for critical applications
- **Currency Checks**: Ensure data currency meets your requirements
- **Error Reporting**: Report data quality issues to API maintainers
- **Disclaimer Provision**: Include appropriate disclaimers about data limitations

#### User Communication
- **Transparency**: Be transparent about data sources and limitations
- **Update Notifications**: Notify users of significant data changes
- **Error Communication**: Communicate data errors or outages to users
- **Support Provision**: Provide appropriate user support for your applications

## Prohibited Uses and Activities

### Strictly Prohibited Activities

#### System Abuse
- **Denial of Service**: Any attempt to overwhelm or disable the Service
- **Resource Monopolization**: Excessive use that impacts other users
- **Infrastructure Probing**: Unauthorized scanning or testing of systems
- **Circumvention Attempts**: Bypassing technical limitations or security measures

#### Data Misuse
- **Personal Harassment**: Using personal data to harass, stalk, or threaten individuals
- **Identity Fraud**: Misusing personal information for fraudulent purposes
- **Discriminatory Use**: Using data to discriminate against protected groups
- **Malicious Profiling**: Creating profiles for harassment or discrimination

#### Legal Violations
- **Copyright Infringement**: Violating copyright in derivative works
- **Privacy Violations**: Breaching individual privacy rights
- **Defamation**: Publishing false or defamatory information
- **Regulatory Violations**: Violating applicable financial or political regulations

### Content and Publication Restrictions

#### Misleading Information
- **False Attribution**: Misrepresenting data sources or origins
- **Data Manipulation**: Altering data to support false narratives
- **Context Removal**: Removing important context that changes meaning
- **Timestamp Manipulation**: Misrepresenting when events occurred

#### Commercial Misuse
- **Unfair Competition**: Using data to create unfair competitive advantages
- **Market Manipulation**: Using insider information for financial gain
- **Spam Generation**: Using contact information for unsolicited communications
- **Automated Decision Harm**: Making automated decisions that harm individuals

## Service Availability and Uptime

### Service Level Expectations

#### Availability Targets
- **Uptime Goal**: 99.5% availability (target, not guarantee)
- **Planned Maintenance**: Maximum 4 hours monthly during off-peak hours
- **Emergency Maintenance**: As needed with minimal advance notice
- **Performance Target**: 85ms-2s response times under normal load

#### Maintenance Windows
- **Regular Maintenance**: First Sunday of each month, 02:00-06:00 CET
- **Security Updates**: As required, with 24-hour advance notice when possible
- **Infrastructure Updates**: Quarterly, with one-week advance notice
- **Database Maintenance**: As needed, during low-traffic periods

### Service Interruptions

#### Planned Outages
- **Advance Notice**: Minimum 24-hour notice for planned maintenance
- **Status Updates**: Real-time status updates on service status page
- **Duration Estimates**: Best-effort estimates for maintenance duration
- **Rollback Plans**: Prepared rollback procedures for failed deployments

#### Unplanned Outages
- **Incident Response**: 24/7 monitoring and incident response
- **Communication**: Status updates within 15 minutes of detection
- **Resolution Priority**: Critical issues resolved within 4 hours target
- **Post-Incident Review**: Public post-mortems for significant outages

#### Force Majeure
The Service may be unavailable due to circumstances beyond reasonable control:
- Natural disasters or extreme weather
- Internet infrastructure failures
- Government mandated shutdowns
- Cyber attacks or security incidents

## Data Accuracy and Disclaimers

### Data Accuracy Commitments

#### Real-Time Data
- **Session Updates**: Parliamentary session data updated within 1-4 hours
- **Vote Recording**: Voting results available within 1 hour of conclusion
- **Document Publishing**: Documents available when officially published
- **Status Changes**: Case status updates reflected within 24 hours

#### Historical Data
- **Immutability**: Historical data is generally immutable once recorded
- **Correction Process**: Errors corrected through documented processes
- **Version Control**: Major corrections noted in change logs
- **Verification**: Historical accuracy verified against official records

### Data Limitations and Disclaimers

#### Accuracy Disclaimer
**THE API DATA IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND**. While we strive for accuracy:

- **Human Error**: Data entry errors may occur
- **Technical Issues**: System failures may cause data gaps
- **Timing Delays**: Real-time data may have delays
- **Format Changes**: Data formats may evolve over time

#### Completeness Disclaimer
Data completeness varies by time period:

| Period | Estimated Completeness | Notes |
|--------|----------------------|-------|
| 2010-Present | 95-100% | Near complete coverage |
| 2000-2009 | 90-98% | Good coverage, minor gaps |
| 1990-1999 | 80-95% | Moderate gaps possible |
| 1980-1989 | 60-85% | Significant gaps possible |
| Pre-1980 | Variable | Major gaps likely |

#### Usage Disclaimer
- **No Warranty**: No warranty for fitness for particular purposes
- **User Responsibility**: Users must verify data for critical applications
- **Independent Verification**: Important decisions should be verified through official channels
- **Currency Check**: Users must verify data currency for time-sensitive applications

## Liability Limitations

### Service Provider Limitations

#### Maximum Liability
**TO THE MAXIMUM EXTENT PERMITTED BY LAW, THE DANISH PARLIAMENT'S LIABILITY IS LIMITED TO:**

- **Direct Damages Only**: No liability for indirect, consequential, or punitive damages
- **Nominal Amounts**: Maximum liability limited to nominal amounts
- **Service Value**: Liability cannot exceed the value of the free service (¬0)
- **Time Limitation**: Claims must be brought within one year of occurrence

#### Exclusions
The following damages are explicitly excluded:
- **Business Losses**: Lost profits, revenue, or business opportunities
- **Data Losses**: Lost data or information (users must maintain backups)
- **Reputation Damage**: Harm to reputation or goodwill
- **Third-Party Claims**: Claims by third parties against users

### User Liability and Indemnification

#### User Responsibilities
Users agree to indemnify and hold harmless the Danish Parliament from:
- **Misuse Claims**: Claims arising from prohibited uses of the Service
- **Privacy Violations**: Claims related to improper handling of personal data
- **Copyright Infringement**: Claims related to derivative works or republication
- **Defamation Claims**: Claims arising from false or misleading statements

#### Insurance Recommendations
Users engaged in commercial activities should consider:
- **Professional Liability Insurance**: Coverage for errors and omissions
- **Cyber Liability Insurance**: Coverage for data breaches and cyber incidents
- **General Liability Insurance**: Coverage for third-party claims
- **Legal Defense Coverage**: Coverage for legal defense costs

### Force Majeure and External Factors

#### Excluded Events
No liability for service interruptions caused by:
- **Natural Disasters**: Earthquakes, floods, storms, or other natural events
- **Government Actions**: Law changes, regulations, or official orders
- **Network Failures**: Internet infrastructure failures beyond our control
- **Third-Party Services**: Failures of essential third-party services
- **Security Incidents**: Cyber attacks or security breaches

## Terms Modification and Updates

### Modification Process

#### Notice Requirements
- **Advance Notice**: Minimum 30 days notice for material changes
- **Publication**: Changes published on the documentation website
- **Version Control**: All versions archived and accessible
- **Effective Date**: Clear effective date for new terms

#### Types of Changes

#### Minor Updates
Non-material changes that may be implemented with reduced notice:
- **Clarifications**: Minor clarifications that don't change meaning
- **Contact Information**: Updates to contact details or procedures  
- **Technical Details**: Minor technical specification updates
- **Formatting**: Improvements to formatting or organization

#### Material Changes
Significant changes requiring full notice period:
- **Rights Modifications**: Changes to user rights or restrictions
- **Liability Changes**: Modifications to liability or indemnification terms
- **Service Changes**: Significant changes to service availability or features
- **Legal Updates**: Changes required by law or regulation

### User Acceptance

#### Continued Use
- **Implied Acceptance**: Continued use after effective date constitutes acceptance
- **Objection Rights**: Users may object to changes before effective date
- **Service Discontinuation**: Users may discontinue use if they object to changes
- **Granular Acceptance**: Some changes may allow selective acceptance

#### Notification Methods
- **Website Notices**: Prominent notices on main documentation pages
- **API Headers**: HTTP headers indicating terms version
- **Status Page**: Updates posted to service status page
- **Archive Access**: Historical terms versions maintained in archive

### Legal Framework Updates

#### Regulatory Changes
Terms may be updated to comply with:
- **GDPR Updates**: Changes to European data protection regulations
- **Danish Law Changes**: Modifications to relevant Danish legislation
- **Court Decisions**: Significant legal precedents affecting the Service
- **International Treaties**: Relevant international agreements

#### Dispute Resolution
- **Danish Jurisdiction**: Disputes governed by Danish law
- **Alternative Resolution**: Preference for mediation before litigation
- **Language**: Disputes conducted in Danish or English as appropriate
- **Venue**: Copenhagen courts have exclusive jurisdiction

## Contact Information and Support

### General Inquiries
- **Email**: folketinget@ft.dk
- **Website**: [www.ft.dk](https://www.ft.dk)
- **Address**: Christiansborg, 1240 København K, Denmark
- **Phone**: +45 33 37 55 00

### Technical Support
- **API Issues**: Report through documentation feedback system
- **Data Quality**: Submit data quality reports via official channels
- **Security Issues**: security@ft.dk (for security vulnerabilities)
- **Status Updates**: Monitor service status page for real-time information

### Legal and Compliance
- **Terms Questions**: Legal department via folketinget@ft.dk
- **Privacy Concerns**: Data protection officer via official channels
- **GDPR Requests**: Follow established data subject rights procedures
- **Commercial Licensing**: For specialized licensing arrangements

---

**Last Updated**: September 2025  
**Version**: 1.0  
**Effective Date**: Immediate  
**Next Review**: March 2026

---

*These terms are provided in English for international accessibility. In case of discrepancy with Danish legal requirements, Danish law takes precedence.*