import { Card } from '@tracertm/ui';

interface VersionPerspectiveCardProps {
  version: number;
  perspective: string | null | undefined;
}

export function VersionPerspectiveCard({
  perspective,
  version,
}: VersionPerspectiveCardProps): JSX.Element {
  const safePerspective = perspective ?? 'default';
  return (
    <Card className='bg-muted/40 border-0 px-4 py-3'>
      <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
        Version & Perspective
      </p>
      <div className='mt-2 flex items-center justify-between text-xs font-bold'>
        <span>v{String(version)}</span>
        <span className='text-muted-foreground'>{safePerspective}</span>
      </div>
    </Card>
  );
}
