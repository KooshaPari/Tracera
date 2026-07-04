import { X } from 'lucide-react';
import { useEffect } from 'react';

import type { KeyboardShortcut } from '@/hooks/useKeyboardShortcuts';

import { formatKeyboardShortcut } from '@/hooks/useKeyboardShortcuts';
import { cn } from '@/lib/utils';

const categoryLabels: Record<string, string> = {
  editing: 'Editing',
  navigation: 'Navigation',
  selection: 'Selection',
  system: 'System',
};

const categoryIcons: Record<string, string> = {
  editing: '✏️',
  navigation: '🧭',
  selection: '☑️',
  system: '⚙️',
};

interface KeyboardShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
  shortcuts: KeyboardShortcut[];
}

interface ShortcutRowProps {
  shortcut: KeyboardShortcut;
}

const ShortcutRow = ({ shortcut }: ShortcutRowProps) => {
  const parts = formatKeyboardShortcut(shortcut).split('+');
  return (
    <div className='bg-muted/20 border-border/30 hover:border-border/50 hover:bg-muted/40 flex items-start justify-between gap-4 rounded-xl border p-4 transition-colors'>
      <div className='min-w-0 flex-1'>
        <p className='text-sm leading-tight font-bold'>{shortcut.description}</p>
        {shortcut.context && (
          <p className='text-muted-foreground mt-1 text-[11px] font-bold tracking-widest uppercase'>
            Context: {shortcut.context}
          </p>
        )}
      </div>
      <div className='flex shrink-0 items-center gap-2'>
        {parts.map((part, idx) => (
          <div key={`${part}-${idx}`}>
            {idx > 0 && <span className='text-muted-foreground mx-1 text-xs'>+</span>}
            <kbd
              className={cn(
                'px-2.5 py-1.5 rounded-lg border font-bold text-[11px] uppercase tracking-widest whitespace-nowrap inline-block',
                part === '+' ? 'hidden' : 'bg-background border-border/60 shadow-sm',
              )}
            >
              {part}
            </kbd>
          </div>
        ))}
      </div>
    </div>
  );
};

interface CategorySectionProps {
  categoryKey: string;
  categoryLabel: string;
  shortcuts: KeyboardShortcut[];
}

const CategorySection = ({ categoryKey, categoryLabel, shortcuts }: CategorySectionProps) => {
  if (shortcuts.length === 0) {
    return null;
  }

  return (
    <div key={categoryKey}>
      <div className='mb-4 flex items-center gap-3'>
        <span className='text-2xl'>{categoryIcons[categoryKey] ?? '•'}</span>
        <h3 className='text-muted-foreground text-sm font-black tracking-[0.2em] uppercase'>
          {categoryLabel}
        </h3>
        <div className='bg-border/50 h-px flex-1' />
      </div>

      <div className='grid grid-cols-1 gap-4 md:grid-cols-2'>
        {shortcuts.map((shortcut, idx) => (
          <ShortcutRow
            key={`${shortcut.category}-${shortcut.description}-${idx}`}
            shortcut={shortcut}
          />
        ))}
      </div>
    </div>
  );
};

interface ModalContentProps {
  onClose: () => void;
  shortcuts: KeyboardShortcut[];
}

const ModalContent = ({ onClose, shortcuts }: ModalContentProps) => {
  const grouped = shortcuts.reduce<Record<string, KeyboardShortcut[]>>((acc, shortcut) => {
    const category = shortcut.category || 'system';
    acc[category] ??= [];
    acc[category].push(shortcut);
    return acc;
  }, {});

  return (
    <div
      className='bg-card border-border/50 animate-in zoom-in-95 slide-in-from-top-4 ring-primary/20 relative flex max-h-[85vh] w-full max-w-3xl flex-col overflow-hidden rounded-[2rem] border shadow-2xl ring-1 duration-300'
      onClick={(e) => {
        e.stopPropagation();
      }}
    >
      {/* Header */}
      <div className='bg-muted/30 flex items-center justify-between border-b px-8 py-6'>
        <div>
          <h2 className='text-2xl font-black tracking-tight uppercase'>⌨️ Keyboard Shortcuts</h2>
          <p className='text-muted-foreground mt-1 text-xs font-bold tracking-widest uppercase'>
            Master power user commands
          </p>
        </div>
        <button
          onClick={onClose}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              onClose();
            }
          }}
          className='hover:bg-muted rounded-lg p-2 transition-colors'
          aria-label='Close shortcuts modal'
          type='button'
        >
          <X className='h-6 w-6' />
        </button>
      </div>

      {/* Content */}
      <div className='custom-scrollbar flex-1 overflow-y-auto'>
        <div className='space-y-8 p-8'>
          {Object.entries(categoryLabels).map(([categoryKey, categoryLabel]) => (
            <CategorySection
              key={categoryKey}
              categoryKey={categoryKey}
              categoryLabel={categoryLabel}
              shortcuts={grouped[categoryKey] ?? []}
            />
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className='bg-muted/20 text-muted-foreground/60 flex items-center justify-between border-t px-8 py-4 text-[10px] font-black tracking-widest uppercase'>
        <span>Press ESC or ? to close</span>
        <div className='flex items-center gap-2'>
          <div className='h-1.5 w-1.5 rounded-full bg-green-500' />
          <span>{shortcuts.length} Shortcuts Available</span>
        </div>
      </div>
    </div>
  );
};

export function KeyboardShortcutsModal({
  isOpen,
  onClose,
  shortcuts,
}: KeyboardShortcutsModalProps) {
  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        event.preventDefault();
        onClose();
      }
    };

    if (isOpen) {
      globalThis.addEventListener('keydown', handler);
      return () => {
        globalThis.removeEventListener('keydown', handler);
      };
    }
    return;
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  return (
    <div
      className='fixed inset-0 z-[101] flex items-center justify-center px-4'
      onClick={onClose}
      onKeyDown={(e) => {
        if (e.key === 'Escape') {
          onClose();
        }
      }}
      role='dialog'
      aria-modal='true'
      aria-labelledby='shortcuts-modal-title'
    >
      <div className='bg-background/80 fixed inset-0 backdrop-blur-sm' />

      <ModalContent onClose={onClose} shortcuts={shortcuts} />
    </div>
  );
}
