import { describe, it } from 'node:test';
import assert from 'node:assert';
import { TrayMenu } from '../tray-menu.js';

describe('Tray Menu', () => {
  it('should initialize tray menu', () => {
    const tray = new TrayMenu();
    assert.ok(tray);
  });

  it('should create menu items', () => {
    const tray = new TrayMenu();
    const items = tray.getItems();
    assert.ok(Array.isArray(items));
    assert.ok(items.length > 0);
  });

  it('should handle menu item clicks', () => {
    const tray = new TrayMenu();
    let clicked = false;
    tray.on('click', () => { clicked = true; });
    tray.clickItem('test-item');
    assert.strictEqual(clicked, true);
  });

  it('should show/hide tray', () => {
    const tray = new TrayMenu();
    tray.show();
    assert.strictEqual(tray.isVisible(), true);
    tray.hide();
    assert.strictEqual(tray.isVisible(), false);
  });
});
