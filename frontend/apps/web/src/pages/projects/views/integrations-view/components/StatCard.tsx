import type { ReactElement } from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle: string;
  warning?: boolean;
}

function containerClassName(warning: boolean): string {
  const base = 'rounded-lg border bg-white p-4 dark:bg-gray-800';
  if (warning) {
    return `${base} border-red-300 dark:border-red-700`;
  }
  return `${base} border-gray-200 dark:border-gray-700`;
}

function valueClassName(warning: boolean): string {
  const base = 'text-2xl font-bold';
  if (warning) {
    return `${base} text-red-600`;
  }
  return `${base} text-gray-900 dark:text-white`;
}

export default function StatCard({
  title,
  value,
  subtitle,
  warning = false,
}: StatCardProps): ReactElement {
  return (
    <div className={containerClassName(warning)}>
      <div className='text-sm text-gray-500'>{title}</div>
      <div className={valueClassName(warning)}>{value}</div>
      <div className='text-xs text-gray-400'>{subtitle}</div>
    </div>
  );
}
