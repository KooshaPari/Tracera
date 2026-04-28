import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface APIEndpointProps {
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  path: string;
  description?: string;
  children?: ReactNode;
  className?: string;
}

const METHOD_COLORS = {
  GET: 'bg-blue-500 text-white',
  POST: 'bg-green-500 text-white',
  PUT: 'bg-yellow-500 text-white',
  PATCH: 'bg-orange-500 text-white',
  DELETE: 'bg-red-500 text-white',
} as const;

/**
 * APIEndpoint - Display API endpoint with method badge
 *
 * Features:
 * - Color-coded HTTP method badges
 * - Endpoint path
 * - Optional description
 * - Optional children for additional content
 */
export function APIEndpoint({
  method,
  path,
  description,
  children,
  className,
}: APIEndpointProps) {
  return (
    <div className={cn('my-4 rounded-lg border overflow-hidden', className)}>
      {/* Endpoint header */}
      <div className="flex items-center gap-3 px-4 py-3 bg-muted/50 border-b">
        <span
          className={cn(
            'px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wide',
            METHOD_COLORS[method]
          )}
        >
          {method}
        </span>
        <code className="flex-1 font-mono text-sm font-semibold">{path}</code>
      </div>

      {/* Description */}
      {description && (
        <div className="px-4 py-3 text-sm text-muted-foreground border-b">
          {description}
        </div>
      )}

      {/* Additional content */}
      {children && <div className="px-4 py-3">{children}</div>}
    </div>
  );
}
