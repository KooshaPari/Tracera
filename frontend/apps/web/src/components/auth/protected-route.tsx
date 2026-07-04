/**
 * Protected route wrapper component.
 * Redirects to login if user is not authenticated.
 * Uses WorkOS AuthKit for authentication state.
 */

import type { ReactNode } from 'react';

import { useAuth } from '@workos-inc/authkit-react';
import { useEffect } from 'react';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';

interface ProtectedRouteProps {
  children: ReactNode;
  requireAccount?: boolean;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps): ReactNode {
  const { user, isLoading } = useAuth();

  useEffect(() => {
    // Wait for auth check to complete before redirecting
    if (!isLoading && !user) {
      // Not authenticated, redirect to login
      globalThis.location.href = '/auth/login';
    }
  }, [user, isLoading]);

  // Show loading state while checking authentication
  if (isLoading) {
    return <LoadingSpinner fullScreen text='Checking session...' />;
  }

  // If not authenticated, return nothing (will redirect via useEffect)
  if (!user) {
    return;
  }

  return children;
}
