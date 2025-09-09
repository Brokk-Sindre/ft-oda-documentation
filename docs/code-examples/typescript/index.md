# TypeScript Definitions

Complete TypeScript type definitions for all 50 entities in the Danish Parliament API, providing type safety and excellent IDE support.

## Overview

The Danish Parliament API contains **50 entities** with complex relationships, role systems, and enumeration types. These TypeScript definitions provide:

- **Complete type coverage** for all entities
- **Role enumerations** (23 SagAktørRolle types, 25 DokumentAktørRolle types)
- **Status classifications** (68 case statuses, 13 actor types, 28 document types)
- **Relationship mappings** between entities
- **Generic client interface** for type-safe API calls

## Installation

```bash
# Save the types to your project
# Copy the types from types.md into your project as danish-parliament-api.d.ts
npm install --save-dev typescript

# Include in your tsconfig.json
{
  "compilerOptions": {
    "types": ["./types/danish-parliament-api"]
  }
}
```

## Quick Start

```typescript
import { DanishParliamentAPI, Sag, Aktør, Afstemning, APIResponse } from './danish-parliament-api';

// Initialize with type safety
const api = new DanishParliamentAPI();

// Type-safe API calls
const cases: APIResponse<Sag> = await api.getCases({
  filter: "substringof('klima', titel)",
  expand: "Sagskategori",
  top: 50
});

// Access with full IntelliSense
cases.value.forEach(case => {
  console.log(`Case ${case.id}: ${case.titel}`);
  console.log(`Category: ${case.Sagskategori?.kategori}`);
  console.log(`Updated: ${new Date(case.opdateringsdato).toLocaleDateString()}`);
});

// Type-safe actor queries
const actors: APIResponse<Aktør> = await api.getActors({
  filter: "aktørtypeid eq 5", // Type 5 = Politicians
  expand: "Aktørtype"
});
```

## Type Libraries

1. **[Complete Type Definitions](types.md)** - All 50 entity interfaces and enums
2. **[Type-Safe Client](client.md)** - Fully typed API client implementation

## Key Features

### 1. Entity Type Safety
```typescript
// Strongly typed entity properties
interface Sag {
  id: number;
  titel: string;
  offentlighedskode: 'O' | 'F' | string; // Public/Confidential
  opdateringsdato: string; // ISO datetime
  typeid: number;
  statusid: number;
  
  // Relationships (optional when expanded)
  Sagskategori?: Sagskategori;
  SagAktør?: SagAktør[];
  Sagstrin?: Sagstrin[];
}
```

### 2. Role System Types
```typescript
// Case-Actor relationship roles (23 types)
enum SagAktørRolle {
  Ordfører = 1,
  MedOrdførerGrp = 2,
  OrdførerGrp = 3,
  Spørger = 5,
  MinisterAdressat = 6,
  // ... all 23 roles defined
}

// Document-Actor relationship roles (25 types)  
enum DokumentAktørRolle {
  Taler = 1,
  Spørger = 5,
  MinisterAdressat = 6,
  Ordfører = 13,
  // ... all 25 roles defined
}
```

### 3. Status Classifications
```typescript
// Case statuses (68 different states)
enum Sagsstatus {
  Modtaget = 1,
  UnderBehandling = 2,
  BehandletFerdig = 3,
  Vedtaget = 4,
  Forkastet = 5,
  // ... all 68 statuses
}

// Actor types (13 categories)
enum Aktørtype {
  Person = 5,
  Parti = 4,
  Regering = 18,
  Udvalg = 20,
  // ... all types
}
```

### 4. Generic API Responses
```typescript
// Standard API response wrapper
interface APIResponse<T> {
  'odata.metadata': string;
  value: T[];
  'odata.count'?: string; // Present when $inlinecount used
}

// Error response types
interface APIError {
  name: 'APIError' | 'NetworkError' | 'ValidationError';
  message: string;
  status?: number;
  code?: string;
}
```

## Usage Examples

### Parliamentary Case Analysis
```typescript
interface CaseAnalysis {
  totalCases: number;
  byStatus: Record<number, number>;
  byType: Record<number, number>;
  recentActivity: number;
}

async function analyzeCases(api: DanishParliamentAPI): Promise<CaseAnalysis> {
  // Get total count with type safety
  const countResponse: APIResponse<Sag> = await api.getCases({
    top: 1,
    inlinecount: 'allpages'
  });
  
  const totalCases = parseInt(countResponse['odata.count'] || '0');
  
  // Get recent cases for analysis
  const recentCases: APIResponse<Sag> = await api.getCases({
    orderby: 'opdateringsdato desc',
    top: 1000
  });
  
  // Type-safe analysis
  const analysis: CaseAnalysis = {
    totalCases,
    byStatus: {},
    byType: {},
    recentActivity: 0
  };
  
  recentCases.value.forEach(case => {
    // Count by status
    analysis.byStatus[case.statusid] = (analysis.byStatus[case.statusid] || 0) + 1;
    
    // Count by type
    analysis.byType[case.typeid] = (analysis.byType[case.typeid] || 0) + 1;
    
    // Check if updated recently (last 7 days)
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    
    if (new Date(case.opdateringsdato) > weekAgo) {
      analysis.recentActivity++;
    }
  });
  
  return analysis;
}
```

