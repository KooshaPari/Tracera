# Contract Versioning Guide

This guide explains how contract versions are managed and how to handle breaking changes.

## Version Structure

```
tests/contracts/versions/
├── v1.0.0/                 # Release v1.0.0 contracts
│   ├── auth.json
│   ├── projects.json
│   └── ...
├── v1.1.0/                 # Release v1.1.0 contracts
│   └── ...
├── v2.0.0/                 # Major version (breaking changes)
│   └── ...
└── current -> v1.1.0/      # Symlink to latest
```

## Version Lifecycle

### 1. Development

During development, contracts are in `tests/contracts/pacts/`:

```
pacts/
├── tracertm-web-auth-tracertm-api.json
├── tracertm-web-projects-tracertm-api.json
└── ...
```

These are **working contracts** that change frequently.

### 2. Release

On release (merge to main), contracts are versioned:

```bash
# Automated by CI/CD
VERSION=$(git describe --tags --always)
mkdir -p tests/contracts/versions/$VERSION
cp tests/contracts/pacts/*.json tests/contracts/versions/$VERSION/
```

### 3. Maintenance

Old versions are preserved for compatibility checking:

```bash
# Check compatibility with v1.0.0
pact-broker can-i-deploy \
  --pacticipant TraceRTM-Web \
  --version $VERSION \
  --to-environment production
```

## Semantic Versioning

### Patch Version (v1.0.1)

**Non-breaking changes**:
- New optional fields
- Additional endpoints
- Documentation updates
- Bug fixes

**Example**:
```typescript
// v1.0.0
{
  id: uuid('123'),
  name: like('Project')
}

// v1.0.1 - Added optional field (non-breaking)
{
  id: uuid('123'),
  name: like('Project'),
  description: like('Optional description') // New optional
}
```

### Minor Version (v1.1.0)

**Backwards-compatible additions**:
- New endpoints
- New optional parameters
- New response fields (optional)

**Example**:
```typescript
// v1.0.0
POST /projects
{
  name: 'Project',
  description: 'Description'
}

// v1.1.0 - New optional parameter (non-breaking)
POST /projects
{
  name: 'Project',
  description: 'Description',
  template: 'agile' // New optional parameter
}
```

### Major Version (v2.0.0)

**Breaking changes**:
- Removing endpoints
- Changing required fields
- Changing response structure
- Renaming fields

**Example**:
```typescript
// v1.x.x
{
  id: uuid('123'),
  project_name: like('Project') // Old name
}

// v2.0.0 - Breaking: renamed field
{
  id: uuid('123'),
  name: like('Project') // New name
}
```

## Breaking Change Process

### 1. Identify Breaking Change

Review contract changes:
```bash
# Compare with previous version
diff tests/contracts/versions/v1.0.0/auth.json \
     tests/contracts/pacts/auth.json
```

### 2. Create Migration Guide

Document in `CHANGELOG.md`:

```markdown
## v2.0.0 - BREAKING CHANGES

### API Changes

**Auth API**

BREAKING: Renamed `project_name` to `name` in all responses.

Migration:
```typescript
// Before (v1.x.x)
const projectName = response.project_name;

// After (v2.0.0)
const projectName = response.name;
```

### 3. Deprecation Period

For major changes, provide deprecation notice:

```typescript
// v1.5.0 - Deprecation notice
{
  id: uuid('123'),
  project_name: like('Project'), // @deprecated Use `name` instead
  name: like('Project') // New field (also available)
}
```

Support both for 1-2 releases.

### 4. Remove Deprecated

In next major version, remove deprecated fields:

```typescript
// v2.0.0 - Deprecated field removed
{
  id: uuid('123'),
  name: like('Project') // Only new field
}
```

## Compatibility Checking

### Can I Deploy?

Check if consumer version is compatible with provider:

```bash
# Check if v1.2.0 consumer can deploy to production
pact-broker can-i-deploy \
  --pacticipant TraceRTM-Web \
  --version v1.2.0 \
  --to-environment production
