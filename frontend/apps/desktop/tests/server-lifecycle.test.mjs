import { describe, it } from 'node:test';
import assert from 'node:assert';
import { ServerLifecycle } from '../server-lifecycle.js';

describe('Server Lifecycle', () => {
  it('should start embedded server', async () => {
    const server = new ServerLifecycle();
    await server.start();
    assert.strictEqual(server.isRunning(), true);
    await server.stop();
  });

  it('should stop embedded server gracefully', async () => {
    const server = new ServerLifecycle();
    await server.start();
    await server.stop();
    assert.strictEqual(server.isRunning(), false);
  });

  it('should expose health endpoint', async () => {
    const server = new ServerLifecycle();
    await server.start();
    const health = await server.getHealth();
    assert.strictEqual(health.status, 'ok');
    await server.stop();
  });

  it('should handle restart', async () => {
    const server = new ServerLifecycle();
    await server.start();
    await server.restart();
    assert.strictEqual(server.isRunning(), true);
    await server.stop();
  });

  it('should track uptime', async () => {
    const server = new ServerLifecycle();
    await server.start();
    const uptime = server.getUptime();
    assert.ok(uptime >= 0);
    await server.stop();
  });
});
