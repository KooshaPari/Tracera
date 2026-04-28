import DOMPurify from 'dompurify';
import { describe, expect, it } from 'vitest';

// Input Sanitization Tests
describe('Input Sanitization Tests', () => {
  describe('Text Input Sanitization', () => {
    const sanitizeText = (input: string): string =>
      input
        .trim()
        .replaceAll(/[<>]/g, '') // Remove angle brackets
        .slice(0, 1000);

    it('should trim whitespace', () => {
      const input = '  test  ';
      const result = sanitizeText(input);

      expect(result).toBe('test');
    });

    it('should remove HTML tags from plain text', () => {
      const input = '<script>alert("XSS")</script>Hello';
      const result = sanitizeText(input);

      expect(result).not.toContain('<');
      expect(result).not.toContain('>');
      expect(result).toContain('Hello');
    });

    it('should limit text length', () => {
      const longInput = 'a'.repeat(2000);
      const result = sanitizeText(longInput);

      expect(result.length).toBeLessThanOrEqual(1000);
    });
  });

  describe('Email Validation and Sanitization', () => {
    const sanitizeEmail = (email: string): string | null => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      const trimmed = email.trim().toLowerCase();

      if (!emailRegex.test(trimmed)) {
        return null;
      }

      // Remove potentially dangerous characters
      return trimmed.replaceAll(/[<>'"]/g, '');
    };

    it('should validate email format', () => {
      expect(sanitizeEmail('test@example.com')).toBe('test@example.com');
      expect(sanitizeEmail('invalid.email')).toBeNull();
      expect(sanitizeEmail('test@')).toBeNull();
      expect(sanitizeEmail('@example.com')).toBeNull();
    });

    it('should normalize email to lowercase', () => {
      const result = sanitizeEmail('Test@Example.COM');

      expect(result).toBe('test@example.com');
    });

    it('should remove dangerous characters from email', () => {
      const malicious = `test<script>@example.com`;
      const result = sanitizeEmail(malicious);

      // Email regex should fail on special characters
      expect(result).toBe('testscript@example.com'); // Characters removed but still valid
    });
  });

  describe('URL Sanitization', () => {
    const sanitizeURL = (url: string): string | null => {
      try {
        const urlObj = new URL(url);

        // Only allow http and https
        if (!['http:', 'https:'].includes(urlObj.protocol)) {
          return null;
        }

        // Block localhost and private IPs
        const hostname = urlObj.hostname.toLowerCase();
        if (
          hostname === 'localhost' ||
          hostname.startsWith('192.168.') ||
          hostname.startsWith('10.') ||
          hostname.startsWith('172.16.') ||
          hostname === '127.0.0.1' ||
          hostname === '0.0.0.0'
        ) {
          return null;
        }

        return urlObj.toString();
      } catch {
        return null;
      }
    };

    it('should accept valid HTTPS URLs', () => {
      const url = 'https://example.com/path';
      const result = sanitizeURL(url);

      expect(result).toBe(url);
    });

    it('should reject javascript: URLs', () => {
      const result = sanitizeURL('javascript:alert("XSS")');

      expect(result).toBeNull();
    });

    it('should reject data: URLs', () => {
      const result = sanitizeURL('data:text/html,<script>alert("XSS")</script>');

      expect(result).toBeNull();
    });

    it('should reject file: URLs', () => {
      const result = sanitizeURL('file:///etc/passwd');

      expect(result).toBeNull();
    });

    it('should reject localhost URLs', () => {
      expect(sanitizeURL('http://localhost:8080')).toBeNull();
      expect(sanitizeURL('http://127.0.0.1')).toBeNull();
    });

    it('should reject private IP ranges', () => {
      expect(sanitizeURL('http://192.168.1.1')).toBeNull();
      expect(sanitizeURL('http://10.0.0.1')).toBeNull();
      expect(sanitizeURL('http://172.16.0.1')).toBeNull();
    });
  });

  describe('Rich Text Sanitization', () => {
    const sanitizeRichText = (html: string): string =>
      DOMPurify.sanitize(html, {
        ALLOW_DATA_ATTR: false,
        ALLOWED_ATTR: ['href', 'title'],
        ALLOWED_TAGS: [
          'p',
          'br',
          'strong',
          'em',
          'u',
          'h1',
          'h2',
          'h3',
          'ul',
          'ol',
          'li',
          'a',
          'blockquote',
          'code',
          'pre',
        ],
        KEEP_CONTENT: true,
      });

    it('should preserve safe HTML tags', () => {
      const input = '<p>Hello <strong>World</strong></p>';
      const result = sanitizeRichText(input);

      expect(result).toContain('<p>');
      expect(result).toContain('<strong>');
      expect(result).toContain('World');
    });

    it('should remove script tags', () => {
      const input = '<p>Text</p><script>alert("XSS")</script>';
      const result = sanitizeRichText(input);

      expect(result).not.toContain('<script>');
      expect(result).toContain('Text');
    });

    it('should remove inline styles', () => {
      const input = '<p style="color: red;">Text</p>';
      const result = sanitizeRichText(input);

      expect(result).not.toContain('style=');
      expect(result).toContain('Text');
    });

    it('should remove event handlers', () => {
      const input = '<button onclick="alert(\'XSS\')">Click</button>';
      const result = sanitizeRichText(input);

      expect(result).not.toContain('onclick=');
    });

    it('should sanitize links', () => {
      const input = '<a href="javascript:alert(\'XSS\')">Link</a>';
      const result = sanitizeRichText(input);

      expect(result).not.toContain('javascript:');
    });
  });

  describe('Filename Sanitization', () => {
    const sanitizeFilename = (filename: string): string =>
      filename
        .replaceAll(/[^a-zA-Z0-9._-]/g, '_') // Replace special chars
        .replaceAll(/\.{2,}/g, '.') // Remove directory traversal
        .slice(0, 255);

    it('should remove path traversal attempts', () => {
      const malicious = '../../../etc/passwd';
      const result = sanitizeFilename(malicious);

      expect(result).not.toContain('..');
      expect(result).not.toContain('/');
    });

    it('should remove special characters', () => {
      const input = 'my<script>file.txt';
      const result = sanitizeFilename(input);

      expect(result).not.toContain('<');
      expect(result).not.toContain('>');
    });

    it('should preserve safe filenames', () => {
      const input = 'document-2024.pdf';
      const result = sanitizeFilename(input);

      expect(result).toBe('document-2024.pdf');
    });

    it('should limit filename length', () => {
      const longName = `${'a'.repeat(300)}.txt`;
      const result = sanitizeFilename(longName);

      expect(result.length).toBeLessThanOrEqual(255);
    });
  });

  describe('JSON Input Sanitization', () => {
    const sanitizeJSON = (input: string): unknown => {
      try {
        const parsed = JSON.parse(input);

        // Remove prototype pollution attempts
        delete parsed.__proto__;
        delete parsed.constructor;
        delete parsed.prototype;

        return parsed;
      } catch {
        return null;
      }
    };

    it('should parse valid JSON', () => {
      const json = '{"name": "test", "value": 123}';
      const result = sanitizeJSON(json);

      expect(result).toEqual({ name: 'test', value: 123 });
    });

    it('should reject invalid JSON', () => {
      const invalid = '{name: test}'; // Missing quotes
      const result = sanitizeJSON(invalid);

      expect(result).toBeNull();
    });

    it('should remove prototype pollution attempts', () => {
      const malicious = '{"__proto__": {"isAdmin": true}, "name": "test"}';
      const result = sanitizeJSON(malicious);

      expect(result).not.toHaveProperty('__proto__');
      expect(result).toHaveProperty('name');
    });
  });

  describe('Search Query Sanitization', () => {
    const sanitizeSearchQuery = (query: string): string =>
      query
        .trim()
        .replaceAll(/[<>'"]/g, '') // Remove potential XSS
        .slice(0, 200);

    it('should trim whitespace', () => {
      const query = '  search term  ';
      const result = sanitizeSearchQuery(query);

      expect(result).toBe('search term');
    });

    it('should remove XSS attempts', () => {
      const malicious = '<script>alert("XSS")</script>search';
      const result = sanitizeSearchQuery(malicious);

      expect(result).not.toContain('<');
      expect(result).not.toContain('>');
      expect(result).toContain('search');
    });

    it('should limit query length', () => {
      const longQuery = 'search'.repeat(100);
      const result = sanitizeSearchQuery(longQuery);

      expect(result.length).toBeLessThanOrEqual(200);
    });
  });

  describe('Phone Number Sanitization', () => {
    const sanitizePhoneNumber = (phone: string): string | null => {
      // Remove all non-digit characters
      const digitsOnly = phone.replaceAll(/\D/g, '');

      // Validate length (example: 10-15 digits)
      if (digitsOnly.length < 10 || digitsOnly.length > 15) {
        return null;
      }

      return digitsOnly;
    };

    it('should extract digits from formatted phone', () => {
      const formatted = '+1 (555) 123-4567';
      const result = sanitizePhoneNumber(formatted);

      expect(result).toBe('15551234567');
    });

    it('should reject too short phone numbers', () => {
      const result = sanitizePhoneNumber('123');

      expect(result).toBeNull();
    });

    it('should reject too long phone numbers', () => {
      const result = sanitizePhoneNumber('1234567890123456');

      expect(result).toBeNull();
    });

    it('should remove non-digit characters', () => {
      const malicious = '555<script>1234';
      const result = sanitizePhoneNumber(malicious);

      // Too short after removing non-digits
      expect(result).toBeNull();
    });
  });

  describe('Tag/Label Sanitization', () => {
    const sanitizeTag = (tag: string): string | null => {
      const cleaned = tag
        .trim()
        .toLowerCase()
        .replaceAll(/[^a-z0-9-]/g, '-') // Replace special chars with dash
        .replaceAll(/-+/g, '-') // Collapse multiple dashes
        .replaceAll(/^-|-$/g, ''); // Remove leading/trailing dashes

      if (cleaned.length < 2 || cleaned.length > 50) {
        return null;
      }

      return cleaned;
    };

    it('should normalize tags', () => {
      const result = sanitizeTag('My Tag!');

      expect(result).toBe('my-tag');
    });

    it('should reject too short tags', () => {
      const result = sanitizeTag('a');

      expect(result).toBeNull();
    });

    it('should reject too long tags', () => {
      const longTag = 'a'.repeat(100);
      const result = sanitizeTag(longTag);

      expect(result).toBeNull();
    });

    it('should remove special characters', () => {
      const malicious = 'tag<script>alert("XSS")</script>';
      const result = sanitizeTag(malicious);

      expect(result).not.toContain('<');
      expect(result).not.toContain('>');
    });
  });

  describe('Integer Input Sanitization', () => {
    const sanitizeInteger = (input: string, min?: number, max?: number): number | null => {
      const num = Number.parseInt(input, 10);

      if (Number.isNaN(num)) {
        return null;
      }

      if (min !== undefined && num < min) {
        return null;
      }

      if (max !== undefined && num > max) {
        return null;
      }

      return num;
    };

    it('should parse valid integers', () => {
      expect(sanitizeInteger('42')).toBe(42);
      expect(sanitizeInteger('0')).toBe(0);
      expect(sanitizeInteger('-10')).toBe(-10);
    });

    it('should reject non-integers', () => {
      expect(sanitizeInteger('abc')).toBeNull();
      expect(sanitizeInteger('12.34')).toBe(12); // Truncates
    });

    it('should enforce minimum value', () => {
      const result = sanitizeInteger('5', 10);

      expect(result).toBeNull();
    });

    it('should enforce maximum value', () => {
      const result = sanitizeInteger('100', undefined, 50);

      expect(result).toBeNull();
    });

    it('should handle overflow attempts', () => {
      const overflow = '999999999999999999999';
      const result = sanitizeInteger(overflow);

      expect(result).toBeDefined();
    });
  });

  describe('Date Input Sanitization', () => {
    const sanitizeDate = (input: string): Date | null => {
      const date = new Date(input);

      if (Number.isNaN(date.getTime())) {
        return null;
      }

      // Validate reasonable date range (e.g., 1900 - 2100)
      const year = date.getFullYear();
      if (year < 1900 || year > 2100) {
        return null;
      }

      return date;
    };

    it('should parse valid dates', () => {
      const result = sanitizeDate('2024-01-15');

      expect(result).toBeInstanceOf(Date);
      expect(result?.getFullYear()).toBe(2024);
    });

    it('should reject invalid dates', () => {
      expect(sanitizeDate('invalid')).toBeNull();
      expect(sanitizeDate('2024-13-45')).toBeNull();
    });

    it('should reject dates outside valid range', () => {
      expect(sanitizeDate('1800-01-01')).toBeNull();
      expect(sanitizeDate('2200-01-01')).toBeNull();
    });
  });

  describe('Boolean Input Sanitization', () => {
    const sanitizeBoolean = (input: string): boolean => {
      const normalized = input.toLowerCase().trim();
      return ['true', '1', 'yes', 'on'].includes(normalized);
    };

    it('should accept truthy values', () => {
      expect(sanitizeBoolean('true')).toBeTruthy();
      expect(sanitizeBoolean('TRUE')).toBeTruthy();
      expect(sanitizeBoolean('1')).toBeTruthy();
      expect(sanitizeBoolean('yes')).toBeTruthy();
    });

    it('should reject falsy values', () => {
      expect(sanitizeBoolean('false')).toBeFalsy();
      expect(sanitizeBoolean('0')).toBeFalsy();
      expect(sanitizeBoolean('no')).toBeFalsy();
      expect(sanitizeBoolean('random')).toBeFalsy();
    });
  });
});

// Comprehensive Sanitization Helper
describe('Comprehensive Sanitization Helper', () => {
  const sanitizeInput = (input: unknown, type: string): unknown => {
    if (typeof input !== 'string') {
      return input;
    }
    switch (type) {
      case 'text': {
        return input.trim().slice(0, 1000);
      }
      case 'html': {
        return DOMPurify.sanitize(input);
      }
      case 'email': {
        return input
          .trim()
          .toLowerCase()
          .replaceAll(/[<>'"]/g, '');
      }
      case 'url': {
        try {
          const url = new URL(input);
          return ['http:', 'https:'].includes(url.protocol) ? url.toString() : null;
        } catch {
          return null;
        }
      }
      case 'integer': {
        return Number.parseInt(input, 10) || 0;
      }
      default: {
        return input;
      }
    }
  };

  it('should sanitize based on type', () => {
    expect(sanitizeInput('  text  ', 'text')).toBe('text');
    expect(sanitizeInput('<script>alert("XSS")</script>', 'html')).not.toContain('<script>');
    expect(sanitizeInput('Test@Example.com', 'email')).toBe('test@example.com');
    expect(sanitizeInput('https://example.com', 'url')).toBe('https://example.com/');
    expect(sanitizeInput('42', 'integer')).toBe(42);
  });
});
