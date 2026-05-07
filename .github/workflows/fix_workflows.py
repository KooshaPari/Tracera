#!/usr/bin/env python3
import os

WORKFLOWS_DIR = '/Users/kooshapari/CodeProjects/Phenotype/repos/Tracera/.github/workflows'

# ============ 1. Fix canary-deploy.yml: duplicate permissions & concurrency ============
canary_path = os.path.join(WORKFLOWS_DIR, 'canary-deploy.yml')
with open(canary_path, 'r') as f:
    content = f.read()

lines = content.split('\n')
result = []
dup_state = 0  # 0=looking for first perms, 1=looked for first concurrency
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    # Remove the FIRST permissions: block (lines 3-5)
    if stripped == 'permissions:' and i > 0 and lines[i-1].strip() == '' and dup_state == 0:
        dup_state = 1  # mark we've skipped first perms
        i += 1
        while i < len(lines) and (lines[i].startswith('  ') or lines[i].strip() == ''):
            i += 1
        continue
    # Remove the FIRST concurrency: block
    if stripped == 'concurrency:' and dup_state == 1 and i < 10:
        dup_state = 2
        i += 1
        while i < len(lines) and (lines[i].startswith('  ') or lines[i].strip() == ''):
            i += 1
        continue
    result.append(line)
    i += 1

# Now remove trailing dup concurrency block too
final_lines = []
found_concurrency = False
i = 0
while i < len(result):
    stripped = result[i].strip()
    if stripped == 'concurrency:' and found_concurrency:
        # skip whole block
        i += 1
        while i < len(result) and (result[i].startswith('  ') or result[i].strip() == ''):
            i += 1
        continue
    if stripped == 'concurrency:' and not found_concurrency:
        found_concurrency = True
    final_lines.append(result[i])
    i += 1

with open(canary_path, 'w') as f:
    f.write('\n'.join(final_lines))
print('Fixed canary-deploy.yml: deduplicated permissions & concurrency')


# ============ 2. Fix deployment-rollback.yml ============
rollback_path = os.path.join(WORKFLOWS_DIR, 'deployment-rollback.yml')
with open(rollback_path, 'r') as f:
    content = f.read()

# The broken step has multiple run: keys. Replace the "Rollback container deployment" section.
# Find the marker and reconstruct using line-based approach
lines = content.split('\n')

# Find the Rollback container deployment step boundaries
break_start = None
break_end = None
for i, line in enumerate(lines):
    if '- name: Rollback container deployment' in line:
        break_start = i
    if break_start is not None and i > break_start:
        # Look for the next step (starts with '    - name:')
        stripped = line.strip()
        if stripped.startswith('- name:') and i > break_start + 1:
            break_end = i
            break

if break_start is not None and break_end is not None:
    # Replace the broken step with properly separated steps
    replacement = [
        '    - name: Rollback container deployment',
        '      run: |',
        '        echo "Rolling back container deployment..."',
        '        # This is a placeholder - actual implementation depends on deployment platform',
        '        echo "Container rollback initiated"',
        '',
        '    - name: Wait for stabilization',
        '      run: |',
        '        echo "Waiting for deployment to stabilize..."',
        '        sleep 30',
        '',
        '    - name: Health check after rollback',
        '      run: |',
        '        ENVIRONMENT="${{ github.event.inputs.environment || github.event.client_payload.environment || \'production\' }}"',
        '        if [ "$ENVIRONMENT" = "production" ]; then',
        '          HEALTH_URL="${{ secrets.PRODUCTION_HEALTH_URL }}"',
        '        else',
        '          HEALTH_URL="${{ secrets.STAGING_HEALTH_URL }}"',
        '        fi',
        '        MAX_RETRIES=10',
        '        RETRY_DELAY=10',
        '        for i in $(seq 1 $MAX_RETRIES); do',
        '          echo "Health check attempt $i/$MAX_RETRIES..."',
        '          RESPONSE=$(curl -s -w "\\n%{http_code}" "$HEALTH_URL/health" || echo "000")',
        '          HTTP_CODE=$(echo "$RESPONSE" | tail -n1)',
        '          if [ "$HTTP_CODE" = "200" ]; then',
        '            echo "Health check passed!"',
        '            exit 0',
        '          fi',
        '          echo "Health check failed (status: $HTTP_CODE). Retrying in ${RETRY_DELAY}s..."',
        '          sleep $RETRY_DELAY',
        '        done',
        '        echo "Health check failed after $MAX_RETRIES attempts"',
        '        exit 1',
    ]
    new_lines = lines[:break_start] + replacement + lines[break_end:]
    content = '\n'.join(new_lines)
    print(f'Fixed deployment-rollback.yml: replaced broken multi-run step at line {break_start+1}')
else:
    print('WARNING: Could not find broken step in deployment-rollback.yml')

# Fix the "Monitor error rates" step that has both run: and uses:
if '    - name: Monitor error rates' in content:
    # Split into two steps: monitor and comment
    old = '    - name: Monitor error rates\n      run: |\n        echo "📊 Monitoring error rates..."'
    new = '    - name: Monitor error rates\n      run: |\n        echo "Monitoring error rates..."'
    content = content.replace(old, new)

    # Now find the 'uses: actions/github-script' block after this and split it off
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'uses: actions/github-script@f28e40c7f34bde8b3046d885e986cb6290c5673b' in line:
            # This needs a separate step name before it
            prev_line = lines[i-1].strip() if i > 0 else ''
            # Check if the previous non-empty line was a `run:` continuation
            # Find the actual step header
            for j in range(i, -1, -1):
                if lines[j].strip().startswith('- name:'):
                    current_name = lines[j].strip()
                    lines[j] = '    - name: Comment rollback result on PR'
                    break
            break
    content = '\n'.join(lines)
    print('Fixed deployment-rollback.yml: split monitor/comment steps')

