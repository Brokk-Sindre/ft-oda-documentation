# cURL Testing Commands

Comprehensive testing and diagnostic commands for the Danish Parliament API. Perfect for health checks, debugging, and API exploration.

## API Health Checks

### 1. Basic Connectivity Tests

```bash
# Simple connectivity test
curl -I "https://oda.ft.dk/api/Sag"

# Test with timeout
curl --max-time 10 -I "https://oda.ft.dk/api/Sag"

# Test with verbose output for debugging
curl -v "https://oda.ft.dk/api/Sag?%24top=1"

# Check response time
curl -w "Total time: %{time_total}s\nHTTP code: %{http_code}\n" -o /dev/null -s "https://oda.ft.dk/api/Sag?%24top=1"
```

### 2. SSL/TLS Verification

```bash
# Check SSL certificate
curl -v "https://oda.ft.dk/api/Sag?%24top=1" 2>&1 | grep -E "(TLS|SSL|certificate)"

# Verify certificate chain
openssl s_client -connect oda.ft.dk:443 -servername oda.ft.dk < /dev/null

# Check supported TLS versions
curl --tlsv1.2 -I "https://oda.ft.dk/api/Sag" 2>&1 | head -1
```

### 3. Response Analysis

```bash
# Get full response headers
curl -D - -o /dev/null -s "https://oda.ft.dk/api/Sag?%24top=1"

# Check content encoding
curl -H "Accept-Encoding: gzip" -v "https://oda.ft.dk/api/Sag?%24top=1" 2>&1 | grep -i "content-encoding"

# Measure response size
curl -w "Response size: %{size_download} bytes\n" -o /dev/null -s "https://oda.ft.dk/api/Sag?%24top=100"
```

## API Functionality Tests

### 1. Entity Availability Tests

```bash
#!/bin/bash

# Test all major entities
ENTITIES=("Sag" "Aktør" "Afstemning" "Stemme" "Dokument" "Møde" "Fil")

echo "Testing entity availability:"
for entity in "${ENTITIES[@]}"; do
    HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null "https://oda.ft.dk/api/${entity}?%24top=1")
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ $entity: OK"
    else
        echo "L $entity: HTTP $HTTP_CODE"
    fi
done
```

### 2. OData Feature Tests

```bash
# Test $top parameter
echo "Testing \$top parameter:"
for size in 1 5 10 50 100; do
    COUNT=$(curl -s "https://oda.ft.dk/api/Sag?%24top=${size}" | jq '.value | length')
    echo "  Requested: $size, Received: $COUNT"
done

# Test $skip parameter
echo "Testing \$skip parameter:"
FIRST_ID=$(curl -s "https://oda.ft.dk/api/Sag?%24top=1&%24skip=0" | jq -r '.value[0].id')
SECOND_ID=$(curl -s "https://oda.ft.dk/api/Sag?%24top=1&%24skip=1" | jq -r '.value[0].id')
echo "  First record ID: $FIRST_ID"
echo "  Second record ID: $SECOND_ID"

# Test $inlinecount
echo "Testing \$inlinecount:"
RESPONSE=$(curl -s "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1")
COUNT=$(echo "$RESPONSE" | jq -r '."odata.count"')
echo "  Total Sag records: $COUNT"

# Test $filter
echo "Testing \$filter:"
FILTER_RESULT=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=id%20eq%201&%24top=1" | jq '.value | length')
echo "  Filter result count: $FILTER_RESULT"

# Test $expand
echo "Testing \$expand:"
EXPAND_TEST=$(curl -s "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=1" | jq -r '.value[0] | has("Sagskategori")')
echo "  Expansion successful: $EXPAND_TEST"

# Test $orderby
echo "Testing \$orderby:"
FIRST_DATE=$(curl -s "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc&%24top=1" | jq -r '.value[0].opdateringsdato')
LAST_DATE=$(curl -s "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20asc&%24top=1" | jq -r '.value[0].opdateringsdato')
echo "  Latest update: $FIRST_DATE"
echo "  Earliest update: $LAST_DATE"

# Test $select
echo "Testing \$select:"
SELECTED_FIELDS=$(curl -s "https://oda.ft.dk/api/Sag?%24select=id,titel&%24top=1" | jq -r '.value[0] | keys | @csv')
echo "  Selected fields: $SELECTED_FIELDS"
```

