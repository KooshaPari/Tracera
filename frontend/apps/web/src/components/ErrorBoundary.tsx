import type { ReactNode } from 'react';

import { AlertCircle, Bug, RefreshCw } from 'lucide-react';
import React from 'react';

import { logger } from '@/lib/logger';
import { captureException as sentryCaptureException } from '@/lib/sentry';
import { Alert, AlertDescription, AlertTitle } from '@tracertm/ui/components/Alert';
import { Button } from '@tracertm/ui/components/Button';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactNode;
  /**
   * Name to identify this error boundary in logs/Sentry
   * @example "GraphView", "FormDialog", "RouteComponent"
   */
  name?: string;
  /**
   * Show error details in production (default: false)
   */
  showDetails?: boolean;
  /**
   * Callback when error is caught
   */
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

/**
 * ErrorBoundary Component
 *
 * Catches React errors in child components and displays a fallback UI.
 * Integrates with Sentry if available for error tracking.
 *
 * @example
 * ```tsx
 * <ErrorBoundary name="GraphView">
 *   <GraphViewContainer />
 * </ErrorBoundary>
 * ```
 *
 * @example Custom fallback
 * ```tsx
 * <ErrorBoundary
 *   name="FormDialog"
 *   fallback={(error, reset) => (
 *     <div>
 *       <p>Form error: {error.message}</p>
 *       <button onClick={reset}>Try again</button>
 *     </div>
 *   )}
 * >
 *   <CreateItemForm />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { error: null, errorInfo: null, hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error, errorInfo: null, hasError: true };
  }

  override componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    const { name, onError } = this.props;

    logger.error(`Error caught by ${name ?? 'ErrorBoundary'}:`, error, errorInfo);

    this.setState({ errorInfo });

    try {
      sentryCaptureException(error, {
        react: {
          componentStack: errorInfo.componentStack,
          errorBoundary: name ?? 'UnnamedBoundary',
        },
      });
    } catch (sentryError) {
      logger.warn('Failed to report error to Sentry:', sentryError);
    }

    if (onError) {
      try {
        onError(error, errorInfo);
      } catch (callbackError) {
        logger.error('Error in onError callback:', callbackError);
      }
    }
  }

  reset = () => {
    this.setState({ error: null, errorInfo: null, hasError: false });
  };

  override render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.reset);
      }

      const isDevelopment = import.meta.env.DEV;
      const showDetails = isDevelopment || this.props.showDetails;

      return (
        <Alert variant='destructive' className='m-4'>
          <AlertCircle className='h-4 w-4' />
          <AlertTitle className='flex items-center gap-2'>
            Something went wrong
            {this.props.name && (
              <span className='bg-destructive/10 rounded px-2 py-1 font-mono text-xs'>
                {this.props.name}
              </span>
            )}
          </AlertTitle>
          <AlertDescription className='mt-2 space-y-3'>
            <p className='text-sm'>{this.state.error.message}</p>

            {showDetails && this.state.errorInfo?.componentStack && (
              <details className='text-xs'>
                <summary className='hover:text-destructive-foreground flex cursor-pointer items-center gap-1 font-medium'>
                  <Bug className='h-3 w-3' />
                  Component Stack
                </summary>
                <pre className='bg-muted/50 mt-2 max-h-32 overflow-x-auto rounded p-2 text-xs'>
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            {showDetails && this.state.error.stack && (
              <details className='text-xs'>
                <summary className='hover:text-destructive-foreground flex cursor-pointer items-center gap-1 font-medium'>
                  <Bug className='h-3 w-3' />
                  Error Stack
                </summary>
                <pre className='bg-muted/50 mt-2 max-h-32 overflow-x-auto rounded p-2 text-xs'>
                  {this.state.error.stack}
                </pre>
              </details>
            )}

            <div className='flex gap-2 pt-2'>
              <Button variant='outline' size='sm' onClick={this.reset} className='gap-1'>
                <RefreshCw className='h-3 w-3' />
                Try again
              </Button>

              <Button
                variant='ghost'
                size='sm'
                onClick={() => {
                  globalThis.location.reload();
                }}
                className='gap-1'
              >
                Reload page
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      );
    }

    return this.props.children;
  }
}

/**
 * Higher-order component to wrap any component with an error boundary
 *
 * @example
 * ```tsx
 * const SafeGraphView = withErrorBoundary(GraphView, { name: "GraphView" });
 * ```
 */
export const withErrorBoundary = <Props extends object>(
  Component: React.ComponentType<Props>,
  options?: Omit<ErrorBoundaryProps, 'children'>,
) => {
  const WrappedComponent = (props: Props) => (
    <ErrorBoundary {...options}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${(Component.displayName ?? Component.name) || 'Component'})`;

  return WrappedComponent;
};
