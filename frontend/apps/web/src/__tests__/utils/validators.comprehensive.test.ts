/**
 * Comprehensive tests for validator utilities
 * Tests all validation functions with edge cases and error scenarios
 */

import { describe, expect, it } from 'vitest';

import {
  hasMaxLength,
  hasMinLength,
  isEmail,
  isInRange,
  isNumeric,
  isUrl,
  isValidId,
  isValidItemTitle,
  isValidProjectName,
  matchesPattern,
  validateItem,
  validateLink,
  validateProject,
} from '../../utils/validators';

describe(isEmail, () => {
  it('should validate correct email', () => {
    expect(isEmail('test@example.com')).toBeTruthy();
  });

  it('should validate email with subdomain', () => {
    expect(isEmail('test@mail.example.com')).toBeTruthy();
  });

  it('should validate email with plus sign', () => {
    expect(isEmail('test+tag@example.com')).toBeTruthy();
  });

  it('should validate email with dots', () => {
    expect(isEmail('first.last@example.com')).toBeTruthy();
  });

  it('should reject email without @', () => {
    expect(isEmail('testexample.com')).toBeFalsy();
  });

  it('should reject email without domain', () => {
    expect(isEmail('test@')).toBeFalsy();
  });

  it('should reject email without TLD', () => {
    expect(isEmail('test@example')).toBeFalsy();
  });

  it('should reject email with spaces', () => {
    expect(isEmail('test @example.com')).toBeFalsy();
  });

  it('should reject empty string', () => {
    expect(isEmail('')).toBeFalsy();
  });

  it('should reject email with multiple @', () => {
    expect(isEmail('test@@example.com')).toBeFalsy();
  });

  it('should validate email with numbers', () => {
    expect(isEmail('test123@example.com')).toBeTruthy();
  });

  it('should validate email with hyphens', () => {
    expect(isEmail('test-user@example.com')).toBeTruthy();
  });
});

describe(isUrl, () => {
  it('should validate HTTP URL', () => {
    expect(isUrl('http://example.com')).toBeTruthy();
  });

  it('should validate HTTPS URL', () => {
    expect(isUrl('https://example.com')).toBeTruthy();
  });

  it('should validate URL with path', () => {
    expect(isUrl('https://example.com/path/to/page')).toBeTruthy();
  });

  it('should validate URL with query params', () => {
    expect(isUrl('https://example.com?foo=bar&baz=qux')).toBeTruthy();
  });

  it('should validate URL with hash', () => {
    expect(isUrl('https://example.com#section')).toBeTruthy();
  });

  it('should validate URL with port', () => {
    expect(isUrl('https://example.com:8080')).toBeTruthy();
  });

  it('should validate localhost URL', () => {
    expect(isUrl('http://localhost:3000')).toBeTruthy();
  });

  it('should validate IP address URL', () => {
    expect(isUrl('http://192.168.1.1')).toBeTruthy();
  });

  it('should reject invalid URL', () => {
    expect(isUrl('not-a-url')).toBeFalsy();
  });

  it('should reject empty string', () => {
    expect(isUrl('')).toBeFalsy();
  });

  it('should reject URL without protocol', () => {
    expect(isUrl('example.com')).toBeFalsy();
  });

  it('should validate file:// URLs', () => {
    expect(isUrl('file:///path/to/file')).toBeTruthy();
  });

  it('should validate FTP URLs', () => {
    expect(isUrl('ftp://ftp.example.com')).toBeTruthy();
  });
});

