# Equivalence Import/Export Guide

Comprehensive guide for importing and exporting equivalence mappings and canonical concepts.

## Overview

The equivalence import/export system allows you to:

- Export equivalence mappings (links between items)
- Export canonical concepts (abstract entities spanning perspectives)
- Export projections (how canonical concepts manifest in items)
- Import previously exported equivalence data
- Merge or replace existing equivalence data
- Share equivalence mappings across projects

## Components

### 1. EquivalenceExport Component

Export equivalence data with filtering and format options.

```typescript
import { EquivalenceExport } from "@/components/graph/equivalence";

export function MyComponent() {
  return (
    <EquivalenceExport
      equivalenceLinks={links}
      canonicalConcepts={concepts}
      canonicalProjections={projections}
      projectId={projectId}
      userId={currentUserId}
    />
  );
}
```

#### Features

- **Format Selection**: JSON or CSV export
- **Content Filtering**:
  - Include/exclude links, concepts, or projections
  - Filter by confidence threshold (0-100%)
  - Filter by link status (confirmed, suggested, rejected, auto-confirmed)
  - Filter by domain
- **Advanced Options**:
  - Include/exclude confidence scores
  - Include/exclude sources and strategies
- **Export Actions**:
  - Download as file
  - Copy JSON to clipboard
- **Preview**: See export summary before downloading

#### Example Usage

```typescript
<EquivalenceExport
  equivalenceLinks={[
    {
      id: "link-1",
      projectId: "proj-1",
      sourceItemId: "item-1",
      targetItemId: "item-2",
      equivalenceType: "same_as",
      confidence: 0.95,
      strategies: [...],
      status: "confirmed",
      createdAt: "2024-01-15T10:00:00Z",
      updatedAt: "2024-01-15T10:00:00Z",
    },
  ]}
  canonicalConcepts={[
    {
      id: "canon-1",
      projectId: "proj-1",
      name: "User Authentication",
      slug: "user-authentication",
      domain: "security",
      confidence: 0.9,
      source: "manual",
      projectionCount: 3,
      version: 1,
      createdAt: "2024-01-15T10:00:00Z",
      updatedAt: "2024-01-15T10:00:00Z",
    },
  ]}
  canonicalProjections={[...]}
  projectId="proj-1"
  userId="user-1"
/>
```

### 2. EquivalenceImport Component

Import equivalence data from JSON or CSV files.

```typescript
import { EquivalenceImport } from "@/components/graph/equivalence";

export function MyComponent() {
  const handleApplyImport = async (links, concepts, projections) => {
    // Apply imported data to your data store
    await saveEquivalenceData(links, concepts, projections);
  };

  return (
    <EquivalenceImport
      existingLinks={currentLinks}
      existingConcepts={currentConcepts}
      existingProjections={currentProjections}
      projectId={projectId}
      onApplyImport={handleApplyImport}
    />
  );
}
```

#### Features

- **File Selection**: Drag-and-drop or click to select JSON/CSV
- **Validation**: Automatic schema validation
- **Conflict Detection**: Identifies existing items
- **Import Modes**:
  - **Merge**: Combine with existing data
  - **Replace**: Overwrite all existing data
- **Conflict Resolution**:
  - Skip existing items
  - Overwrite with imported data
  - Merge metadata only
- **Options**:
  - Validate references
  - Preserve original timestamps
  - Update project ID to current
- **Preview**: Review what will be imported before applying

#### Example Usage

```typescript
<EquivalenceImport
  existingLinks={currentLinks}
  existingConcepts={currentConcepts}
  existingProjections={currentProjections}
  projectId="proj-1"
  onApplyImport={async (links, concepts, projections) => {
    await api.saveEquivalenceData({
      equivalenceLinks: links,
      canonicalConcepts: concepts,
      canonicalProjections: projections,
    });
  }}
/>
```

## Utility Functions

### Serialization

