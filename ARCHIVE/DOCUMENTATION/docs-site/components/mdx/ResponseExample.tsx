'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';
import { Copy, Check } from 'lucide-react';

interface ResponseExampleProps {
  status: number;
  statusText?: string;
  headers?: Record<string, string>;
  body: object | string;
  className?: string;
}

/**
 * ResponseExample - Display API response examples with copy functionality
 *
 * Features:
 * - Syntax-highlighted JSON
 * - HTTP status code with color coding
 * - Optional headers display
 * - Copy to clipboard
 * - Dark mode support
 */
export function ResponseExample({
  status,
  statusText,
  headers,
  body,
  className,
}: ResponseExampleProps) {
  const [copied, setCopied] = useState(false);

  const statusColor =
    status >= 200 && status < 300
      ? 'text-green-500'
      : status >= 400
        ? 'text-red-500'
        : 'text-yellow-500';

  const jsonBody = typeof body === 'string' ? body : JSON.stringify(body, null, 2);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(jsonBody);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={cn('my-4 rounded-lg border overflow-hidden', className)}>
      {/* Header with status code */}
      <div className="flex items-center justify-between px-4 py-2 bg-muted/50 border-b">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Response</span>
          <span className={cn('font-mono text-sm font-bold', statusColor)}>
            {status}
          </span>
          {statusText && (
            <span className="text-sm text-muted-foreground">{statusText}</span>
          )}
        </div>
        <button
          onClick={handleCopy}
          className="p-1 hover:bg-accent rounded transition-colors"
          title="Copy to clipboard"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-500" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Headers */}
      {headers && Object.keys(headers).length > 0 && (
        <div className="px-4 py-2 border-b bg-muted/30">
          <div className="text-xs text-muted-foreground mb-1 font-semibold">
            Headers
          </div>
          <div className="space-y-0.5">
            {Object.entries(headers).map(([key, value]) => (
              <div key={key} className="font-mono text-xs">
                <span className="text-blue-600 dark:text-blue-400">{key}</span>
                <span className="text-muted-foreground">: </span>
                <span className="text-foreground">{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Body */}
      <pre className="p-4 overflow-x-auto bg-zinc-950 dark:bg-zinc-900 text-zinc-100">
        <code className="text-sm font-mono">{jsonBody}</code>
      </pre>
    </div>
  );
}
