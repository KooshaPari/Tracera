import type { ReactElement } from 'react';

const STATUS_COLORS: Record<string, string> = {
  active: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  completed: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  expired: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
  failed: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  paused: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  pending: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  processing: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
};

function statusClassName(status: string): string {
  const base = 'rounded px-2 py-1 text-xs font-medium';
  const colorClasses = STATUS_COLORS[status];
  if (colorClasses !== undefined) {
    return `${base} ${colorClasses}`;
  }
  return `${base} bg-gray-100 text-gray-700`;
}

export default function StatusBadge({ status }: { status: string }): ReactElement {
  return <span className={statusClassName(status)}>{status}</span>;
}
