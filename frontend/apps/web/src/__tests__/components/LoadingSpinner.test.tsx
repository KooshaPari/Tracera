/**
 * LoadingSpinner Component Tests
 *
 * Comprehensive tests covering:
 * - Different sizes (sm, md, lg, xl)
 * - Full screen mode
 * - Text display
 * - Custom classNames
 * - Animations
 * - Edge cases
 */

import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { LoadingSpinner } from '../../components/layout/LoadingSpinner';

describe('LoadingSpinner Component', () => {
  describe('Basic Rendering', () => {
    it('should render spinner with default props', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = container.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('should render spinner with default medium size', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = container.querySelector('.w-8.h-8');
      expect(spinner).toBeInTheDocument();
    });

    it('should render spinner with border classes', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = container.querySelector('.rounded-full');
      expect(spinner).toBeInTheDocument();
    });

    it('should have animate-spin class', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = container.querySelector('.animate-spin');
      expect(spinner).toHaveClass('animate-spin');
    });
  });

  describe('Size Variants', () => {
    it('should render small size (sm)', () => {
      const { container } = render(<LoadingSpinner size='sm' />);

      const spinner = container.querySelector('.w-4.h-4');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveClass('border-2');
    });

    it('should render medium size (md)', () => {
      const { container } = render(<LoadingSpinner size='md' />);

      const spinner = container.querySelector('.w-8.h-8');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveClass('border-2');
    });

    it('should render large size (lg)', () => {
      const { container } = render(<LoadingSpinner size='lg' />);

      const spinner = container.querySelector('.w-12.h-12');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveClass('border-3');
    });

    it('should render extra large size (xl)', () => {
      const { container } = render(<LoadingSpinner size='xl' />);

      const spinner = container.querySelector('.w-16.h-16');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveClass('border-4');
    });
  });

  describe('Text Display', () => {
    it('should render with text when provided', () => {
      const { container } = render(<LoadingSpinner text='Loading data...' />);

      expect(screen.getByText('Loading data...')).toBeInTheDocument();
    });

    it('should not render text when not provided', () => {
      const { container } = render(<LoadingSpinner />);

      const text = container.querySelector('.text-sm');
      expect(text).not.toBeInTheDocument();
    });

    it('should render text with correct styling', () => {
      const { container } = render(<LoadingSpinner text='Loading...' />);

      const text = screen.getByText('Loading...');
      expect(text).toHaveClass('text-sm', 'text-gray-600', 'dark:text-gray-400');
    });

    it('should render text below spinner', () => {
      const { container } = render(<LoadingSpinner text='Loading...' />);

      const wrapper = container.querySelector('.flex.flex-col');
      expect(wrapper).toHaveClass('gap-3');
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className to spinner', () => {
      const { container } = render(<LoadingSpinner className='custom-spinner' />);

      const spinner = container.querySelector('.animate-spin');
      expect(spinner).toHaveClass('custom-spinner');
    });

    it('should merge custom className with default classes', () => {
      const { container } = render(<LoadingSpinner className='border-red-500' />);

      const spinner = container.querySelector('.animate-spin');
      expect(spinner).toHaveClass('border-red-500', 'rounded-full');
    });

    it('should apply multiple custom classes', () => {
      const { container } = render(<LoadingSpinner className='custom-class-1 custom-class-2' />);

      const spinner = container.querySelector('.animate-spin');
      expect(spinner).toHaveClass('custom-class-1', 'custom-class-2');
    });
  });

  describe('Full Screen Mode', () => {
    it('should render in full screen mode when fullScreen is true', () => {
      const { container } = render(<LoadingSpinner fullScreen />);

      const overlay = container.querySelector('.fixed.inset-0');
      expect(overlay).toBeInTheDocument();
    });

    it('should have full screen overlay classes', () => {
      const { container } = render(<LoadingSpinner fullScreen />);

      const overlay = container.querySelector('.fixed.inset-0');
      expect(overlay).toHaveClass('flex', 'items-center', 'justify-center');
    });

    it('should have backdrop blur in full screen mode', () => {
      const { container } = render(<LoadingSpinner fullScreen />);

      const overlay = container.querySelector('.backdrop-blur-sm');
      expect(overlay).toBeInTheDocument();
    });

    it('should have high z-index in full screen mode', () => {
      const { container } = render(<LoadingSpinner fullScreen />);

      const overlay = container.querySelector('.z-50');
      expect(overlay).toBeInTheDocument();
    });

    it('should not render full screen overlay by default', () => {
      const { container } = render(<LoadingSpinner />);

      const overlay = container.querySelector('.fixed.inset-0');
      expect(overlay).not.toBeInTheDocument();
    });

    it('should render text in full screen mode', () => {
      const { container } = render(<LoadingSpinner fullScreen text='Loading application...' />);

      expect(screen.getByText('Loading application...')).toBeInTheDocument();
    });
  });

  describe('Combined Props', () => {
    it('should render with all props combined', () => {
      const { container } = render(
        <LoadingSpinner size='lg' text='Please wait...' className='custom-loading' fullScreen />,
      );

      const spinner = container.querySelector('.animate-spin');
      expect(spinner).toHaveClass('w-12', 'h-12', 'custom-loading');
      expect(screen.getByText('Please wait...')).toBeInTheDocument();
      expect(container.querySelector('.fixed.inset-0')).toBeInTheDocument();
    });

    it('should render small spinner with text', () => {
      const { container } = render(<LoadingSpinner size='sm' text='Saving...' />);

      const spinner = container.querySelector('.w-4.h-4');
      expect(spinner).toBeInTheDocument();
      expect(screen.getByText('Saving...')).toBeInTheDocument();
    });

    it('should render xl spinner in full screen with text', () => {
      const { container } = render(
        <LoadingSpinner size='xl' fullScreen text='Initializing application...' />,
      );

      const spinner = container.querySelector('.w-16.h-16');
      expect(spinner).toBeInTheDocument();
      expect(screen.getByText('Initializing application...')).toBeInTheDocument();
      expect(container.querySelector('.fixed.inset-0')).toBeInTheDocument();
    });
  });

  describe('Dark Mode Support', () => {
    it('should have dark mode classes for spinner border', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = container.querySelector(String.raw`.dark\:border-gray-800`);
      expect(spinner).toBeInTheDocument();
    });

    it('should have dark mode classes for text', () => {
      const { container } = render(<LoadingSpinner text='Loading...' />);

      const text = screen.getByText('Loading...');
      expect(text).toHaveClass('dark:text-gray-400');
    });

    it('should have dark mode classes for full screen overlay', () => {
      const { container } = render(<LoadingSpinner fullScreen />);

      const overlay = container.querySelector(String.raw`.dark\:bg-gray-900\/80`);
      expect(overlay).toBeInTheDocument();
    });
  });

  describe('Animation Classes', () => {
    it('should have animate-spin class', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = container.querySelector('.animate-spin');
      expect(spinner).toHaveClass('animate-spin');
    });

    it('should have rounded-full for circular spinner', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = container.querySelector('.rounded-full');
      expect(spinner).toBeInTheDocument();
    });

    it('should have border styles for spinning effect', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = container.querySelector('.border-gray-200');
      expect(spinner).toBeInTheDocument();
    });

    it('should have contrasting border-top color', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = container.querySelector('.border-t-primary-600');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty string text', () => {
      const { container } = render(<LoadingSpinner text='' />);

      const wrapper = container.querySelector('.flex-col');
      expect(wrapper).toBeInTheDocument();
    });

    it('should handle very long text', () => {
      const longText = 'A'.repeat(200);
      const { container } = render(<LoadingSpinner text={longText} />);

      expect(screen.getByText(longText)).toBeInTheDocument();
    });

    it('should handle special characters in text', () => {
      const { container } = render(<LoadingSpinner text="Loading <data> & 'items'..." />);

      expect(screen.getByText("Loading <data> & 'items'...")).toBeInTheDocument();
    });

    it('should handle fullScreen=false explicitly', () => {
      const { container } = render(<LoadingSpinner fullScreen={false} />);

      const overlay = container.querySelector('.fixed.inset-0');
      expect(overlay).not.toBeInTheDocument();
    });

    it('should maintain aspect ratio with different sizes', () => {
      const { container: smContainer } = render(<LoadingSpinner size='sm' />);
      const { container: xlContainer } = render(<LoadingSpinner size='xl' />);

      const smSpinner = smContainer.querySelector('.w-4.h-4');
      const xlSpinner = xlContainer.querySelector('.w-16.h-16');

      expect(smSpinner).toBeInTheDocument();
      expect(xlSpinner).toBeInTheDocument();
    });
  });

  describe('Container Structure', () => {
    it('should have flex container for spinner and text', () => {
      const { container } = render(<LoadingSpinner text='Loading...' />);

      const flexContainer = container.querySelector('.flex.flex-col');
      expect(flexContainer).toHaveClass('items-center', 'justify-center');
    });

    it('should have gap between spinner and text', () => {
      const { container } = render(<LoadingSpinner text='Loading...' />);

      const flexContainer = container.querySelector('.gap-3');
      expect(flexContainer).toBeInTheDocument();
    });

    it('should only render spinner div when no text', () => {
      const { container } = render(<LoadingSpinner />);

      const spinnerDiv = container.querySelector('.animate-spin');
      expect(spinnerDiv).toBeInTheDocument();

      const textElement = container.querySelector('p');
      expect(textElement).not.toBeInTheDocument();
    });
  });

  describe('Real-world Use Cases', () => {
    it('should render as inline loading indicator', () => {
      const { container } = render(<LoadingSpinner size='sm' />);

      const spinner = container.querySelector('.w-4.h-4');
      expect(spinner).toBeInTheDocument();
      expect(container.querySelector('.fixed')).not.toBeInTheDocument();
    });

    it('should render as page loading overlay', () => {
      const { container } = render(<LoadingSpinner fullScreen size='lg' text='Loading page...' />);

      expect(container.querySelector('.fixed.inset-0')).toBeInTheDocument();
      expect(container.querySelector('.w-12.h-12')).toBeInTheDocument();
      expect(screen.getByText('Loading page...')).toBeInTheDocument();
    });

    it('should render as button loading state', () => {
      const { container } = render(<LoadingSpinner size='sm' />);

      const spinner = container.querySelector('.w-4.h-4.border-2');
      expect(spinner).toBeInTheDocument();
    });

    it('should render as data fetching indicator', () => {
      const { container } = render(<LoadingSpinner size='md' text='Fetching data...' />);

      const spinner = screen.getByText('Fetching data...').previousSibling;
      expect(spinner).toHaveClass('animate-spin');
    });

    it('should render as form submission indicator', () => {
      const { container } = render(<LoadingSpinner size='sm' text='Submitting...' />);

      expect(screen.getByText('Submitting...')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have descriptive text for screen readers', () => {
      const { container } = render(<LoadingSpinner text='Loading content' />);

      expect(screen.getByText('Loading content')).toBeInTheDocument();
    });

    it('should be keyboard accessible (no interaction needed)', () => {
      const { container } = render(<LoadingSpinner />);

      // Spinner should not be focusable as it's not interactive
      const spinner = container.querySelector('.animate-spin');
      expect(spinner).not.toHaveAttribute('tabindex');
    });

    it('should have semantic text element', () => {
      const { container } = render(<LoadingSpinner text='Loading...' />);

      const text = container.querySelector('p');
      expect(text).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('should render quickly without complex computations', () => {
      const start = performance.now();
      const { container } = render(<LoadingSpinner />);
      const end = performance.now();

      // Should render in less than 100ms
      expect(end - start).toBeLessThan(100);
    });

    it('should handle multiple spinners on same page', () => {
      const { container } = render(
        <>
          <LoadingSpinner size='sm' />
          <LoadingSpinner size='md' />
          <LoadingSpinner size='lg' />
        </>,
      );

      const spinners = container.querySelectorAll('.animate-spin');
      expect(spinners).toHaveLength(3);
    });
  });
});
