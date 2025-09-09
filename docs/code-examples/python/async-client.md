# Python Async Client

High-performance asynchronous client for the Danish Parliament API using `asyncio` and `aiohttp` for concurrent requests.

## Installation

```bash
pip install aiohttp asyncio  # Required for async functionality
```

## Async Client Implementation

```python
import asyncio
import aiohttp
import urllib.parse
import time
from typing import Dict, List, Optional, Union, Any, AsyncGenerator
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger('AsyncDanishParliamentAPI')

class AsyncDanishParliamentAPI:
    """
    High-performance async client for Danish Parliament API.
    
    Features:
    - Concurrent request processing
    - Connection pooling and reuse
    - Async pagination with generators
    - Rate limiting and backoff
    - Memory-efficient streaming
    """
    
    def __init__(self, max_connections: int = 10, request_delay: float = 0.1):
        """
        Initialize async API client.
        
        Args:
            max_connections: Maximum concurrent connections
            request_delay: Minimum delay between requests (seconds)
        """
        self.base_url = "https://oda.ft.dk/api/"
        self.max_connections = max_connections
        self.request_delay = request_delay
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure aiohttp session is created."""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=self.max_connections,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            
            timeout = aiohttp.ClientTimeout(total=60, connect=10)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'AsyncDanishParliamentAPI/1.0'}
            )
    
    async def close(self):
        """Clean up session resources."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _rate_limit(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            await asyncio.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()
    
    def _build_url(self, entity: str, **params) -> str:
        """Build properly encoded URL with OData parameters."""
        url = f"{self.base_url}{entity}"
        
        if not params:
            return url
        
        # Build query parameters with proper encoding
        query_parts = []
        for key, value in params.items():
            if value is not None:
                if key.startswith('$'):
                    encoded_key = urllib.parse.quote(key, safe='')
                else:
                    encoded_key = key
                
                encoded_value = urllib.parse.quote(str(value), safe='()\',%')
                query_parts.append(f"{encoded_key}={encoded_value}")
        
        return f"{url}?{'&'.join(query_parts)}"
    
    async def _make_request(self, url: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Make async HTTP request with error handling and retries.
        
        Args:
            url: URL to request
            max_retries: Number of retry attempts
            
        Returns:
            Parsed JSON response
            
        Raises:
            aiohttp.ClientError: For various client errors
        """
        await self._ensure_session()
        await self._rate_limit()
        
        for attempt in range(max_retries):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 400:
                        raise aiohttp.ClientError(
                            f"Bad Request (400): Invalid OData syntax for {url}"
                        )
                    elif response.status == 404:
                        if '/api/' in url and url.count('/') == 4:
                            raise aiohttp.ClientError(f"Entity not found: {url}")
                        else:
                            raise aiohttp.ClientError(f"Record not found: {url}")
                    elif response.status == 501:
                        raise aiohttp.ClientError(
                            "API is read-only - write operations not supported"
                        )
                    else:
                        response.raise_for_status()
                        
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1
                    logger.warning(f"Request timeout, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                raise aiohttp.ClientError(f"Request timeout after {max_retries} attempts")
                
            except aiohttp.ClientError:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1
                    await asyncio.sleep(wait_time)
                    continue
                raise
    
    async def get_cases(self, top: int = 100, skip: int = 0, 
                       filter_expr: Optional[str] = None,
                       expand: Optional[str] = None,
                       select: Optional[str] = None,
                       orderby: Optional[str] = None) -> Dict[str, Any]:
        """
        Get parliamentary cases asynchronously.
        
        Args:
            top: Number of records (max 100)
            skip: Records to skip
            filter_expr: OData filter
            expand: Related entities
            select: Specific fields
            orderby: Sort order
            
        Returns:
            API response with case data
        """
        params = {'$top': min(top, 100), '$skip': skip}
        
        if filter_expr:
            params['$filter'] = filter_expr
        if expand:
            params['$expand'] = expand
        if select:
            params['$select'] = select
        if orderby:
            params['$orderby'] = orderby
        
        url = self._build_url('Sag', **params)
        return await self._make_request(url)
    
    async def get_actors(self, top: int = 100, skip: int = 0,
                        filter_expr: Optional[str] = None,
                        expand: Optional[str] = None) -> Dict[str, Any]:
        """Get parliamentary actors asynchronously."""
        params = {'$top': min(top, 100), '$skip': skip}
        
        if filter_expr:
            params['$filter'] = filter_expr
        if expand:
            params['$expand'] = expand
        
        url = self._build_url('Aktør', **params)
        return await self._make_request(url)
    
    async def paginate_all(self, entity: str, batch_size: int = 100,
                          max_records: Optional[int] = None,
                          **params) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Async generator for paginating through all records.
        
        Args:
            entity: Entity name
            batch_size: Records per batch
            max_records: Maximum total records
            **params: Additional OData parameters
            
        Yields:
            Individual records
        """
        skip = 0
        total_yielded = 0
        batch_size = min(batch_size, 100)
        
        while True:
            # Build request parameters
            request_params = {**params, '$top': batch_size, '$skip': skip}
            url = self._build_url(entity, **request_params)
            
            try:
                response = await self._make_request(url)
                records = response.get('value', [])
                
                if not records:
                    break
                
                # Yield each record
                for record in records:
                    yield record
                    total_yielded += 1
                    
                    if max_records and total_yielded >= max_records:
                        return
                
                skip += batch_size
                
            except Exception as e:
                logger.error(f"Error paginating at skip={skip}: {e}")
                break
    
    async def get_concurrent_batches(self, entity: str, skip_values: List[int],
                                   batch_size: int = 100,
                                   **params) -> List[Dict[str, Any]]:
        """
        Fetch multiple batches concurrently.
        
        Args:
            entity: Entity name
            skip_values: List of skip values for concurrent requests
            batch_size: Records per batch
            **params: Additional OData parameters
            
        Returns:
            List of batch responses
        """
        tasks = []
        
        for skip in skip_values:
            request_params = {**params, '$top': batch_size, '$skip': skip}
            url = self._build_url(entity, **request_params)
            task = self._make_request(url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful responses
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch at skip={skip_values[i]} failed: {result}")
            else:
                successful_results.append(result)
        
        return successful_results
    
    async def search_parallel(self, queries: List[Dict[str, Any]],
                            max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """
        Execute multiple search queries in parallel.
        
        Args:
            queries: List of query parameters
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of query results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_query(query):
            async with semaphore:
                entity = query.pop('entity', 'Sag')
                url = self._build_url(entity, **query)
                return await self._make_request(url)
        
        tasks = [execute_query(query.copy()) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [r for r in results if not isinstance(r, Exception)]
    
    async def monitor_changes(self, entities: List[str], 
                            check_interval: int = 300,
                            hours_back: int = 4) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Continuously monitor for changes across multiple entities.
        
        Args:
            entities: List of entity names to monitor
            check_interval: Seconds between checks
            hours_back: Hours of history to check
            
        Yields:
            Change events as they're detected
        """
        last_check_time = datetime.now() - timedelta(hours=hours_back)
        
        while True:
            current_time = datetime.now()
            iso_time = last_check_time.strftime('%Y-%m-%dT%H:%M:%S')
            
            # Check all entities for changes
            queries = []
            for entity in entities:
                queries.append({
                    'entity': entity,
                    '$filter': f"opdateringsdato gt datetime'{iso_time}'",
                    '$orderby': 'opdateringsdato desc',
                    '$top': 100
                })
            
            try:
                results = await self.search_parallel(queries)
                
                # Process and yield changes
                for i, result in enumerate(results):
                    entity = entities[i]
                    changes = result.get('value', [])
                    
                    for change in changes:
                        yield {
                            'entity': entity,
                            'record': change,
                            'change_type': 'update',
                            'detected_at': current_time.isoformat()
                        }
                
                last_check_time = current_time
                
            except Exception as e:
                logger.error(f"Error monitoring changes: {e}")
            
            # Wait before next check
            await asyncio.sleep(check_interval)


# High-level async utility functions
async def bulk_fetch_cases(search_terms: List[str], 
                          max_concurrent: int = 5) -> Dict[str, List[Dict]]:
    """
    Fetch cases for multiple search terms concurrently.
    
    Args:
        search_terms: List of terms to search for
        max_concurrent: Maximum concurrent requests
        
    Returns:
        Dictionary mapping search terms to their results
    """
    async with AsyncDanishParliamentAPI(max_connections=max_concurrent) as api:
        queries = []
        for term in search_terms:
            queries.append({
                'entity': 'Sag',
                '$filter': f"substringof('{term}', titel)",
                '$top': 100
            })
        
        results = await api.search_parallel(queries, max_concurrent)
        
        # Map results back to search terms
        return {
            search_terms[i]: result.get('value', [])
            for i, result in enumerate(results)
            if i < len(search_terms)
        }

async def fast_pagination_example():
    """Demonstrate fast pagination with concurrent requests."""
    
    async with AsyncDanishParliamentAPI() as api:
        # Get total count first
        count_response = await api.get_cases(top=1, **{'$inlinecount': 'allpages'})
        total_records = int(count_response.get('odata.count', 0))
        
        print(f"Total records to fetch: {total_records:,}")
        
        # Generate skip values for concurrent batches
        batch_size = 100
        max_batches = 10  # Limit for demo
        skip_values = [i * batch_size for i in range(max_batches)]
        
        # Fetch multiple batches concurrently
        print(f"Fetching {len(skip_values)} batches concurrently...")
        start_time = time.time()
        
        batches = await api.get_concurrent_batches('Sag', skip_values, batch_size)
        
        end_time = time.time()
        total_records_fetched = sum(len(batch.get('value', [])) for batch in batches)
        
        print(f"Fetched {total_records_fetched:,} records in {end_time - start_time:.2f} seconds")
        print(f"Average: {total_records_fetched / (end_time - start_time):.0f} records/second")

async def streaming_example():
    """Demonstrate memory-efficient streaming of large datasets."""
    
    async with AsyncDanishParliamentAPI() as api:
        print("Streaming all climate-related cases...")
        
        count = 0
        async for case in api.paginate_all(
            'Sag',
            max_records=500,  # Limit for demo
            **{'$filter': "substringof('klima', titel)"}
        ):
            count += 1
            if count % 50 == 0:
                print(f"Processed {count} cases...")
            
            # Process each case individually without storing in memory
            # e.g., save to database, transform data, etc.
        
        print(f"Finished processing {count} climate cases")

async def real_time_monitoring_example():
    """Demonstrate real-time parliamentary activity monitoring."""
    
    entities_to_monitor = ['Sag', 'Afstemning', 'Dokument']
    
    async with AsyncDanishParliamentAPI() as api:
        print("Starting real-time monitoring...")
        print("Press Ctrl+C to stop")
        
        try:
            change_count = 0
            async for change in api.monitor_changes(
                entities_to_monitor, 
                check_interval=60,  # Check every minute
                hours_back=1        # Look at last hour
            ):
                change_count += 1
                entity = change['entity']
                record = change['record']
                
                print(f"Change #{change_count} in {entity}: {record.get('titel', record.get('navn', 'Unknown'))[:60]}")
                
                # Demo: stop after 10 changes
                if change_count >= 10:
                    break
        
        except KeyboardInterrupt:
            print("\nMonitoring stopped")

# Usage examples
async def main():
    """Main example demonstrating various async patterns."""
    
    # Example 1: Basic async usage
    print("=== Basic Async Usage ===")
    async with AsyncDanishParliamentAPI() as api:
        cases = await api.get_cases(top=10)
        print(f"Fetched {len(cases['value'])} cases")
    
    # Example 2: Concurrent searches
    print("\n=== Concurrent Searches ===")
    search_results = await bulk_fetch_cases([
        'klima', 'miljø', 'energi', 'transport'
    ])
    
    for term, results in search_results.items():
        print(f"'{term}': {len(results)} cases found")
    
    # Example 3: Fast pagination
    print("\n=== Fast Pagination ===")
    await fast_pagination_example()
    
    # Example 4: Streaming
    print("\n=== Streaming Example ===")
    await streaming_example()
    
    # Example 5: Real-time monitoring (commented out for demo)
    # print("\n=== Real-time Monitoring ===")
    # await real_time_monitoring_example()

if __name__ == "__main__":
    # Run the async examples
    asyncio.run(main())
```

