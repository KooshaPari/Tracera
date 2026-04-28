import type { ReactNode } from 'react';

import { AlertTriangle, RefreshCcw, RotateCw } from 'lucide-react';
import { Component } from 'react';

import { logger } from '@/lib/logger';
import { Button } from '@tracertm/ui';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { error: null, hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error, hasError: true };
  }

  override componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    logger.error('ErrorBoundary caught error:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  reset = () => {
    this.setState({ error: null, hasError: false });
  };

  reloadPage = () => {
    globalThis.location.reload();
  };

  override render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.reset);
      }

      return (
        <div className='animate-in fade-in zoom-in-95 flex items-center justify-center p-6 duration-300'>
          <div className='bg-card border-destructive/20 w-full max-w-md space-y-6 rounded-2xl border p-8 shadow-2xl'>
            <div className='flex flex-col items-center space-y-4 text-center'>
              <div className='bg-destructive/10 text-destructive flex h-16 w-16 items-center justify-center rounded-full'>
                <AlertTriangle className='h-8 w-8' />
              </div>

              <div className='space-y-1'>
                <h2 className='text-xl font-bold tracking-tight'>Component Failure</h2>
                <p className='text-muted-foreground text-sm'>
                  A sub-system encountered an unrecoverable state.
                </p>
              </div>
            </div>

            <div className='bg-muted/30 border-border/50 max-h-40 overflow-auto rounded-xl border p-4 font-mono text-xs'>
              <p className='text-destructive mb-1 font-bold'>EXCEPTION:</p>
              <p className='text-muted-foreground break-all'>
                {this.state.error.message || 'An unexpected error occurred'}
              </p>
            </div>

            <div className='flex gap-3'>
              <Button onClick={this.reset} className='flex-1 gap-2' size='sm'>
                <RefreshCcw className='h-3.5 w-3.5' />
                Try Reset
              </Button>
              <Button
                onClick={this.reloadPage}
                variant='outline'
                className='flex-1 gap-2'
                size='sm'
              >
                <RotateCw className='h-3.5 w-3.5' />
                Hard Reload
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
