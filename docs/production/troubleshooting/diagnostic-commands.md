# Diagnostic Commands and Tools

This comprehensive reference provides essential command-line tools and scripts for diagnosing issues with the Danish Parliamentary OData API in production environments.

## Overview

The diagnostic commands in this guide are organized by use case, from basic connectivity testing to complex performance analysis. All commands are tested against the production API at `https://oda.ft.dk/api/` and include expected outputs for validation.

!!! warning "URL Encoding Critical"
    Always use `%24` instead of `$` in OData parameters. This is the most common cause of diagnostic failures.

## Quick Health Check Commands

### Basic Connectivity Test
```bash
# Test basic API connectivity
curl -s "https://oda.ft.dk/api/Sag?%24top=1" | jq '.value | length'
# Expected output: 1
```

### API Status Verification
```bash
# Check HTTP status and headers
curl -I "https://oda.ft.dk/api/Sag"
# Expected: HTTP/1.1 200 OK
```

### URL Encoding Validation
```bash
# Test proper URL encoding (should return 5 records)
curl -s "https://oda.ft.dk/api/Sag?%24top=5" | jq '.value | length'
# Expected output: 5

# Test incorrect encoding (will return default 100 records)
curl -s "https://oda.ft.dk/api/Sag?\$top=5" | jq '.value | length'  
# Expected output: 100 (indicates encoding problem)
```

## Essential Diagnostic Commands

### 1. Entity Availability Testing

```bash
# Test all major entities
entities=("Sag" "Aktør" "Afstemning" "Stemme" "Dokument" "Møde")
for entity in "${entities[@]}"; do
    status=$(curl -s -w "%{http_code}" -o /dev/null "https://oda.ft.dk/api/$entity?%24top=1")
    echo "$entity: HTTP $status"
done
```

### 2. Data Count Verification

```bash
# Get total record counts for major entities
curl -s "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1" | jq '.["odata.count"]'
# Expected: "96538" (approximate, will grow over time)

curl -s "https://oda.ft.dk/api/Aktør?%24inlinecount=allpages&%24top=1" | jq '.["odata.count"]'
# Expected: "18139" (approximate)
```

### 3. Filter Functionality Test

```bash
# Test basic filter functionality
curl -s "https://oda.ft.dk/api/Sag?%24filter=id%20eq%201&%24top=1" | jq '.value[0].id'
# Expected output: 1

# Test filter with no results
curl -s "https://oda.ft.dk/api/Sag?%24filter=titel%20eq%20'nonexistentcase'" | jq '.value | length'
# Expected output: 0
```

### 4. Expansion Capability Test

```bash
# Test single-level expansion
curl -s "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=1" | jq '.value[0].Sagskategori'
# Expected: JSON object with category data

# Test two-level expansion
curl -s "https://oda.ft.dk/api/Afstemning?%24expand=Stemme/Aktør&%24top=1" | jq '.value[0].Stemme[0].Aktør'
# Expected: JSON object with actor data
```

## curl Commands for API Testing

### Authentication Testing

```bash
# Verify no authentication is required
curl -H "Authorization: Bearer invalid-token" "https://oda.ft.dk/api/Sag?%24top=1"
# Should work normally (auth headers ignored)

# Test with various user agents
curl -H "User-Agent: Bot/1.0" "https://oda.ft.dk/api/Sag?%24top=1"
# Should work (no user agent restrictions)
```

### Content Type and Encoding Tests

```bash
# Test gzip compression support
curl -H "Accept-Encoding: gzip" "https://oda.ft.dk/api/Sag?%24top=1" | gunzip | jq '.value | length'
# Expected: 1

# Test UTF-8 encoding with Danish characters
curl -s "https://oda.ft.dk/api/Aktør?%24filter=substringof('ø',navn)&%24top=3" | jq '.value[0].navn'
# Should return Danish names with proper ø character
```

### Error Condition Testing