## Advanced Async Patterns

### 1. Producer-Consumer Pattern for ETL

```python
import asyncio
from asyncio import Queue
import json

async def data_producer(api: AsyncDanishParliamentAPI, queue: Queue, entity: str):
    """Produce data and put into queue."""
    async for record in api.paginate_all(entity, max_records=1000):
        await queue.put(record)
    
    # Signal completion
    await queue.put(None)

async def data_processor(queue: Queue, output_file: str):
    """Process data from queue and save to file."""
    processed_count = 0
    
    with open(output_file, 'w', encoding='utf-8') as f:
        while True:
            record = await queue.get()
            
            if record is None:  # Producer finished
                break
            
            # Process the record (e.g., transform, validate)
            processed_record = {
                'id': record['id'],
                'title': record.get('titel', ''),
                'updated': record.get('opdateringsdato', ''),
                'processed_at': datetime.now().isoformat()
            }
            
            # Save to file
            f.write(json.dumps(processed_record, ensure_ascii=False) + '\n')
            processed_count += 1
            
            if processed_count % 100 == 0:
                print(f"Processed {processed_count} records...")
            
            queue.task_done()
    
    print(f"Finished processing {processed_count} records")

async def etl_pipeline_example():
    """Demonstrate ETL pipeline using producer-consumer pattern."""
    async with AsyncDanishParliamentAPI() as api:
        # Create queue for communication
        queue = asyncio.Queue(maxsize=100)  # Buffer size
        
        # Start producer and consumer concurrently
        producer_task = asyncio.create_task(
            data_producer(api, queue, 'Sag')
        )
        consumer_task = asyncio.create_task(
            data_processor(queue, 'processed_cases.jsonl')
        )
        
        # Wait for both to complete
        await asyncio.gather(producer_task, consumer_task)
```

