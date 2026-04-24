import type { ReactNode } from 'react';

import { X } from 'lucide-react';
import { useCallback, useEffect, useRef } from 'react';

import { cn } from '@/lib/utils';

interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string | undefined;
  children: ReactNode;
  className?: string | undefined;
  showHandle?: boolean | undefined;
  dismissible?: boolean | undefined;
}

/**
 * Mobile-optimized bottom sheet modal that slides up from bottom
 * Perfect for mobile dialogs with good touch interaction
 */
export const BottomSheet = function BottomSheet({
  isOpen,
  onClose,
  title,
  children,
  className,
  showHandle = true,
  dismissible = true,
}: BottomSheetProps) {
  const sheetRef = useRef<HTMLDivElement>(null);

  // Handle escape key
  useEffect(() => {
    if (!isOpen || !dismissible) {
      return;
    }

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    globalThis.addEventListener('keydown', handleEscape);
    return () => {
      globalThis.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, dismissible, onClose]);

  // Prevent body scroll when sheet is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) {
    return null;
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className='fixed inset-0 z-40 bg-black/40 transition-opacity duration-300'
        onClick={dismissible ? onClose : undefined}
        aria-hidden='true'
      />

      {/* Bottom Sheet */}
      <div
        ref={sheetRef}
        className={cn(
          'fixed bottom-0 left-0 right-0 z-50',
          'bg-background rounded-t-2xl sm:rounded-t-3xl',
          'border-t border-border/30',
          'max-h-[80vh] overflow-y-auto',
          'animate-in slide-in-from-bottom-5 duration-300',
          className,
        )}
      >
        {/* Handle indicator for touch */}
        {showHandle && (
          <div className='flex justify-center pt-2 pb-1'>
            <div className='bg-muted-foreground/20 h-1 w-12 rounded-full' />
          </div>
        )}

        {/* Header */}
        {title && (
          <div className='bg-background border-border/30 sticky top-0 flex items-center justify-between gap-4 border-b px-4 py-4 sm:px-6 sm:py-5'>
            <h2 className='text-foreground text-lg font-semibold sm:text-xl'>{title}</h2>
            {dismissible && (
              <button
                onClick={onClose}
                className={cn(
                  'h-10 w-10 rounded-lg flex items-center justify-center',
                  'text-muted-foreground hover:text-foreground hover:bg-muted',
                  'transition-all duration-200',
                  'focus:outline-none focus:ring-2 focus:ring-primary',
                  'min-h-[44px] min-w-[44px]',
                )}
                aria-label='Close'
              >
                <X className='h-5 w-5' />
              </button>
            )}
          </div>
        )}

        {/* Content */}
        <div className='p-4 sm:p-6'>{children}</div>
      </div>
    </>
  );
};

export interface MobilePickerOption {
  value: string | number;
  label: string;
  description?: string | undefined;
  disabled?: boolean | undefined;
}

interface MobilePickerProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string | undefined;
  options: MobilePickerOption[];
  selectedValue?: string | number | undefined;
  onSelect: (value: string | number) => void;
}

/**
 * Mobile picker optimized for touch with large tap targets
 */
export const MobilePicker = function MobilePicker({
  isOpen,
  onClose,
  title,
  options,
  selectedValue,
  onSelect,
}: MobilePickerProps) {
  const handleSelect = useCallback(
    (value: string | number) => {
      onSelect(value);
      onClose();
    },
    [onSelect, onClose],
  );

  const handleOptionClick = useCallback(
    (e: React.MouseEvent<HTMLButtonElement>) => {
      const raw = e.currentTarget.getAttribute('data-value');
      if (raw === null || raw === undefined) {
        return;
      }
      try {
        const value = JSON.parse(raw) as string | number;
        handleSelect(value);
      } catch {
        // Ignore invalid data-value
      }
    },
    [handleSelect],
  );

  return (
    <BottomSheet isOpen={isOpen} onClose={onClose} title={title}>
      <div className='space-y-2'>
        {options.map((option) => (
          <button
            key={option.value}
            data-value={JSON.stringify(option.value)}
            onClick={handleOptionClick}
            disabled={option.disabled}
            className={cn(
              'w-full px-4 py-4 rounded-lg text-left',
              'min-h-[56px] flex items-center gap-3',
              'transition-all duration-200',
              'focus:outline-none focus:ring-2 focus:ring-primary',
              'active:scale-95 transition-transform',
              option.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-muted',
              selectedValue === option.value
                ? 'bg-primary/10 border border-primary/30'
                : 'border border-transparent',
            )}
          >
            <div className='flex-1'>
              <div className='text-foreground font-medium'>{option.label}</div>
              {option.description && (
                <div className='text-muted-foreground mt-0.5 text-xs sm:text-sm'>
                  {option.description}
                </div>
              )}
            </div>
            {selectedValue === option.value && <div className='bg-primary h-5 w-5 rounded-full' />}
          </button>
        ))}
      </div>
    </BottomSheet>
  );
};
