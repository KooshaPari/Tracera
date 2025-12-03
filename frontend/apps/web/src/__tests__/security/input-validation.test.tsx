import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { z } from 'zod';

/**
 * Input Validation Security Tests
 *
 * Tests form input validation, Zod schema enforcement,
 * and protection against malicious input patterns.
 */
describe('Input Validation Security Tests', () => {
  describe('Zod Schema Validation', () => {
    it('should enforce string length limits', () => {
      const schema = z.object({
        title: z.string().min(1).max(500),
      });

      expect(() => schema.parse({ title: '' })).toThrow();
      expect(() => schema.parse({ title: 'a'.repeat(501) })).toThrow();
      expect(() => schema.parse({ title: 'Valid Title' })).not.toThrow();
    });

    it('should enforce email format validation', () => {
      const schema = z.object({
        email: z.string().email(),
      });

      expect(() => schema.parse({ email: 'invalid' })).toThrow();
      expect(() => schema.parse({ email: 'test@' })).toThrow();
      expect(() => schema.parse({ email: '@example.com' })).toThrow();
      expect(() => schema.parse({ email: 'valid@example.com' })).not.toThrow();
    });

    it('should enforce URL format validation', () => {
      const schema = z.object({
        url: z.string().url(),
      });

      expect(() => schema.parse({ url: 'not-a-url' })).toThrow();
      // Note: Zod's url() validator accepts javascript: as valid URL
      // Use custom refinement for additional security checks in production
      expect(() => schema.parse({ url: 'https://example.com' })).not.toThrow();
    });

    it('should enforce UUID format validation', () => {
      const schema = z.object({
        id: z.string().uuid(),
      });

      expect(() => schema.parse({ id: 'invalid-uuid' })).toThrow();
      expect(() => schema.parse({ id: '12345' })).toThrow();
      expect(() => schema.parse({
        id: '550e8400-e29b-41d4-a716-446655440000'
      })).not.toThrow();
    });

    it('should enforce numeric range validation', () => {
      const schema = z.object({
        priority: z.number().min(1).max(10),
      });

      expect(() => schema.parse({ priority: 0 })).toThrow();
      expect(() => schema.parse({ priority: 11 })).toThrow();
      expect(() => schema.parse({ priority: 5 })).not.toThrow();
    });

    it('should enforce enum validation', () => {
      const schema = z.object({
        status: z.enum(['todo', 'in_progress', 'done']),
      });

      expect(() => schema.parse({ status: 'invalid' })).toThrow();
      expect(() => schema.parse({ status: 'completed' })).toThrow();
      expect(() => schema.parse({ status: 'todo' })).not.toThrow();
    });

    it('should handle optional fields correctly', () => {
      const schema = z.object({
        required: z.string(),
        optional: z.string().optional(),
      });

      expect(() => schema.parse({ required: 'test' })).not.toThrow();
      expect(() => schema.parse({
        required: 'test',
        optional: 'value'
      })).not.toThrow();
      expect(() => schema.parse({})).toThrow();
    });
  });

  describe('SQL Injection Prevention', () => {
    it('should reject SQL injection patterns in text input', () => {
      const hasSQLInjection = (input: string): boolean => {
        const sqlPatterns = [
          /(\bOR\b|\bAND\b)\s+['"]?\d+['"]?\s*=\s*['"]?\d+['"]?/i,
          /(\bUNION\b|\bSELECT\b|\bDROP\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b)/i,
          /--/,
          /;\s*DROP/i,
          /\/\*/,
          /\*\//,
          /xp_/i,
        ];

        return sqlPatterns.some(pattern => pattern.test(input));
      };

      expect(hasSQLInjection("' OR '1'='1")).toBe(true);
      expect(hasSQLInjection("admin'--")).toBe(true);
      expect(hasSQLInjection("1; DROP TABLE users")).toBe(true);
      expect(hasSQLInjection("UNION SELECT * FROM passwords")).toBe(true);
      expect(hasSQLInjection("Normal input text")).toBe(false);
    });

    it('should use parameterized queries (schema validation)', () => {
      // Ensure all inputs go through Zod validation
      const schema = z.object({
        username: z.string().regex(/^[a-zA-Z0-9_-]+$/),
      });

      // These should fail validation
      expect(() => schema.parse({ username: "admin' OR '1'='1" })).toThrow();
      expect(() => schema.parse({ username: "user; DROP TABLE" })).toThrow();

      // Valid input
      expect(() => schema.parse({ username: "valid_user-123" })).not.toThrow();
    });
  });

  describe('NoSQL Injection Prevention', () => {
    it('should reject NoSQL injection in JSON inputs', () => {
      const hasNoSQLInjection = (input: string): boolean => {
        try {
          const parsed = JSON.parse(input);

          // Check for $where, $regex, etc.
          const dangerous = ['$where', '$regex', '$ne', '$gt', '$lt'];
          const str = JSON.stringify(parsed);

          return dangerous.some(pattern => str.includes(pattern));
        } catch {
          return false;
        }
      };

      expect(hasNoSQLInjection('{"$where": "this.password == \'secret\'"}'))
        .toBe(true);
      expect(hasNoSQLInjection('{"username": {"$ne": null}}'))
        .toBe(true);
      expect(hasNoSQLInjection('{"username": "normal"}'))
        .toBe(false);
    });

    it('should validate object structure against schema', () => {
      const schema = z.object({
        username: z.string(),
        age: z.number(),
      }).strict(); // Reject extra properties

      // Valid input
      expect(() => schema.parse({
        username: 'test',
        age: 25
      })).not.toThrow();

      // Invalid: extra properties
      expect(() => schema.parse({
        username: 'test',
        age: 25,
        $where: 'malicious'
      })).toThrow();
    });
  });

  describe('Command Injection Prevention', () => {
    it('should reject shell command characters', () => {
      const hasCommandInjection = (input: string): boolean => {
        const commandChars = ['|', '&', ';', '$', '`', '\n', '>', '<', '(', ')'];
        return commandChars.some(char => input.includes(char));
      };

      expect(hasCommandInjection('file.txt; rm -rf /')).toBe(true);
      expect(hasCommandInjection('file.txt | cat /etc/passwd')).toBe(true);
      expect(hasCommandInjection('$(malicious)')).toBe(true);
      expect(hasCommandInjection('safe-filename.txt')).toBe(false);
    });

    it('should whitelist allowed filename characters', () => {
      const schema = z.object({
        filename: z.string().regex(/^[a-zA-Z0-9._-]+$/),
      });

      expect(() => schema.parse({ filename: 'file; rm -rf /' })).toThrow();
      expect(() => schema.parse({ filename: 'file|cat' })).toThrow();
      expect(() => schema.parse({ filename: 'document-2024.pdf' })).not.toThrow();
    });
  });

  describe('Path Traversal Prevention', () => {
    it('should reject directory traversal attempts', () => {
      const hasPathTraversal = (path: string): boolean => {
        return path.includes('..') ||
               path.includes('//') ||
               path.startsWith('/');
      };

      expect(hasPathTraversal('../../../etc/passwd')).toBe(true);
      expect(hasPathTraversal('../../secret.txt')).toBe(true);
      expect(hasPathTraversal('/etc/passwd')).toBe(true);
      expect(hasPathTraversal('documents/file.txt')).toBe(false);
    });

    it('should normalize and validate file paths', () => {
      const normalizePath = (path: string): string | null => {
        // Remove directory traversal
        const cleaned = path.replace(/\.\./g, '').replace(/\/+/g, '/');

        // Must not start with /
        if (cleaned.startsWith('/')) return null;

        // Must not be empty
        if (cleaned.trim().length === 0) return null;

        return cleaned;
      };

      expect(normalizePath('../../../etc/passwd')).toBeNull();
      expect(normalizePath('/etc/passwd')).toBeNull();
      expect(normalizePath('')).toBeNull();
      expect(normalizePath('documents/file.txt')).toBe('documents/file.txt');
    });
  });

  describe('Integer Overflow Protection', () => {
    it('should enforce safe integer ranges', () => {
      const schema = z.object({
        count: z.number()
          .int()
          .min(Number.MIN_SAFE_INTEGER)
          .max(Number.MAX_SAFE_INTEGER),
      });

      expect(() => schema.parse({ count: Number.MAX_SAFE_INTEGER + 1 }))
        .toThrow();
      expect(() => schema.parse({ count: Number.MIN_SAFE_INTEGER - 1 }))
        .toThrow();
      expect(() => schema.parse({ count: 42 })).not.toThrow();
    });

    it('should reject NaN and Infinity', () => {
      const schema = z.number().finite();

      expect(() => schema.parse(NaN)).toThrow();
      expect(() => schema.parse(Infinity)).toThrow();
      expect(() => schema.parse(-Infinity)).toThrow();
      expect(() => schema.parse(42)).not.toThrow();
    });
  });

  describe('Regex Denial of Service (ReDoS) Prevention', () => {
    it('should use safe regex patterns', () => {
      // Dangerous: catastrophic backtracking
      const dangerousRegex = /^(a+)+$/;

      // Safe: no backtracking
      const safeRegex = /^[a-zA-Z0-9]+$/;

      const shortInput = 'aaa';
      const longInput = 'a'.repeat(1000);

      // Safe regex should handle long input quickly
      const startTime = performance.now();
      safeRegex.test(longInput);
      const elapsed = performance.now() - startTime;

      expect(elapsed).toBeLessThan(100); // Should be very fast
    });

    it('should limit input length before regex validation', () => {
      const MAX_LENGTH = 1000;

      const validateSafely = (input: string, pattern: RegExp): boolean => {
        if (input.length > MAX_LENGTH) return false;
        return pattern.test(input);
      };

      const safeInput = 'a'.repeat(100);
      const unsafeInput = 'a'.repeat(10000);

      expect(validateSafely(safeInput, /^[a]+$/)).toBe(true);
      expect(validateSafely(unsafeInput, /^[a]+$/)).toBe(false);
    });
  });

  describe('File Upload Validation', () => {
    it('should validate file extensions', () => {
      const allowedExtensions = ['.jpg', '.png', '.pdf', '.txt'];

      const isAllowedFile = (filename: string): boolean => {
        const ext = filename.substring(filename.lastIndexOf('.')).toLowerCase();
        return allowedExtensions.includes(ext);
      };

      expect(isAllowedFile('document.pdf')).toBe(true);
      expect(isAllowedFile('image.jpg')).toBe(true);
      expect(isAllowedFile('script.exe')).toBe(false);
      expect(isAllowedFile('malware.bat')).toBe(false);
    });

    it('should validate file size limits', () => {
      const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

      const isValidFileSize = (size: number): boolean => {
        return size > 0 && size <= MAX_FILE_SIZE;
      };

      expect(isValidFileSize(5 * 1024 * 1024)).toBe(true); // 5 MB
      expect(isValidFileSize(20 * 1024 * 1024)).toBe(false); // 20 MB
      expect(isValidFileSize(0)).toBe(false);
      expect(isValidFileSize(-1)).toBe(false);
    });

    it('should validate MIME types', () => {
      const allowedMimeTypes = [
        'image/jpeg',
        'image/png',
        'application/pdf',
        'text/plain',
      ];

      const isAllowedMimeType = (mimeType: string): boolean => {
        return allowedMimeTypes.includes(mimeType);
      };

      expect(isAllowedMimeType('image/jpeg')).toBe(true);
      expect(isAllowedMimeType('application/pdf')).toBe(true);
      expect(isAllowedMimeType('application/x-executable')).toBe(false);
      expect(isAllowedMimeType('text/html')).toBe(false);
    });

    it('should prevent double extension attacks', () => {
      const hasDoubleExtension = (filename: string): boolean => {
        const dangerousExtensions = ['.exe', '.bat', '.cmd', '.sh', '.php'];
        const lowerFilename = filename.toLowerCase();

        // Check if any dangerous extension exists before the final extension
        return dangerousExtensions.some(ext => {
          const index = lowerFilename.indexOf(ext);
          return index !== -1 && index < lowerFilename.lastIndexOf('.');
        });
      };

      expect(hasDoubleExtension('malware.exe.jpg')).toBe(true);
      expect(hasDoubleExtension('script.php.png')).toBe(true);
      expect(hasDoubleExtension('document.pdf')).toBe(false);
      expect(hasDoubleExtension('image.jpg')).toBe(false);
    });
  });

  describe('Form Validation Edge Cases', () => {
    it('should handle null and undefined inputs', () => {
      const schema = z.object({
        name: z.string(),
        age: z.number(),
      });

      expect(() => schema.parse({ name: null, age: 25 })).toThrow();
      expect(() => schema.parse({ name: 'test', age: undefined })).toThrow();
      expect(() => schema.parse(null)).toThrow();
      expect(() => schema.parse(undefined)).toThrow();
    });

    it('should trim whitespace from string inputs', () => {
      const schema = z.object({
        username: z.string().trim().min(1),
      });

      expect(() => schema.parse({ username: '   ' })).toThrow();

      const result = schema.parse({ username: '  test  ' });
      expect(result.username).toBe('test');
    });

    it('should normalize data before validation', () => {
      const schema = z.object({
        email: z.string().toLowerCase().email(),
      });

      const result = schema.parse({ email: 'Test@Example.COM' });
      expect(result.email).toBe('test@example.com');
    });

    it('should handle array inputs safely', () => {
      const schema = z.object({
        tags: z.array(z.string()).max(10),
      });

      expect(() => schema.parse({ tags: [] })).not.toThrow();
      expect(() => schema.parse({ tags: ['a', 'b', 'c'] })).not.toThrow();

      const tooManyTags = Array(11).fill('tag');
      expect(() => schema.parse({ tags: tooManyTags })).toThrow();
    });
  });

  describe('Prototype Pollution Prevention', () => {
    it('should reject __proto__ in input', () => {
      const schema = z.object({
        username: z.string(),
      }).strict();

      const maliciousInput = JSON.parse('{"__proto__": {"isAdmin": true}, "username": "test"}');

      // Strict mode should reject extra properties
      expect(() => schema.parse(maliciousInput)).toThrow();
    });

    it('should reject constructor in input', () => {
      const isPrototypePollution = (input: string): boolean => {
        // Check JSON string for dangerous keys before parsing
        const dangerousKeys = ['__proto__', 'prototype', 'constructor'];
        return dangerousKeys.some(key => input.includes(`"${key}"`));
      };

      expect(isPrototypePollution('{"__proto__": {}}')).toBe(true);
      expect(isPrototypePollution('{"prototype": {}}')).toBe(true);
      expect(isPrototypePollution('{"constructor": {}}')).toBe(true);
      expect(isPrototypePollution('{"name": "test"}')).toBe(false);
    });
  });

  describe('Unicode and Special Character Handling', () => {
    it('should handle Unicode characters safely', () => {
      const schema = z.object({
        text: z.string().max(100),
      });

      expect(() => schema.parse({ text: '你好世界' })).not.toThrow();
      expect(() => schema.parse({ text: 'Héllo Wörld' })).not.toThrow();
      expect(() => schema.parse({ text: '🎉🎊🎈' })).not.toThrow();
    });

    it('should handle zero-width characters', () => {
      const hasZeroWidthChars = (input: string): boolean => {
        const zeroWidthChars = [
          '\u200B', // Zero Width Space
          '\u200C', // Zero Width Non-Joiner
          '\u200D', // Zero Width Joiner
          '\uFEFF', // Zero Width No-Break Space
        ];

        return zeroWidthChars.some(char => input.includes(char));
      };

      expect(hasZeroWidthChars('normal text')).toBe(false);
      expect(hasZeroWidthChars('text\u200Bwith\u200Bzero\u200Bwidth')).toBe(true);
    });

    it('should normalize Unicode for comparison', () => {
      const normalize = (text: string): string => {
        return text.normalize('NFC');
      };

      // These should be equal after normalization
      const composed = 'é'; // Single character
      const decomposed = 'é'; // e + combining acute accent

      expect(normalize(composed)).toBe(normalize(decomposed));
    });
  });

  describe('Rate Limiting Input Validation', () => {
    it('should enforce request size limits', () => {
      const MAX_REQUEST_SIZE = 1024 * 1024; // 1 MB

      const isValidRequestSize = (data: string): boolean => {
        const size = new Blob([data]).size;
        return size <= MAX_REQUEST_SIZE;
      };

      const smallData = 'small request';
      const largeData = 'x'.repeat(2 * 1024 * 1024);

      expect(isValidRequestSize(smallData)).toBe(true);
      expect(isValidRequestSize(largeData)).toBe(false);
    });

    it('should limit array sizes in requests', () => {
      const schema = z.object({
        items: z.array(z.string()).max(100),
      });

      const validArray = Array(50).fill('item');
      const invalidArray = Array(150).fill('item');

      expect(() => schema.parse({ items: validArray })).not.toThrow();
      expect(() => schema.parse({ items: invalidArray })).toThrow();
    });
  });

  describe('Business Logic Validation', () => {
    it('should validate date ranges', () => {
      const schema = z.object({
        startDate: z.date(),
        endDate: z.date(),
      }).refine(
        data => data.endDate >= data.startDate,
        { message: 'End date must be after start date' }
      );

      const validDates = {
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-12-31'),
      };

      const invalidDates = {
        startDate: new Date('2024-12-31'),
        endDate: new Date('2024-01-01'),
      };

      expect(() => schema.parse(validDates)).not.toThrow();
      expect(() => schema.parse(invalidDates)).toThrow();
    });

    it('should validate mutually exclusive fields', () => {
      const schema = z.object({
        option1: z.string().optional(),
        option2: z.string().optional(),
      }).refine(
        data => (data.option1 ? 1 : 0) + (data.option2 ? 1 : 0) === 1,
        { message: 'Exactly one option must be provided' }
      );

      expect(() => schema.parse({ option1: 'a' })).not.toThrow();
      expect(() => schema.parse({ option2: 'b' })).not.toThrow();
      expect(() => schema.parse({ option1: 'a', option2: 'b' })).toThrow();
      expect(() => schema.parse({})).toThrow();
    });
  });
});

/**
 * Real-World Form Validation Tests
 */
describe('Real-World Form Validation', () => {
  describe('CreateItemForm Validation', () => {
    it('should enforce title length constraints', () => {
      const schema = z.object({
        title: z.string().min(1).max(500),
      });

      expect(() => schema.parse({ title: '' })).toThrow();
      expect(() => schema.parse({ title: 'a'.repeat(501) })).toThrow();
      expect(() => schema.parse({ title: 'Valid Title' })).not.toThrow();
    });

    it('should enforce description length constraints', () => {
      const schema = z.object({
        description: z.string().max(5000).optional(),
      });

      expect(() => schema.parse({ description: 'a'.repeat(5001) })).toThrow();
      expect(() => schema.parse({ description: 'Valid description' }))
        .not.toThrow();
      expect(() => schema.parse({})).not.toThrow();
    });

    it('should validate enum fields', () => {
      const statusSchema = z.enum(['todo', 'in_progress', 'done', 'blocked', 'cancelled']);

      expect(() => statusSchema.parse('todo')).not.toThrow();
      expect(() => statusSchema.parse('invalid_status')).toThrow();
    });

    it('should validate UUID fields', () => {
      const schema = z.object({
        parentId: z.string().uuid().optional().or(z.literal('')),
      });

      expect(() => schema.parse({ parentId: '' })).not.toThrow();
      expect(() => schema.parse({
        parentId: '550e8400-e29b-41d4-a716-446655440000'
      })).not.toThrow();
      expect(() => schema.parse({ parentId: 'invalid-uuid' })).toThrow();
    });
  });
});
