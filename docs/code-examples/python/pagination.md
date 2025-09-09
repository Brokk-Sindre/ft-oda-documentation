# Python Pagination

Comprehensive pagination strategies for handling large datasets from the Danish Parliament API.

## Overview

The Danish Parliament API has a hard limit of **100 records per request**. For large datasets, you need proper pagination strategies.

## Key Limitations

- **Maximum records per request**: 100 (enforced by API)
- **Total dataset sizes**: 
  - Sag (Cases): 96,538+ records
  - Aktør (Actors): 18,139+ records
  - Stemme (Votes): Millions of records

## Basic Pagination

```python
import time
from danish_parliament_api import DanishParliamentAPI

def paginate_all_records(api, entity_name, batch_size=100, max_records=None):
    """
    Fetch all records from an entity with pagination.
    
    Args:
        api: DanishParliamentAPI instance
        entity_name: Name of entity ('Sag', 'Aktør', etc.)
        batch_size: Records per request (max 100)
        max_records: Maximum total records to fetch
    
    Returns:
        List of all records
    """
    all_records = []
    skip = 0
    batch_size = min(batch_size, 100)  # Enforce API limit
    
    while True:
        # Fetch batch
        if entity_name == 'Sag':
            response = api.get_cases(top=batch_size, skip=skip)
        elif entity_name == 'Aktør':
            response = api.get_actors(top=batch_size, skip=skip)
        else:
            # Generic approach
            url = api._build_url(entity_name, **{'$top': batch_size, '$skip': skip})
            response = api._make_request(url)
        
        records = response.get('value', [])
        
        # Check if we got any records
        if not records:
            break
            
        all_records.extend(records)
        print(f"Fetched {len(records)} records, total: {len(all_records)}")
        
        # Check limits
        if max_records and len(all_records) >= max_records:
            all_records = all_records[:max_records]
            break
            
        skip += batch_size
        
        # Be respectful to the API
        time.sleep(0.1)  # 100ms delay between requests
    
    return all_records

# Usage example
api = DanishParliamentAPI()

# Get all cases (will take ~17 minutes for full dataset)
print("Fetching all cases...")
all_cases = paginate_all_records(api, 'Sag', max_records=1000)  # Limit for demo
print(f"Total cases fetched: {len(all_cases)}")
```

## Generator-Based Pagination

More memory-efficient approach using Python generators:

```python
def paginate_records_generator(api, entity_name, batch_size=100, 
                             filter_expr=None, expand=None, select=None):
    """
    Generator that yields records one by one with pagination.
    Memory efficient for very large datasets.
    
    Args:
        api: DanishParliamentAPI instance
        entity_name: Entity name
        batch_size: Records per request
        filter_expr: OData filter
        expand: Related entities to expand
        select: Fields to select
    
    Yields:
        Individual records
    """
    skip = 0
    batch_size = min(batch_size, 100)
    
    while True:
        # Build parameters
        params = {'$top': batch_size, '$skip': skip}
        if filter_expr:
            params['$filter'] = filter_expr
        if expand:
            params['$expand'] = expand
        if select:
            params['$select'] = select
        
        # Fetch batch
        url = api._build_url(entity_name, **params)
        response = api._make_request(url)
        records = response.get('value', [])
        
        if not records:
            break
            
        # Yield each record
        for record in records:
            yield record
            
        skip += batch_size
        time.sleep(0.1)  # Rate limiting

# Usage with generator
api = DanishParliamentAPI()

print("Processing climate cases one by one...")
climate_count = 0
for case in paginate_records_generator(
    api, 'Sag', 
    filter_expr="substringof('klima', titel)"
):
    climate_count += 1
    print(f"Case {climate_count}: {case['titel'][:60]}...")
    
    # Process each case individually without storing all in memory
    # This is perfect for ETL pipelines or data processing
    
    if climate_count >= 20:  # Demo limit
        break

print(f"Processed {climate_count} climate cases")
```

## Advanced Pagination with Progress Tracking