### 3. Data Quality Tests

```bash
# Check for null/empty data patterns
echo "Data quality tests:"

# Check for empty titles
EMPTY_TITLES=$(curl -s "https://oda.ft.dk/api/Sag?%24top=100" | jq '[.value[] | select(.titel == "" or .titel == null)] | length')
echo "  Cases with empty titles: $EMPTY_TITLES"

# Check for recent updates (data freshness)
RECENT_UPDATES=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-01-01T00:00:00'&%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"')
echo "  Cases updated in 2025: $RECENT_UPDATES"

# Check for consistent ID patterns
FIRST_IDS=$(curl -s "https://oda.ft.dk/api/Sag?%24top=5" | jq -r '.value[].id' | head -5)
echo "  First 5 case IDs: $(echo $FIRST_IDS | tr '\n' ' ')"

# Test Danish character encoding
DANISH_TEST=$(curl -s "https://oda.ft.dk/api/Aktør?%24filter=substringof('ø',navn)&%24top=1" | jq '.value | length')
echo "  Actors with 'ø' in name: $DANISH_TEST"
```

## Error Condition Tests

### 1. Expected Error Scenarios

```bash
echo "Testing error conditions:"

# Test invalid entity (should return 404)
INVALID_ENTITY=$(curl -s -w "%{http_code}" -o /dev/null "https://oda.ft.dk/api/InvalidEntity")
echo "  Invalid entity: HTTP $INVALID_ENTITY (expect 404)"

# Test invalid ID (should return 404 or empty result)
INVALID_ID=$(curl -s "https://oda.ft.dk/api/Sag(999999999)" | jq '.value | length // "null"')
echo "  Invalid ID result: $INVALID_ID records"

# Test invalid $expand (should return 400)
INVALID_EXPAND=$(curl -s -w "%{http_code}" -o /dev/null "https://oda.ft.dk/api/Sag?%24expand=NonExistentRelation")
echo "  Invalid expansion: HTTP $INVALID_EXPAND (expect 400)"

# Test malformed filter (behavior varies)
MALFORMED_FILTER=$(curl -s -w "%{http_code}" -o /dev/null "https://oda.ft.dk/api/Sag?%24filter=invalid syntax here")
echo "  Malformed filter: HTTP $MALFORMED_FILTER"

# Test very large $top (should be limited to 100)
LARGE_TOP=$(curl -s "https://oda.ft.dk/api/Sag?%24top=10000" | jq '.value | length')
echo "  Large \$top result: $LARGE_TOP records (max 100)"
```

### 2. Edge Case Testing

```bash
# Test empty results
echo "Testing edge cases:"

# Query that should return no results
NO_RESULTS=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=titel%20eq%20'ThisShouldNotExist12345'" | jq '.value | length')
echo "  No results query: $NO_RESULTS records"

# Test special characters in filter
SPECIAL_CHARS=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=substringof('&',titel)" | jq '.value | length')
echo "  Special character filter: $SPECIAL_CHARS records"

# Test date boundaries
FUTURE_DATE=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2030-01-01T00:00:00'" | jq '.value | length')
echo "  Future date filter: $FUTURE_DATE records"

# Test very old date
OLD_DATE=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20lt%20datetime'1990-01-01T00:00:00'" | jq '.value | length')
echo "  Old date filter: $OLD_DATE records"
```

## Performance Testing

### 1. Response Time Analysis

```bash
#!/bin/bash

# Test response times for different query sizes
echo "Performance testing:"

test_response_time() {
    local query=$1
    local description=$2
    
    local total_time=$(curl -w "%{time_total}" -o /dev/null -s "$query")
    echo "  $description: ${total_time}s"
}

test_response_time "https://oda.ft.dk/api/Sag?%24top=1" "Single record"
test_response_time "https://oda.ft.dk/api/Sag?%24top=10" "10 records"
test_response_time "https://oda.ft.dk/api/Sag?%24top=100" "100 records"
test_response_time "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=10" "With expansion"
test_response_time "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)&%24top=50" "With filter"
```

