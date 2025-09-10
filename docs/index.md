---
title: Danish Parliament API Documentation - Comprehensive Guide to oda.ft.dk
description: Complete documentation for Denmark's Parliamentary Open Data API (oda.ft.dk). Access 96,538+ cases, 18,139+ actors, and 74+ years of parliamentary data with no authentication required.
keywords: danish parliament api, oda.ft.dk, odata api, government transparency, parliamentary data, folketing api, open data denmark
author: Danish Parliament API Documentation Project
---

# Danish Parliament API Documentation

![Logo](assets/images/logo.svg)

Welcome to the comprehensive documentation for Denmark's Parliamentary Open Data API (oda.ft.dk) - the world's gold standard for government transparency APIs.

## 🏛️ API Highlights

- **Universal Access**: No authentication required
- **Massive Dataset**: 96,538+ cases, 18,139+ actors, 74+ years of data
- **Real-Time Updates**: Parliamentary activity reflected within hours
- **Complete Transparency**: Every vote, document, and relationship tracked
- **50 Entities**: Comprehensive parliamentary process modeling
- **Exceptional Performance**: 85ms-2s response times

## 🚀 Quick Start

### Your First API Call

```bash
curl "https://oda.ft.dk/api/Sag?%24top=5"
```

!!! warning "Critical: URL Encoding"
    Always use `%24` instead of `$` in OData parameters. This is the most common mistake developers make.

### Recent Parliamentary Activity

```bash
# Get today's case updates
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-09-09T00:00:00'&%24top=10"
```

## 📊 Live API Status Dashboard

<div class="enhanced-api-status" id="api-status-widget">
  <!-- Primary Status -->
  <div class="status-primary">
    <div class="status-main">
      <div class="status-indicator-large" id="main-status">
        <div class="pulse-ring"></div>
        <div class="pulse-dot"></div>
      </div>
      <div class="status-info">
        <h3 class="status-title">Danish Parliament API</h3>
        <p class="status-description" id="status-text">Checking status...</p>
        <p class="status-uptime">Uptime: <span id="uptime-display">--</span></p>
      </div>
    </div>
    <div class="response-time">
      <div class="metric">
        <span class="metric-value" id="response-time">--</span>
        <span class="metric-unit">ms</span>
        <span class="metric-label">Response Time</span>
      </div>
    </div>
  </div>

  <!-- Data Metrics -->
  <div class="status-metrics">
    <div class="metric-group">
      <h4>📄 Core Data</h4>
      <div class="metric-grid">
        <div class="metric-item">
          <span class="metric-number" data-api-count="cases" data-entity="Sag">96,538</span>
          <span class="metric-label">Cases (Sag)</span>
          <div class="metric-trend" data-trend="cases"></div>
        </div>
        <div class="metric-item">
          <span class="metric-number" data-api-count="actors" data-entity="Aktør">18,139</span>
          <span class="metric-label">Actors (Aktør)</span>
          <div class="metric-trend" data-trend="actors"></div>
        </div>
        <div class="metric-item">
          <span class="metric-number" data-api-count="votes" data-entity="Stemme">--</span>
          <span class="metric-label">Votes (Stemme)</span>
          <div class="metric-trend" data-trend="votes"></div>
        </div>
        <div class="metric-item">
          <span class="metric-number" data-api-count="documents" data-entity="Dokument">--</span>
          <span class="metric-label">Documents</span>
          <div class="metric-trend" data-trend="documents"></div>
        </div>
      </div>
    </div>

    <div class="metric-group">
      <h4>🔄 Recent Activity</h4>
      <div class="activity-stats">
        <div class="activity-item">
          <span class="activity-number" id="today-updates">--</span>
          <span class="activity-label">Updates Today</span>
        </div>
        <div class="activity-item">
          <span class="activity-time" id="last-update">--</span>
          <span class="activity-label">Last Update</span>
        </div>
      </div>
    </div>

    <div class="metric-group">
      <h4>⚡ Performance</h4>
      <div class="performance-bars">
        <div class="perf-item">
          <span class="perf-label">API Response</span>
          <div class="perf-bar">
            <div class="perf-fill" id="response-bar" style="width: 0%"></div>
          </div>
          <span class="perf-value" id="response-quality">Excellent</span>
        </div>
        <div class="perf-item">
          <span class="perf-label">Data Freshness</span>
          <div class="perf-bar">
            <div class="perf-fill" id="freshness-bar" style="width: 0%"></div>
          </div>
          <span class="perf-value" id="freshness-quality">Real-time</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Status Details -->
  <div class="status-details">
    <div class="detail-tabs">
      <button class="detail-tab active" data-tab="health">Health</button>
      <button class="detail-tab" data-tab="metrics">Metrics</button>
      <button class="detail-tab" data-tab="history">History</button>
    </div>
    
    <div class="detail-content active" data-tab="health">
      <div class="health-checks">
        <div class="health-item" id="endpoint-check">
          <span class="health-icon">⏳</span>
          <span class="health-label">Primary Endpoint</span>
          <span class="health-status">Checking...</span>
        </div>
        <div class="health-item" id="odata-check">
          <span class="health-icon">⏳</span>
          <span class="health-label">OData Service</span>
          <span class="health-status">Checking...</span>
        </div>
        <div class="health-item" id="metadata-check">
          <span class="health-icon">⏳</span>
          <span class="health-label">Metadata</span>
          <span class="health-status">Checking...</span>
        </div>
      </div>
    </div>
    
    <div class="detail-content" data-tab="metrics">
      <div class="metrics-summary">
        <p>Entity counts updated every 15 minutes</p>
        <p>Response time measured from Copenhagen, Denmark</p>
        <p>Uptime calculated over 30-day rolling window</p>
      </div>
    </div>
    
    <div class="detail-content" data-tab="history">
      <div class="history-chart">
        <canvas id="response-history" width="400" height="100"></canvas>
      </div>
    </div>
  </div>

  <!-- Refresh Control -->
  <div class="status-controls">
    <button class="refresh-btn" id="refresh-status">🔄 Refresh</button>
    <span class="last-check">Last checked: <span id="last-check-time">--</span></span>
  </div>
