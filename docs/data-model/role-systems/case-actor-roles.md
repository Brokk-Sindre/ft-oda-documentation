# Case-Actor Role System (SagAktørRolle)

The SagAktørRolle system defines the semantic relationships between cases (Sag) and actors (Aktør) in the Danish Parliament. This sophisticated role system captures the many different ways individuals, committees, and organizations participate in the parliamentary process.

## Overview

The SagAktør junction table links cases to actors, with the specific nature of the relationship defined by the SagAktørRolle entity. This creates a rich semantic network that precisely describes how different actors participate in parliamentary cases.

**Key Statistics:**
- **23 distinct role types** covering all forms of parliamentary participation
- **Millions of relationships** across 70+ years of parliamentary history
- **Multi-language semantics** with Danish terms and English explanations

## Complete SagAktørRolle Reference

### 1. Taler (Speaker)
**Danish:** Taler  
**English:** Speaker  
**Context:** Actor who speaks during parliamentary debates on the case  
**Usage:** Links speakers to the cases they addressed in parliamentary sessions  

### 2. Ordfører for forslagsstillerne (Spokesperson for Proposers)
**Danish:** Ordfører for forslagsstillerne  
**English:** Spokesperson for proposers  
**Context:** Designated spokesperson representing all proposers of a bill or proposal  
**Usage:** Key role in legislative process - the main voice for supporters  

### 3. Tidligere henvist til (Previously Referred To)
**Danish:** Tidligere henvist til  
**English:** Previously referred to  
**Context:** Case was previously referred to this actor/committee for consideration  
**Usage:** Tracks historical referral patterns and committee jurisdiction changes  

### 4. Af (By/From)
**Danish:** Af  
**English:** By/From  
**Context:** Generic attribution - case originated from or was initiated by this actor  
**Usage:** Broad attribution role for various forms of case initiation  

### 5. Medspørger (Co-questioner)
**Danish:** Medspørger  
**English:** Co-questioner  
**Context:** Additional questioner in parliamentary questions (beyond primary questioner)  
**Usage:** Tracks collaborative questioning in § 20-spørgsmål and similar formats  

### 6. Ministerområde (Ministry Area)
**Danish:** Ministerområde  
**English:** Ministry area  
**Context:** Case falls under the jurisdiction of this ministry/minister  
**Usage:** Links cases to responsible government departments  

### 7. Privatist (Private Individual)
**Danish:** Privatist  
**English:** Private individual  
**Context:** Private citizen or organization involved in the case  
**Usage:** Enables citizen participation tracking in parliamentary processes  

### 8. Kopi sendt til (Copy Sent To)
**Danish:** Kopi sendt til  
**English:** Copy sent to  
**Context:** Actor receives copies of case-related communications  
**Usage:** Tracks information distribution in parliamentary correspondence  

### 9. Relevant for (Relevant For)
**Danish:** Relevant for  
**English:** Relevant for  
**Context:** Case is considered relevant to this actor's interests or responsibilities  
**Usage:** Broad relevance marking for interested parties  

### 10. Spørger (Questioner)
**Danish:** Spørger  
**English:** Questioner  
**Context:** Primary questioner in parliamentary questions  
**Usage:** Essential role in § 20-spørgsmål and other inquiry formats  

### 11. Henvist til (Referred To)
**Danish:** Henvist til  
**English:** Referred to  
**Context:** Case is currently referred to this actor/committee for consideration  
**Usage:** Active referral relationships - tracks current committee responsibilities  

### 12. Udsteder (Issuer)
**Danish:** Udsteder  
**English:** Issuer  
**Context:** Actor who issues or publishes case-related materials  
**Usage:** Attribution for official publications and statements  

### 13. Optaget af (Recorded By)
**Danish:** Optaget af  
**English:** Recorded by  
**Context:** Actor responsible for recording or documenting case proceedings  
**Usage:** Administrative role in parliamentary documentation  

### 14. Minister
**Danish:** Minister  
**English:** Minister  
**Context:** Government minister responsible for the case area  
**Usage:** Critical role linking cases to government responsibility and accountability  

### 15. Forespørger (Inquirer)
**Danish:** Forespørger  
**English:** Inquirer  
**Context:** Actor making formal inquiries about the case  
**Usage:** Used in forespørgsel (inquiry) case types  

### 16. Forslagsstiller (priv.) (Private Proposer)
**Danish:** Forslagsstiller (priv.)  
**English:** Private proposer  
**Context:** Private actor proposing legislation or parliamentary action  
**Usage:** Enables citizen initiative tracking in the parliamentary system  

### 17. Til (To)
**Danish:** Til  
**English:** To  
**Context:** Case is directed to or intended for this actor  
**Usage:** Target or recipient relationship in case communications  

### 18. Afgivet af (Submitted By)
**Danish:** Afgivet af  
**English:** Submitted by  
**Context:** Actor who formally submits case materials or responses  
**Usage:** Attribution for formal submissions and responses  

### 19. Forslagsstiller (reg.) (Regular Proposer)
**Danish:** Forslagsstiller (reg.)  
**English:** Regular proposer  
**Context:** Official parliamentary proposer (typically MPs or committees)  
**Usage:** Standard legislative proposer role - most common for lovforslag  

### 20. Orlovssøgende (Leave Applicant)
**Danish:** Orlovssøgende  
**English:** Leave applicant  
**Context:** MP applying for leave of absence  
**Usage:** Specialized role for leave application cases  

