import * as Vitest from 'vitest';

import { cn } from '../lib/utils';

Vitest.describe('cn utility', () => {
  Vitest.it('merges class names', () => {
    Vitest.expect(cn('foo', 'bar')).toBe('foo bar');
  });

  Vitest.it('handles conditional classes', () => {
    const hidden = false;
    Vitest.expect(cn('base', hidden && 'hidden', 'visible')).toBe('base visible');
  });

  Vitest.it('handles undefined and null values', () => {
    Vitest.expect(cn('base', undefined, null, 'end')).toBe('base end');
  });

  Vitest.it('merges tailwind classes correctly', () => {
    Vitest.expect(cn('px-2 py-1', 'px-4')).toBe('py-1 px-4');
  });

  Vitest.it('returns empty string for no arguments', () => {
    Vitest.expect(cn()).toBe('');
  });
});
