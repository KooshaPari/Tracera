# Target 10 Services - Quick Analysis

**Date:** 2026-02-12
**Purpose:** Pre-annotation analysis for rapid FR extraction

---

## Service Capabilities Summary

### 1. import_service.py ✅
**Purpose:** Import TraceRTM data from JSON format
**Key Methods:**
- `import_from_json()` - Import project, items, and links from JSON

**Functional Areas:**
- Data Import (FR-IMPORT category)
- Project/Item/Link creation
- JSON parsing and validation

**Potential FR:** FR-IMPORT-001: JSON Data Import
**Epic:** EPIC-001 (External Integration)

---

### 2. export_service.py ✅
**Purpose:** Export TraceRTM data to JSON/CSV formats
**Key Methods:**
- `export_to_json()` - Export project to JSON
- `export_to_csv()` (likely exists)

**Functional Areas:**
- Data Export (FR-EXPORT category)
- Multiple format support
- Project serialization

**Potential FR:** FR-EXPORT-001: Multi-Format Export
**Epic:** EPIC-008 (Reporting & Analytics)

---

### 3. link_service.py ✅
**Purpose:** Stub service for unit tests (minimal functionality)
**Key Methods:**
- `list_links()` - Returns empty list (test stub)

**Functional Areas:**
- Test infrastructure
- Link management interface

**Potential FR:** FR-LINK-001: Link Management (when implemented)
**Epic:** EPIC-006 (Application & Tracking)
**Note:** Currently a test stub, may need real implementation

---

### 4. item_service.py ✅
**Purpose:** Core item CRUD operations
**Key Methods:**
- `create_item()` (inferred from CreateItemInput)
- `list_items()` (inferred from ListItemsParams)
- Item update/delete operations

**Functional Areas:**
- Item lifecycle management (FR-ITEM category)
- Metadata handling
- Status/priority management
- Concurrency control

**Potential FR:** FR-ITEM-001: Item CRUD Operations
**Epic:** EPIC-006 (Application & Tracking)

---

### 5. graph_service.py ✅
**Purpose:** Graph projection and retrieval
**Key Methods:**
- `get_graph()` - Retrieve graph with nodes/links

**Functional Areas:**
- Graph visualization data (FR-GRAPH category)
- Node/link projection
- Multiple graph types

**Potential FR:** FR-GRAPH-001: Graph Data Retrieval
**Epic:** EPIC-008 (Reporting & Analytics)

---

### 6. graph_analysis_service.py ✅
**Purpose:** Graph analysis algorithms
**Functional Areas:**
- Dependency analysis
- Critical path detection
- Cycle detection
- Impact analysis

**Potential FR:** FR-GRAPH-002: Graph Analysis Algorithms
**Epic:** EPIC-005 (Qualification & Analysis)

---

### 7. impact_analysis_service.py ✅
**Purpose:** Impact analysis for requirement changes
**Functional Areas:**
- Change impact assessment (FR-IMPACT category)
- Dependency traversal
- Affected item identification

**Potential FR:** FR-IMPACT-001: Change Impact Analysis
**Epic:** EPIC-005 (Qualification & Analysis)

---

### 8. traceability_service.py ✅
**Purpose:** Core traceability operations
**Functional Areas:**
- Traceability link management (FR-TRACE category)
- Coverage analysis
- Validation rules

**Potential FR:** FR-TRACE-001: Traceability Operations
**Epic:** EPIC-006 (Application & Tracking)

---

### 9. traceability_matrix_service.py ✅
**Purpose:** Traceability matrix generation
**Functional Areas:**
- Matrix generation (FR-MATRIX category)
- Coverage reporting
- Relationship visualization

**Potential FR:** FR-MATRIX-001: Traceability Matrix Generation
**Epic:** EPIC-008 (Reporting & Analytics)

---

### 10. specification_service.py ❌
**Status:** File does not exist
**FR Mapping:** FR-QUAL-002 already exists in FUNCTIONAL_REQUIREMENTS.md
**Action:** Skip or investigate if file was renamed

---

## Summary

**Services Analyzed:** 9/10 (specification_service.py missing)
**Ready for FR Extraction:** 9 services
**Estimated FRs to Create:** 9

---

## Epic Assignment Summary

| Epic | Services Assigned | Count |
|------|-------------------|-------|
| EPIC-001 (External Integration) | import_service | 1 |
| EPIC-005 (Qualification & Analysis) | graph_analysis, impact_analysis | 2 |
| EPIC-006 (Application & Tracking) | link, item, traceability | 3 |
| EPIC-008 (Reporting & Analytics) | export, graph, traceability_matrix | 3 |

---

## Next Steps (Awaiting Team Lead Decision)

**Option A:** Extract full FRs → Update FUNCTIONAL_REQUIREMENTS.md → Annotate
**Option B:** Add placeholder annotations → Mark for future FR extraction
**Option C:** Lightweight FR extraction from code → Annotate

**Status:** ✅ Analysis complete, ready to proceed