### 21. Stedfortræder (Deputy)
**Danish:** Stedfortræder  
**English:** Deputy  
**Context:** Deputy or substitute representative  
**Usage:** Tracks deputy assignments and temporary representations  

### 22. Statsrevisor inhabil (State Auditor Disqualified)
**Danish:** Statsrevisor inhabil  
**English:** State auditor disqualified  
**Context:** State auditor who must recuse themselves from a case due to conflicts  
**Usage:** Specialized role for audit independence requirements  

### 23. Besvaret af (Answered By)
**Danish:** Besvaret af  
**English:** Answered by  
**Context:** Actor who provides official answers to parliamentary questions  
**Usage:** Links questions to their official responses, typically ministers

## Role Categories

### Legislative Roles
- **Forslagsstiller (reg.)** - Regular proposer
- **Forslagsstiller (priv.)** - Private proposer  
- **Ordfører for forslagsstillerne** - Spokesperson for proposers
- **Taler** - Speaker

### Administrative Roles
- **Minister** - Government minister
- **Ministerområde** - Ministry area
- **Udsteder** - Issuer
- **Optaget af** - Recorded by
- **Stedfortræder** - Deputy

### Query and Response Roles
- **Spørger** - Questioner
- **Medspørger** - Co-questioner
- **Forespørger** - Inquirer
- **Besvaret af** - Answered by

### Process Roles
- **Henvist til** - Referred to
- **Tidligere henvist til** - Previously referred to
- **Afgivet af** - Submitted by
- **Relevant for** - Relevant for

### Communication Roles
- **Til** - To
- **Af** - By/From
- **Kopi sendt til** - Copy sent to

### Special Cases
- **Privatist** - Private individual
- **Orlovssøgende** - Leave applicant
- **Statsrevisor inhabil** - State auditor disqualified

## Usage Patterns

### Most Common Roles

1. **Minister** - Appears in most government-related cases
2. **Forslagsstiller (reg.)** - Standard role for parliamentary proposals
3. **Spørger** - Common in § 20-spørgsmål question format
4. **Henvist til** - Frequent for committee referrals
5. **Besvaret af** - Common in question-answer cycles

### Legislative Process Flow

```mermaid
graph LR
    A[Forslagsstiller] --> B[Case Created]
    B --> C[Henvist til Committee]
    C --> D[Ordfører appointed]
    D --> E[Taler in debate]
    E --> F[Minister response]
```

### Question Process Flow

```mermaid
graph LR
    A[Spørger asks question] --> B[Medspørger may join]
    B --> C[Henvist til Ministry]
    C --> D[Minister assigned]
    D --> E[Besvaret af Minister]
```

## Query Examples

### Find All Actors for a Specific Case

```bash
# Get all actor relationships for case ID 102903
curl "https://oda.ft.dk/api/SagAktør?%24filter=sagid%20eq%20102903&%24expand=Aktør,SagAktørRolle"
```

### Find Cases by Role Type

```bash
# Find all cases where someone is a "Minister"
curl "https://oda.ft.dk/api/SagAktør?%24filter=rolleid%20eq%2014&%24expand=Sag,Aktør"

# Find all cases with private proposers
curl "https://oda.ft.dk/api/SagAktør?%24filter=rolleid%20eq%2016&%24expand=Sag,Aktør"
```

### Find Actor Participation Patterns

```bash
# Find all roles for a specific actor
curl "https://oda.ft.dk/api/SagAktør?%24filter=aktørid%20eq%2012345&%24expand=SagAktørRolle,Sag"
```

## API Implementation Notes

### Role ID Mapping

The `rolleid` field in SagAktør maps to the `id` field in SagAktørRolle:

```json
{
  "id": 123456,
  "sagid": 102903,
  "aktørid": 7890,
  "rolleid": 14,  // Maps to Minister role
  "opdateringsdato": "2025-09-09T15:30:00"
}
```

### Expansion Patterns

**Single Level:**
```bash
curl "https://oda.ft.dk/api/SagAktør?%24expand=SagAktørRolle"
```

**Two Level:**
```bash
curl "https://oda.ft.dk/api/SagAktør?%24expand=Aktør,SagAktørRolle"
```

### Performance Considerations

- SagAktør is one of the largest junction tables
- Use specific filters to limit result sets
- Role-based queries are well-indexed
- Consider pagination for large result sets

## Historical Context

### Role Evolution

The 23 role types have evolved to capture the complexity of Danish parliamentary procedure:

- **Traditional roles**: Taler, Minister, Forslagsstiller
- **Modern additions**: Privatist (citizen participation)
- **Administrative roles**: Statsrevisor inhabil (audit independence)
- **Process roles**: Henvist til/Tidligere henvist til (referral tracking)

### Data Quality

- **Complete historical coverage**: Roles applied retroactively to historical data
- **Consistent usage**: Role semantics maintained across different parliamentary periods
- **Regular updates**: New relationships created in real-time as parliamentary work progresses

## Conclusion

The SagAktørRolle system represents one of the most sophisticated role classification systems in any parliamentary API. Its 23 distinct roles capture the full spectrum of parliamentary participation, from formal legislative roles to administrative functions to citizen engagement.

This granular role system enables precise analysis of:
- **Democratic participation patterns**
- **Government accountability relationships** 
- **Committee jurisdiction and workflow**
- **Inter-party collaboration patterns**
- **Citizen engagement in parliamentary processes**

The semantic richness of these roles makes the Danish Parliament API invaluable for researchers studying democratic processes and civic engagement patterns.