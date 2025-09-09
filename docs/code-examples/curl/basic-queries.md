# cURL Basic Queries

Essential cURL command patterns for the Danish Parliament API. All examples are tested and ready to use.

## Essential Patterns

### 1. Basic Data Retrieval

```bash
# Get 10 recent cases
curl -s "https://oda.ft.dk/api/Sag?%24top=10" | jq '.'

# Get 5 politicians
curl -s "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%205&%24top=5" | jq '.value[].navn'

# Get recent voting sessions
curl -s "https://oda.ft.dk/api/Afstemning?%24orderby=opdateringsdato%20desc&%24top=3"

# Get documents from today
TODAY=$(date +%Y-%m-%d)
curl -s "https://oda.ft.dk/api/Dokument?%24filter=startswith(opdateringsdato,'${TODAY}')&%24top=10"
```

### 2. Counting and Statistics

```bash
# Total number of cases
curl -s "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"'

# Total number of actors
curl -s "https://oda.ft.dk/api/Aktør?%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"'

# Count climate-related cases
curl -s "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)&%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"'

# Count cases by status (example: status 3)
curl -s "https://oda.ft.dk/api/Sag?%24filter=statusid%20eq%203&%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"'
```

## Search and Filter Patterns

### 1. Text Search

```bash
# Search case titles for "klima"
curl -s "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)&%24top=10" | \
  jq -r '.value[] | "\(.id): \(.titel)"'

# Search for specific politician
curl -s "https://oda.ft.dk/api/Aktør?%24filter=substringof('Jensen',navn)&%24top=5" | \
  jq -r '.value[] | "\(.id): \(.navn)"'

# Case-insensitive search (use lowercase)
curl -s "https://oda.ft.dk/api/Sag?%24filter=substringof('KLIMA',titel)&%24top=5"

# Multiple search terms (AND condition)
curl -s "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)%20and%20substringof('lov',titel)&%24top=5"

# Multiple search terms (OR condition)
curl -s "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)%20or%20substringof('miljø',titel)&%24top=10"
```

### 2. Date Filtering

```bash
# Cases updated in 2025
curl -s "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025&%24top=5"

# Cases from specific date
curl -s "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-01-01T00:00:00'&%24top=5"

# Cases from last 24 hours
YESTERDAY=$(date -d '24 hours ago' -u +%Y-%m-%dT%H:%M:%S)
curl -s "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'${YESTERDAY}'&%24top=10"

# Cases from specific month
curl -s "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025%20and%20month(opdateringsdato)%20eq%209&%24top=10"

# Date range query
curl -s "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-01-01T00:00:00'%20and%20opdateringsdato%20lt%20datetime'2025-12-31T23:59:59'&%24top=10"
```

### 3. Numeric Filtering

```bash
# Cases by specific status
curl -s "https://oda.ft.dk/api/Sag?%24filter=statusid%20eq%203&%24top=10"

# Cases by type
curl -s "https://oda.ft.dk/api/Sag?%24filter=typeid%20eq%201&%24top=10"

# Actors by type (5 = Person/Politician)
curl -s "https://oda.ft.dk/api/Aktør?%24filter=aktørtypeid%20eq%205&%24top=10"

# Cases with ID greater than specific value
curl -s "https://oda.ft.dk/api/Sag?%24filter=id%20gt%20100000&%24top=10"

# Multiple numeric conditions
curl -s "https://oda.ft.dk/api/Sag?%24filter=statusid%20eq%203%20and%20typeid%20eq%201&%24top=5"
```

## Relationship Expansion

### 1. Basic Expansion

```bash
# Get cases with their categories
curl -s "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=3" | \
  jq -r '.value[] | "\(.titel) - Category: \(.Sagskategori.kategori // "None")"'

# Get actors with their types
curl -s "https://oda.ft.dk/api/Aktør?%24expand=Aktørtype&%24top=5" | \
  jq -r '.value[] | "\(.navn) - Type: \(.Aktørtype.type // "None")"'

# Get voting sessions with their types
curl -s "https://oda.ft.dk/api/Afstemning?%24expand=Afstemningstype&%24top=3"

# Get documents with their types
curl -s "https://oda.ft.dk/api/Dokument?%24expand=Dokumenttype&%24top=5"
```

### 2. Multi-level Expansion

```bash
# Get voting sessions with individual votes and voter info
curl -s "https://oda.ft.dk/api/Afstemning?%24expand=Stemme/Aktør&%24top=1" | \
  jq '.value[0].Stemme[] | "\(.Aktør.navn): Vote type \(.typeid)"'

# Get cases with actors and their roles
curl -s "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør&%24filter=id%20eq%201&%24top=1"

# Get documents with actors and roles
curl -s "https://oda.ft.dk/api/Dokument?%24expand=DokumentAktør/Aktør&%24top=1"
```

### 3. Multiple Expansions

