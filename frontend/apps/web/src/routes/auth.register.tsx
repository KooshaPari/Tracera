import { createFileRoute, Link, useNavigate } from '@tanstack/react-router';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

import { logger } from '@/lib/logger';
import { useAuthStore } from '@/stores/auth-store';
import { Button, Input } from '@tracertm/ui';

const Register = () => {
  const navigate = useNavigate();
  // Note: auth-store doesn't expose a direct 'register' action,
  // but we can call the API directly or add it to the store.
  // The backend has /api/v1/auth/register.
  // For now, I'll fetch directly here or assume we should add 'register' to store.
  // Given I modified auth-store.ts, let's check if it has register.
  // It does NOT have register.
  // I should probably add it to auth-store.ts or just handle it here.
  // Handling here is fine for now, but cleaner in store.
  // I will handle it here using fetch to match the store pattern.

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Use store setter to update state after successful registration
  const setUser = useAuthStore((state) => state.setUser);
  const setToken = useAuthStore((state) => state.setToken);
  const initializeAutoRefresh = useAuthStore((state) => state.initializeAutoRefresh);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Registration failed');
      }

      // Assume response structure matches login: { user, token }
      if (data.user && data.token) {
        setUser(data.user);
        setToken(data.token);
        initializeAutoRefresh();
        toast.success('Account created successfully!');
        navigate({ to: '/home' });
      } else {
        // Maybe just success message and redirect to login?
        // Backend code returns { user, token }, so we should be logged in.
        toast.success('Registration successful. Please log in.');
        navigate({ to: '/auth/login' });
      }
    } catch (error: any) {
      logger.error('Registration failed', error);
      toast.error(error.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='flex min-h-screen items-center justify-center bg-slate-950 p-4'>
      <div className='w-full max-w-md space-y-8 rounded-2xl border border-slate-800 bg-slate-900/50 p-8 shadow-xl backdrop-blur-sm'>
        <div className='text-center'>
          <h1 className='text-3xl font-bold tracking-tight text-slate-100'>Create an account</h1>
          <p className='mt-2 text-sm text-slate-400'>Get started with TraceRTM today</p>
        </div>

        <form onSubmit={handleSubmit} className='mt-8 space-y-6'>
          <div className='space-y-4'>
            <div>
              <label htmlFor='name' className='block text-sm font-medium text-slate-300'>
                Full Name
              </label>
              <Input
                id='name'
                type='text'
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className='mt-1 block w-full bg-slate-800/50 text-slate-100 placeholder-slate-500'
                placeholder='John Doe'
              />
            </div>

            <div>
              <label htmlFor='email' className='block text-sm font-medium text-slate-300'>
                Email address
              </label>
              <Input
                id='email'
                type='email'
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className='mt-1 block w-full bg-slate-800/50 text-slate-100 placeholder-slate-500'
                placeholder='name@example.com'
              />
            </div>

            <div>
              <label htmlFor='password' className='block text-sm font-medium text-slate-300'>
                Password
              </label>
              <div className='relative mt-1'>
                <Input
                  id='password'
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className='block w-full bg-slate-800/50 pr-10 text-slate-100 placeholder-slate-500'
                  placeholder='••••••••'
                  minLength={8}
                />
                <button
                  type='button'
                  onClick={() => setShowPassword(!showPassword)}
                  className='absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-200'
                >
                  {showPassword ? <EyeOff className='h-4 w-4' /> : <Eye className='h-4 w-4' />}
                </button>
              </div>
            </div>

            <div>
              <label htmlFor='confirmPassword' className='block text-sm font-medium text-slate-300'>
                Confirm Password
              </label>
              <Input
                id='confirmPassword'
                type='password'
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className='mt-1 block w-full bg-slate-800/50 text-slate-100 placeholder-slate-500'
                placeholder='••••••••'
              />
            </div>
          </div>

          <Button
            type='submit'
            disabled={isLoading}
            className='bg-primary hover:bg-primary/90 text-primary-foreground w-full'
          >
            {isLoading ? (
              <>
                <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                Creating account...
              </>
            ) : (
              'Create account'
            )}
          </Button>

          <div className='text-center text-sm'>
            <span className='text-slate-400'>Already have an account? </span>
            <Link
              to='/auth/login'
              className='text-primary hover:text-primary/80 font-medium hover:underline'
            >
              Sign in
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/auth/register')({
  component: Register,
});
