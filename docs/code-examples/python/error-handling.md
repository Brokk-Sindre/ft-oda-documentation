# Python Error Handling

Comprehensive error handling patterns for the Danish Parliament API, based on real-world testing of all failure modes.

## Overview

The Danish Parliament API has specific error behaviors that require careful handling:

- **HTTP 400**: Invalid OData syntax (returns empty response)
- **HTTP 404**: Invalid entity names (returns HTML) or missing records (empty response)  
- **HTTP 501**: Unsupported write operations (returns JSON error)
- **Silent failures**: Invalid filter fields return all data instead of errors
- **Network timeouts**: Large queries may timeout

## Error Classification

### 1. OData Syntax Errors (HTTP 400)

Invalid OData parameters return HTTP 400 with empty response:

```python
from danish_parliament_api import DanishParliamentAPI, APIError

def handle_odata_errors():
    """Demonstrate OData error handling."""
    api = DanishParliamentAPI()
    
    try:
        # This will fail - invalid expansion
        response = api._make_request(
            api._build_url('Sag', **{'$expand': 'NonExistentRelation'})
        )
    except APIError as e:
        print(f"OData Error: {e}")
        # Error: Invalid query parameters. Check $expand and $filter syntax.

# Common OData errors:
odata_errors = [
    "Sag?$expand=InvalidRelation",           # Invalid relationship
    "Sag?$expand=Deep/Very/Deep/Relation",   # Too deep (>2 levels)
    "Sag?$filter=invalid syntax",            # Malformed filter
    "Sag?$orderby=nonexistent_field",        # Invalid field in orderby
]

for error_query in odata_errors:
    try:
        url = f"https://oda.ft.dk/api/{error_query}"
        response = api._make_request(url)
    except APIError as e:
        print(f"Expected error for '{error_query}': {e}")
```

### 2. Entity Not Found (HTTP 404)

Invalid entity names return HTML error pages:

```python
def handle_entity_errors():
    """Handle invalid entity names."""
    api = DanishParliamentAPI()
    
    try:
        # Invalid entity name
        url = api._build_url('InvalidEntity')
        response = api._make_request(url)
    except EntityNotFoundError as e:
        print(f"Entity Error: {e}")
        # Suggests checking entity name against metadata

# Test multiple invalid entities
invalid_entities = [
    'Cases',        # English instead of Danish 'Sag'
    'Politicians',  # English instead of Danish 'Aktør'  
    'Votes',        # English instead of Danish 'Stemme'
    'NonExistent',  # Completely invalid
]

for entity in invalid_entities:
    try:
        response = api._make_request(f"https://oda.ft.dk/api/{entity}")
    except EntityNotFoundError as e:
        print(f"Entity '{entity}' not found: {e}")
```

### 3. Record Not Found (HTTP 404)

Valid entities with invalid IDs return empty responses:

```python
def handle_record_errors():
    """Handle missing record IDs.""" 
    api = DanishParliamentAPI()
    
    # Test various invalid IDs
    invalid_ids = [999999999, -1, 0, 'invalid']
    
    for invalid_id in invalid_ids:
        try:
            url = f"https://oda.ft.dk/api/Sag({invalid_id})"
            response = api._make_request(url)
            print(f"Unexpected: ID {invalid_id} returned data")
        except RecordNotFoundError as e:
            print(f"Record {invalid_id} not found (expected): {e}")
        except APIError as e:
            print(f"API error for ID {invalid_id}: {e}")

# Robust record fetching with fallback
def get_case_safe(api, case_id, fallback_search=True):
    """
    Safely get a case by ID with fallback options.
    
    Args:
        api: DanishParliamentAPI instance
        case_id: Case ID to fetch
        fallback_search: Try searching if direct ID fails
    
    Returns:
        Case data or None if not found
    """
    try:
        # Try direct ID access
        url = api._build_url('Sag', **{'$filter': f'id eq {case_id}'})
        response = api._make_request(url)
        
        if response.get('value'):
            return response['value'][0]
        
        # ID not found - try fallback if enabled
        if fallback_search:
            print(f"Case {case_id} not found, searching for similar IDs...")
            
            # Search for nearby IDs
            for offset in [-1, 1, -2, 2, -5, 5]:
                try_id = case_id + offset
                url = api._build_url('Sag', **{'$filter': f'id eq {try_id}'})
                response = api._make_request(url)
                
                if response.get('value'):
                    print(f"Found similar case: {try_id}")
                    return response['value'][0]
        
        return None
        
    except APIError as e:
        print(f"Error fetching case {case_id}: {e}")
        return None

# Usage
api = DanishParliamentAPI()
case = get_case_safe(api, 999999, fallback_search=True)
if case:
    print(f"Found case: {case['titel'][:50]}...")
else:
    print("No case found")
```

