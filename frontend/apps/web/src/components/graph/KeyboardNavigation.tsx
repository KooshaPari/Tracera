// Keyboard Navigation Component
// Provides keyboard shortcuts for graph navigation
// Arrow keys, Enter, Escape support

import {
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  CornerDownLeft,
  HelpCircle,
} from 'lucide-react';
import { memo, useEffect, useState } from 'react';

import { cn } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Card } from '@tracertm/ui/components/Card';

/**
 * Keyboard shortcuts configuration
 */
export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  description: string;
  action: string;
}

const DEFAULT_SHORTCUTS: KeyboardShortcut[] = [
  {
    action: 'navigate-parent',
    description: 'Navigate to parent node',
    key: 'ArrowUp',
  },
  {
    action: 'navigate-child',
    description: 'Navigate to first child node',
    key: 'ArrowDown',
  },
  {
    action: 'collapse',
    description: 'Collapse node',
    key: 'ArrowLeft',
  },
  {
    action: 'expand',
    description: 'Expand node',
    key: 'ArrowRight',
  },
  {
    action: 'toggle-expansion',
    description: 'Toggle node expansion',
    key: 'Enter',
  },
  {
    action: 'navigate-back',
    description: 'Go back in navigation history',
    key: 'Backspace',
  },
  {
    action: 'close-panel',
    description: 'Close current panel/deselect',
    key: 'Escape',
  },
  {
    action: 'open-search',
    ctrl: true,
    description: 'Open search',
    key: 'f',
  },
];

interface KeyboardNavigationProps {
  onKeyPress: (action: string, event: KeyboardEvent) => void;
  shortcuts?: KeyboardShortcut[];
  showHelp?: boolean;
  className?: string;
}

/**
 * Format keyboard shortcut display
 */
function formatShortcut(shortcut: KeyboardShortcut): string {
  const parts: string[] = [];

  if (shortcut.ctrl) {
    parts.push('Ctrl');
  }
  if (shortcut.shift) {
    parts.push('Shift');
  }
  if (shortcut.alt) {
    parts.push('Alt');
  }

  const keyLabel =
    shortcut.key === 'ArrowUp'
      ? '↑'
      : shortcut.key === 'ArrowDown'
        ? '↓'
        : shortcut.key === 'ArrowLeft'
          ? '←'
          : shortcut.key === 'ArrowRight'
            ? '→'
            : shortcut.key === 'Enter'
              ? 'Return'
              : shortcut.key === 'Backspace'
                ? 'Backspace'
                : shortcut.key === 'Escape'
                  ? 'Esc'
                  : shortcut.key.toUpperCase();

  parts.push(keyLabel);
  return parts.join('+');
}

/**
 * Get icon for keyboard action
 */
function getActionIcon(action: string) {
  switch (action) {
    case 'navigate-parent': {
      return <ArrowUp className='h-4 w-4' />;
    }
    case 'navigate-child': {
      return <ArrowDown className='h-4 w-4' />;
    }
    case 'collapse': {
      return <ArrowLeft className='h-4 w-4' />;
    }
    case 'expand': {
      return <ArrowRight className='h-4 w-4' />;
    }
    case 'toggle-expansion': {
      return <CornerDownLeft className='h-4 w-4' />;
    }
    case 'navigate-back': {
      return <ArrowLeft className='h-4 w-4' />;
    }
    case 'close-panel': {
      return <button className='text-base leading-none'>×</button>;
    }
    default: {
      return null;
    }
  }
}

/**
 * Keyboard Navigation Controller Component
 */
