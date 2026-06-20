import { createFileRoute, useParams, useNavigate } from '@tanstack/react-router';
import { useEffect } from 'react';

import { useItem } from '@/hooks/useItems';
import { requireAuth } from '@/lib/route-guards';

/**
 * Redirect handler for old item URLs (/items/:itemId)
 * Maintains backward compatibility by redirecting to new format:
 * /projects/:projectId/views/:viewType/:itemId
 */
const ItemRedirectComponent = () => {
  const { itemId = '' } = useParams({ from: '/items/$itemId' });
  const navigate = useNavigate();
  const { data: item, error, isLoading } = useItem(itemId);

  useEffect(() => {
    if (item) {
      // Redirect to new URL format
      navigate({ to: `/projects/${item.projectId}/views/items/${item.id}` });
    }
  }, [item, navigate]);

  if (isLoading) {
    return (
      <div className='bg-background flex min-h-screen flex-col items-center justify-center'>
        <div className='border-primary h-8 w-8 animate-spin rounded-full border-4 border-t-transparent' />
        <p className='text-muted-foreground mt-4 text-sm'>Redirecting...</p>
      </div>
    );
  }

  if (error || !item) {
    return (
      <div className='bg-background text-foreground flex min-h-screen flex-col items-center justify-center'>
        <h1 className='text-destructive mb-4 text-2xl font-bold'>Item Not Found</h1>
        <p className='text-muted-foreground mb-6'>
          The item you're looking for doesn't exist or has been deleted.
        </p>
        <a
          href='/projects'
          className='bg-primary text-primary-foreground hover:bg-primary/90 rounded-md px-4 py-2 transition-colors'
        >
          Back to Projects
        </a>
      </div>
    );
  }

  // Show nothing while redirecting
  return null;
};

export const Route = createFileRoute('/items/$itemId')({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: ItemRedirectComponent,
});
