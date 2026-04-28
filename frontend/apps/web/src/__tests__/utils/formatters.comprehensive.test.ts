/**
 * Comprehensive tests for formatter utilities
 * Tests all formatting functions with edge cases and error handling
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  camelCase,
  capitalize,
  formatBytes,
  formatDate,
  formatDuration,
  formatNumber,
  formatPercentage,
  formatRelativeTime,
  formatStatus,
  formatTime,
  getPriorityColor,
  getStatusColor,
  kebabCase,
  titleCase,
  truncate,
} from '../../utils/formatters';

describe(formatDate, () => {
  it('should format Date object in short format', () => {
    const date = new Date('2024-01-15T10:30:00Z');
    const result = formatDate(date, 'short');
    expect(result).toContain('Jan');
    expect(result).toContain('15');
    expect(result).toContain('2024');
  });

  it('should format string date in short format', () => {
    const result = formatDate('2024-01-15T10:30:00Z', 'short');
    expect(result).toContain('Jan');
    expect(result).toContain('15');
    expect(result).toContain('2024');
  });

  it('should format date in long format', () => {
    const date = new Date('2024-01-15T10:30:00Z');
    const result = formatDate(date, 'long');
    expect(result).toContain('January');
    expect(result).toContain('15');
    expect(result).toContain('2024');
  });

  it('should format date in relative format for recent dates', () => {
    const now = new Date();
    const result = formatDate(now, 'relative');
    expect(result).toBe('just now');
  });

  it('should default to short format', () => {
    const date = new Date('2024-01-15T10:30:00Z');
    const result = formatDate(date);
    expect(result).toContain('Jan');
  });

  it('should handle invalid date strings gracefully', () => {
    const result = formatDate('invalid-date', 'short');
    expect(result).toBeDefined();
  });

  it('should handle different timezones', () => {
    const date = new Date('2024-06-15T23:59:59Z');
    const result = formatDate(date, 'short');
    expect(result).toBeDefined();
    expect(result).toContain('2024');
  });

  it('should handle dates far in the past', () => {
    const date = new Date('1970-01-01T00:00:00Z');
    const result = formatDate(date, 'short');
    expect(result).toMatch(/197[0-9]|196[9]/);
  });

  it('should handle dates far in the future', () => {
    const date = new Date('2099-12-31T23:59:59Z');
    const result = formatDate(date, 'short');
    expect(result).toContain('2099');
  });
});

describe(formatRelativeTime, () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should show "just now" for dates less than 60 seconds ago', () => {
    const now = new Date('2024-01-15T10:30:00Z');
    vi.setSystemTime(now);

    const date = new Date('2024-01-15T10:29:30Z'); // 30 seconds ago
    expect(formatRelativeTime(date)).toBe('just now');
  });

  it('should show minutes ago for dates less than an hour ago', () => {
    const now = new Date('2024-01-15T10:30:00Z');
    vi.setSystemTime(now);

    const date = new Date('2024-01-15T10:15:00Z'); // 15 minutes ago
    expect(formatRelativeTime(date)).toBe('15m ago');
  });

  it('should show hours ago for dates less than a day ago', () => {
    const now = new Date('2024-01-15T10:30:00Z');
    vi.setSystemTime(now);

    const date = new Date('2024-01-15T07:30:00Z'); // 3 hours ago
    expect(formatRelativeTime(date)).toBe('3h ago');
  });

  it('should show days ago for dates less than a week ago', () => {
    const now = new Date('2024-01-15T10:30:00Z');
    vi.setSystemTime(now);

    const date = new Date('2024-01-13T10:30:00Z'); // 2 days ago
    expect(formatRelativeTime(date)).toBe('2d ago');
  });

  it('should show weeks ago for dates less than a month ago', () => {
    const now = new Date('2024-01-29T10:30:00Z');
    vi.setSystemTime(now);

    const date = new Date('2024-01-15T10:30:00Z'); // 2 weeks ago
    expect(formatRelativeTime(date)).toBe('2w ago');
  });

  it('should show formatted date for dates more than a month ago', () => {
    const now = new Date('2024-03-15T10:30:00Z');
    vi.setSystemTime(now);

    const date = new Date('2024-01-15T10:30:00Z'); // 2 months ago
    const result = formatRelativeTime(date);
    expect(result).toContain('Jan');
  });

  it('should handle edge case at exactly 60 seconds', () => {
    const now = new Date('2024-01-15T10:30:00Z');
    vi.setSystemTime(now);

    const date = new Date('2024-01-15T10:29:00Z'); // Exactly 60 seconds
    expect(formatRelativeTime(date)).toBe('1m ago');
  });

  it('should handle edge case at exactly 1 hour', () => {
    const now = new Date('2024-01-15T10:30:00Z');
    vi.setSystemTime(now);

    const date = new Date('2024-01-15T09:30:00Z'); // Exactly 1 hour
    expect(formatRelativeTime(date)).toBe('1h ago');
  });
});

describe(formatTime, () => {
  it('should format time from Date object', () => {
    const date = new Date('2024-01-15T14:30:00Z');
    const result = formatTime(date);
    expect(result).toMatch(/\d{1,2}:\d{2}/);
  });

  it('should format time from string', () => {
    const result = formatTime('2024-01-15T14:30:00Z');
    expect(result).toMatch(/\d{1,2}:\d{2}/);
  });

  it('should handle midnight', () => {
    const date = new Date('2024-01-15T00:00:00Z');
    const result = formatTime(date);
    expect(result).toBeDefined();
  });

  it('should handle noon', () => {
    const date = new Date('2024-01-15T12:00:00Z');
    const result = formatTime(date);
    expect(result).toBeDefined();
  });
});

describe(formatNumber, () => {
  it('should format integer with default options', () => {
    expect(formatNumber(1234)).toBe('1,234');
  });

  it('should format decimal with default options', () => {
    expect(formatNumber(1234.56)).toBe('1,234.56');
  });

  it('should format with custom minimumFractionDigits', () => {
    const result = formatNumber(10, { minimumFractionDigits: 2 });
    expect(result).toBe('10.00');
  });

  it('should format with custom maximumFractionDigits', () => {
    const result = formatNumber(10.123_45, { maximumFractionDigits: 2 });
    expect(result).toBe('10.12');
  });

  it('should handle zero', () => {
    expect(formatNumber(0)).toBe('0');
  });

  it('should handle negative numbers', () => {
    expect(formatNumber(-1234)).toBe('-1,234');
  });

  it('should handle very large numbers', () => {
    const result = formatNumber(1_234_567_890);
    expect(result).toContain(',');
  });

  it('should handle very small decimals', () => {
    const result = formatNumber(0.0001, { minimumFractionDigits: 4 });
    expect(result).toBe('0.0001');
  });
});

describe(formatPercentage, () => {
  it('should format percentage with default decimals', () => {
    expect(formatPercentage(25, 100)).toBe('25%');
  });

  it('should format percentage with custom decimals', () => {
    expect(formatPercentage(25, 100, 2)).toBe('25.00%');
  });

  it('should handle zero total gracefully', () => {
    expect(formatPercentage(10, 0)).toBe('0%');
  });

  it('should handle zero value', () => {
    expect(formatPercentage(0, 100)).toBe('0%');
  });

  it('should handle fractional percentages', () => {
    expect(formatPercentage(1, 3, 2)).toBe('33.33%');
  });

  it('should handle value greater than total (>100%)', () => {
    expect(formatPercentage(150, 100, 0)).toBe('150%');
  });

  it('should round correctly', () => {
    expect(formatPercentage(2, 3, 0)).toBe('67%');
  });

  it('should handle very small percentages', () => {
    expect(formatPercentage(1, 1000, 2)).toBe('0.10%');
  });
});

describe(formatBytes, () => {
  it('should format 0 bytes', () => {
    expect(formatBytes(0)).toBe('0 Bytes');
  });

  it('should format bytes', () => {
    expect(formatBytes(500)).toBe('500 Bytes');
  });

  it('should format KB', () => {
    expect(formatBytes(1024)).toBe('1 KB');
  });

  it('should format MB', () => {
    expect(formatBytes(1_048_576)).toBe('1 MB');
  });

  it('should format GB', () => {
    expect(formatBytes(1_073_741_824)).toBe('1 GB');
  });

  it('should format TB', () => {
    expect(formatBytes(1_099_511_627_776)).toBe('1 TB');
  });

  it('should format with custom decimals', () => {
    expect(formatBytes(1536, 0)).toBe('2 KB');
  });

  it('should format fractional values', () => {
    expect(formatBytes(1500, 2)).toBe('1.46 KB');
  });

  it('should handle very large values', () => {
    const result = formatBytes(1_099_511_627_776 * 10); // 10 TB
    expect(result).toContain('TB');
  });
});

describe(truncate, () => {
  it('should not truncate short text', () => {
    expect(truncate('Hello', 10)).toBe('Hello');
  });

  it('should truncate long text with default suffix', () => {
    expect(truncate('Hello World', 8)).toBe('Hello...');
  });

  it('should truncate with custom suffix', () => {
    expect(truncate('Hello World', 8, '…')).toBe('Hello W…');
  });

  it('should handle empty string', () => {
    expect(truncate('', 10)).toBe('');
  });

  it('should handle exact length match', () => {
    expect(truncate('Hello', 5)).toBe('Hello');
  });

  it('should handle very short length', () => {
    expect(truncate('Hello World', 3)).toBe('...');
  });

  it('should account for suffix length', () => {
    const text = 'Hello World';
    const result = truncate(text, 8, '...');
    expect(result.length).toBe(8);
  });
});

describe(capitalize, () => {
  it('should capitalize first letter', () => {
    expect(capitalize('hello')).toBe('Hello');
  });

  it('should lowercase rest of string', () => {
    expect(capitalize('hELLO')).toBe('Hello');
  });

  it('should handle single character', () => {
    expect(capitalize('h')).toBe('H');
  });

  it('should handle empty string', () => {
    expect(capitalize('')).toBe('');
  });

  it('should handle already capitalized', () => {
    expect(capitalize('Hello')).toBe('Hello');
  });

  it('should handle numbers', () => {
    expect(capitalize('123abc')).toBe('123abc');
  });

  it('should handle special characters', () => {
    expect(capitalize('!hello')).toBe('!hello');
  });
});

describe(titleCase, () => {
  it('should capitalize each word', () => {
    expect(titleCase('hello world')).toBe('Hello World');
  });

  it('should handle single word', () => {
    expect(titleCase('hello')).toBe('Hello');
  });

  it('should handle mixed case input', () => {
    expect(titleCase('hELLO wORLD')).toBe('Hello World');
  });

  it('should handle multiple spaces', () => {
    expect(titleCase('hello  world')).toBe('Hello  World');
  });

  it('should handle empty string', () => {
    expect(titleCase('')).toBe('');
  });

  it('should handle numbers', () => {
    expect(titleCase('hello 123 world')).toBe('Hello 123 World');
  });

  it('should handle special characters', () => {
    expect(titleCase('hello-world')).toBe('Hello-world');
  });
});

describe(kebabCase, () => {
  it('should convert to kebab case', () => {
    expect(kebabCase('Hello World')).toBe('hello-world');
  });

  it('should handle multiple spaces', () => {
    expect(kebabCase('Hello  World')).toBe('hello-world');
  });

  it('should remove special characters', () => {
    expect(kebabCase('Hello@World!')).toBe('helloworld');
  });

  it('should preserve hyphens', () => {
    expect(kebabCase('Hello-World')).toBe('hello-world');
  });

  it('should handle underscores', () => {
    expect(kebabCase('Hello_World')).toBe('hello_world');
  });

  it('should handle camelCase', () => {
    expect(kebabCase('helloWorld')).toBe('helloworld');
  });

  it('should handle empty string', () => {
    expect(kebabCase('')).toBe('');
  });
});

describe(camelCase, () => {
  it('should convert to camelCase', () => {
    expect(camelCase('hello world')).toBe('helloWorld');
  });

  it('should handle hyphens', () => {
    expect(camelCase('hello-world')).toBe('helloWorld');
  });

  it('should handle underscores', () => {
    expect(camelCase('hello_world')).toBe('helloWorld');
  });

  it('should handle multiple separators', () => {
    expect(camelCase('hello-world_test')).toBe('helloWorldTest');
  });

  it('should handle already camelCase', () => {
    expect(camelCase('helloWorld')).toBe('helloworld');
  });

  it('should handle empty string', () => {
    expect(camelCase('')).toBe('');
  });

  it('should handle single word', () => {
    expect(camelCase('hello')).toBe('hello');
  });
});

describe(formatStatus, () => {
  it('should format status with underscores', () => {
    expect(formatStatus('in_progress')).toBe('In Progress');
  });

  it('should format single word status', () => {
    expect(formatStatus('todo')).toBe('Todo');
  });

  it('should handle multiple underscores', () => {
    expect(formatStatus('waiting_for_review')).toBe('Waiting For Review');
  });

  it('should handle all caps', () => {
    expect(formatStatus('IN_PROGRESS')).toBe('In Progress');
  });

  it('should handle mixed case', () => {
    expect(formatStatus('In_Progress')).toBe('In Progress');
  });

  it('should handle empty string', () => {
    expect(formatStatus('')).toBe('');
  });
});

describe(getPriorityColor, () => {
  it('should return red for critical', () => {
    expect(getPriorityColor('critical')).toBe('red');
  });

  it('should return orange for high', () => {
    expect(getPriorityColor('high')).toBe('orange');
  });

  it('should return yellow for medium', () => {
    expect(getPriorityColor('medium')).toBe('yellow');
  });

  it('should return green for low', () => {
    expect(getPriorityColor('low')).toBe('green');
  });

  it('should handle case insensitive', () => {
    expect(getPriorityColor('CRITICAL')).toBe('red');
    expect(getPriorityColor('High')).toBe('orange');
  });

  it('should return gray for unknown priority', () => {
    expect(getPriorityColor('unknown')).toBe('gray');
  });

  it('should handle empty string', () => {
    expect(getPriorityColor('')).toBe('gray');
  });
});

describe(getStatusColor, () => {
  it('should return gray for todo', () => {
    expect(getStatusColor('todo')).toBe('gray');
  });

  it('should return blue for in_progress', () => {
    expect(getStatusColor('in_progress')).toBe('blue');
  });

  it('should return green for done', () => {
    expect(getStatusColor('done')).toBe('green');
  });

  it('should return red for blocked', () => {
    expect(getStatusColor('blocked')).toBe('red');
  });

  it('should return gray for cancelled', () => {
    expect(getStatusColor('cancelled')).toBe('gray');
  });

  it('should handle case insensitive', () => {
    expect(getStatusColor('DONE')).toBe('green');
    expect(getStatusColor('In_Progress')).toBe('blue');
  });

  it('should return gray for unknown status', () => {
    expect(getStatusColor('unknown')).toBe('gray');
  });

  it('should handle empty string', () => {
    expect(getStatusColor('')).toBe('gray');
  });
});

describe(formatDuration, () => {
  it('should format seconds', () => {
    expect(formatDuration(30)).toBe('30s');
  });

  it('should format minutes and seconds', () => {
    expect(formatDuration(90)).toBe('1m 30s');
  });

  it('should format hours and minutes', () => {
    expect(formatDuration(3665)).toBe('1h 1m');
  });

  it('should format multiple hours', () => {
    expect(formatDuration(7200)).toBe('2h 0m');
  });

  it('should handle zero', () => {
    expect(formatDuration(0)).toBe('0s');
  });

  it('should handle exactly 60 seconds', () => {
    expect(formatDuration(60)).toBe('1m 0s');
  });

  it('should handle exactly 3600 seconds', () => {
    expect(formatDuration(3600)).toBe('1h 0m');
  });

  it('should handle very large durations', () => {
    const result = formatDuration(86_400); // 24 hours
    expect(result).toContain('h');
  });
});
