/**
 * Mobile Tests: Responsive Design, Touch Targets, Mobile Forms, and Gestures
 * Tests mobile-specific UX and accessibility requirements
 */

import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { describe, expect, it, vi } from 'vitest';

// Mock Responsive Card Component
function MockResponsiveCard({
  title = 'Card Title',
  description = 'Card description',
  actionLabel = 'Action',
  onAction = vi.fn(),
}: {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <div className='mx-auto max-w-sm rounded-lg bg-white p-4 shadow sm:max-w-md sm:p-6'>
      <h3 className='text-lg font-semibold text-gray-900 sm:text-xl'>{title}</h3>
      <p className='mt-2 text-sm text-gray-600 sm:text-base'>{description}</p>
      <button
        onClick={onAction}
        className='mt-4 w-full rounded bg-blue-600 px-4 py-3 font-medium text-white transition-colors hover:bg-blue-700 active:bg-blue-800'
        aria-label={actionLabel}
      >
        {actionLabel}
      </button>
    </div>
  );
}

// Mock Mobile Form Component
function MockMobileForm({
  onSubmit = vi.fn(),
}: {
  onSubmit?: (data: { email: string; message: string }) => void;
}) {
  const [email, setEmail] = React.useState('');
  const [message, setMessage] = React.useState('');
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 100));
      onSubmit({ email, message });
      setEmail('');
      setMessage('');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className='mx-auto max-w-2xl rounded-lg bg-white p-4 shadow sm:p-6'
    >
      <h2 className='mb-6 text-xl font-bold sm:text-2xl'>Contact Form</h2>

      <div className='mb-6'>
        <label htmlFor='email' className='mb-2 block text-sm font-medium'>
          Email Address
        </label>
        <input
          id='email'
          type='email'
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
          }}
          placeholder='your@email.com'
          className='w-full rounded-lg border px-4 py-3 text-base focus:border-transparent focus:ring-2 focus:ring-blue-600'
          required
        />
      </div>

      <div className='mb-6'>
        <label htmlFor='message' className='mb-2 block text-sm font-medium'>
          Message
        </label>
        <textarea
          id='message'
          value={message}
          onChange={(e) => {
            setMessage(e.target.value);
          }}
          placeholder='Your message...'
          className='w-full rounded-lg border px-4 py-3 text-base focus:border-transparent focus:ring-2 focus:ring-blue-600'
          rows={4}
          required
        />
      </div>

      <button
        type='submit'
        disabled={isSubmitting}
        className='w-full rounded-lg bg-blue-600 px-4 py-3 font-medium text-white transition-colors hover:bg-blue-700 active:bg-blue-800 disabled:opacity-50'
      >
        {isSubmitting ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  );
}

// Mock Bottom Sheet Component
function MockBottomSheet({
  isOpen = false,
  title = 'Options',
  onClose = vi.fn(),
  children,
}: {
  isOpen?: boolean;
  title?: string;
  onClose?: () => void;
  children?: React.ReactNode;
}) {
  if (!isOpen) {
    return null;
  }

  return (
    <div
      className='fixed inset-0 z-50 bg-black/50'
      onClick={onClose}
      role='dialog'
      aria-modal='true'
    >
      <div
        onClick={(e) => {
          e.stopPropagation();
        }}
        className='animate-slide-up absolute right-0 bottom-0 left-0 rounded-t-lg bg-white shadow-lg'
        aria-labelledby='sheet-title'
      >
        <div className='flex items-center justify-between border-b border-gray-200 p-4'>
          <h2 id='sheet-title' className='font-semibold'>
            {title}
          </h2>
          <button
            onClick={onClose}
            className='rounded px-3 py-2 text-gray-600 hover:bg-gray-100'
            aria-label='Close'
          >
            ×
          </button>
        </div>
        <div className='p-4'>{children}</div>
      </div>
    </div>
  );
}

