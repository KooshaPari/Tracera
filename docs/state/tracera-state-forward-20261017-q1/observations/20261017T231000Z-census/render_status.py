"""Render the canonical evidence census, without third-party dependencies."""
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIMS = ('Implementation', 'Usability', 'Validation', 'Assurance')
VOCAB = {'PASS', 'FAIL', 'NOT_RUN', 'UNKNOWN', 'STALE', 'BLOCKED',
         'NOT_APPLICABLE', '?'}


def cell_line(dimension, cell):
    evidence = cell.get('evidence') or 'No qualifying witness collected'
    limit = cell.get('limit', '')
    return f'  +-- {dimension}: {cell["verdict"]} | {evidence}' + (f' | {limit}' if limit else '')


def parent_cell(goal, leaves, dimension):
    """Conjunction; one specific counterexample can refute whole-goal closure."""
    members = [leaves[i][dimension] | {'leaf': i} for i in goal['required_leaves']]
    failed = next((c for c in members if c['verdict'] == 'FAIL'), None)
    if failed:
        return dict(verdict='FAIL', evidence=failed['evidence'],
                    limit=f'Counterexample {failed["leaf"]}; no claim other children fail')
    if members and all(c['verdict'] in ('PASS', 'NOT_APPLICABLE') for c in members):
        return dict(verdict='PASS', evidence='; '.join(c['leaf'] for c in members),
                    limit='Conjunction of all required leaves at this dimension')
    pending = next((c for c in members if c['verdict'] == 'BLOCKED'), None)
    if pending:
        return dict(verdict='BLOCKED', evidence=pending['evidence'],
                    limit=f'Unclosed child {pending["leaf"]}')
    stale = next((c for c in members if c['verdict'] == 'STALE'), None)
    if stale:
        return dict(verdict='STALE', evidence=stale['evidence'],
                    limit=f'Unclosed child {stale["leaf"]}')
    unclosed = [c['leaf'] for c in members if c['verdict'] not in ('PASS', 'NOT_APPLICABLE')]
    return dict(verdict='UNKNOWN', evidence='STATUS.json#' + ','.join(unclosed),
                limit='Full criterion unclosed; source existence is insufficient')


def main():
    source = ROOT / 'STATUS.json'
    data = json.loads(source.read_text())
    leaves = {leaf['id']: leaf for leaf in data['leaves']}
    assert len(leaves) == len(data['leaves']), 'Duplicate leaf ID'
    for leaf in leaves.values():
        for dim in DIMS:
            cell = leaf[dim]
            assert cell['verdict'] in VOCAB, (leaf['id'], dim)
            assert cell['verdict'] in ('UNKNOWN', '?') or cell.get('evidence'), (leaf['id'], dim)
        assert leaf['kind'] in ('acceptance', 'observation', 'instrument', 'crosscut')
    for goal in data['goals']:
        assert goal['required_leaves'] and set(goal['required_leaves']) <= leaves.keys()
    counted = [leaf for leaf in leaves.values() if leaf['kind'] in ('observation', 'instrument')]
    guards = sum(leaf['kind'] == 'acceptance' for leaf in leaves.values())
    crosscuts = sum(leaf['kind'] == 'crosscut' for leaf in leaves.values())
    counts = {dim: dict(collections.Counter(leaf[dim]['verdict'] for leaf in counted)) for dim in DIMS}
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    text = ['# Tracera intent and domain evidence tree', '',
            '> GENERATED from STATUS.json. Do not edit this projection.', '',
            f'Generated: `{data["generated_at_utc"]}` | source SHA-256: `{digest}`', '',
            'Four dimensions remain separate. Counts are unique evidence leaves, not requirements or completion.',
            'Source-only observations qualify only their stated narrow criterion. Full parent closure requires every required child.',
            'A FAIL parent names a specific counterexample; UNKNOWN identifies unclosed children.', '',
            '## Intent tree', '', '```text']
    for goal in data['goals']:
        text.append(f'{goal["id"]} {goal["title"]}')
        text.append('  Criterion: ' + goal['criterion'])
        for dim in DIMS:
            text.append(cell_line(dim, parent_cell(goal, leaves, dim)))
    text += ['```', '', '## Domain overlays (aliases; excluded from leaf counts)', '']
    text.append('```text')
    for overlay in data['domains']:
        text.append(overlay['domain'] + ' -> ' + ', '.join(overlay['goals']))
        members = [g for g in data['goals'] if g['id'] in overlay['goals']]
        proxy = {'required_leaves': sorted({i for g in members for i in g['required_leaves']})}
        for dim in DIMS:
            text.append(cell_line(dim, parent_cell(proxy, leaves, dim)))
    text.append('```')
    text += ['', 'Each referenced goal has four independently derived cells above. Overlay aliases do not add acceptance.',
             '', '## Unique leaf cell counts', '', '| Verdict | Implementation | Usability | Validation | Assurance |',
             '|---|---:|---:|---:|---:|']
    for verdict in sorted(VOCAB):
        if any(counts[d].get(verdict, 0) for d in DIMS):
            text.append('| ' + verdict + ' | ' + ' | '.join(str(counts[d].get(verdict, 0)) for d in DIMS) + ' |')
    text += ['', f'Unique counted leaves: {len(counted)}. Criterion guards and crosscuts excluded: {len(leaves)-len(counted)} ({guards} whole-goal guards, {crosscuts} crosscuts). Parent and domain aliases excluded.', '',
             '## Detailed evidence', '', '[Acceptance leaves](acceptance.md) | [Interface leaves](interface.md) | [Backend and Desk leaves](backend.md) | [Store crosscuts](store.md)', '',
             'Scope and provenance: [README](README.md), [raw intent census](evidence/intent-report.json), [raw interface census](evidence/evidence-cells.json).', '',
             '## Cheapest remaining evidence work', '']
    text += ['- ' + item for item in data['next_evidence']]
    text += ['', '## Authority-dependent work', '']
    text += ['- ' + item for item in data['authority_dependencies']]
    (ROOT / 'STATUS.md').write_text('\n'.join(text) + '\n')
    for group in ('acceptance', 'interface', 'backend', 'store'):
        lines = [f'# {group.title()} evidence leaves', '', '> GENERATED from STATUS.json.', '', '```text']
        for leaf in leaves.values():
            if leaf['group'] != group:
                continue
            lines += [f'{leaf["id"]} [{leaf["kind"]}] {leaf["claim"]}']
            lines += [cell_line(dim, leaf[dim]) for dim in DIMS]
        lines += ['```', '']
        assert len(lines) <= 500, (group, len(lines))
        (ROOT / f'{group}.md').write_text('\n'.join(lines))
    print(json.dumps({'unique_leaves': len(counted), 'excluded_guards_and_crosscuts': len(leaves)-len(counted), 'counts': counts}, sort_keys=True))


if __name__ == '__main__':
    main()