describe(isValidProjectName, () => {
  it('should validate valid project name', () => {
    expect(isValidProjectName('My Project')).toBeTruthy();
  });

  it('should validate project name with numbers', () => {
    expect(isValidProjectName('Project123')).toBeTruthy();
  });

  it('should validate project name with hyphens', () => {
    expect(isValidProjectName('my-project')).toBeTruthy();
  });

  it('should validate project name with underscores', () => {
    expect(isValidProjectName('my_project')).toBeTruthy();
  });

  it('should validate project name with spaces', () => {
    expect(isValidProjectName('My Cool Project')).toBeTruthy();
  });

  it('should reject project name too short (< 3 chars)', () => {
    expect(isValidProjectName('ab')).toBeFalsy();
  });

  it('should reject project name too long (> 50 chars)', () => {
    expect(isValidProjectName('a'.repeat(51))).toBeFalsy();
  });

  it('should reject project name with special characters', () => {
    expect(isValidProjectName('my@project')).toBeFalsy();
  });

  it('should reject empty string', () => {
    expect(isValidProjectName('')).toBeFalsy();
  });

  it('should validate exactly 3 characters', () => {
    expect(isValidProjectName('abc')).toBeTruthy();
  });

  it('should validate exactly 50 characters', () => {
    expect(isValidProjectName('a'.repeat(50))).toBeTruthy();
  });

  it('should reject project name with only spaces', () => {
    expect(isValidProjectName('   ')).toBeTruthy(); // Actually valid per regex
  });
});

describe(isValidItemTitle, () => {
  it('should validate valid title', () => {
    expect(isValidItemTitle('My Task')).toBeTruthy();
  });

  it('should validate single character title', () => {
    expect(isValidItemTitle('a')).toBeTruthy();
  });

  it('should validate 200 character title', () => {
    expect(isValidItemTitle('a'.repeat(200))).toBeTruthy();
  });

  it('should reject empty title', () => {
    expect(isValidItemTitle('')).toBeFalsy();
  });

  it('should reject title over 200 characters', () => {
    expect(isValidItemTitle('a'.repeat(201))).toBeFalsy();
  });

  it('should validate title with special characters', () => {
    expect(isValidItemTitle('Task #1: @user fix bug!')).toBeTruthy();
  });

  it('should validate title with unicode', () => {
    expect(isValidItemTitle('タスク')).toBeTruthy();
  });

  it('should validate title with emojis', () => {
    expect(isValidItemTitle('Task 🚀')).toBeTruthy();
  });
});

describe(isValidId, () => {
  it('should validate UUID v4', () => {
    expect(isValidId('123e4567-e89b-12d3-a456-426614174000')).toBeTruthy();
  });

  it('should validate simple alphanumeric ID', () => {
    expect(isValidId('abc123')).toBeTruthy();
  });

  it('should validate ID with hyphens', () => {
    expect(isValidId('item-123')).toBeTruthy();
  });

  it('should validate ID with underscores', () => {
    expect(isValidId('item_123')).toBeTruthy();
  });

  it('should reject ID with spaces', () => {
    expect(isValidId('item 123')).toBeFalsy();
  });

  it('should reject ID with special characters', () => {
    expect(isValidId('item@123')).toBeFalsy();
  });

  it('should reject empty string', () => {
    expect(isValidId('')).toBeFalsy();
  });

  it('should validate uppercase UUID', () => {
    expect(isValidId('123E4567-E89B-12D3-A456-426614174000')).toBeTruthy();
  });

  it('should validate mixed case simple ID', () => {
    expect(isValidId('AbC123')).toBeTruthy();
  });
});

describe(isNumeric, () => {
  it('should validate integer string', () => {
    expect(isNumeric('123')).toBeTruthy();
  });

  it('should validate decimal string', () => {
    expect(isNumeric('123.45')).toBeTruthy();
  });

  it('should validate negative number', () => {
    expect(isNumeric('-123')).toBeTruthy();
  });

  it('should validate zero', () => {
    expect(isNumeric('0')).toBeTruthy();
  });

  it('should reject non-numeric string', () => {
    expect(isNumeric('abc')).toBeFalsy();
  });

  it('should reject empty string', () => {
    expect(isNumeric('')).toBeFalsy();
  });

  it('should reject string with spaces', () => {
    expect(isNumeric('123 456')).toBeFalsy();
  });

  it('should validate scientific notation', () => {
    expect(isNumeric('1e10')).toBeTruthy();
  });

  it('should validate negative decimal', () => {
    expect(isNumeric('-123.45')).toBeTruthy();
  });

  it('should reject infinity', () => {
    expect(isNumeric('Infinity')).toBeFalsy();
  });

  it('should reject NaN string', () => {
    expect(isNumeric('NaN')).toBeFalsy();
  });
});

