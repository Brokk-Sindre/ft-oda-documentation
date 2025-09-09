# cURL Examples

Comprehensive command-line examples for accessing the Danish Parliament API using cURL. Perfect for testing, scripting, and command-line tools.

## Overview

The Danish Parliament API is ideal for cURL usage because:
- **No authentication required** - Direct access without API keys
- **CORS enabled** - Works from any environment
- **Standard HTTP/JSON** - Simple request/response patterns
- **Rich OData support** - Powerful query capabilities

## Quick Start

```bash
# Basic API test - get 5 recent cases
curl "https://oda.ft.dk/api/Sag?%24top=5"

# Pretty print JSON (if you have jq)
curl -s "https://oda.ft.dk/api/Sag?%24top=5" | jq '.'

# Get total count of cases
curl -s "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1" | jq '."odata.count"'
```

## Critical: URL Encoding

**The #1 mistake developers make**: Always use `%24` instead of `$` in URLs.

```bash
# L WRONG - This will not work
curl "https://oda.ft.dk/api/Sag?$top=5"

#  CORRECT - Always encode $ as %24
curl "https://oda.ft.dk/api/Sag?%24top=5"

# Or use proper shell escaping (bash/zsh)
curl "https://oda.ft.dk/api/Sag?\$top=5"
```

## Quick Reference

| Purpose | Entity | Example |
|---------|--------|---------|
| Cases/Bills | `Sag` | `curl "https://oda.ft.dk/api/Sag?%24top=10"` |
| Politicians | `Aktør` | `curl "https://oda.ft.dk/api/Aktør?%24top=10"` |
| Votes | `Afstemning` | `curl "https://oda.ft.dk/api/Afstemning?%24top=5"` |
| Individual Votes | `Stemme` | `curl "https://oda.ft.dk/api/Stemme?%24top=5"` |
| Documents | `Dokument` | `curl "https://oda.ft.dk/api/Dokument?%24top=5"` |
| Meetings | `Møde` | `curl "https://oda.ft.dk/api/Møde?%24top=5"` |

## Examples by Category

1. **[Basic Queries](basic-queries.md)** - Essential cURL patterns
2. **[Testing Commands](testing.md)** - API health checks and diagnostics

## Common Patterns

### Search and Filter
```bash
# Search for climate legislation
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',%20titel)"

# Cases updated in 2025
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025"

# Recent activity (last 24 hours)
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-09-08T00:00:00'"
```

### Pagination
```bash
# First page (records 1-100)
curl "https://oda.ft.dk/api/Sag?%24top=100&%24skip=0"

# Second page (records 101-200)
curl "https://oda.ft.dk/api/Sag?%24top=100&%24skip=100"

# Get total count for pagination
curl "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1" | jq '."odata.count"'
```

### Relationships
```bash
# Get cases with categories
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=5"

# Get voting with individual votes
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme&%24top=1"

# Deep expansion (2 levels)
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme/Aktør&%24top=1"
```

## Useful cURL Options

```bash
# Silent mode (no progress bar)
curl -s "https://oda.ft.dk/api/Sag?%24top=1"

# Include HTTP headers in output
curl -i "https://oda.ft.dk/api/Sag?%24top=1"

# Show only HTTP status code
curl -s -w "%{http_code}" -o /dev/null "https://oda.ft.dk/api/Sag"

# Timeout after 30 seconds
curl --max-time 30 "https://oda.ft.dk/api/Sag?%24top=100"

# Follow redirects
curl -L "https://oda.ft.dk/api/Sag?%24top=1"

# Save to file
curl -o cases.json "https://oda.ft.dk/api/Sag?%24top=100"
```

## JSON Processing with jq

```bash
# Extract just the titles
curl -s "https://oda.ft.dk/api/Sag?%24top=5" | jq '.value[].titel'

# Count records returned
curl -s "https://oda.ft.dk/api/Sag?%24top=10" | jq '.value | length'

# Get specific fields
curl -s "https://oda.ft.dk/api/Sag?%24top=3" | jq '.value[] | {id, titel, opdateringsdato}'

# Filter by field value
curl -s "https://oda.ft.dk/api/Sag?%24top=20" | jq '.value[] | select(.statusid == 3)'

# Sort by update date
curl -s "https://oda.ft.dk/api/Sag?%24top=10" | jq '.value | sort_by(.opdateringsdato) | reverse'
```

## Shell Scripting Examples

### Simple monitoring script
```bash
#!/bin/bash

# Monitor recent parliamentary activity
echo "Recent Parliamentary Activity (Last 4 hours):"

CUTOFF=$(date -d '4 hours ago' -u +%Y-%m-%dT%H:%M:%S)
RECENT=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'${CUTOFF}'&%24top=10")

echo "$RECENT" | jq -r '.value[] | "\(.id): \(.titel[0:60])... (Updated: \(.opdateringsdato))"'
```

