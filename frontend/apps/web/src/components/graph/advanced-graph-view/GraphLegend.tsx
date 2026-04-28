import type { EnhancedNodeData } from '@/components/graph/types';

import { ENHANCED_TYPE_COLORS, LINK_STYLES } from '@/components/graph/types';
import { Card } from '@tracertm/ui/components/Card';
import { Separator } from '@tracertm/ui/components/Separator';

interface GraphLegendProps {
  filteredNodes: EnhancedNodeData[];
}

export function GraphLegend({ filteredNodes }: GraphLegendProps): JSX.Element {
  return (
    <Card className='p-3'>
      <div className='flex flex-wrap items-center gap-4 text-xs'>
        <span className='text-muted-foreground font-medium'>Types:</span>
        {Object.entries(ENHANCED_TYPE_COLORS)
          .filter(([type]) => filteredNodes.some((n) => n.type === type))
          .slice(0, 10)
          .map(([type, color]) => (
            <div key={type} className='flex items-center gap-1.5'>
              <div className='h-3 w-6 rounded' style={{ backgroundColor: color }} />
              <span className='capitalize'>{type.replaceAll('_', ' ')}</span>
            </div>
          ))}

        <Separator orientation='vertical' className='h-4' />

        <span className='text-muted-foreground font-medium'>Links:</span>
        {Object.entries(LINK_STYLES)
          .slice(0, 5)
          .map(([type, style]) => (
            <div key={type} className='flex items-center gap-1.5'>
              <div
                className='h-0.5 w-6'
                style={{
                  backgroundColor: style.color,
                  borderStyle: style.dashed ? 'dashed' : 'solid',
                }}
              />
              <span>{type.replaceAll('_', ' ')}</span>
            </div>
          ))}
      </div>
    </Card>
  );
}