### 2. Batch Processing with Error Recovery

```python
async def resilient_batch_processor(api: AsyncDanishParliamentAPI,
                                  entity: str, 
                                  batch_size: int = 100,
                                  max_concurrent: int = 5):
    """Process data in batches with error recovery."""
    
    # Get total count
    count_response = await api.get_cases(top=1, **{'$inlinecount': 'allpages'})
    total_records = int(count_response.get('odata.count', 0))
    
    print(f"Processing {total_records:,} records in batches of {batch_size}")
    
    semaphore = asyncio.Semaphore(max_concurrent)
    failed_batches = []
    
    async def process_batch(skip_value):
        async with semaphore:
            try:
                response = await api.get_cases(top=batch_size, skip=skip_value)
                records = response.get('value', [])
                
                # Simulate processing
                await asyncio.sleep(0.1)  # Processing time
                
                print(f" Processed batch at skip={skip_value}: {len(records)} records")
                return len(records)
                
            except Exception as e:
                print(f"L Failed batch at skip={skip_value}: {e}")
                failed_batches.append(skip_value)
                return 0
    
    # Create tasks for all batches
    skip_values = range(0, min(total_records, 1000), batch_size)  # Limit for demo
    tasks = [process_batch(skip) for skip in skip_values]
    
    # Process all batches
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful_records = sum(r for r in results if isinstance(r, int))
    
    print(f"\nProcessed {successful_records:,} records successfully")
    
    # Retry failed batches
    if failed_batches:
        print(f"Retrying {len(failed_batches)} failed batches...")
        retry_tasks = [process_batch(skip) for skip in failed_batches]
        retry_results = await asyncio.gather(*retry_tasks, return_exceptions=True)
        retry_successful = sum(r for r in retry_results if isinstance(r, int))
        print(f"Recovered {retry_successful:,} records from failed batches")
```

