import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { EnvManager } from '../env-manager';

/**
 * Helper: assert that a function throws an Error whose message contains the expected substring.
 * Vitest 4.x toThrow() is broken on Node 25, so we use try/catch.
 */
function expectThrow(
  fn: () => unknown,
  expectedMessage: string,
  errorType: new (...a: any[]) => Error = Error,
): void {
  let caught: unknown;
  try {
    fn();
  } catch (e) {
    caught = e;
  }
  expect(caught).toBeDefined();
  expect(caught).toBeInstanceOf(errorType);
  expect((caught as Error).message).toContain(expectedMessage);
}

describe('EnvManager', () => {
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    originalEnv = { ...process.env };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('constructor', () => {
    it('loads variables from process.env on construction', () => {
      process.env.TEST_CONSTRUCTOR_VAR = 'from_process';
      const mgr = new EnvManager();
      expect(mgr.get('TEST_CONSTRUCTOR_VAR')).toBe('from_process');
    });

    it('loads variables from a config object, overriding process.env', () => {
      process.env.MY_VAR = 'process_value';
      const mgr = new EnvManager({ MY_VAR: 'config_value' });
      expect(mgr.get('MY_VAR')).toBe('config_value');
    });

    it('skips undefined values in config object', () => {
      const mgr = new EnvManager({ DEFINED: 'yes', UNDEF: undefined });
      expect(mgr.has('DEFINED')).toBeTruthy();
      expect(mgr.has('UNDEF')).toBeFalsy();
    });

    it('coerces numeric and boolean config values to strings', () => {
      const mgr = new EnvManager({ NUM: 42, BOOL: true });
      expect(mgr.get('NUM')).toBe('42');
      expect(mgr.get('BOOL')).toBe('true');
    });

    it('works with no config argument', () => {
      const mgr = new EnvManager();
      expect(mgr).toBeInstanceOf(EnvManager);
    });
  });

  describe('get', () => {
    it('returns the value for an existing key', () => {
      const mgr = new EnvManager({ FOO: 'bar' });
      expect(mgr.get('FOO')).toBe('bar');
    });

    it('returns undefined for a missing key with no default', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      expect(mgr.get('NONEXISTENT')).toBeUndefined();
    });

    it('returns the default value when key is missing', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      expect(mgr.get('MISSING', 'fallback')).toBe('fallback');
    });

    it('returns the actual value over the default when key exists', () => {
      const mgr = new EnvManager({ KEY: 'actual' });
      expect(mgr.get('KEY', 'fallback')).toBe('actual');
    });
  });

  describe('getRequired', () => {
    it('returns value for a set variable', () => {
      const mgr = new EnvManager({ REQUIRED_VAR: 'present' });
      expect(mgr.getRequired('REQUIRED_VAR')).toBe('present');
    });

    it('throws for a missing variable', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      expectThrow(
        () => mgr.getRequired('MISSING_VAR'),
        'Required environment variable MISSING_VAR not set',
      );
    });

    it('throws for an empty string variable (falsy)', () => {
      // loadFromConfig stores '' in the map (value !== undefined),
      // but getRequired checks !value, and !'' is true, so it throws.
      const mgr = new EnvManager({ EMPTY_KEY: '' });
      expectThrow(
        () => mgr.getRequired('EMPTY_KEY'),
        'Required environment variable EMPTY_KEY not set',
      );
    });
  });

  describe('getNumber', () => {
    it('returns parsed number for valid numeric string', () => {
      const mgr = new EnvManager({ PORT: '8080' });
      expect(mgr.getNumber('PORT')).toBe(8080);
    });

    it('returns default when key is missing', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      expect(mgr.getNumber('PORT', 3000)).toBe(3000);
    });

    it('returns undefined when key is missing and no default given', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      expect(mgr.getNumber('PORT')).toBeUndefined();
    });

    it('throws TypeError for non-numeric value', () => {
      const mgr = new EnvManager({ PORT: 'not_a_number' });
      expectThrow(
        () => mgr.getNumber('PORT'),
        'Environment variable PORT is not a valid number: not_a_number',
        TypeError,
      );
    });

    it('handles negative numbers', () => {
      const mgr = new EnvManager({ NEG: '-5' });
      expect(mgr.getNumber('NEG')).toBe(-5);
    });

    it('handles floating point numbers', () => {
      const mgr = new EnvManager({ FLOAT: '3.14' });
      expect(mgr.getNumber('FLOAT')).toBe(3.14);
    });

    it('handles zero', () => {
      const mgr = new EnvManager({ ZERO: '0' });
      expect(mgr.getNumber('ZERO')).toBe(0);
    });
  });

  describe('getBoolean', () => {
    it('returns true for "true"', () => {
      const mgr = new EnvManager({ FLAG: 'true' });
      expect(mgr.getBoolean('FLAG')).toBeTruthy();
    });

    it('returns true for "1"', () => {
      const mgr = new EnvManager({ FLAG: '1' });
      expect(mgr.getBoolean('FLAG')).toBeTruthy();
    });

    it('returns true for "yes"', () => {
      const mgr = new EnvManager({ FLAG: 'yes' });
      expect(mgr.getBoolean('FLAG')).toBeTruthy();
    });

    it('returns true for "on"', () => {
      const mgr = new EnvManager({ FLAG: 'on' });
      expect(mgr.getBoolean('FLAG')).toBeTruthy();
    });

    it('is case-insensitive for truthy values', () => {
      const mgr = new EnvManager({ FLAG: 'TRUE' });
      expect(mgr.getBoolean('FLAG')).toBeTruthy();
    });

    it('returns false for unrecognized string values', () => {
      const mgr = new EnvManager({ FLAG: 'false' });
      expect(mgr.getBoolean('FLAG')).toBeFalsy();
    });

    it('returns false for "0"', () => {
      const mgr = new EnvManager({ FLAG: '0' });
      expect(mgr.getBoolean('FLAG')).toBeFalsy();
    });

    it('returns default value when key is missing', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      expect(mgr.getBoolean('MISSING')).toBeFalsy();
      expect(mgr.getBoolean('MISSING', true)).toBeTruthy();
    });
  });

  describe('getArray', () => {
    it('splits comma-separated values by default', () => {
      const mgr = new EnvManager({ LIST: 'a,b,c' });
      expect(mgr.getArray('LIST')).toEqual(['a', 'b', 'c']);
    });

    it('trims whitespace from array items', () => {
      const mgr = new EnvManager({ LIST: ' a , b , c ' });
      expect(mgr.getArray('LIST')).toEqual(['a', 'b', 'c']);
    });

    it('returns empty array for missing key', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      expect(mgr.getArray('MISSING')).toEqual([]);
    });

    it('supports custom separator', () => {
      const mgr = new EnvManager({ LIST: 'a|b|c' });
      expect(mgr.getArray('LIST', '|')).toEqual(['a', 'b', 'c']);
    });

    it('returns single-element array for value without separator', () => {
      const mgr = new EnvManager({ SINGLE: 'only_one' });
      expect(mgr.getArray('SINGLE')).toEqual(['only_one']);
    });
  });

  describe('getJSON', () => {
    it('parses valid JSON object', () => {
      const mgr = new EnvManager({ DATA: '{"key":"value"}' });
      expect(mgr.getJSON('DATA')).toEqual({ key: 'value' });
    });

    it('returns default when key is missing', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      expect(mgr.getJSON('MISSING', { fallback: true })).toEqual({ fallback: true });
    });

    it('returns undefined when key is missing and no default', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      expect(mgr.getJSON('MISSING')).toBeUndefined();
    });

    it('throws for invalid JSON', () => {
      const mgr = new EnvManager({ BAD_JSON: '{not valid json}' });
      expectThrow(() => mgr.getJSON('BAD_JSON'), 'Environment variable BAD_JSON is not valid JSON');
    });

    it('parses JSON arrays', () => {
      const mgr = new EnvManager({ ARR: '[1,2,3]' });
      expect(mgr.getJSON('ARR')).toEqual([1, 2, 3]);
    });

    it('includes the cause in the error for invalid JSON', () => {
      const mgr = new EnvManager({ BAD: 'not-json' });
      let caught: unknown;
      try {
        mgr.getJSON('BAD');
      } catch (e) {
        caught = e;
      }
      expect(caught).toBeDefined();
      expect((caught as Error).cause).toBeDefined();
    });
  });

  describe('set', () => {
    it('sets a string value', () => {
      const mgr = new EnvManager({});
      mgr.set('NEW_KEY', 'new_value');
      expect(mgr.get('NEW_KEY')).toBe('new_value');
    });

    it('coerces numbers to strings', () => {
      const mgr = new EnvManager({});
      mgr.set('NUM', 123);
      expect(mgr.get('NUM')).toBe('123');
    });

    it('coerces booleans to strings', () => {
      const mgr = new EnvManager({});
      mgr.set('BOOL', false);
      expect(mgr.get('BOOL')).toBe('false');
    });

    it('overwrites existing values', () => {
      const mgr = new EnvManager({ KEY: 'old' });
      mgr.set('KEY', 'new');
      expect(mgr.get('KEY')).toBe('new');
    });
  });

  describe('has', () => {
    it('returns true for existing key', () => {
      const mgr = new EnvManager({ EXISTS: 'yes' });
      expect(mgr.has('EXISTS')).toBeTruthy();
    });

    it('returns false for missing key', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      expect(mgr.has('NOPE')).toBeFalsy();
    });
  });

  describe('validate', () => {
    it('does not throw when all required variables are present', () => {
      const mgr = new EnvManager({ A: '1', B: '2', C: '3' });
      // Should not throw
      mgr.validate(['A', 'B', 'C']);
    });

    it('throws listing all missing variables', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      mgr.set('A', '1');
      expectThrow(
        () => mgr.validate(['A', 'B', 'C']),
        'Missing required environment variables: B, C',
      );
    });

    it('throws listing single missing variable', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      expectThrow(
        () => mgr.validate(['ONLY_ONE']),
        'Missing required environment variables: ONLY_ONE',
      );
    });

    it('does not throw for empty required list', () => {
      const mgr = new EnvManager({});
      // Should not throw
      mgr.validate([]);
    });
  });

  describe('getAll', () => {
    it('returns all variables as a plain object', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      mgr.set('X', 'x_val');
      mgr.set('Y', 'y_val');
      expect(mgr.getAll()).toEqual({ X: 'x_val', Y: 'y_val' });
    });
  });

  describe('getByPrefix', () => {
    it('returns only variables matching prefix', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      mgr.set('VITE_API_URL', 'http://api');
      mgr.set('VITE_WS_URL', 'ws://ws');
      mgr.set('NODE_ENV', 'test');
      const result = mgr.getByPrefix('VITE_');
      expect(result).toEqual({
        VITE_API_URL: 'http://api',
        VITE_WS_URL: 'ws://ws',
      });
    });

    it('returns empty object when no variables match prefix', () => {
      const mgr = new EnvManager({});
      mgr.clear();
      mgr.set('FOO', 'bar');
      expect(mgr.getByPrefix('VITE_')).toEqual({});
    });
  });

  describe('clear', () => {
    it('removes all variables', () => {
      const mgr = new EnvManager({ A: '1', B: '2' });
      mgr.clear();
      expect(mgr.has('A')).toBeFalsy();
      expect(mgr.has('B')).toBeFalsy();
      expect(mgr.getAll()).toEqual({});
    });
  });

  describe('singleton export', () => {
    it('exports envManager as an EnvManager instance', async () => {
      const { envManager } = await import('../env-manager');
      expect(envManager).toBeInstanceOf(EnvManager);
    });
  });
});