### Batch data collection
```bash
#!/bin/bash

# Collect climate legislation data
TOPICS=("klima" "miljø" "energi" "bæredygtig")
OUTPUT_DIR="parliamentary_data"
mkdir -p "$OUTPUT_DIR"

for topic in "${TOPICS[@]}"; do
    echo "Collecting data for: $topic"
    
    curl -s "https://oda.ft.dk/api/Sag?%24filter=substringof('${topic}',%20titel)&%24top=100" \
        > "${OUTPUT_DIR}/${topic}_cases.json"
    
    # Count results
    COUNT=$(cat "${OUTPUT_DIR}/${topic}_cases.json" | jq '.value | length')
    echo "Found $COUNT cases for $topic"
    
    # Be respectful to the API
    sleep 1
done
```

## Error Handling

```bash
# Check for HTTP errors
response=$(curl -s -w "HTTPSTATUS:%{http_code}" "https://oda.ft.dk/api/InvalidEntity")
http_code=$(echo "$response" | grep -o "HTTPSTATUS:.*" | cut -d: -f2)

if [ "$http_code" -eq 200 ]; then
    echo "Success"
    echo "$response" | sed 's/HTTPSTATUS:.*$//'
else
    echo "HTTP Error: $http_code"
fi

# Retry on failure
max_attempts=3
attempt=1

while [ $attempt -le $max_attempts ]; do
    response=$(curl -s --max-time 30 "https://oda.ft.dk/api/Sag?%24top=1")
    
    if [ $? -eq 0 ]; then
        echo "Success on attempt $attempt"
        break
    else
        echo "Attempt $attempt failed, retrying..."
        sleep $((attempt * 2))  # Exponential backoff
        ((attempt++))
    fi
done
```

## Advanced Use Cases

### Parliamentary Activity Dashboard
```bash
#!/bin/bash

echo "=== Danish Parliament Activity Dashboard ==="
echo

# Total statistics
echo "=Ê Overall Statistics:"
TOTAL_CASES=$(curl -s "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"')
TOTAL_ACTORS=$(curl -s "https://oda.ft.dk/api/Aktør?%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"')
echo "  Total Cases: ${TOTAL_CASES}"
echo "  Total Actors: ${TOTAL_ACTORS}"

# Recent activity
echo
echo "¡ Recent Activity (Last 24 hours):"
YESTERDAY=$(date -d '24 hours ago' -u +%Y-%m-%dT%H:%M:%S)
RECENT=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'${YESTERDAY}'&%24top=5&%24orderby=opdateringsdato%20desc")

echo "$RECENT" | jq -r '.value[] | "  " \(.titel[0:50])... (ID: \(.id))"'

# Topic analysis
echo
echo "<÷ Topic Analysis:"
declare -A topics=(
    ["klima"]="Climate"
    ["sundhed"]="Health" 
    ["økonomi"]="Economy"
    ["uddannelse"]="Education"
)

for key in "${!topics[@]}"; do
    COUNT=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=substringof('${key}',%20titel)&%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"')
    printf "  %-12s: %s cases\n" "${topics[$key]}" "$COUNT"
done
```

## Performance Tips

```bash
# Use compression for large responses
curl --compressed "https://oda.ft.dk/api/Sag?%24top=100"

# Parallel requests (be respectful - max 3-5 concurrent)
{
    curl -s "https://oda.ft.dk/api/Sag?%24top=50&%24skip=0" > page1.json &
    curl -s "https://oda.ft.dk/api/Sag?%24top=50&%24skip=50" > page2.json &
    curl -s "https://oda.ft.dk/api/Sag?%24top=50&%24skip=100" > page3.json &
    wait
}

# Use HTTP/2 for better performance
curl --http2 "https://oda.ft.dk/api/Sag?%24top=10"

# Connection reuse for multiple requests
{
    echo "url = \"https://oda.ft.dk/api/Sag?%24top=10\""
    echo "url = \"https://oda.ft.dk/api/Aktør?%24top=10\""
    echo "url = \"https://oda.ft.dk/api/Afstemning?%24top=5\""
} | curl --config -
```

## Security Notes

```bash
# Always use HTTPS (the API enforces this)
curl "https://oda.ft.dk/api/Sag?%24top=1"  #  Secure

# Verify SSL certificate
curl --cacert /etc/ssl/certs/ca-certificates.crt "https://oda.ft.dk/api/Sag?%24top=1"

# Check TLS version
curl -v "https://oda.ft.dk/api/Sag?%24top=1" 2>&1 | grep "TLS"
```

## Next Steps

1. **[Basic Queries](basic-queries.md)** - Essential cURL patterns and examples
2. **[Testing Commands](testing.md)** - API health checks and diagnostics

cURL provides an excellent way to explore the Danish Parliament API, test queries, and build command-line tools for parliamentary data analysis.