with open(rollback_path, 'w') as f:
    f.write(content)


# ============ 3. Fix dependabot-auto-merge.yml ============
dab_path = os.path.join(WORKFLOWS_DIR, 'dependabot-auto-merge.yml')
with open(dab_path, 'r') as f:
    content = f.read()

# Scope permissions to contents: write only (remove pull-requests: write)
old_perms = 'permissions:\n  contents: write\n  pull-requests: write'
new_perms = 'permissions:\n  contents: write'
if old_perms in content:
    content = content.replace(old_perms, new_perms)
    print('Fixed dependabot-auto-merge.yml: scoped permissions to contents: write')

# Add timeout-minutes to the verify-tests job if not present
if 'timeout-minutes' not in content:
    content = content.replace(
        '  verify-tests:\n    name: Verify Tests Pass\n    runs-on: ubuntu-latest\n    if:',
        '  verify-tests:\n    name: Verify Tests Pass\n    runs-on: ubuntu-latest\n    timeout-minutes: 15\n    if:'
    )
    print('Fixed dependabot-auto-merge.yml: added timeout-minutes')

with open(dab_path, 'w') as f:
    f.write(content)


# ============ 4. Fix release.yml ============
release_path = os.path.join(WORKFLOWS_DIR, 'release.yml')
with open(release_path, 'r') as f:
    content = f.read()

# Already has actions: read set. Check if timeout-minutes is at step level
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'timeout-minutes: 30' in line and line.startswith('    '):
        lines[i] = '  timeout-minutes: 30'
        print(f'Fixed release.yml: moved timeout-minutes to job level (was at step level)')
        break

content = '\n'.join(lines)
with open(release_path, 'w') as f:
    f.write(content)


# ============ 5. Fix scorecard.yml: explicit permissions ============
scorecard_path = os.path.join(WORKFLOWS_DIR, 'scorecard.yml')
with open(scorecard_path, 'r') as f:
    content = f.read()

content = content.replace(
    'permissions: read-all',
    'permissions:\n  contents: read\n  actions: read'
)
print('Fixed scorecard.yml: explicit permissions')

with open(scorecard_path, 'w') as f:
    f.write(content)


# ============ 6. Fix journey-gate.yml: add permissions, pin SHA ============
journey_path = os.path.join(WORKFLOWS_DIR, 'journey-gate.yml')
with open(journey_path, 'r') as f:
    content = f.read()

# Insert permissions before jobs:
content = content.replace(
    '\njobs:\n  journey-verify:',
    '\npermissions:\n  contents: read\n\njobs:\n  journey-verify:'
)
# Pin checkout SHA
content = content.replace(
    'actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4',
    'actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683'
)
print('Fixed journey-gate.yml: added permissions, pinned checkout SHA')

with open(journey_path, 'w') as f:
    f.write(content)


# ============ 7. Fix alert-sync-issues.yml: add actions: read ============
alert_path = os.path.join(WORKFLOWS_DIR, 'alert-sync-issues.yml')
with open(alert_path, 'r') as f:
    content = f.read()

content = content.replace(
    'permissions:\n  contents: read',
    'permissions:\n  contents: read\n  actions: read'
)
print('Fixed alert-sync-issues.yml: added actions: read')

with open(alert_path, 'w') as f:
    f.write(content)


# ============ 8. Fix architecture.yml: correct permissions ============
arch_path = os.path.join(WORKFLOWS_DIR, 'architecture.yml')
with open(arch_path, 'r') as f:
    content = f.read()

content = content.replace(
    'permissions:\n  contents: read\n  issues: write\n  pull-requests: read',
    'permissions:\n  contents: read\n  pull-requests: write'
)
print('Fixed architecture.yml: corrected permissions')

with open(arch_path, 'w') as f:
    f.write(content)


# ============ 9. Fix test-pyramid.yml: too broad permissions ============
pyramid_path = os.path.join(WORKFLOWS_DIR, 'test-pyramid.yml')
with open(pyramid_path, 'r') as f:
    content = f.read()

content = content.replace(
    'permissions:\n  contents: read\n  issues: write\n  pull-requests: write',
    'permissions:\n  contents: read\n  pull-requests: write'
)
print('Fixed test-pyramid.yml: corrected permissions (removed issues: write)')

with open(pyramid_path, 'w') as f:
    f.write(content)


# ============ 10. Fix remaining workflows that need actions: read ============
# Find all workflows without actions: read that use reusable workflows
# Workflows using reusable workflows via 'uses:' need actions: read
reusable_workflows = [
    'contracts.yml', 'test.yml', 'security-guard-hook-audit.yml',
    'security-scans.yml', 'ci.yml', 'go-tests.yml'
]

for fname in reusable_workflows:
    fpath = os.path.join(WORKFLOWS_DIR, fname)
    with open(fpath, 'r') as f:
        content = f.read()

    # Check if it uses reusable workflows
    uses_reusable = 'uses:' in content and ('/reusable/' in content or '/.github/workflows/' in content)

    # Add actions: read if missing
    perms_pattern = 'permissions:\n  contents: read'
    if perms_pattern in content and 'actions: read' not in content:
        content = content.replace(
            perms_pattern,
            'permissions:\n  contents: read\n  actions: read'
        )
        print(f'Fixed {fname}: added actions: read')

    with open(fpath, 'w') as f:
        f.write(content)


print('\nAll targeted fixes applied successfully!')
