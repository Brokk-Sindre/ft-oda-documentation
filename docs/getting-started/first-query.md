# Your First Query

Let's walk through making your first successful API call to the Danish Parliament API step by step.

## Step 1: Open Your Terminal

Open a terminal or command prompt on your system.

## Step 2: Basic API Call

Start with the simplest possible query to get 5 recent cases:

```bash
curl "https://oda.ft.dk/api/Sag?%24top=5"
```

!!! success "Expected Result"
    You should see JSON data containing 5 parliamentary cases with fields like `id`, `titel`, `offentlighedskode`, and `opdateringsdato`.

## Step 3: Understanding the Response

The response structure looks like this:

```json
{
  "odata.metadata": "https://oda.ft.dk/api/$metadata#Sag",
  "value": [
    {
      "id": 102903,
      "titel": "Kommissionsmeddelelse om den europæiske grønne pagt...",
      "offentlighedskode": "O",
      "opdateringsdato": "2025-09-09T17:49:11.87",
      "periodeid": 32,
      "statsbudgetsag": true,
      "statusid": 11,
      "typeid": 5,
      "kategoriid": 19,
      "numero": null,
      "lovnummer": null,
      "lovnummerdato": null,
      "retsinformationsurl": null,
      "fremsatundersagid": null,
      "deltundersagid": null
    }
  ]
}
```

Key fields explained:
- **id**: Unique identifier for the case
- **titel**: Title of the parliamentary case
- **offentlighedskode**: Publicity code ("O" = Open/Public)
- **opdateringsdato**: Last update timestamp
- **periodeid**: Parliamentary period identifier

## Step 4: Format the Response (Optional)

For better readability, pipe the response through `jq` if you have it installed:

```bash
curl "https://oda.ft.dk/api/Sag?%24top=5" | jq '.'
```

Or just get the titles:

```bash
curl "https://oda.ft.dk/api/Sag?%24top=5" | jq '.value[].titel'
```

## Step 5: Try a Filter Query

Let's search for cases containing the word "budget":

```bash
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('budget',titel)&%24top=3"
```

## Step 6: Get More Specific Data

Let's only retrieve specific fields to improve performance:

```bash
curl "https://oda.ft.dk/api/Sag?%24select=id,titel,opdateringsdato&%24top=5"
```

## Step 7: Explore Other Entities

### Get Politicians and Actors
```bash
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24top=5"
```

### Get Recent Voting Sessions
```bash
curl "https://oda.ft.dk/api/Afstemning?%24top=3"
```

### Get Documents
```bash
curl "https://oda.ft.dk/api/Dokument?%24top=3"
```

## Step 8: Add Relationships

Include related data using `$expand`:

```bash
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=3"
```

This returns each case with its category information nested inside.

## Step 9: Verify Data Freshness

Check how recent the data is:

```bash
curl "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc&%24top=1&%24select=titel,opdateringsdato"
```

You should see very recent timestamps, often within hours of the current time.

## Step 10: Count Total Records

Get the total number of cases in the system:

```bash
curl "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1" | jq '."odata.count"'
```

This will return a number like "96538", showing the massive size of the dataset.

## Troubleshooting

### If You Get an Error

**HTTP 400 Bad Request**
- Check that you're using `%24` instead of `$`
- Verify spaces are encoded as `%20`

**"command not found" in shell**
- You're missing the `%24` encoding
- Shell is interpreting `$` as a variable

**Empty response**
- API might be temporarily unavailable
- Check your internet connection
- Verify the URL is correct

### Success Indicators

✅ **HTTP 200 status code**
✅ **JSON response with "odata.metadata" field**
✅ **"value" array containing data**
✅ **Recent "opdateringsdato" timestamps**

## Next Steps

Now that you've made your first successful API call:

1. **[URL Encoding](url-encoding.md)** - Master proper URL encoding
2. **[Common Mistakes](common-mistakes.md)** - Avoid these pitfalls
3. **[API Reference](../api-reference/)** - Explore all 50 entities

## Quick Experiments

Try these queries to explore the API:

### Find Climate Legislation
```bash
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)&%24top=5"
```

### Get Latest Updates
```bash
curl "https://oda.ft.dk/api/Sag?%24filter=year(opdateringsdato)%20eq%202025&%24orderby=opdateringsdato%20desc&%24top=5"
```

### Explore Voting Data
```bash
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme&%24top=1"
```

Congratulations! You've successfully made your first API calls to the Danish Parliament API. The system contains 74+ years of parliamentary data waiting to be explored.