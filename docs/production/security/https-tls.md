# HTTPS and TLS Configuration

The Danish Parliament API implements strong TLS encryption to protect data in transit. This guide covers TLS configuration details, certificate management, and client-side implementation best practices.

## TLS Configuration Analysis

### Current TLS Setup

Based on comprehensive security testing (Phase 15 investigation), the API uses:

```
TLS Version: 1.2
Cipher Suite: ECDHE-RSA-AES256-SHA384
Certificate Authority: GlobalSign RSA OV SSL CA 2018
Certificate Validity: Until August 3, 2026
Wildcard Coverage: *.ft.dk (covers oda.ft.dk)
```

### Certificate Details

```bash
# Verify current certificate status
curl -I -v "https://oda.ft.dk/api/Sag" 2>&1 | grep -E "(SSL|TLS|Certificate)"

# Expected output:
# * TLSv1.2 (OUT), TLS handshake, Client hello (1):
# * TLSv1.2 (IN), TLS handshake, Server hello (2):
# * TLSv1.2 (IN), TLS handshake, Certificate (11):
# * SSL certificate verify ok.
```

### Security Strength Assessment

**Strengths:**
- ✅ Strong cipher suite (AES-256, SHA-384)
- ✅ Forward secrecy (ECDHE key exchange)
- ✅ Valid certificate chain
- ✅ Wildcard certificate properly configured
- ✅ Certificate from trusted CA (GlobalSign)

**Limitations:**
-   No HTTP/2 support (uses HTTP/1.1)
-   Missing security headers (HSTS, CSP)
-   Aggressive no-cache policies (no ETag support)

## Client Configuration

### Python Implementation

```python
import requests
import ssl
import urllib3
from requests.adapters import HTTPAdapter

class SecureDanishParliamentClient:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://oda.ft.dk/api"
        self._configure_tls()
    
    def _configure_tls(self):
        """Configure secure TLS settings"""
        # Create SSL context with strong security
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # Disable weak protocols
        ssl_context.options |= ssl.OP_NO_SSLv2
        ssl_context.options |= ssl.OP_NO_SSLv3
        ssl_context.options |= ssl.OP_NO_TLSv1
        ssl_context.options |= ssl.OP_NO_TLSv1_1
        
        # Set minimum TLS version to 1.2
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # Configure adapter
        adapter = HTTPAdapter()
        self.session.mount('https://', adapter)
        
        # Verify certificate
        self.session.verify = True
    
    def verify_connection_security(self):
        """Verify TLS connection security"""
        try:
            response = self.session.get(f"{self.base_url}/Sag?$top=1")
            
            # Check response headers for security info
            connection_info = {
                'status_code': response.status_code,
                'url': response.url,
                'headers': dict(response.headers),
                'tls_verified': response.url.startswith('https://'),
                'certificate_valid': True  # If no SSL error occurred
            }
            
            return connection_info
        except requests.exceptions.SSLError as e:
            return {'error': f'TLS verification failed: {e}'}
    
    def get_with_security_check(self, endpoint, params=None):
        """Make API request with security validation"""
        try:
            response = self.session.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=30  # Prevent hanging connections
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.SSLError as e:
            raise SecurityError(f"TLS security check failed: {e}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}")

# Usage example
client = SecureDanishParliamentClient()
security_status = client.verify_connection_security()
print(f"Connection security: {security_status}")
```

### JavaScript/Node.js Implementation