```python
from datetime import datetime
import json

class PaginationTracker:
    """Track pagination progress and handle resumption."""
    
    def __init__(self, entity_name, filename=None):
        self.entity_name = entity_name
        self.filename = filename or f"{entity_name}_progress.json"
        self.progress = self.load_progress()
    
    def load_progress(self):
        """Load pagination progress from file."""
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'skip': 0, 'total_fetched': 0, 'last_update': None}
    
    def save_progress(self):
        """Save current progress to file."""
        self.progress['last_update'] = datetime.now().isoformat()
        with open(self.filename, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def update_progress(self, records_fetched):
        """Update progress with new records."""
        self.progress['skip'] += 100  # Standard batch size
        self.progress['total_fetched'] += records_fetched
        self.save_progress()

def paginate_with_resume(api, entity_name, total_expected=None, 
                        filter_expr=None, expand=None):
    """
    Paginate with ability to resume from interruption.
    
    Args:
        api: DanishParliamentAPI instance
        entity_name: Entity to paginate
        total_expected: Expected total records (for progress)
        filter_expr: OData filter
        expand: Relationships to expand
    
    Returns:
        Generator yielding records with progress tracking
    """
    tracker = PaginationTracker(entity_name)
    skip = tracker.progress['skip']
    
    print(f"Resuming from record {skip:,}")
    if total_expected:
        print(f"Progress: {skip:,} / {total_expected:,} ({skip/total_expected*100:.1f}%)")
    
    batch_size = 100
    consecutive_empty = 0
    
    while consecutive_empty < 3:  # Stop after 3 empty responses
        params = {'$top': batch_size, '$skip': skip}
        if filter_expr:
            params['$filter'] = filter_expr
        if expand:
            params['$expand'] = expand
        
        try:
            url = api._build_url(entity_name, **params)
            response = api._make_request(url)
            records = response.get('value', [])
            
            if not records:
                consecutive_empty += 1
                skip += batch_size
                continue
            else:
                consecutive_empty = 0
            
            # Update progress
            tracker.update_progress(len(records))
            
            # Progress reporting
            if skip % 1000 == 0:  # Report every 1000 records
                print(f"Processed {tracker.progress['total_fetched']:,} records...")
                if total_expected:
                    pct = tracker.progress['total_fetched'] / total_expected * 100
                    print(f"Progress: {pct:.1f}%")
            
            # Yield records
            for record in records:
                yield record
            
            skip += batch_size
            time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            print(f"Error at skip={skip}: {e}")
            print("Progress saved. You can resume later.")
            raise

# Usage with resume capability
api = DanishParliamentAPI()

# Get total count first for progress tracking
total_cases = api.get_entity_count('Sag')
print(f"Total cases to process: {total_cases:,}")

# Process all cases with resume capability
processed = 0
try:
    for case in paginate_with_resume(api, 'Sag', total_expected=total_cases):
        processed += 1
        
        # Your processing logic here
        # e.g., save to database, analyze, transform, etc.
        
        if processed % 100 == 0:
            print(f"Processed {processed:,} cases...")
        
        # Demo: stop after 500 records
        if processed >= 500:
            break
            
except KeyboardInterrupt:
    print(f"\nInterrupted after processing {processed:,} cases")
    print("Progress has been saved. Run again to resume.")
```

## Parallel Pagination

For even faster data retrieval using concurrent requests:

