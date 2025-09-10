# Live Interactive Examples

Welcome to the interactive tools and examples for the Danish Parliamentary Open Data API! This section provides hands-on, browser-based tools that let you explore the API without writing code.

## <¯ Overview of Interactive Features

The Danish Parliament API documentation includes several live interactive components that make learning and testing the API effortless:

### =Ê API Status Dashboard
Real-time monitoring of the Danish Parliament API with comprehensive health metrics and performance indicators.

### = Advanced Query Builder
Visual interface for constructing complex OData queries with form-based controls and live preview.

### =Ë Response Viewer
Interactive viewer for exploring API responses with formatted JSON/XML display and data visualization.

### >ê Real-Time Testing Tools
Browser-based testing utilities for immediate API query execution and result analysis.

## =€ Quick Start with Interactive Tools

### 1. Check API Status
Visit the [homepage](../../index.md) to see the live API status dashboard showing:

- **Real-time availability**: Green indicator for operational status
- **Response times**: Live measurements from Copenhagen
- **Data freshness**: How recently parliamentary data was updated
- **Entity counts**: Current record counts for major entities
- **Performance metrics**: Response quality and data freshness bars

### 2. Build Your First Query
Use any `.query-builder` widget on documentation pages to:

1. **Select an entity** (Cases, Actors, Votes, etc.)
2. **Set parameters** (limit, skip, filters)
3. **Add expansions** to include related data
4. **Generate the URL** automatically with proper encoding
5. **Test immediately** with the built-in tester

### 3. Explore Response Data
Interactive response viewers help you:

- **Format JSON/XML** with syntax highlighting
- **Navigate nested objects** with collapsible trees  
- **Understand relationships** between entities
- **Copy specific values** with one-click selection

## =à Available Interactive Tools

### API Status Dashboard

The enhanced status dashboard provides comprehensive API monitoring:

```html
<div id="api-status-widget">
  <!-- Displays live API health, metrics, and performance -->
</div>
```

**Features:**
- **Primary Status**: Large indicator showing overall API health
- **Core Data Metrics**: Live counts for Cases, Actors, Votes, Documents
- **Recent Activity**: Today's updates and last data refresh time
- **Performance Bars**: Visual representation of response time and data freshness
- **Health Checks**: Individual component status (endpoint, OData service, metadata)
- **Historical Charts**: Response time trends over recent checks
- **Auto-refresh**: Updates every 5 minutes with manual refresh option

### Advanced Query Builder

Interactive form for constructing OData queries:

```html
<div class="query-builder">
  <!-- Interactive query construction interface -->
</div>
```

**Capabilities:**
- **Entity Selection**: Choose from 50+ available entities with descriptions
- **Basic Parameters**: Set `$top`, `$skip`, `$filter`, `$expand`, `$select`, `$orderby`
- **Filter Builder**: Visual interface for complex filter expressions
- **Quick Filters**: Pre-built filters for common scenarios
- **Live URL Generation**: Real-time URL construction with proper encoding
- **Example Library**: Pre-built queries for each entity type
- **Format Options**: Toggle between JSON and XML output

**Supported Entities:**
- =Ä **Sag** (Cases) - 96,538+ parliamentary cases
- =d **Aktør** (Actors) - 18,139+ political actors  
- =ó **Afstemning** (Voting Sessions) - Parliamentary votes
-  **Stemme** (Individual Votes) - Individual politician votes
- =Ë **Dokument** (Documents) - Parliamentary documents
- <Û **Møde** (Meetings) - Parliamentary meetings
- = **SagAktør** (Case-Actor Relations) - Who worked on what
- = **DokumentAktør** (Document-Actor Relations) - Document authorship

### Response Viewer

Interactive JSON/XML response exploration:

```html
<div class="response-viewer">
  <!-- Interactive response data viewer -->
</div>
```

**Features:**
- **Syntax Highlighting**: Color-coded JSON and XML
- **Collapsible Trees**: Navigate complex nested structures
- **Copy Functionality**: One-click copying of values or entire objects
- **Search Within Response**: Find specific fields or values
- **Format Toggle**: Switch between JSON and XML views
- **Download Options**: Export responses as files

## =» Browser Requirements

### Supported Browsers
- **Chrome** 88+ (recommended)
- **Firefox** 85+
- **Safari** 14+
- **Edge** 88+

### Required Features
- **JavaScript**: All interactive features require JavaScript
- **Fetch API**: For API testing functionality
- **Clipboard API**: For copy-to-clipboard features (graceful fallback available)
- **CSS Grid**: For responsive layout (fallback available)

### Optional Enhancements
- **Canvas API**: For response time history charts
- **Web Share API**: For sharing query URLs on mobile
- **Local Storage**: For saving query history (coming soon)

## =ñ Mobile Experience

All interactive tools are fully responsive and work on mobile devices:

- **Touch-friendly**: Large buttons and touch targets
- **Swipe Navigation**: Navigate tabs and sections with swipes
- **Responsive Layout**: Adapts to screen size automatically
- **Offline Caching**: Core functionality available offline

## <¯ Interactive Widget Integration

### Adding Widgets to Pages

The interactive widgets automatically initialize when the page loads. Simply include the widget HTML structure:

```html
<!-- API Status Widget -->
<div id="api-status-widget">
  <!-- Widget content loaded by interactive.js -->
</div>

<!-- Query Builder Widget -->  
<div class="query-builder">
  <!-- Widget content loaded by interactive.js -->
</div>

<!-- Response Viewer -->
<div class="response-viewer" data-response-url="https://...">
  <!-- Widget content loaded by interactive.js -->
</div>
```

