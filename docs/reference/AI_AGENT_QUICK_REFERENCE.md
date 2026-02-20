# AI Agent Quick Reference - TraceRTM Frontend

## 🚨 CRITICAL RULES - READ FIRST

### #1: NEVER Create Versioned Names

```
❌ Dashboard_v2.tsx
❌ NewDashboard.tsx
❌ ImprovedDashboard.tsx
❌ EnhancedDashboard.tsx
❌ Dashboard_2.tsx
❌ Dashboard_new.tsx

✅ Dashboard.tsx (EDIT IN PLACE)
```

**Why**: This creates orphaned files. We aggressively evolve - no backward compatibility needed.

**Detection**: Automated checks will block commits with versioned names.

### #2: Edit Files In Place

```bash
# ❌ WRONG
# 1. Read Dashboard.tsx
# 2. Write to Dashboard_v2.tsx
# 3. Update imports

# ✅ CORRECT
# 1. Read Dashboard.tsx
# 2. Use Edit tool on Dashboard.tsx
# 3. No import changes needed
```

### #3: Delete Orphaned Code Immediately

```bash
# Find orphaned versions
ls *Dashboard*.tsx

# If you see multiple versions:
Dashboard.tsx
Dashboard_v2.tsx      # DELETE THIS
EnhancedDashboard.tsx # DELETE THIS

# Keep only the canonical one being used
```

---

## 🔒 Linting Configuration

### Current Config: `.oxlintrc.json`

**Maximum strictness for AI-coded projects**

### Run Linting

```bash
# Check all violations
bunx oxlint --type-aware .

# Auto-fix what's possible
bunx oxlint --type-aware . --fix

# Check specific file
bunx oxlint --type-aware src/components/MyComponent.tsx
```

### Key Rules

| Rule                                       | Level      | Why                      |
| ------------------------------------------ | ---------- | ------------------------ |
| `typescript/no-explicit-any`               | ERROR      | Prevents type unsafety   |
| `typescript/explicit-function-return-type` | ERROR      | Forces explicit types    |
| `eslint/max-lines-per-function`            | ERROR (50) | Prevents bloat           |
| `eslint/max-params`                        | ERROR (3)  | Forces simple signatures |
| `eslint/no-magic-numbers`                  | ERROR      | Requires named constants |
| `eslint/sort-imports`                      | ERROR      | Consistent import order  |
| `react-perf/jsx-no-new-object-as-prop`     | ERROR      | Prevents re-renders      |
| `import/no-cycle`                          | ERROR      | Prevents circular deps   |

---

## 📝 Before Starting Work

```bash
# 1. Check current linting state
bunx oxlint --type-aware . > baseline.txt
wc -l baseline.txt

# 2. Note the number of violations
# Goal: Don't increase violations, ideally decrease them
```

---

## 🛠️ During Development

### Every 15 Minutes

```bash
# Run linting check
bunx oxlint --type-aware .

# Auto-fix if possible
bunx oxlint --type-aware . --fix
```

### Before Each Commit

```bash
# 1. Run full linting
bunx oxlint --type-aware .

# 2. Check for naming explosion
./scripts/check-naming-explosion.sh

# 3. Only commit if:
#    - No new violations introduced
#    - OR violations decreased
#    - OR you're fixing violations
```

---

## ⚠️ Common AI Anti-Patterns to Avoid

### Anti-Pattern #1: Naming Explosion

```typescript
// ❌ Creating versions
Dashboard.tsx
Dashboard_v2.tsx
NewDashboard.tsx

// ✅ Edit in place
Dashboard.tsx (single file, edited multiple times)
```

### Anti-Pattern #2: Type Unsafety

```typescript
// ❌ Using any
function getData(id: any) { ... }

// ✅ Explicit types
function getData(id: string): UserData | undefined { ... }
```

### Anti-Pattern #3: Magic Numbers

```typescript
// ❌ Magic numbers
if (retries > 3) {
  setTimeout(fn, 5000);
}

// ✅ Named constants
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 5000;
if (retries > MAX_RETRIES) {
  setTimeout(fn, RETRY_DELAY_MS);
}
```

### Anti-Pattern #4: Monolithic Functions

```typescript
// ❌ 150-line function
function processUser(user, options, context, flags) {
  // 150 lines of nested logic...
}

// ✅ Decomposed functions (max 50 lines each)
function processUser(user: User): ProcessedUser {
  const validated = validateUser(user);
  const enriched = enrichUserData(validated);
  return transformUser(enriched);
}
```