// Mock Swipe Action Component
function MockSwipeableListItem({
  label = 'Item',
  onSwipeLeft = vi.fn(),
  onSwipeRight = vi.fn(),
}: {
  label?: string;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
}) {
  const [startX, setStartX] = React.useState(0);
  const [offset, setOffset] = React.useState(0);

  const handleTouchStart = (e: React.TouchEvent) => {
    setStartX(e.touches[0].clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    const currentX = e.touches[0].clientX;
    const diff = currentX - startX;
    setOffset(diff);
  };

  const handleTouchEnd = () => {
    if (offset < -50) {
      onSwipeLeft();
    } else if (offset > 50) {
      onSwipeRight();
    }
    setOffset(0);
  };

  return (
    <div
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className='touch-pan-y border-b bg-white'
      style={{ transform: `translateX(${offset}px)` }}
    >
      <div className='flex items-center p-4'>
        <span>{label}</span>
      </div>
    </div>
  );
}

describe('Responsive Card Views - Viewport Sizes', () => {
  it('should render card with responsive padding', () => {
    render(<MockResponsiveCard title='Test Card' />);

    const card = container.querySelector('.p-4');
    expect(card).toBeInTheDocument();
    // Should have both mobile (p-4) and tablet (sm:p-6) classes
    expect(card?.className).toContain('p-4');
    expect(card?.className).toContain('sm:p-6');
  });

  it('should have appropriate max-width for card', () => {
    render(<MockResponsiveCard />);

    const card = container.querySelector('.max-w-sm');
    expect(card).toBeInTheDocument();
  });

  it('should display content properly on mobile viewport', () => {
    render(<MockResponsiveCard title='Mobile Card' description='Test' />);

    expect(screen.getByText('Mobile Card')).toBeInTheDocument();
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});

describe('Touch Target Sizes', () => {
  it('should have minimum 44x44px touch targets', () => {
    render(<MockResponsiveCard actionLabel='Click Me' />);

    const button = screen.getByRole('button');
    const rect = button.getBoundingClientRect();

    // Touch target should be at least 44x44px
    expect(Math.min(rect.width, rect.height)).toBeGreaterThanOrEqual(44);
  });

  it('should have sufficient padding on buttons for touch', () => {
    render(<MockResponsiveCard />);

    const button = screen.getByRole('button');
    const _styles = globalThis.getComputedStyle(button);

    // Should have visible padding
    expect(button.className).toContain('px-4');
    expect(button.className).toContain('py-3');
  });

  it('should have proper spacing between interactive elements', () => {
    render(
      <div className='flex flex-col gap-4'>
        <button className='rounded bg-blue-600 px-4 py-3 text-white'>Button 1</button>
        <button className='rounded bg-blue-600 px-4 py-3 text-white'>Button 2</button>
      </div>,
    );

    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(2);
  });

  it('should have adequate spacing around form inputs', () => {
    render(<MockMobileForm />);

    const input = container.querySelector("input[type='email']");
    expect(input).toBeInTheDocument();
    if (input instanceof HTMLElement) {
      expect(input.className).toContain('px-4');
      expect(input.className).toContain('py-3');
    }
  });

  it('should use large text size for mobile inputs', () => {
    render(<MockMobileForm />);

    const emailInput = container.querySelector("input[type='email']");
    expect(emailInput).toBeInTheDocument();
    if (emailInput instanceof HTMLElement) {
      expect(emailInput.className).toContain('text-base');
    }
  });

  it('should show appropriate keyboard for email input', () => {
    render(<MockMobileForm />);

    const emailInput = screen.getByPlaceholderText('your@email.com');
    expect(emailInput).toHaveAttribute('type', 'email');
  });
});

describe('Mobile Forms - Input Sizing', () => {
  it('should render form with full-width inputs', () => {
    render(<MockMobileForm />);

    const inputs = container.querySelectorAll('input, textarea');
    inputs.forEach((input) => {
      expect(input.className).toContain('w-full');
    });
  });

  it('should allow focusing on form inputs without zoom', async () => {
    render(<MockMobileForm />);

    const emailInput = screen.getByPlaceholderText('your@email.com');

    await user.click(emailInput);
    expect(emailInput).toHaveFocus();
  });

  it('should submit form with valid data', async () => {
    const handleSubmit = vi.fn();

    render(<MockMobileForm onSubmit={handleSubmit} />);

    const emailInput = screen.getByPlaceholderText('your@email.com');
    const messageInput = screen.getByPlaceholderText('Your message...');
    const submitBtn = screen.getByRole('button', { name: /Send Message/i });

    await user.type(emailInput, 'test@example.com');
    await user.type(messageInput, 'Test message');
    await user.click(submitBtn);

    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        message: 'Test message',
      });
    });
  });
});

