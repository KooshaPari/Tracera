# Equivalence Import/Export Implementation

Complete implementation of import/export functionality for equivalence mappings and canonical concepts.

## Files Created

### 1. Components

#### EquivalenceExport.tsx
Export component for equivalence data with advanced filtering and format options.

**Location:** `/src/components/graph/EquivalenceExport.tsx`

**Key Features:**
- Export to JSON or CSV format
- Filter by confidence threshold (0-100%)
- Filter by link status (confirmed, suggested, rejected, auto-confirmed)
- Filter by domain
- Include/exclude confidence scores and sources
- Export summary with preview
- Copy JSON to clipboard
- Download files directly

**Props:**
```typescript
interface EquivalenceExportProps {
  equivalenceLinks: EquivalenceLink[];
  canonicalConcepts: CanonicalConcept[];
  canonicalProjections: CanonicalProjection[];
  projectId: string;
  userId?: string;
}
```

**Usage:**
```typescript
import { EquivalenceExport } from "@/components/graph";

<EquivalenceExport
  equivalenceLinks={links}
  canonicalConcepts={concepts}
  canonicalProjections={projections}
  projectId={projectId}
  userId={userId}
/>
```

#### EquivalenceImport.tsx
Import component for equivalence data with validation and conflict resolution.

**Location:** `/src/components/graph/EquivalenceImport.tsx`

**Key Features:**
- Import from JSON or CSV files
- Drag-and-drop file selection
- Schema validation with error display
- Conflict detection and reporting
- Merge vs replace modes
- Conflict resolution options (skip, overwrite, merge_metadata)
- Reference validation
- Timestamp preservation options
- Project ID updating
- Import preview before applying

**Props:**
```typescript
interface EquivalenceImportProps {
  existingLinks: EquivalenceLink[];
  existingConcepts: CanonicalConcept[];
  existingProjections: CanonicalProjection[];
  projectId: string;
  onApplyImport?: (
    links: EquivalenceLink[],
    concepts: CanonicalConcept[],
    projections: CanonicalProjection[]
  ) => void | Promise<void>;
  isLoading?: boolean;
}
```

**Usage:**
```typescript
import { EquivalenceImport } from "@/components/graph";

<EquivalenceImport
  existingLinks={currentLinks}
  existingConcepts={currentConcepts}
  existingProjections={currentProjections}
  projectId={projectId}
  onApplyImport={async (links, concepts, projections) => {
    await api.updateEquivalenceData({links, concepts, projections});
  }}
/>
```

### 2. Utilities

#### equivalenceIO.ts
Core serialization, validation, and merge utilities.

**Location:** `/src/components/graph/utils/equivalenceIO.ts`

**Exported Functions:**

**Serialization:**
- `serializeToJSON(data)` - Serialize to JSON string
- `deserializeFromJSON(json)` - Deserialize from JSON string
- `serializeToCSV(data)` - Serialize to CSV format (returns links, concepts, projections)
- `deserializeLinksFromCSV(csv)` - Parse CSV back to EquivalenceLink[]
- `deserializeConceptsFromCSV(csv)` - Parse CSV back to CanonicalConcept[]
- `deserializeProjectionsFromCSV(csv)` - Parse CSV back to CanonicalProjection[]

**Validation:**
- `validateExportPackage(data)` - Validate export package structure
- `validateImportOptions(options)` - Validate import options

**Processing:**
- `mergeExportPackages(existing, incoming, options)` - Merge two export packages
- `createExportSummary(data)` - Generate export summary with statistics

**Schemas (Zod):**
- `EquivalenceEvidenceSchema`
- `EquivalenceLinkSchema`
- `CanonicalConceptSchema`
- `CanonicalProjectionSchema`
- `EquivalenceExportPackageSchema`
- `EquivalenceImportOptionsSchema`

### 3. Export Index

#### equivalence/index.ts
Central export file for all equivalence import/export functionality.

