import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface TypeProperty {
  type: string;
  required?: boolean;
  default?: string | number | boolean;
  description: string | ReactNode;
}

interface TypeTableProps {
  type: Record<string, TypeProperty>;
  className?: string;
}

/**
 * TypeTable - Display type definitions for API parameters or TypeScript interfaces
 *
 * Features:
 * - Required/optional indicators
 * - Type annotations
 * - Default values
 * - Descriptions
 */
export function TypeTable({ type, className }: TypeTableProps) {
  return (
    <div className={cn('my-4 overflow-x-auto', className)}>
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b bg-muted/50">
            <th className="px-4 py-2 text-left font-semibold">Property</th>
            <th className="px-4 py-2 text-left font-semibold">Type</th>
            <th className="px-4 py-2 text-left font-semibold">Description</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(type).map(([name, prop], index) => (
            <tr
              key={name}
              className={cn(
                'border-b',
                index % 2 === 0 ? 'bg-background' : 'bg-muted/20'
              )}
            >
              {/* Property name */}
              <td className="px-4 py-3 align-top">
                <code className="font-mono text-sm font-semibold">{name}</code>
                {prop.required && (
                  <span className="ml-1 text-red-500 text-xs">*</span>
                )}
              </td>

              {/* Type */}
              <td className="px-4 py-3 align-top">
                <code className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">
                  {prop.type}
                </code>
                {prop.default !== undefined && (
                  <div className="mt-1 text-xs text-muted-foreground">
                    Default:{' '}
                    <code className="font-mono bg-muted px-1 py-0.5 rounded">
                      {typeof prop.default === 'string'
                        ? `"${prop.default}"`
                        : String(prop.default)}
                    </code>
                  </div>
                )}
              </td>

              {/* Description */}
              <td className="px-4 py-3 align-top text-muted-foreground">
                {prop.description}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {Object.values(type).some((prop) => prop.required) && (
        <p className="text-xs text-muted-foreground mt-2">
          <span className="text-red-500">*</span> Required field
        </p>
      )}
    </div>
  );
}