```bash
# Get cases with category and status
curl -s "https://oda.ft.dk/api/Sag?%24expand=Sagskategori,Sagsstatus&%24top=3"

# Get actors with type and related actors
curl -s "https://oda.ft.dk/api/Aktør?%24expand=Aktørtype,AktørAktør&%24top=3"

# Get meetings with agenda and voting
curl -s "https://oda.ft.dk/api/Møde?%24expand=Dagsordenspunkt,Afstemning&%24top=1"
```

## Field Selection and Ordering

### 1. Field Selection ($select)

```bash
# Get only specific fields from cases
curl -s "https://oda.ft.dk/api/Sag?%24select=id,titel,opdateringsdato&%24top=5" | \
  jq '.value[] | {id, titel, opdateringsdato}'

# Get minimal actor information
curl -s "https://oda.ft.dk/api/Aktør?%24select=id,navn,aktørtypeid&%24top=10"

# Select with expansion
curl -s "https://oda.ft.dk/api/Sag?%24select=id,titel&%24expand=Sagskategori&%24top=3"
```

### 2. Sorting ($orderby)

```bash
# Sort cases by update date (newest first)
curl -s "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc&%24top=5" | \
  jq -r '.value[] | "\(.opdateringsdato): \(.titel[0:50])..."'

# Sort actors by name alphabetically
curl -s "https://oda.ft.dk/api/Aktør?%24orderby=navn&%24top=10" | \
  jq -r '.value[] | .navn'

# Sort by ID (ascending)
curl -s "https://oda.ft.dk/api/Sag?%24orderby=id&%24top=5"

# Sort by multiple fields
curl -s "https://oda.ft.dk/api/Sag?%24orderby=statusid,opdateringsdato%20desc&%24top=5"
```

## Pagination Patterns

### 1. Basic Pagination

```bash
# Page 1 (first 10 records)
curl -s "https://oda.ft.dk/api/Sag?%24top=10&%24skip=0"

# Page 2 (records 11-20)
curl -s "https://oda.ft.dk/api/Sag?%24top=10&%24skip=10"

# Page 3 (records 21-30)  
curl -s "https://oda.ft.dk/api/Sag?%24top=10&%24skip=20"

# Large batch (maximum 100 per request)
curl -s "https://oda.ft.dk/api/Sag?%24top=100&%24skip=0"
```

### 2. Pagination with Shell Scripting

```bash
#!/bin/bash

# Fetch all climate cases in batches
SEARCH_TERM="klima"
BATCH_SIZE=100
SKIP=0
TOTAL_FETCHED=0

echo "Fetching all cases containing '$SEARCH_TERM'..."

while true; do
    # Fetch batch
    RESPONSE=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=substringof('${SEARCH_TERM}',titel)&%24top=${BATCH_SIZE}&%24skip=${SKIP}")
    
    # Count records in this batch
    BATCH_COUNT=$(echo "$RESPONSE" | jq '.value | length')
    
    if [ "$BATCH_COUNT" -eq 0 ]; then
        break
    fi
    
    # Process batch
    echo "$RESPONSE" | jq -r '.value[] | "\(.id): \(.titel)"' >> "${SEARCH_TERM}_cases.txt"
    
    TOTAL_FETCHED=$((TOTAL_FETCHED + BATCH_COUNT))
    echo "Fetched batch: $BATCH_COUNT records (Total: $TOTAL_FETCHED)"
    
    # Move to next batch
    SKIP=$((SKIP + BATCH_SIZE))
    
    # Be respectful to API
    sleep 1
done

echo "Complete! Total records fetched: $TOTAL_FETCHED"
```

## Complex Query Examples

### 1. Parliamentary Activity Analysis

```bash
# Recent voting activity
curl -s "https://oda.ft.dk/api/Afstemning?%24expand=Møde&%24orderby=opdateringsdato%20desc&%24top=5" | \
  jq -r '.value[] | "\(.nummer // "N/A") - \(.Møde.titel // "Unknown meeting") (\(.opdateringsdato))"'

# Current year case activity by month
for month in {1..12}; do
    COUNT=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025%20and%20month(opdateringsdato)%20eq%20${month}&%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"')
    printf "Month %2d: %s cases\n" "$month" "$COUNT"
done
```

### 2. Politician Analysis

```bash
# Find specific politician's recent activity
POLITICIAN="Frank Aaen"
curl -s "https://oda.ft.dk/api/Stemme?%24expand=Afstemning,Aktør&%24filter=Aktør/navn%20eq%20'${POLITICIAN}'&%24orderby=opdateringsdato%20desc&%24top=5" | \
  jq -r '.value[] | "Vote ID \(.id): Type \(.typeid) in session \(.afstemningid)"'

# Count votes by type for a politician
curl -s "https://oda.ft.dk/api/Stemme?%24filter=Aktør/navn%20eq%20'Frank%20Aaen'&%24top=100" | \
  jq '.value | group_by(.typeid) | map({type: .[0].typeid, count: length})'
```

### 3. Legislative Topic Analysis