### 2. Concurrent Request Testing

```bash
#!/bin/bash

# Test concurrent requests (be respectful - max 3-5)
echo "Testing concurrent requests:"

concurrent_test() {
    local concurrent_count=$1
    echo "  Testing $concurrent_count concurrent requests..."
    
    start_time=$(date +%s.%N)
    
    for ((i=1; i<=concurrent_count; i++)); do
        curl -s "https://oda.ft.dk/api/Sag?%24top=10&%24skip=$((i*10))" > "/tmp/concurrent_$i.json" &
    done
    
    wait  # Wait for all background processes
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    
    echo "    Duration: ${duration}s"
    
    # Clean up
    rm -f /tmp/concurrent_*.json
}

concurrent_test 3
concurrent_test 5
```

### 3. Large Dataset Testing

```bash
# Test large dataset retrieval patterns
echo "Large dataset testing:"

# Test pagination performance
echo "  Testing pagination performance:"
for skip in 0 100 1000 5000; do
    time_taken=$(curl -w "%{time_total}" -o /dev/null -s "https://oda.ft.dk/api/Sag?%24top=100&%24skip=${skip}")
    echo "    Skip $skip: ${time_taken}s"
done

# Test complex queries on large datasets
echo "  Testing complex query performance:"
complex_time=$(curl -w "%{time_total}" -o /dev/null -s "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24filter=year(opdateringsdato)%20eq%202025&%24top=100")
echo "    Complex query: ${complex_time}s"
```

## Data Validation Tests

### 1. Schema Consistency

```bash
# Validate data schema consistency
echo "Schema validation tests:"

# Check required fields presence
REQUIRED_FIELDS_TEST=$(curl -s "https://oda.ft.dk/api/Sag?%24top=5" | jq -r '
    .value[] | 
    [.id, .titel, .opdateringsdato] | 
    map(type) | 
    @csv
' | head -1)
echo "  Required field types (id,titel,opdateringsdato): $REQUIRED_FIELDS_TEST"

# Check date format consistency
DATE_FORMAT_TEST=$(curl -s "https://oda.ft.dk/api/Sag?%24top=10" | jq -r '
    [.value[].opdateringsdato | test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}")] | 
    all
')
echo "  Date format consistency: $DATE_FORMAT_TEST"

# Check ID uniqueness in sample
ID_UNIQUENESS=$(curl -s "https://oda.ft.dk/api/Sag?%24top=100" | jq '
    .value | 
    length as $total | 
    map(.id) | 
    unique | 
    length as $unique | 
    $total == $unique
')
echo "  ID uniqueness in sample: $ID_UNIQUENESS"
```

### 2. Relationship Integrity

```bash
# Test relationship integrity
echo "Relationship integrity tests:"

# Test foreign key consistency
FK_TEST=$(curl -s "https://oda.ft.dk/api/SagAktør?%24expand=Sag,Aktør&%24top=5" | jq -r '
    .value[] | 
    select(.Sag and .Aktør) | 
    "✅ SagAktør \(.id): Links Sag \(.sagid) to Aktør \(.aktørid)"
')
echo "$FK_TEST" | head -3

# Test expansion consistency  
EXPAND_TEST=$(curl -s "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=5" | jq '
    [.value[] | select(.Sagskategori)] | length
')
TOTAL_WITH_CATEGORY=$(curl -s "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=5" | jq '.value | length')
echo "  Expansion success rate: $EXPAND_TEST/$TOTAL_WITH_CATEGORY have categories"
```

## Comprehensive Health Check Script

