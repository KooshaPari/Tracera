import { Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui';

import type { TypeDistributionRow } from './SpecificationsDashboardView.data';

export interface SpecificationsDashboardTypeDistributionCardProps {
  totalItems: number;
  typeDistribution: TypeDistributionRow[];
}

function widthStyle(percent: number): React.CSSProperties {
  return { width: `${percent}%` };
}

export function SpecificationsDashboardTypeDistributionCard({
  totalItems,
  typeDistribution,
}: SpecificationsDashboardTypeDistributionCardProps): JSX.Element {
  if (typeDistribution.length === 0) {
    return (
      <Card className='bg-card/50 border-none'>
        <CardHeader className='pb-3'>
          <CardTitle className='text-sm'>Item Type Mix</CardTitle>
        </CardHeader>
        <CardContent>
          <div className='text-muted-foreground text-sm'>
            No items yet. Create a requirement, task, or story to start populating distribution.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className='bg-card/50 border-none'>
      <CardHeader className='pb-3'>
        <CardTitle className='text-sm'>Item Type Mix</CardTitle>
      </CardHeader>
      <CardContent>
        <div className='space-y-3'>
          {typeDistribution.map((row) => {
            let percent = 0;
            if (totalItems > 0) {
              percent = Math.round((row.count / totalItems) * Number('100'));
            }
            return (
              <div key={row.type} className='space-y-1'>
                <div className='flex items-center justify-between text-xs'>
                  <span className='text-muted-foreground tracking-wide uppercase'>{row.type}</span>
                  <span className='font-semibold'>
                    {row.count} ({percent}%)
                  </span>
                </div>
                <div className='bg-muted/40 h-2 w-full overflow-hidden rounded-full'>
                  <div className='bg-primary/70 h-full' style={widthStyle(percent)} />
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
