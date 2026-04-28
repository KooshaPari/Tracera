# Mock Data Generation Library

This library provides a modular, extensible system for generating comprehensive, realistic mock data for TraceRTM projects.

## Module Structure

### `types.ts`

Core type definitions for the mock data system:

- `ItemType`, `ItemStatus`, `ItemPriority`, `LinkType` - Item and link enumerations
- `ProjectConfig` - Project configuration interface
- `ItemsByType` - Organized collection of items by type
- `Project` - Project entity interface

### `data.ts`

Content and code snippets for realistic mock data:

- **Code Snippets**: Sample code in Python, TypeScript, JavaScript, and SQL
- **Descriptions**: Realistic descriptions for:
  - Requirements (functional requirements, system properties)
  - Features (user-facing capabilities)
  - Code (implementation details)
  - Tests (testing coverage areas)
  - APIs (endpoint descriptions)
  - Database (schema and optimization)

### `projects.ts`

Pre-configured project templates:

- **8 Diverse Projects**: Full-stack, mobile, data, DevOps, AI, frontend, backend, integration
- **Per-Project Configuration**: Item counts for each type (requirements, features, code, tests, etc.)
- **Helper Functions**: `getTotalItemCount()`, `getProjectStats()`

### `api.ts`

HTTP client utilities for API communication:

- `createItemWithRetry()` - Create items with exponential backoff
- `createLinkWithRetry()` - Create traceability links with retry logic
- `checkProjectItems()` - Query existing item count
- `fetchProjects()` - List all projects
- `createProject()` - Create a new project
- `getApiUrl()` - Get configured API endpoint

### `generator.ts`

Core mock data generation logic:

- `randomChoice()` - Select random element from array
- `createItemsBatch()` - Create items in parallel batches
- `createItemsByType()` - Generate all item types for a project
- `createTraceabilityLinks()` - Generate realistic item relationships
  - Requirement → Feature (implements)
  - Feature → Code (implements)
  - Code → Test (tests)
  - Code → Database (depends_on)
  - API → Code (depends_on)
  - Feature → Wireframe (relates_to)

### `populator.ts`

High-level project population orchestrator:

- `populateProject()` - Main function to populate a single project with all data types

## Usage

### Basic Usage

```bash
bun run populate-mock-data.ts
```

### Environment Variables

```bash
VITE_API_URL=http://localhost:8000 bun run populate-mock-data.ts
```

### Output

The script generates:

- 8 complete projects
- ~3,850 total data entities (requirements, features, code, tests, APIs, databases, wireframes, documentation, deployments)
- ~1,100+ traceability links
- Realistic relationships between items (30% link ratio)

## Project Breakdown

| Project                          | Domain    | Items | Focus                     |
| -------------------------------- | --------- | ----- | ------------------------- |
| TraceRTM Core Platform           | fullstack | 1,350 | Enterprise traceability   |
| React Native Mobile Client       | mobile    | 920   | Cross-platform mobile     |
| Data Analytics & Insights Engine | data      | 1,140 | Real-time analytics       |
| Infrastructure & DevOps          | devops    | 780   | Kubernetes deployment     |
| AI-Powered Recommendations       | ai        | 925   | ML models                 |
| Frontend Web Application v2      | frontend  | 1,200 | Web interface             |
| Backend API Gateway              | backend   | 1,040 | GraphQL/REST gateway      |
| Integration Platform             | backend   | 815   | Multi-vendor integrations |

## Extending the Library

### Add New Project

```typescript
// In projects.ts
const PROJECTS: ProjectConfig[] = [
  // ... existing projects
  {
    name: 'My New Project',
    description: 'Project description',
    domain: 'backend',
    itemCounts: {
      requirements: 100,
      features: 150,
      code: 200,
      // ... etc
    },
  },
];
```

### Add New Descriptions

```typescript
// In data.ts
export const descriptions = {
  // ... existing descriptions
  myNewType: [
    'Description 1',
    'Description 2',
    // ... etc
  ],
};
```

### Add New Link Types

```typescript
// In types.ts
export type LinkType = 'implements' | 'tests' | 'depends_on' | 'relates_to' | 'my_new_type'; // Add here

// Then in generator.ts createTraceabilityLinks()
// Add link creation logic
```

## Features

### High Quality Data

- ✅ Realistic, contextual descriptions
- ✅ Domain-specific code snippets
- ✅ Proper technical terminology
- ✅ Enterprise standards focus

### Realistic Relationships

- ✅ Requirement → Feature → Code → Test chain
- ✅ Code depends on Database
- ✅ APIs depend on Code
- ✅ Features relate to Wireframes
- ✅ ~30% link ratio (1 link per 3+ items)

### Performance

- ✅ Batch processing (25-item batches)
- ✅ Parallel batch execution
- ✅ Rate limit handling
- ✅ Automatic retry with exponential backoff
- ✅ Efficient bulk operation headers

### Scalability

- ✅ Handles 10,000+ items
- ✅ Configurable batch sizes
- ✅ Project-specific configurations
- ✅ Incremental population

## Troubleshooting

### Rate Limiting

If you see rate limit warnings, the script automatically backs off and retries. Increase sleep delays if needed:

```typescript
// In generator.ts
const batchSize = 10; // Reduce batch size
```

### API Connection

Ensure API is running and accessible:

```bash
curl http://localhost:8000/api/v1/projects
```

### Database Connection

Check backend logs for database connection issues. Mock data requires a functional database backend.

## Performance Notes

- Full population typically takes 5-10 minutes depending on network latency
- API rate limiting defaults to 50ms between items
- Batch processing creates items in parallel (25 at a time)
- Links are created in batches of 50 for efficiency