### Widget Configuration

Widgets support various configuration options via data attributes:

```html
<!-- Query Builder with pre-selected entity -->
<div class="query-builder" data-entity="Sag" data-filter="year(opdateringsdato) eq 2025">
</div>

<!-- Response Viewer with specific URL -->
<div class="response-viewer" 
     data-url="https://oda.ft.dk/api/Sag?$top=5"
     data-format="json">
</div>
```

## =' Advanced Features

### Analytics and Tracking

The interactive tools include built-in analytics to track:

- **Query Building**: Which entities and filters are most popular
- **Copy Events**: Which code examples are copied most frequently
- **External Links**: Which API endpoints are accessed most
- **Engagement**: How users interact with the documentation

### Performance Optimization

Interactive features include several performance optimizations:

- **Lazy Loading**: Widgets initialize only when visible
- **Request Caching**: API responses cached for 15 minutes
- **Responsive Images**: Optimized assets for different screen sizes
- **Code Splitting**: Interactive features load separately from main content

### Accessibility

All interactive tools follow WCAG 2.1 guidelines:

- **Keyboard Navigation**: Full keyboard support for all interactions
- **Screen Reader Support**: ARIA labels and descriptions
- **High Contrast**: Respects system preferences
- **Focus Management**: Proper focus handling for dynamic content

## =ú Navigation to Specific Tools

### Query Builder
- **Location**: Available on most documentation pages
- **Direct Link**: [Query Builder Tool](query-builder.md)
- **Use Case**: Building and testing OData queries interactively

### Response Viewer  
- **Location**: Code example pages and API reference
- **Direct Link**: [Response Viewer Tool](response-viewer.md)
- **Use Case**: Exploring API response structure and data

### API Status Dashboard
- **Location**: [Homepage](../../index.md) - enhanced widget
- **Simple Version**: Most pages - basic status indicator
- **Use Case**: Real-time API health monitoring

## =€ Getting Started Workflow

1. **Check API Status** - Visit the homepage to ensure the API is operational
2. **Explore Examples** - Browse the [Code Examples](../index.md) section
3. **Build a Query** - Use the interactive query builder on any page
4. **Test Your Query** - Click "Test" to see live results
5. **View Responses** - Use the response viewer to understand the data structure
6. **Copy Code** - Use the copy buttons to get code for your application
7. **Iterate and Learn** - Experiment with different entities and parameters

## > Interactive Help and Support

### Built-in Help
- **Tooltips**: Hover over any input for contextual help
- **Examples**: Pre-built queries for every entity type  
- **Validation**: Real-time feedback on query construction
- **Error Messages**: Clear explanations when something goes wrong

### Documentation Integration
- **Contextual Links**: Jump directly to relevant documentation sections
- **Field Descriptions**: Understand what each parameter does
- **Relationship Mapping**: Visual guides to entity relationships

## =¡ Interactive Examples in Action

### Try the Query Builder

<div class="query-builder">
  <!-- This will be replaced by the interactive query builder when the page loads -->
  <p><em>Loading interactive query builder...</em></p>
</div>

### API Status Check

<div class="api-status">
  <div class="status-indicator"></div>
  <div class="status-info">
    <strong>Danish Parliament API</strong>
    <br>Status: <span class="status-text">Checking...</span>
    <br>Cases: <span data-api-count="cases">96,538+</span>
    <br>Actors: <span data-api-count="actors">18,139+</span>
  </div>
</div>

## <® Interactive Features Summary

| Feature | Purpose | Location | Mobile Support |
|---------|---------|----------|----------------|
| **API Status Dashboard** | Real-time API health monitoring | Homepage |  Full support |
| **Query Builder** | Visual OData query construction | Most pages |  Touch-optimized |
| **Response Viewer** | JSON/XML response exploration | Code examples |  Swipe navigation |
| **Copy-to-Clipboard** | Quick code copying | All code blocks |  Fallback available |
| **Search Enhancement** | Improved documentation search | Header |  Voice search ready |

## = OData Query Examples

The interactive tools make it easy to construct complex queries. Here are some examples you can build:

### Recent Parliamentary Cases
```
Entity: Sag
Filter: year(opdateringsdato) eq 2025
OrderBy: opdateringsdato desc
Top: 10
```

### Climate-Related Legislation
```
Entity: Sag  
Filter: substringof('klima', titel) or substringof('miljø', titel)
Expand: Sagsstatus,Sagstype
Top: 20
```

### Active Politicians from Specific Party
```
Entity: Aktør
Filter: typeid eq 5 and slutdato eq null
Expand: Aktørtype,Periode
Top: 50
```

## <ÃB Performance Tips

### Optimizing Interactive Queries
- **Use Top Parameter**: Limit results to avoid large responses
- **Specific Filters**: Narrow down results with precise filters  
- **Selective Expansion**: Only expand relationships you need
- **Field Selection**: Use `$select` to get only required fields

### Browser Performance  
- **Modern Browser**: Use Chrome 88+ for best performance
- **JavaScript Enabled**: Required for all interactive features
- **Good Connection**: Interactive features work better with stable internet

The interactive tools are designed to make the Danish Parliament API accessible to developers of all skill levels. Whether you're a seasoned API developer or just starting out, these browser-based tools will help you understand and effectively use the world's most comprehensive parliamentary data API.

---

*Next: Explore the [Advanced Query Builder](query-builder.md) for hands-on query construction*