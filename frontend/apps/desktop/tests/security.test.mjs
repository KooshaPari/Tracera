import { describe, it } from 'node:test';
import assert from 'node:assert';
import { SecurityPolicy } from '../security.js';

describe('Security Policies', () => {
  it('should enforce CSP headers', () => {
    const security = new SecurityPolicy();
    const csp = security.getCSP();
    assert.ok(csp.includes("default-src 'self'"));
  });

  it('should validate URLs', () => {
    const security = new SecurityPolicy();
    assert.strictEqual(security.isValidUrl('http://localhost:8080'), true);
    assert.strictEqual(security.isValidUrl('javascript:alert(1)'), false);
  });

  it('should sanitize inputs', () => {
    const security = new SecurityPolicy();
    const clean = security.sanitize('<script>alert(1)</script>');
    assert.ok(!clean.includes('<script>'));
  });

  it('should handle navigation requests', () => {
    const security = new SecurityPolicy();
    assert.strictEqual(security.canNavigate('http://localhost'), true);
    assert.strictEqual(security.canNavigate('http://evil.com'), false);
  });
});