```typescript
import {
  serializeToJSON,
  serializeToCSV,
  deserializeFromJSON,
  deserializeLinksFromCSV,
  deserializeConceptsFromCSV,
  deserializeProjectionsFromCSV,
} from '@/components/graph/equivalence';

// JSON serialization
const json = serializeToJSON(exportPackage);
const package = deserializeFromJSON(json);

// CSV serialization
const csv = serializeToCSV(exportPackage);
const links = deserializeLinksFromCSV(csv.links);
const concepts = deserializeConceptsFromCSV(csv.concepts);
const projections = deserializeProjectionsFromCSV(csv.projections);
```

### Validation

```typescript
import { validateExportPackage, validateImportOptions } from '@/components/graph/equivalence';

// Validate export package
const { valid, errors } = validateExportPackage(data);
if (!valid) {
  console.error('Validation errors:', errors);
}

// Validate import options
const result = validateImportOptions({
  mode: 'merge',
  conflictResolution: 'skip',
});
```

### Merging

```typescript
import { mergeExportPackages } from '@/components/graph/equivalence';

const merged = mergeExportPackages(existingPackage, incomingPackage, {
  mode: 'merge',
  conflictResolution: 'overwrite',
  validateReferences: true,
  preserveTimestamps: false,
  updateProjectId: true,
  targetProjectId: 'proj-1',
});
```

### Summary

```typescript
import { createExportSummary } from '@/components/graph/equivalence';

const summary = createExportSummary(exportPackage);
console.log(`Total links: ${summary.totalLinks}`);
console.log(`Total concepts: ${summary.totalConcepts}`);
console.log(`Confirmed: ${summary.confirmedCount}`);
console.log(`Average confidence: ${summary.confidenceStats.average}`);
console.log(`Domains: ${Object.keys(summary.domainBreakdown)}`);
console.log(`Strategies: ${Object.keys(summary.strategyBreakdown)}`);
```

## JSON Export Format

```json
{
  "version": "1.0",
  "exportedAt": "2024-01-15T10:00:00Z",
  "projectId": "proj-1",
  "exportedBy": "user-1",
  "metadata": {
    "totalLinks": 5,
    "totalConcepts": 3,
    "totalProjections": 8,
    "confidence": {
      "min": 0.6,
      "max": 1.0,
      "average": 0.88
    }
  },
  "equivalenceLinks": [
    {
      "id": "link-1",
      "projectId": "proj-1",
      "sourceItemId": "item-1",
      "targetItemId": "item-2",
      "equivalenceType": "same_as",
      "confidence": 0.95,
      "strategies": [
        {
          "strategy": "manual_link",
          "confidence": 0.95,
          "details": "User confirmed",
          "detectedAt": "2024-01-15T10:00:00Z",
          "metadata": {}
        }
      ],
      "canonicalId": "canon-1",
      "status": "confirmed",
      "confirmedBy": "user-1",
      "confirmedAt": "2024-01-15T10:05:00Z",
      "createdAt": "2024-01-15T10:00:00Z",
      "updatedAt": "2024-01-15T10:05:00Z"
    }
  ],
  "canonicalConcepts": [
    {
      "id": "canon-1",
      "projectId": "proj-1",
      "name": "User Authentication",
      "slug": "user-authentication",
      "description": "The concept of authenticating users",
      "domain": "security",
      "category": "identity",
      "tags": ["security", "auth"],
      "confidence": 0.9,
      "source": "manual",
      "projectionCount": 3,
      "createdAt": "2024-01-15T10:00:00Z",
      "updatedAt": "2024-01-15T10:00:00Z",
      "version": 1
    }
  ],
  "canonicalProjections": [
    {
      "id": "proj-1",
      "canonicalId": "canon-1",
      "itemId": "item-1",
      "projectId": "proj-1",
      "perspective": "technical",
      "confidence": 0.95,
      "strategy": "manual_link",
      "isConfirmed": true,
      "isRejected": false,
      "confirmedBy": "user-1",
      "confirmedAt": "2024-01-15T10:05:00Z",
      "createdAt": "2024-01-15T10:00:00Z",
      "updatedAt": "2024-01-15T10:05:00Z"
    }
  ]
}
```