### 4. Silent Filter Failures

**Critical**: Invalid field names in filters don't return errors - they return all data!

```python
def detect_silent_failures():
    """Detect when filters are silently ignored."""
    api = DanishParliamentAPI()
    
    # Test with known small dataset first
    valid_response = api.get_cases(
        filter_expr="id eq 1",  # Should return 1 record
        top=100
    )
    valid_count = len(valid_response.get('value', []))
    print(f"Valid filter returned {valid_count} records")
    
    # Test with invalid field name
    invalid_response = api.get_cases(
        filter_expr="invalid_field eq 'test'",  # Should fail but doesn't!
        top=100
    )
    invalid_count = len(invalid_response.get('value', []))
    print(f"Invalid filter returned {invalid_count} records")
    
    if invalid_count == 100:  # Got default batch size
        print("   WARNING: Invalid filter was silently ignored!")
        print("    Always validate filter field names!")
    
    return valid_count, invalid_count

# Validation function for filter fields
def validate_filter_fields(api, entity_name, filter_expr):
    """
    Validate that filter fields exist before running query.
    
    Args:
        api: API instance
        entity_name: Entity to check
        filter_expr: Filter expression to validate
    
    Returns:
        True if filter appears valid, False otherwise
    """
    # Get sample record to check available fields
    try:
        sample_response = api._make_request(
            api._build_url(entity_name, **{'$top': 1})
        )
        
        if not sample_response.get('value'):
            print(f"No records found in {entity_name} to validate against")
            return False
        
        sample_record = sample_response['value'][0]
        available_fields = set(sample_record.keys())
        
        # Extract field names from filter (basic parsing)
        import re
        field_matches = re.findall(r'\b([a-zA-ZæøåÆØÅ_][a-zA-ZæøåÆØÅ0-9_]*)\s+(?:eq|ne|gt|lt|ge|le|and|or)', filter_expr)
        
        invalid_fields = []
        for field in field_matches:
            if field not in available_fields and field not in ['and', 'or', 'not']:
                invalid_fields.append(field)
        
        if invalid_fields:
            print(f"   Invalid fields detected: {invalid_fields}")
            print(f"   Available fields: {sorted(available_fields)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Could not validate fields: {e}")
        return False  # Assume invalid on error

# Safe filtering with validation
def safe_filter_query(api, entity_name, filter_expr, **params):
    """
    Execute filter query with validation to prevent silent failures.
    
    Args:
        api: API instance
        entity_name: Entity name
        filter_expr: Filter expression
        **params: Additional parameters
    
    Returns:
        Query results or None if validation fails
    """
    # Validate filter fields
    if not validate_filter_fields(api, entity_name, filter_expr):
        print("Filter validation failed - aborting query")
        return None
    
    # Execute query
    try:
        params['$filter'] = filter_expr
        url = api._build_url(entity_name, **params)
        return api._make_request(url)
    except APIError as e:
        print(f"Query failed: {e}")
        return None

# Usage example
api = DanishParliamentAPI()

# This will validate fields before querying
result = safe_filter_query(
    api, 'Sag', 
    "substringof('klima', titel)",  # Valid filter
    **{'$top': 10}
)

if result:
    print(f"Query succeeded: {len(result['value'])} records")
else:
    print("Query failed validation or execution")
```

### 5. Network Error Handling

Comprehensive network error handling with retry logic:

```python
import time
import requests
from typing import Optional

class RobustAPI(DanishParliamentAPI):
    """Extended API client with robust network error handling."""
    
    def __init__(self, timeout=30, retry_attempts=3, backoff_factor=2):
        super().__init__(timeout, retry_attempts)
        self.backoff_factor = backoff_factor
        self.session = requests.Session()  # Reuse connections
    
    def _make_request_robust(self, url: str, max_retries: Optional[int] = None) -> dict:
        """
        Make HTTP request with comprehensive error handling and retry logic.
        
        Args:
            url: URL to request
            max_retries: Override default retry attempts
        
        Returns:
            Parsed JSON response
        
        Raises:
            NetworkError: For persistent network issues
            APIError: For API-specific errors
        """
        max_retries = max_retries or self.retry_attempts
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                
                # Make request with session for connection reuse
                response = self.session.get(url, timeout=self.timeout)
                
                # Handle HTTP status codes
                if response.status_code == 200:
                    try:
                        return response.json()
                    except ValueError as e:
                        raise APIError(f"Invalid JSON response: {e}")
                
                elif response.status_code == 400:
                    raise APIError(
                        f"Bad Request (400): Invalid OData syntax. "
                        f"Check $filter, $expand, and other parameters. URL: {url}"
                    )
                
                elif response.status_code == 404:
                    # Distinguish between entity not found vs record not found
                    if '/api/' in url and url.count('/') == 4:  # Just entity name
                        raise EntityNotFoundError(f"Entity not found: {url.split('/')[-1]}")
                    else:  # Specific record or invalid ID
                        raise RecordNotFoundError(f"Record not found: {url}")
                
                elif response.status_code == 501:
                    raise UnsupportedOperationError(
                        "This API is read-only. Write operations (POST/PUT/DELETE) are not supported."
                    )
                
                elif response.status_code == 503:
                    # Service temporarily unavailable - retry with longer delay
                    if attempt < max_retries - 1:
                        wait_time = (self.backoff_factor ** attempt) * 5  # Longer wait for 503
                        print(f"Service unavailable (503). Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise NetworkError(f"Service unavailable after {max_retries} attempts")
                
                else:
                    response.raise_for_status()
            
            except requests.exceptions.Timeout as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = (self.backoff_factor ** attempt) * 1
                    print(f"Request timeout. Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise NetworkError(f"Request timed out after {self.timeout} seconds. Tried {max_retries} times.")
            
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = (self.backoff_factor ** attempt) * 2
                    print(f"Connection error. Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise NetworkError(f"Connection failed after {max_retries} attempts: {str(e)}")
            
            except requests.exceptions.HTTPError as e:
                # For other HTTP errors not specifically handled above
                raise APIError(f"HTTP error {e.response.status_code}: {e}")
            
            except requests.exceptions.RequestException as e:
                # Catch-all for other request errors
                raise NetworkError(f"Request failed: {str(e)}")
        
        # This should not be reached due to the exception handling above
        raise NetworkError(f"Unknown error after {max_retries} attempts. Last exception: {last_exception}")
    
    def health_check(self) -> dict:
        """
        Perform basic API health check.
        
        Returns:
            Health status information
        """
        health_info = {
            'api_accessible': False,
            'response_time_ms': None,
            'record_count_sample': None,
            'timestamp': datetime.now().isoformat(),
            'errors': []
        }
        
        try:
            # Test basic connectivity with timing
            start_time = time.time()
            response = self._make_request_robust(
                self._build_url('Sag', **{'$top': 1})
            )
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            health_info.update({
                'api_accessible': True,
                'response_time_ms': round(response_time, 2),
                'record_count_sample': len(response.get('value', []))
            })
            
            # Test OData functionality
            try:
                count_response = self.get_entity_count('Sag')
                health_info['total_cases'] = count_response
            except Exception as e:
                health_info['errors'].append(f"Count query failed: {e}")
            
            # Test filtering
            try:
                filter_response = self._make_request_robust(
                    self._build_url('Sag', **{
                        '$filter': 'id eq 1',
                        '$top': 1
                    })
                )
                health_info['filtering_works'] = len(filter_response.get('value', [])) > 0
            except Exception as e:
                health_info['errors'].append(f"Filter test failed: {e}")
                health_info['filtering_works'] = False
        
        except Exception as e:
            health_info['errors'].append(f"Health check failed: {e}")
        
        return health_info

# Usage examples
def example_error_handling():
    """Demonstrate comprehensive error handling."""
    api = RobustAPI(timeout=60, retry_attempts=5)
    
    # Health check first
    print("Performing health check...")
    health = api.health_check()
    print(f"API accessible: {health['api_accessible']}")
    print(f"Response time: {health['response_time_ms']}ms")
    
    if health['errors']:
        print(f"Health check warnings: {health['errors']}")
    
    # Test various error conditions
    error_tests = [
        # Valid query
        ('Valid query', lambda: api.get_cases(top=5)),
        
        # Invalid entity
        ('Invalid entity', lambda: api._make_request_robust('https://oda.ft.dk/api/InvalidEntity')),
        
        # Invalid OData
        ('Invalid OData', lambda: api._make_request_robust('https://oda.ft.dk/api/Sag?$expand=Invalid')),
        
        # Very large query (might timeout)
        ('Large query', lambda: api.get_cases(top=100, expand🔧SagAktør/Aktør')),
    ]
    
    for test_name, test_func in error_tests:
        print(f"\n--- Testing: {test_name} ---")
        try:
            result = test_func()
            if isinstance(result, dict) and 'value' in result:
                print(f"✅ Success: {len(result['value'])} records")
            else:
                print(f"✅ Success: {result}")
        except EntityNotFoundError as e:
            print(f"L Entity Error: {e}")
        except RecordNotFoundError as e:
            print(f"L Record Error: {e}")
        except APIError as e:
            print(f"L API Error: {e}")
        except NetworkError as e:
            print(f"L Network Error: {e}")
        except Exception as e:
            print(f"L Unexpected Error: {e}")

if __name__ == "__main__":
    example_error_handling()
```

