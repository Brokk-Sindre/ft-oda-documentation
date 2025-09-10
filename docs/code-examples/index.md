---
title: Code Examples - Danish Parliament API Implementation Guide
description: Complete code examples for the Danish Parliament API (oda.ft.dk) in Python, JavaScript, TypeScript, and cURL. Production-ready implementations with error handling, pagination, and real-time features.
keywords: danish parliament api code examples, oda.ft.dk implementation, parliamentary data code, python javascript typescript curl examples, api integration guide
---

# Code Examples

Comprehensive code examples and implementations for the Danish Parliament API (oda.ft.dk) across multiple programming languages and environments.

## = Quick Start by Language

Choose your preferred programming language to get started immediately:

<div class="language-grid">
  <div class="language-card">
    <h3>= Python</h3>
    <p>Production-ready client with async support, pagination, and comprehensive error handling</p>
    <a href="python/">Get Started </a>
  </div>
  
  <div class="language-card">
    <h3>=è JavaScript</h3>
    <p>Modern ES6+ client using fetch API, works in browser and Node.js environments</p>
    <a href="javascript/">Get Started </a>
  </div>
  
  <div class="language-card">
    <h3>=Ø TypeScript</h3>
    <p>Fully typed client with complete type definitions for all 50+ API entities</p>
    <a href="typescript/">Get Started </a>
  </div>
  
  <div class="language-card">
    <h3>< cURL</h3>
    <p>Command-line examples perfect for testing, scripting, and API exploration</p>
    <a href="curl/">Get Started </a>
  </div>
</div>

## =Ê Interactive Examples

Try the API live with these interactive tools:

- **[Query Builder](live-examples/query-builder.md)** - Visual OData query construction
- **[Response Viewer](live-examples/response-viewer.md)** - Real-time API response explorer
- **[Live Testing](live-examples/)** - Interactive API playground

## <¯ Example Categories

### Basic Integration
Perfect for getting started with the API:

- **First API Calls** - Simple queries to test connectivity
- **Basic Entity Retrieval** - Getting cases, actors, votes, documents
- **Simple Filtering** - Text search and basic conditions
- **Result Handling** - Processing API responses

### Production Features
Essential for real-world applications:

- **Error Handling** - Comprehensive error management patterns
- **Pagination** - Efficient handling of large datasets
- **Rate Limiting** - Respectful API usage patterns
- **Retry Logic** - Robust network error recovery
- **Caching** - Response caching strategies

### Advanced Use Cases
Complex parliamentary data analysis:

- **Voting Analysis** - Political alignment and voting patterns
- **Legislative Tracking** - Following bills through the process
- **Real-time Monitoring** - Detecting parliamentary activity changes
- **Relationship Navigation** - Complex entity relationships
- **Data Mining** - Large-scale data analysis patterns

## =' Prerequisites

### General Requirements
- **Internet Connection** - API requires HTTPS access to oda.ft.dk
- **No Authentication** - API is completely open and free
- **JSON Processing** - All responses are in JSON format
- **URL Encoding** - Critical: Always use `%24` instead of `$` in URLs

### Language-Specific Setup

=== "Python"
    ```bash
    # Basic requirements
    pip install requests
    
    # For async support
    pip install aiohttp
    
    # For data analysis
    pip install pandas numpy
    ```

=== "JavaScript/Node.js"
    ```bash
    # Node.js 18+ (native fetch support)
    node --version  # Should be 18.0.0+
    
    # For older Node.js
    npm install node-fetch
    ```

=== "TypeScript"
    ```bash
    # TypeScript development
    npm install -D typescript @types/node
    
    # Optional: ts-node for development
    npm install -D ts-node
    ```

=== "cURL"
    ```bash
    # cURL (usually pre-installed)
    curl --version
    
    # Optional: jq for JSON processing
    # Ubuntu/Debian:
    sudo apt-get install jq
    
    # macOS:
    brew install jq
    ```

## =È API Overview

Understanding what you're working with:

### Dataset Scale
- **96,538+** Parliamentary cases
- **18,139+** Political actors  
- **74+ years** of historical data
- **50 entity types** with complex relationships
- **Real-time updates** within hours of parliamentary activity

### Performance Characteristics
- **Response Times**: 85ms - 2 seconds
- **Throughput**: Excellent for concurrent requests
- **Reliability**: High uptime and stability
- **Rate Limits**: Generous, respect the service

### Key Entity Types
| Entity | Description | Example Use |
|--------|-------------|-------------|
| `Sag` | Cases/Bills | Track legislation progress |
| `Aktør` | Politicians/Parties | Analyze political actors |
| `Afstemning` | Voting Sessions | Study voting patterns |
| `Stemme` | Individual Votes | Detailed vote analysis |
| `Dokument` | Parliamentary Documents | Document research |
| `Møde` | Committee Meetings | Meeting attendance |

## <¨ Code Style Guidelines

### Universal Patterns
All examples follow these principles:

1. **Error-First Design** - Always handle errors gracefully
2. **Readable Code** - Clear variable names and comments
3. **Production Ready** - Include proper error handling and logging
4. **Performance Conscious** - Use pagination and field selection
5. **Respectful Usage** - Rate limiting and connection reuse

### Common Patterns

#### URL Encoding (Critical)
```python
# L WRONG - This will fail
url = "https://oda.ft.dk/api/Sag?$top=5"

#  CORRECT - Always encode $ as %24
url = "https://oda.ft.dk/api/Sag?%24top=5"
```

#### Error Handling
```python
try:
    response = api_client.get_cases(top=10)
    print(f"Success: {len(response['value'])} cases")
except APIError as e:
    logger.error(f"API error: {e.message}")
except NetworkError as e:
    logger.error(f"Network error: {e.message}")
```

