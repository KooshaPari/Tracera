import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useEffect } from 'react';

/**
 * Redirect handler for old search URL (/search)
 * Redirects to projects page where users can use the command palette (Cmd+K)
 * for global search
 */
function SearchRedirectComponent() {
  const navigate = useNavigate();

  useEffect(() => {}, [navigate]);

  return (
    <div className='bg-background flex min-h-screen flex-col items-center justify-center'>
      <div className='border-primary h-8 w-8 animate-spin rounded-full border-4 border-t-transparent' />
      <p className='text-muted-foreground mt-4 text-sm'>Redirecting to projects...</p>
      <p className='text-muted-foreground mt-2 text-xs'>
        Use Cmd+K or Ctrl+K to open global search
      </p>
    </div>
  );
}

export const Route = createFileRoute('/search')({
  component: SearchRedirectComponent,
});
