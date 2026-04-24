import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import type { CardItem } from '@/components/mobile/ResponsiveCardView';

import { ResponsiveCardView } from '@/components/mobile/ResponsiveCardView';

describe(ResponsiveCardView, () => {
  it('renders card items', () => {
    const items: CardItem[] = [
      {
        id: '1',
        subtitle: 'Subtitle 1',
        title: 'Test Item 1',
      },
      {
        id: '2',
        subtitle: 'Subtitle 2',
        title: 'Test Item 2',
      },
    ];

    render(<ResponsiveCardView items={items} />);

    expect(screen.getByText('Test Item 1')).toBeInTheDocument();
    expect(screen.getByText('Test Item 2')).toBeInTheDocument();
    expect(screen.getByText('Subtitle 1')).toBeInTheDocument();
    expect(screen.getByText('Subtitle 2')).toBeInTheDocument();
  });

  it('displays empty state when no items', () => {
    const emptyState = <div>No items found</div>;

    render(<ResponsiveCardView items={[]} emptyState={emptyState} />);

    expect(screen.getByText('No items found')).toBeInTheDocument();
  });

  it('displays loading state', () => {
    render(<ResponsiveCardView items={[]} isLoading />);

    // Should render skeleton loaders
    const animatedElements = document.querySelectorAll('.animate-pulse');
    expect(animatedElements.length).toBeGreaterThan(0);
  });

  it('calls onItemClick when card is clicked', () => {
    const onItemClick = vi.fn();
    const items: CardItem[] = [
      {
        id: '1',
        title: 'Click Me',
      },
    ];

    const { container } = render(<ResponsiveCardView items={items} onItemClick={onItemClick} />);

    const button = container.querySelector('button');
    if (button) {
      button.click();
      expect(onItemClick).toHaveBeenCalled();
    }
  });

  it('renders with responsive grid classes', () => {
    const items: CardItem[] = [
      { id: '1', title: 'Item 1' },
      { id: '2', title: 'Item 2' },
      { id: '3', title: 'Item 3' },
    ];

    const { container } = render(<ResponsiveCardView items={items} />);

    // Check for responsive grid classes
    const gridContainer = container.querySelector('.grid');
    expect(gridContainer).toHaveClass('grid-cols-1');
    expect(gridContainer).toHaveClass('sm:grid-cols-2');
    expect(gridContainer).toHaveClass('lg:grid-cols-3');
  });

  it('ensures cards have minimum touch target height', () => {
    const items: CardItem[] = [{ id: '1', title: 'Test' }];

    const { container } = render(<ResponsiveCardView items={items} />);

    const button = container.querySelector('button');
    expect(button).toHaveClass('min-h-[120px]');
    expect(button).toHaveClass('sm:min-h-[140px]');
  });

  it('renders badges, status, and priority when provided', () => {
    const items: CardItem[] = [
      {
        badge: <span>Badge</span>,
        id: '1',
        priority: <span>High</span>,
        status: <span>In Progress</span>,
        title: 'Item with extras',
      },
    ];

    render(<ResponsiveCardView items={items} />);

    expect(screen.getByText('Badge')).toBeInTheDocument();
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('High')).toBeInTheDocument();
  });

  it('renders action buttons', () => {
    const items: CardItem[] = [
      {
        actions: <button>Action</button>,
        id: '1',
        title: 'Item with actions',
      },
    ];

    render(<ResponsiveCardView items={items} />);

    expect(screen.getByText('Action')).toBeInTheDocument();
  });
});
