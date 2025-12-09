# AGENTS.md Governance

This document defines the governance structure for organizing markdown files in the repository.

## Directory Structure

All markdown files in the root directory should be organized into the following structure:

```
./
├── AGENTS.md                    # This governance file
├── README.md                    # Main project README (stays in root)
├── CHANGELOG.md                 # Project changelog (stays in root)
│
├── AGENTS/                      # Agent-specific documentation
│   ├── AGENT1/                  # Agent 1 work products
│   ├── AGENT2/                  # Agent 2 work products
│   └── CLAUDE/                  # Claude-specific guides
│
├── EPICS/                       # Epic completion reports
│   ├── EPIC_1_COMPLETE.md
│   ├── EPIC_2_COMPLETE.md
│   └── ...
│
├── PHASES/                      # Phase completion reports
│   ├── PHASE_1_*.md
│   ├── PHASE_2_*.md
│   └── ...
│
├── STATUS/                       # Status and completion summaries
│   ├── FINAL_*.md
│   ├── COMPLETE_*.md
│   ├── COMPLETION_*.md
│   └── MVP_*.md
│
├── PLANNING/                    # Planning and implementation documents
│   ├── IMPLEMENTATION_*.md
│   ├── PLAN_*.md
│   └── ROADMAP_*.md
│
├── RESEARCH/                    # Research findings and summaries
│   ├── RESEARCH_*.md
│   ├── ARCHITECTURE_*.md
│   ├── BACKEND_*.md
│   └── DATABASE_*.md
│
├── TESTING/                     # Testing documentation
│   ├── TEST_*.md
│   ├── E2E_*.md
│   ├── COVERAGE_*.md
│   └── TESTING_*.md
│
├── DOCUMENTATION/               # Documentation and audit files
│   ├── DOCUMENTATION_*.md
│   ├── GAP_*.md
│   ├── AUDIT_*.md
│   └── COMPREHENSIVE_*.md
│
└── GUIDES/                     # Guides and references
    ├── QUICK_REFERENCE.md
    ├── INTEGRATION_GUIDE.md
    ├── DEPLOYMENT_CHECKLIST.md
    └── ...
```

## File Organization Rules

### 1. Agent Files (AGENTS/)
- All files starting with `AGENT1_*` → `AGENTS/AGENT1/`
- All files starting with `AGENT2_*` → `AGENTS/AGENT2/`
- All files starting with `AGENT*` → `AGENTS/` (general agent files)

### 2. Epic Files (EPICS/)
- All files starting with `EPIC_*` → `EPICS/`

### 3. Phase Files (PHASES/)
- All files starting with `PHASE_*` → `PHASES/`
- All files starting with `PHASES_*` → `PHASES/`

### 4. Status Files (STATUS/)
- Files starting with `FINAL_*` → `STATUS/`
- Files starting with `COMPLETE_*` (not COMPLETION) → `STATUS/`
- Files starting with `COMPLETION_*` → `STATUS/`
- Files starting with `MVP_*` → `STATUS/`
- Files starting with `PROJECT_COMPLETION_*` → `STATUS/`

### 5. Planning Files (PLANNING/)
- Files starting with `IMPLEMENTATION_*` → `PLANNING/`
- Files containing `PLAN` or `ROADMAP` → `PLANNING/`
- Files containing `CHECKLIST` → `PLANNING/`

### 6. Research Files (RESEARCH/)
- Files starting with `RESEARCH_*` → `RESEARCH/`
- Files starting with `ARCHITECTURE_*` → `RESEARCH/`
- Files starting with `BACKEND_*` → `RESEARCH/`
- Files starting with `DATABASE_*` → `RESEARCH/`
- Files starting with `CLOUD_*` → `RESEARCH/`
- Files starting with `FRONTEND_*` → `RESEARCH/`

### 7. Testing Files (TESTING/)
- Files starting with `TEST_*` → `TESTING/`
- Files starting with `E2E_*` → `TESTING/`
- Files starting with `COVERAGE_*` → `TESTING/`
- Files containing `TESTING` → `TESTING/`
- Files with numeric prefixes like `00_README_TESTING_*` → `TESTING/`
- Files with `100_PERCENT_TEST_*` → `TESTING/`

### 8. Documentation Files (DOCUMENTATION/)
- Files starting with `DOCUMENTATION_*` → `DOCUMENTATION/`
- Files starting with `GAP_*` → `DOCUMENTATION/`
- Files starting with `AUDIT_*` → `DOCUMENTATION/`
- Files starting with `COMPREHENSIVE_*` → `DOCUMENTATION/`
- Files starting with `CURRENT_*` → `DOCUMENTATION/`
- Files starting with `ADDITIONAL_*` → `DOCUMENTATION/`
- Files starting with `ORIGINAL_*` → `DOCUMENTATION/`

### 9. Guides (GUIDES/)
- Files containing `GUIDE` → `GUIDES/`
- Files containing `REFERENCE` → `GUIDES/`
- Files containing `WALKTHROUGH` → `GUIDES/`
- Files containing `DEMONSTRATION` → `GUIDES/`
- Files containing `EXAMPLES` → `GUIDES/`

### 10. Root Files (Stay in Root)
- `README.md` - Main project documentation
- `CHANGELOG.md` - Project changelog
- `AGENTS.md` - This governance file

## Migration Process

When organizing files:
1. Create the directory structure if it doesn't exist
2. Move files according to the rules above
3. Update any cross-references in moved files
4. Update README.md if it references moved files

## Maintenance

- New markdown files should be placed in the appropriate directory from the start
- Review and reorganize quarterly to maintain structure
- Update this governance document as the project evolves
