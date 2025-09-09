# Security Overview

The Danish Parliament API (oda.ft.dk) implements a transparent, open access model that prioritizes democratic transparency while maintaining robust technical security. This section covers the security architecture, best practices, and considerations for production deployments.

## Key Security Characteristics

### Open Access Model
- **No Authentication Required**: All endpoints accessible without API keys, tokens, or credentials
- **Universal Access**: No geographic restrictions or IP-based filtering
- **CORS Friendly**: Direct browser access supported for client-side applications
- **Democratic Transparency**: Open data principles prioritize accessibility over access control

### Technical Security Foundation
- **Strong TLS Encryption**: TLS 1.2 with ECDHE-RSA-AES256-SHA384 cipher suite
- **Valid SSL Certificate**: GlobalSign RSA OV SSL CA 2018 (valid until August 2026)
- **Read-Only API**: Write operations properly rejected with HTTP 501 responses
- **Government Infrastructure**: Microsoft IIS/ASP.NET production stack

## Security Best Practices

### For API Consumers

#### TLS Configuration
Always use HTTPS endpoints and verify certificate validity:

```bash
# Verify TLS configuration
curl -I -v "https://oda.ft.dk/api/Sag"
```

Expected security headers:
- `TLS Version`: 1.2 or higher
- `Certificate Authority`: GlobalSign
- `Cipher Suite`: ECDHE-RSA-AES256-SHA384

#### Client-Side Security

```python
import requests
import ssl

# Enforce TLS 1.2+ in Python
session = requests.Session()
session.mount('https://', requests.adapters.HTTPAdapter(
    socket_options=[(ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)]
))

response = session.get('https://oda.ft.dk/api/Sag')
```

### Data Handling Security

#### Personal Data Protection
The API exposes extensive personal information about public officials:

```python
def handle_personal_data_securely(actor_data):
    """
    Handle biographical information with appropriate security measures
    """
    # Remove sensitive fields in client applications if not needed
    safe_fields = ['id', 'navn', 'typeid', 'startdato', 'slutdato']
    return {k: v for k, v in actor_data.items() if k in safe_fields}

# Example: Get politician info without sensitive biographical details
response = requests.get(
    "https://oda.ft.dk/api/Aktør",
    params={"$select": "id,navn,typeid,startdato,slutdato"}
)
```

#### Secure Credential Storage
Even though the API requires no authentication, implement secure practices for any derived data:

```python
import os
from cryptography.fernet import Fernet

class SecureDataHandler:
    def __init__(self):
        # For storing processed/cached API data securely
        self.encryption_key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher_suite = Fernet(self.encryption_key)
    
    def store_cached_response(self, data):
        """Encrypt cached API responses"""
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        # Store encrypted_data safely
        return encrypted_data
```

## Network Security

### Connection Security

```typescript
// TypeScript example with proper TLS configuration
import https from 'https';

const httpsAgent = new https.Agent({
    secureProtocol: 'TLSv1_2_method',
    checkServerIdentity: (host, cert) => {
        // Verify oda.ft.dk certificate
        if (host !== 'oda.ft.dk') {
            throw new Error('Invalid hostname');
        }
        return undefined; // Certificate is valid
    }
});

fetch('https://oda.ft.dk/api/Sag', {
    agent: httpsAgent
});
```

### Rate Limiting and Throttling

The API has no enforced rate limits, but implement client-side throttling for responsible usage:

```python
import time
from functools import wraps

def throttle_requests(delay=0.1):
    """Throttle API requests to be respectful"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator

class ResponsibleAPIClient:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api"
    
    @throttle_requests(delay=0.1)  # 100ms between requests
    def get_data(self, endpoint, params=None):
        """Make throttled API requests"""
        return requests.get(f"{self.base_url}/{endpoint}", params=params)
    
    def bulk_request(self, endpoints, max_concurrent=5):
        """Handle bulk requests with concurrency limits"""
        import asyncio
        import aiohttp
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_limit(session, url):
            async with semaphore:
                await asyncio.sleep(0.1)  # Throttle
                async with session.get(url) as response:
                    return await response.json()
```

## Infrastructure Security

### Server-Side Considerations

Based on API investigation findings:

```yaml
# Expected Infrastructure Characteristics
SSL_Certificate: "GlobalSign RSA OV SSL CA 2018"
TLS_Version: "1.2"
Server: "Microsoft-IIS/8.5"
Framework: "ASP.NET 4.0.30319"
Certificate_Expiry: "2026-08-03"
IP_Address: "152.115.53.70"
```

### Missing Security Headers

The API lacks some modern security headers. Client applications should compensate:

```html
<!-- Add security headers in your client application -->
<meta http-equiv="Content-Security-Policy" content="default-src 'self' https://oda.ft.dk">
<meta http-equiv="X-Content-Type-Options" content="nosniff">
<meta http-equiv="X-Frame-Options" content="DENY">
```

## Vulnerability Considerations

### Read-Only Architecture Benefits
- **No Injection Attacks**: API rejects all write operations
- **No Authentication Bypass**: No authentication to bypass  
- **Data Integrity**: Government data cannot be modified via API
- **Minimal Attack Surface**: Query-only functionality limits exposure

### Potential Risks and Mitigations

#### 1. Data Exposure Risk
```python
# Risk: Accidentally exposing personal data
def get_politician_public_info(politician_name):
    """Get only public-facing information"""
    response = requests.get(
        "https://oda.ft.dk/api/Aktør",
        params={
            "$filter": f"navn eq '{politician_name}'",
            "$select": "id,navn,typeid"  # Exclude biografi field
        }
    )
    return response.json()
```

#### 2. Query Injection Prevention
```python
import urllib.parse

def safe_odata_filter(field, value):
    """Safely construct OData filters"""
    # Escape single quotes and validate field names
    safe_value = value.replace("'", "''")
    safe_field = urllib.parse.quote(field)
    return f"{safe_field} eq '{safe_value}'"

# Usage
filter_expr = safe_odata_filter("titel", "Klima'test")
```

#### 3. Large Response Handling
```python
def handle_large_dataset_securely(entity, max_records=1000):
    """Prevent accidentally downloading massive datasets"""
    # Use pagination to limit memory usage
    records = []
    skip = 0
    page_size = 100
    
    while len(records) < max_records:
        response = requests.get(
            f"https://oda.ft.dk/api/{entity}",
            params={
                "$top": min(page_size, max_records - len(records)),
                "$skip": skip
            }
        )
        
        data = response.json().get('value', [])
        if not data:
            break
            
        records.extend(data)
        skip += page_size
    
    return records
```

## Security Checklist

### Pre-Production Security Review

- [ ] **TLS Configuration**: Verify TLS 1.2+ enforcement
- [ ] **Certificate Validation**: Check certificate expiry (current: 2026-08-03)
- [ ] **Client-Side Throttling**: Implement request rate limiting
- [ ] **Personal Data Handling**: Review biographical data usage
- [ ] **Error Handling**: Secure error response processing
- [ ] **Logging**: Implement secure audit logging
- [ ] **Access Patterns**: Monitor for unusual request patterns
- [ ] **Backup Security**: Encrypt cached/stored API data

### Monitoring and Alerting

```python
import logging

# Setup security-focused logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_security.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('parlamentapi_security')

def log_security_event(event_type, details):
    """Log security-relevant events"""
    logger.info(f"SECURITY_EVENT: {event_type} - {details}")

# Usage examples
log_security_event("API_REQUEST", f"Endpoint: /Aktør, Response_Size: {len(response.text)}")
log_security_event("PERSONAL_DATA_ACCESS", f"Biografisk data accessed for: {actor_name}")
```

## Compliance Integration

This security framework integrates with:

- **[GDPR Compliance](../../compliance/gdpr/)** - Personal data handling
- **[Data Quality](../../compliance/data-quality/)** - Data integrity and reliability  
- **[Production Deployment](../deployment/)** - Operational security

## Security Resources

- **API Investigation Report**: See [scratchpad.md](../../../scratchpad.md) Phase 15-16
- **TLS Testing Results**: Certificate analysis and configuration validation
- **Error Patterns**: Security implications of API error responses
- **Contact**: folketinget@ft.dk for security-related concerns

The Danish Parliament API's open access model represents a balance between democratic transparency and technical security. While the lack of authentication barriers may seem unusual, it reflects the public nature of parliamentary data and Denmark's commitment to government transparency.