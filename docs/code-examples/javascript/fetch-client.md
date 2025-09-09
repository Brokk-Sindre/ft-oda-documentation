# JavaScript Fetch Client

Complete, production-ready JavaScript client for the Danish Parliament API using modern fetch API.

## Complete Client Implementation

```javascript
/**
 * Production-ready Danish Parliament API Client
 * 
 * Features:
 * - Modern fetch API with async/await
 * - Comprehensive error handling
 * - Automatic retry with exponential backoff
 * - Rate limiting and request throttling
 * - Memory-efficient pagination
 * - Browser and Node.js compatible
 */

// Polyfill for Node.js < 18 (uncomment if needed)
// import fetch from 'node-fetch';

class DanishParliamentAPI {
  /**
   * Initialize the API client
   * 
   * @param {Object} options - Configuration options
   * @param {number} options.timeout - Request timeout in milliseconds (default: 30000)
   * @param {number} options.retryAttempts - Number of retry attempts (default: 3)
   * @param {number} options.requestDelay - Minimum delay between requests in ms (default: 100)
   */
  constructor(options = {}) {
    this.baseUrl = 'https://oda.ft.dk/api/';
    this.timeout = options.timeout || 30000;
    this.retryAttempts = options.retryAttempts || 3;
    this.requestDelay = options.requestDelay || 100;
    this.lastRequestTime = 0;
  }

  /**
   * Enforce rate limiting between requests
   */
  async _rateLimit() {
    const elapsed = Date.now() - this.lastRequestTime;
    if (elapsed < this.requestDelay) {
      await this._sleep(this.requestDelay - elapsed);
    }
    this.lastRequestTime = Date.now();
  }

  /**
   * Sleep for specified milliseconds
   */
  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Build properly encoded URL with OData parameters
   * 
   * @param {string} entity - Entity name (e.g., 'Sag', 'Aktør')
   * @param {Object} params - OData parameters
   * @returns {string} Complete URL with encoded parameters
   */
  _buildUrl(entity, params = {}) {
    const url = `${this.baseUrl}${entity}`;
    
    if (Object.keys(params).length === 0) {
      return url;
    }

    const queryParts = [];
    for (const [key, value] of Object.entries(params)) {
      if (value !== null && value !== undefined) {
        // Ensure $ parameters are properly encoded
        const encodedKey = key.startsWith('$') ? 
          encodeURIComponent(key) : key;
        const encodedValue = encodeURIComponent(value);
        queryParts.push(`${encodedKey}=${encodedValue}`);
      }
    }

    return `${url}?${queryParts.join('&')}`;
  }

  /**
   * Make HTTP request with retry logic and error handling
   * 
   * @param {string} url - URL to request
   * @param {number} maxRetries - Override default retry attempts
   * @returns {Promise<Object>} Parsed JSON response
   */
  async _makeRequest(url, maxRetries = this.retryAttempts) {
    await this._rateLimit();

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        // Create AbortController for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const response = await fetch(url, {
          signal: controller.signal,
          headers: {
            'Accept': 'application/json',
            'User-Agent': 'DanishParliamentAPI-JS/1.0'
          }
        });

        clearTimeout(timeoutId);

        // Handle HTTP status codes
        if (response.ok) {
          return await response.json();
        }

        switch (response.status) {
          case 400:
            throw new APIError(
              `Invalid query parameters. Check $expand and $filter syntax. URL: ${url}`,
              'INVALID_QUERY'
            );
          
          case 404:
            if (url.includes('/api/') && url.split('/').length === 5) {
              throw new EntityNotFoundError(`Entity not found: ${url.split('/').pop()}`);
            } else {
              throw new RecordNotFoundError(`Record not found: ${url}`);
            }
          
          case 501:
            throw new UnsupportedOperationError(
              'Write operations are not supported by this API'
            );
          
          default:
            throw new APIError(`HTTP ${response.status}: ${response.statusText}`);
        }

      } catch (error) {
        // Handle AbortError (timeout)
        if (error.name === 'AbortError') {
          if (attempt < maxRetries - 1) {
            const waitTime = Math.pow(2, attempt) * 1000; // Exponential backoff
            console.warn(`Request timeout, retrying in ${waitTime}ms... (attempt ${attempt + 1}/${maxRetries})`);
            await this._sleep(waitTime);
            continue;
          }
          throw new NetworkError(`Request timed out after ${this.timeout}ms`);
        }

        // Handle network errors
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
          if (attempt < maxRetries - 1) {
            const waitTime = Math.pow(2, attempt) * 1000;
            console.warn(`Network error, retrying in ${waitTime}ms... (attempt ${attempt + 1}/${maxRetries})`);
            await this._sleep(waitTime);
            continue;
          }
          throw new NetworkError(`Network error: ${error.message}`);
        }

        // Re-throw API errors without retry
        if (error instanceof APIError) {
          throw error;
        }

        // Unknown errors
        throw new NetworkError(`Request failed: ${error.message}`);
      }
    }
  }

  /**
   * Get parliamentary cases (Sag) with optional filtering and expansion
   * 
   * @param {Object} options - Query options
   * @param {number} options.top - Number of records to return (max 100)
   * @param {number} options.skip - Number of records to skip for pagination
   * @param {string} options.filter - OData filter expression
   * @param {string} options.expand - Related entities to include
   * @param {string} options.select - Specific fields to return
   * @param {string} options.orderby - Sort order
   * @returns {Promise<Object>} API response with case data
   * 
   * @example
   * // Get recent climate legislation
   * const cases = await api.getCases({
   *   filter: "substringof('klima', titel)",
   *   expand: "Sagskategori",
   *   top: 50
   * });
   */
  async getCases(options = {}) {
    const { top = 100, skip = 0, filter, expand, select, orderby } = options;
    
    const params = {
      '$top': Math.min(top, 100), // Enforce 100 record limit
      '$skip': skip
    };

    if (filter) params['$filter'] = filter;
    if (expand) params['$expand'] = expand;
    if (select) params['$select'] = select;
    if (orderby) params['$orderby'] = orderby;

    const url = this._buildUrl('Sag', params);
    return await this._makeRequest(url);
  }

  /**
   * Get parliamentary actors (Aktør) - politicians, committees, ministries
   * 
   * @param {Object} options - Query options
   * @returns {Promise<Object>} API response with actor data
   * 
   * @example
   * // Find all politicians with 'Jensen' in name
   * const actors = await api.getActors({
   *   filter: "substringof('Jensen', navn)"
   * });
   */
  async getActors(options = {}) {
    const { top = 100, skip = 0, filter, expand } = options;
    
    const params = {
      '$top': Math.min(top, 100),
      '$skip': skip
    };

    if (filter) params['$filter'] = filter;
    if (expand) params['$expand'] = expand;

    const url = this._buildUrl('Aktør', params);
    return await this._makeRequest(url);
  }

  /**
   * Get voting sessions (Afstemning)
   * 
   * @param {Object} options - Query options
   * @returns {Promise<Object>} API response with voting session data
   */
  async getVotingSessions(options = {}) {
    const { top = 100, skip = 0, filter, expand, select } = options;
    
    const params = {
      '$top': Math.min(top, 100),
      '$skip': skip
    };

    if (filter) params['$filter'] = filter;
    if (expand) params['$expand'] = expand;
    if (select) params['$select'] = select;

    const url = this._buildUrl('Afstemning', params);
    return await this._makeRequest(url);
  }

  /**
   * Get all voting records for a specific politician
   * 
   * @param {string} politicianName - Full name of politician
   * @param {number} limit - Maximum number of votes to return
   * @returns {Promise<Array>} Array of voting records
   * 
   * @example
   * const votes = await api.getVotingRecords("Frank Aaen");
   */
  async getVotingRecords(politicianName, limit = 1000) {
    const allVotes = [];
    let skip = 0;
    const batchSize = 100;

    while (allVotes.length < limit && skip < 10000) { // Safety limit
      const params = {
        '$expand': 'Afstemning,Aktør',
        '$filter': `Aktør/navn eq '${politicianName}'`,
        '$top': batchSize,
        '$skip': skip
      };

      const url = this._buildUrl('Stemme', params);
      const response = await this._makeRequest(url);
      const votes = response.value || [];

      if (votes.length === 0) {
        break;
      }

      allVotes.push(...votes);
      skip += batchSize;
    }

    return allVotes.slice(0, limit);
  }

  /**
   * Get recent changes to parliamentary data
   * 
   * @param {string} entity - Entity to check ('Sag', 'Aktør', 'Afstemning', etc.)
   * @param {number} hoursBack - How many hours back to check
   * @returns {Promise<Object>} Recent changes in the specified entity
   * 
   * @example
   * // Check for cases updated in last 4 hours
   * const recent = await api.getRecentChanges('Sag', 4);
   */
  async getRecentChanges(entity = 'Sag', hoursBack = 24) {
    const cutoffTime = new Date();
    cutoffTime.setHours(cutoffTime.getHours() - hoursBack);
    const isoTime = cutoffTime.toISOString().slice(0, 19); // Remove milliseconds

    const params = {
      '$filter': `opdateringsdato gt datetime'${isoTime}'`,
      '$orderby': 'opdateringsdato desc',
      '$top': 100
    };

    const url = this._buildUrl(entity, params);
    return await this._makeRequest(url);
  }

  /**
   * Get detailed information about a voting session
   * 
   * @param {number} votingId - ID of the voting session (Afstemning)
   * @param {boolean} expandVotes - Whether to include individual vote details
   * @returns {Promise<Object>} Voting session with optional vote details
   */
  async getVotingSessionDetails(votingId, expandVotes = true) {
    const expandParts = ['Møde'];
    if (expandVotes) {
      expandParts.push('Stemme/Aktør');
    }

    const params = {
      '$filter': `id eq ${votingId}`,
      '$expand': expandParts.join(',')
    };

    const url = this._buildUrl('Afstemning', params);
    const response = await this._makeRequest(url);

    if (response.value && response.value.length > 0) {
      return response.value[0];
    } else {
      throw new RecordNotFoundError(`Voting session ${votingId} not found`);
    }
  }

  /**
   * Search parliamentary documents by title
   * 
   * @param {string} searchTerm - Term to search for in document titles
   * @param {boolean} includeFiles - Whether to include file download URLs
   * @returns {Promise<Object>} Matching documents
   */
  async searchDocuments(searchTerm, includeFiles = false) {
    const params = {
      '$filter': `substringof('${searchTerm}', titel)`,
      '$top': 100
    };

    if (includeFiles) {
      params['$expand'] = 'Fil';
    }

    const url = this._buildUrl('Dokument', params);
    return await this._makeRequest(url);
  }

  /**
   * Get total count of records in an entity
   * 
   * @param {string} entity - Entity name
   * @returns {Promise<number>} Total number of records
   */
  async getEntityCount(entity) {
    const params = {
      '$inlinecount': 'allpages',
      '$top': 1
    };

    const url = this._buildUrl(entity, params);
    const response = await this._makeRequest(url);
    
    const countStr = response['odata.count'] || '0';
    return parseInt(countStr, 10);
  }

  /**
   * Generic request method for custom queries
   * 
   * @param {string} entity - Entity name
   * @param {Object} params - OData parameters
   * @returns {Promise<Object>} API response
   */
  async request(entity, params = {}) {
    const url = this._buildUrl(entity, params);
    return await this._makeRequest(url);
  }

  /**
   * Async generator for paginating through all records
   * 
   * @param {string} entity - Entity name
   * @param {Object} options - Pagination options
   * @param {number} options.batchSize - Records per batch (max 100)
   * @param {number} options.maxRecords - Maximum total records to fetch
   * @param {Object} options.params - Additional OData parameters
   * 
   * @example
   * // Process all climate cases
   * for await (const case of api.paginateAll('Sag', {
   *   params: { '$filter': "substringof('klima', titel)" },
   *   maxRecords: 500
   * })) {
   *   console.log(case.titel);
   * }
   */
  async* paginateAll(entity, options = {}) {
    const { batchSize = 100, maxRecords = Infinity, params = {} } = options;
    
    let skip = 0;
    let totalYielded = 0;
    const safeBatchSize = Math.min(batchSize, 100);

    while (totalYielded < maxRecords && skip < 100000) { // Safety limit
      const requestParams = {
        ...params,
        '$top': safeBatchSize,
        '$skip': skip
      };

      try {
        const url = this._buildUrl(entity, requestParams);
        const response = await this._makeRequest(url);
        const records = response.value || [];

        if (records.length === 0) {
          break; // No more records
        }

        // Yield each record individually
        for (const record of records) {
          if (totalYielded >= maxRecords) {
            return;
          }
          yield record;
          totalYielded++;
        }

        skip += safeBatchSize;

      } catch (error) {
        console.error(`Error paginating ${entity} at skip=${skip}:`, error);
        break;
      }
    }
  }

  /**
   * Batch multiple requests concurrently
   * 
   * @param {Array} requests - Array of request configurations
   * @param {number} maxConcurrent - Maximum concurrent requests
   * @returns {Promise<Array>} Array of responses
   * 
   * @example
   * const results = await api.batchRequests([
   *   { entity: 'Sag', params: { '$top': 10 } },
   *   { entity: 'Aktør', params: { '$top': 5 } },
   *   { entity: 'Afstemning', params: { '$top': 3 } }
   * ]);
   */
  async batchRequests(requests, maxConcurrent = 5) {
    // Limit concurrent requests to be respectful to the API
    const semaphore = new Semaphore(maxConcurrent);
    
    const executeRequest = async (request) => {
      await semaphore.acquire();
      try {
        const url = this._buildUrl(request.entity, request.params || {});
        return await this._makeRequest(url);
      } finally {
        semaphore.release();
      }
    };

    return await Promise.all(requests.map(executeRequest));
  }

  /**
   * Analyze voting patterns for a set of votes
   * 
   * @param {Array} votes - Array of voting records
   * @returns {Object} Voting analysis
   */
  analyzeVotingPatterns(votes) {
    const analysis = {
      totalVotes: votes.length,
      voteTypes: {},
      partiesVotedWith: {},
      timeSpan: { earliest: null, latest: null }
    };

    for (const vote of votes) {
      // Count vote types
      const voteType = vote.typeid;
      analysis.voteTypes[voteType] = (analysis.voteTypes[voteType] || 0) + 1;

      // Track time span
      const voteDate = new Date(vote.Afstemning?.dato || '1900-01-01');
      if (!analysis.timeSpan.earliest || voteDate < analysis.timeSpan.earliest) {
        analysis.timeSpan.earliest = voteDate;
      }
      if (!analysis.timeSpan.latest || voteDate > analysis.timeSpan.latest) {
        analysis.timeSpan.latest = voteDate;
      }
    }

    return analysis;
  }
}

// Helper class for limiting concurrent requests
class Semaphore {
  constructor(max) {
    this.max = max;
    this.current = 0;
    this.queue = [];
  }

  async acquire() {
    return new Promise((resolve) => {
      if (this.current < this.max) {
        this.current++;
        resolve();
      } else {
        this.queue.push(resolve);
      }
    });
  }

  release() {
    this.current--;
    if (this.queue.length > 0) {
      this.current++;
      const resolve = this.queue.shift();
      resolve();
    }
  }
}

// Custom Error Classes
class APIError extends Error {
  constructor(message, code = 'API_ERROR') {
    super(message);
    this.name = 'APIError';
    this.code = code;
  }
}

class NetworkError extends Error {
  constructor(message) {
    super(message);
    this.name = 'NetworkError';
  }
}

class EntityNotFoundError extends APIError {
  constructor(message) {
    super(message, 'ENTITY_NOT_FOUND');
    this.name = 'EntityNotFoundError';
  }
}

class RecordNotFoundError extends APIError {
  constructor(message) {
    super(message, 'RECORD_NOT_FOUND');
    this.name = 'RecordNotFoundError';
  }
}

class UnsupportedOperationError extends APIError {
  constructor(message) {
    super(message, 'UNSUPPORTED_OPERATION');
    this.name = 'UnsupportedOperationError';
  }
}

// Export for ES6 modules
export {
  DanishParliamentAPI,
  APIError,
  NetworkError,
  EntityNotFoundError,
  RecordNotFoundError,
  UnsupportedOperationError
};

// Export for CommonJS (Node.js)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    DanishParliamentAPI,
    APIError,
    NetworkError,
    EntityNotFoundError,
    RecordNotFoundError,
    UnsupportedOperationError
  };
}

// Usage Examples
if (typeof window === 'undefined') { // Node.js environment
  // Example usage
  (async () => {
    try {
      const api = new DanishParliamentAPI();
      
      // Get recent cases
      console.log('Getting recent cases...');
      const cases = await api.getCases({ top: 5 });
      console.log(`Found ${cases.value.length} cases`);
      
      // Search for climate legislation
      console.log('\nSearching for climate legislation...');
      const climateCases = await api.getCases({
        filter: "substringof('klima', titel)",
        top: 10
      });
      console.log(`Found ${climateCases.value.length} climate-related cases`);
      
      // Get total case count
      console.log('\nGetting total case count...');
      const totalCases = await api.getEntityCount('Sag');
      console.log(`Total cases in database: ${totalCases.toLocaleString()}`);
      
      // Get recent changes
      console.log('\nChecking recent changes...');
      const recent = await api.getRecentChanges('Sag', 24);
      console.log(`Cases updated in last 24 hours: ${recent.value.length}`);
      
    } catch (error) {
      if (error instanceof APIError) {
        console.error('API Error:', error.message);
      } else if (error instanceof NetworkError) {
        console.error('Network Error:', error.message);
      } else {
        console.error('Unexpected error:', error);
      }
    }
  })();
}
```

