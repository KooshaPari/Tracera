import { describe, it } from 'node:test';
import assert from 'node:assert';
import { E2EDesktopTest } from '../e2e_desktop.js';

describe('Desktop Integration', () => {
  it('should launch full application', async () => {
    const app = new E2EDesktopTest();
    await app.launch();
    assert.ok(app.isRunning());
    await app.quit();
  });

  it('should navigate between views', async () => {
    const app = new E2EDesktopTest();
    await app.launch();
    await app.navigate('/settings');
    assert.ok(app.isInView('settings'));
    await app.quit();
  });

  it('should persist user settings', async () => {
    const app = new E2EDesktopTest();
    await app.launch();
    await app.setSetting('theme', 'dark');
    assert.strictEqual(app.getSetting('theme'), 'dark');
    await app.quit();
  });

  it('should handle window state changes', async () => {
    const app = new E2EDesktopTest();
    await app.launch();
    app.minimize();
    assert.ok(app.isMinimized());
    app.restore();
    assert.ok(!app.isMinimized());
    await app.quit();
  });

  it('should complete E2E workflow', async () => {
    const app = new E2EDesktopTest();
    await app.launch();
    await app.login('testuser');
    await app.navigate('/dashboard');
    const title = await app.getTitle();
    assert.ok(title.includes('Dashboard'));
    await app.quit();
  });
});