**Location:** `/src/components/graph/equivalence/index.ts`

**Exports:**
- `EquivalenceExport` component
- `EquivalenceImport` component
- All utility functions
- Type definitions

### 4. Tests

#### equivalenceIO.test.ts
Comprehensive test suite for serialization, validation, and merging.

**Location:** `/src/__tests__/equivalenceIO.test.ts`

**Test Coverage:**
- Serialization (JSON, CSV, roundtrip)
- Deserialization
- Validation
- Schema enforcement
- Merging strategies
- Conflict resolution
- Summary generation
- Status counting
- Domain breakdown
- Strategy breakdown

**Test Results:** 31 tests, all passing

### 5. Documentation

#### EQUIVALENCE_IO_GUIDE.md
Comprehensive user guide for import/export functionality.

**Location:** `/src/components/graph/EQUIVALENCE_IO_GUIDE.md`

**Contents:**
- Component overview and features
- Utility function reference
- JSON export format specification
- CSV export format specification
- Basic and advanced usage workflows
- Type definitions
- Error handling
- Performance considerations
- Security notes
- Best practices

## Architecture

### Data Flow

#### Export Flow
```
Component State (links, concepts, projections)
    ↓
Filter/Selection (confidence, status, domain)
    ↓
Export Package Creation
    ↓
Format Conversion (JSON or CSV)
    ↓
File Download or Clipboard
```

#### Import Flow
```
File Selection (JSON or CSV)
    ↓
Parse File Content
    ↓
Schema Validation
    ↓
Conflict Detection
    ↓
Merge/Replace Strategy
    ↓
Import Preview
    ↓
Apply Changes
    ↓
Callback to Handler
```

### Key Design Decisions

1. **Client-Side Processing**
   - All serialization/deserialization happens in the browser
   - No server round-trips for format conversion
   - Validation schemas ensure consistency

2. **Zod Validation**
   - Schema-based validation with helpful error messages
   - Type-safe deserialization
   - Extensible validation rules

3. **Flexible Merging**
   - Support for merge and replace modes
   - Configurable conflict resolution
   - Ability to update project IDs during import
   - Preservation of original timestamps option

4. **Comprehensive Filtering**
   - Export filtering by confidence, status, and domain
   - Granular control over what data is exported
   - Export summaries for preview

5. **Format Support**
   - JSON for complete data with metadata
   - CSV for spreadsheet compatibility
   - Both formats support roundtrip conversion

## Integration Guide

### Basic Integration

```typescript
import { EquivalenceExport, EquivalenceImport } from "@/components/graph/equivalence";

function MyComponent() {
  const [links, setLinks] = useState<EquivalenceLink[]>([]);
  const [concepts, setConcepts] = useState<CanonicalConcept[]>([]);
  const [projections, setProjections] = useState<CanonicalProjection[]>([]);

  const handleImport = async (newLinks, newConcepts, newProjections) => {
    // Update state or call API
    setLinks(newLinks);
    setConcepts(newConcepts);
    setProjections(newProjections);

    // Or call backend API
    await api.updateEquivalenceData({
      equivalenceLinks: newLinks,
      canonicalConcepts: newConcepts,
      canonicalProjections: newProjections,
    });
  };

  return (
    <div className="space-y-4">
      <EquivalenceExport
        equivalenceLinks={links}
        canonicalConcepts={concepts}
        canonicalProjections={projections}
        projectId={projectId}
        userId={userId}
      />

      <EquivalenceImport
        existingLinks={links}
        existingConcepts={concepts}
        existingProjections={projections}
        projectId={projectId}
        onApplyImport={handleImport}
      />
    </div>
  );
}
```

### Advanced Integration

