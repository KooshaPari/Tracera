import { memo } from 'react';

import { Badge } from '@tracertm/ui/components/Badge';
import { Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui/components/Card';

interface NodeHoverTooltipProps {
  nodeId: string;
  nodeType: string;
  label: string;
  status?: string;
  metadata?: Record<string, unknown>;
  position: { x: number; y: number };
}

export const NodeHoverTooltip = memo(function NodeHoverTooltip({
  label,
  nodeType,
  status,
  metadata,
  position,
}: NodeHoverTooltipProps) {
  return (
    <div
      className='pointer-events-none fixed z-50'
      style={{
        left: position.x + 10,
        top: position.y + 10,
      }}
    >
      <Card className='w-64 shadow-lg'>
        <CardHeader className='pb-3'>
          <div className='flex items-center justify-between'>
            <CardTitle className='text-sm font-medium'>{label}</CardTitle>
            {status && (
              <Badge variant='outline' className='text-xs'>
                {status}
              </Badge>
            )}
          </div>
          <p className='text-muted-foreground text-xs'>{nodeType}</p>
        </CardHeader>
        {metadata && Object.keys(metadata).length > 0 && (
          <CardContent className='pt-0'>
            <dl className='space-y-1'>
              {Object.entries(metadata)
                .slice(0, 3)
                .map(([key, value]) => (
                  <div key={key} className='flex justify-between text-xs'>
                    <dt className='text-muted-foreground'>{key}:</dt>
                    <dd className='font-medium'>{String(value)}</dd>
                  </div>
                ))}
            </dl>
          </CardContent>
        )}
      </Card>
    </div>
  );
});
