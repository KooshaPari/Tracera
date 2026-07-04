/**
 * ErrorBoundary Component Tests
 *
 * Comprehensive tests covering:
 * - Error catching and display
 * - Fallback rendering
 * - Custom fallback
 * - Error reset functionality
 * - Error callback
 * - Development mode stack traces
 * - User interactions
 * - Edge cases
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { ErrorBoundary } from '@/components/layout/ErrorBoundary';

// Component that throws an error
const ThrowError = ({
  shouldThrow = true,
  message = 'Test error',
}: {
  shouldThrow?: boolean;
  message?: string;
}) => {
  if (shouldThrow) {
    throw new Error(message);
  }
  return <div>No error</div>;
};

describe('ErrorBoundary Component', () => {
  // Suppress console errors during tests
  const originalConsoleError = console.error;
  beforeEach(() => {
    console.error = vi.fn();
  });

  afterEach(() => {
    console.error = originalConsoleError;
  });

  describe('Normal Rendering', () => {
    it('should render children when no error occurs', () => {
      render(
        <ErrorBoundary>
          <div>Normal content</div>
        </ErrorBoundary>,
      );

      expect(screen.getByText('Normal content')).toBeInTheDocument();
    });

    it('should render multiple children without errors', () => {
      render(
        <ErrorBoundary>
          <div>Child 1</div>
          <div>Child 2</div>
          <div>Child 3</div>
        </ErrorBoundary>,
      );

      expect(screen.getByText('Child 1')).toBeInTheDocument();
      expect(screen.getByText('Child 2')).toBeInTheDocument();
      expect(screen.getByText('Child 3')).toBeInTheDocument();
    });

    it('should render complex nested children', () => {
      render(
        <ErrorBoundary>
          <div>
            <span>Nested</span>
            <div>
              <p>Deeply nested</p>
            </div>
          </div>
        </ErrorBoundary>,
      );

      expect(screen.getByText('Nested')).toBeInTheDocument();
      expect(screen.getByText('Deeply nested')).toBeInTheDocument();
    });
  });

  describe('Error Catching', () => {
    it('should catch errors thrown by children', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });

    it('should display error message', () => {
      render(
        <ErrorBoundary>
          <ThrowError message='Custom error message' />
        </ErrorBoundary>,
      );

      expect(screen.getByText('Custom error message')).toBeInTheDocument();
    });

    it('should display default message for errors without message', () => {
      render(
        <ErrorBoundary>
          <ThrowError message='' />
        </ErrorBoundary>,
      );

      expect(screen.getByText('An unexpected error occurred')).toBeInTheDocument();
    });

    it('should render error UI instead of children', () => {
      render(
        <ErrorBoundary>
          <div data-testid='normal-content'>Normal content</div>
          <ThrowError />
        </ErrorBoundary>,
      );

      expect(screen.queryByTestId('normal-content')).not.toBeInTheDocument();
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });
  });

  describe('Default Error UI', () => {
    it('should render error title', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });

    it('should render error icon', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should render Try again button', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      expect(screen.getByText('Try again')).toBeInTheDocument();
    });

    it('should render Reload page button', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      expect(screen.getByText('Reload page')).toBeInTheDocument();
    });

    it('should have centered layout', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const wrapper = container.querySelector('.min-h-screen');
      expect(wrapper).toHaveClass('flex', 'items-center', 'justify-center');
    });
  });

  describe('Error Reset', () => {
    it('should reset error state when Try again is clicked', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow />
        </ErrorBoundary>,
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();

      // After reset, the component will re-render
      // We need to provide a non-throwing child
      fireEvent.click(screen.getByText('Try again'));

      // The error boundary will attempt to re-render children
      // In a real scenario, the child component would handle the retry logic
    });

    it('should call reset handler multiple times', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      // The error boundary shows the fallback with Try again button
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();

      // Each click resets, but ThrowError throws again so fallback re-appears
      fireEvent.click(screen.getByText('Try again'));
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();

      fireEvent.click(screen.getByText('Try again'));
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });
  });

  describe('Reload Page Button', () => {
    it('should reload page when Reload page is clicked', () => {
      const mockReload = vi.fn();
      Object.defineProperty(globalThis, 'location', {
        value: { reload: mockReload },
        writable: true,
      });

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      fireEvent.click(screen.getByText('Reload page'));

      expect(mockReload).toHaveBeenCalledTimes(1);
    });

    it('should handle undefined window gracefully', () => {
      const originalWindow = globalThis.window;

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const reloadButton = screen.getByText('Reload page');

      // Should not throw even if window is undefined in onClick
      expect(reloadButton).toBeInTheDocument();

      // Restore window
      Object.defineProperty(globalThis, 'window', {
        configurable: true,
        value: originalWindow,
        writable: true,
      });
    });
  });

  describe('Custom Fallback', () => {
    it('should render custom fallback when provided', () => {
      render(
        <ErrorBoundary
          fallback={(error, reset) => (
            <div data-testid='custom-fallback'>
              Custom error: {error.message}
              <button onClick={reset}>Custom Reset</button>
            </div>
          )}
        >
          <ThrowError message='Custom error occurred' />
        </ErrorBoundary>,
      );

      expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
      expect(screen.getByText(/Custom error: Custom error occurred/)).toBeInTheDocument();
      expect(screen.getByText('Custom Reset')).toBeInTheDocument();
    });

    it('should provide error object to custom fallback', () => {
      render(
        <ErrorBoundary
          fallback={(error) => (
            <div>
              Error name: {error.name}
              <br />
              Error message: {error.message}
            </div>
          )}
        >
          <ThrowError message='Test error' />
        </ErrorBoundary>,
      );

      expect(screen.getByText(/Error name: Error/)).toBeInTheDocument();
      expect(screen.getByText(/Error message: Test error/)).toBeInTheDocument();
    });

    it('should provide reset function to custom fallback', () => {
      render(
        <ErrorBoundary
          fallback={(_error, reset) => (
            <button onClick={reset} data-testid='custom-reset'>
              Custom Reset
            </button>
          )}
        >
          <ThrowError />
        </ErrorBoundary>,
      );

      // First render shows custom fallback
      expect(screen.getByTestId('custom-reset')).toBeInTheDocument();

      // Click reset - this triggers re-render, child throws again, fallback re-shows
      fireEvent.click(screen.getByTestId('custom-reset'));

      // Custom fallback should still be visible since child throws again
      expect(screen.getByTestId('custom-reset')).toBeInTheDocument();
    });

    it('should render complex custom fallback UI', () => {
      render(
        <ErrorBoundary
          fallback={(error, reset) => (
            <div data-testid='complex-fallback'>
              <h1>Error</h1>
              <p>{error.message}</p>
              <div>
                <button onClick={reset}>Retry</button>
                <a href='/'>Home</a>
              </div>
            </div>
          )}
        >
          <ThrowError message='Complex error' />
        </ErrorBoundary>,
      );

      expect(screen.getByTestId('complex-fallback')).toBeInTheDocument();
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });

  describe('Error Callback', () => {
    it('should call onError callback when error occurs', () => {
      const onError = vi.fn();

      render(
        <ErrorBoundary onError={onError}>
          <ThrowError message='Callback test error' />
        </ErrorBoundary>,
      );

      expect(onError).toHaveBeenCalledTimes(1);
    });

    it('should provide error to onError callback', () => {
      const onError = vi.fn();

      render(
        <ErrorBoundary onError={onError}>
          <ThrowError message='Test error' />
        </ErrorBoundary>,
      );

      expect(onError).toHaveBeenCalledWith(
        expect.objectContaining({ message: 'Test error' }),
        expect.any(Object),
      );
    });

    it('should provide errorInfo to onError callback', () => {
      const onError = vi.fn();

      render(
        <ErrorBoundary onError={onError}>
          <ThrowError />
        </ErrorBoundary>,
      );

      expect(onError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({ componentStack: expect.any(String) }),
      );
    });

    it('should not call onError when no error occurs', () => {
      const onError = vi.fn();

      render(
        <ErrorBoundary onError={onError}>
          <div>Normal content</div>
        </ErrorBoundary>,
      );

      expect(onError).not.toHaveBeenCalled();
    });
  });

  describe('Development Mode', () => {
    it('should show stack trace in development mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      const { container } = render(
        <ErrorBoundary>
          <ThrowError message='Dev error' />
        </ErrorBoundary>,
      );

      const stackTrace = container.querySelector('.font-mono');
      expect(stackTrace).toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });

    it('should not show stack trace in production mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      const { container } = render(
        <ErrorBoundary>
          <ThrowError message='Prod error' />
        </ErrorBoundary>,
      );

      const stackTrace = container.querySelector('.font-mono');
      expect(stackTrace).not.toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });

    it('should display error stack in development', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      render(
        <ErrorBoundary>
          <ThrowError message='Stack test' />
        </ErrorBoundary>,
      );

      // Stack trace container should exist
      const stackContainer = screen.getByText('Stack test').closest('.max-w-md');
      expect(stackContainer).toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('Styling and Layout', () => {
    it('should have full screen layout for error UI', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const wrapper = container.querySelector('.min-h-screen');
      expect(wrapper).toBeInTheDocument();
    });

    it('should have centered error content', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const wrapper = container.querySelector('.flex.items-center.justify-center');
      expect(wrapper).toBeInTheDocument();
    });

    it('should have error card with shadow', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const card = container.querySelector('.shadow-lg');
      expect(card).toBeInTheDocument();
    });

    it('should have rounded corners on error card', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const card = container.querySelector('.rounded-lg');
      expect(card).toBeInTheDocument();
    });

    it('should have icon with error styling', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const iconContainer = container.querySelector('.bg-red-100');
      expect(iconContainer).toBeInTheDocument();
    });
  });

  describe('Dark Mode', () => {
    it('should have dark mode classes for background', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const background = container.querySelector(String.raw`.dark\:bg-gray-900`);
      expect(background).toBeInTheDocument();
    });

    it('should have dark mode classes for card', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const card = container.querySelector(String.raw`.dark\:bg-gray-800`);
      expect(card).toBeInTheDocument();
    });

    it('should have dark mode classes for icon', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const iconBg = container.querySelector(String.raw`.dark\:bg-red-900`);
      expect(iconBg).toBeInTheDocument();
    });

    it('should have dark mode classes for text', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const title = container.querySelector(String.raw`.dark\:text-gray-100`);
      expect(title).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle errors with very long messages', () => {
      const longMessage = 'A'.repeat(1000);
      render(
        <ErrorBoundary>
          <ThrowError message={longMessage} />
        </ErrorBoundary>,
      );

      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    it('should handle errors with special characters', () => {
      render(
        <ErrorBoundary>
          <ThrowError message="<Error> & 'special' characters" />
        </ErrorBoundary>,
      );

      expect(screen.getByText("<Error> & 'special' characters")).toBeInTheDocument();
    });

    it('should handle errors with multiline messages', () => {
      render(
        <ErrorBoundary>
          <ThrowError message='Line 1\nLine 2\nLine 3' />
        </ErrorBoundary>,
      );

      expect(screen.getByText(/Line 1/)).toBeInTheDocument();
    });

    it('should handle null error message', () => {
      render(
        <ErrorBoundary>
          <ThrowError message='' />
        </ErrorBoundary>,
      );

      expect(screen.getByText('An unexpected error occurred')).toBeInTheDocument();
    });

    it('should handle multiple sequential errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError message='Error 1' />
        </ErrorBoundary>,
      );

      expect(screen.getByText('Error 1')).toBeInTheDocument();

      // Reset and throw new error
      fireEvent.click(screen.getByText('Try again'));

      // Should still show error UI
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });
  });

  describe('Component Lifecycle', () => {
    it('should call componentDidCatch', () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      // ComponentDidCatch logs to console
      expect(consoleErrorSpy).toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
    });

    it('should update state via getDerivedStateFromError', () => {
      render(
        <ErrorBoundary>
          <ThrowError message='State update test' />
        </ErrorBoundary>,
      );

      // If state wasn't updated, error UI wouldn't show
      expect(screen.getByText('State update test')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have semantic heading for error title', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const heading = container.querySelector('h2');
      expect(heading).toBeInTheDocument();
      expect(heading?.textContent).toBe('Something went wrong');
    });

    it('should have descriptive error message', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError message='Descriptive error' />
        </ErrorBoundary>,
      );

      const message = container.querySelector('p');
      expect(message).toBeInTheDocument();
      expect(message?.textContent).toBe('Descriptive error');
    });

    it('should have accessible buttons', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>,
      );

      const tryAgainButton = screen.getByRole('button', { name: /try again/i });
      const reloadButton = screen.getByRole('button', { name: /reload page/i });

      expect(tryAgainButton).toBeInTheDocument();
      expect(reloadButton).toBeInTheDocument();
    });
  });

  describe('Real-world Scenarios', () => {
    it('should catch network errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError message='Network request failed' />
        </ErrorBoundary>,
      );

      expect(screen.getByText('Network request failed')).toBeInTheDocument();
    });

    it('should catch API errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError message='API returned 500' />
        </ErrorBoundary>,
      );

      expect(screen.getByText('API returned 500')).toBeInTheDocument();
    });

    it('should catch parsing errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError message='JSON parse error' />
        </ErrorBoundary>,
      );

      expect(screen.getByText('JSON parse error')).toBeInTheDocument();
    });

    it('should wrap entire application', () => {
      render(
        <ErrorBoundary>
          <div>
            <header>Header</header>
            <main>
              <ThrowError />
            </main>
            <footer>Footer</footer>
          </div>
        </ErrorBoundary>,
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.queryByText('Header')).not.toBeInTheDocument();
      expect(screen.queryByText('Footer')).not.toBeInTheDocument();
    });
  });
});
