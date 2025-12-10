'use client';

import { useState } from 'react';
import { Copy, Check, Terminal } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CLICommandProps {
  command: string;
  output?: string;
  description?: string;
  className?: string;
}

/**
 * CLICommand - Display CLI commands with output and copy functionality
 *
 * Features:
 * - Terminal-styled display
 * - Copy command to clipboard
 * - Optional command output
 * - Optional description
 */
export function CLICommand({
  command,
  output,
  description,
  className,
}: CLICommandProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={cn('my-4 rounded-lg border overflow-hidden', className)}>
      {/* Description */}
      {description && (
        <div className="px-4 py-2 border-b bg-muted/30 text-sm text-muted-foreground">
          {description}
        </div>
      )}

      {/* Command */}
      <div className="flex items-center gap-2 px-4 py-3 bg-zinc-900 text-zinc-100">
        <Terminal className="w-4 h-4 text-zinc-400 flex-shrink-0" />
        <code className="flex-1 font-mono text-sm break-all">{command}</code>
        <button
          onClick={handleCopy}
          className="p-1 hover:bg-zinc-800 rounded transition-colors flex-shrink-0"
          title="Copy command"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-500" />
          ) : (
            <Copy className="w-4 h-4 text-zinc-400" />
          )}
        </button>
      </div>

      {/* Output */}
      {output && (
        <pre className="px-4 py-3 bg-zinc-800 text-zinc-300 overflow-x-auto border-t border-zinc-700">
          <code className="text-sm font-mono whitespace-pre">{output}</code>
        </pre>
      )}
    </div>
  );
}
