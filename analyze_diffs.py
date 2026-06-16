import subprocess
import sys

with open('branch_counts.txt') as f:
    lines = f.readlines()

with open('branch_diffs.txt', 'w') as out:
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split('|')
        branch, bu, ub = parts[0], parts[1], parts[2]
        if bu == '0' or bu == '?':
            continue
        try:
            result = subprocess.run(
                ['git', 'diff', '--stat', f'fix/main-ci-greenup...{branch}'],
                capture_output=True, text=True, timeout=60
            )
            summary_lines = result.stdout.strip().split('\n')
            summary = summary_lines[-1] if summary_lines else 'NO DIFF'
        except subprocess.TimeoutExpired:
            summary = 'TIMEOUT'
        out.write(f'{branch}|{bu}|{ub}|{summary}\n')
        out.flush()
        print(f'Done: {branch}', file=sys.stderr)

print('All done', file=sys.stderr)
