# URL Encoding - Critical Knowledge

!!! danger "Most Common Mistake"
    URL encoding is the **#1 source of errors** when using the Danish Parliament API. Failure to properly encode URLs will result in HTTP 400 errors or unexpected results.

## The Golden Rule

**Always use `%24` instead of `$` in OData query parameters.**

| L Wrong |  Correct | Result |
|----------|------------|--------|
| `?$top=5` | `?%24top=5` | Works |
| `?$filter=id eq 1` | `?%24filter=id%20eq%201` | Works |
| `?$expand=Aktør` | `?%24expand=Akt%C3%B8r` | Works |

## Why This Matters

OData uses the `$` character for system query options like `$top`, `$filter`, etc. However, `$` has special meaning in URLs and shells, so it must be URL encoded as `%24`.

## Complete Encoding Reference

### Basic Characters
```
Space         %20
$             %24
&             %26
=             %3D (usually handled automatically)
'             %27
(             %28
)             %29
```

### Danish Characters
```
ø             %C3%B8
å             %C3%A5
æ             %C3%A6
Ø             %C3%98
Å             %C3%85
Æ             %C3%86
```

## Real Examples

### Basic Queries

=== "Wrong"
    ```bash
    # This will fail
    curl "https://oda.ft.dk/api/Sag?$top=5"
    ```

=== "Correct"
    ```bash
    # This works
    curl "https://oda.ft.dk/api/Sag?%24top=5"
    ```

### Text Filtering

=== "Wrong"
    ```bash
    # This will fail
    curl "https://oda.ft.dk/api/Sag?$filter=substringof('minister', titel)"
    ```

=== "Correct"
    ```bash
    # This works
    curl "https://oda.ft.dk/api/Sag?%24filter=substringof('minister',titel)"
    ```

### Complex Queries

=== "Wrong"
    ```bash
    # Multiple issues
    curl "https://oda.ft.dk/api/Sag?$filter=year(opdateringsdato) eq 2025&$top=10&$orderby=titel"
    ```

=== "Correct"
    ```bash
    # Properly encoded
    curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025&%24top=10&%24orderby=titel"
    ```

### Danish Text Searches

=== "Wrong"
    ```bash
    # Danish characters not encoded
    curl "https://oda.ft.dk/api/Aktør?$filter=substringof('ø', navn)"
    ```

=== "Correct"
    ```bash
    # Danish characters properly encoded
    curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=substringof('%C3%B8',navn)"
    ```

## Programming Language Examples

### Python
```python
import urllib.parse

# Proper URL encoding
query = "$filter=substringof('klima', titel)&$top=5"
encoded_query = urllib.parse.quote(query, safe='&=')
url = f"https://oda.ft.dk/api/Sag?{encoded_query}"

# Or use requests which handles encoding
import requests
params = {
    '$filter': "substringof('klima', titel)",
    '$top': 5
}
response = requests.get('https://oda.ft.dk/api/Sag', params=params)
```

### JavaScript
```javascript
// Proper URL encoding
const params = new URLSearchParams({
    '$filter': "substringof('klima', titel)",
    '$top': 5
});
const url = `https://oda.ft.dk/api/Sag?${params}`;

// Or use encodeURIComponent for manual encoding
const filter = encodeURIComponent("substringof('klima', titel)");
const url2 = `https://oda.ft.dk/api/Sag?%24filter=${filter}&%24top=5`;
```

### curl in Shell Scripts
```bash
#!/bin/bash
# Proper escaping in shell scripts
FILTER="year(opdateringsdato) eq 2025"
curl "https://oda.ft.dk/api/Sag?%24filter=${FILTER// /%20}&%24top=10"
```

## Common Encoding Mistakes

### 1. Missing Dollar Sign Encoding
```bash
# L Will cause HTTP 400
curl "https://oda.ft.dk/api/Sag?$top=5"

#  Correct
curl "https://oda.ft.dk/api/Sag?%24top=5"
```

### 2. Missing Space Encoding
```bash
# L Malformed query
curl "https://oda.ft.dk/api/Sag?%24filter=id eq 1"

#  Spaces encoded
curl "https://oda.ft.dk/api/Sag?%24filter=id%20eq%201"
```

### 3. Danish Characters
```bash
# L May cause issues
curl "https://oda.ft.dk/api/Aktør?%24filter=substringof('ø',navn)"

#  Properly encoded
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=substringof('%C3%B8',navn)"
```

### 4. Complex Boolean Logic
```bash
# L Parentheses not encoded
curl "https://oda.ft.dk/api/Sag?%24filter=(typeid eq 3) and (year(opdateringsdato) gt 2020)"

#  Complete encoding
curl "https://oda.ft.dk/api/Sag?%24filter=%28typeid%20eq%203%29%20and%20%28year%28opdateringsdato%29%20gt%202020%29"
```

## Testing Your Encoding

Use these test queries to verify your encoding works:

### Test 1: Basic Query
```bash
curl "https://oda.ft.dk/api/Sag?%24top=1" | jq '.value | length'
# Expected: 1
```

### Test 2: Text Filter
```bash
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('forslag',titel)&%24top=1" | jq '.value | length'
# Expected: 1 (if results exist)
```

### Test 3: Date Filter
```bash
curl "https://oda.ft.dk/api/Sag?%24filter=year%28opdateringsdato%29%20eq%202025&%24top=1" | jq '.value | length'
# Expected: 1 (if results exist)
```

## Error Symptoms

If your URLs aren't properly encoded, you'll see:

### HTTP 400 Bad Request
```json
{
  "error": {
    "code": "400",
    "message": "Bad Request"
  }
}
```

### Empty HTML Response
```html
<!DOCTYPE html>
<html>
<head><title>400 Bad Request</title></head>
<body>
<h1>400 Bad Request</h1>
</body>
</html>
```

### Shell Errors
```bash
bash: $top: command not found
```

## Quick Reference Table

| Character/Sequence | Encoding | Example Usage |
|-------------------|----------|---------------|
| `$top=5` | `%24top=5` | Pagination |
| `$filter=` | `%24filter=` | Filtering |
| `id eq 1` | `id%20eq%201` | Filter condition |
| `substringof('text', field)` | `substringof('text',field)` | Text search |
| `year(date) eq 2025` | `year%28date%29%20eq%202025` | Date functions |
| `(condition1) and (condition2)` | `%28condition1%29%20and%20%28condition2%29` | Boolean logic |

## Tools for URL Encoding

### Online Tools
- [URL Encoder/Decoder](https://www.urlencoder.org/)
- [W3Schools URL Encoder](https://www.w3schools.com/tags/ref_urlencode.asp)

### Command Line Tools
```bash
# Python one-liner
python3 -c "import urllib.parse; print(urllib.parse.quote(input()))"

# Node.js one-liner
node -e "console.log(encodeURIComponent(process.argv[1]))" "your text here"
```

Remember: **When in doubt, encode everything!** It's better to over-encode than under-encode with this API.