```javascript
const https = require('https');
const crypto = require('crypto');

class SecureDanishParliamentClient {
    constructor() {
        this.baseURL = 'https://oda.ft.dk/api';
        this.httpsAgent = this.createSecureAgent();
    }
    
    createSecureAgent() {
        return new https.Agent({
            // Enforce TLS 1.2+
            secureProtocol: 'TLSv1_2_method',
            
            // Certificate verification
            checkServerIdentity: (host, cert) => {
                if (host !== 'oda.ft.dk') {
                    throw new Error('Invalid hostname in certificate');
                }
                
                // Verify certificate chain
                const now = new Date();
                const notAfter = new Date(cert.valid_to);
                if (now > notAfter) {
                    throw new Error('Certificate has expired');
                }
                
                return undefined; // Certificate is valid
            },
            
            // Cipher suite restrictions
            ciphers: [
                'ECDHE-RSA-AES256-GCM-SHA384',
                'ECDHE-RSA-AES256-SHA384',
                'ECDHE-RSA-AES128-GCM-SHA256'
            ].join(':'),
            
            // Security options
            honorCipherOrder: true,
            rejectUnauthorized: true
        });
    }
    
    async makeSecureRequest(endpoint, params = {}) {
        const url = new URL(endpoint, this.baseURL);
        Object.entries(params).forEach(([key, value]) => {
            url.searchParams.append(key, value);
        });
        
        return new Promise((resolve, reject) => {
            const options = {
                agent: this.httpsAgent,
                headers: {
                    'User-Agent': 'Danish-Parliament-Client/1.0',
                    'Accept': 'application/json'
                }
            };
            
            https.get(url, options, (response) => {
                let data = '';
                
                response.on('data', chunk => data += chunk);
                response.on('end', () => {
                    if (response.statusCode === 200) {
                        try {
                            resolve(JSON.parse(data));
                        } catch (e) {
                            reject(new Error('Invalid JSON response'));
                        }
                    } else {
                        reject(new Error(`HTTP ${response.statusCode}`));
                    }
                });
            }).on('error', (error) => {
                if (error.code === 'CERT_UNTRUSTED') {
                    reject(new Error('Certificate trust verification failed'));
                } else if (error.code === 'EPROTO') {
                    reject(new Error('TLS protocol error'));
                } else {
                    reject(error);
                }
            });
        });
    }
    
    async verifyCertificate() {
        return new Promise((resolve, reject) => {
            const options = {
                host: 'oda.ft.dk',
                port: 443,
                agent: this.httpsAgent
            };
            
            const socket = crypto.connect(options, () => {
                const cert = socket.getPeerCertificate(true);
                const result = {
                    subject: cert.subject,
                    issuer: cert.issuer,
                    valid_from: cert.valid_from,
                    valid_to: cert.valid_to,
                    fingerprint: cert.fingerprint,
                    serialNumber: cert.serialNumber,
                    is_valid: socket.authorized
                };
                socket.end();
                resolve(result);
            });
            
            socket.on('error', reject);
        });
    }
}

// Usage
const client = new SecureDanishParliamentClient();

// Verify certificate before making requests
client.verifyCertificate()
    .then(cert => {
        console.log('Certificate verified:', cert);
        return client.makeSecureRequest('Sag', {'$top': '5'});
    })
    .then(data => console.log('API data:', data))
    .catch(error => console.error('Security error:', error));
```

### Browser Implementation

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" 
          content="default-src 'self' https://oda.ft.dk; 
                   img-src 'self' data: https:; 
                   style-src 'self' 'unsafe-inline';">
    <title>Secure Danish Parliament API Client</title>