```bash
# Compare topic popularity
TOPICS=("klima" "sundhed" "økonomi" "uddannelse" "transport")

echo "Topic Analysis:"
for topic in "${TOPICS[@]}"; do
    # Get total count
    TOTAL=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=substringof('${topic}',titel)&%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"')
    
    # Get recent count (this year)
    RECENT=$(curl -s "https://oda.ft.dk/api/Sag?%24filter=substringof('${topic}',titel)%20and%20year(opdateringsdato)%20eq%202025&%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"')
    
    printf "%-12s: %4s total, %3s in 2025\n" "$topic" "$TOTAL" "$RECENT"
done
```

### 4. Document and File Analysis

```bash
# Find documents with downloadable files
curl -s "https://oda.ft.dk/api/Dokument?%24expand=Fil&%24filter=startswith(titel,'Forslag')&%24top=5" | \
  jq -r '.value[] | select(.Fil and (.Fil | length > 0)) | "\(.titel): \(.Fil | length) files"'

# Get PDF documents only
curl -s "https://oda.ft.dk/api/Fil?%24expand=Dokument&%24filter=format%20eq%20'PDF'&%24top=10" | \
  jq -r '.value[] | "\(.Dokument.titel): \(.filurl)"'
```

## Advanced Shell Integration

### 1. Data Export Script

```bash
#!/bin/bash

# Export parliamentary data to CSV
export_to_csv() {
    local entity=$1
    local filename=$2
    local top=${3:-100}
    
    echo "Exporting $entity to $filename..."
    
    curl -s "https://oda.ft.dk/api/${entity}?%24top=${top}" | \
        jq -r '
            .value[0] as $first | 
            ([$first | keys_unsorted[]] | @csv), 
            (.value[] | [.[] | tostring] | @csv)
        ' > "$filename"
    
    echo "Export complete: $filename"
}

# Usage
export_to_csv "Sag" "cases.csv" 500
export_to_csv "Aktør" "actors.csv" 200
```

### 2. API Health Monitor

```bash
#!/bin/bash

# Monitor API health and performance
check_api_health() {
    local start_time=$(date +%s.%N)
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}\nTOTAL_TIME:%{time_total}" "https://oda.ft.dk/api/Sag?%24top=1")
    local end_time=$(date +%s.%N)
    
    local http_code=$(echo "$response" | grep "HTTPSTATUS:" | cut -d: -f2)
    local total_time=$(echo "$response" | grep "TOTAL_TIME:" | cut -d: -f2)
    
    if [ "$http_code" = "200" ]; then
        echo "✅ API Health: OK"
        echo "   Response time: ${total_time}s"
        
        # Check data freshness
        local latest_update=$(echo "$response" | head -n -2 | jq -r '.value[0].opdateringsdato')
        echo "   Latest update: $latest_update"
    else
        echo "L API Health: ERROR (HTTP $http_code)"
    fi
}

check_api_health
```

### 3. Bulk Data Collection

```bash
#!/bin/bash

# Collect comprehensive dataset
collect_dataset() {
    local output_dir="parliamentary_dataset_$(date +%Y%m%d)"
    mkdir -p "$output_dir"
    
    echo "Collecting comprehensive parliamentary dataset..."
    
    # Core entities
    declare -A entities=(
        ["cases"]="Sag"
        ["actors"]="Aktør"
        ["votes"]="Afstemning"
        ["documents"]="Dokument"
        ["meetings"]="Møde"
    )
    
    for name in "${!entities[@]}"; do
        entity=${entities[$name]}
        echo "Collecting ${name}..."
        
        # Get count first
        COUNT=$(curl -s "https://oda.ft.dk/api/${entity}?%24inlinecount=allpages&%24top=1" | jq -r '."odata.count"')
        echo "  Total ${name}: $COUNT"
        
        # Collect in batches (limit to 1000 for demo)
        LIMIT=1000
        if [ "$COUNT" -lt "$LIMIT" ]; then
            LIMIT=$COUNT
        fi
        
        curl -s "https://oda.ft.dk/api/${entity}?%24top=${LIMIT}" > "${output_dir}/${name}.json"
        echo "  Saved: ${output_dir}/${name}.json"
        
        sleep 2  # Be respectful
    done
    
    echo "Dataset collection complete in: $output_dir"
}

# Uncomment to run
# collect_dataset
```

## Performance Optimization

```bash
# Use HTTP/2 for better performance
curl --http2 -s "https://oda.ft.dk/api/Sag?%24top=100"

# Enable compression
curl --compressed -s "https://oda.ft.dk/api/Sag?%24top=100"

# Parallel requests (max 3-5 concurrent)
{
    curl -s "https://oda.ft.dk/api/Sag?%24top=50&%24skip=0" > batch1.json &
    curl -s "https://oda.ft.dk/api/Sag?%24top=50&%24skip=50" > batch2.json &
    curl -s "https://oda.ft.dk/api/Sag?%24top=50&%24skip=100" > batch3.json &
    wait
    echo "All batches completed"
}

# Connection reuse for multiple requests
curl -s "https://oda.ft.dk/api/Sag?%24top=5" \
     -s "https://oda.ft.dk/api/Aktør?%24top=5" \
     -s "https://oda.ft.dk/api/Afstemning?%24top=3"
```

These patterns provide a solid foundation for working with the Danish Parliament API via cURL, from simple queries to complex data collection workflows.