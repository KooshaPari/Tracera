import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';

import { logger } from '@/lib/logger';
import { useAuthStore } from '@/stores/auth-store';

const AuthCallback = () => {
  const navigate = useNavigate();
  const loginWithCode = useAuthStore((state) => state.loginWithCode);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const state = params.get('state');

        if (!code) {
          const errorDesc =
            params.get('error_description') ??
            params.get('error') ??
            'No authorization code received';
          throw new Error(errorDesc);
        }

        if (!state) {
          throw new Error('No state parameter received');
        }

        await loginWithCode(code, state);
        toast.success('Welcome back!');
        navigate({ to: '/home', replace: true });
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Authentication failed';
        logger.error('AuthKit callback failed:', err);
        setError(message);
        toast.error(message);
        setTimeout(() => {
          navigate({ to: '/auth/login', replace: true });
        }, 2000);
      }
    };

    handleCallback();
  }, [loginWithCode, navigate]);

  if (error) {
    return (
      <div className='flex min-h-screen items-center justify-center bg-slate-950 p-4'>
        <div className='space-y-6 text-center'>
          <div className='space-y-2'>
            <h2 className='text-2xl font-bold text-red-400'>Authentication failed</h2>
            <p className='text-sm text-slate-400'>{error}</p>
            <p className='text-sm text-slate-500'>Redirecting to login...</p>
          </div>
        </div>
      </div>
    );
  }

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
          <h2 className='text-2xl font-bold text-slate-100'>Completing sign in...</h2>
          <p className='text-sm text-slate-400'>Please wait while we verify your credentials.</p>
        </div>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/auth/callback')({
  component: AuthCallback,
});