```bash
# Test invalid entity (should return 404)
curl -s -w "\nHTTP_STATUS:%{http_code}" "https://oda.ft.dk/api/InvalidEntity"
# Expected: HTTP_STATUS:404

# Test invalid entity ID (should return 404)  
curl -s -w "\nHTTP_STATUS:%{http_code}" "https://oda.ft.dk/api/Sag(999999999)"
# Expected: HTTP_STATUS:404

# Test invalid expansion (should return 400)
curl -s -w "\nHTTP_STATUS:%{http_code}" "https://oda.ft.dk/api/Sag?%24expand=NonExistentRelation&%24top=1"
# Expected: HTTP_STATUS:400
```

## Network Diagnostic Tools

### Connection and SSL Testing

```bash
# Test SSL certificate and TLS version
curl -I -v "https://oda.ft.dk/api/Sag" 2>&1 | grep -E "(TLS|SSL|cipher)"

# Test connection timing
curl -s -w "connect:%{time_connect} ssl:%{time_appconnect} total:%{time_total}\n" -o /dev/null "https://oda.ft.dk/api/Sag?%24top=1"
```

### DNS and Routing Tests

```bash
# DNS resolution test
dig oda.ft.dk

# Traceroute to API server
traceroute oda.ft.dk

# Test from different geographic locations (if available)
curl -H "X-Forwarded-For: 8.8.8.8" "https://oda.ft.dk/api/Sag?%24top=1"
```

### Network Performance Testing

```bash
# Test concurrent connections
for i in {1..5}; do
    (curl -s "https://oda.ft.dk/api/Sag?%24top=10" > /dev/null &)
done
wait
echo "Concurrent test completed"

# Bandwidth test with larger dataset
time curl -s "https://oda.ft.dk/api/Sag?%24top=1000" > /dev/null
# Typical response time: 1-3 seconds
```

## Performance Testing Commands

### Response Time Benchmarking

```bash
#!/bin/bash
# Performance benchmark script
test_queries=(
    "Sag?%24top=1"
    "Sag?%24top=100" 
    "Sag?%24top=1000"
    "Sag?%24expand=Sagskategori&%24top=10"
    "Afstemning?%24expand=Stemme/Aktør&%24top=10"
)

for query in "${test_queries[@]}"; do
    echo "Testing: $query"
    time curl -s "https://oda.ft.dk/api/$query" > /dev/null
    echo "---"
done
```

### Load Testing Script

```bash
#!/bin/bash
# Simple load test
CONCURRENT=10
REQUESTS=100

echo "Starting load test: $CONCURRENT concurrent users, $REQUESTS requests each"
for i in $(seq 1 $CONCURRENT); do
    (
        for j in $(seq 1 $REQUESTS); do
            curl -s "https://oda.ft.dk/api/Sag?%24top=10" > /dev/null
        done
    ) &
done
wait
echo "Load test completed"
```

### Memory Usage Testing

```bash
# Test large response handling
curl -s "https://oda.ft.dk/api/Sag?%24top=10000" | wc -c
# Expected: ~50MB response size

# Monitor memory usage during large requests
/usr/bin/time -v curl -s "https://oda.ft.dk/api/Sag?%24top=5000" > /dev/null
```

## Data Validation and Integrity Checks

### Data Consistency Tests

```bash
# Check for data consistency across related entities
sag_count=$(curl -s "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1" | jq -r '.["odata.count"]')
echo "Total Sag count: $sag_count"

# Verify recent updates
curl -s "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc&%24top=5" | jq '.value[].opdateringsdato'
```

### Relationship Integrity Validation

```bash
# Test entity relationships
curl -s "https://oda.ft.dk/api/Sag?%24expand=SagAktør&%24top=1" | jq '.value[0].SagAktør | length'
# Should return number > 0 for cases with actors

# Verify junction table consistency
curl -s "https://oda.ft.dk/api/SagAktør?%24top=1" | jq '.value[0]'
# Should contain sagid and aktørid
```

### Data Quality Checks

```bash
# Check for empty/null values in critical fields
curl -s "https://oda.ft.dk/api/Sag?%24select=titel&%24top=100" | jq '.value[] | select(.titel == "")'
# Should ideally return no results

# Verify date format consistency
curl -s "https://oda.ft.dk/api/Sag?%24select=opdateringsdato&%24top=10" | jq '.value[].opdateringsdato'
# All dates should follow ISO format
```

## Log Analysis Commands

### API Response Analysis

