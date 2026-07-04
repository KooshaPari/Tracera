/**
 * DiffViewer - Field-by-field diff visualization for modified items
 *
 * Features:
 * - Side-by-side field comparison
 * - Visual highlighting of old/new values
 * - Expandable field details
 * - Copy value functionality
 * - JSON value formatting
 */

import type { ReactNode } from 'react';

import { CheckCircle, ChevronDown, ChevronUp, Copy } from 'lucide-react';
import { useCallback, useState } from 'react';

import type { DiffItem, DiffViewerState, FieldDiffChange } from '@tracertm/types';

import { logger } from '@/lib/logger';

interface DiffViewerProps {
  item: DiffItem;
  fieldChanges: FieldDiffChange[];
  viewerState: DiffViewerState;
  compact?: boolean;
}

const COPY_RESET_MS = 2000;

const formatFieldChangeCount = (count: number): string => {
  let noun = 'fields';
  if (count === 1) {
    noun = 'field';
  }
  return `${count} ${noun} changed`;
};

const DiffViewer = ({ fieldChanges, compact = false }: DiffViewerProps): JSX.Element => {
  const [copiedField, setCopiedField] = useState<string | undefined>();

  const handleCopyValue = useCallback(async (value: unknown, field: string): Promise<void> => {
    const text = formatValueForCopy(value);
    try {
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(text);
      }
    } catch (error) {
      logger.warn('Failed to copy diff value', error);
    }
    setCopiedField(field);
    globalThis.setTimeout(() => {
      setCopiedField(undefined);
    }, COPY_RESET_MS);
  }, []);

  return (
    <div className='space-y-4'>
      <div className='text-sm font-medium text-gray-700'>
        {formatFieldChangeCount(fieldChanges.length)}
      </div>

      <div className='space-y-3'>
        {fieldChanges.map((change) => (
          <FieldChangeRow
            key={change.field}
            change={change}
            onCopy={handleCopyValue}
            isCopied={copiedField === change.field}
            compact={compact}
          />
        ))}
      </div>
    </div>
  );
};

interface FieldChangeRowProps {
  change: FieldDiffChange;
  onCopy: (value: unknown, field: string) => void;
  isCopied: boolean;
  compact?: boolean;
}

interface FieldChangeExpandedProps {
  change: FieldDiffChange;
  onCopyOld: () => void;
  onCopyNew: () => void;
  isCopied: boolean;
}

const FieldChangeExpanded = ({
  change,
  onCopyOld,
  onCopyNew,
  isCopied,
}: FieldChangeExpandedProps): JSX.Element => (
  <div className='mt-3 space-y-2'>
    {change.changeType !== 'added' && (
      <ValueDisplay
        label='Old Value'
        value={change.oldValue}
        type='old'
        onCopy={onCopyOld}
        isCopied={isCopied}
      />
    )}
    {change.changeType !== 'removed' && (
      <ValueDisplay
        label='New Value'
        value={change.newValue}
        type='new'
        onCopy={onCopyNew}
        isCopied={isCopied}
      />
    )}
  </div>
);

const getChangeTypeColor = (changeType: string): string => {
  switch (changeType) {
    case 'added': {
      return 'bg-green-50 border-l-green-500 text-green-900';
    }
    case 'removed': {
      return 'bg-red-50 border-l-red-500 text-red-900';
    }
    case 'modified': {
      return 'bg-blue-50 border-l-blue-500 text-blue-900';
    }
    default: {
      return 'bg-gray-50 border-l-gray-500';
    }
  }
};