## Key Features

### 1. Modern JavaScript
- Uses native `fetch()` API (no dependencies)
- Async/await throughout for clean code
- ES6 classes with proper encapsulation
- Comprehensive JSDoc documentation

### 2. Error Handling
- Custom error classes for different failure types
- Automatic retry with exponential backoff
- Timeout handling with AbortController
- Graceful degradation for network issues

### 3. Performance Optimizations
- Built-in rate limiting to respect API
- Connection reuse through fetch API
- Efficient pagination with generators
- Concurrent request batching with limits

### 4. Production Ready
- TypeScript-compatible (JSDoc types)
- Works in both browser and Node.js
- Comprehensive test coverage potential
- Configurable timeout and retry settings

## Installation & Setup

### Browser Usage
```html
<!DOCTYPE html>
<html>
<head>
  <title>Danish Parliament API Example</title>
</head>
<body>
  <script type="module">
    import { DanishParliamentAPI } from './danish-parliament-api.js';
    
    const api = new DanishParliamentAPI();
    
    // Your code here
    api.getCases({ top: 10 }).then(cases => {
      console.log('Cases:', cases.value);
    });
  </script>
</body>
</html>
```

### Node.js Usage
```javascript
// For Node.js 18+
const { DanishParliamentAPI } = require('./danish-parliament-api.js');

// For older Node.js versions, install node-fetch first:
// npm install node-fetch
// Then uncomment the import at the top of the file

const api = new DanishParliamentAPI({
  timeout: 60000,        // 60 seconds
  retryAttempts: 5,      // 5 retry attempts
  requestDelay: 200      // 200ms between requests
});

async function main() {
  try {
    const cases = await api.getCases({ top: 100 });
    console.log(`Found ${cases.value.length} cases`);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();
```

This implementation provides a robust, production-ready JavaScript client that handles all the complexities of the Danish Parliament API while providing a clean, modern interface.