```bash
#!/bin/bash

# Complete API health check
echo "=== Danish Parliament API Health Check ==="
echo "Timestamp: $(date -u)"
echo

# Basic connectivity
echo "1. Basic Connectivity:"
HTTP_STATUS=$(curl -s -w "%{http_code}" -o /dev/null --max-time 10 "https://oda.ft.dk/api/Sag?%24top=1")
if [ "$HTTP_STATUS" = "200" ]; then
    echo "  ✅ API is accessible (HTTP $HTTP_STATUS)"
else
    echo "  L API connection failed (HTTP $HTTP_STATUS)"
    exit 1
fi

# Response time
echo "2. Performance:"
RESPONSE_TIME=$(curl -w "%{time_total}" -o /dev/null -s --max-time 30 "https://oda.ft.dk/api/Sag?%24top=1")
echo "  Response time: ${RESPONSE_TIME}s"

# Data freshness
echo "3. Data Freshness:"
LATEST_UPDATE=$(curl -s "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc&%24top=1" | jq -r '.value[0].opdateringsdato')
echo "  Latest case update: $LATEST_UPDATE"

# Record counts
echo "4. Dataset Sizes:"
CASE_COUNT=$(curl -s "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"')
ACTOR_COUNT=$(curl -s "https://oda.ft.dk/api/Aktør?%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"')
echo "  Total cases: $CASE_COUNT"
echo "  Total actors: $ACTOR_COUNT"

# OData functionality
echo "5. OData Features:"
FILTER_TEST=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=id%20eq%201" | jq '.value | length')
EXPAND_TEST=$(curl -s "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=1" | jq -r '.value[0] | has("Sagskategori")')
echo "  Filtering: $([ "$FILTER_TEST" -ge 0 ] && echo "✅ Working" || echo "L Failed")"
echo "  Expansion: $([ "$EXPAND_TEST" = "true" ] && echo "✅ Working" || echo "L Failed")"

# Recent activity
echo "6. Recent Activity:"
TODAY=$(date +%Y-%m-%d)
RECENT_COUNT=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=startswith(opdateringsdato,'${TODAY}')&%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"')
echo "  Cases updated today: $RECENT_COUNT"

echo
echo "Health check complete!"

# Summary
if [ "$HTTP_STATUS" = "200" ] && [ $(echo "$RESPONSE_TIME < 5.0" | bc) -eq 1 ]; then
    echo "✅ API Status: HEALTHY"
    exit 0
else
    echo "   API Status: DEGRADED"
    exit 1
fi
```

## Debugging Utilities

### 1. URL Encoding Helper

```bash
# Helper function to properly encode OData URLs
encode_odata_url() {
    local base_url="https://oda.ft.dk/api/"
    local entity=$1
    local params=$2
    
    # Replace $ with %24
    encoded_params=$(echo "$params" | sed 's/\$/%24/g')
    
    echo "${base_url}${entity}?${encoded_params}"
}

# Usage examples
echo "Encoded URLs:"
echo $(encode_odata_url "Sag" "top=5&filter=id eq 1")
echo $(encode_odata_url "Aktør" "expand=Aktørtype&orderby=navn")
```

### 2. Response Inspector

```bash
# Detailed response analysis
inspect_response() {
    local url=$1
    echo "Inspecting: $url"
    
    # Get full response with headers
    RESPONSE=$(curl -i -s "$url")
    
    # Extract headers and body
    HEADERS=$(echo "$RESPONSE" | sed '/^\r$/q')
    BODY=$(echo "$RESPONSE" | sed '1,/^\r$/d')
    
    echo "Headers:"
    echo "$HEADERS" | grep -E "(HTTP|Content-|Cache-|Server)"
    
    echo "Body structure:"
    echo "$BODY" | jq -r 'keys'
    
    if echo "$BODY" | jq -e '.value' > /dev/null; then
        RECORD_COUNT=$(echo "$BODY" | jq '.value | length')
        echo "Records returned: $RECORD_COUNT"
        
        if [ "$RECORD_COUNT" -gt 0 ]; then
            echo "First record keys:"
            echo "$BODY" | jq -r '.value[0] | keys | @csv'
        fi
    fi
}

# Usage
inspect_response "https://oda.ft.dk/api/Sag?%24top=3"
```

These testing commands provide comprehensive coverage for validating API functionality, performance, and data quality. Use them for troubleshooting, monitoring, and ensuring reliable integration with the Danish Parliament API.