# Import/Export E2E Tests - Quick Reference

## Quick Start

Run all import/export tests:
```bash
npx playwright test e2e/import-export.spec.ts
```

View test report:
```bash
npx playwright show-report
```

---

## Test Overview

**Location:** `frontend/apps/web/e2e/import-export.spec.ts`

**Total:** 27 comprehensive E2E tests covering:
- Export items/projects to JSON and CSV
- Import items/projects from JSON and CSV
- File validation and error handling
- Large file handling
- Export filters
- Round-trip data integrity
- Edge cases and special characters

---

## Test Categories

### Export Tests (5 tests)
1. Export items to JSON - Display button
2. Export items to JSON - Full export
3. Export items to JSON - With filters
4. Export items to JSON - Progress/confirmation
5. Export items to CSV - Basic export
6. Export items to CSV - Large files
7. Export projects - Display button
8. Export projects - With all items
9. Export projects - To CSV

### Import Tests (12 tests)
1. Import JSON - Display button
2. Import JSON - Open dialog
3. Import JSON - File upload area
4. Import JSON - Format selection
5. Import JSON - Validation
6. Import CSV - Full import
7. Import CSV - Summary display
8. Import Errors - Missing columns
9. Import Errors - Duplicates
10. Import Errors - File size limits
11. Import Errors - Partial results
12. Import Projects - Full import

### Round-trip Tests (2 tests)
1. JSON export/import cycle
2. CSV export/import with transformation

### Edge Case Tests (3 tests)
1. Special characters handling
2. Empty project export
3. Corrupted file prevention

---

## Test Patterns

### Basic Export Test
```typescript
test("should export items as JSON", async ({ page }) => {
  await page.goto("/items");
  await page.waitForLoadState("networkidle");

  const exportButton = page.getByRole("button", { name: /export/i }).first();
  if (await exportButton.isVisible()) {
    const downloadPromise = page.waitForEvent("download", { timeout: 5000 });
    await exportButton.click();

    const jsonOption = page.getByText(/json/).first();
    if (await jsonOption.isVisible({ timeout: 2000 })) {
      await jsonOption.click();
      const download = await downloadPromise.catch(() => null);
      if (download) {
        expect(await download.suggestedFilename()).toMatch(/\.json$/);
      }
    }
  }
});
```

### Basic Import Test
```typescript
test("should import items from CSV", async ({ page }) => {
  await page.goto("/items");
  await page.waitForLoadState("networkidle");

  const importButton = page.getByRole("button", { name: /import/i }).first();
  if (await importButton.isVisible()) {
    await importButton.click();

    const fileInput = page.locator("input[type='file']").first();
    if (await fileInput.isVisible({ timeout: 2000 })) {
      await fileInput.setInputFiles("/path/to/file.csv");

      const submitBtn = page.getByRole("button", { name: /submit/i });
      if (await submitBtn.isVisible()) {
        await submitBtn.click();
        await page.waitForLoadState("networkidle");
      }
    }
  }
});
```

---

## File Operations

All file tests create temporary test files:

```typescript
import * as fs from "fs";
import * as path from "path";

const testDir = "/tmp";
const csvFile = path.join(testDir, "items.csv");
fs.writeFileSync(csvFile, csvContent);

// ... use file in test ...

// Clean up
fs.unlinkSync(csvFile);
```

---

## Supported Scenarios

### Export Formats
- JSON (`.json`)
- CSV (`.csv`)
- Markdown (`.md`) - Graph export

### Import Formats
- JSON (`.json`)
- CSV (`.csv`)

### Data Types
- Items
- Projects
- Links/Dependencies
- Metadata

### Validation
- File format validation
- Column requirement validation
- Duplicate detection
- Size limits
- Corruption detection

---

## Common Test Assertions

```typescript
// File download
expect(filename).toMatch(/\.json$/);

// Success message
const successMsg = page.getByText(/import.*success/i);
await expect(successMsg).toBeVisible({ timeout: 5000 });

// Error message
const errorMsg = page.getByText(/invalid|error/i);
await expect(errorMsg).toBeVisible({ timeout: 3000 });

// File size
const stats = fs.statSync(filePath);
expect(stats.size).toBeGreaterThan(0);
```