function KeyboardNavigationComponent({
  onKeyPress,
  shortcuts = DEFAULT_SHORTCUTS,
  showHelp = false,
  className,
}: KeyboardNavigationProps) {
  const [showHelpPanel, setShowHelpPanel] = useState(showHelp);

  // Handle keyboard events
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Check shortcuts
      for (const shortcut of shortcuts) {
        const keyMatch =
          event.key === shortcut.key ||
          (event.key === 'Enter' && shortcut.key === 'Enter') ||
          (event.key === 'Escape' && shortcut.key === 'Escape') ||
          (event.key === 'Backspace' && shortcut.key === 'Backspace') ||
          (event.key === 'ArrowUp' && shortcut.key === 'ArrowUp') ||
          (event.key === 'ArrowDown' && shortcut.key === 'ArrowDown') ||
          (event.key === 'ArrowLeft' && shortcut.key === 'ArrowLeft') ||
          (event.key === 'ArrowRight' && shortcut.key === 'ArrowRight') ||
          event.key.toLowerCase() === shortcut.key.toLowerCase();

        const ctrlMatch = shortcut.ctrl
          ? event.ctrlKey || event.metaKey
          : !event.ctrlKey && !event.metaKey;
        const shiftMatch = shortcut.shift ? event.shiftKey : !event.shiftKey;
        const altMatch = shortcut.alt ? event.altKey : !event.altKey;

        if (keyMatch && ctrlMatch && shiftMatch && altMatch) {
          // Special handling for help toggle
          if (shortcut.action === 'open-search') {
            event.preventDefault();
            setShowHelpPanel(!showHelpPanel);
            return;
          }

          onKeyPress(shortcut.action, event);
          break;
        }
      }
    };

    globalThis.addEventListener('keydown', handleKeyDown);

    return () => {
      globalThis.removeEventListener('keydown', handleKeyDown);
    };
  }, [onKeyPress, shortcuts, showHelpPanel]);

  return (
    <>
      {/* Help panel */}
      {showHelpPanel && (
        <Card className={cn('absolute bottom-4 right-4 w-80 p-4', className)}>
          <div className='space-y-3'>
            <div className='mb-4 flex items-center justify-between'>
              <h3 className='flex items-center gap-2 font-semibold'>
                <HelpCircle className='h-4 w-4' />
                Keyboard Shortcuts
              </h3>
              <button
                onClick={() => {
                  setShowHelpPanel(false);
                }}
                className='text-muted-foreground hover:text-foreground'
                type='button'
              >
                ×
              </button>
            </div>

            <div className='max-h-80 space-y-2 overflow-y-auto'>
              {shortcuts.map((shortcut) => (
                <div
                  key={`${shortcut.key}-${shortcut.ctrl}-${shortcut.shift}-${shortcut.alt}`}
                  className='hover:bg-muted/50 flex items-center justify-between gap-2 rounded-md p-2 transition-colors'
                >
                  <div className='flex min-w-0 flex-1 items-center gap-2'>
                    {getActionIcon(shortcut.action) && (
                      <div className='text-muted-foreground shrink-0'>
                        {getActionIcon(shortcut.action)}
                      </div>
                    )}
                    <span className='truncate text-sm'>{shortcut.description}</span>
                  </div>
                  <Badge variant='outline' className='shrink-0 font-mono text-xs'>
                    {formatShortcut(shortcut)}
                  </Badge>
                </div>
              ))}
            </div>

            <div className='text-muted-foreground border-t pt-3 text-xs'>
              Press{' '}
              <Badge variant='secondary' className='text-[10px]'>
                Ctrl+F
              </Badge>{' '}
              to toggle this help panel
            </div>
          </div>
        </Card>
      )}
    </>
  );
}

/**
 * Keyboard shortcut reference card
 */
export function KeyboardShortcutCard({
  shortcuts = DEFAULT_SHORTCUTS,
  className,
}: {
  shortcuts?: KeyboardShortcut[];
  className?: string;
}) {
  return (
    <Card className={cn('p-4', className)}>
      <h3 className='mb-4 flex items-center gap-2 font-semibold'>
        <HelpCircle className='h-4 w-4' />
        Keyboard Shortcuts
      </h3>

      <div className='grid grid-cols-2 gap-3'>
        {shortcuts.map((shortcut) => (
          <div key={`${shortcut.key}-ref`} className='space-y-1'>
            <Badge variant='outline' className='font-mono text-xs'>
              {formatShortcut(shortcut)}
            </Badge>
            <p className='text-muted-foreground text-xs'>{shortcut.description}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}

export const KeyboardNavigation = memo(KeyboardNavigationComponent);
