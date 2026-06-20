# Go Linting Phase 1 - Quick Reference

**Status**: ✅ COMPLETE | **Date**: 2026-02-02 | **Commit**: 706899b5b

---

## What Changed

### 7 New Linters
- **mnd** (719) - Magic numbers
- **perfsprint** (565) - Performance
- **funlen** (203) - Function length
- **dupl** (63) - Duplicate code
- **goconst** (60) - Repeated strings
- **nolintlint** (23) - Invalid //nolint
- **gochecknoglobals** (17) - Global vars

### Complexity Tightened
- **gocyclo**: 15 → 10
- **gocognit**: 20 → 12

---

## Quick Commands

### Run Linting
```bash
cd backend
golangci-lint run
```

### Check Only New Linters
```bash
cd backend
golangci-lint run --disable-all \
  --enable=dupl,goconst,funlen,mnd,nolintlint,gochecknoglobals,perfsprint
```

### Generate Current Report
```bash
cd backend
golangci-lint run --output.json.path=golangci-current.json
```

### Count Violations
```bash
cd backend
cat golangci-current.json | jq -r '.Issues[] | .FromLinter' | sort | uniq -c | sort -rn
```

---

## Files

### Active (in backend/)
- `backend/.golangci.yml` - Configuration
- `backend/golangci-baseline.json` - Baseline (1.3 MB)
- `backend/golangci-phase1-summary.txt` - Summary

### Committed (in root, backend/ is gitignored)
- `.golangci-backend.yml`
- `golangci-baseline-backend.json`
- `golangci-phase1-summary-backend.txt`

---

## Metrics

| Metric | Value |
|--------|-------|
| Total Issues | 3,642 |
| New from Phase 1 | ~1,700 |
| Linters Enabled | 29 (was 22) |
| Lint Time | +15-20s |

---

## Next Steps

1. **Phase 2** (Weeks 2-3): Fix errcheck, gosec, staticcheck
2. **Phase 3** (Weeks 4-5): Refactor funlen, gocyclo, gocognit
3. **Phase 4** (Week 6): Fix mnd, perfsprint, goconst, dupl

---

## Full Details

See: `/docs/reports/PHASE1_GO_LINTING_COMPLETE.md`