```bash
# Extract and analyze API response patterns
curl -s "https://oda.ft.dk/api/Sag?%24top=100" | jq '.value[] | {id, titel, opdateringsdato}' > api_sample.json

# Analyze response structure
jq 'keys' api_sample.json | sort | uniq -c
```

### Error Pattern Detection

```bash
# Test common error scenarios
error_tests=(
    "InvalidEntity"
    "Sag(999999999)"
    "Sag?%24filter=invalid_field%20eq%20'test'"
    "Sag?%24expand=InvalidRelation"
)

for test in "${error_tests[@]}"; do
    echo "Testing: $test"
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "https://oda.ft.dk/api/$test")
    echo "$response" | grep "HTTPSTATUS"
    echo "---"
done
```

### Traffic Pattern Analysis

```bash
# Monitor API usage patterns (requires log access)
# Example for analyzing access logs:
# awk '/api\/Sag/ {print $1}' access.log | sort | uniq -c | sort -nr | head -10
```

## System Health Check Procedures

### Complete API Health Assessment

```bash
#!/bin/bash
# comprehensive-health-check.sh

echo "=== Danish Parliamentary API Health Check ==="
echo "Timestamp: $(date)"
echo

# 1. Basic connectivity
echo "1. Testing basic connectivity..."
if curl -s "https://oda.ft.dk/api/Sag?%24top=1" > /dev/null; then
    echo " Basic connectivity: OK"
else
    echo "L Basic connectivity: FAILED"
fi

# 2. SSL certificate
echo "2. Testing SSL certificate..."
if openssl s_client -connect oda.ft.dk:443 -servername oda.ft.dk < /dev/null 2>/dev/null | grep -q "Verify return code: 0"; then
    echo " SSL certificate: Valid"
else
    echo "L SSL certificate: Invalid"
fi

# 3. Response times
echo "3. Testing response times..."
response_time=$(curl -s -w "%{time_total}" -o /dev/null "https://oda.ft.dk/api/Sag?%24top=100")
if (( $(echo "$response_time < 2.0" | bc -l) )); then
    echo " Response time: $response_time seconds (Good)"
else
    echo "  Response time: $response_time seconds (Slow)"
fi

# 4. Data availability
echo "4. Testing data availability..."
count=$(curl -s "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1" | jq -r '.["odata.count"]')
if [[ "$count" =~ ^[0-9]+$ ]] && (( count > 90000 )); then
    echo " Data availability: $count records available"
else
    echo "L Data availability: Insufficient data ($count)"
fi

# 5. Feature functionality
echo "5. Testing core features..."
filter_test=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=id%20eq%201&%24top=1" | jq '.value | length')
if [[ "$filter_test" == "1" ]]; then
    echo " Filtering: Working"
else
    echo "L Filtering: Not working"
fi

expand_test=$(curl -s "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=1" | jq '.value[0].Sagskategori')
if [[ "$expand_test" != "null" ]]; then
    echo " Expansion: Working"
else
    echo "L Expansion: Not working"
fi

echo
echo "=== Health Check Complete ==="
```

### Entity-Specific Health Checks

```bash
# Check status of all major entities
entities=("Sag" "Aktør" "Afstemning" "Stemme" "Dokument" "Møde" "DokumentAktør" "SagAktør")

echo "Entity Status Report:"
for entity in "${entities[@]}"; do
    count=$(curl -s "https://oda.ft.dk/api/$entity?%24inlinecount=allpages&%24top=1" | jq -r '.["odata.count"]' 2>/dev/null)
    if [[ "$count" =~ ^[0-9]+$ ]]; then
        echo "$entity: $count records "
    else
        echo "$entity: ERROR L"
    fi
done
```

## Automated Diagnostic Scripts

### Comprehensive Diagnostic Script

