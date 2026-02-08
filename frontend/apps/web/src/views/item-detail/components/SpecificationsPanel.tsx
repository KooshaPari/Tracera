import { ItemSpecTabs } from '@/components/specifications/items/ItemSpecTabs';
import { Card } from '@tracertm/ui';

interface SpecificationsPanelProps {
  itemId: string;
  projectId: string | undefined;
  itemType: string;
  onCreateSpec: (specType: string) => void;
}

export function SpecificationsPanel({
  itemId,
  itemType,
  onCreateSpec,
  projectId,
}: SpecificationsPanelProps): JSX.Element {
  let body: JSX.Element = (
    <p className='border-border/50 bg-background/50 text-muted-foreground rounded-xl border border-dashed py-6 text-center text-xs italic'>
      Specifications are unavailable for this item.
    </p>
  );

  if (projectId !== undefined) {
    body = (
      <ItemSpecTabs
        projectId={projectId}
        itemId={itemId}
        itemType={itemType}
        onCreateSpec={onCreateSpec}
      />
    );
  }

  return <Card className='bg-muted/40 space-y-4 border-0 p-5'>{body}</Card>;
}