## CSV Export Format

### equivalence-links.csv

```csv
id,projectId,sourceItemId,targetItemId,equivalenceType,confidence,strategies,canonicalId,status,confirmedBy,confirmedAt,rejectedReason,createdAt,updatedAt
"link-1","proj-1","item-1","item-2","same_as","0.95","[{""strategy"":""manual_link"",""confidence"":0.95,""details"":""User confirmed"",""detectedAt"":""2024-01-15T10:00:00Z""}]","canon-1","confirmed","user-1","2024-01-15T10:05:00Z","","2024-01-15T10:00:00Z","2024-01-15T10:05:00Z"
```

### canonical-concepts.csv

```csv
id,projectId,name,slug,description,domain,category,tags,embedding,embeddingModel,embeddingUpdatedAt,projectionCount,projectionIds,relatedConceptIds,parentConceptId,childConceptIds,confidence,source,createdBy,createdAt,updatedAt,version
"canon-1","proj-1","User Authentication","user-authentication","The concept of authenticating users","security","identity","security|auth","","","",3,"","","","","0.9","manual","","2024-01-15T10:00:00Z","2024-01-15T10:00:00Z","1"
```

### canonical-projections.csv

```csv
id,canonicalId,itemId,projectId,perspective,confidence,strategy,isConfirmed,isRejected,confirmedBy,confirmedAt,metadata,createdAt,updatedAt
"proj-1","canon-1","item-1","proj-1","technical","0.95","manual_link","true","false","user-1","2024-01-15T10:05:00Z","","2024-01-15T10:00:00Z","2024-01-15T10:05:00Z"
```

## Import/Export Workflow

### Basic Export Workflow

```typescript
import { EquivalenceExport } from "@/components/graph/equivalence";

function ExportButton() {
  return (
    <EquivalenceExport
      equivalenceLinks={links}
      canonicalConcepts={concepts}
      canonicalProjections={projections}
      projectId="proj-1"
      userId="user-1"
    />
  );
}
```

### Basic Import Workflow

```typescript
import { EquivalenceImport } from "@/components/graph/equivalence";

function ImportButton() {
  const handleApply = async (links, concepts, projections) => {
    // 1. Validate in your backend
    // 2. Update your database
    // 3. Sync with UI

    await api.updateEquivalenceData({
      links,
      concepts,
      projections,
    });

    // Refresh data in UI
    await refreshEquivalenceData();
  };

  return (
    <EquivalenceImport
      existingLinks={currentLinks}
      existingConcepts={currentConcepts}
      existingProjections={currentProjections}
      projectId="proj-1"
      onApplyImport={handleApply}
    />
  );
}
```

## Advanced Usage

### Programmatic Export

```typescript
import { serializeToJSON, createExportSummary } from '@/components/graph/equivalence';

async function exportAndUpload() {
  const exportPackage = {
    version: '1.0',
    exportedAt: new Date().toISOString(),
    projectId: 'proj-1',
    equivalenceLinks: links,
    canonicalConcepts: concepts,
    canonicalProjections: projections,
  };

  // Create summary
  const summary = createExportSummary(exportPackage);
  console.log(`Exporting ${summary.totalLinks} links`);

  // Serialize
  const json = serializeToJSON(exportPackage);

  // Upload
  await api.uploadEquivalenceBackup(json);
}
```

### Conditional Filtering

```typescript
function ExportHighConfidenceOnly() {
  // Filter links with >90% confidence
  const highConfidenceLinks = links.filter((l) => l.confidence > 0.9);

  return (
    <EquivalenceExport
      equivalenceLinks={highConfidenceLinks}
      canonicalConcepts={concepts}
      canonicalProjections={projections}
      projectId="proj-1"
    />
  );
}
```

