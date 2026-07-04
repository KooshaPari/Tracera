import { createFileRoute, useParams } from '@tanstack/react-router';

import { FullScreenPage } from '@/components/layout/FullScreenPage';
import { useItem } from '@/hooks/useItems';
import { requireAuth } from '@/lib/route-guards';
import ItemDetailRouter from '@/views/details/ItemDetailRouter';

function ItemDetailComponent() {
  const { projectId, itemId } = useParams({ strict: false });
  const projectIdValue = projectId ?? '';
  const itemIdValue = itemId ?? '';
  const { data: item, isLoading, error } = useItem(itemIdValue);

  if (isLoading) {
    return (
      <div className='bg-background flex min-h-screen items-center justify-center'>
        <div className='border-primary h-8 w-8 animate-spin rounded-full border-4 border-t-transparent' />
      </div>
    );
  }

  if (error || !item) {
    return (
      <FullScreenPage>
        <div className='bg-background text-foreground flex min-h-screen flex-col items-center justify-center'>
          <h1 className='text-destructive mb-4 text-2xl font-bold'>Item Not Found</h1>
          <p className='text-muted-foreground'>The item you're looking for doesn't exist.</p>
        </div>
      </FullScreenPage>
    );
  }

  return <ItemDetailRouter item={item} projectId={projectIdValue} />;
}

export const Route = createFileRoute('/projects/$projectId/views/$viewType/$itemId' as any)({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: ItemDetailComponent,
  errorComponent: () => (
    <FullScreenPage>
      <div className='bg-background text-foreground flex min-h-screen flex-col items-center justify-center'>
        <h1 className='text-destructive mb-4 text-2xl font-bold'>Item Not Found</h1>
        <p className='text-muted-foreground'>The item you're looking for doesn't exist.</p>
      </div>
    </FullScreenPage>
  ),
  loader: async () => ({}),
});