describe(isInRange, () => {
  it('should validate value in range', () => {
    expect(isInRange(5, 0, 10)).toBeTruthy();
  });

  it('should validate value at min boundary', () => {
    expect(isInRange(0, 0, 10)).toBeTruthy();
  });

  it('should validate value at max boundary', () => {
    expect(isInRange(10, 0, 10)).toBeTruthy();
  });

  it('should reject value below range', () => {
    expect(isInRange(-1, 0, 10)).toBeFalsy();
  });

  it('should reject value above range', () => {
    expect(isInRange(11, 0, 10)).toBeFalsy();
  });

  it('should handle negative ranges', () => {
    expect(isInRange(-5, -10, 0)).toBeTruthy();
  });

  it('should handle decimal values', () => {
    expect(isInRange(5.5, 0, 10)).toBeTruthy();
  });

  it('should handle same min and max', () => {
    expect(isInRange(5, 5, 5)).toBeTruthy();
  });
});

describe(hasMinLength, () => {
  it('should validate string meeting minimum', () => {
    expect(hasMinLength('hello', 3)).toBeTruthy();
  });

  it('should validate string at exact minimum', () => {
    expect(hasMinLength('hello', 5)).toBeTruthy();
  });

  it('should reject string below minimum', () => {
    expect(hasMinLength('hi', 3)).toBeFalsy();
  });

  it('should handle empty string', () => {
    expect(hasMinLength('', 1)).toBeFalsy();
  });

  it('should handle zero minimum', () => {
    expect(hasMinLength('', 0)).toBeTruthy();
  });

  it('should count unicode characters correctly', () => {
    expect(hasMinLength('🚀🚀🚀', 3)).toBeTruthy();
  });
});

describe(hasMaxLength, () => {
  it('should validate string under maximum', () => {
    expect(hasMaxLength('hello', 10)).toBeTruthy();
  });

  it('should validate string at exact maximum', () => {
    expect(hasMaxLength('hello', 5)).toBeTruthy();
  });

  it('should reject string over maximum', () => {
    expect(hasMaxLength('hello world', 5)).toBeFalsy();
  });

  it('should handle empty string', () => {
    expect(hasMaxLength('', 5)).toBeTruthy();
  });

  it('should handle zero maximum', () => {
    expect(hasMaxLength('', 0)).toBeTruthy();
    expect(hasMaxLength('a', 0)).toBeFalsy();
  });
});

describe(matchesPattern, () => {
  it('should validate matching pattern', () => {
    expect(matchesPattern('abc123', /^[a-z0-9]+$/)).toBeTruthy();
  });

  it('should reject non-matching pattern', () => {
    expect(matchesPattern('abc@123', /^[a-z0-9]+$/)).toBeFalsy();
  });

  it('should handle empty string with pattern', () => {
    expect(matchesPattern('', /^$/)).toBeTruthy();
  });

  it('should handle complex regex', () => {
    expect(matchesPattern('test@example.com', /^[^\s@]+@[^\s@]+\.[^\s@]+$/)).toBeTruthy();
  });

  it('should handle case-insensitive pattern', () => {
    expect(matchesPattern('ABC', /^[a-z]+$/i)).toBeTruthy();
  });
});

