import { createFileRoute, Link, useNavigate } from '@tanstack/react-router';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

import { useAuthStore } from '@/stores/auth-store';
import { Button, Input } from '@tracertm/ui';

const Login = () => {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const isLoading = useAuthStore((state) => state.isLoading);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate({ to: '/home' });
    } catch (error) {
      toast.error('Invalid credentials');
    }
  };

  return (
    <div className='flex min-h-screen items-center justify-center bg-slate-950 p-4'>
      <div className='w-full max-w-md space-y-8 rounded-2xl border border-slate-800 bg-slate-900/50 p-8 shadow-xl backdrop-blur-sm'>
        <div className='text-center'>
          <h1 className='text-3xl font-bold tracking-tight text-slate-100'>Sign in</h1>
          <p className='mt-2 text-sm text-slate-400'>
            Enter your credentials to access your account
          </p>
        </div>

        <form onSubmit={handleSubmit} className='mt-8 space-y-6'>
          <div className='space-y-4'>
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
          </div>

          <Button
            type='submit'
            disabled={isLoading}
            className='bg-primary hover:bg-primary/90 text-primary-foreground w-full'
          >
            {isLoading ? (
              <>
                <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                Signing in...
              </>
            ) : (
              'Sign in'
            )}
          </Button>

          <div className='text-center text-sm'>
            <span className='text-slate-400'>Don't have an account? </span>
            <Link
              to='/auth/register'
              className='text-primary hover:text-primary/80 font-medium hover:underline'
            >
              Sign up
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/auth/login')({
  component: Login,
});
