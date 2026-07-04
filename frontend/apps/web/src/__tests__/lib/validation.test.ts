import { describe, it, expect } from 'vitest';

import {
  isValidUUID,
  isValidEmail,
  isValidURL,
  validateLength,
  validateRequired,
  validatePasswordStrength,
  validatePasswordMatch,
  validateFileSize,
  validateFileType,
  validateFilename,
  hasPathTraversal,
  containsXSS,
  containsSQLInjection,
  sanitizeString,
  validateEnum,
  combineValidators,
} from '@/lib/validation/form-validators';
import {
  createItemSchema,
  loginSchema,
  registerSchema,
  emailSchema,
  passwordSchema,
  uuidSchema,
} from '@/lib/validation/schemas';

describe('UUID Validation', () => {
  it('validates correct UUIDs', () => {
    expect(isValidUUID('550e8400-e29b-41d4-a716-446655440000')).toBe(true);
    expect(isValidUUID('123e4567-e89b-12d3-a456-426614174000')).toBe(true);
  });

  it('rejects invalid UUIDs', () => {
    expect(isValidUUID('invalid-uuid')).toBe(false);
    expect(isValidUUID('')).toBe(false);
    expect(isValidUUID('550e8400-e29b-41d4-a716')).toBe(false);
    expect(isValidUUID('550e8400e29b41d4a716446655440000')).toBe(false); // Missing hyphens
  });

  it('validates with Zod schema', () => {
    expect(() => uuidSchema.parse('550e8400-e29b-41d4-a716-446655440000')).not.toThrow();
    expect(() => uuidSchema.parse('invalid')).toThrow();
  });
});

describe('Email Validation', () => {
  it('validates correct emails', () => {
    expect(isValidEmail('user@example.com')).toBe(true);
    expect(isValidEmail('user+tag@example.com')).toBe(true);
    expect(isValidEmail('user.name@example.co.uk')).toBe(true);
  });

  it('rejects invalid emails', () => {
    expect(isValidEmail('')).toBe(false);
    expect(isValidEmail('invalid')).toBe(false);
    expect(isValidEmail('@example.com')).toBe(false);
    expect(isValidEmail('user@')).toBe(false);
    expect(isValidEmail('user @example.com')).toBe(false);
  });

  it('validates with Zod schema', () => {
    expect(() => emailSchema.parse('user@example.com')).not.toThrow();
    expect(() => emailSchema.parse('invalid')).toThrow();
    expect(() => emailSchema.parse('')).toThrow();
  });
});

describe('URL Validation', () => {
  it('validates correct URLs', () => {
    expect(isValidURL('http://example.com')).toBe(true);
    expect(isValidURL('https://example.com')).toBe(true);
    expect(isValidURL('https://example.com/path?query=value')).toBe(true);
  });

  it('rejects invalid URLs', () => {
    expect(isValidURL('')).toBe(false);
    expect(isValidURL('not-a-url')).toBe(false);
    expect(isValidURL('ftp://example.com')).toBe(false);
  });
});

describe('String Length Validation', () => {
  it('validates strings within range', () => {
    expect(validateLength('hello', 1, 10)).toBeUndefined();
    expect(validateLength('hello', 5, 10)).toBeUndefined();
  });

  it('rejects strings outside range', () => {
    expect(validateLength('hi', 5, 10)).toBeDefined();
    expect(validateLength('hello world!', 1, 5)).toBeDefined();
  });

  it('trims whitespace before validation', () => {
    expect(validateLength('  hello  ', 5, 10)).toBeUndefined();
  });
});

describe('Required Field Validation', () => {
  it('accepts non-empty values', () => {
    expect(validateRequired('value')).toBeUndefined();
  });

  it('rejects empty values', () => {
    expect(validateRequired('')).toBeDefined();
    expect(validateRequired('   ')).toBeDefined();
    expect(validateRequired(null)).toBeDefined();
    expect(validateRequired(undefined)).toBeDefined();
  });
});

describe('Password Validation', () => {
  it('validates strong passwords', () => {
    expect(validatePasswordStrength('Password123')).toBeUndefined();
    expect(validatePasswordStrength('MyP@ssw0rd')).toBeUndefined();
  });

  it('rejects weak passwords', () => {
    expect(validatePasswordStrength('short')).toBeDefined();
    expect(validatePasswordStrength('alllowercase')).toBeDefined();
    expect(validatePasswordStrength('ALLUPPERCASE')).toBeDefined();
    expect(validatePasswordStrength('NoNumbers')).toBeDefined();
  });

  it('validates password matching', () => {
    expect(validatePasswordMatch('Password123', 'Password123')).toBeUndefined();
    expect(validatePasswordMatch('Password123', 'Different123')).toBeDefined();
  });

  it('validates with Zod schema', () => {
    expect(() => passwordSchema.parse('Password123')).not.toThrow();
    expect(() => passwordSchema.parse('weak')).toThrow();
  });
});