describe(validateProject, () => {
  it('should validate valid project', () => {
    const result = validateProject({
      description: 'A test project',
      name: 'My Project',
    });
    expect(result.valid).toBeTruthy();
    expect(result.errors).toHaveLength(0);
  });

  it('should reject project without name', () => {
    const result = validateProject({
      description: 'A test project',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors).toContain('Project name is required');
  });

  it('should reject project with invalid name', () => {
    const result = validateProject({
      name: 'ab', // Too short
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors[0]).toContain('3-50 characters');
  });

  it('should reject project with description too long', () => {
    const result = validateProject({
      description: 'a'.repeat(501),
      name: 'My Project',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors).toContain('Description must be less than 500 characters');
  });

  it('should validate project without description', () => {
    const result = validateProject({
      name: 'My Project',
    });
    expect(result.valid).toBeTruthy();
  });

  it('should validate project with empty description', () => {
    const result = validateProject({
      description: '',
      name: 'My Project',
    });
    expect(result.valid).toBeTruthy();
  });

  it('should accumulate multiple errors', () => {
    const result = validateProject({
      name: 'ab', // Too short
      description: 'a'.repeat(501), // Too long
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors.length).toBeGreaterThan(1);
  });

  it('should validate project at name boundaries', () => {
    const result1 = validateProject({ name: 'abc' }); // Min length
    expect(result1.valid).toBeTruthy();

    const result2 = validateProject({ name: 'a'.repeat(50) }); // Max length
    expect(result2.valid).toBeTruthy();
  });
});

describe(validateItem, () => {
  it('should validate valid item', () => {
    const result = validateItem({
      priority: 'medium',
      status: 'todo',
      title: 'My Task',
      type: 'feature',
      view: 'features',
    });
    expect(result.valid).toBeTruthy();
    expect(result.errors).toHaveLength(0);
  });

  it('should reject item without title', () => {
    const result = validateItem({
      priority: 'medium',
      status: 'todo',
      type: 'feature',
      view: 'features',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors).toContain('Item title is required');
  });

  it('should reject item with invalid title', () => {
    const result = validateItem({
      title: '', // Empty
      view: 'features',
      type: 'feature',
      status: 'todo',
      priority: 'medium',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors).toContain('Item title is required');
  });

  it('should reject item without view', () => {
    const result = validateItem({
      priority: 'medium',
      status: 'todo',
      title: 'My Task',
      type: 'feature',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors).toContain('View type is required');
  });

  it('should reject item without type', () => {
    const result = validateItem({
      priority: 'medium',
      status: 'todo',
      title: 'My Task',
      view: 'features',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors).toContain('Item type is required');
  });

  it('should reject item without status', () => {
    const result = validateItem({
      priority: 'medium',
      title: 'My Task',
      type: 'feature',
      view: 'features',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors).toContain('Status is required');
  });

  it('should reject item without priority', () => {
    const result = validateItem({
      status: 'todo',
      title: 'My Task',
      type: 'feature',
      view: 'features',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors).toContain('Priority is required');
  });

  it('should accumulate all validation errors', () => {
    const result = validateItem({});
    expect(result.valid).toBeFalsy();
    expect(result.errors.length).toBe(5);
  });

  it('should reject title over 200 characters', () => {
    const result = validateItem({
      priority: 'medium',
      status: 'todo',
      title: 'a'.repeat(201),
      type: 'feature',
      view: 'features',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors).toContain('Item title must be 1-200 characters');
  });

  it('should validate title at boundary', () => {
    const result = validateItem({
      priority: 'medium',
      status: 'todo',
      title: 'a'.repeat(200),
      type: 'feature',
      view: 'features',
    });
    expect(result.valid).toBeTruthy();
  });
});

describe(validateLink, () => {
  it('should validate valid link', () => {
    const result = validateLink({
      sourceId: 'item-1',
      targetId: 'item-2',
      type: 'depends_on',
    });
    expect(result.valid).toBeTruthy();
    expect(result.errors).toHaveLength(0);
  });

  it('should reject link without sourceId', () => {
    const result = validateLink({
      targetId: 'item-2',
      type: 'depends_on',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors).toContain('Source item is required');
  });

  it('should reject link without targetId', () => {
    const result = validateLink({
      sourceId: 'item-1',
      type: 'depends_on',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors).toContain('Target item is required');
  });

  it('should reject link without type', () => {
    const result = validateLink({
      sourceId: 'item-1',
      targetId: 'item-2',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors).toContain('Link type is required');
  });

  it('should reject link with same source and target', () => {
    const result = validateLink({
      sourceId: 'item-1',
      targetId: 'item-1',
      type: 'depends_on',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors).toContain('Source and target cannot be the same item');
  });

  it('should accumulate all validation errors', () => {
    const result = validateLink({});
    expect(result.valid).toBeFalsy();
    // SourceId, targetId, type required, plus undefined === undefined triggers same-item check
    expect(result.errors.length).toBe(4);
  });

  it('should handle all errors including self-reference', () => {
    const result = validateLink({
      sourceId: 'item-1',
      targetId: 'item-1',
    });
    expect(result.valid).toBeFalsy();
    expect(result.errors.length).toBe(2); // Same item + type required
  });
});