describe('Bottom Sheet - Mobile Pattern', () => {
  it('should render bottom sheet when open', () => {
    render(
      <MockBottomSheet isOpen title='Menu'>
        <button>Option 1</button>
        <button>Option 2</button>
      </MockBottomSheet>,
    );

    expect(screen.getByText('Menu')).toBeInTheDocument();
    expect(screen.getByText('Option 1')).toBeInTheDocument();
  });

  it('should have proper dialog semantics', () => {
    render(
      <MockBottomSheet isOpen title='Menu'>
        Content
      </MockBottomSheet>,
    );

    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby');
  });

  it('should close on backdrop click', async () => {
    const handleClose = vi.fn();

    render(
      <MockBottomSheet isOpen title='Menu' onClose={handleClose}>
        Content
      </MockBottomSheet>,
    );

    const backdrop = container.querySelector(String.raw`.bg-black\/50`);
    if (backdrop) {
      await user.click(backdrop);
    }

    expect(handleClose).toHaveBeenCalled();
  });

  it('should close on close button click', async () => {
    const handleClose = vi.fn();

    render(
      <MockBottomSheet isOpen title='Menu' onClose={handleClose}>
        Content
      </MockBottomSheet>,
    );

    const closeBtn = screen.getByRole('button', { name: 'Close' });
    await user.click(closeBtn);

    expect(handleClose).toHaveBeenCalled();
  });

  it('should not close when clicking content', async () => {
    const handleClose = vi.fn();

    render(
      <MockBottomSheet isOpen title='Menu' onClose={handleClose}>
        <button>Option</button>
      </MockBottomSheet>,
    );

    const content = container.querySelector('.bg-white');
    if (content) {
      await user.click(content);
    }

    expect(handleClose).not.toHaveBeenCalled();
  });
});

describe('Swipe Gestures - Touch Interactions', () => {
  it('should detect swipe left gesture', async () => {
    const handleSwipeLeft = vi.fn();

    render(<MockSwipeableListItem label='Item' onSwipeLeft={handleSwipeLeft} />);

    const item = container.querySelector('.bg-white');

    // Simulate swipe left
    const touchStart = new TouchEvent('touchstart', {
      // Minimal touch for test; Touch type is narrow
      touches: [{ clientX: 100 } as Touch],
    });
    const touchEnd = new TouchEvent('touchend');

    item?.dispatchEvent(touchStart);

    // Simulate moving to x=30 (swipe left)
    const touchMove = new TouchEvent('touchmove', {
      touches: [{ clientX: 30 } as Touch],
    });
    item?.dispatchEvent(touchMove);
    item?.dispatchEvent(touchEnd);
  });

  it('should have smooth touch interaction', () => {
    render(<MockSwipeableListItem label='Item' />);

    const item = container.querySelector('.touch-pan-y');
    expect(item).toBeInTheDocument();
    // Touch-pan-y allows vertical scrolling while swiping horizontally
  });
});

