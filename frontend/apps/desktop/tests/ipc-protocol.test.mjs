import { describe, it } from 'node:test';
import assert from 'node:assert';
import { IPCProtocol } from '../ipc-protocol.js';

describe('IPC Protocol', () => {
  it('should register message handlers', () => {
    const ipc = new IPCProtocol();
    ipc.register('test', () => {});
    assert.ok(ipc.hasHandler('test'));
  });

  it('should send and receive messages', async () => {
    const ipc = new IPCProtocol();
    ipc.register('echo', (msg) => msg);
    const response = await ipc.send('echo', { data: 'hello' });
    assert.deepStrictEqual(response, { data: 'hello' });
  });

  it('should handle unknown channels', async () => {
    const ipc = new IPCProtocol();
    try {
      await ipc.send('unknown', {});
    } catch (e) {
      assert.ok(e.message.includes('unknown'));
    }
  });

  it('should serialize complex objects', async () => {
    const ipc = new IPCProtocol();
    ipc.register('complex', (msg) => msg);
    const data = { nested: { array: [1, 2, 3] } };
    const response = await ipc.send('complex', data);
    assert.deepStrictEqual(response, data);
  });
});