const FieldChangeRow = ({
  change,
  onCopy,
  isCopied,
  compact = false,
}: FieldChangeRowProps): JSX.Element => {
  const [expanded, setExpanded] = useState(!compact);
  const toggleExpanded = useCallback(() => {
    setExpanded((value) => !value);
  }, []);
  const handleCopyOld = useCallback(() => {
    onCopy(change.oldValue, change.field);
  }, [onCopy, change.oldValue, change.field]);
  const handleCopyNew = useCallback(() => {
    onCopy(change.newValue, change.field);
  }, [onCopy, change.newValue, change.field]);
  let icon = <ChevronDown className='h-4 w-4 text-gray-500' />;
  if (expanded) {
    icon = <ChevronUp className='h-4 w-4 text-gray-500' />;
  }

  return (
    <div className={`border-l-4 ${getChangeTypeColor(change.changeType)} rounded-r-lg`}>
      <div className='p-4'>
        {/* Field Header */}
        <button
          type='button'
          className='flex w-full cursor-pointer items-center justify-between border-0 bg-transparent p-0 text-left'
          onClick={toggleExpanded}
        >
          <div className='flex items-center gap-2'>
            {icon}
            <span className='text-sm font-semibold'>{change.field}</span>
            <ChangeTypeBadge type={change.changeType} />
          </div>
        </button>
        {expanded && (
          <FieldChangeExpanded
            change={change}
            onCopyOld={handleCopyOld}
            onCopyNew={handleCopyNew}
            isCopied={isCopied}
          />
        )}
      </div>
    </div>
  );
};

interface ChangeTypeBadgeProps {
  type: string;
}

const BADGE_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  added: {
    bg: 'bg-green-100',
    label: 'Added',
    text: 'text-green-800',
  },
  modified: {
    bg: 'bg-blue-100',
    label: 'Modified',
    text: 'text-blue-800',
  },
  removed: {
    bg: 'bg-red-100',
    label: 'Removed',
    text: 'text-red-800',
  },
};

interface BadgeStyle {
  bg: string;
  text: string;
  label: string;
}

const DEFAULT_BADGE: BadgeStyle = BADGE_STYLES['modified'] as BadgeStyle;

const ChangeTypeBadge = ({ type }: ChangeTypeBadgeProps): JSX.Element => {
  const badge: BadgeStyle = BADGE_STYLES[type] ?? DEFAULT_BADGE;

  return (
    <span
      className={`inline-block rounded px-2 py-1 text-xs font-medium ${badge.bg} ${badge.text}`}
    >
      {badge.label}
    </span>
  );
};

interface ValueDisplayProps {
  label: string;
  value: unknown;
  type: 'old' | 'new';
  onCopy: () => void;
  isCopied: boolean;
}

const JSON_INDENT = 2;

const JSON_REPLACER = undefined;

const renderValueContent = (value: unknown): ReactNode => {
  if (value === undefined) {
    return <span className='italic opacity-60'>null</span>;
  }
  if (typeof value === 'object') {
    return (
      <pre className='whitespace-pre-wrap'>{JSON.stringify(value, JSON_REPLACER, JSON_INDENT)}</pre>
    );
  }
  if (typeof value === 'boolean') {
    let boolLabel = 'false';
    if (value) {
      boolLabel = 'true';
    }
    return <span>{boolLabel}</span>;
  }
  return <span>{String(value)}</span>;
};

const ValueDisplay = ({ label, value, type, onCopy, isCopied }: ValueDisplayProps): JSX.Element => {
  let valueClassName = 'bg-green-50 text-green-900';
  if (type === 'old') {
    valueClassName = 'bg-red-50 text-red-900';
  }
  let icon = <Copy className='h-4 w-4' />;
  if (isCopied) {
    icon = <CheckCircle className='h-4 w-4 text-green-600' />;
  }

  return (
    <div className='rounded border border-gray-200 bg-white'>
      <div className='flex items-center justify-between border-b border-gray-200 bg-gray-50 px-3 py-2'>
        <span className='text-xs font-medium text-gray-600'>{label}</span>
        <button
          type='button'
          onClick={onCopy}
          className='p-1 text-gray-400 transition-colors hover:text-gray-600'
          title='Copy to clipboard'
        >
          {icon}
        </button>
      </div>
      <div
        className={`max-h-48 overflow-y-auto px-3 py-3 font-mono text-sm break-words ${valueClassName}`}
      >
        {renderValueContent(value)}
      </div>
    </div>
  );
};

const formatValueForCopy = (value: unknown): string => {
  if (value === undefined) {
    return 'null';
  }
  if (typeof value === 'object') {
    return JSON.stringify(value, JSON_REPLACER, JSON_INDENT);
  }
  return String(value);
};

export { DiffViewer, type DiffViewerProps };
export default DiffViewer;
