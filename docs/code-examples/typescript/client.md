# TypeScript Client Implementation

A fully type-safe TypeScript client for the Danish Parliament API with complete IntelliSense support, compile-time error checking, and runtime type validation.

## Complete Type-Safe Client

```typescript
import {
  APIResponse,
  BaseEntity,
  QueryParams,
  Sag,
  Aktør,
  Afstemning,
  Stemme,
  Dokument,
  Møde,
  Fil,
  APIError,
  NetworkError,
  ValidationError,
  AnyEntity,
  SagWithCategory,
  AktørWithType
} from './types';

/**
 * Production-ready TypeScript client for Danish Parliament API
 * 
 * Features:
 * - Complete type safety for all 50 entities
 * - Runtime type validation
 * - Comprehensive error handling with typed errors
 * - Generic request methods with type inference
 * - Async iterator support for pagination
 * - Built-in rate limiting and retry logic
 */
class DanishParliamentAPIClient {
  private readonly baseUrl = 'https://oda.ft.dk/api/';
  private readonly timeout: number;
  private readonly retryAttempts: number;
  private readonly requestDelay: number;
  private lastRequestTime = 0;

  constructor(options: {
    timeout?: number;
    retryAttempts?: number;
    requestDelay?: number;
  } = {}) {
    this.timeout = options.timeout ?? 30000;
    this.retryAttempts = options.retryAttempts ?? 3;
    this.requestDelay = options.requestDelay ?? 100;
  }

  /**
   * Generic request method with complete type safety
   */
  async request<T extends BaseEntity>(
    entity: string,
    params: QueryParams<T> = {}
  ): Promise<APIResponse<T>> {
    const url = this.buildUrl(entity, params);
    return this.makeRequest<T>(url);
  }

  /**
   * Get parliamentary cases with type safety
   */
  async getCases(params: QueryParams<Sag> = {}): Promise<APIResponse<Sag>> {
    return this.request<Sag>('Sag', params);
  }

  /**
   * Get parliamentary actors with type safety
   */
  async getActors(params: QueryParams<Aktør> = {}): Promise<APIResponse<Aktør>> {
    return this.request<Aktør>('Aktør', params);
  }

  /**
   * Get voting sessions with type safety
   */
  async getVotingSessions(params: QueryParams<Afstemning> = {}): Promise<APIResponse<Afstemning>> {
    return this.request<Afstemning>('Afstemning', params);
  }

  /**
   * Get individual votes with type safety
   */
  async getVotes(params: QueryParams<Stemme> = {}): Promise<APIResponse<Stemme>> {
    return this.request<Stemme>('Stemme', params);
  }

  /**
   * Get documents with type safety
   */
  async getDocuments(params: QueryParams<Dokument> = {}): Promise<APIResponse<Dokument>> {
    return this.request<Dokument>('Dokument', params);
  }

  /**
   * Get meetings with type safety
   */
  async getMeetings(params: QueryParams<Møde> = {}): Promise<APIResponse<Møde>> {
    return this.request<Møde>('Møde', params);
  }

  /**
   * Type-safe async pagination generator
   */
  async* paginateAll<T extends BaseEntity>(
    entity: string,
    options: {
      batchSize?: number;
      maxRecords?: number;
      params?: QueryParams<T>;
    } = {}
  ): AsyncGenerator<T, void, unknown> {
    const { batchSize = 100, maxRecords = Infinity, params = {} } = options;
    
    let skip = 0;
    let totalYielded = 0;
    const safeBatchSize = Math.min(batchSize, 100);

    while (totalYielded < maxRecords && skip < 100000) {
      const requestParams: QueryParams<T> = {
        ...params,
        $top: safeBatchSize,
        $skip: skip
      };

      try {
        const response = await this.request<T>(entity, requestParams);
        
        if (!response.value || response.value.length === 0) {
          break;
        }

        for (const record of response.value) {
          if (totalYielded >= maxRecords) {
            return;
          }

          // Runtime type validation
          if (this.validateEntity(record)) {
            yield record;
            totalYielded++;
          }
        }

        skip += safeBatchSize;

      } catch (error) {
        console.error(`Pagination error at skip=${skip}:`, error);
        break;
      }
    }
  }

  /**
   * Get entity count with type safety
   */
  async getEntityCount(entity: string): Promise<number> {
    const response = await this.request(entity, {
      $inlinecount: 'allpages',
      $top: 1
    });

    const countStr = response['odata.count'] || '0';
    return parseInt(countStr, 10);
  }

  /**
   * Type-safe batch requests
   */
  async batchRequests<T extends BaseEntity>(
    requests: Array<{
      entity: string;
      params?: QueryParams<T>;
    }>,
    maxConcurrent = 5
  ): Promise<APIResponse<T>[]> {
    const semaphore = new Semaphore(maxConcurrent);
    
    const executeRequest = async (request: { entity: string; params?: QueryParams<T> }) => {
      await semaphore.acquire();
      try {
        return await this.request<T>(request.entity, request.params || {});
      } finally {
        semaphore.release();
      }
    };

    return Promise.all(requests.map(executeRequest));
  }

  // =============================================================================
  // SPECIALIZED TYPE-SAFE METHODS
  // =============================================================================

  /**
   * Get cases with categories (strongly typed result)
   */
  async getCasesWithCategories(
    params: Omit<QueryParams<Sag>, '$expand'> = {}
  ): Promise<APIResponse<SagWithCategory>> {
    const response = await this.getCases({
      ...params,
      $expand: 'Sagskategori'
    });

    // Runtime validation that categories are present
    const validatedValue = response.value.filter((sag): sag is SagWithCategory => 
      sag.Sagskategori !== undefined
    );

    return {
      ...response,
      value: validatedValue
    };
  }

  /**
   * Get actors with types (strongly typed result)
   */
  async getActorsWithTypes(
    params: Omit<QueryParams<Aktør>, '$expand'> = {}
  ): Promise<APIResponse<AktørWithType>> {
    const response = await this.getActors({
      ...params,
      $expand: 'Aktørtype'
    });

    const validatedValue = response.value.filter((actor): actor is AktørWithType => 
      actor.Aktørtype !== undefined
    );

    return {
      ...response,
      value: validatedValue
    };
  }

  /**
   * Get voting records for a politician with full type safety
   */
  async getVotingRecords(
    politicianName: string,
    options: {
      limit?: number;
      includeVotingDetails?: boolean;
    } = {}
  ): Promise<Stemme[]> {
    const { limit = 1000, includeVotingDetails = true } = options;
    
    const expandParts = ['Aktør'];
    if (includeVotingDetails) {
      expandParts.push('Afstemning');
    }

    const allVotes: Stemme[] = [];
    let skip = 0;
    const batchSize = 100;

    while (allVotes.length < limit && skip < 10000) {
      const params: QueryParams<Stemme> = {
        $expand: expandParts.join(','),
        $filter: `Aktør/navn eq '${politicianName}'`,
        $top: batchSize,
        $skip: skip
      };

      const response = await this.getVotes(params);
      
      if (!response.value || response.value.length === 0) {
        break;
      }

      allVotes.push(...response.value);
      skip += batchSize;
    }

    return allVotes.slice(0, limit);
  }

  /**
   * Search with type-safe filters
   */
  async searchCases(searchOptions: {
    title?: string;
    year?: number;
    status?: number;
    type?: number;
    includeCategory?: boolean;
    includeActors?: boolean;
    limit?: number;
  }): Promise<APIResponse<Sag>> {
    const { 
      title, 
      year, 
      status, 
      type, 
      includeCategory = false, 
      includeActors = false,
      limit = 100 
    } = searchOptions;

    // Build filter conditions
    const filterConditions: string[] = [];
    
    if (title) {
      filterConditions.push(`substringof('${title}', titel)`);
    }
    
    if (year) {
      filterConditions.push(`year(opdateringsdato) eq ${year}`);
    }
    
    if (status !== undefined) {
      filterConditions.push(`statusid eq ${status}`);
    }
    
    if (type !== undefined) {
      filterConditions.push(`typeid eq ${type}`);
    }

    // Build expand clause
    const expandParts: string[] = [];
    if (includeCategory) expandParts.push('Sagskategori');
    if (includeActors) expandParts.push('SagAktør/Aktør');

    const params: QueryParams<Sag> = {
      $top: Math.min(limit, 100)
    };

    if (filterConditions.length > 0) {
      params.$filter = filterConditions.join(' and ');
    }

    if (expandParts.length > 0) {
      params.$expand = expandParts.join(',');
    }

    return this.getCases(params);
  }

  /**
   * Get recent changes with type safety
   */
  async getRecentChanges<T extends BaseEntity>(
    entity: string,
    hoursBack = 24
  ): Promise<APIResponse<T>> {
    const cutoffTime = new Date();
    cutoffTime.setHours(cutoffTime.getHours() - hoursBack);
    const isoTime = cutoffTime.toISOString().slice(0, 19);

    const params: QueryParams<T> = {
      $filter: `opdateringsdato gt datetime'${isoTime}'`,
      $orderby: 'opdateringsdato desc',
      $top: 100
    };

    return this.request<T>(entity, params);
  }

  // =============================================================================
  // PRIVATE HELPER METHODS
  // =============================================================================

  private async rateLimit(): Promise<void> {
    const elapsed = Date.now() - this.lastRequestTime;
    if (elapsed < this.requestDelay) {
      await this.sleep(this.requestDelay - elapsed);
    }
    this.lastRequestTime = Date.now();
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private buildUrl<T extends BaseEntity>(entity: string, params: QueryParams<T>): string {
    const url = `${this.baseUrl}${entity}`;
    
    if (Object.keys(params).length === 0) {
      return url;
    }

    const queryParts: string[] = [];
    
    for (const [key, value] of Object.entries(params)) {
      if (value !== null && value !== undefined) {
        const encodedKey = key.startsWith('$') ? 
          encodeURIComponent(key) : key;
        
        let encodedValue: string;
        if (Array.isArray(value)) {
          // Handle select arrays
          encodedValue = encodeURIComponent(value.join(','));
        } else {
          encodedValue = encodeURIComponent(String(value));
        }
        
        queryParts.push(`${encodedKey}=${encodedValue}`);
      }
    }

    return `${url}?${queryParts.join('&')}`;
  }

  private async makeRequest<T extends BaseEntity>(url: string): Promise<APIResponse<T>> {
    await this.rateLimit();

    for (let attempt = 0; attempt < this.retryAttempts; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const response = await fetch(url, {
          signal: controller.signal,
          headers: {
            'Accept': 'application/json',
            'User-Agent': 'TypeScript-DanishParliamentAPI/1.0'
          }
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          const data = await response.json();
          return this.validateResponse<T>(data);
        }

        // Handle HTTP errors with typed exceptions
        switch (response.status) {
          case 400:
            throw new ValidationError(
              `Invalid query parameters. Check $expand and $filter syntax. URL: ${url}`,
              'INVALID_QUERY'
            );
          
          case 404:
            if (url.includes('/api/') && url.split('/').length === 5) {
              throw new APIError(`Entity not found: ${url.split('/').pop()}`, 'ENTITY_NOT_FOUND');
            } else {
              throw new APIError(`Record not found: ${url}`, 'RECORD_NOT_FOUND');
            }
          
          case 501:
            throw new APIError(
              'Write operations are not supported by this API',
              'UNSUPPORTED_OPERATION'
            );
          
          default:
            throw new APIError(`HTTP ${response.status}: ${response.statusText}`, 'HTTP_ERROR');
        }

      } catch (error) {
        if (error instanceof APIError) {
          throw error;
        }

        if (error.name === 'AbortError') {
          if (attempt < this.retryAttempts - 1) {
            const waitTime = Math.pow(2, attempt) * 1000;
            await this.sleep(waitTime);
            continue;
          }
          throw new NetworkError(`Request timed out after ${this.timeout}ms`, 'TIMEOUT');
        }

        if (error.name === 'TypeError' && error.message.includes('fetch')) {
          if (attempt < this.retryAttempts - 1) {
            const waitTime = Math.pow(2, attempt) * 1000;
            await this.sleep(waitTime);
            continue;
          }
          throw new NetworkError(`Network error: ${error.message}`, 'CONNECTION_ERROR');
        }

        throw new APIError(`Unexpected error: ${error.message}`, 'UNKNOWN_ERROR');
      }
    }

    throw new NetworkError(`Request failed after ${this.retryAttempts} attempts`, 'MAX_RETRIES_EXCEEDED');
  }

  private validateResponse<T extends BaseEntity>(data: any): APIResponse<T> {
    // Runtime validation of API response structure
    if (!data || typeof data !== 'object') {
      throw new ValidationError('Invalid response format', 'INVALID_RESPONSE_FORMAT');
    }

    if (!data['odata.metadata']) {
      throw new ValidationError('Missing odata.metadata field', 'MISSING_METADATA');
    }

    if (!Array.isArray(data.value)) {
      throw new ValidationError('Response value is not an array', 'INVALID_VALUE_FORMAT');
    }

    return data as APIResponse<T>;
  }

  private validateEntity(entity: any): entity is BaseEntity {
    // Basic validation that entity has required fields
    return entity && 
           typeof entity === 'object' && 
           typeof entity.id === 'number' &&
           typeof entity.opdateringsdato === 'string';
  }
}

// =============================================================================
// SPECIALIZED TYPE-SAFE ERROR CLASSES
// =============================================================================

class APIError extends Error {
  readonly name = 'APIError' as const;
  readonly code: string;
  readonly timestamp: string;

  constructor(message: string, code: string) {
    super(message);
    this.code = code;
    this.timestamp = new Date().toISOString();
  }
}

class NetworkError extends APIError {
  readonly name = 'NetworkError' as const;
  readonly connectionType: 'timeout' | 'connection_failed' | 'dns_error' | 'unknown';

  constructor(message: string, connectionType: NetworkError['connectionType']) {
    super(message, 'NETWORK_ERROR');
    this.connectionType = connectionType;
  }
}

class ValidationError extends APIError {
  readonly name = 'ValidationError' as const;
  readonly field?: string;

  constructor(message: string, code: string, field?: string) {
    super(message, code);
    this.field = field;
  }
}

// =============================================================================
// UTILITY CLASSES
// =============================================================================

class Semaphore {
  private current = 0;
  private queue: (() => void)[] = [];

  constructor(private max: number) {}

  async acquire(): Promise<void> {
    return new Promise(resolve => {
      if (this.current < this.max) {
        this.current++;
        resolve();
      } else {
        this.queue.push(resolve);
      }
    });
  }

  release(): void {
    this.current--;
    if (this.queue.length > 0) {
      this.current++;
      const resolve = this.queue.shift()!;
      resolve();
    }
  }
}

// =============================================================================
// USAGE EXAMPLES
// =============================================================================

/**
 * Example usage with full type safety
 */
async function exampleUsage() {
  const api = new DanishParliamentAPIClient({
    timeout: 60000,
    retryAttempts: 5,
    requestDelay: 200
  });

  try {
    // Type-safe case retrieval with IntelliSense
    const cases = await api.getCases({
      $filter: "substringof('klima', titel)",
      $expand: "Sagskategori",
      $orderby: "opdateringsdato desc",
      $top: 50
    });

    // Full type safety - TypeScript knows all properties
    cases.value.forEach(case => {
      console.log(`Case ${case.id}: ${case.titel}`);
      console.log(`Status: ${case.statusid}`);
      console.log(`Category: ${case.Sagskategori?.kategori ?? 'No category'}`);
      console.log(`Updated: ${new Date(case.opdateringsdato).toLocaleDateString()}`);
    });

    // Type-safe pagination
    console.log('Processing all climate cases...');
    let count = 0;
    for await (const case of api.paginateAll<Sag>('Sag', {
      maxRecords: 500,
      params: { $filter: "substringof('klima', titel)" }
    })) {
      count++;
      console.log(`${count}: ${case.titel.substring(0, 50)}...`);
    }

    // Strongly typed specialized methods
    const casesWithCategories = await api.getCasesWithCategories({
      $filter: "year(opdateringsdato) eq 2025",
      $top: 20
    });

    // TypeScript ensures Sagskategori is always present
    casesWithCategories.value.forEach(case => {
      console.log(`${case.titel} - ${case.Sagskategori.kategori}`); // No optional chaining needed
    });

    // Type-safe voting analysis
    const votes = await api.getVotingRecords('Frank Aaen', {
      limit: 100,
      includeVotingDetails: true
    });

    console.log(`Found ${votes.length} votes`);
    
    // Group votes by type with type safety
    const votesByType = votes.reduce((acc, vote) => {
      const type = vote.typeid;
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {} as Record<number, number>);

    console.log('Vote breakdown:', votesByType);

  } catch (error) {
    // Strongly typed error handling
    if (error instanceof ValidationError) {
      console.error('Validation error:', error.message);
      console.error('Field:', error.field);
    } else if (error instanceof NetworkError) {
      console.error('Network error:', error.message);
      console.error('Connection type:', error.connectionType);
    } else if (error instanceof APIError) {
      console.error('API error:', error.message);
      console.error('Code:', error.code);
    } else {
      console.error('Unexpected error:', error);
    }
  }
}

// =============================================================================
// ADVANCED TYPE-SAFE PATTERNS
// =============================================================================

/**
 * Type-safe query builder
 */
class QueryBuilder<T extends BaseEntity> {
  private params: QueryParams<T> = {};

  filter(condition: string): this {
    this.params.$filter = this.params.$filter 
      ? `(${this.params.$filter}) and (${condition})`
      : condition;
    return this;
  }

  expand(relationship: string): this {
    this.params.$expand = this.params.$expand
      ? `${this.params.$expand},${relationship}`
      : relationship;
    return this;
  }

  select(fields: (keyof T)[]): this {
    this.params.$select = fields;
    return this;
  }

  orderBy(field: keyof T, direction: 'asc' | 'desc' = 'asc'): this {
    this.params.$orderby = `${String(field)} ${direction}`;
    return this;
  }

  top(count: number): this {
    this.params.$top = Math.min(count, 100);
    return this;
  }

  skip(count: number): this {
    this.params.$skip = count;
    return this;
  }

  inlineCount(): this {
    this.params.$inlinecount = 'allpages';
    return this;
  }

  build(): QueryParams<T> {
    return { ...this.params };
  }
}

// Usage example
const query = new QueryBuilder<Sag>()
  .filter("substringof('klima', titel)")
  .expand('Sagskategori')
  .select(['id', 'titel', 'statusid'])
  .orderBy('opdateringsdato', 'desc')
  .top(50)
  .inlineCount()
  .build();

// Export everything
export {
  DanishParliamentAPIClient,
  APIError,
  NetworkError,
  ValidationError,
  QueryBuilder,
  Semaphore
};

export default DanishParliamentAPIClient;
```

