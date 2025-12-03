# Security Tests

Comprehensive security testing suite for TraceRTM frontend application.

## Test Coverage

### 1. XSS Prevention (`xss.test.ts`)
- Script tag injection prevention
- Event handler sanitization
- URL protocol validation (javascript:, data:, etc.)
- DOM clobbering prevention
- React dangerouslySetInnerHTML protection
- Markdown XSS prevention
- Content Security Policy compatibility

### 2. Input Sanitization (`sanitization.test.ts`)
- Text input sanitization
- Email validation and normalization
- URL sanitization (protocol, private IPs)
- Rich text/HTML sanitization
- Filename sanitization (path traversal prevention)
- JSON input sanitization (prototype pollution)
- Search query sanitization
- Phone number validation
- Tag/label normalization
- Integer and date input validation

### 3. Authentication Security (`auth.test.tsx`)
- Token storage security (localStorage vs httpOnly cookies)
- JWT token validation and expiration
- Authentication state management
- Session security and timeout handling
- Password security best practices
- Role-Based Access Control (RBAC)
- CSRF protection
- Multi-Factor Authentication (MFA) support
- Account lockout protection
- Session fixation prevention
- Secure authentication headers
- User profile security

### 4. Input Validation (`input-validation.test.tsx`)
- Zod schema validation
- SQL injection prevention
- NoSQL injection prevention
- Command injection prevention
- Path traversal prevention
- Integer overflow protection
- ReDoS (Regular Expression Denial of Service) prevention
- File upload validation (extensions, size, MIME types)
- Prototype pollution prevention
- Unicode and special character handling
- Business logic validation
- Real-world form validation (CreateItemForm)

### 5. Content Security Policy (`csp.test.ts`)
- CSP directive validation
- Inline script prevention
- External resource validation
- Frame protection
- Subresource Integrity (SRI)
- CSP violation reporting
- Trusted Types API
- Script loading strategies
- Meta tag security
- WebSocket security

### 6. Security Headers (`headers.test.ts`)
- Content-Security-Policy configuration
- X-Frame-Options (clickjacking prevention)
- X-Content-Type-Options (MIME sniffing prevention)
- Strict-Transport-Security (HSTS)
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy
- CORS headers validation
- Cache-Control for sensitive data
- Cookie security attributes (Secure, HttpOnly, SameSite)
- Server information disclosure prevention
- Header injection prevention
- HTTP method security

## Running Tests

### Run All Security Tests
```bash
npm run test:security
```

### Watch Mode
```bash
npm run test:security:watch
```

### UI Mode
```bash
npm run test:security:ui
```

### Coverage Report
```bash
npm run test:security:coverage
```

## Security Test Principles

1. **Defense in Depth**: Multiple layers of security validation
2. **Fail Secure**: Tests validate secure defaults and error handling
3. **Input Validation**: All user inputs are validated and sanitized
4. **Output Encoding**: All outputs are properly encoded
5. **Least Privilege**: Tests verify minimal permissions model
6. **Security by Default**: Secure configurations are the default

## Common Attack Vectors Tested

- **XSS (Cross-Site Scripting)**: Script injection, HTML injection, attribute injection
- **CSRF (Cross-Site Request Forgery)**: Token validation, SameSite cookies
- **SQL/NoSQL Injection**: Parameter validation, query sanitization
- **Path Traversal**: Directory traversal prevention
- **Command Injection**: Shell command character filtering
- **Session Hijacking**: Token security, session management
- **Clickjacking**: Frame protection headers
- **MIME Sniffing**: Content-Type enforcement
- **Prototype Pollution**: Object validation
- **ReDoS**: Safe regex patterns

## Integration with CI/CD

Security tests are part of the CI/CD pipeline:

```yaml
- name: Run Security Tests
  run: npm run test:security

- name: Check Security Coverage
  run: npm run test:security:coverage
```

## Security Test Standards

### Test Naming Convention
```typescript
describe('Security Category', () => {
  describe('Specific Attack Type', () => {
    it('should prevent/enforce/validate specific behavior', () => {
      // Test implementation
    });
  });
});
```

### Test Structure
1. Arrange: Set up test data and conditions
2. Act: Execute the code under test
3. Assert: Verify security guarantees

### Coverage Requirements
- **Critical Security Functions**: 100% coverage
- **Security Utilities**: 100% coverage
- **Authentication/Authorization**: 100% coverage
- **Input Validation**: 100% coverage

## Security Testing Tools

- **Vitest**: Test runner and assertion library
- **Testing Library**: React component testing
- **DOMPurify**: HTML sanitization library
- **Zod**: Schema validation and type safety
- **crypto.subtle**: Cryptographic operations

## Best Practices

1. **Always test malicious inputs** alongside valid inputs
2. **Test boundary conditions** (min/max lengths, edge cases)
3. **Verify error handling** doesn't leak sensitive information
4. **Test with realistic attack payloads** from OWASP
5. **Keep tests updated** with new vulnerability patterns
6. **Document security assumptions** in test comments

## Security Checklist

- [ ] XSS prevention in all user inputs
- [ ] SQL/NoSQL injection prevention
- [ ] CSRF tokens on state-changing operations
- [ ] Secure token storage (not in localStorage for sensitive tokens)
- [ ] Input validation with Zod schemas
- [ ] Output sanitization with DOMPurify
- [ ] Security headers properly configured
- [ ] Authentication flows tested
- [ ] Authorization checks tested
- [ ] Session management tested

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [Secure Headers](https://securityheaders.com/)
- [DOMPurify Documentation](https://github.com/cure53/DOMPurify)
- [Zod Documentation](https://zod.dev/)

## Reporting Security Issues

If you discover a security vulnerability:
1. **DO NOT** open a public issue
2. Email security@tracertm.com with details
3. Include steps to reproduce
4. Wait for acknowledgment before disclosure

## Maintenance

Security tests should be reviewed and updated:
- **Monthly**: Check for new vulnerability patterns
- **After security incidents**: Add regression tests
- **Before major releases**: Full security test audit
- **When dependencies update**: Verify security test compatibility
