import { describe, it } from 'node:test';
import assert from 'node:assert';
import { Logger } from '../logging.js';

describe('Logging System', () => {
  it('should initialize logger', () => {
    const logger = new Logger('test');
    assert.ok(logger);
  });

  it('should log info messages', () => {
    const logger = new Logger('test');
    const spy = logger.spy('info');
    logger.info('test message');
    assert.ok(spy.called);
  });

  it('should log error messages', () => {
    const logger = new Logger('test');
    const spy = logger.spy('error');
    logger.error('error message');
    assert.ok(spy.called);
  });

  it('should handle context', () => {
    const logger = new Logger('test', { context: 'unit-test' });
    assert.strictEqual(logger.getContext(), 'unit-test');
  });
});
