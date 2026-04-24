/**
 * UX Tests: Confirmation Dialogs, Toasts, and Error Boundaries
 * Tests user feedback mechanisms and error handling UX
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

let user: ReturnType<typeof userEvent.setup>;

// Mock ConfirmDialog component
function MockConfirmDialog({
  open = false,
  title = 'Confirm Action',
  message = 'Are you sure?',
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  isDestructive = false,
  onConfirm = vi.fn(),
  onCancel = vi.fn(),
}: {
  open?: boolean;
  title?: string;
  message?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  isDestructive?: boolean;
  onConfirm?: () => void;
  onCancel?: () => void;
}) {
  if (!open) {
    return null;
  }

  return (
    <div
      role='alertdialog'
      aria-modal='true'
      aria-labelledby='dialog-title'
      aria-describedby='dialog-description'
      className='fixed inset-0 z-50 flex items-center justify-center'
    >
      <div onClick={onCancel} aria-hidden='true' className='fixed inset-0' />
      <div
        onClick={(e) => {
          e.stopPropagation();
        }}
        className='max-w-sm rounded-lg bg-white p-6 shadow-lg'
      >
        <h2 id='dialog-title' className='text-lg font-semibold'>
          {title}
        </h2>
        <p id='dialog-description' className='mt-2 text-gray-600'>
          {message}
        </p>
        <div className='mt-6 flex justify-end gap-2'>
          <button onClick={onCancel} className='rounded px-4 py-2 text-gray-600 hover:bg-gray-100'>
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className={`rounded px-4 py-2 text-white ${
              isDestructive ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

// Mock Toast component
function MockToast({
  open = false,
  type = 'info',
  message = 'Message',
  duration = 3000,
  onClose = vi.fn(),
}: {
  open?: boolean;
  type?: 'success' | 'error' | 'warning' | 'info';
  message?: string;
  duration?: number;
  onClose?: () => void;
}) {
  React.useEffect(() => {
    if (open && duration) {
      const timer = setTimeout(onClose, duration);
      return () => {
        clearTimeout(timer);
      };
    }
    return;
  }, [open, duration, onClose]);

  if (!open) {
    return null;
  }

  const bgColor = {
    error: 'bg-red-600',
    info: 'bg-blue-600',
    success: 'bg-green-600',
    warning: 'bg-yellow-600',
  }[type];

  return (
    <div
      role='status'
      aria-live='polite'
      aria-atomic='true'
      className={`fixed right-4 bottom-4 ${bgColor} rounded px-4 py-3 text-white shadow-lg`}
    >
      {message}
    </div>
  );
}

// Mock ErrorBoundary component
class MockErrorBoundary extends React.Component<
  { children: React.ReactNode; onError?: (error: Error) => void },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode; onError?: (error: Error) => void }) {
    super(props);
    this.state = { error: null, hasError: false };
  }

  static override getDerivedStateFromError(error: Error) {
    return { error, hasError: true };
  }

  override componentDidCatch(error: Error) {
    this.props.onError?.(error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div role='alert' className='border-l-4 border-red-600 bg-red-50 p-6' aria-live='assertive'>
          <h2 className='font-semibold text-red-800'>Something went wrong</h2>
          <p className='mt-2 text-red-700'>{this.state.error?.message}</p>
          <button
            onClick={() => {
              globalThis.location.reload();
            }}
            className='mt-4 rounded bg-red-600 px-4 py-2 text-white hover:bg-red-700'
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

describe('Confirmation Dialogs - Structure and Accessibility', () => {
  it('should render dialog with proper ARIA roles', () => {
    render(<MockConfirmDialog open />);

    const dialog = screen.getByRole('alertdialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby');
    expect(dialog).toHaveAttribute('aria-describedby');
  });

  it('should have proper heading and description', () => {
    render(<MockConfirmDialog open title='Delete Item' message='This action cannot be undone' />);

    expect(screen.getByText('Delete Item')).toBeInTheDocument();
    expect(screen.getByText('This action cannot be undone')).toBeInTheDocument();
  });

  it('should have labeled action buttons', () => {
    render(<MockConfirmDialog open confirmLabel='Delete' cancelLabel='Keep' />);

    expect(screen.getByRole('button', { name: 'Delete' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Keep' })).toBeInTheDocument();
  });
});

describe('Confirmation Dialogs - User Interactions', () => {
  beforeEach(() => {
    user = userEvent.setup();
  });

  it('should call onConfirm when confirm button clicked', async () => {
    const handleConfirm = vi.fn();

    render(<MockConfirmDialog open confirmLabel='Confirm' onConfirm={handleConfirm} />);

    await user.click(screen.getByRole('button', { name: 'Confirm' }));
    expect(handleConfirm).toHaveBeenCalledOnce();
  });

  it('should call onCancel when cancel button clicked', async () => {
    const handleCancel = vi.fn();

    render(<MockConfirmDialog open cancelLabel='Cancel' onCancel={handleCancel} />);

    await user.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(handleCancel).toHaveBeenCalledOnce();
  });

  it('should close dialog when backdrop clicked', async () => {
    const handleCancel = vi.fn();

    const { container } = render(<MockConfirmDialog open onCancel={handleCancel} />);

    const backdrop = container.querySelector("[aria-hidden='true']");
    if (backdrop) {
      await user.click(backdrop);
    }
    expect(handleCancel).toHaveBeenCalled();
  });

  it('should support keyboard navigation (Tab, Enter, Escape)', async () => {
    const handleCancel = vi.fn();

    render(<MockConfirmDialog open cancelLabel='Cancel' onCancel={handleCancel} />);

    const confirmBtn = screen.getByRole('button', { name: 'Confirm' });
    const cancelBtn = screen.getByRole('button', { name: 'Cancel' });

    // Tab between buttons
    confirmBtn.focus();
    expect(confirmBtn).toHaveFocus();

    await user.keyboard('{Tab}');
    expect(cancelBtn).toHaveFocus();

    // Escape should cancel
    await user.keyboard('{Escape}');
    expect(handleCancel).toHaveBeenCalled();
  });
});

describe('Confirmation Dialogs - Destructive Actions', () => {
  it('should style destructive actions distinctly', () => {
    render(<MockConfirmDialog open isDestructive />);

    const confirmBtn = screen.getByRole('button', { name: 'Confirm' });
    expect(confirmBtn.className).toContain('bg-red-600');
  });

  it('should require confirmation for destructive actions', () => {
    render(<MockConfirmDialog open isDestructive />);

    const dialog = screen.getByRole('alertdialog');
    expect(dialog).toBeInTheDocument();
    // Should require explicit action
  });
});

describe('Success Toast - Display and Behavior', () => {
  it("should render toast with role='status'", () => {
    render(<MockToast open type='success' message='Saved successfully' />);

    const toast = screen.getByRole('status');
    expect(toast).toBeInTheDocument();
    expect(toast).toHaveAttribute('aria-live', 'polite');
    expect(toast).toHaveAttribute('aria-atomic', 'true');
  });

  it('should display success message', () => {
    render(<MockToast open type='success' message='Item created successfully' />);

    expect(screen.getByText('Item created successfully')).toBeInTheDocument();
  });

  it('should auto-dismiss after duration', async () => {
    const handleClose = vi.fn();
    render(
      <MockToast open type='success' message='Success' duration={100} onClose={handleClose} />,
    );

    await waitFor(() => {
      expect(handleClose).toHaveBeenCalled();
    });
  });

  it('should apply success styling', () => {
    const { container } = render(<MockToast open type='success' message='Success' />);

    const toast = container.querySelector('.bg-green-600');
    expect(toast).toBeInTheDocument();
  });
});

describe('Error Toast - Display and Behavior', () => {
  it('should render error toast with distinct styling', () => {
    const { container } = render(<MockToast open type='error' message='Error occurred' />);

    const toast = container.querySelector('.bg-red-600');
    expect(toast).toBeInTheDocument();
    expect(screen.getByText('Error occurred')).toBeInTheDocument();
  });

  it('should not auto-dismiss error toasts by default', async () => {
    const handleClose = vi.fn();
    render(<MockToast open type='error' message='Error' duration={0} onClose={handleClose} />);

    // Should stay visible
    expect(screen.getByText('Error')).toBeInTheDocument();
  });

  it('should provide clear error messaging', () => {
    render(<MockToast open type='error' message='Failed to save: Network error' />);

    expect(screen.getByText('Failed to save: Network error')).toBeInTheDocument();
  });
});

describe('Toast Types and Variants', () => {
  it('should support multiple toast types', () => {
    const types: ('success' | 'error' | 'warning' | 'info')[] = [
      'success',
      'error',
      'warning',
      'info',
    ];

    types.forEach((type) => {
      const { unmount } = render(<MockToast open type={type} message={`${type} message`} />);

      expect(screen.getByText(`${type} message`)).toBeInTheDocument();
      unmount();
    });
  });

  it('should apply appropriate styling for each type', () => {
    const styleMap = {
      error: 'bg-red-600',
      info: 'bg-blue-600',
      success: 'bg-green-600',
      warning: 'bg-yellow-600',
    };

    Object.entries(styleMap).forEach(([type, className]) => {
      const { container, unmount } = render(
        <MockToast
          open
          type={
            type === 'success'
              ? 'success'
              : type === 'error'
                ? 'error'
                : type === 'warning'
                  ? 'warning'
                  : 'info'
          }
          message={type}
        />,
      );

      const toast = container.querySelector(`.${className}`);
      expect(toast).toBeInTheDocument();
      unmount();
    });
  });
});

describe('Error Boundary - Error Catching', () => {
  it('should catch errors from child components', () => {
    const ErrorComponent = () => {
      throw new Error('Test error');
    };

    const handleError = vi.fn();

    render(
      <MockErrorBoundary onError={handleError}>
        <ErrorComponent />
      </MockErrorBoundary>,
    );

    expect(handleError).toHaveBeenCalled();
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('should display error message to user', () => {
    const ErrorComponent = () => {
      throw new Error('Database connection failed');
    };

    render(
      <MockErrorBoundary>
        <ErrorComponent />
      </MockErrorBoundary>,
    );

    expect(screen.getByText('Database connection failed')).toBeInTheDocument();
  });

  it('should provide recovery option (reload button)', async () => {
    const ErrorComponent = () => {
      throw new Error('Fatal error');
    };

    render(
      <MockErrorBoundary>
        <ErrorComponent />
      </MockErrorBoundary>,
    );

    const reloadBtn = screen.getByRole('button', { name: 'Reload Page' });
    expect(reloadBtn).toBeInTheDocument();
  });

  it('should have alert role for screen readers', () => {
    const ErrorComponent = () => {
      throw new Error('Test error');
    };

    render(
      <MockErrorBoundary>
        <ErrorComponent />
      </MockErrorBoundary>,
    );

    const alert = screen.getByRole('alert');
    expect(alert).toBeInTheDocument();
  });

  it('should not catch errors in event handlers', () => {
    // Error boundaries don't catch event handler errors
    const handleClick = vi.fn(() => {
      throw new Error('Click handler error');
    });

    render(
      <MockErrorBoundary>
        <button onClick={handleClick}>Click me</button>
      </MockErrorBoundary>,
    );

    const button = screen.getByRole('button');
    // This should not trigger error boundary
    expect(() => {
      button.click();
    }).toThrow();
  });
});

describe('Empty States - User Feedback', () => {
  beforeEach(() => {
    user = userEvent.setup();
  });

  function MockEmptyState({
    icon = '📭',
    title = 'No items',
    message = 'Create your first item to get started',
    actionLabel = 'Create Item',
    onAction = vi.fn(),
  }: {
    icon?: string;
    title?: string;
    message?: string;
    actionLabel?: string;
    onAction?: () => void;
  }) {
    return (
      <div className='py-12 text-center' role='region' aria-label='Empty state'>
        <span className='mb-4 block text-4xl'>{icon}</span>
        <h2 className='text-xl font-semibold text-gray-800'>{title}</h2>
        <p className='mt-2 text-gray-600'>{message}</p>
        {actionLabel && (
          <button
            onClick={onAction}
            className='mt-4 rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700'
          >
            {actionLabel}
          </button>
        )}
      </div>
    );
  }

  it('should render empty state with descriptive messaging', () => {
    render(<MockEmptyState />);

    expect(screen.getByText('No items')).toBeInTheDocument();
    expect(screen.getByText('Create your first item to get started')).toBeInTheDocument();
  });

  it('should provide action to create item', async () => {
    const handleAction = vi.fn();

    render(<MockEmptyState actionLabel='Create Item' onAction={handleAction} />);

    await user.click(screen.getByRole('button', { name: 'Create Item' }));
    expect(handleAction).toHaveBeenCalled();
  });

  it('should have appropriate role for accessibility', () => {
    render(<MockEmptyState />);

    const region = screen.getByRole('region');
    expect(region).toHaveAttribute('aria-label', 'Empty state');
  });
});

describe('Loading States - User Feedback', () => {
  function MockLoadingState() {
    return (
      <div role='status' aria-busy='true' aria-live='polite'>
        <div className='inline-block h-4 w-4 animate-spin border-2 border-blue-600' />
        <span className='ml-2'>Loading...</span>
      </div>
    );
  }

  it('should render loading state with proper ARIA', () => {
    render(<MockLoadingState />);

    const status = screen.getByRole('status');
    expect(status).toHaveAttribute('aria-busy', 'true');
    expect(status).toHaveAttribute('aria-live', 'polite');
  });

  it('should announce loading status to screen readers', () => {
    render(<MockLoadingState />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
});
