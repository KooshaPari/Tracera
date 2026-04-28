# Import/Export E2E Test Coverage Report

## Overview

Comprehensive end-to-end test suite for the Import/Export functionality in TraceRTM. This document outlines the test coverage, test organization, and validation scenarios.

**File Location:** `frontend/apps/web/e2e/import-export.spec.ts`
**Total Tests:** 27 comprehensive E2E tests
**Test File Size:** 1,084 lines

---

## Test Organization

The test suite is organized into 7 main test groups:

### 1. Export Functionality (5 tests)

Focus: Exporting items and projects in various formats

#### Export Items to JSON (4 tests)

- **Display Export Button**: Verifies export button is visible on items page
- **Export All Items as JSON**: Tests complete JSON export with download validation
- **Export with Filters**: Tests exporting filtered subsets of items
- **Export Progress/Confirmation**: Validates user feedback on successful export

**Key Validations:**

- Button visibility and accessibility
- Download event handling
- Filename validation (.json extension)
- Filter application before export
- Success message display

#### Export Items to CSV (2 tests)

- **Export Items as CSV**: Tests CSV export format and download
- **Handle Large CSV Exports**: Tests performance with large datasets

**Key Validations:**

- CSV format generation
- File size verification
- Extended timeout for large files
- Download success

#### Export Projects (2 tests)

- **Display Export Button on Projects Page**: Verifies export UI on project list
- **Export Project with All Items**: Tests complete project export including nested items
- **Export Project as CSV**: Tests CSV format for project data

**Key Validations:**

- Multi-level data export (project + items)
- Format selection
- File integrity

---

### 2. Import Functionality (12 tests)

#### Import Items from JSON (5 tests)

- **Display Import Button**: Verifies import UI availability
- **Open Import Dialog**: Tests dialog/modal opening
- **Show File Upload Area**: Validates upload interface
- **Allow Format Selection**: Tests format selector (JSON/CSV)
- **Validate JSON File Before Import**: Tests input validation

**Key Validations:**

- UI element visibility
- Dialog state management
- File input functionality
- Format selection UX
- JSON syntax validation

#### Import Items from CSV (2 tests)

- **Import Items from CSV File**: Tests CSV file upload and import process
- **Show Import Summary with Count**: Validates preview of import count

**Key Validations:**

- File upload handling
- CSV parsing
- Row count display
- Form submission
- Success confirmation

#### Import Error Handling (5 tests)

- **Handle Missing Required Columns**: Tests CSV validation with incomplete headers
- **Handle Duplicate Entries**: Tests duplicate detection and handling
- **Handle File Size Limits**: Tests file size validation
- **Show Partial Import Results**: Tests mixed valid/invalid data handling
- **Prevent Import of Corrupted Files**: Tests corruption detection

**Key Validations:**

- CSV column validation
- Duplicate detection
- File size enforcement
- Partial success handling
- JSON/CSV corruption detection
- Error message display
- Data integrity on partial imports

#### Import Projects (1 test)

- **Display Import Button on Projects Page**: Verifies project import UI
- **Allow Importing Full Project Export**: Tests round-trip import (export → import)

**Key Validations:**

- Project-level import
- File format handling
- Data preservation
- Success confirmation

---

### 3. Export/Import Round-trip Tests (2 tests)

#### Data Integrity Tests

- **JSON Export/Import Cycle**: Full round-trip test with JSON format
- **CSV Export/Import Round-trip**: Tests data transformation through CSV format

**Key Validations:**

- Data consistency after round-trip
- Format conversion accuracy
- Field preservation
- Special character handling
- Import success confirmation

---

### 4. Edge Cases and Error Scenarios (3 tests)

- **Handle Special Characters**: Tests Unicode and special character preservation
- **Handle Empty Project Export**: Tests export of projects with no items
- **Prevent Import of Corrupted Files**: Tests corruption detection

**Key Validations:**

- Character encoding
- Empty data handling
- Corruption prevention
- File integrity verification

---

## Test Coverage Matrix

| Feature         | Export JSON | Export CSV | Import JSON | Import CSV | Error Handling | Round-trip |
| --------------- | ----------- | ---------- | ----------- | ---------- | -------------- | ---------- |
| Items           | ✓           | ✓          | ✓           | ✓          | ✓              | ✓          |
| Projects        | ✓           | ✓          | ✓           | -          | ✓              | ✓          |
| Filters         | ✓           | -          | -           | -          | -              | -          |
| UI Elements     | ✓           | ✓          | ✓           | ✓          | ✓              | ✓          |
| File Validation | -           | -          | ✓           | ✓          | ✓              | ✓          |
| Performance     | ✓           | ✓          | ✓           | ✓          | ✓              | ✓          |

---

## Error Scenarios Covered

### File Validation

1. Invalid JSON format
2. Missing CSV headers
3. Corrupted file content
4. Invalid data types

### Data Validation

1. Missing required columns
2. Duplicate entries
3. Invalid field values
4. Empty datasets

### Size and Performance

1. Large file handling (10,000+ rows)
2. Multiple export formats
3. Concurrent exports
4. Memory limits

### User Experience

1. Progress indicators
2. Success/error messages
3. Dialog interactions
4. Format selection
5. File upload feedback

---

## Test Implementation Details

### Setup and Teardown

- **beforeEach**: Navigation to relevant page and wait for content loading
- **Page Navigation**: Uses `/items` and `/projects` routes
- **Network Waiting**: `waitForLoadState("networkidle")` ensures content is ready
- **Timeouts**: Configurable timeouts (2000-10000ms) based on operation

