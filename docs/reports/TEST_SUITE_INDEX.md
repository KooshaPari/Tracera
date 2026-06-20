# Test Suite - Complete Index & Reference

## 🎯 Quick Links

### Running Tests
- **Mock tests** (development): `npx playwright test`
- **Live tests** (real data): `VITE_USE_MOCK_DATA=false npx playwright test`
- **Live dashboard**: `VITE_USE_MOCK_DATA=false npx playwright test dashboard-live-data.spec.ts`

### Documentation
1. **[TEST_SUITE_DOCUMENTATION.md](./TEST_SUITE_DOCUMENTATION.md)** - Complete guide
   - All commands and usage
   - Environment variables
   - CI/CD integration
   - Troubleshooting

2. **[TEST_MIGRATION_PLAN.md](./TEST_MIGRATION_PLAN.md)** - Implementation approach
   - Phased rollout plan
   - Code examples
   - Success criteria

### Test Files
- **Mock tests**: `frontend/apps/web/e2e/*.spec.ts` (61 files)
- **Live tests**: `frontend/apps/web/e2e/dashboard-live-data.spec.ts` (new)

---

## 📊 Test Suite Summary

### Coverage
- **Playwright E2E**: 61 files (85% real API)
- **Python API**: 43 files (86% real API)
- **Python E2E**: 13 files (CLI tests)
- **Unit Tests**: 639 files (frontend packages)
- **Total**: 756 test files

### Test Account
```
Email:       test@tracertm.io
Profile ID:  86f0050b-7758-460b-8271-0e00dc1b1ae0
Account:     My Account
Projects:    SwiftRide (5,686 items) ✅ + others
Role:        member
Status:      Ready to use
```

### Modes Supported
| Mode | Speed | Data | Best For |
|------|-------|------|----------|
| Mock | <500ms | Synthetic | Development |
| Live | 2-5s | Real (5,686) | Validation |

---

## 🚀 Common Commands

```bash
# Development (mock tests, fast)
npx playwright test

# Validation (live tests, real data)
VITE_USE_MOCK_DATA=false npx playwright test

# Debug specific test
VITE_USE_MOCK_DATA=false npx playwright test dashboard-live-data.spec.ts --debug

# UI mode
VITE_USE_MOCK_DATA=false npx playwright test --ui

# Generate report
npx playwright show-report
```

---

## 📁 File Structure

```
frontend/apps/web/
├── playwright.config.ts          [Modified] Dynamic baseURL
├── e2e/
│   ├── global-setup.ts           [Modified] Dual test user
│   ├── dashboard-live-data.spec.ts  [New] Live tests
│   └── ... 60 other test files
│
src/mocks/
├── handlers.ts                   MSW handlers (mock endpoints)
├── data.ts                       Synthetic test data
└── browser.ts                    MSW setup

docs/
└── guides/
    └── TEST_SUITE_DOCUMENTATION.md  [Complete guide]
```

---

## ✅ What's Implemented

1. **Dual-Mode Testing** ✅
   - Mock mode for fast development
   - Live mode for realistic testing

2. **Test Account** ✅
   - test@tracertm.io in PostgreSQL
   - Full access to SwiftRide (5,686 items)
   - Verified and ready to use

3. **Configuration** ✅
   - Environment variable: VITE_USE_MOCK_DATA
   - Auto-switching baseURL
   - Backward compatible

4. **Live Test Suite** ✅
   - dashboard-live-data.spec.ts created
   - 11 tests for real data
   - Performance benchmarks

5. **Documentation** ✅
   - Complete testing guide
   - CI/CD examples
   - Troubleshooting

---

## 🎓 Best Practices

1. **Development**: Use mock tests (fast feedback)
2. **Before Push**: Run live tests (validate with real data)
3. **CI/CD**: Run both (quick + comprehensive validation)
4. **Performance**: Baseline with live tests (5,686 items)

---

## 📞 Troubleshooting

**Tests fail in live mode?**
- Check backend: `curl http://localhost:8000/health`
- Verify env var: `echo $VITE_USE_MOCK_DATA`

**MSW still intercepting?**
- Make sure env var is set before running: `export VITE_USE_MOCK_DATA=false`

**Test account has no access?**
- Check DB: `psql ... -c "SELECT * FROM account_users WHERE user_id='test@tracertm.io'"`

**See full guide**: [TEST_SUITE_DOCUMENTATION.md](./TEST_SUITE_DOCUMENTATION.md)

---

## 📈 Performance Expectations

- **Mock dashboard**: <500ms
- **Live dashboard**: 2-5s (5,686 items)
- **Mock tests**: 5-10 min (61 files)
- **Live tests**: 15-30 min (61 files)

---

## 🔧 CI/CD Integration

### GitHub Actions
```yaml
- run: npx playwright test              # Fast mock tests
- run: VITE_USE_MOCK_DATA=false npx playwright test  # Comprehensive
```

### Jenkins
```groovy
stage('E2E - Mock') { sh 'npx playwright test' }
stage('E2E - Live') { 
  withEnv(['VITE_USE_MOCK_DATA=false']) { 
    sh 'npx playwright test' 
  } 
}
```

---

## 📚 Related Documentation

- [Playwright Docs](https://playwright.dev)
- [Mock Service Worker](https://mswjs.io)
- [Backend API](http://localhost:8000/docs)
- [Full Testing Guide](./TEST_SUITE_DOCUMENTATION.md)

---

**Status**: ✅ Complete & Ready  
**Date**: 2026-02-06  
**Test Account**: test@tracertm.io  
**Test Data**: SwiftRide (5,686 items)