```

### Version Matrix

Maintain compatibility matrix:

| Consumer | Provider | Compatible |
|----------|----------|------------|
| v1.0.x   | v1.0.x   | ✅ Yes     |
| v1.0.x   | v1.1.x   | ✅ Yes     |
| v1.1.x   | v1.0.x   | ⚠️ Degraded|
| v2.0.x   | v1.x.x   | ❌ No      |

## Contract Evolution Examples

### Example 1: Add Optional Field (Non-Breaking)

**Before (v1.0.0)**:
```typescript
it('should return user info', async () => {
  willRespondWith: standardResponse({
    id: uuid('123'),
    email: like('user@example.com'),
    name: like('User')
  })
});
```

**After (v1.1.0)**:
```typescript
it('should return user info', async () => {
  willRespondWith: standardResponse({
    id: uuid('123'),
    email: like('user@example.com'),
    name: like('User'),
    avatar: like('https://avatar.url') // New optional field
  })
});
```

✅ **Non-breaking**: Old consumers still work.

### Example 2: Add New Endpoint (Non-Breaking)

**Before (v1.0.0)**:
- `GET /projects`
- `POST /projects`

**After (v1.1.0)**:
- `GET /projects`
- `POST /projects`
- `GET /projects/search` ← New endpoint

✅ **Non-breaking**: New endpoint doesn't affect existing contracts.

### Example 3: Change Required Field (Breaking)

**Before (v1.x.x)**:
```typescript
withRequest: {
  body: {
    email: 'user@example.com',
    password: 'password'
  }
}
```

**After (v2.0.0)**:
```typescript
withRequest: {
  body: {
    email: 'user@example.com',
    password: 'password',
    mfaCode: '123456' // Now required
  }
}
```

❌ **Breaking**: Requires major version bump.

### Example 4: Remove Endpoint (Breaking)

**Before (v1.x.x)**:
- `GET /old-endpoint`
- `GET /new-endpoint`

**After (v2.0.0)**:
- `GET /new-endpoint`

❌ **Breaking**: Requires major version and migration guide.

## Best Practices

### 1. Review All Changes

Before merging:
```bash
# Generate pacts
bun run test:contracts

# Compare with current version
diff -r tests/contracts/versions/current tests/contracts/pacts
```

### 2. Document Breaking Changes

In PR description:
```markdown
## Contract Changes

**Breaking Changes**: Yes ⚠️

- Renamed `project_name` to `name` (breaking)
- Removed deprecated `GET /old-endpoint` (breaking)

**Migration Required**: Yes
```

### 3. Version Bump Checklist

- [ ] Identified all breaking changes
- [ ] Updated version in `package.json` / `go.mod`
- [ ] Created migration guide in `CHANGELOG.md`
- [ ] Updated all consumer code
- [ ] Verified provider tests pass
- [ ] Documented deprecations (if any)

### 4. Communication

For breaking changes:
1. Notify all consumers (frontend, CLI, MCP teams)
2. Share migration guide
3. Set deprecation timeline
4. Provide support during migration

## Tools

### Compare Contracts

```bash
# Compare two versions
./scripts/compare-contracts.sh v1.0.0 v1.1.0
```

### Validate Compatibility

```bash
# Check if contracts are compatible
pact-broker can-i-deploy \
  --pacticipant TraceRTM-Web \
  --version v1.2.0 \
  --pacticipant TraceRTM-API \
  --version v1.2.0
```

### Archive Old Versions

```bash
# Archive versions older than 6 months
./scripts/archive-old-contracts.sh --older-than 6m
```

## Resources

- [Semantic Versioning](https://semver.org/)
- [Pact Versioning Best Practices](https://docs.pact.io/getting_started/versioning_in_the_pact_broker)
- [Contract Testing Guide](./README.md)
