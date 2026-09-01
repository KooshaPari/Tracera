import { describe, it } from 'node:test';
import assert from 'node:assert';
import { DesktopConfig } from '../config.js';

describe('Desktop Configuration', () => {
  it('should load default configuration', () => {
    const config = new DesktopConfig();
    assert.ok(config.data);
    assert.ok(config.data.theme);
  });

  it('should allow configuration updates', () => {
    const config = new DesktopConfig();
    config.set('theme', 'dark');
    assert.strictEqual(config.get('theme'), 'dark');
  });

  it('should persist configuration changes', () => {
    const config = new DesktopConfig();
    config.set('debug', true);
    assert.strictEqual(config.get('debug'), true);
  });

  it('should validate configuration schema', () => {
    const config = new DesktopConfig();
    const isValid = config.validate();
    assert.strictEqual(isValid, true);
  });
});