```typescript
import {
  serializeToJSON,
  deserializeFromJSON,
  mergeExportPackages,
  createExportSummary,
  validateExportPackage,
} from "@/components/graph/equivalence";

async function syncEquivalenceData(sourceProject, targetProject) {
  // Export from source
  const sourceExport = {
    version: "1.0",
    exportedAt: new Date().toISOString(),
    projectId: sourceProject.id,
    equivalenceLinks: sourceProject.links,
    canonicalConcepts: sourceProject.concepts,
    canonicalProjections: sourceProject.projections,
  };

  // Create summary
  const summary = createExportSummary(sourceExport);
  console.log(`Syncing ${summary.totalLinks} links...`);

  // Import to target with validation
  const validation = validateExportPackage(sourceExport);
  if (!validation.valid) {
    throw new Error(`Validation failed: ${validation.errors.join(", ")}`);
  }

  // Merge with existing data
  const merged = mergeExportPackages(
    targetProject.exportPackage,
    sourceExport,
    {
      mode: "merge",
      conflictResolution: "overwrite",
      validateReferences: true,
      updateProjectId: true,
      targetProjectId: targetProject.id,
    }
  );

  // Apply changes
  await api.updateEquivalenceData(merged);
}
```

## Type Safety

All components and utilities are fully typed with TypeScript. Key types:

```typescript
// From @tracertm/types
interface EquivalenceLink { ... }
interface CanonicalConcept { ... }
interface CanonicalProjection { ... }

// From equivalenceIO.ts
interface EquivalenceExportPackage { ... }
interface EquivalenceImportOptions { ... }
```

## Error Handling

### Validation Errors
```typescript
const result = validateExportPackage(data);
if (!result.valid) {
  result.errors.forEach(error => {
    console.error(`Validation error: ${error}`);
  });
}
```

### Import Errors
```typescript
const { EquivalenceImport } = await import("@/components/graph/equivalence");

// Errors are displayed in the import dialog
// Check the validationErrors state for details
```

### Deserialization Errors
```typescript
try {
  const data = deserializeFromJSON(json);
} catch (error) {
  console.error("Failed to parse JSON:", error.message);
}
```

## Performance

- Serialization/deserialization: O(n) where n is number of items
- CSV parsing: Optimized line-by-line parsing with quoted field handling
- Validation: Zod schema validation is fast for typical datasets
- Large datasets (>10MB): Consider streaming or batching

## Browser Compatibility

- All modern browsers (Chrome, Firefox, Safari, Edge)
- File API support required for import
- Blob API support required for export

## Testing

Run tests:
```bash
cd frontend/apps/web
bun run test -- src/__tests__/equivalenceIO.test.ts
```

Test coverage: 31 tests covering:
- JSON serialization/deserialization
- CSV serialization/deserialization
- Schema validation
- Package merging
- Conflict resolution
- Summary generation

## Limitations & Future Enhancements

### Current Limitations
- CSV export requires multiple files (one per entity type)
- Large exports (>10MB) require manual chunking
- No built-in compression

### Future Enhancements
- Streaming import for large files
- Batch import API endpoints
- Compression support (gzip)
- Differential/delta exports
- Scheduled automated exports
- Multi-format support (XML, protobuf)
- Import scheduling and automation
- Equivalence data comparison tool
- Visual diff viewer

## Security Considerations

1. **Validation:** All imported data is validated against Zod schemas
2. **Project Isolation:** Project IDs are explicitly managed during import
3. **Audit Trail:** Keep logs of all import/export operations
4. **Sensitive Data:** Be careful with equivalence data containing sensitive info
5. **Backend Validation:** Always validate again on the backend

## Contributing

To extend the equivalence import/export system:

1. Add new validation rules to schemas in `equivalenceIO.ts`
2. Update tests in `equivalenceIO.test.ts`
3. Document changes in `EQUIVALENCE_IO_GUIDE.md`
4. Ensure TypeScript compilation passes
5. Ensure all tests pass

## Support

For issues or questions:
1. Check `EQUIVALENCE_IO_GUIDE.md` for usage
2. Review test cases for examples
3. Check error messages for validation issues
4. Review browser console for detailed errors
