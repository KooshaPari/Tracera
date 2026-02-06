import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { Loader2, LogOut } from 'lucide-react';
import { useEffect, useState } from 'react';

import { logger } from '@/lib/logger';
import { useAuthStore } from '@/stores/auth-store';

const LOGOUT_REDIRECT_DELAY_MS = 500;

const LogoutPage = () => {
  const navigate = useNavigate();
  const logout = useAuthStore((state) => state.logout);
  const [isLoggingOut, setIsLoggingOut] = useState(true);

  useEffect(() => {
    const performLogout = async () => {
      try {
        await logout();
        setTimeout(() => {
          navigate({ to: '/auth/login' });
        }, LOGOUT_REDIRECT_DELAY_MS);
      } catch (error) {
        logger.error('Logout error:', error);
        navigate({ to: '/auth/login' });
      } finally {
        setIsLoggingOut(false);
      }
    };

    performLogout();
  }, [logout, navigate]);

  return (
    <div className='bg-background flex min-h-screen items-center justify-center'>
      <div className='space-y-6 text-center'>
        <div className='relative mx-auto h-20 w-20'>
          <div className='bg-primary/10 absolute inset-0 animate-pulse rounded-full' />
          <div className='relative flex h-full w-full items-center justify-center'>
            {isLoggingOut ? (
              <Loader2 className='text-primary h-10 w-10 animate-spin' />
            ) : (
              <LogOut className='text-primary h-10 w-10' />
            )}
          </div>
        </div>

        <div className='space-y-2'>
          <h2 className='text-2xl font-bold'>
            {isLoggingOut ? 'Signing out...' : 'Signed out successfully'}
          </h2>
          <p className='text-muted-foreground'>
            {isLoggingOut ? 'Clearing your session' : 'Redirecting to login page'}
          </p>
        </div>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/auth/logout')({
  component: LogoutPage,
});
