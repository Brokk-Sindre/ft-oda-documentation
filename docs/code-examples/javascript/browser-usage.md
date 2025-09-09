# JavaScript Browser Usage

Complete guide for using the Danish Parliament API in web browsers with CORS handling, modern JavaScript, and interactive examples.

## Overview

The Danish Parliament API supports **CORS (Cross-Origin Resource Sharing)**, making it directly accessible from web browsers without a backend proxy. This enables powerful client-side applications for parliamentary data visualization and analysis.

## Browser Compatibility

- **Modern browsers**: Chrome 42+, Firefox 39+, Safari 10.1+, Edge 14+
- **Native fetch API**: No external dependencies required
- **ES6+ features**: Async/await, classes, modules
- **CORS enabled**: Direct API access from any domain

## Basic Browser Setup

### 1. HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Danish Parliament API Browser Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .loading {
            color: #666;
            font-style: italic;
        }
        .error {
            color: #d32f2f;
            background: #ffebee;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .success {
            color: #388e3c;
            background: #e8f5e8;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .case-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            background: #fafafa;
        }
        .case-title {
            font-weight: bold;
            color: #1976d2;
            margin-bottom: 5px;
        }
        .case-meta {
            font-size: 0.9em;
            color: #666;
        }
        .controls {
            margin: 20px 0;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
        }
        .controls input, .controls button {
            margin: 5px;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .controls button {
            background: #1976d2;
            color: white;
            cursor: pointer;
        }
        .controls button:hover {
            background: #1565c0;
        }
        #progressBar {
            width: 100%;
            height: 20px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        #progressFill {
            height: 100%;
            background: #4caf50;
            width: 0%;
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <h1>Danish Parliament API Browser Demo</h1>
    
    <div class="controls">
        <h3>Search Parliamentary Cases</h3>
        <input type="text" id="searchTerm" placeholder="Search term (e.g., 'klima')" value="klima">
        <input type="number" id="maxResults" placeholder="Max results" value="20" min="1" max="100">
        <button onclick="searchCases()">Search Cases</button>
        <button onclick="getRecentActivity()">Get Recent Activity</button>
        <button onclick="clearResults()">Clear Results</button>
    </div>
    
    <div id="status" class="loading" style="display: none;">Loading...</div>
    <div id="progressBar" style="display: none;">
        <div id="progressFill"></div>
    </div>
    <div id="results"></div>
    
    <script type="module">
        // Import the API client (assuming it's in the same directory)
        import { DanishParliamentAPI } from './danish-parliament-api.js';
        
        // Initialize the API client
        const api = new DanishParliamentAPI({
            requestDelay: 200 // Be extra respectful in browsers
        });
        
        // Make functions globally available
        window.api = api;
        window.searchCases = searchCases;
        window.getRecentActivity = getRecentActivity;
        window.clearResults = clearResults;
        
        // Search function
        async function searchCases() {
            const searchTerm = document.getElementById('searchTerm').value.trim();
            const maxResults = parseInt(document.getElementById('maxResults').value) || 20;
            
            if (!searchTerm) {
                showError('Please enter a search term');
                return;
            }
            
            showStatus('Searching for cases...');
            showProgress(0);
            
            try {
                // Search for cases
                const response = await api.getCases({
                    filter: `substringof('${searchTerm}', titel)`,
                    top: Math.min(maxResults, 100),
                    orderby: 'opdateringsdato desc'
                });
                
                showProgress(100);
                displayCases(response.value, `Search results for "${searchTerm}"`);
                showSuccess(`Found ${response.value.length} cases`);
                
            } catch (error) {
                showError(`Search failed: ${error.message}`);
                hideProgress();
            }
        }
        
        // Get recent activity
        async function getRecentActivity() {
            showStatus('Fetching recent parliamentary activity...');
            showProgress(0);
            
            try {
                const response = await api.getRecentChanges('Sag', 24); // Last 24 hours
                
                showProgress(100);
                displayCases(response.value, 'Recent Parliamentary Activity (Last 24 hours)');
                showSuccess(`Found ${response.value.length} recently updated cases`);
                
            } catch (error) {
                showError(`Failed to fetch recent activity: ${error.message}`);
                hideProgress();
            }
        }
        
        // Display cases in the UI
        function displayCases(cases, title) {
            const resultsDiv = document.getElementById('results');
            
            if (cases.length === 0) {
                resultsDiv.innerHTML = `<div class="error">No cases found</div>`;
                return;
            }
            
            let html = `<h2>${title}</h2>`;
            
            cases.forEach(case => {
                const updatedDate = new Date(case.opdateringsdato).toLocaleDateString('da-DK');
                html += `
                    <div class="case-card">
                        <div class="case-title">${case.titel}</div>
                        <div class="case-meta">
                            ID: ${case.id} | 
                            Updated: ${updatedDate} | 
                            Type: ${case.typeid}
                        </div>
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = html;
            hideStatus();
        }
        
        // UI helper functions
        function showStatus(message) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.style.display = 'block';
            statusDiv.className = 'loading';
        }
        
        function showSuccess(message) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.style.display = 'block';
            statusDiv.className = 'success';
            setTimeout(() => hideStatus(), 3000);
        }
        
        function showError(message) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.style.display = 'block';
            statusDiv.className = 'error';
        }
        
        function hideStatus() {
            document.getElementById('status').style.display = 'none';
        }
        
        function showProgress(percentage) {
            const progressBar = document.getElementById('progressBar');
            const progressFill = document.getElementById('progressFill');
            
            progressBar.style.display = 'block';
            progressFill.style.width = percentage + '%';
        }
        
        function hideProgress() {
            document.getElementById('progressBar').style.display = 'none';
        }
        
        function clearResults() {
            document.getElementById('results').innerHTML = '';
            hideStatus();
            hideProgress();
        }
        
        // Initialize with a sample search on page load
        window.addEventListener('load', () => {
            console.log('Danish Parliament API Browser Demo loaded');
            console.log('Try searching for "klima" to see climate-related legislation');
        });
    </script>
</body>
</html>
```

### 2. Advanced Interactive Dashboard

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parliamentary Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .widget {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .widget h3 {
            margin: 0 0 15px 0;
            color: #333;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-item {
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #1976d2;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #1976d2;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <h1>Danish Parliament Live Dashboard</h1>
    
    <div class="dashboard">
        <!-- Statistics Widget -->
        <div class="widget">
            <h3>=Ê Parliamentary Statistics</h3>
            <div id="statsLoader" class="loading-spinner"></div>
            <div id="statsContent" style="display: none;">
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="stat-number" id="totalCases">-</div>
                        <div class="stat-label">Total Cases</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="totalActors">-</div>
                        <div class="stat-label">Total Actors</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="recentUpdates">-</div>
                        <div class="stat-label">Updates Today</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="apiResponseTime">-</div>
                        <div class="stat-label">API Response (ms)</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Recent Activity Widget -->
        <div class="widget">
            <h3>¡ Recent Activity</h3>
            <div id="recentLoader" class="loading-spinner"></div>
            <div id="recentActivity" style="display: none;"></div>
        </div>
        
        <!-- Topic Analysis Widget -->
        <div class="widget">
            <h3><÷ Topic Analysis</h3>
            <div id="topicsLoader" class="loading-spinner"></div>
            <div class="chart-container">
                <canvas id="topicsChart" style="display: none;"></canvas>
            </div>
        </div>
        
        <!-- Real-time Monitor Widget -->
        <div class="widget">
            <h3>=4 Live Monitor</h3>
            <button id="startMonitoring" onclick="toggleMonitoring()">Start Monitoring</button>
            <div id="monitorStatus" style="margin-top: 10px;"></div>
            <div id="liveUpdates" style="max-height: 300px; overflow-y: auto; margin-top: 15px;"></div>
        </div>
    </div>

    <script type="module">
        import { DanishParliamentAPI } from './danish-parliament-api.js';
        
        const api = new DanishParliamentAPI({ requestDelay: 300 });
        let monitoringInterval = null;
        let isMonitoring = false;
        
        // Initialize dashboard
        async function initializeDashboard() {
            await loadStatistics();
            await loadRecentActivity();
            await loadTopicAnalysis();
        }
        
        // Load basic statistics
        async function loadStatistics() {
            try {
                const startTime = Date.now();
                
                // Get counts for major entities
                const [caseCount, actorCount, recentChanges] = await Promise.all([
                    api.getEntityCount('Sag'),
                    api.getEntityCount('Aktør'),
                    api.getRecentChanges('Sag', 24)
                ]);
                
                const responseTime = Date.now() - startTime;
                
                // Update UI
                document.getElementById('totalCases').textContent = caseCount.toLocaleString();
                document.getElementById('totalActors').textContent = actorCount.toLocaleString();
                document.getElementById('recentUpdates').textContent = recentChanges.value.length;
                document.getElementById('apiResponseTime').textContent = responseTime;
                
                // Show content, hide loader
                document.getElementById('statsLoader').style.display = 'none';
                document.getElementById('statsContent').style.display = 'block';
                
            } catch (error) {
                console.error('Failed to load statistics:', error);
                document.getElementById('statsLoader').innerHTML = '<div style="color: red;">Failed to load</div>';
            }
        }
        
        // Load recent activity
        async function loadRecentActivity() {
            try {
                const recent = await api.getRecentChanges('Sag', 6); // Last 6 hours
                const activityDiv = document.getElementById('recentActivity');
                
                if (recent.value.length === 0) {
                    activityDiv.innerHTML = '<p>No recent activity</p>';
                } else {
                    let html = '';
                    recent.value.slice(0, 5).forEach(case => {
                        const timeAgo = getTimeAgo(new Date(case.opdateringsdato));
                        html += `
                            <div style="padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 6px;">
                                <strong>${case.titel.substring(0, 60)}${case.titel.length > 60 ? '...' : ''}</strong><br>
                                <small style="color: #666;">Updated ${timeAgo}</small>
                            </div>
                        `;
                    });
                    activityDiv.innerHTML = html;
                }
                
                document.getElementById('recentLoader').style.display = 'none';
                activityDiv.style.display = 'block';
                
            } catch (error) {
                console.error('Failed to load recent activity:', error);
                document.getElementById('recentLoader').innerHTML = '<div style="color: red;">Failed to load</div>';
            }
        }
        
        // Load topic analysis
        async function loadTopicAnalysis() {
            try {
                // Search for common topics
                const topics = ['klima', 'miljø', 'økonomi', 'sundhed', 'uddannelse'];
                const results = await Promise.all(
                    topics.map(async topic => {
                        const response = await api.getCases({
                            filter: `substringof('${topic}', titel)`,
                            top: 1
                        });
                        // Get count from a separate query
                        const countResponse = await api.request('Sag', {
                            '$filter': `substringof('${topic}', titel)`,
                            '$inlinecount': 'allpages',
                            '$top': 1
                        });
                        return {
                            topic: topic,
                            count: parseInt(countResponse['odata.count'] || 0)
                        };
                    })
                );
                
                // Create chart
                const ctx = document.getElementById('topicsChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: results.map(r => r.topic.charAt(0).toUpperCase() + r.topic.slice(1)),
                        datasets: [{
                            label: 'Number of Cases',
                            data: results.map(r => r.count),
                            backgroundColor: [
                                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Cases by Topic'
                            }
                        }
                    }
                });
                
                document.getElementById('topicsLoader').style.display = 'none';
                document.getElementById('topicsChart').style.display = 'block';
                
            } catch (error) {
                console.error('Failed to load topic analysis:', error);
                document.getElementById('topicsLoader').innerHTML = '<div style="color: red;">Failed to load</div>';
            }
        }
        
        // Real-time monitoring
        window.toggleMonitoring = function() {
            if (isMonitoring) {
                stopMonitoring();
            } else {
                startMonitoring();
            }
        };
        
        function startMonitoring() {
            isMonitoring = true;
            document.getElementById('startMonitoring').textContent = 'Stop Monitoring';
            document.getElementById('monitorStatus').innerHTML = '<span style="color: green;">=â Monitoring active</span>';
            
            // Check for updates every 30 seconds
            monitoringInterval = setInterval(checkForUpdates, 30000);
            checkForUpdates(); // Initial check
        }
        
        function stopMonitoring() {
            isMonitoring = false;
            document.getElementById('startMonitoring').textContent = 'Start Monitoring';
            document.getElementById('monitorStatus').innerHTML = '<span style="color: #666;">ª Monitoring stopped</span>';
            
            if (monitoringInterval) {
                clearInterval(monitoringInterval);
                monitoringInterval = null;
            }
        }
        
        async function checkForUpdates() {
            try {
                // Check for updates in the last 5 minutes
                const cutoffTime = new Date();
                cutoffTime.setMinutes(cutoffTime.getMinutes() - 5);
                const isoTime = cutoffTime.toISOString().slice(0, 19);
                
                const updates = await api.request('Sag', {
                    '$filter': `opdateringsdato gt datetime'${isoTime}'`,
                    '$orderby': 'opdateringsdato desc',
                    '$top': 10
                });
                
                const updatesDiv = document.getElementById('liveUpdates');
                
                if (updates.value && updates.value.length > 0) {
                    let html = '';
                    updates.value.forEach(case => {
                        const timeAgo = getTimeAgo(new Date(case.opdateringsdato));
                        html += `
                            <div style="padding: 8px; margin: 3px 0; background: #e8f5e8; border-radius: 4px; border-left: 4px solid #4caf50;">
                                <strong>New Update:</strong> ${case.titel.substring(0, 50)}...<br>
                                <small style="color: #666;">${timeAgo}</small>
                            </div>
                        `;
                    });
                    
                    updatesDiv.innerHTML = html + updatesDiv.innerHTML;
                    
                    // Limit to 20 updates
                    const children = updatesDiv.children;
                    while (children.length > 20) {
                        updatesDiv.removeChild(children[children.length - 1]);
                    }
                } else {
                    // Add a "no updates" message occasionally
                    if (Math.random() < 0.2) { // 20% chance
                        const now = new Date().toLocaleTimeString();
                        updatesDiv.innerHTML = `
                            <div style="padding: 8px; margin: 3px 0; background: #f0f0f0; border-radius: 4px; color: #666;">
                                No new updates (checked at ${now})
                            </div>
                        ` + updatesDiv.innerHTML;
                    }
                }
                
            } catch (error) {
                console.error('Error checking for updates:', error);
                document.getElementById('monitorStatus').innerHTML = '<span style="color: red;">L Monitor error</span>';
            }
        }
        
        // Utility function to calculate time ago
        function getTimeAgo(date) {
            const now = new Date();
            const diffInSeconds = Math.floor((now - date) / 1000);
            
            if (diffInSeconds < 60) return `${diffInSeconds} seconds ago`;
            if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
            if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
            return `${Math.floor(diffInSeconds / 86400)} days ago`;
        }
        
        // Initialize dashboard when page loads
        window.addEventListener('load', () => {
            console.log('Parliamentary Dashboard initializing...');
            initializeDashboard();
        });
        
    </script>
</body>
</html>
```

## CORS Configuration

The Danish Parliament API correctly supports CORS:

```javascript
// These headers are returned by the API:
// Access-Control-Allow-Origin: *
// Access-Control-Allow-Methods: GET,POST,PUT,PATCH,MERGE,DELETE
// Access-Control-Allow-Headers: Content-Type

// This means you can make direct requests from any domain
const response = await fetch('https://oda.ft.dk/api/Sag?%24top=5');
const data = await response.json();
```

## Error Handling in Browsers

```javascript
// Browser-specific error handling
class BrowserAPIError extends Error {
    constructor(message, type = 'UNKNOWN') {
        super(message);
        this.name = 'BrowserAPIError';
        this.type = type;
        this.timestamp = new Date().toISOString();
    }
    
    // Display error in user-friendly way
    displayToUser(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="error-message" style="
                    background: #ffebee; 
                    color: #c62828; 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin: 10px 0;
                    border-left: 4px solid #d32f2f;
                ">
                    <strong>Error:</strong> ${this.message}<br>
                    <small>Time: ${new Date(this.timestamp).toLocaleString()}</small>
                </div>
            `;
        }
    }
}

// Enhanced error handling for browser environment
async function safeAPICall(apiCall, errorContainerId = null) {
    try {
        return await apiCall();
    } catch (error) {
        let browserError;
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            browserError = new BrowserAPIError(
                'Network connection failed. Please check your internet connection.',
                'NETWORK_ERROR'
            );
        } else if (error.name === 'AbortError') {
            browserError = new BrowserAPIError(
                'Request took too long and was cancelled.',
                'TIMEOUT_ERROR'
            );
        } else if (error.message.includes('CORS')) {
            browserError = new BrowserAPIError(
                'Cross-origin request blocked. This should not happen with the Danish Parliament API.',
                'CORS_ERROR'
            );
        } else {
            browserError = new BrowserAPIError(error.message, 'API_ERROR');
        }
        
        // Log for debugging
        console.error('API Error:', browserError);
        
        // Display to user if container provided
        if (errorContainerId) {
            browserError.displayToUser(errorContainerId);
        }
        
        throw browserError;
    }
}

// Usage example
async function searchWithErrorHandling() {
    await safeAPICall(
        () => api.getCases({ filter: "substringof('klima', titel)" }),
        'errorContainer'
    );
}
```

## Progressive Web App (PWA) Example

```javascript
// Service Worker for offline functionality (sw.js)
const CACHE_NAME = 'parliament-api-v1';
const CACHE_URLS = [
    '/',
    '/index.html',
    '/danish-parliament-api.js',
    'https://cdn.jsdelivr.net/npm/chart.js'
];

// Install event - cache resources
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(CACHE_URLS))
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
    // Only cache GET requests to our domain or the API
    if (event.request.method === 'GET' && 
        (event.request.url.includes(location.origin) || 
         event.request.url.includes('oda.ft.dk'))) {
        
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    // Return cached version or fetch from network
                    return response || fetch(event.request).then(fetchResponse => {
                        // Cache successful API responses
                        if (fetchResponse.status === 200) {
                            const responseClone = fetchResponse.clone();
                            caches.open(CACHE_NAME)
                                .then(cache => cache.put(event.request, responseClone));
                        }
                        return fetchResponse;
                    });
                })
                .catch(() => {
                    // Return offline page or cached data
                    return caches.match('/offline.html');
                })
        );
    }
});
```

```html
<!-- PWA Manifest (manifest.json) -->
{
    "name": "Danish Parliament Dashboard",
    "short_name": "Parliament",
    "description": "Real-time Danish Parliament data dashboard",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#1976d2",
    "icons": [
        {
            "src": "icon-192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "icon-512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}

<!-- In HTML head -->
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#1976d2">

<!-- Register service worker -->
<script>
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(registration => console.log('SW registered'))
        .catch(error => console.log('SW registration failed'));
}
</script>
```

## Performance Optimization for Browsers

### 1. Request Batching
```javascript
class RequestBatcher {
    constructor(api, batchDelay = 100) {
        this.api = api;
        this.batchDelay = batchDelay;
        this.queue = [];
        this.timeoutId = null;
    }
    
    // Add request to batch
    addRequest(entity, params) {
        return new Promise((resolve, reject) => {
            this.queue.push({ entity, params, resolve, reject });
            
            // Start batch timer if not already running
            if (!this.timeoutId) {
                this.timeoutId = setTimeout(() => this.processBatch(), this.batchDelay);
            }
        });
    }
    
    // Process all queued requests
    async processBatch() {
        const currentQueue = [...this.queue];
        this.queue = [];
        this.timeoutId = null;
        
        // Group similar requests
        const grouped = {};
        currentQueue.forEach(req => {
            const key = `${req.entity}_${JSON.stringify(req.params)}`;
            if (!grouped[key]) {
                grouped[key] = [];
            }
            grouped[key].push(req);
        });
        
        // Execute unique requests
        for (const [key, requests] of Object.entries(grouped)) {
            const firstReq = requests[0];
            
            try {
                const result = await this.api.request(firstReq.entity, firstReq.params);
                
                // Resolve all similar requests with same result
                requests.forEach(req => req.resolve(result));
                
            } catch (error) {
                // Reject all similar requests
                requests.forEach(req => req.reject(error));
            }
        }
    }
}

// Usage
const api = new DanishParliamentAPI();
const batcher = new RequestBatcher(api);

// These will be batched together
const results = await Promise.all([
    batcher.addRequest('Sag', { '$top': 10 }),
    batcher.addRequest('Sag', { '$top': 10 }), // Duplicate - will reuse result
    batcher.addRequest('Aktør', { '$top': 5 })
]);
```

### 2. Caching Strategy
```javascript
class CachedAPI {
    constructor(api, cacheDuration = 300000) { // 5 minutes default
        this.api = api;
        this.cacheDuration = cacheDuration;
        this.cache = new Map();
    }
    
    // Generate cache key
    getCacheKey(entity, params) {
        return `${entity}_${JSON.stringify(params)}`;
    }
    
    // Check if cache entry is valid
    isValidCache(entry) {
        return Date.now() - entry.timestamp < this.cacheDuration;
    }
    
    // Cached request
    async request(entity, params) {
        const key = this.getCacheKey(entity, params);
        const cached = this.cache.get(key);
        
        // Return cached result if valid
        if (cached && this.isValidCache(cached)) {
            console.log('Cache hit:', key);
            return cached.data;
        }
        
        // Fetch from API
        try {
            const result = await this.api.request(entity, params);
            
            // Cache the result
            this.cache.set(key, {
                data: result,
                timestamp: Date.now()
            });
            
            console.log('Cache miss:', key);
            return result;
            
        } catch (error) {
            // Return stale cache if available
            if (cached) {
                console.log('Using stale cache due to error:', key);
                return cached.data;
            }
            throw error;
        }
    }
    
    // Clear expired cache entries
    cleanupCache() {
        for (const [key, entry] of this.cache.entries()) {
            if (!this.isValidCache(entry)) {
                this.cache.delete(key);
            }
        }
    }
}

// Usage
const api = new DanishParliamentAPI();
const cachedApi = new CachedAPI(api);

// Clean up cache every 10 minutes
setInterval(() => cachedApi.cleanupCache(), 600000);
```

## Mobile-Responsive Patterns

```css
/* Mobile-first responsive design */
@media (max-width: 768px) {
    .dashboard {
        grid-template-columns: 1fr;
        padding: 10px;
    }
    
    .widget {
        padding: 15px;
    }
    
    .stat-grid {
        grid-template-columns: 1fr;
    }
    
    .controls input,
    .controls button {
        width: 100%;
        box-sizing: border-box;
        margin: 5px 0;
    }
}

/* Touch-friendly buttons */
.controls button {
    min-height: 44px; /* iOS minimum touch target */
    min-width: 44px;
}
```

```javascript
// Mobile-specific optimizations
class MobileOptimizedAPI extends DanishParliamentAPI {
    constructor(options = {}) {
        super({
            ...options,
            // Longer timeout for mobile networks
            timeout: 45000,
            // More aggressive rate limiting
            requestDelay: 500
        });
        
        this.isMobile = this.detectMobile();
    }
    
    detectMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i
            .test(navigator.userAgent);
    }
    
    // Mobile-optimized pagination (smaller batches)
    async* paginateAll(entity, options = {}) {
        const mobileOptions = {
            ...options,
            batchSize: this.isMobile ? 20 : (options.batchSize || 100)
        };
        
        yield* super.paginateAll(entity, mobileOptions);
    }
}
```

This comprehensive browser usage guide provides everything needed to build powerful client-side applications with the Danish Parliament API, from simple demos to full-featured progressive web apps.