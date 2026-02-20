# Mock Data Population Script

This script populates the "TraceRTM Core" and "Mobile App" projects with comprehensive mock data (1000+ entities each).

## What it creates:

### TraceRTM Core (~1000 items):

- 100 Requirements
- 150 Features
- 200 Code modules (Python, TypeScript, JavaScript with code snippets)
- 200 Test cases
- 100 API endpoints
- 100 Database schemas (SQL snippets)
- 50 Wireframes
- 50 Documentation items
- 50 Deployment configurations
- ~500+ traceability links

### Mobile App (~830 items):

- 80 Requirements
- 120 Features
- 150 React Native components (TypeScript with code snippets)
- 150 Test cases
- 80 API endpoints
- 50 Database schemas
- 100 Wireframes
- 50 Documentation items
- 50 Deployment configurations
- ~400+ traceability links

## Usage:

```bash
# Make sure your backend API is running on http://localhost:8000
# (or set VITE_API_URL environment variable)

cd frontend/apps/web
bun run populate:mock
```

## Requirements:

- Backend API server must be running
- Projects "TraceRTM Core" and "Mobile App" will be created if they don't exist
- Script includes retry logic and progress indicators
- Takes several minutes to complete (creates 1800+ items and 900+ links)

## Features:

- Realistic code snippets in descriptions
- Proper parent-child relationships
- Traceability links (implements, tests, depends_on)
- Random statuses and priorities
- Progress indicators every 10 items
- Error handling with retries
