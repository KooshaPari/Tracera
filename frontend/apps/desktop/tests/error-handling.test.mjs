import { describe, it } from 'node:test';
import assert from 'node:assert';
import { ErrorHandler } from '../error-handling.js';

describe('Error Recovery', () => {
  it('should catch unhandled errors', () => {
    const handler = new ErrorHandler();
    handler.init();
    assert.ok(handler.isActive());
  });

  it('should log errors correctly', () => {
    const handler = new ErrorHandler();
    const logSpy = handler.spy('log');
    handler.handleError(new Error('test'));
    assert.ok(logSpy.called);
  });

  it('should recover from crashes', async () => {
    const handler = new ErrorHandler();
    await handler.recover();
    assert.ok(handler.isRecovered());
  });

  it('should provide error context', () => {
    const handler = new ErrorHandler();
    const error = new Error('test');
    const context = handler.getContext(error);
    assert.ok(context.message);
    assert.ok(context.stack);
  });
});
