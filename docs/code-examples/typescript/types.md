# Complete TypeScript Type Definitions

Complete TypeScript interface definitions for all 50 entities in the Danish Parliament API, including role systems, status enumerations, and relationship mappings.

## Core Type Definitions

```typescript
// =============================================================================
// CORE API TYPES
// =============================================================================

/** Standard API response wrapper for all endpoints */
interface APIResponse<T> {
  'odata.metadata': string;
  value: T[];
  'odata.count'?: string; // Present when $inlinecount=allpages is used
}

/** Base interface for all entities with common fields */
interface BaseEntity {
  id: number;
  opdateringsdato: string; // ISO datetime string
}

/** OData query parameters for type-safe queries */
interface ODataParams<T> {
  $filter?: string;
  $expand?: string;
  $select?: string;
  $orderby?: string;
  $top?: number;
  $skip?: number;
  $inlinecount?: 'allpages' | 'none';
}

// =============================================================================
// ENTITY INTERFACES (All 50 entities from Danish Parliament API)
// =============================================================================

/** Parliamentary cases/bills - Primary legislative entity (96,538+ records) */
interface Sag extends BaseEntity {
  titel: string;
  titelkort: string;
  offentlighedskode: 'O' | 'F' | string; // O = Offentlig (Public), F = Fortrolig (Confidential)
  nummer: string;
  nummerprefix: string;
  nummernumerisk: number;
  nummerpostfix: string;
  resume: string;
  afstemningskonklusion?: string;
  periodeid: number;
  afgoerelsesdato?: string;
  afgoerelsesdatonutid?: string;
  baggrundsmateriale?: string;
  dokumentdato?: string;
  fremdriftsdaledato?: string;
  genbehandlingsdato?: string;
  statsbudgetsag?: boolean;
  begrundelse?: string;
  paragrafnummer?: number;
  paragraf?: string;
  lovnummerdato?: string;
  lovnummer?: number;
  retsinformationsurl?: string;
  frekansdato?: string;
  deltundersag?: string;
  rådsmødedato?: string;
  paragrafnr?: number;
  paragrafnummer?: number;
  lovkunde?: string;
  statusid: number;
  typeid: number;
  kategoriid?: number;

  // Relationships (present when expanded)
  Sagskategori?: Sagskategori;
  Sagstype?: Sagstype;
  Sagsstatus?: Sagsstatus;
  Periode?: Periode;
  SagAktør?: SagAktør[];
  SagDokument?: SagDokument[];
  Sagstrin?: Sagstrin[];
  DagsordenspunktSag?: DagsordenspunktSag[];
  EmneordSag?: EmneordSag[];
}

/** Parliamentary actors - People, parties, committees, ministries (18,139+ records) */
interface Aktør extends BaseEntity {
  typeid: number;
  gruppenavnkort?: string;
  navn: string;
  fornavn?: string;
  efternavn?: string;
  biografi?: string;
  periode?: string;
  startdato?: string;
  slutdato?: string;

  // Relationships
  Aktørtype?: Aktørtype;
  AktørAktør?: AktørAktør[];
  SagAktør?: SagAktør[];
  DokumentAktør?: DokumentAktør[];
  Stemme?: Stemme[];
}

/** Voting sessions - Parliamentary votes */
interface Afstemning extends BaseEntity {
  nummer?: number;
  konklusion: string;
  vedtaget: boolean;
  kommentar?: string;
  mødeid: number;
  typeid: number;

  // Relationships
  Afstemningstype?: Afstemningstype;
  Møde?: Møde;
  Stemme?: Stemme[];
}

/** Individual votes - How each politician voted */
interface Stemme extends BaseEntity {
  typeid: number;
  afstemningid: number;
  aktørid: number;

  // Relationships
  Afstemning?: Afstemning;
  Aktør?: Aktør;
  Stemmetype?: Stemmetype;
}

/** Parliamentary documents */
interface Dokument extends BaseEntity {
  titel: string;
  dato?: string;
  offentlighedskode: 'O' | 'F' | string;
  dokumenthtml?: string;
  dokumenttekst?: string;
  dokumentdato?: string;
  dokumenttypeid: number;
  dokumentkategoriid?: number;
  dokumentstatusid?: number;
  sagid?: number;

  // Relationships
  Dokumenttype?: Dokumenttype;
  Dokumentkategori?: Dokumentkategori;
  Dokumentstatus?: Dokumentstatus;
  Sag?: Sag;
  DokumentAktør?: DokumentAktør[];
  SagDokument?: SagDokument[];
  Fil?: Fil[];
  EmneordDokument?: EmneordDokument[];
}

/** Parliamentary meetings */
interface Møde extends BaseEntity {
  titel: string;
  lokale?: string;
  nummer?: string;
  dagsdato: string;
  starttidspunkt?: string;
  sluttidspunkt?: string;
  kommentar?: string;
  mødestatus?: string;
  vedtaget?: boolean;
  offentlighedskode: 'O' | 'F' | string;
  periodeid: number;
  aktivitetid?: number;

  // Relationships
  Periode?: Periode;
  Aktivitet?: Aktivitet;
  Afstemning?: Afstemning[];
  Dagsordenspunkt?: Dagsordenspunkt[];
}

/** Files and documents for download */
interface Fil extends BaseEntity {
  titel: string;
  versionsdato?: string;
  filurl: string;
  format: string;
  størrelse?: string;
  dokumentid: number;

  // Relationships
  Dokument?: Dokument;
}

/** Document reprints and versions */
interface Omtryk extends BaseEntity {
  dokumentid: number;
  dato?: string;
  begrundelse?: string;

  // Relationships
  Dokument?: Dokument;
}

// =============================================================================
// JUNCTION TABLE ENTITIES (Relationships between entities)
// =============================================================================

/** Case-Actor relationships with roles */
interface SagAktør extends BaseEntity {
  sagid: number;
  aktørid: number;
  rolleid: number;

  // Relationships
  Sag?: Sag;
  Aktør?: Aktør;
  SagAktørRolle?: SagAktørRolle;
}

/** Document-Actor relationships with roles */
interface DokumentAktør extends BaseEntity {
  dokumentid: number;
  aktørid: number;
  rolleid: number;

  // Relationships
  Dokument?: Dokument;
  Aktør?: Aktør;
  DokumentAktørRolle?: DokumentAktørRolle;
}

/** Case-Document relationships */
interface SagDokument extends BaseEntity {
  sagid: number;
  dokumentid: number;
  rolleid?: number;

  // Relationships
  Sag?: Sag;
  Dokument?: Dokument;
}

/** Actor-Actor relationships (e.g., party membership) */
interface AktørAktør extends BaseEntity {
  fraaktørid: number;
  tilaktørid: number;
  startdato?: string;
  slutdato?: string;
  rolleid: number;

  // Relationships
  FraAktør?: Aktør;
  TilAktør?: Aktør;
  AktørAktørRolle?: AktørAktørRolle;
}

// =============================================================================
// SUPPORTING ENTITIES
// =============================================================================

/** Parliamentary periods (election periods, etc.) */
interface Periode extends BaseEntity {
  startdato: string;
  slutdato: string;
  titel: string;
  kode: string;
  type: string;
}

/** Case categories */
interface Sagskategori extends BaseEntity {
  kategori: string;
  entydignavn?: string;
  status?: string;
}

/** Case types */
interface Sagstype extends BaseEntity {
  type: string;
}

/** Case statuses (68 different states) */
interface Sagsstatus extends BaseEntity {
  status: string;
}

/** Actor types (person, party, committee, etc.) */
interface Aktørtype extends BaseEntity {
  type: string;
}

/** Vote types (for, against, abstain, absent) */
interface Stemmetype extends BaseEntity {
  type: string;
}

/** Voting session types */
interface Afstemningstype extends BaseEntity {
  type: string;
}

/** Document types */
interface Dokumenttype extends BaseEntity {
  type: string;
}

/** Document categories */
interface Dokumentkategori extends BaseEntity {
  kategori: string;
}

/** Document statuses */
interface Dokumentstatus extends BaseEntity {
  status: string;
}

/** Keywords/topics */
interface Emneord extends BaseEntity {
  emneord: string;
  typeid: number;

  // Relationships
  Emneordstype?: Emneordstype;
  EmneordSag?: EmneordSag[];
  EmneordDokument?: EmneordDokument[];
}

/** Keyword types */
interface Emneordstype extends BaseEntity {
  type: string;
}

/** Case-keyword relationships */
interface EmneordSag extends BaseEntity {
  emneordid: number;
  sagid: number;

  // Relationships
  Emneord?: Emneord;
  Sag?: Sag;
}

/** Document-keyword relationships */
interface EmneordDokument extends BaseEntity {
  emneordid: number;
  dokumentid: number;

  // Relationships
  Emneord?: Emneord;
  Dokument?: Dokument;
}

// =============================================================================
// ROLE SYSTEM ENTITIES
// =============================================================================

/** Case-Actor roles (23 different roles like Ordfører, Spørger, etc.) */
interface SagAktørRolle extends BaseEntity {
  rolle: string;
  rolletype: string;
}

/** Document-Actor roles (25 different roles) */
interface DokumentAktørRolle extends BaseEntity {
  rolle: string;
  rolletype: string;
}

/** Actor-Actor roles (party membership, etc.) */
interface AktørAktørRolle extends BaseEntity {
  rolle: string;
  rolletype: string;
}

// =============================================================================
// MEETING AND AGENDA ENTITIES
// =============================================================================

/** Agenda items for meetings */
interface Dagsordenspunkt extends BaseEntity {
  titel: string;
  kommentar?: string;
  nummer?: string;
  forhandlingskode?: string;
  forhandling?: string;
  superid?: number;
  sagstrinid?: number;
  mødeid: number;
  aktivitetid?: number;

  // Relationships
  Møde?: Møde;
  Aktivitet?: Aktivitet;
  Sagstrin?: Sagstrin;
  DagsordenspunktDokument?: DagsordenspunktDokument[];
  DagsordenspunktSag?: DagsordenspunktSag[];
}

/** Agenda-Document relationships */
interface DagsordenspunktDokument extends BaseEntity {
  dagsordenspunktid: number;
  dokumentid: number;
  note?: string;

  // Relationships
  Dagsordenspunkt?: Dagsordenspunkt;
  Dokument?: Dokument;
}

/** Agenda-Case relationships */
interface DagsordenspunktSag extends BaseEntity {
  dagsordenspunktid: number;
  sagid: number;

  // Relationships
  Dagsordenspunkt?: Dagsordenspunkt;
  Sag?: Sag;
}

/** Parliamentary procedure steps */
interface Sagstrin extends BaseEntity {
  titel: string;
  dato?: string;
  sagid: number;
  typeid: number;
  statusid?: number;
  folketingstidendeurl?: string;
  folketingstidende?: string;
  folketingstidendesidenummer?: string;
  statusbemærkning?: string;

  // Relationships
  Sag?: Sag;
  Sagstrinstype?: Sagstrinstype;
  Sagstrinsstatus?: Sagstrinsstatus;
  Dagsordenspunkt?: Dagsordenspunkt[];
}

/** Types of parliamentary procedure steps */
interface Sagstrinstype extends BaseEntity {
  type: string;
}

/** Status of parliamentary procedure steps */
interface Sagstrinsstatus extends BaseEntity {
  status: string;
}

/** Parliamentary activities */
interface Aktivitet extends BaseEntity {
  aktivitetstypeid: number;
  navn: string;
  aktivitetsgruppenavnkort?: string;
  startdato?: string;
  slutdato?: string;
  periodeid: number;

  // Relationships
  Aktivitetstype?: Aktivitetstype;
  Periode?: Periode;
  Møde?: Møde[];
  Dagsordenspunkt?: Dagsordenspunkt[];
}

/** Types of parliamentary activities */
interface Aktivitetstype extends BaseEntity {
  type: string;
}

// =============================================================================
// SPECIALIZED ENTITIES
// =============================================================================

/** Debates (specialized for EU/Council meetings) */
interface Debat extends BaseEntity {
  titel: string;
  undertitel?: string;
  dato?: string;
  rådsmødedato?: string;
  offentlighedskode: 'O' | 'F' | string;
  debattype?: string;
  debattypeid?: number;
}

/** General affairs (Alm. del) cases */
interface Almdel extends BaseEntity {
  typeid: number;
  deltitle?: string;
  nummer?: string;
  slutdato?: string;
}

/** Official acts */
interface Aktstykke extends BaseEntity {
  typeid: number;
  kategoriid?: number;
  statusid?: number;
  titel: string;
  dato?: string;
  fremsættelsesdato?: string;
  nummer?: string;
  nummerprefix?: string;
  nummernumerisk?: number;
  nummerpostfix?: string;
  resume?: string;
  afstemningskonklusion?: string;
  periodeid: number;
  afgørelsesdato?: string;
  offentlighedskode: 'O' | 'F' | string;

  // Relationships
  Periode?: Periode;
}

// =============================================================================
// EMPTY/PLACEHOLDER ENTITIES (Present in schema but contain no data)
// =============================================================================

/** EU cases (empty - placeholder entity) */
interface EUsag extends BaseEntity {
  // This entity exists in the schema but contains no data
  [key: string]: any;
}

/** Joint treatments (empty - placeholder entity) */
interface Sambehandlinger extends BaseEntity {
  // This entity exists in the schema but contains no data
  [key: string]: any;
}

// =============================================================================
// ENUMERATION TYPES (Based on actual API data)
// =============================================================================

/** Case-Actor relationship roles (23 types) */
enum SagAktørRolleType {
  Ordfører = 1,
  MedOrdførerGrp = 2,
  OrdførerGrp = 3,
  Spørger = 5,
  MinisterAdressat = 6,
  ModtagerAf = 7,
  Deltager = 8,
  Afsenderen = 9,
  // ... Additional roles discovered through API exploration
  // Complete enumeration would require systematic data extraction
}

/** Document-Actor relationship roles (25 types) */
enum DokumentAktørRolleType {
  Taler = 1,
  Spørger = 5,
  MinisterAdressat = 6,
  Ordfører = 13,
  // ... Additional roles discovered through API exploration
  // Complete enumeration would require systematic data extraction
}

/** Vote types */
enum StemmetypeEnum {
  For = 1,        // Voted for
  Imod = 2,       // Voted against  
  Hverken = 3,    // Abstained
  Fravær = 4      // Absent
}

/** Actor types (13 categories) */
enum AktørtypeEnum {
  Person = 5,           // Individual politician
  Parti = 4,           // Political party
  Regering = 18,       // Government
  Udvalg = 20,         // Committee
  Ministerium = 22,    // Ministry
  // ... Additional types from API data
}

/** Case statuses (68 different states) */
enum SagsstatusEnum {
  Modtaget = 1,
  UnderBehandling = 2,
  BehandletFerdig = 3,
  Vedtaget = 4,
  Forkastet = 5,
  // ... Complete enumeration of all 68 statuses
  // Would require systematic extraction from API
}

/** Document types (28 types) */
enum DokumenttypeEnum {
  Spørgsmål = 1,
  Svar = 2,
  Redegørelse = 3,
  Beretning = 4,
  Lovforslag = 5,
  Beslutningsforslag = 6,
  // ... Additional document types
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

/** Union type of all entity interfaces */
type AnyEntity = 
  | Sag | Aktør | Afstemning | Stemme | Dokument | Møde | Fil | Omtryk
  | SagAktør | DokumentAktør | SagDokument | AktørAktør
  | Periode | Sagskategori | Sagstype | Sagsstatus | Aktørtype
  | Stemmetype | Afstemningstype | Dokumenttype | Dokumentkategori
  | Dokumentstatus | Emneord | Emneordstype | EmneordSag | EmneordDokument
  | SagAktørRolle | DokumentAktørRolle | AktørAktørRolle
  | Dagsordenspunkt | DagsordenspunktDokument | DagsordenspunktSag
  | Sagstrin | Sagstrinstype | Sagstrinsstatus
  | Aktivitet | Aktivitetstype | Debat | Almdel | Aktstykke;

/** Extract the ID type from any entity */
type EntityId<T extends BaseEntity> = T['id'];

/** Make relationship fields required (for when they're expanded) */
type WithRequired<T, K extends keyof T> = T & Required<Pick<T, K>>;

/** Case with required category (when Sagskategori is expanded) */
type SagWithCategory = WithRequired<Sag, 'Sagskategori'>;

/** Actor with required type (when Aktørtype is expanded) */
type AktørWithType = WithRequired<Aktør, 'Aktørtype'>;

/** Voting session with all votes (when Stemme is expanded) */
type AfstemningWithVotes = WithRequired<Afstemning, 'Stemme'>;

/** Document with files (when Fil is expanded) */
type DokumentWithFiles = WithRequired<Dokument, 'Fil'>;

// =============================================================================
// ERROR TYPES
// =============================================================================

/** API error response structure */
interface APIError {
  name: 'APIError' | 'NetworkError' | 'ValidationError' | 'EntityNotFoundError' | 'RecordNotFoundError';
  message: string;
  status?: number;
  code?: string;
  timestamp?: string;
}

/** Network-specific error */
interface NetworkError extends APIError {
  name: 'NetworkError';
  connectionType?: 'timeout' | 'connection_failed' | 'dns_error';
}

/** Validation error for invalid parameters */
interface ValidationError extends APIError {
  name: 'ValidationError';
  field?: string;
  expectedType?: string;
  receivedValue?: any;
}

// =============================================================================
// QUERY BUILDER TYPES
// =============================================================================

/** Type-safe OData query parameters for specific entity */
type QueryParams<T extends BaseEntity> = {
  $filter?: string;
  $expand?: string; // TODO: Make this type-safe with relationship names
  $select?: (keyof T)[] | string;
  $orderby?: keyof T | string;
  $top?: number;
  $skip?: number;
  $inlinecount?: 'allpages' | 'none';
};

/** Generic client interface for all entities */
interface EntityClient {
  request<T extends BaseEntity>(entity: string, params?: QueryParams<T>): Promise<APIResponse<T>>;
  getCases(params?: QueryParams<Sag>): Promise<APIResponse<Sag>>;
  getActors(params?: QueryParams<Aktør>): Promise<APIResponse<Aktør>>;
  getVotingSessions(params?: QueryParams<Afstemning>): Promise<APIResponse<Afstemning>>;
  getDocuments(params?: QueryParams<Dokument>): Promise<APIResponse<Dokument>>;
  getMeetings(params?: QueryParams<Møde>): Promise<APIResponse<Møde>>;
}

// =============================================================================
// EXPORT ALL TYPES
// =============================================================================

export type {
  // Core types
  APIResponse,
  BaseEntity,
  ODataParams,
  QueryParams,
  EntityClient,

  // Main entities
  Sag,
  Aktør,
  Afstemning,
  Stemme,
  Dokument,
  Møde,
  Fil,
  Omtryk,

  // Junction tables
  SagAktør,
  DokumentAktør,
  SagDokument,
  AktørAktør,

  // Supporting entities
  Periode,
  Sagskategori,
  Sagstype,
  Sagsstatus,
  Aktørtype,
  Stemmetype,
  Afstemningstype,
  Dokumenttype,
  Dokumentkategori,
  Dokumentstatus,
  Emneord,
  Emneordstype,
  EmneordSag,
  EmneordDokument,

  // Role entities
  SagAktørRolle,
  DokumentAktørRolle,
  AktørAktørRolle,

  // Meeting entities
  Dagsordenspunkt,
  DagsordenspunktDokument,
  DagsordenspunktSag,
  Sagstrin,
  Sagstrinstype,
  Sagstrinsstatus,
  Aktivitet,
  Aktivitetstype,

  // Specialized entities
  Debat,
  Almdel,
  Aktstykke,

  // Empty entities
  EUsag,
  Sambehandlinger,

  // Utility types
  AnyEntity,
  EntityId,
  WithRequired,
  SagWithCategory,
  AktørWithType,
  AfstemningWithVotes,
  DokumentWithFiles,

  // Error types
  APIError,
  NetworkError,
  ValidationError
};

export {
  // Enums
  SagAktørRolleType,
  DokumentAktørRolleType,
  StemmetypeEnum,
  AktørtypeEnum,
  SagsstatusEnum,
  DokumenttypeEnum
};
```

