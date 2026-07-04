import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useEffect } from 'react';

/**
 * Redirect handler for old graph URL (/graph)
 * Redirects to projects page where users can select a project to view its graph
 */
function GraphRedirectComponent() {
  const navigate = useNavigate();

  useEffect(() => {}, [navigate]);

  return (
    <div className='bg-background flex min-h-screen flex-col items-center justify-center'>
      <div className='border-primary h-8 w-8 animate-spin rounded-full border-4 border-t-transparent' />
      <p className='text-muted-foreground mt-4 text-sm'>Redirecting to projects...</p>
      <p className='text-muted-foreground mt-2 text-xs'>
        Please select a project to view its graph
      </p>
    </div>
  );
}

export const Route = createFileRoute('/graph')({
  component: GraphRedirectComponent,
});
