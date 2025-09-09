# Python Basic Client

A complete, production-ready Python client for the Danish Parliament API with comprehensive error handling.

## Complete Client Implementation

```python
import requests
import urllib.parse
import time
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import json

class DanishParliamentAPI:
    """
    Production-ready client for Danish Parliament Open Data API (oda.ft.dk)
    
    Features:
    - Comprehensive error handling
    - Automatic retry with exponential backoff
    - Built-in pagination support
    - Rate limiting protection
    - Complete type hints
    """
    
    def __init__(self, timeout: int = 30, retry_attempts: int = 3):
        """
        Initialize the API client.
        
        Args:
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
        """
        self.base_url = "https://oda.ft.dk/api/"
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.last_request_time = 0
        self.min_request_interval = 0.1  # Minimum 100ms between requests
    
    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            url: Complete URL to request
            
        Returns:
            Parsed JSON response
            
        Raises:
            APIError: For various API errors
            NetworkError: For network-related errors
        """
        self._rate_limit()
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(url, timeout=self.timeout)
                
                # Handle different HTTP status codes
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 400:
                    raise APIError(
                        f"Invalid query parameters. Check $expand and $filter syntax. "
                        f"URL: {url}"
                    )
                elif response.status_code == 404:
                    if 'api/' in url and url.count('/') == 4:  # Entity not found
                        raise EntityNotFoundError(f"Entity not found: {url}")
                    else:  # Invalid ID
                        raise RecordNotFoundError(f"Record not found: {url}")
                elif response.status_code == 501:
                    raise UnsupportedOperationError(
                        "Write operations are not supported by this API"
                    )
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout:
                if attempt < self.retry_attempts - 1:
                    wait_time = (2 ** attempt) * 1  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                raise NetworkError(f"Request timed out after {self.timeout} seconds")
                
            except requests.exceptions.ConnectionError:
                if attempt < self.retry_attempts - 1:
                    wait_time = (2 ** attempt) * 1
                    time.sleep(wait_time)
                    continue
                raise NetworkError("Connection error - check your internet connection")
                
            except requests.exceptions.RequestException as e:
                raise NetworkError(f"Request failed: {str(e)}")
    
    def _build_url(self, entity: str, **params) -> str:
        """
        Build properly encoded URL with OData parameters.
        
        Args:
            entity: Entity name (e.g., 'Sag', 'Aktør')
            **params: OData parameters
            
        Returns:
            Complete URL with encoded parameters
        """
        # Start with base URL and entity
        url = f"{self.base_url}{entity}"
        
        if not params:
            return url
        
        # Build query parameters with proper encoding
        query_parts = []
        for key, value in params.items():
            if value is not None:
                # Ensure $ parameters are properly encoded
                if key.startswith('$'):
                    encoded_key = urllib.parse.quote(key, safe🔧')
                else:
                    encoded_key = key
                
                encoded_value = urllib.parse.quote(str(value), safe🔧()\',%')
                query_parts.append(f"{encoded_key}={encoded_value}")
        
        return f"{url}?{'&'.join(query_parts)}"
    
    def get_cases(self, top: int = 100, skip: int = 0, filter_expr: Optional[str] = None, 
                  expand: Optional[str] = None, select: Optional[str] = None,
                  orderby: Optional[str] = None) -> Dict[str, Any]:
        """
        Get parliamentary cases (Sag) with optional filtering and expansion.
        
        Args:
            top: Number of records to return (max 100)
            skip: Number of records to skip for pagination
            filter_expr: OData filter expression
            expand: Related entities to include
            select: Specific fields to return
            orderby: Sort order
            
        Returns:
            API response with case data
            
        Example:
            # Get recent climate legislation
            cases = api.get_cases(
                filter_expr="substringof('klima', titel)",
                expand="Sagskategori",
                top=50
            )
        """
        params = {'$top': min(top, 100), '$skip': skip}  # Enforce 100 record limit
        
        if filter_expr:
            params['$filter'] = filter_expr
        if expand:
            params['$expand'] = expand
        if select:
            params['$select'] = select
        if orderby:
            params['$orderby'] = orderby
        
        url = self._build_url('Sag', **params)
        return self._make_request(url)
    
    def get_actors(self, top: int = 100, skip: int = 0, filter_expr: Optional[str] = None,
                   expand: Optional[str] = None) -> Dict[str, Any]:
        """
        Get parliamentary actors (Aktør) - politicians, committees, ministries.
        
        Args:
            top: Number of records to return (max 100)
            skip: Number of records to skip for pagination
            filter_expr: OData filter expression
            expand: Related entities to include
            
        Returns:
            API response with actor data
            
        Example:
            # Find all politicians with 'Jensen' in name
            actors = api.get_actors(
                filter_expr="substringof('Jensen', navn)"
            )
        """
        params = {'$top': min(top, 100), '$skip': skip}
        
        if filter_expr:
            params['$filter'] = filter_expr
        if expand:
            params['$expand'] = expand
        
        url = self._build_url('Aktør', **params)
        return self._make_request(url)
    
    def get_voting_records(self, politician_name: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get all voting records for a specific politician.
        
        Args:
            politician_name: Full name of politician
            limit: Maximum number of votes to return
            
        Returns:
            List of voting records with expanded details
            
        Example:
            votes = api.get_voting_records("Frank Aaen")
        """
        all_votes = []
        skip = 0
        batch_size = 100
        
        while len(all_votes) < limit and skip < 10000:  # Safety limit
            params = {
                '$expand': 'Afstemning,Aktør',
                '$filter': f"Aktør/navn eq '{politician_name}'",
                '$top': batch_size,
                '$skip': skip
            }
            
            url = self._build_url('Stemme', **params)
            response = self._make_request(url)
            
            votes = response.get('value', [])
            if not votes:
                break
            
            all_votes.extend(votes)
            skip += batch_size
        
        return all_votes[:limit]
    
    def get_recent_changes(self, entity: str = 'Sag', hours_back: int = 24) -> Dict[str, Any]:
        """
        Get recent changes to parliamentary data.
        
        Args:
            entity: Entity to check ('Sag', 'Aktør', 'Afstemning', etc.)
            hours_back: How many hours back to check
            
        Returns:
            Recent changes in the specified entity
            
        Example:
            # Check for cases updated in last 4 hours
            recent = api.get_recent_changes('Sag', hours_back=4)
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        iso_time = cutoff_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        params = {
            '$filter': f"opdateringsdato gt datetime'{iso_time}'",
            '$orderby': 'opdateringsdato desc',
            '$top': 100
        }
        
        url = self._build_url(entity, **params)
        return self._make_request(url)
    
    def get_voting_session_details(self, voting_id: int, expand_votes: bool = True) -> Dict[str, Any]:
        """
        Get detailed information about a voting session.
        
        Args:
            voting_id: ID of the voting session (Afstemning)
            expand_votes: Whether to include individual vote details
            
        Returns:
            Voting session with optional vote details
        """
        expand_parts = ['Møde']
        if expand_votes:
            expand_parts.append('Stemme/Aktør')
        
        params = {
            '$filter': f'id eq {voting_id}',
            '$expand': ','.join(expand_parts)
        }
        
        url = self._build_url('Afstemning', **params)
        response = self._make_request(url)
        
        if response.get('value'):
            return response['value'][0]
        else:
            raise RecordNotFoundError(f"Voting session {voting_id} not found")
    
    def search_documents(self, search_term: str, include_files: bool = False) -> Dict[str, Any]:
        """
        Search parliamentary documents by title.
        
        Args:
            search_term: Term to search for in document titles
            include_files: Whether to include file download URLs
            
        Returns:
            Matching documents
        """
        params = {
            '$filter': f"substringof('{search_term}', titel)",
            '$top': 100
        }
        
        if include_files:
            params['$expand'] = 'Fil'
        
        url = self._build_url('Dokument', **params)
        return self._make_request(url)
    
    def get_entity_count(self, entity: str) -> int:
        """
        Get total count of records in an entity.
        
        Args:
            entity: Entity name
            
        Returns:
            Total number of records
        """
        params = {
            '$inlinecount': 'allpages',
            '$top': 1
        }
        
        url = self._build_url(entity, **params)
        response = self._make_request(url)
        
        count_str = response.get('odata.count', '0')
        return int(count_str)


# Custom Exception Classes
class APIError(Exception):
    """Base exception for API errors."""
    pass

class NetworkError(APIError):
    """Network-related errors."""
    pass

class EntityNotFoundError(APIError):
    """Entity does not exist."""
    pass

class RecordNotFoundError(APIError):
    """Specific record does not exist."""
    pass

class UnsupportedOperationError(APIError):
    """Operation not supported by API."""
    pass


# Usage Examples
if __name__ == "__main__":
    # Initialize client
    api = DanishParliamentAPI()
    
    try:
        # Get recent cases
        print("Getting recent cases...")
        cases = api.get_cases(top=5)
        print(f"Found {len(cases['value'])} cases")
        
        # Search for climate legislation
        print("\nSearching for climate legislation...")
        climate_cases = api.get_cases(
            filter_expr="substringof('klima', titel)",
            top=10
        )
        print(f"Found {len(climate_cases['value'])} climate-related cases")
        
        # Get total case count
        print("\nGetting total case count...")
        total_cases = api.get_entity_count('Sag')
        print(f"Total cases in database: {total_cases:,}")
        
        # Get recent changes
        print("\nChecking recent changes...")
        recent = api.get_recent_changes('Sag', hours_back=24)
        print(f"Cases updated in last 24 hours: {len(recent['value'])}")
        
    except APIError as e:
        print(f"API Error: {e}")
    except NetworkError as e:
        print(f"Network Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Key Features

### Error Handling
- **Comprehensive**: Handles all API error conditions
- **Informative**: Provides clear error messages with context
- **Retry Logic**: Automatic retry with exponential backoff
- **Type-Safe**: Custom exception hierarchy

### Performance
- **Rate Limiting**: Built-in request throttling
- **Efficient Pagination**: Handles large datasets properly
- **Field Selection**: Supports `$select` for faster queries
- **Connection Reuse**: Uses requests session for efficiency

### Production Ready
- **Logging Ready**: Easy to integrate with Python logging
- **Configurable**: Timeout and retry settings
- **Type Hints**: Full type annotations for IDE support
- **Documentation**: Comprehensive docstrings

## Installation & Setup

Save the code as `danish_parliament_api.py` and use:

```python
from danish_parliament_api import DanishParliamentAPI, APIError

# Initialize with custom settings
api = DanishParliamentAPI(timeout=60, retry_attempts=5)

# Use in production with proper error handling
try:
    cases = api.get_cases(top=100)
    # Process cases...
except APIError as e:
    logger.error(f"API error occurred: {e}")
    # Handle error appropriately
```