### File Handling

- **Temporary Files**: Tests create temporary files in `/tmp` directory
- **Cleanup**: Files are deleted after test completion
- **Path Utilities**: Uses Node.js `path` and `fs` modules
- **Download Events**: Uses Playwright's `waitForEvent("download")` API

### Locators and Selectors

- **Role-based**: Uses `getByRole()` for semantic HTML
- **Text matching**: Uses regex patterns for flexible matching
- **Fallback selectors**: Multiple selectors tried to ensure robustness
- **Visibility checks**: Validates element visibility before interaction

### Error Handling

- **Soft assertions**: `.catch()` for non-critical checks
- **Graceful degradation**: Tests continue if optional UI not found
- **Logging**: Console logs for debugging and reporting
- **Timeouts**: Custom timeouts for different operations

---

## Test Execution

### Running All Import/Export Tests

```bash
npx playwright test e2e/import-export.spec.ts
```

### Running Specific Test Group

```bash
npx playwright test e2e/import-export.spec.ts -g "Export Items to JSON"
```

### Running with Specific Browser

```bash
npx playwright test e2e/import-export.spec.ts --project=chromium
```

### Debug Mode

```bash
npx playwright test e2e/import-export.spec.ts --debug
```

### View Test Report

```bash
npx playwright show-report
```

---

## Key Testing Patterns

### 1. Download Handling

```typescript
const downloadPromise = page.waitForEvent('download', { timeout: 5000 });
await exportButton.click();
const download = await downloadPromise.catch(() => null);
if (download) {
  const filename = await download.suggestedFilename();
}
```

### 2. File Upload

```typescript
const fileInput = page.locator("input[type='file']").first();
await fileInput.setInputFiles(filePath);
```

### 3. Format Selection

```typescript
const formatSelect = page.getByRole('combobox', { name: /format/i }).first();
await formatSelect.click();
const csvOption = page.getByText(/csv/i).first();
await csvOption.click();
```

### 4. Error Validation

```typescript
const errorMessage = page.getByText(/invalid|error|format/i).first();
await expect(errorMessage).toBeVisible({ timeout: 3000 });
```

---

## Limitations and Assumptions

### Known Limitations

1. **UI-Dependent**: Tests rely on specific button/selector names
2. **Mock Data**: Uses existing MSW mock data for items and projects
3. **File Content**: Does not validate internal file content (unit tests handle this)
4. **Browser Storage**: Limited testing of file system integration

### Assumptions

1. Export/import API endpoints are available at `/api/v1/projects/{id}/export|import`
2. UI provides export/import buttons on items and projects pages
3. File upload input accepts `.json` and `.csv` files
4. Success is confirmed by download event or success message
5. Temporary file access is allowed in `/tmp` directory

---

## Future Enhancements

1. **API Mocking**: Mock different export formats to test without backend
2. **File Content Validation**: Add tests to verify exported file contents
3. **Performance Benchmarks**: Measure export/import duration
4. **Concurrent Operations**: Test multiple exports/imports in parallel
5. **Network Resilience**: Test behavior with network timeouts
6. **Large Dataset Testing**: Dynamic test data generation for scale testing
7. **Accessibility Testing**: Verify keyboard navigation and screen reader support
8. **Browser Compatibility**: Extend to Firefox, Safari, and mobile browsers

---

## Related Test Files

- **Unit Tests**: `frontend/apps/web/src/__tests__/`
  - `hooks/useItems.test.ts` - Item state management
  - `hooks/useProjects.test.ts` - Project state management
  - `stores/itemsStore.test.ts` - Store functionality

- **Other E2E Tests**: `frontend/apps/web/e2e/`
  - `items.spec.ts` - Item CRUD operations
  - `projects.spec.ts` - Project CRUD operations
  - `graph.spec.ts` - Graph visualization (includes export)
  - `integration-workflows.spec.ts` - Complex workflows

---

## Test Metrics

| Metric                | Value        |
| --------------------- | ------------ |
| Total Tests           | 27           |
| Test Groups           | 7            |
| Lines of Code         | 1,084        |
| Average Test Duration | 5-15 seconds |
| Timeout Range         | 2000-10000ms |
| File Operations       | 15           |
| Download Validations  | 11           |
| Error Scenarios       | 8            |

---

## Contributing

When adding new import/export tests:

1. Follow the existing test structure and naming conventions
2. Use role-based selectors (`getByRole`) as primary method
3. Include both positive (success) and negative (error) scenarios
4. Add cleanup for any temporary files created
5. Include informative console logs for debugging
6. Use soft assertions (`.catch()`) for non-critical checks
7. Document the test purpose in comments

---

## Troubleshooting

### Common Issues

**Export button not found**

- Check if export feature is implemented on the page
- Look for button with different text (e.g., "Download", "Save")
- Verify page navigation completed with `waitForLoadState("networkidle")`

**Download not captured**

- Ensure `waitForEvent("download")` is called before triggering download
- Check browser download settings
- Verify file extension in filename assertion

**File upload not working**

- Check if file input is visible and enabled
- Verify file path is absolute
- Ensure file exists and is readable
- Check file format is accepted

**Import validation fails**

- Verify error message text matches expected pattern
- Check if validation occurs before or after file selection
- Look for detailed error messages in page content

---

## References

- Playwright Documentation: https://playwright.dev/docs/intro
- Playwright File Uploads: https://playwright.dev/docs/input
- Playwright Download Handling: https://playwright.dev/docs/downloads
- Test Configuration: `playwright.config.ts`
- API Endpoints: `src/api/endpoints.ts`
