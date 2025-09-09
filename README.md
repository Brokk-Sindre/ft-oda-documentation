# Danish Parliament API Documentation

Comprehensive documentation for Denmark's Parliamentary Open Data API (oda.ft.dk) - the world's gold standard for government transparency APIs.

🌐 **[View Live Documentation](https://brokk-sindre.github.io/ft-oda-documentation/)**

## Overview

The Danish Parliament (Folketinget) provides complete access to parliamentary data through a public OData 3.0 API. This repository contains extensive documentation, code examples, and best practices for using the API effectively.

### Key Features

- **No Authentication Required** - Completely open access
- **96,538+ Parliamentary Cases** - Complete legislative history
- **18,139+ Political Actors** - MPs, ministers, committees
- **Real-time Updates** - Data updated within hours of parliamentary activity
- **74+ Years of History** - Records from 1952 to present
- **OData 3.0 Protocol** - Powerful querying capabilities

## Quick Start

### Simple API Call
```bash
# Get recent parliamentary cases
curl "https://oda.ft.dk/api/Sag?$top=5"
```

### Python Example
```python
import requests

# Get voting records for a specific case
response = requests.get(
    "https://oda.ft.dk/api/Afstemning",
    params={"$filter": "sagid eq 102903", "$expand": "Stemme"}
)
data = response.json()
```

## Documentation Structure

### 📚 [Getting Started](https://brokk-sindre.github.io/ft-oda-documentation/getting-started/)
- First queries and basic concepts
- Understanding Danish parliamentary terms
- No authentication setup
- Common mistakes to avoid

### 🔧 [API Reference](https://brokk-sindre.github.io/ft-oda-documentation/api-reference/)
- Complete entity documentation
- OData query parameters
- Error handling
- Performance optimization

### 💻 [Code Examples](https://brokk-sindre.github.io/ft-oda-documentation/code-examples/)
- Python, JavaScript, TypeScript implementations
- Pagination and error handling
- Ready-to-use client libraries
- Interactive examples

### 📊 [Use Case Guides](https://brokk-sindre.github.io/ft-oda-documentation/guides/)
- Voting analysis and patterns
- Legislative tracking
- Real-time monitoring
- Advanced data analysis

### 🏗️ [Production](https://brokk-sindre.github.io/ft-oda-documentation/production/)
- Architecture patterns
- Security considerations
- Performance optimization
- Troubleshooting

## Local Development

### Prerequisites
- Python 3.11+
- pip package manager

### Setup
```bash
# Clone the repository
git clone https://github.com/Brokk-Sindre/ft-oda-documentation.git
cd ft-oda-documentation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

The documentation will be available at `http://localhost:8000`

## Repository Structure

```
ft-oda-documentation/
├── docs/                    # Documentation source files
│   ├── index.md            # Home page
│   ├── getting-started/    # Getting started guides
│   ├── api-reference/      # API reference documentation
│   ├── code-examples/      # Code examples
│   ├── guides/             # Use case guides
│   ├── data-model/         # Data model documentation
│   ├── production/         # Production deployment guides
│   ├── compliance/         # Legal and compliance
│   └── appendix/           # Additional resources
├── mkdocs.yml              # MkDocs configuration
├── requirements.txt        # Python dependencies
└── .github/workflows/      # GitHub Actions for deployment
```

## Key API Entities

| Entity | Description | Endpoint |
|--------|-------------|----------|
| **Sag** | Parliamentary cases, bills, proposals | `/api/Sag` |
| **Aktør** | Politicians, committees, ministries | `/api/Aktør` |
| **Afstemning** | Voting sessions | `/api/Afstemning` |
| **Stemme** | Individual votes | `/api/Stemme` |
| **Dokument** | Parliamentary documents | `/api/Dokument` |
| **Møde** | Parliamentary meetings | `/api/Møde` |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Workflow
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Testing the API

### Basic Connection Test
```bash
# Test API availability
curl -I https://oda.ft.dk/api/

# Get API metadata
curl https://oda.ft.dk/api/\$metadata
```

### Performance Test
```python
import time
import requests

def test_performance():
    endpoints = ['Sag', 'Aktør', 'Afstemning']
    for endpoint in endpoints:
        start = time.time()
        response = requests.get(f"https://oda.ft.dk/api/{endpoint}?$top=1")
        elapsed = time.time() - start
        print(f"{endpoint}: {elapsed:.2f}s - Status: {response.status_code}")

test_performance()
```

## Support

### Documentation Issues
- Open an issue in this repository
- Submit a pull request with fixes

### API Issues
- Contact: folketinget@ft.dk
- Subject: "Åbne Data" (Open Data)

### Community
- Discuss in GitHub Issues
- Share use cases and examples
- Request documentation improvements

## License

This documentation is provided as-is for public use. The Danish Parliament API data is publicly available under Denmark's open data initiative.

### Attribution
When using data from the API, please attribute:
```
Data source: Danish Parliament (Folketinget) - oda.ft.dk
```

## Acknowledgments

- Danish Parliament (Folketinget) for providing the open data API
- The Danish government's commitment to transparency
- Contributors to this documentation project

## Related Resources

- [Official Parliament Website](https://www.ft.dk/)
- [Danish Open Data Portal](https://www.opendata.dk/)
- [OData Protocol Documentation](https://www.odata.org/)

---

**Last Updated**: September 2025  
**Documentation Version**: 1.0.0  
**API Version**: OData 3.0