```bash
#!/bin/bash
# diagnostic-suite.sh - Complete API diagnostic suite

API_BASE="https://oda.ft.dk/api"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
LOG_FILE="api_diagnostics_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

test_url_encoding() {
    log "Testing URL encoding..."
    
    # Test correct encoding
    correct=$(curl -s "$API_BASE/Sag?%24top=5" | jq '.value | length')
    if [[ "$correct" == "5" ]]; then
        log " URL encoding test: PASS"
    else
        log "L URL encoding test: FAIL (got $correct, expected 5)"
    fi
    
    # Test incorrect encoding (common mistake)
    incorrect=$(curl -s "$API_BASE/Sag?\$top=5" | jq '.value | length')
    if [[ "$incorrect" == "100" ]]; then
        log " Incorrect encoding detected properly"
    else
        log "  Unexpected behavior with incorrect encoding: $incorrect"
    fi
}

test_odata_features() {
    log "Testing OData features..."
    
    # Test $filter
    filter_result=$(curl -s "$API_BASE/Sag?%24filter=id%20eq%201&%24top=1" | jq '.value[0].id')
    if [[ "$filter_result" == "1" ]]; then
        log " \$filter: Working"
    else
        log "L \$filter: Not working"
    fi
    
    # Test $select
    select_result=$(curl -s "$API_BASE/Sag?%24select=id,titel&%24top=1" | jq '.value[0] | keys | length')
    if [[ "$select_result" == "2" ]]; then
        log " \$select: Working"
    else
        log "L \$select: Not working"
    fi
    
    # Test $expand
    expand_result=$(curl -s "$API_BASE/Sag?%24expand=Sagskategori&%24top=1" | jq '.value[0].Sagskategori')
    if [[ "$expand_result" != "null" ]]; then
        log " \$expand: Working"
    else
        log "L \$expand: Not working"
    fi
    
    # Test $orderby
    orderby_result=$(curl -s "$API_BASE/Sag?%24orderby=id%20desc&%24top=2" | jq '.value[0].id > .value[1].id')
    if [[ "$orderby_result" == "true" ]]; then
        log " \$orderby: Working"
    else
        log "L \$orderby: Not working"
    fi
}

test_performance() {
    log "Testing performance..."
    
    # Small query
    small_time=$(curl -s -w "%{time_total}" -o /dev/null "$API_BASE/Sag?%24top=10")
    log "Small query (10 records): ${small_time}s"
    
    # Medium query
    medium_time=$(curl -s -w "%{time_total}" -o /dev/null "$API_BASE/Sag?%24top=100")
    log "Medium query (100 records): ${medium_time}s"
    
    # Large query
    large_time=$(curl -s -w "%{time_total}" -o /dev/null "$API_BASE/Sag?%24top=1000")
    log "Large query (1000 records): ${large_time}s"
    
    # Complex query
    complex_time=$(curl -s -w "%{time_total}" -o /dev/null "$API_BASE/Afstemning?%24expand=Stemme/Aktør&%24top=10")
    log "Complex query (with expansion): ${complex_time}s"
}

# Run all tests
log "Starting comprehensive API diagnostics"
test_url_encoding
test_odata_features
test_performance
log "Diagnostic suite completed. Results saved to: $LOG_FILE"
```

### Continuous Monitoring Script

```bash
#!/bin/bash
# monitor-api.sh - Continuous API monitoring

INTERVAL=300  # 5 minutes
API_BASE="https://oda.ft.dk/api"

monitor_loop() {
    while true; do
        timestamp=$(date +"%Y-%m-%d %H:%M:%S")
        
        # Test API availability
        if response=$(curl -s -w "time:%{time_total} status:%{http_code}" "$API_BASE/Sag?%24top=1"); then
            time=$(echo "$response" | grep -o 'time:[0-9.]*' | cut -d: -f2)
            status=$(echo "$response" | grep -o 'status:[0-9]*' | cut -d: -f2)
            
            if [[ "$status" == "200" ]]; then
                echo "[$timestamp] API OK - Response time: ${time}s"
            else
                echo "[$timestamp] API ERROR - Status: $status"
            fi
        else
            echo "[$timestamp] API DOWN - Connection failed"
        fi
        
        sleep $INTERVAL
    done
}

monitor_loop
```

## Production Monitoring Commands

### Real-time API Status

```bash
# Monitor API in real-time
watch -n 10 'curl -s -w "Status: %{http_code} | Time: %{time_total}s\n" -o /dev/null "https://oda.ft.dk/api/Sag?%24top=1"'
```

### Alert-based Monitoring

