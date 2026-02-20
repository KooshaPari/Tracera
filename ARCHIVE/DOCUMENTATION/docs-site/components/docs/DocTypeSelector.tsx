'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import {
  Users,
  Code,
  Zap,
  Package,
  Monitor,
  ChevronDown,
  Check,
} from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Documentation type definitions with metadata
 */
const DOC_TYPES = [
  {
    id: 'user',
    label: 'User Docs',
    description: 'For business users & analysts',
    icon: Users,
    basePath: '/docs/user',
    color: 'text-blue-500',
  },
  {
    id: 'developer',
    label: 'Developer Docs',
    description: 'For engineers & contributors',
    icon: Code,
    basePath: '/docs/developer',
    color: 'text-green-500',
  },
  {
    id: 'api',
    label: 'API Reference',
    description: 'REST & GraphQL documentation',
    icon: Zap,
    basePath: '/docs/api',
    color: 'text-yellow-500',
  },
  {
    id: 'sdk',
    label: 'SDK Docs',
    description: 'Python, JavaScript, Go SDKs',
    icon: Package,
    basePath: '/docs/sdk',
    color: 'text-purple-500',
  },
  {
    id: 'clients',
    label: 'Client Guides',
    description: 'Web UI, CLI, Desktop apps',
    icon: Monitor,
    basePath: '/docs/clients',
    color: 'text-orange-500',
  },
] as const;

type DocTypeId = (typeof DOC_TYPES)[number]['id'];

interface DocTypeSelectorProps {
  /** Additional CSS classes */
  className?: string;
  /** Compact mode for mobile */
  compact?: boolean;
}

/**
 * DocTypeSelector - Combobox navigation for switching between documentation types
 *
 * Features:
 * - Auto-detects current doc type from URL
 * - Keyboard navigation support
 * - Click outside to close
 * - Escape key to close
 * - Visual indicator of current selection
 */
export function DocTypeSelector({ className, compact }: DocTypeSelectorProps) {
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const pathname = usePathname();
  const containerRef = useRef<HTMLDivElement>(null);

  // Determine current doc type from URL
  const currentType =
    DOC_TYPES.find((type) => pathname.startsWith(type.basePath)) || DOC_TYPES[0];

  // Handle selection
  const handleSelect = (type: (typeof DOC_TYPES)[number]) => {
    setOpen(false);
    if (type.basePath !== currentType.basePath) {
      router.push(type.basePath);
    }
  };

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    };

    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [open]);

  // Close on escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpen(false);
      }
    };

    if (open) {
      document.addEventListener('keydown', handleEscape);
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [open]);

  const IconComponent = currentType.icon;

  return (
    <div ref={containerRef} className={cn('relative', className)}>
      {/* Trigger Button */}
      <button
        onClick={() => setOpen(!open)}
        className={cn(
          'flex items-center gap-2 rounded-lg transition-colors',
          'bg-muted hover:bg-muted/80',
          'text-sm font-medium w-full',
          compact ? 'px-2 py-1.5' : 'px-3 py-2'
        )}
        aria-expanded={open}
        aria-haspopup="listbox"
        aria-label="Select documentation type"
      >
        <IconComponent className={cn('w-4 h-4', currentType.color)} />
        {!compact && (
          <>
            <span className="flex-1 text-left truncate">{currentType.label}</span>
            <ChevronDown
              className={cn(
                'w-4 h-4 text-muted-foreground transition-transform duration-200',
                open && 'rotate-180'
              )}
            />
          </>
        )}
      </button>

      {/* Dropdown Menu */}
      {open && (
        <div
          className={cn(
            'absolute top-full left-0 right-0 mt-1 z-50',
            'rounded-lg border shadow-lg bg-popover',
            'py-1 overflow-hidden',
            'animate-in fade-in-0 zoom-in-95 duration-100'
          )}
          role="listbox"
          aria-label="Documentation types"
        >
          {DOC_TYPES.map((type) => {
            const TypeIcon = type.icon;
            const isSelected = currentType.id === type.id;

            return (
              <button
                key={type.id}
                onClick={() => handleSelect(type)}
                className={cn(
                  'flex items-center gap-3 w-full px-3 py-2',
                  'text-left transition-colors',
                  'hover:bg-accent',
                  isSelected && 'bg-accent/50'
                )}
                role="option"
                aria-selected={isSelected}
              >
                <TypeIcon className={cn('w-4 h-4 flex-shrink-0', type.color)} />
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm">{type.label}</div>
                  <div className="text-xs text-muted-foreground truncate">
                    {type.description}
                  </div>
                </div>
                {isSelected && (
                  <Check className="w-4 h-4 text-primary flex-shrink-0" />
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default DocTypeSelector;