</div>

## 🎯 Common Use Cases

=== "Voting Analysis"
    Track individual politician voting records and patterns
    
    ```python
    # Get all votes by specific politician
    api_client.get_voting_records("Frank Aaen")
    ```

=== "Legislative Tracking"
    Monitor bill progress through parliamentary process
    
    ```python
    # Track climate legislation
    api_client.get_cases(filter="substringof('klima', titel)")
    ```

=== "Real-Time Monitoring"
    Monitor parliamentary activity as it happens
    
    ```python
    # Get recent changes
    api_client.get_recent_changes(hours_back=4)
    ```

## 📚 Documentation Structure

- **[Getting Started](getting-started/)** - Your first steps with the API
- **[API Reference](api-reference/)** - Complete technical specification
- **[Code Examples](code-examples/)** - Production-ready client libraries
- **[Guides](guides/)** - Common use cases and patterns
- **[Data Model](data-model/)** - Parliamentary process understanding
- **[Production](production/)** - Deployment and optimization

## ⭐ What Makes This Documentation Special

This documentation is based on the most comprehensive technical investigation ever conducted on a parliamentary API:

- **30 Investigation Phases**: Every aspect tested and documented
- **Real-World Testing**: All examples tested against live API
- **Production Experience**: Includes error patterns and optimization strategies
- **Complete Coverage**: 50 entities, 200+ status types, 100+ role types documented

## 🤝 Contributing

This documentation is open source. Contributions, corrections, and improvements are welcome!

---

*Built with ❤️ for democratic transparency*

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "Danish Parliament API Documentation - Comprehensive Guide to oda.ft.dk",
  "description": "Complete documentation for Denmark's Parliamentary Open Data API (oda.ft.dk). Access 96,538+ cases, 18,139+ actors, and 74+ years of parliamentary data with no authentication required.",
  "author": {
    "@type": "Organization",
    "name": "Danish Parliament API Documentation Project"
  },
  "publisher": {
    "@type": "Organization", 
    "name": "Danish Parliament API Documentation Project"
  },
  "datePublished": "2025-09-09",
  "dateModified": "2025-09-09",
  "mainEntity": {
    "@type": "SoftwareApplication",
    "name": "Danish Parliament Open Data API",
    "applicationCategory": "GovernmentApplication",
    "operatingSystem": "Web-based",
    "url": "https://oda.ft.dk/",
    "description": "Open Data API providing access to Danish Parliament data including cases, actors, votes, and documents",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "DKK",
      "availability": "https://schema.org/InStock"
    },
    "featureList": [
      "96,538+ parliamentary cases",
      "18,139+ political actors",
      "74+ years of historical data", 
      "Real-time updates",
      "No authentication required",
      "OData 3.0 protocol support"
    ]
  },
  "about": {
    "@type": "Thing",
    "name": "Danish Parliament",
    "description": "The national parliament of Denmark"
  },
  "keywords": "danish parliament api, oda.ft.dk, odata api, government transparency, parliamentary data, folketing api, open data denmark"
}
</script>