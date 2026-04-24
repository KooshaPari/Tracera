import { Card } from '@tracertm/ui';

const EM_DASH = '—';
const SHORT_ID_PREFIX = 8;

interface CanonicalParentCardProps {
  canonicalId: string | null | undefined;
  parentId: string | null | undefined;
}

function formatParent(parentId: string | null | undefined): string {
  if (parentId === null || parentId === undefined) {
    return 'Root';
  }
  const trimmed = parentId.trim();
  if (trimmed.length === 0) {
    return 'Root';
  }
  return trimmed.slice(0, SHORT_ID_PREFIX);
}

export function CanonicalParentCard({
  canonicalId,
  parentId,
}: CanonicalParentCardProps): JSX.Element {
  const safeCanonical = canonicalId ?? EM_DASH;
  const parentLabel = formatParent(parentId);

  return (
    <Card className='bg-muted/40 border-0 px-4 py-3'>
      <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
        Canonical & Parent
      </p>
      <div className='mt-2 flex items-center justify-between text-xs font-bold'>
        <span className='truncate'>{safeCanonical}</span>
        <span className='text-muted-foreground'>{parentLabel}</span>
      </div>
    </Card>
  );
}