```bash
#!/bin/bash
# alert-monitor.sh - Send alerts when API issues detected

ALERT_EMAIL="admin@example.com"
MAX_RESPONSE_TIME=3.0
CHECK_INTERVAL=60

while true; do
    response_time=$(curl -s -w "%{time_total}" -o /dev/null "https://oda.ft.dk/api/Sag?%24top=10")
    http_status=$(curl -s -w "%{http_code}" -o /dev/null "https://oda.ft.dk/api/Sag?%24top=1")
    
    # Check for slow response
    if (( $(echo "$response_time > $MAX_RESPONSE_TIME" | bc -l) )); then
        echo "ALERT: Slow response time: ${response_time}s" | mail -s "API Performance Alert" "$ALERT_EMAIL"
    fi
    
    # Check for HTTP errors
    if [[ "$http_status" != "200" ]]; then
        echo "ALERT: API returning HTTP $http_status" | mail -s "API Status Alert" "$ALERT_EMAIL"
    fi
    
    sleep $CHECK_INTERVAL
done
```

### Capacity Monitoring

```bash
# Monitor data growth patterns
check_growth() {
    entities=("Sag" "Aktør" "Afstemning" "Stemme" "Dokument")
    
    for entity in "${entities[@]}"; do
        count=$(curl -s "https://oda.ft.dk/api/$entity?%24inlinecount=allpages&%24top=1" | jq -r '.["odata.count"]')
        echo "$(date): $entity count: $count" >> "${entity}_growth.log"
    done
}

# Run hourly
while true; do
    check_growth
    sleep 3600
done
```

## Emergency Response and Recovery Commands

### Incident Response Checklist

```bash
#!/bin/bash
# incident-response.sh - Emergency diagnostic commands

echo "=== INCIDENT RESPONSE DIAGNOSTIC ==="
echo "Timestamp: $(date)"
echo

# 1. Basic connectivity test
echo "1. Testing basic connectivity..."
if timeout 10 curl -s "https://oda.ft.dk/api/Sag?%24top=1" > /dev/null 2>&1; then
    echo " API is responding"
else
    echo "L API is not responding"
    exit 1
fi

# 2. Check response times for key endpoints
echo "2. Checking response times..."
critical_endpoints=(
    "Sag?%24top=1"
    "Aktør?%24top=1" 
    "Afstemning?%24top=1"
)

for endpoint in "${critical_endpoints[@]}"; do
    time=$(curl -s -w "%{time_total}" -o /dev/null "https://oda.ft.dk/api/$endpoint")
    echo "$endpoint: ${time}s"
done

# 3. Test core functionality
echo "3. Testing core functionality..."
filter_test=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=id%20eq%201" | jq '.value | length')
echo "Filter test result: $filter_test (should be 1)"

# 4. Check data freshness
echo "4. Checking data freshness..."
latest=$(curl -s "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc&%24top=1" | jq -r '.value[0].opdateringsdato')
echo "Latest update: $latest"

# 5. Test error handling
echo "5. Testing error handling..."
error_status=$(curl -s -w "%{http_code}" -o /dev/null "https://oda.ft.dk/api/InvalidEntity")
echo "Invalid entity status: $error_status (should be 404)"

echo "=== DIAGNOSTIC COMPLETE ==="
```

### Recovery Verification Commands

```bash
# Verify API recovery after an incident
recovery_test() {
    echo "Starting recovery verification..."
    
    # Test basic operations
    tests=(
        "Basic query:Sag?%24top=5"
        "Filter test:Sag?%24filter=id%20eq%201"
        "Expansion test:Sag?%24expand=Sagskategori&%24top=1"
        "Complex query:Afstemning?%24expand=Stemme&%24top=3"
    )
    
    for test in "${tests[@]}"; do
        name=$(echo "$test" | cut -d: -f1)
        query=$(echo "$test" | cut -d: -f2)
        
        if result=$(curl -s "https://oda.ft.dk/api/$query" | jq '.value | length'); then
            echo " $name: $result records"
        else
            echo "L $name: Failed"
        fi
    done
    
    echo "Recovery verification complete"
}

recovery_test
```

### Data Integrity Verification