#### Pagination
```python
# Handle large datasets efficiently
for page in api_client.paginate('Sag', batch_size=100):
    for case in page['value']:
        process_case(case)
```

## < Featured Examples

### 1. Parliamentary Activity Monitor
Real-time monitoring of parliamentary changes:

=== "Python"
    ```python
    # Monitor recent activity
    from datetime import datetime, timedelta
    
    def monitor_recent_activity(hours_back=4):
        cutoff = datetime.now() - timedelta(hours=hours_back)
        cutoff_str = cutoff.strftime('%Y-%m-%dT%H:%M:%S')
        
        recent = api.get_cases(
            filter=f"opdateringsdato gt datetime'{cutoff_str}'",
            orderby="opdateringsdato desc",
            top=20
        )
        
        print(f"Found {len(recent['value'])} recent updates:")
        for case in recent['value']:
            print(f"  {case['titel'][:60]}... (ID: {case['id']})")
    ```

=== "JavaScript"
    ```javascript
    // Monitor recent activity
    async function monitorRecentActivity(hoursBack = 4) {
        const cutoff = new Date(Date.now() - hoursBack * 60 * 60 * 1000);
        const cutoffStr = cutoff.toISOString().slice(0, 19);
        
        const recent = await api.getCases({
            filter: `opdateringsdato gt datetime'${cutoffStr}'`,
            orderby: "opdateringsdato desc",
            top: 20
        });
        
        console.log(`Found ${recent.value.length} recent updates:`);
        recent.value.forEach(case => {
            console.log(`  ${case.titel.slice(0, 60)}... (ID: ${case.id})`);
        });
    }
    ```

### 2. Voting Pattern Analysis
Analyze how politicians vote:

=== "Python"
    ```python
    def analyze_voting_patterns(politician_name):
        votes = api.get_voting_records(politician_name)
        
        pattern = {
            'for': 0, 'against': 0, 'abstain': 0, 'absent': 0
        }
        
        for vote in votes:
            if vote['typeid'] == 1: pattern['for'] += 1
            elif vote['typeid'] == 2: pattern['against'] += 1
            elif vote['typeid'] == 3: pattern['abstain'] += 1
            else: pattern['absent'] += 1
                
        return {
            'politician': politician_name,
            'total_votes': len(votes),
            'breakdown': pattern
        }
    ```

### 3. Legislative Progress Tracker
Track bills through the parliamentary process:

=== "Python"
    ```python
    def track_legislation_progress(search_term):
        cases = api.get_cases(
            filter=f"substringof('{search_term}', titel)",
            expand="Sagstrin,Sagskategori",
            top=50
        )
        
        progress_report = []
        for case in cases['value']:
            stages = len(case.get('Sagstrin', []))
            category = case.get('Sagskategori', {}).get('kategori', 'Unknown')
            
            progress_report.append({
                'title': case['titel'],
                'status': case['statusid'],
                'category': category,
                'stages_completed': stages,
                'last_update': case['opdateringsdato']
            })
        
        return progress_report
    ```

## =Ú Learning Path

### Beginner (First Hour)
1. **[Getting Started](../getting-started/)** - Basic concepts and first API call
2. **[Your Language's Quick Start](#quick-start-by-language)** - Language-specific setup
3. **[Basic Queries](curl/basic-queries.md)** - Essential query patterns
4. **Common Mistakes** - URL encoding and error handling

### Intermediate (Week 1)
1. **[Pagination Patterns](python/pagination.md)** - Handle large datasets
2. **[Error Handling](python/error-handling.md)** - Production error patterns
3. **[Entity Relationships](../data-model/entity-relationships.md)** - Understanding data connections
4. **Performance Best Practices** - Efficient queries and caching

### Advanced (Month 1)
1. **[Voting Analysis](javascript/pagination.md)** - Complex political analysis
2. **[Real-time Monitoring](../guides/real-time-monitoring/)** - Change detection
3. **[Data Mining Patterns](../guides/advanced-analysis/)** - Large-scale analysis
4. **Production Deployment** - Scaling and monitoring

## =à Development Tools

### API Testing Tools
- **[Query Builder](live-examples/query-builder.md)** - Visual query construction
- **[Response Viewer](live-examples/response-viewer.md)** - Interactive API explorer
- **[Postman Collection](#)** - Pre-built API requests
- **[Insomnia Workspace](#)** - Alternative REST client setup

### Development Environment
- **Local Testing Server** - Test your integration locally
- **Mock Data Generator** - Generate test data matching API structure
- **Schema Validator** - Validate API responses
- **Performance Profiler** - Monitor request performance

## = Related Resources

### Documentation Sections
- **[API Reference](../api-reference/)** - Complete entity documentation
- **[Use Case Guides](../guides/)** - Practical implementation guides
- **[Data Model](../data-model/)** - Understanding parliamentary structures
- **[Performance Guide](../api-reference/performance/)** - Optimization strategies

### External Tools
- **[Danish Parliament Website](https://www.ft.dk)** - Context for the data
- **[OData Documentation](http://www.odata.org/documentation/)** - Query language reference
- **[JSON Tools](https://jsonformatter.org/)** - JSON formatting and validation

## > Contributing Examples

Have a great example to share? We welcome contributions!

### Contribution Guidelines
1. **Follow existing patterns** - Match the style and structure
2. **Include error handling** - Production-ready code only
3. **Add comments** - Explain complex logic
4. **Test thoroughly** - Verify examples work with real API
5. **Update documentation** - Keep docs in sync

### Example Template
```python
"""
Brief description of what this example demonstrates.

Requirements:
- List any special requirements

Usage:
- How to run the example
- Expected output

Author: Your Name
Date: YYYY-MM-DD
"""

# Your example code here
```

Ready to start coding? Choose your language and dive in!