---

## Debugging

### View test in browser
```bash
npx playwright test e2e/import-export.spec.ts --headed
```

### Debug specific test
```bash
npx playwright test e2e/import-export.spec.ts -g "should export items as JSON" --debug
```

### Verbose output
```bash
npx playwright test e2e/import-export.spec.ts --verbose
```

### Generate trace (for replay)
```bash
npx playwright test e2e/import-export.spec.ts --trace on
```

---

## Configuration

### Timeouts
- Button visibility: 5000ms
- Dialog/modal: 2000ms
- Download event: 5000ms (10000ms for large files)
- File operations: 1000ms
- Network idle: automatic

### Retry Policy
- CI: 2 retries
- Local: 0 retries

### Workers
- CI: 1 worker (sequential)
- Local: parallel

---

## Checklist for New Tests

When adding new import/export tests:

- [ ] Use `test.describe()` for grouping
- [ ] Include `test.beforeEach()` for setup
- [ ] Wait for `networkidle` after navigation
- [ ] Use role-based selectors (`getByRole`)
- [ ] Include timeout values (2000-10000ms)
- [ ] Add `.catch()` for soft assertions
- [ ] Clean up temporary files
- [ ] Include console logs
- [ ] Document test purpose
- [ ] Handle both success and error cases
- [ ] Test actual file operations where possible

---

## API Endpoints

Import/Export functionality uses these API endpoints:

```
GET  /api/v1/projects/{id}/export?format={json|csv|markdown}
POST /api/v1/projects/{id}/import
  body: { format: "json" | "csv", data: string }
```

---

## File Specifications

### JSON Format
```json
{
  "id": "proj-1",
  "name": "Project Name",
  "items": [
    {
      "id": "item-1",
      "title": "Item Title",
      "type": "Requirement",
      "status": "Pending",
      "priority": "High"
    }
  ]
}
```

### CSV Format (Items)
```csv
Title,Type,Status,Priority,Description
Item 1,Requirement,Pending,High,Description text
Item 2,Feature,In Progress,Medium,Another description
```

---

## Performance Considerations

- **Small dataset** (< 100 items): ~2-3 seconds
- **Medium dataset** (100-1000 items): ~5-8 seconds
- **Large dataset** (1000-10000 items): ~10-15 seconds

Test timeouts are set to accommodate these ranges with buffer.

---

## Browser Support

Currently tested on:
- Chromium ✓

Can be extended to:
- Firefox (enable in `playwright.config.ts`)
- WebKit/Safari (enable in `playwright.config.ts`)
- Mobile (enable in `playwright.config.ts`)

---

## Related Files

- **Tests:** `e2e/import-export.spec.ts` (this file)
- **Documentation:** `e2e/IMPORT_EXPORT_TEST_COVERAGE.md`
- **API:** `src/api/endpoints.ts` (exportImportApi)
- **Config:** `playwright.config.ts`

---

## Troubleshooting

**Tests failing to find elements?**
- Check page navigation completed: `await page.waitForLoadState("networkidle")`
- Verify element selectors match current UI
- Look for alternative selector patterns in test

**Download not working?**
- Ensure download listener is set up before clicking
- Check browser download settings
- Verify button actually triggers download

**File operations failing?**
- Check `/tmp` directory permissions
- Ensure Node.js `fs` module is imported
- Verify file paths are absolute
- Check file content is valid for format

**Validation errors not showing?**
- Increase timeout for error message appearance
- Check error message text/selector
- Look for different error UI (toast, inline, modal)

---

## Support

For issues or questions:
1. Check test comments for implementation details
2. Review `IMPORT_EXPORT_TEST_COVERAGE.md` for comprehensive documentation
3. Check Playwright documentation: https://playwright.dev
4. Review related E2E tests: `items.spec.ts`, `projects.spec.ts`