### Anti-Pattern #5: Inline Objects in JSX

```typescript
// ❌ Creates new objects on every render
<Child data={{ value: 123 }} items={[1, 2, 3]} />

// ✅ Define outside or use constants
const DATA = { value: 123 };
const ITEMS = [1, 2, 3];
<Child data={DATA} items={ITEMS} />
```

---

## 🎯 Commit Message Format

```bash
# For new features
git commit -m "feat: add user profile editing"

# For bug fixes
git commit -m "fix: resolve null pointer in dashboard"

# For linting fixes
git commit -m "refactor: fix 50 type safety violations"

# For naming cleanup
git commit -m "refactor: consolidate Dashboard to canonical implementation"
```

---

## 📊 Quality Metrics

### Target Goals

| Metric                 | Target | Status    |
| ---------------------- | ------ | --------- |
| Type safety violations | 0      | 🔴 8,849  |
| Functions > 50 lines   | 0      | 🔴 ~200   |
| Magic numbers          | 0      | 🔴 ~500   |
| Circular dependencies  | 0      | 🔴 41     |
| Total violations       | <5,000 | 🔴 53,469 |

### Check Your Impact

```bash
# Before work
bunx oxlint --type-aware . | wc -l
# 53469

# After work
bunx oxlint --type-aware . | wc -l
# 53400  (✅ Reduced by 69!)
```

---

## 🆘 When You're Blocked

### Issue: "Linting is blocking my commit"

**Response**: Fix the violations, don't bypass them.

```bash
# See what's wrong
bunx oxlint --type-aware .

# Auto-fix what's possible
bunx oxlint --type-aware . --fix

# Manually fix remaining issues
```

### Issue: "I need to disable a rule"

**Response**: Only with documentation + approval.

```typescript
// ❌ NEVER do this without explanation
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function handler(data: any) { ... }

// ✅ Acceptable (with context)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
// TODO(#1234): Replace with proper type after API v2 migration (Q2 2026)
// API v1 returns inconsistent shapes - any is required temporarily
function legacyApiHandler(data: any) { ... }
```

### Issue: "Naming check is blocking Dashboard_v2"

**Response**: This is intentional - consolidate to canonical name.

```bash
# 1. Find what's actually used
rg "import.*Dashboard" --type tsx

# 2. That's your canonical file - edit it
# Use Edit tool on Dashboard.tsx

# 3. Delete Dashboard_v2.tsx
rm Dashboard_v2.tsx

# 4. Verify no broken imports
rg "Dashboard_v2" --type tsx
```

---

## 📚 Documentation Files

| File                                | Purpose                       |
| ----------------------------------- | ----------------------------- |
| `AI_CODING_QUALITY_GATES.md`        | Complete implementation guide |
| `AI_CODED_LINTING_STRATEGY.md`      | Why strict linting for AI     |
| `AI_NAMING_EXPLOSION_PREVENTION.md` | Versioned naming prevention   |
| `PLAYWRIGHT_QA_SETUP_COMPLETE.md`   | Testing infrastructure        |
| `SETUP_COMPLETE.md`                 | Original setup documentation  |

---

## ✅ Pre-Commit Checklist

Before every commit:

- [ ] No versioned naming (Dashboard_v2, NewDashboard, etc.)
- [ ] Linting violations not increased (or decreased!)
- [ ] No `any` types introduced
- [ ] Functions < 50 lines
- [ ] Max 3 parameters per function
- [ ] Magic numbers extracted to constants
- [ ] Imports sorted alphabetically
- [ ] Tests passing
- [ ] Orphaned files deleted

---

## 🚀 Quick Commands

```bash
# Lint everything
bunx oxlint --type-aware .

# Auto-fix
bunx oxlint --type-aware . --fix

# Check naming explosion
./scripts/check-naming-explosion.sh

# Find orphaned versions
ls *Dashboard*.tsx

# Check what imports a file
rg "import.*Dashboard" --type tsx

# Count violations
bunx oxlint --type-aware . | wc -l

# Run tests
bun test

# Run E2E tests
bun run test:e2e
```

---

## 🎓 Remember

1. **Edit in place, never duplicate**
2. **No versioned names, ever**
3. **Fix code, not rules**
4. **Delete orphaned files immediately**
5. **Type safety is non-negotiable**
6. **This is an AI-coded project - strict rules prevent chaos**

---

**Last Updated**: 2026-02-02
**Project**: TraceRTM Frontend (AI-Coded)
**Config**: `.oxlintrc.json`