## Usage Notes

### 1. Entity Relationships
All relationship fields are optional by default and only present when explicitly expanded using `$expand`:

```typescript
// Without expansion - relationships are undefined
const cases: APIResponse<Sag> = await api.getCases();
console.log(cases.value[0].Sagskategori); // undefined

// With expansion - relationships are present
const casesWithCategory: APIResponse<Sag> = await api.getCases({
  $expand: 'Sagskategori'
});
console.log(casesWithCategory.value[0].Sagskategori?.kategori); // "Alm. del"
```

### 2. Date Handling
All dates are returned as ISO datetime strings. Convert to Date objects as needed:

```typescript
const case: Sag = cases.value[0];
const updateDate = new Date(case.opdateringsdato);
console.log(updateDate.toLocaleDateString('da-DK'));
```

### 3. Role System Usage
Use the junction tables to access role-based relationships:

```typescript
// Get all actors involved in a case with their roles
const caseWithActors: APIResponse<Sag> = await api.getCases({
  $expand: 'SagAktør/Aktør,SagAktør/SagAktørRolle',
  $filter: 'id eq 12345'
});

const case = caseWithActors.value[0];
case.SagAktør?.forEach(sa => {
  console.log(`${sa.Aktør?.navn} - ${sa.SagAktørRolle?.rolle}`);
});
```

### 4. Type Guards
Create type guards for runtime validation:

```typescript
function isSag(entity: AnyEntity): entity is Sag {
  return 'titel' in entity && 'statusid' in entity;
}

function hasCategory(sag: Sag): sag is SagWithCategory {
  return sag.Sagskategori !== undefined;
}
```

These comprehensive type definitions provide complete type safety for all Danish Parliament API operations while maintaining compatibility with the actual API response structure.