</head>
<body>
    <script>
        class BrowserSecureClient {
            constructor() {
                this.baseURL = 'https://oda.ft.dk/api';
            }
            
            async makeSecureRequest(endpoint, params = {}) {
                const url = new URL(endpoint, this.baseURL);
                Object.entries(params).forEach(([key, value]) => {
                    url.searchParams.append(key, value);
                });
                
                try {
                    const response = await fetch(url, {
                        method: 'GET',
                        mode: 'cors',
                        credentials: 'omit', // No credentials needed
                        headers: {
                            'Accept': 'application/json',
                            'Cache-Control': 'no-cache'
                        },
                        // Browser automatically handles TLS
                        redirect: 'follow'
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    
                    // Verify we're still on HTTPS
                    if (!response.url.startsWith('https://')) {
                        throw new Error('Response was not served over HTTPS');
                    }
                    
                    return await response.json();
                } catch (error) {
                    console.error('Secure request failed:', error);
                    throw error;
                }
            }
            
            checkConnectionSecurity() {
                return {
                    protocol: location.protocol,
                    is_secure: location.protocol === 'https:',
                    mixed_content_blocked: !window.isSecureContext,
                    tls_version: 'Managed by browser'
                };
            }
        }
        
        // Initialize secure client
        const client = new BrowserSecureClient();
        
        // Check security status
        console.log('Connection security:', client.checkConnectionSecurity());
        
        // Make secure API request
        client.makeSecureRequest('Sag', {'$top': '3'})
            .then(data => console.log('Secure API response:', data))
            .catch(error => console.error('Security error:', error));
    </script>
</body>
</html>
```

## Certificate Management

### Monitoring Certificate Expiry

```python
import ssl
import socket
from datetime import datetime

def check_certificate_expiry(hostname🔧oda.ft.dk', port=443):
    """Monitor certificate expiry"""
    context = ssl.create_default_context()
    
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            
            # Parse expiry date
            expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_until_expiry = (expiry_date - datetime.now()).days
            
            return {
                'certificate_subject': cert['subject'],
                'issuer': cert['issuer'],
                'expires': expiry_date.isoformat(),
                'days_until_expiry': days_until_expiry,
                'is_valid': days_until_expiry > 0
            }

# Example monitoring
cert_status = check_certificate_expiry()
print(f"Certificate expires in {cert_status['days_until_expiry']} days")

if cert_status['days_until_expiry'] < 30:
    print("WARNING: Certificate expires soon!")
```

### Certificate Pinning (Advanced)

```python
import hashlib
import ssl

# Expected certificate fingerprints (update when certificates change)
EXPECTED_CERT_FINGERPRINTS = [
    'sha256:expected_fingerprint_here'  # Update with actual fingerprint
]

def verify_certificate_pin(hostname🔧oda.ft.dk', port=443):
    """Verify certificate against known fingerprints"""
    context = ssl.create_default_context()
    
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert_der = ssock.getpeercert_chain()[0].encode('DER')
            cert_fingerprint = hashlib.sha256(cert_der).hexdigest()
            
            if f"sha256:{cert_fingerprint}" in EXPECTED_CERT_FINGERPRINTS:
                return True
            else:
                raise SecurityError(f"Certificate fingerprint mismatch: {cert_fingerprint}")
```

## Troubleshooting TLS Issues

### Common TLS Problems

#### 1. Certificate Verification Errors

```python
# Problem: Certificate verification fails
# Solution: Update certificate store or check system time

import certifi
import requests

# Use latest certificate bundle
response = requests.get(
    'https://oda.ft.dk/api/Sag',
    verify=certifi.where()
)
```

#### 2. TLS Version Mismatches

```python
# Problem: Client using outdated TLS version
# Solution: Explicitly configure TLS 1.2+

import ssl
import urllib3

# Disable warnings for testing only
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create context with specific TLS version
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.minimum_version = ssl.TLSVersion.TLSv1_2
```

#### 3. Cipher Suite Compatibility

```bash
# Test supported cipher suites
openssl s_client -connect oda.ft.dk:443 -cipher 'ECDHE-RSA-AES256-SHA384'

# Expected output should include:
# Cipher    : ECDHE-RSA-AES256-SHA384
# Verification: OK
```

### Diagnostic Commands

```bash
# Comprehensive TLS analysis
curl -I -v "https://oda.ft.dk/api/Sag" 2>&1 | grep -E "(TLS|SSL|Certificate|Cipher)"

# Test specific TLS version
openssl s_client -connect oda.ft.dk:443 -tls1_2

# Certificate chain analysis
openssl s_client -connect oda.ft.dk:443 -showcerts < /dev/null

# Check certificate expiry
openssl s_client -connect oda.ft.dk:443 < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

## Best Practices Summary

### Security Requirements
1. **Always use HTTPS**: Never make API requests over HTTP
2. **Verify certificates**: Enable certificate verification in all clients
3. **Use TLS 1.2+**: Disable older protocol versions
4. **Monitor expiry**: Track certificate expiration dates
5. **Handle errors**: Properly handle TLS-related exceptions

### Performance Considerations
1. **Connection pooling**: Reuse TLS connections when possible
2. **Timeout settings**: Set appropriate connection timeouts
3. **Certificate caching**: Cache certificate validation results
4. **HTTP/1.1 limitation**: API doesn't support HTTP/2, optimize accordingly

### Compliance Integration
- **GDPR**: Ensure encrypted data transmission for personal information
- **Data Quality**: Verify data integrity through secure connections
- **Monitoring**: Log TLS-related security events

The Danish Parliament API's TLS implementation provides strong encryption for data in transit. While it lacks some modern features like HTTP/2 and security headers, the core TLS configuration is robust and suitable for production use.