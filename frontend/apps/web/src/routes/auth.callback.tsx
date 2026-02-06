import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useAuth } from '@workos-inc/authkit-react';
import { AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';

import config from '@/config/constants';
import { getReturnTo } from '@/lib/auth-utils';
import { Button } from '@tracertm/ui';

/**
 * OAuth Callback Route for WorkOS Authentication
 *
 * This route handles the redirect from WorkOS after authentication.
 * It processes the OAuth callback, exchanges the authorization code for tokens,
 * updates the auth store, and redirects the user to their intended destination.
 *
 * Flow:
 * 1. WorkOS redirects here with auth code/state in URL
 * 2. WorkOS AuthKit SDK automatically handles token exchange
 * 3. AuthKitSync component syncs user/token to our auth store
 * 4. This component shows loading state and handles final redirect
 * 5. Redirects to returnTo URL or dashboard
 */

function handleCancel() {
  globalThis.location.href = '/home';
}

interface CallbackState {
  status: 'loading' | 'success' | 'error';
  message: string;
}

function AuthCallback() {
  const navigate = useNavigate();
  const { user, isLoading } = useAuth();
  // 	Const _setAuthFromWorkOS = useAuthStore((state) => state.setAuthFromWorkOS);
  const [state, setState] = useState<CallbackState>({
    message: 'Processing authentication...',
    status: 'loading',
  });

  useEffect(() => {
    // Get the URL search params for returnTo
    const searchParams = new URLSearchParams(globalThis.location.search);
    const error = searchParams.get('error');
    const errorDescription = searchParams.get('error_description');

    // Handle OAuth errors from WorkOS
    if (error) {
      setState({
        message: errorDescription || 'Authentication failed. Please try again.',
        status: 'error',
      });
      return;
    }

    // WorkOS SDK handles the OAuth callback automatically
    // Wait for the SDK to complete authentication
    if (isLoading) {
      setState({
        message: 'Verifying credentials...',
        status: 'loading',
      });
      return;
    }

    // Check if authentication was successful
    if (!user) {
      // If no user after loading completes, something went wrong
      setState({
        message: 'Authentication failed. No user information received.',
        status: 'error',
      });
      return;
    }

    // Success! User is authenticated
    setState({
      message: 'Authentication successful! Redirecting...',
      status: 'success',
    });

    // Redirect to intended destination
    // AuthKitSync will handle the actual token sync
    const returnTo = getReturnTo(searchParams);

    // Use a small delay to show success state
    const redirectTimeout = setTimeout(() => {
      globalThis.location.href = returnTo;
    }, 500);

    return () => clearTimeout(redirectTimeout);
  }, [user, isLoading, navigate]);

  // Handle manual retry for error state
  const handleRetry = () => {
    setState({
      message: 'Retrying authentication...',
      status: 'loading',
    });

    // Clear any stale state and redirect to login
    setTimeout(() => {
      globalThis.location.href = config.AUTH_ROUTES.LOGIN;
    }, 500);
  };

  return (
    <div className='bg-background flex min-h-screen items-center justify-center p-4'>
      <div className='bg-card animate-in fade-in zoom-in-95 w-full max-w-md space-y-6 rounded-2xl border p-8 shadow-xl duration-300'>
        {/* Status Icon */}
        <div className='flex items-center justify-center'>
          {state.status === 'loading' && (
            <div className='bg-primary/10 flex h-16 w-16 items-center justify-center rounded-full'>
              <Loader2 className='text-primary h-8 w-8 animate-spin' />
            </div>
          )}
          {state.status === 'success' && (
            <div className='animate-in zoom-in flex h-16 w-16 items-center justify-center rounded-full bg-green-500/10 duration-300'>
              <CheckCircle className='h-8 w-8 text-green-500' />
            </div>
          )}
          {state.status === 'error' && (
            <div className='bg-destructive/10 animate-in zoom-in flex h-16 w-16 items-center justify-center rounded-full duration-300'>
              <AlertCircle className='text-destructive h-8 w-8' />
            </div>
          )}
        </div>

        {/* Status Message */}
        <div className='space-y-2 text-center'>
          <h1 className='text-2xl font-bold'>
            {state.status === 'loading' && 'Authenticating'}
            {state.status === 'success' && 'Welcome Back'}
            {state.status === 'error' && 'Authentication Error'}
          </h1>
          <p className='text-muted-foreground'>{state.message}</p>
        </div>

        {/* Error State Actions */}
        {state.status === 'error' && (
          <div className='flex flex-col gap-3'>
            <Button onClick={handleRetry} className='w-full'>
              Try Again
            </Button>
            <Button variant='outline' onClick={handleCancel} className='w-full'>
              Cancel
            </Button>
          </div>
        )}

        {/* Loading Indicator */}
        {state.status === 'loading' && (
          <div className='space-y-2'>
            <div className='bg-muted h-1.5 w-full overflow-hidden rounded-full'>
              <div className='bg-primary animate-pulse-slow h-full rounded-full' />
            </div>
            <p className='text-muted-foreground text-center text-xs'>
              This may take a few moments...
            </p>
          </div>
        )}

        {/* Success State - auto-redirecting */}
        {state.status === 'success' && (
          <div className='text-muted-foreground text-center text-sm'>Redirecting you now...</div>
        )}
      </div>
    </div>
  );
}

// TanStack Router file-based route export
export const Route = createFileRoute('/auth/callback')({
  component: AuthCallback,
  // This is a public route - no auth required
  beforeLoad: () => {
    // No-op - allow access without authentication
  },
});
