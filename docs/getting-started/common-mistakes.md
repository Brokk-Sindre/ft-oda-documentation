# Common Mistakes to Avoid

Learn from the most frequent errors developers make when using the Danish Parliament API, so you can avoid them entirely.

## 1. URL Encoding Issues (Most Critical)

### L The #1 Mistake: Using $ Instead of %24

This is by far the most common error:

```bash
# L WRONG - Will cause HTTP 400 or shell errors
curl "https://oda.ft.dk/api/Sag?$top=5"

#  CORRECT - Always use %24
curl "https://oda.ft.dk/api/Sag?%24top=5"
```

**Why this happens:**
- `$` has special meaning in URLs and shells
- Must be URL encoded as `%24`
- Shell interprets `$top` as a variable name

### L Missing Space Encoding

```bash
# L WRONG - Spaces break the query
curl "https://oda.ft.dk/api/Sag?%24filter=id eq 1"

#  CORRECT - Spaces become %20
curl "https://oda.ft.dk/api/Sag?%24filter=id%20eq%201"
```

## 2. Pagination Misunderstandings

### L Assuming 1000 Record Limit

```bash
# L WRONG - API now limits to 100 records max
curl "https://oda.ft.dk/api/Sag?%24top=1000"

#  CORRECT - Use maximum of 100
curl "https://oda.ft.dk/api/Sag?%24top=100"
```

**Updated Finding:** The API now has a hard limit of 100 records per request, not 1000 as previously documented.

### L Not Using Pagination for Large Datasets

```python
# L WRONG - Trying to get all data at once
response = requests.get("https://oda.ft.dk/api/Sag?%24top=100000")

#  CORRECT - Paginate through results
def get_all_cases():
    skip = 0
    all_cases = []
    while True:
        response = requests.get(f"https://oda.ft.dk/api/Sag?%24skip={skip}&%24top=100")
        data = response.json()
        if not data['value']:
            break
        all_cases.extend(data['value'])
        skip += 100
    return all_cases
```

## 3. Silent Filter Failures

### L Invalid Field Names Return All Data

This is a particularly dangerous mistake:

```bash
# L WRONG - Typo in field name, but NO ERROR returned
curl "https://oda.ft.dk/api/Sag?%24filter=tittel%20eq%20'test'"  # 'tittel' should be 'titel'

# Result: Returns ALL records instead of filtered results!
```

**Critical Problem:** Invalid filter field names don't produce errors. They silently return all data, which can:
- Overwhelm your application
- Cause performance issues
- Lead to incorrect analysis

** Solution:** Always test filters with `%24top=1` first:

```bash
# Test your filter syntax first
curl "https://oda.ft.dk/api/Sag?%24filter=titel%20eq%20'test'&%24top=1"
```

## 4. Performance Mistakes

### L Requesting Everything When You Need Little

```bash
# L WRONG - Gets all fields for all expansions
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør&%24top=100"

#  CORRECT - Select only needed fields
curl "https://oda.ft.dk/api/Sag?%24select=titel,SagAktør/Aktør/navn&%24expand=SagAktør/Aktør&%24top=100"
```

### L Not Using Field Selection

```python
# L WRONG - Downloads unnecessary data
response = requests.get("https://oda.ft.dk/api/Sag?%24top=100")

#  CORRECT - Only get what you need
response = requests.get("https://oda.ft.dk/api/Sag?%24select=id,titel,opdateringsdato&%24top=100")
```

## 5. Date and Time Errors

### L Wrong Date Function Syntax

```bash
# L WRONG - Missing parentheses
curl "https://oda.ft.dk/api/Sag?%24filter=year opdateringsdato eq 2025"

#  CORRECT - Proper function syntax
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025"
```

### L Incorrect DateTime Format

```bash
# L WRONG - Missing 'datetime' wrapper
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20'2025-09-09'"

#  CORRECT - Proper datetime format
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-09-09T00:00:00'"
```

## 6. Danish Character Issues

### L Not Encoding Danish Characters

```bash
# L WRONG - Direct Danish characters may cause issues
curl "https://oda.ft.dk/api/Aktør?%24filter=substringof('ø',navn)"

#  CORRECT - Properly encoded
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=substringof('%C3%B8',navn)"
```