## Performance Benefits

The async client provides significant performance improvements:

1. **Concurrent Requests**: 5-10x faster for multiple queries
2. **Memory Efficiency**: Streaming prevents memory overflow
3. **Connection Reuse**: HTTP/1.1 connection pooling
4. **Non-blocking I/O**: CPU available for other tasks during network waits

## Usage Guidelines

1. **Always use context manager** (`async with`) for proper cleanup
2. **Respect rate limits** - the API doesn't have explicit limits but be courteous
3. **Handle exceptions** properly in async code
4. **Use semaphores** to limit concurrent requests
5. **Consider memory usage** when processing large datasets

## Production Deployment

```python
# For production, use proper error handling and logging
import logging
logging.basicConfig(level=logging.INFO)

async def production_example():
    """Production-ready async usage."""
    
    api_config = {
        'max_connections': 10,
        'request_delay': 0.1
    }
    
    try:
        async with AsyncDanishParliamentAPI(**api_config) as api:
            # Your production logic here
            pass
    except Exception as e:
        logging.error(f"Production API error: {e}")
        # Handle appropriately (alerts, fallback, etc.)
```

The async client is ideal for:
- **ETL pipelines** processing large datasets
- **Real-time monitoring** applications
- **Data analysis** requiring multiple concurrent queries
- **Web applications** needing responsive API calls