### Cross-Project Import

```typescript
const handleImport = async (links, concepts, projections) => {
  // Map IDs to new project
  const remappedLinks = links.map((l) => ({
    ...l,
    id: generateNewId(),
    projectId: targetProjectId,
  }));

  const remappedConcepts = concepts.map((c) => ({
    ...c,
    id: generateNewId(),
    projectId: targetProjectId,
  }));

  await api.importEquivalenceData({
    links: remappedLinks,
    concepts: remappedConcepts,
    projections: projections.map((p) => ({
      ...p,
      id: generateNewId(),
      projectId: targetProjectId,
    })),
  });
};
```

## Type Definitions

### EquivalenceExportProps

```typescript
interface EquivalenceExportProps {
  equivalenceLinks: EquivalenceLink[];
  canonicalConcepts: CanonicalConcept[];
  canonicalProjections: CanonicalProjection[];
  projectId: string;
  userId?: string;
}
```

### EquivalenceImportProps

```typescript
interface EquivalenceImportProps {
  existingLinks: EquivalenceLink[];
  existingConcepts: CanonicalConcept[];
  existingProjections: CanonicalProjection[];
  projectId: string;
  onApplyImport?: (
    links: EquivalenceLink[],
    concepts: CanonicalConcept[],
    projections: CanonicalProjection[],
  ) => void | Promise<void>;
  isLoading?: boolean;
}
```

### EquivalenceExportPackage

```typescript
interface EquivalenceExportPackage {
  version: '1.0';
  exportedAt: string;
  projectId: string;
  exportedBy?: string;
  metadata?: {
    totalLinks: number;
    totalConcepts: number;
    totalProjections: number;
    confidence: {
      min: number;
      max: number;
      average: number;
    };
  };
  equivalenceLinks: EquivalenceLink[];
  canonicalConcepts: CanonicalConcept[];
  canonicalProjections: CanonicalProjection[];
}
```

### EquivalenceImportOptions

```typescript
interface EquivalenceImportOptions {
  mode: 'replace' | 'merge';
  conflictResolution: 'skip' | 'overwrite' | 'merge_metadata';
  validateReferences: boolean;
  preserveTimestamps: boolean;
  updateProjectId: boolean;
  targetProjectId?: string;
}
```

## Error Handling

```typescript
import { validateExportPackage } from '@/components/graph/equivalence';

try {
  const json = await file.text();
  const data = JSON.parse(json);

  const validation = validateExportPackage(data);
  if (!validation.valid) {
    // Handle validation errors
    console.error('Validation failed:', validation.errors);
    throw new Error(validation.errors.join(', '));
  }

  // Proceed with import
} catch (error) {
  console.error('Import failed:', error);
  showErrorNotification(error.message);
}
```

## Performance Considerations

- Large exports (>10MB) may require streaming
- CSV parsing is slower than JSON for large datasets
- Validation happens client-side before import
- Consider batching large imports to the backend
- Use filtered exports for sharing to reduce file size

## Security Notes

- All import/export happens client-side
- Validate all imported data on the backend
- Sanitize IDs and project references during import
- Consider rate-limiting bulk imports
- Log all import/export operations

## Best Practices

1. **Regular Exports**: Export equivalence data regularly for backup
2. **Filtered Exports**: Use minimum confidence filter to export only validated mappings
3. **Conflict Review**: Always review conflicts before import
4. **Merge Mode**: Use merge mode to preserve existing data
5. **Validation**: Enable reference validation during import
6. **Timestamps**: Preserve original timestamps for audit trails
7. **Project IDs**: Update project IDs when importing to new projects
8. **Testing**: Test imports on non-production projects first
9. **Backup**: Keep backups of critical equivalence mappings
10. **Documentation**: Document custom domains and categories in exports