```python
import concurrent.futures
import threading
from queue import Queue

class ParallelPaginator:
    """Fetch data using multiple parallel requests."""
    
    def __init__(self, api, max_workers=5):
        self.api = api
        self.max_workers = max_workers
        self.results_queue = Queue()
        self.lock = threading.Lock()
    
    def fetch_batch(self, entity_name, skip, batch_size=100, **params):
        """Fetch a single batch of records."""
        try:
            # Add pagination params
            params.update({'$top': batch_size, '$skip': skip})
            
            url = self.api._build_url(entity_name, **params)
            response = self.api._make_request(url)
            records = response.get('value', [])
            
            with self.lock:
                print(f"Fetched batch starting at {skip}: {len(records)} records")
            
            return skip, records
            
        except Exception as e:
            print(f"Error fetching batch at {skip}: {e}")
            return skip, []
    
    def paginate_parallel(self, entity_name, total_records=None, 
                         batch_size=100, **filter_params):
        """
        Paginate using parallel requests.
        
        Args:
            entity_name: Entity to fetch
            total_records: Total expected records (for batching)
            batch_size: Records per batch
            **filter_params: Additional OData parameters
        
        Returns:
            All records sorted by original order
        """
        # Get total count if not provided
        if total_records is None:
            total_records = self.api.get_entity_count(entity_name)
        
        print(f"Fetching {total_records:,} records in parallel...")
        
        # Create batch tasks
        batch_tasks = []
        for skip in range(0, total_records, batch_size):
            batch_tasks.append((skip, min(batch_size, total_records - skip)))
        
        # Execute in parallel
        all_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_skip = {
                executor.submit(
                    self.fetch_batch, entity_name, skip, size, **filter_params
                ): skip
                for skip, size in batch_tasks
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_skip):
                skip, records = future.result()
                all_results.append((skip, records))
        
        # Sort by original order and flatten
        all_results.sort(key=lambda x: x[0])
        all_records = []
        for skip, records in all_results:
            all_records.extend(records)
        
        return all_records

# Usage
api = DanishParliamentAPI()
paginator = ParallelPaginator(api, max_workers=3)  # Be respectful

# Fetch climate cases in parallel
climate_cases = paginator.paginate_parallel(
    'Sag',
    total_records=500,  # Limit for demo
    **{'$filter': "substringof('klima', titel)"}
)

print(f"Fetched {len(climate_cases)} climate cases in parallel")
```

## Best Practices

### 1. Always Use Rate Limiting
```python
import time

def respectful_pagination(api, entity_name):
    """Paginate with proper delays."""
    skip = 0
    while True:
        response = api.get_cases(top=100, skip=skip)
        records = response.get('value', [])
        
        if not records:
            break
        
        # Process records...
        yield from records
        
        skip += 100
        time.sleep(0.1)  # 100ms delay - be respectful!
```

### 2. Handle Network Interruptions
```python
def robust_pagination(api, entity_name):
    """Paginate with error recovery."""
    skip = 0
    consecutive_failures = 0
    
    while consecutive_failures < 5:
        try:
            response = api.get_cases(top=100, skip=skip)
            records = response.get('value', [])
            
            if not records:
                break
            
            consecutive_failures = 0  # Reset on success
            yield from records
            skip += 100
            
        except Exception as e:
            consecutive_failures += 1
            wait_time = min(2 ** consecutive_failures, 60)  # Exponential backoff
            print(f"Error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
```

### 3. Memory Management for Large Datasets
```python
def memory_efficient_processing(api, entity_name):
    """Process large datasets without storing all in memory."""
    
    for batch_start in range(0, 100000, 100):  # Process in chunks
        response = api.get_cases(top=100, skip=batch_start)
        records = response.get('value', [])
        
        if not records:
            break
        
        # Process batch immediately
        for record in records:
            # Do your processing here
            process_single_record(record)
        
        # Clear references to help garbage collection
        del records, response
        
        # Optional: Force garbage collection for very large datasets
        import gc
        gc.collect()
```

## Performance Tips

1. **Use `$select`** to fetch only needed fields
2. **Avoid deep `$expand`** for better performance  
3. **Implement backoff** for network errors
4. **Monitor API response times** and adjust accordingly
5. **Cache results** when appropriate
6. **Use parallel processing** carefully (max 3-5 concurrent requests)

## Error Handling in Pagination

```python
def safe_paginate(api, entity_name, max_retries=3):
    """Paginate with comprehensive error handling."""
    skip = 0
    
    while True:
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = api.get_cases(top=100, skip=skip)
                records = response.get('value', [])
                
                if not records:
                    return  # No more data
                
                yield from records
                break  # Success - exit retry loop
                
            except NetworkError as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise e
                print(f"Network error, retrying... ({retry_count}/{max_retries})")
                time.sleep(2 ** retry_count)  # Exponential backoff
                
            except APIError as e:
                print(f"API error: {e}")
                raise  # Don't retry API errors
        
        skip += 100
```

This comprehensive pagination system allows you to efficiently work with the entire Danish Parliament dataset while being respectful to the API and handling all edge cases.