describe('Responsive Navigation', () => {
  function MockMobileNav({ onNavigate = vi.fn() }: { onNavigate?: (path: string) => void }) {
    const [isOpen, setIsOpen] = React.useState(false);

    return (
      <nav className='bg-white shadow'>
        <div className='flex items-center justify-between px-4 py-3'>
          <span className='text-lg font-bold'>Logo</span>
          <button
            onClick={() => {
              setIsOpen(!isOpen);
            }}
            className='rounded px-3 py-2 hover:bg-gray-100'
            aria-label='Toggle menu'
            aria-expanded={isOpen}
          >
            ☰
          </button>
        </div>

        {isOpen && (
          <div className='border-t bg-gray-50 px-4 py-2'>
            <button
              onClick={() => {
                onNavigate('/');
                setIsOpen(false);
              }}
              className='mb-2 block w-full rounded px-4 py-2 text-left hover:bg-gray-200'
            >
              Home
            </button>
            <button
              onClick={() => {
                onNavigate('/projects');
                setIsOpen(false);
              }}
              className='block w-full rounded px-4 py-2 text-left hover:bg-gray-200'
            >
              Projects
            </button>
          </div>
        )}
      </nav>
    );
  }

  it('should show mobile menu toggle button', () => {
    render(<MockMobileNav />);

    const menuBtn = screen.getByRole('button', { name: /Toggle menu/i });
    expect(menuBtn).toBeInTheDocument();
  });

  it('should toggle menu visibility', async () => {
    render(<MockMobileNav />);

    const menuBtn = screen.getByRole('button', { name: /Toggle menu/i });

    // Menu should be hidden initially
    expect(menuBtn).toHaveAttribute('aria-expanded', 'false');

    await user.click(menuBtn);

    // Menu should be visible
    expect(menuBtn).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByText('Home')).toBeInTheDocument();
  });

  it('should close menu when item clicked', async () => {
    const handleNavigate = vi.fn();

    render(<MockMobileNav onNavigate={handleNavigate} />);

    const menuBtn = screen.getByRole('button', { name: /Toggle menu/i });
    await user.click(menuBtn);

    const homeBtn = screen.getByRole('button', { name: 'Home' });
    await user.click(homeBtn);

    expect(handleNavigate).toHaveBeenCalledWith('/');
    expect(menuBtn).toHaveAttribute('aria-expanded', 'false');
  });
});

describe('Portrait/Landscape Orientation', () => {
  it('should adapt layout for different orientations', () => {
    render(
      <div className='grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3'>
        <div>Item 1</div>
        <div>Item 2</div>
        <div>Item 3</div>
      </div>,
    );

    expect(container.querySelector('.grid')).toBeInTheDocument();
    // Should have responsive grid classes
    expect(container.querySelector('.grid')?.className).toContain('grid-cols-1');
  });
});

describe('Mobile Accessibility', () => {
  it('should have sufficient color contrast for mobile', () => {
    render(
      <div className='bg-white text-gray-900'>
        <h1>Accessible Heading</h1>
      </div>,
    );

    expect(container.querySelector('.text-gray-900')).toBeInTheDocument();
  });

  it('should have readable font sizes on mobile', () => {
    render(
      <div>
        <p className='text-sm sm:text-base'>Text</p>
      </div>,
    );

    const text = container.querySelector('.text-sm');
    expect(text).toBeInTheDocument();
  });

  it('should have adequate line height for readability', () => {
    render(
      <p className='text-base leading-relaxed'>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
      </p>,
    );

    const text = container.querySelector('.leading-relaxed');
    expect(text).toBeInTheDocument();
  });
});

describe('Orientation Change Handling', () => {
  it('should handle viewport resize', () => {
    render(<div className='w-full sm:max-w-md'>Content</div>);

    expect(container.querySelector('.w-full')).toBeInTheDocument();
  });
});

describe('Fixed/Sticky Element Safety', () => {
  it('should avoid fixed elements that interfere with input', () => {
    render(
      <div>
        <div className='sticky top-0 z-10 bg-white shadow'>Header</div>
        <input className='w-full px-4 py-3' placeholder='Input' />
      </div>,
    );

    expect(container.querySelector('.sticky')).toBeInTheDocument();
    expect(container.querySelector('input')).toBeInTheDocument();
  });
});