### L Wrong Entity Name Encoding

```bash
# L WRONG - Entity name not encoded
curl "https://oda.ft.dk/api/Aktør"  # May work but inconsistent

#  CORRECT - Consistently encoded
curl "https://oda.ft.dk/api/Akt%C3%B8r"
```

## 7. Boolean Logic Errors

### L Wrong Operator Precedence

```bash
# L WRONG - Ambiguous logic
curl "https://oda.ft.dk/api/Sag?%24filter=typeid%20eq%201%20or%20typeid%20eq%202%20and%20statusid%20eq%203"

#  CORRECT - Clear parentheses
curl "https://oda.ft.dk/api/Sag?%24filter=%28typeid%20eq%201%20or%20typeid%20eq%202%29%20and%20statusid%20eq%203"
```

## 8. Error Handling Mistakes

### L Not Checking HTTP Status Codes

```python
# L WRONG - Assumes request always succeeds
response = requests.get(url)
data = response.json()  # May crash if HTTP error

#  CORRECT - Proper error handling
response = requests.get(url)
response.raise_for_status()  # Raises exception for HTTP errors
data = response.json()
```

### L Not Handling Empty Results

```python
# L WRONG - Assumes data always exists
first_case = response.json()['value'][0]  # May crash if empty

#  CORRECT - Check for empty results
data = response.json()
if data['value']:
    first_case = data['value'][0]
else:
    print("No results found")
```

## 9. Write Operation Mistakes

### L Attempting Write Operations

```bash
# L WRONG - API is read-only, will return HTTP 501
curl -X POST "https://oda.ft.dk/api/Sag" -d '{"titel":"test"}'

#  CORRECT - Only use GET requests
curl "https://oda.ft.dk/api/Sag?%24top=5"
```

**Important:** The API is completely read-only. All POST, PUT, PATCH, DELETE operations return HTTP 501.

## 10. Relationship Expansion Mistakes

### L Too Many Levels of Expansion

```bash
# L WRONG - May cause performance issues or timeouts
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør/AktørAktør/Aktør"

#  CORRECT - Limit expansion depth
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør&%24top=10"
```

## 11. Caching and Data Freshness Mistakes

### L Over-Caching Dynamic Data

```python
# L WRONG - Caching for too long
@cache(timeout=3600*24)  # 24 hours is too long
def get_recent_cases():
    return api.get("Sag?%24filter=year(opdateringsdato)%20eq%202025")

#  CORRECT - Shorter cache for fresh data
@cache(timeout=300)  # 5 minutes for recent data
def get_recent_cases():
    return api.get("Sag?%24filter=year(opdateringsdato)%20eq%202025")
```

## 12. Data Type Assumptions

### L Assuming Fields Are Always Present

```python
# L WRONG - Field may be null/missing
title = case['titel'].lower()  # May crash if titel is null

#  CORRECT - Handle null values
title = (case.get('titel') or '').lower()
```

## Quick Debugging Checklist

When something doesn't work:

1. **Check URL encoding** - Are you using `%24` instead of `$`?
2. **Test with %24top=1** - Does a simple query work?
3. **Verify field names** - Are you using the correct Danish field names?
4. **Check HTTP status** - Is the server returning 200 OK?
5. **Test incrementally** - Start simple, add complexity gradually
6. **Use browser dev tools** - Check the actual HTTP requests being sent

## Testing Strategy

Always test your queries incrementally:

```bash
# Step 1: Basic query
curl "https://oda.ft.dk/api/Sag?%24top=1"

# Step 2: Add filter
curl "https://oda.ft.dk/api/Sag?%24filter=id%20eq%201&%24top=1"

# Step 3: Add expansion
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24filter=id%20eq%201&%24top=1"

# Step 4: Add selection
curl "https://oda.ft.dk/api/Sag?%24select=titel,Sagskategori/kategori&%24expand=Sagskategori&%24filter=id%20eq%201&%24top=1"
```

Remember: The Danish Parliament API is very forgiving in some ways (no authentication) but strict in others (URL encoding). Taking time to understand these common mistakes will save you hours of debugging!