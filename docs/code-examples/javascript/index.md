# JavaScript Client Library

Modern JavaScript/Node.js client for the Danish Parliament API with fetch-based examples, async patterns, and browser support.

## Features

- **Modern ES6+**: Uses fetch API and async/await
- **Browser & Node.js**: Works in both environments
- **Generator Patterns**: Memory-efficient pagination
- **Error Handling**: Comprehensive error management
- **TypeScript Ready**: Full type support available
- **No Dependencies**: Uses native fetch API

## Quick Start

```javascript
// ES6 Modules
import { DanishParliamentAPI } from './danish-parliament-api.js';

// CommonJS (Node.js)
const { DanishParliamentAPI } = require('./danish-parliament-api.js');

// Initialize client
const api = new DanishParliamentAPI();

// Get recent cases
const cases = await api.getCases({ top: 10 });
console.log(`Found ${cases.value.length} cases`);

// Search for climate legislation
const climateCases = await api.getCases({
  filter: "substringof('klima', titel)",
  top: 50
});
console.log(`Climate cases: ${climateCases.value.length}`);
```

## Installation

### Browser (ES6 Modules)
```html
<script type="module">
import { DanishParliamentAPI } from './js/danish-parliament-api.js';

const api = new DanishParliamentAPI();
// Use the API...
</script>
```

### Node.js
```bash
# No installation needed - uses native fetch (Node.js 18+)
# For older Node.js versions:
npm install node-fetch
```

## Client Libraries

1. **[Fetch Client](fetch-client.md)** - Complete modern client implementation
2. **[Pagination](pagination.md)** - Generator patterns for large datasets  
3. **[Browser Usage](browser-usage.md)** - Client-side usage and CORS handling

## Examples

### Parliamentary Monitoring
```javascript
// Monitor recent activity
const recentChanges = await api.getRecentChanges('Sag', 4); // Last 4 hours
for (const case of recentChanges.value) {
  console.log(`Updated: ${case.titel} at ${case.opdateringsdato}`);
}
```

### Voting Analysis
```javascript
// Get all votes by a politician
const votes = await api.getVotingRecords('Frank Aaen');
console.log(`Found ${votes.length} votes`);

// Analyze voting patterns
const voteAnalysis = api.analyzeVotingPatterns(votes);
console.log(voteAnalysis);
```

### Concurrent Processing
```javascript
// Process multiple search terms concurrently
const searchTerms = ['klima', 'miljø', 'energi'];
const results = await Promise.all(
  searchTerms.map(term => 
    api.getCases({ filter: `substringof('${term}', titel)` })
  )
);

searchTerms.forEach((term, i) => {
  console.log(`${term}: ${results[i].value.length} cases`);
});
```

## Browser Compatibility

- **Modern browsers**: Chrome 42+, Firefox 39+, Safari 10.1+, Edge 14+
- **Node.js**: 18+ (native fetch) or 14+ with node-fetch polyfill
- **CORS**: API supports cross-origin requests from browsers

## Key Features

### 1. Modern JavaScript
- Uses native `fetch()` API
- Async/await throughout
- ES6 classes and modules
- Promise-based error handling

### 2. Efficient Pagination
- Generator functions for memory efficiency
- Automatic batching and rate limiting
- Progress tracking and resumption

### 3. Error Handling
- Comprehensive error classification
- Automatic retry with exponential backoff
- Network error recovery

### 4. Performance Optimized
- Connection reuse
- Request deduplication
- Intelligent caching
- Concurrent request limiting

## Usage Patterns

### Simple Queries
```javascript
// Get basic case information
const cases = await api.getCases({ top: 20 });

// Search with filters
const filtered = await api.getCases({
  filter: "year(opdateringsdato) eq 2025",
  orderby: "opdateringsdato desc"
});
```

### Advanced Queries  
```javascript
// Complex relationships
const casesWithActors = await api.getCases({
  expand: "SagAktør/Aktør",
  filter: "substringof('klima', titel)",
  select: "id,titel,SagAktør/Aktør/navn"
});

// Multiple entity queries
const [cases, actors, votes] = await Promise.all([
  api.getCases({ top: 10 }),
  api.getActors({ top: 10 }), 
  api.getVotingSessions({ top: 5 })
]);
```

### Streaming Data
```javascript
// Process large datasets efficiently
for await (const case of api.paginateAll('Sag', { batchSize: 100 })) {
  // Process each case individually
  console.log(case.titel);
  
  // Memory stays constant even for 100k+ records
}
```

## Error Handling

```javascript
try {
  const cases = await api.getCases({ top: 10 });
  console.log(`Success: ${cases.value.length} cases`);
} catch (error) {
  if (error.name === 'ValidationError') {
    console.error('Invalid parameters:', error.message);
  } else if (error.name === 'NetworkError') {
    console.error('Network issue:', error.message);
  } else if (error.name === 'APIError') {
    console.error('API error:', error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## Next Steps

1. **[Fetch Client](fetch-client.md)** - Complete implementation
2. **[Pagination](pagination.md)** - Handle large datasets
3. **[Browser Usage](browser-usage.md)** - Client-side patterns