### Voting Record Analysis
```typescript
interface VotingPattern {
  politician: string;
  totalVotes: number;
  voteBreakdown: {
    for: number;        // typeid = 1
    against: number;    // typeid = 2
    abstain: number;    // typeid = 3
    absent: number;     // typeid = 4
  };
  partyAlignment: number; // Percentage voting with party
}

async function analyzeVotingPattern(
  api: DanishParliamentAPI, 
  politicianName: string
): Promise<VotingPattern | null> {
  
  // Get all votes with type safety
  const votesResponse: APIResponse<Stemme> = await api.request('Stemme', {
    expand: 'Afstemning,Aktør',
    filter: `Aktør/navn eq '${politicianName}'`,
    top: 1000 // Batch process if needed
  });
  
  if (votesResponse.value.length === 0) {
    return null;
  }
  
  const votes = votesResponse.value;
  const pattern: VotingPattern = {
    politician: politicianName,
    totalVotes: votes.length,
    voteBreakdown: { for: 0, against: 0, abstain: 0, absent: 0 },
    partyAlignment: 0
  };
  
  // Type-safe vote counting
  votes.forEach((vote: Stemme) => {
    switch (vote.typeid) {
      case 1: pattern.voteBreakdown.for++; break;
      case 2: pattern.voteBreakdown.against++; break;
      case 3: pattern.voteBreakdown.abstain++; break;
      case 4: pattern.voteBreakdown.absent++; break;
    }
  });
  
  return pattern;
}
```

### Document Processing with Files
```typescript
interface DocumentWithFiles {
  id: number;
  title: string;
  files: {
    url: string;
    format: string;
    size?: string;
  }[];
  actors: {
    name: string;
    role: string;
  }[];
}

async function getDocumentsWithFiles(
  api: DanishParliamentAPI,
  searchTerm: string
): Promise<DocumentWithFiles[]> {
  
  const docsResponse: APIResponse<Dokument> = await api.request('Dokument', {
    filter: `substringof('${searchTerm}', titel)`,
    expand: 'Fil,DokumentAktør/Aktør,DokumentAktør/DokumentAktørRolle',
    top: 50
  });
  
  return docsResponse.value.map((doc: Dokument): DocumentWithFiles => ({
    id: doc.id,
    title: doc.titel,
    files: (doc.Fil || []).map((file: Fil) => ({
      url: file.filurl,
      format: file.format,
      size: file.størrelse
    })),
    actors: (doc.DokumentAktør || []).map((da: DokumentAktør) => ({
      name: da.Aktør?.navn || 'Unknown',
      role: da.DokumentAktørRolle?.rolle || 'Unknown Role'
    }))
  }));
}
```

## Advanced Type Features

### 1. Conditional Types for Expansions
```typescript
// Type that changes based on expansion parameter
type SagWithExpansion<T extends string> = 
  T extends 'Sagskategori' ? Sag & { Sagskategori: Sagskategori } :
  T extends 'SagAktør' ? Sag & { SagAktør: SagAktør[] } :
  T extends 'SagAktør/Aktør' ? Sag & { SagAktør: (SagAktør & { Aktør: Aktør })[] } :
  Sag;

// Usage
const casesWithCategory: SagWithExpansion<'Sagskategori'> = 
  await api.getCases({ expand: 'Sagskategori' });
```

### 2. Query Builder Types
```typescript
interface QueryOptions<T> {
  filter?: string;
  expand?: keyof T | string;
  select?: (keyof T)[];
  orderby?: keyof T | string;
  top?: number;
  skip?: number;
  inlinecount?: 'allpages' | 'none';
}

// Type-safe query building
const query: QueryOptions<Sag> = {
  filter: "year(opdateringsdato) eq 2025",
  expand: "Sagskategori", // Autocomplete works
  select: ["id", "titel", "statusid"], // Only valid fields
  orderby: "opdateringsdato desc",
  top: 100
};
```

### 3. Utility Types
```typescript
// Extract specific fields
type SagSummary = Pick<Sag, 'id' | 'titel' | 'opdateringsdato'>;

// Make relationships required
type SagWithCategory = Sag & Required<Pick<Sag, 'Sagskategori'>>;

// Union of all entity types
type AnyEntity = Sag | Aktør | Afstemning | Stemme | Dokument | Møde;

// Extract ID from any entity
type EntityId<T extends { id: number }> = T['id'];
```

## Benefits

### 1. Development Experience
- **IntelliSense**: Full autocomplete for all properties and methods
- **Error Prevention**: Catch typos and invalid field names at compile time
- **Refactoring Safety**: Rename fields across entire codebase safely
- **Documentation**: Hover tooltips show field descriptions

### 2. Runtime Safety
- **Type Guards**: Validate API responses match expected types
- **Error Handling**: Strongly typed error responses
- **Null Safety**: Optional chaining for relationship properties
- **Date Handling**: Consistent datetime string types

### 3. Team Collaboration
- **Shared Types**: Consistent interfaces across team members
- **API Contract**: Clear documentation of expected data structures
- **Version Control**: Type changes tracked in git
- **Testing**: Mock data that matches real API structure

## Next Steps

1. **[Complete Type Definitions](types.md)** - All 50 entities and enums
2. **[Type-Safe Client](client.md)** - Fully typed implementation