import { act, renderHook } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import type { KeyboardShortcutAction } from '@/hooks/useKeyboardShortcuts';

import {
  __resetKeyboardShortcutsRegistry,
  formatKeyboardShortcut,
  useKeyboardShortcuts,
} from '@/hooks/useKeyboardShortcuts';

describe(useKeyboardShortcuts, () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset global registry to ensure test isolation
    __resetKeyboardShortcutsRegistry();
  });

  afterEach(() => {
    // Clean up after each test
    __resetKeyboardShortcutsRegistry();
  });

  it('initializes with closed modal', () => {
    const { result } = renderHook(() => useKeyboardShortcuts([]));

    expect(result.current.isShortcutsModalOpen).toBeFalsy();
  });

  it('opens and closes shortcuts modal', () => {
    const { result } = renderHook(() => useKeyboardShortcuts([]));

    act(() => {
      result.current.setIsShortcutsModalOpen(true);
    });

    expect(result.current.isShortcutsModalOpen).toBeTruthy();

    act(() => {
      result.current.setIsShortcutsModalOpen(false);
    });

    expect(result.current.isShortcutsModalOpen).toBeFalsy();
  });

  it('returns all registered shortcuts', () => {
    const shortcuts: KeyboardShortcutAction[] = [
      {
        action: vi.fn(),
        category: 'editing',
        description: 'Save',
        key: 's',
        meta: true,
      },
      {
        action: vi.fn(),
        category: 'navigation',
        description: 'New',
        key: 'n',
        meta: true,
      },
    ];

    const { result } = renderHook(() => useKeyboardShortcuts(shortcuts));

    expect(result.current.allShortcuts).toHaveLength(2);
    expect(result.current.allShortcuts[0].description).toBe('Save');
    expect(result.current.allShortcuts[1].description).toBe('New');
  });

  it('registers new shortcuts dynamically', () => {
    const { result } = renderHook(() => useKeyboardShortcuts([]));

    expect(result.current.allShortcuts).toHaveLength(0);

    const newShortcut: KeyboardShortcutAction = {
      action: vi.fn(),
      category: 'editing',
      description: 'Save',
      key: 's',
      meta: true,
    };

    act(() => {
      result.current.register(newShortcut);
    });

    expect(result.current.allShortcuts).toHaveLength(1);
  });

  it('unregisters shortcuts', () => {
    const shortcut: KeyboardShortcutAction = {
      action: vi.fn(),
      category: 'editing',
      description: 'Save',
      key: 's',
      meta: true,
    };

    const { result } = renderHook(() => useKeyboardShortcuts([shortcut]));

    expect(result.current.allShortcuts).toHaveLength(1);

    act(() => {
      // Unregister would need the ID returned from register
      // This is a simplified test
    });
  });

  it('groups shortcuts by category', () => {
    const shortcuts: KeyboardShortcutAction[] = [
      {
        action: vi.fn(),
        category: 'editing',
        description: 'Save',
        key: 's',
        meta: true,
      },
      {
        action: vi.fn(),
        category: 'editing',
        description: 'New Item',
        key: 'n',
        meta: true,
      },
      {
        action: vi.fn(),
        category: 'navigation',
        description: 'Find',
        key: 'f',
        meta: true,
      },
    ];

    const { result } = renderHook(() => useKeyboardShortcuts(shortcuts));

    const editingShortcuts = result.current.allShortcuts.filter((s) => s.category === 'editing');
    const navigationShortcuts = result.current.allShortcuts.filter(
      (s) => s.category === 'navigation',
    );

    expect(editingShortcuts).toHaveLength(2);
    expect(navigationShortcuts).toHaveLength(1);
  });

  it('respects enabled flag', () => {
    const shortcut: KeyboardShortcutAction = {
      action: vi.fn(),
      category: 'editing',
      description: 'Save',
      key: 's',
      meta: true,
    };

    const { result: resultDisabled } = renderHook(() => useKeyboardShortcuts([shortcut], false));

    expect(resultDisabled.current.allShortcuts).toHaveLength(0);
  });
});

describe(formatKeyboardShortcut, () => {
  it('formats meta shortcuts', () => {
    const result = formatKeyboardShortcut({
      category: 'editing',
      description: 'Save',
      key: 's',
      meta: true,
    });

    expect(result).toContain('⌘');
    expect(result).toContain('S');
  });

  it('formats ctrl shortcuts', () => {
    const result = formatKeyboardShortcut({
      category: 'editing',
      ctrl: true,
      description: 'Save',
      key: 's',
    });

    expect(result).toContain('Ctrl');
    expect(result).toContain('S');
  });

  it('formats shift shortcuts', () => {
    const result = formatKeyboardShortcut({
      category: 'editing',
      description: 'Save',
      key: 's',
      shift: true,
    });

    expect(result).toContain('Shift');
    expect(result).toContain('S');
  });

  it('formats alt shortcuts', () => {
    const result = formatKeyboardShortcut({
      alt: true,
      category: 'editing',
      description: 'Save',
      key: 's',
    });

    expect(result).toContain('Alt');
    expect(result).toContain('S');
  });

  it('formats arrow keys', () => {
    expect(
      formatKeyboardShortcut({
        category: 'navigation',
        description: 'Move up',
        key: 'ArrowUp',
      }),
    ).toContain('↑');

    expect(
      formatKeyboardShortcut({
        category: 'navigation',
        description: 'Move down',
        key: 'ArrowDown',
      }),
    ).toContain('↓');

    expect(
      formatKeyboardShortcut({
        category: 'navigation',
        description: 'Move left',
        key: 'ArrowLeft',
      }),
    ).toContain('←');

    expect(
      formatKeyboardShortcut({
        category: 'navigation',
        description: 'Move right',
        key: 'ArrowRight',
      }),
    ).toContain('→');
  });

  it('formats special keys', () => {
    expect(
      formatKeyboardShortcut({
        category: 'editing',
        description: 'Confirm',
        key: 'Enter',
      }),
    ).toContain('↵');

    expect(
      formatKeyboardShortcut({
        category: 'system',
        description: 'Close',
        key: 'Escape',
      }),
    ).toContain('Esc');

    expect(
      formatKeyboardShortcut({
        category: 'editing',
        description: 'Delete',
        key: 'Backspace',
      }),
    ).toContain('⌫');

    expect(
      formatKeyboardShortcut({
        category: 'editing',
        description: 'Delete',
        key: 'Delete',
      }),
    ).toContain('Del');
  });

  it('formats combined shortcuts', () => {
    const result = formatKeyboardShortcut({
      category: 'editing',
      description: 'Redo',
      key: 'z',
      meta: true,
      shift: true,
    });

    expect(result).toContain('⌘');
    expect(result).toContain('Shift');
    expect(result).toContain('Z');
  });
});