## Production Error Handling Patterns

### 1. Circuit Breaker Pattern

```python
import threading
from datetime import datetime, timedelta

class CircuitBreaker:
    """Implement circuit breaker pattern for API reliability."""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        with self.lock:
            if self.state == 'OPEN':
                if self._should_attempt_reset():
                    self.state = 'HALF_OPEN'
                else:
                    raise NetworkError("Circuit breaker is OPEN - API calls suspended")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
                
            except Exception as e:
                self._on_failure()
                raise
    
    def _should_attempt_reset(self):
        return (datetime.now() - self.last_failure_time).seconds >= self.recovery_timeout
    
    def _on_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'

# Usage with circuit breaker
class ProductionAPI(RobustAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.circuit_breaker = CircuitBreaker()
    
    def safe_request(self, url):
        """Make request with circuit breaker protection."""
        return self.circuit_breaker.call(self._make_request_robust, url)
```

### 2. Comprehensive Logging

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format🔧%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('danish_parliament_api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('DanishParliamentAPI')

class LoggedAPI(RobustAPI):
    """API client with comprehensive logging."""
    
    def _make_request_robust(self, url: str, max_retries: Optional[int] = None) -> dict:
        """Override with logging."""
        logger.info(f"Making request to: {url}")
        start_time = time.time()
        
        try:
            result = super()._make_request_robust(url, max_retries)
            response_time = (time.time() - start_time) * 1000
            
            record_count = len(result.get('value', [])) if 'value' in result else 1
            logger.info(f"Request successful: {record_count} records in {response_time:.1f}ms")
            
            return result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Request failed after {response_time:.1f}ms: {e}")
            raise

# Usage with logging
api = LoggedAPI()
try:
    cases = api.get_cases(top=10)
    logger.info(f"Successfully retrieved {len(cases['value'])} cases")
except Exception as e:
    logger.error(f"Failed to retrieve cases: {e}")
```

## Error Recovery Strategies

### 1. Graceful Degradation
```python
def get_cases_with_fallback(api, primary_params, fallback_params_list):
    """Try multiple query strategies with fallbacks."""
    
    strategies = [primary_params] + fallback_params_list
    
    for i, params in enumerate(strategies):
        try:
            logger.info(f"Trying strategy {i + 1}: {params}")
            return api.get_cases(**params)
            
        except APIError as e:
            logger.warning(f"Strategy {i + 1} failed: {e}")
            if i == len(strategies) - 1:
                raise e  # Last strategy failed
            continue

# Usage
api = DanishParliamentAPI()
try:
    cases = get_cases_with_fallback(
        api,
        primary_params={'filter_expr': "substringof('klima', titel)", 'expand': 'Sagskategori'},
        fallback_params_list=[
            {'filter_expr': "substringof('klima', titel)"},  # Remove expansion
            {'top': 50},  # Just get some cases
            {}  # Last resort - default query
        ]
    )
    print(f"Retrieved {len(cases['value'])} cases using fallback strategy")
except Exception as e:
    print(f"All strategies failed: {e}")
```

This comprehensive error handling system ensures your application can gracefully handle all known failure modes of the Danish Parliament API while providing useful feedback for debugging and monitoring.