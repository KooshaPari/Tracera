import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

import { OptimizedImage, DocImage, Avatar, Logo } from '../optimized-image';

// Mock next/image to render a standard img tag with the props we care about
vi.mock('next/image', () => ({
  default: (props: any) => {
    // Simulate the onLoad callback for testing loading states
    // Extract non-standard DOM props and put them as data attributes to avoid React warnings
    const { onLoad, fill, priority, blurDataURL, ...rest } = props;
    return (
      <img
        {...rest}
        data-fill={fill ? 'true' : undefined}
        data-priority={priority ? 'true' : 'false'}
        data-blur-data-url={blurDataURL || undefined}
        data-testid='next-image'
        onLoad={onLoad}
      />
    );
  },
}));

describe('OptimizedImage', () => {
  it('renders an image with src and alt', () => {
    render(<OptimizedImage src='/test.jpg' alt='Test image' width={800} height={600} />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('src')).toBe('/test.jpg');
    expect(img.getAttribute('alt')).toBe('Test image');
  });

  it('renders width and height when fill is false', () => {
    render(<OptimizedImage src='/test.jpg' alt='Test' width={800} height={600} />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('width')).toBe('800');
    expect(img.getAttribute('height')).toBe('600');
  });

  it('renders with fill when fill=true', () => {
    render(<OptimizedImage src='/test.jpg' alt='Test' fill />);

    const img = screen.getByTestId('next-image');
    expect(img.dataset.fill).toBe('true');
  });

  it('shows loading indicator initially', () => {
    const { container } = render(
      <OptimizedImage src='/test.jpg' alt='Test' width={800} height={600} />,
    );

    // The loading overlay has animate-pulse class
    const loadingOverlay = container.querySelector('.animate-pulse');
    expect(loadingOverlay).not.toBeNull();
  });

  it('hides loading indicator after image loads', () => {
    const { container } = render(
      <OptimizedImage src='/test.jpg' alt='Test' width={800} height={600} />,
    );

    const img = screen.getByTestId('next-image');
    fireEvent.load(img);

    // After load, the loading overlay should be gone
    const loadingOverlay = container.querySelector('.animate-pulse');
    expect(loadingOverlay).toBeNull();
  });

  it('applies default quality of 85', () => {
    render(<OptimizedImage src='/test.jpg' alt='Test' width={800} height={600} />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('quality')).toBe('85');
  });

  it('applies custom quality', () => {
    render(<OptimizedImage src='/test.jpg' alt='Test' width={800} height={600} quality={50} />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('quality')).toBe('50');
  });

  it('applies responsive sizes', () => {
    render(
      <OptimizedImage
        src='/test.jpg'
        alt='Test'
        width={800}
        height={600}
        sizes='(max-width: 768px) 100vw, 50vw'
      />,
    );

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('sizes')).toBe('(max-width: 768px) 100vw, 50vw');
  });

  it('uses default sizes when not specified in non-fill mode', () => {
    render(<OptimizedImage src='/test.jpg' alt='Test' width={800} height={600} />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('sizes')).toBe(
      '(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw',
    );
  });

  it('uses "100vw" as default sizes in fill mode', () => {
    render(<OptimizedImage src='/test.jpg' alt='Test' fill />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('sizes')).toBe('100vw');
  });

  it('applies blur placeholder when blurDataURL is provided', () => {
    render(
      <OptimizedImage
        src='/test.jpg'
        alt='Test'
        width={800}
        height={600}
        blurDataURL='data:image/jpeg;base64,abc'
      />,
    );

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('placeholder')).toBe('blur');
    expect(img.getAttribute('data-blur-data-url')).toBe('data:image/jpeg;base64,abc');
  });

  it('uses empty placeholder when no blurDataURL', () => {
    render(<OptimizedImage src='/test.jpg' alt='Test' width={800} height={600} />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('placeholder')).toBe('empty');
  });

  it('applies priority loading and skips lazy loading', () => {
    render(<OptimizedImage src='/test.jpg' alt='Test' width={800} height={600} priority />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('data-priority')).toBe('true');
    // Priority images should NOT have loading="lazy"
    expect(img.getAttribute('loading')).toBeNull();
  });

  it('applies lazy loading when not priority', () => {
    render(<OptimizedImage src='/test.jpg' alt='Test' width={800} height={600} />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('loading')).toBe('lazy');
  });
});

describe('DocImage', () => {
  it('renders with preset documentation dimensions', () => {
    render(<DocImage src='/doc.jpg' alt='Documentation image' />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('width')).toBe('1200');
    expect(img.getAttribute('height')).toBe('675');
  });

  it('renders a figcaption when caption is provided', () => {
    render(<DocImage src='/doc.jpg' alt='Doc' caption='Figure 1: Architecture' />);

    expect(screen.getByText('Figure 1: Architecture')).toBeInTheDocument();
  });

  it('does not render a figcaption when caption is omitted', () => {
    const { container } = render(<DocImage src='/doc.jpg' alt='Doc' />);

    expect(container.querySelector('figcaption')).toBeNull();
  });

  it('wraps content in a figure element', () => {
    const { container } = render(<DocImage src='/doc.jpg' alt='Doc' />);
    expect(container.querySelector('figure')).not.toBeNull();
  });
});

describe('Avatar', () => {
  it('renders with default size of 40', () => {
    const { container } = render(<Avatar src='/avatar.jpg' alt='User' />);

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.style.width).toBe('40px');
    expect(wrapper.style.height).toBe('40px');
  });

  it('renders with custom size', () => {
    const { container } = render(<Avatar src='/avatar.jpg' alt='User' size={64} />);

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.style.width).toBe('64px');
    expect(wrapper.style.height).toBe('64px');
  });

  it('has rounded-full class for circular appearance', () => {
    const { container } = render(<Avatar src='/avatar.jpg' alt='User' />);

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('rounded-full');
  });
});

describe('Logo', () => {
  it('renders with default dimensions', () => {
    render(<Logo src='/logo.png' alt='Company Logo' />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('width')).toBe('120');
    expect(img.getAttribute('height')).toBe('40');
  });

  it('renders with custom dimensions', () => {
    render(<Logo src='/logo.png' alt='Logo' width={200} height={60} />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('width')).toBe('200');
    expect(img.getAttribute('height')).toBe('60');
  });

  it('renders with priority loading', () => {
    render(<Logo src='/logo.png' alt='Logo' />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('data-priority')).toBe('true');
  });

  it('uses quality of 100', () => {
    render(<Logo src='/logo.png' alt='Logo' />);

    const img = screen.getByTestId('next-image');
    expect(img.getAttribute('quality')).toBe('100');
  });
});