## Key Features

### 1. Complete Type Safety
- **Compile-time validation**: Catch errors before runtime
- **IntelliSense support**: Full autocomplete for all properties
- **Type inference**: Automatic type detection for returned data
- **Generic methods**: Flexible, reusable code with type constraints

### 2. Runtime Validation
- **Response structure validation**: Ensures API responses match expected format
- **Entity validation**: Basic checks for required fields
- **Error type validation**: Strongly typed error handling

### 3. Advanced Error Handling
```typescript
try {
  const cases = await api.getCases({ $filter: "invalid syntax" });
} catch (error) {
  if (error instanceof ValidationError) {
    // Handle validation errors specifically
    console.log(`Validation failed: ${error.message}`);
    console.log(`Field: ${error.field}`);
  } else if (error instanceof NetworkError) {
    // Handle network errors
    console.log(`Network issue: ${error.connectionType}`);
  }
}
```

### 4. Type-Safe Pagination
```typescript
// Process all records with full type safety
for await (const actor of api.paginateAll<Aktør>('Aktør', {
  maxRecords: 1000,
  params: { $filter: "aktørtypeid eq 5" } // Politicians only
})) {
  // actor is strongly typed as Aktør
  console.log(`${actor.navn}: ${actor.biografi?.substring(0, 100)}...`);
}
```

### 5. Specialized Methods
```typescript
// Get cases with guaranteed categories (no optional chaining needed)
const casesWithCategories = await api.getCasesWithCategories({
  $filter: "year(opdateringsdato) eq 2025"
});

casesWithCategories.value.forEach(case => {
  // TypeScript knows Sagskategori is always present
  console.log(`${case.titel} - ${case.Sagskategori.kategori}`);
});
```

## Benefits

1. **Developer Experience**: Full IntelliSense, compile-time error checking
2. **Maintenance**: Refactoring safety, clear interfaces
3. **Reliability**: Runtime validation, comprehensive error handling  
4. **Performance**: Efficient pagination, concurrent request handling
5. **Documentation**: Self-documenting code with TypeScript interfaces

This type-safe client provides a robust foundation for building production applications with the Danish Parliament API while maintaining complete type safety throughout your codebase.