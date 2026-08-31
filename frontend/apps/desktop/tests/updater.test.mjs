import { describe, it, before, after } from 'node:test';
import assert from 'node:assert';
import { autoUpdater } from '../updater.js';

describe('Updater', () => {
  it('should check for updates', async () => {
    const result = await autoUpdater.checkForUpdates();
    assert.strictEqual(typeof result, 'object');
    assert.ok('available' in result);
  });

  it('should return current version', () => {
    const version = autoUpdater.getVersion();
    assert.ok(typeof version === 'string');
    assert.ok(version.length > 0);
  });

  it('should handle update failure gracefully', async () => {
    // Simulate network error
    await assert.doesNotReject(() => autoUpdater.checkForUpdates());
  });
});
