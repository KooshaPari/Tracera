import { useCallback, useEffect, useMemo, useState } from 'react';

export interface KeyboardShortcut {
  key: string;
  meta?: boolean | undefined;
  ctrl?: boolean | undefined;
  shift?: boolean | undefined;
  alt?: boolean | undefined;
  description: string;
  category: 'navigation' | 'selection' | 'editing' | 'system';
  context?: string | undefined;
}

export interface KeyboardShortcutAction extends KeyboardShortcut {
  action: () => void;
  enabled?: boolean | undefined;
}

interface RegisteredShortcut {
  shortcut: KeyboardShortcutAction;
  id: string;
}

let shortcutRegistry: RegisteredShortcut[] = [];
let shortcutCounter = 0;

// Export for testing purposes
export function __resetKeyboardShortcutsRegistry() {
  shortcutRegistry = [];
  shortcutCounter = 0;
}

export function useKeyboardShortcuts(
  shortcuts: KeyboardShortcutAction[],
  enabled = true,
): {
  isShortcutsModalOpen: boolean;
  setIsShortcutsModalOpen: (open: boolean) => void;
  allShortcuts: KeyboardShortcut[];
  register: (shortcut: KeyboardShortcutAction) => () => void;
  unregister: (id: string) => void;
} {
  const [isShortcutsModalOpen, setIsShortcutsModalOpen] = useState(false);
  const [_registeredShortcuts, setRegisteredShortcuts] = useState<RegisteredShortcut[]>([]);

  // Add provided shortcuts to registry
  useEffect(() => {
    if (!enabled) {
      return;
    }

    const shortcutIds = new Set(
      shortcuts.map((shortcut) => {
        const id = `shortcut-${shortcutCounter++}`;
        shortcutRegistry.push({ id, shortcut });
        return id;
      }),
    );

    setRegisteredShortcuts([...shortcutRegistry]);

    return () => {
      shortcutRegistry = shortcutRegistry.filter((item) => !shortcutIds.has(item.id));
      setRegisteredShortcuts([...shortcutRegistry]);
    };
  }, [shortcuts, enabled]);

  const allShortcuts = useMemo(
    () =>
      shortcutRegistry.map((item) => ({
        alt: item.shortcut.alt,
        category: item.shortcut.category,
        context: item.shortcut.context,
        ctrl: item.shortcut.ctrl,
        description: item.shortcut.description,
        key: item.shortcut.key,
        meta: item.shortcut.meta,
        shift: item.shortcut.shift,
      })),
    [],
  );

  // Global keyboard listener
  useEffect(() => {
    if (!enabled) {
      return;
    }

    const handler = (event: KeyboardEvent) => {
      // Check for shortcuts modal trigger (?)
      if (
        event.key === '?' &&
        !event.ctrlKey &&
        !event.metaKey &&
        !event.shiftKey &&
        !event.altKey
      ) {
        event.preventDefault();
        setIsShortcutsModalOpen(true);
        return;
      }

      // Check registered shortcuts
      for (const registered of shortcutRegistry) {
        const { shortcut } = registered;

        const metaMatch = shortcut.meta === undefined || event.metaKey === shortcut.meta;
        const ctrlMatch = shortcut.ctrl === undefined || event.ctrlKey === shortcut.ctrl;
        const shiftMatch = shortcut.shift === undefined || event.shiftKey === shortcut.shift;
        const altMatch = shortcut.alt === undefined || event.altKey === shortcut.alt;
        const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase();

        if (
          keyMatch &&
          metaMatch &&
          ctrlMatch &&
          shiftMatch &&
          altMatch &&
          shortcut.enabled !== false
        ) {
          event.preventDefault();
          shortcut.action();
          return;
        }
      }
    };

    globalThis.addEventListener('keydown', handler);
    return () => {
      globalThis.removeEventListener('keydown', handler);
    };
  }, [enabled]);

  const register = useCallback((shortcut: KeyboardShortcutAction) => {
    const id = `shortcut-${(shortcutCounter += 1)}`;
    shortcutRegistry.push({ id, shortcut });
    setRegisteredShortcuts([...shortcutRegistry]);

    return () => {
      shortcutRegistry = shortcutRegistry.filter((item) => item.id !== id);
      setRegisteredShortcuts([...shortcutRegistry]);
    };
  }, []);

  const unregister = useCallback((id: string) => {
    shortcutRegistry = shortcutRegistry.filter((item) => item.id !== id);
    setRegisteredShortcuts([...shortcutRegistry]);
  }, []);

  return {
    allShortcuts,
    isShortcutsModalOpen,
    register,
    setIsShortcutsModalOpen,
    unregister,
  };
}

// Helper function to format keyboard shortcut display
export function formatKeyboardShortcut(shortcut: KeyboardShortcut): string {
  const parts: string[] = [];

  if (shortcut.meta) {
    parts.push('⌘');
  }
  if (shortcut.ctrl) {
    parts.push('Ctrl');
  }
  if (shortcut.alt) {
    parts.push('Alt');
  }
  if (shortcut.shift) {
    parts.push('Shift');
  }

  // Format key
  let displayKey = shortcut.key.toUpperCase();
  if (shortcut.key.length === 1) {
    displayKey = shortcut.key.toUpperCase();
  } else if (shortcut.key === 'ArrowUp') {
    displayKey = '↑';
  } else if (shortcut.key === 'ArrowDown') {
    displayKey = '↓';
  } else if (shortcut.key === 'ArrowLeft') {
    displayKey = '←';
  } else if (shortcut.key === 'ArrowRight') {
    displayKey = '→';
  } else if (shortcut.key === 'Enter') {
    displayKey = '↵';
  } else if (shortcut.key === 'Escape') {
    displayKey = 'Esc';
  } else if (shortcut.key === 'Backspace') {
    displayKey = '⌫';
  } else if (shortcut.key === 'Delete') {
    displayKey = 'Del';
  }

  parts.push(displayKey);

  return parts.join('+');
}
