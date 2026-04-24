import { createFileRoute } from '@tanstack/react-router';
import { Loader2 } from 'lucide-react';
import { useEffect } from 'react';
import { toast } from 'sonner';

import { logger } from '@/lib/logger';
import { useAuthStore } from '@/stores/auth-store';

const Login = () => {
  const redirectToAuthKit = useAuthStore((state) => state.redirectToAuthKit);
  const isLoading = useAuthStore((state) => state.isLoading);

  useEffect(() => {
    const redirect = async () => {
      try {
        await redirectToAuthKit();
      } catch (error) {
        logger.error('Failed to redirect to AuthKit:', error);
        toast.error('Failed to start authentication. Please try again.');
      }
    };

    redirect();
  }, [redirectToAuthKit]);

  return (
    <div className='flex min-h-screen items-center justify-center bg-slate-950 p-4'>
      <div className='space-y-6 text-center'>
        <div className='relative mx-auto h-20 w-20'>
          <div className='bg-primary/10 absolute inset-0 animate-pulse rounded-full' />
          <div className='relative flex h-full w-full items-center justify-center'>
            <Loader2 className='text-primary h-10 w-10 animate-spin' />
          </div>
        </div>
        <div className='space-y-2'>
          <h2 className='text-2xl font-bold text-slate-100'>Redirecting to sign in...</h2>
          <p className='text-sm text-slate-400'>
            You will be redirected to our secure authentication page.
          </p>
        </div>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/auth/login')({
  component: Login,
});
