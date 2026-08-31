import { describe, it } from 'node:test';
import assert from 'node:assert';
import { WindowManager } from '../window-management.js';

describe('Window Management', () => {
  it('should create new window', () => {
    const wm = new WindowManager();
    const win = wm.create({ url: 'index.html' });
    assert.ok(win);
    assert.ok(win.id);
  });

  it('should focus existing window', () => {
    const wm = new WindowManager();
    const win = wm.create({ url: 'index.html' });
    wm.focus(win.id);
    assert.strictEqual(wm.getFocused(), win.id);
  });

  it('should minimize window', () => {
    const wm = new WindowManager();
    const win = wm.create({ url: 'index.html' });
    wm.minimize(win.id);
    assert.ok(wm.isMinimized(win.id));
  });

  it('should close window', () => {
    const wm = new WindowManager();
    const win = wm.create({ url: 'index.html' });
    wm.close(win.id);
    assert.strictEqual(wm.get(win.id), null);
  });
});
