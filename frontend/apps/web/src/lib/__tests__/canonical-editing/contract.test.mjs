import test from 'node:test';
import assert from 'node:assert/strict';
import { canonicalItemPayload, scopedGraphPath } from '../../canonical-editing.ts';

test('same imported ID has distinct, encoded project mutation targets after switching projects', () => {
  const first = new URL(scopedGraphPath('items', 'FR-01/shared', 'project one'), 'https://tracera.example');
  const second = new URL(scopedGraphPath('items', 'FR-01/shared', 'project two'), 'https://tracera.example');
  assert.equal(first.searchParams.get('project_id'), 'project one');
  assert.equal(second.searchParams.get('project_id'), 'project two');
  assert.notEqual(first.href, second.href);
  assert.equal(first.pathname, '/api/v1/items/FR-01%2Fshared');
});
test('opaque link IDs are preserved and deletions require explicit project scope', () => {
  const path = scopedGraphPath('links', 'WyJhL2IiLCJjIiwidGVzdHMiXQ', 'demo&other');
  assert.equal(new URL(path, 'https://tracera.example').searchParams.get('project_id'), 'demo&other');
  assert.throws(() => scopedGraphPath('links', 'link', ''), /Select a project/);
  assert.throws(() => scopedGraphPath('items', 'item', '  '), /Select a project/);
});
test('create sends supported fields and explicitly supplies project provenance', () => {
  const input = { projectId: 'demo', title: 'Review contract', view: 'feature', type: 'task', status: 'draft', description: 'Current intent' };
  const body = JSON.parse(JSON.stringify(canonicalItemPayload(input, true)));
  assert.deepEqual(body, { project_id: 'demo', title: 'Review contract', view: 'feature', type: 'task', status: 'draft', description: 'Current intent' });
  assert.equal(input.projectId, 'demo');
});
test('edit cannot overwrite import provenance, ID, unsupported attributes or another project', () => {
  for (const [key, value] of Object.entries({ id: 'new', projectId: 'other', project_id: 'other', owner: 'me', priority: 'high', parentId: 'parent', metadata: {} })) {
    assert.throws(() => canonicalItemPayload({ title: 'edit', [key]: value }), /not supported/);
  }
  assert.deepEqual(canonicalItemPayload({ title: 'Changed', description: '' }), { title: 'Changed', description: '' });
});
test('unsupported create data is rejected before making a mutation', () => {
  assert.throws(() => canonicalItemPayload({ projectId: 'demo', title: 'test', priority: 'medium' }, true), /priority is not supported/);
  assert.throws(() => canonicalItemPayload({ title: 'test' }, true), /Select a project/);
});