```bash
# Verify data integrity after recovery
integrity_check() {
    echo "Performing post-incident data integrity check..."
    
    # Check record counts
    entities=("Sag" "Aktør" "Afstemning" "Stemme")
    declare -A expected_counts
    expected_counts["Sag"]=96000    # Approximate, adjust as needed
    expected_counts["Aktør"]=18000
    expected_counts["Afstemning"]=10000
    expected_counts["Stemme"]=500000
    
    for entity in "${entities[@]}"; do
        current=$(curl -s "https://oda.ft.dk/api/$entity?%24inlinecount=allpages&%24top=1" | jq -r '.["odata.count"]')
        expected=${expected_counts[$entity]}
        
        if (( current >= expected )); then
            echo " $entity: $current records (>= $expected expected)"
        else
            echo "L $entity: $current records (< $expected expected)"
        fi
    done
    
    # Check relationship integrity
    echo "Checking relationship integrity..."
    junction_test=$(curl -s "https://oda.ft.dk/api/SagAktør?%24top=1" | jq '.value | length')
    echo "Junction table test: $junction_test (should be 1)"
    
    echo "Data integrity check complete"
}

integrity_check
```

## Troubleshooting Common Issues

### Silent Filter Failures

The API has a critical behavior where invalid filter field names don't return errors - they return the complete unfiltered dataset:

```bash
# This will return ALL records instead of filtering (silent failure)
curl "https://oda.ft.dk/api/Sag?%24filter=nonexistent_field%20eq%20'test'" | jq '.value | length'
# Dangerous: May return 96,538+ records

# Always validate filter fields first
curl "https://oda.ft.dk/api/Sag?%24top=1" | jq '.value[0] | keys'
# Shows available fields for validation
```

### URL Encoding Issues

```bash
# Common mistake: Using backslash escaping (doesn't work)
curl "https://oda.ft.dk/api/Sag?\$top=5" | jq '.value | length'
# Returns: 100 (default limit, parameter ignored)

# Correct: Use URL encoding
curl "https://oda.ft.dk/api/Sag?%24top=5" | jq '.value | length'  
# Returns: 5 (parameter respected)
```

### Performance Issues

```bash
# Avoid: Large queries without field selection
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør&%24top=1000"  # Slow

# Better: Select only needed fields
curl "https://oda.ft.dk/api/Sag?%24select=id,titel&%24top=1000"  # Fast

# Optimal: Use pagination
curl "https://oda.ft.dk/api/Sag?%24top=100&%24skip=0"  # Manageable chunks
```

## Advanced Diagnostic Techniques

### Metadata Analysis

```bash
# Extract complete entity schema
curl -s "https://oda.ft.dk/api/\$metadata" > api_metadata.xml

# Count available entities
grep -c "EntityType Name" api_metadata.xml

# Find all navigation properties
grep "NavigationProperty" api_metadata.xml | head -10
```

### Relationship Mapping

```bash
# Map entity relationships
map_relationships() {
    entities=$(curl -s "https://oda.ft.dk/api/\$metadata" | grep -o 'EntityType Name="[^"]*"' | cut -d'"' -f2)
    
    for entity in $entities; do
        echo "Testing $entity relationships..."
        curl -s "https://oda.ft.dk/api/$entity?\$top=1" | jq -r ".value[0] | keys[] | select(. | test(\"^[A-Z]\"))" 2>/dev/null | head -5
    done
}
```

### Performance Profiling

```bash
# Profile different query types
profile_queries() {
    queries=(
        "Simple:Sag?%24top=100"
        "Filtered:Sag?%24filter=year(opdateringsdato)%20eq%202025&%24top=100"
        "Selected:Sag?%24select=id,titel&%24top=100"
        "Expanded:Sag?%24expand=Sagskategori&%24top=100"
        "Complex:Afstemning?%24expand=Stemme/Aktør&%24filter=year(opdateringsdato)%20eq%202025&%24top=50"
    )
    
    for query in "${queries[@]}"; do
        name=$(echo "$query" | cut -d: -f1)
        url=$(echo "$query" | cut -d: -f2)
        
        echo "Profiling $name query..."
        time curl -s "https://oda.ft.dk/api/$url" > /dev/null
    done
}
```

This comprehensive diagnostic commands reference provides production teams with the tools needed to quickly identify, diagnose, and resolve issues with the Danish Parliamentary OData API. All commands have been tested against the live API and include expected outputs for validation.