describe('File Validation', () => {
  it('validates file size', () => {
    const smallFile = new File(['a'.repeat(1000)], 'test.txt');
    const largeFile = new File(['a'.repeat(10000000)], 'test.txt');

    expect(validateFileSize(smallFile, 5000)).toBeUndefined();
    expect(validateFileSize(largeFile, 5000)).toBeDefined();
  });

  it('validates file type', () => {
    const allowedTypes = ['image/jpeg', 'image/png'];

    expect(
      validateFileType(new File([], 'test.jpg', { type: 'image/jpeg' }), allowedTypes),
    ).toBeUndefined();

    expect(
      validateFileType(new File([], 'test.gif', { type: 'image/gif' }), allowedTypes),
    ).toBeDefined();
  });

  it('validates filename', () => {
    expect(validateFilename('document.pdf')).toBeUndefined();
    expect(validateFilename('../etc/passwd')).toBeDefined();
    expect(validateFilename('file\0.txt')).toBeDefined();
    expect(validateFilename('a'.repeat(256))).toBeDefined();
  });
});

describe('Security Validation', () => {
  it('detects path traversal', () => {
    expect(hasPathTraversal('../etc/passwd')).toBe(true);
    expect(hasPathTraversal('..\\windows\\system32')).toBe(true);
    expect(hasPathTraversal('uploads/file.txt')).toBe(false);
  });

  it('detects XSS attempts', () => {
    expect(containsXSS("<script>alert('XSS')</script>")).toBe(true);
    expect(containsXSS("<iframe src='evil.com'></iframe>")).toBe(true);
    expect(containsXSS("javascript:alert('XSS')")).toBe(true);
    expect(containsXSS("<div onclick='alert()'>")).toBe(true);
    expect(containsXSS('Hello World')).toBe(false);
  });

  it('detects SQL injection attempts', () => {
    expect(containsSQLInjection("'; DROP TABLE users--")).toBe(true);
    expect(containsSQLInjection('1 UNION SELECT * FROM users')).toBe(true);
    expect(containsSQLInjection('/* comment */')).toBe(true);
    expect(containsSQLInjection('Normal text')).toBe(false);
  });
});

describe('Sanitization', () => {
  it('sanitizes strings', () => {
    expect(sanitizeString('  hello  ')).toBe('hello');
    expect(sanitizeString('hello\0world')).toBe('helloworld');
  });
});

describe('Enum Validation', () => {
  it('validates enum values', () => {
    const statuses = ['draft', 'published', 'archived'] as const;

    expect(validateEnum('draft', statuses)).toBeUndefined();
    expect(validateEnum('invalid', statuses)).toBeDefined();
  });
});

describe('Validator Composition', () => {
  it('combines multiple validators', () => {
    const validator = combineValidators(
      (value: string) => validateRequired(value, 'Field'),
      (value: string) => validateLength(value, 5, 10, 'Field'),
    );

    expect(validator('hello')).toBeUndefined();
    expect(validator('')).toBeDefined();
    expect(validator('hi')).toBeDefined();
    expect(validator('hello world!')).toBeDefined();
  });
});

describe('Schema Validation', () => {
  describe('Login Schema', () => {
    it('validates correct login data', () => {
      const data = {
        email: 'user@example.com',
        password: 'password123',
      };
      expect(() => loginSchema.parse(data)).not.toThrow();
    });

    it('rejects invalid login data', () => {
      expect(() => loginSchema.parse({ email: 'invalid', password: 'pass' })).toThrow();
      expect(() => loginSchema.parse({ email: 'user@example.com', password: '' })).toThrow();
    });
  });

  describe('Register Schema', () => {
    it('validates correct registration data', () => {
      const data = {
        email: 'user@example.com',
        password: 'Password123',
        name: 'John Doe',
        confirmPassword: 'Password123',
      };
      expect(() => registerSchema.parse(data)).not.toThrow();
    });

    it('rejects mismatched passwords', () => {
      const data = {
        email: 'user@example.com',
        password: 'Password123',
        name: 'John Doe',
        confirmPassword: 'Different123',
      };
      expect(() => registerSchema.parse(data)).toThrow();
    });

    it('rejects weak passwords', () => {
      const data = {
        email: 'user@example.com',
        password: 'weak',
        name: 'John Doe',
        confirmPassword: 'weak',
      };
      expect(() => registerSchema.parse(data)).toThrow();
    });
  });

  describe('Create Item Schema', () => {
    it('validates correct item data', () => {
      const data = {
        title: 'Test Item',
        description: 'Test description',
        view: 'FEATURE',
        type: 'feature',
        status: 'todo',
        priority: 'medium',
        projectId: '550e8400-e29b-41d4-a716-446655440000',
      };
      expect(() => createItemSchema.parse(data)).not.toThrow();
    });

    it('rejects invalid item data', () => {
      const data = {
        title: '', // Empty title
        view: 'FEATURE',
        type: 'feature',
        status: 'todo',
        priority: 'medium',
        projectId: '550e8400-e29b-41d4-a716-446655440000',
      };
      expect(() => createItemSchema.parse(data)).toThrow();
    });

    it('rejects invalid UUID', () => {
      const data = {
        title: 'Test',
        view: 'FEATURE',
        type: 'feature',
        status: 'todo',
        priority: 'medium',
        projectId: 'invalid-uuid',
      };
      expect(() => createItemSchema.parse(data)).toThrow();
    });

    it('rejects invalid enum values', () => {
      const data = {
        title: 'Test',
        view: 'INVALID',
        type: 'feature',
        status: 'todo',
        priority: 'medium',
        projectId: '550e8400-e29b-41d4-a716-446655440000',
      };
      expect(() => createItemSchema.parse(data)).toThrow();
    });
  });
});
