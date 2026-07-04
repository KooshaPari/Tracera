/**
 * Empty State Component Tests
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Inbox } from 'lucide-react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  EmptyState,
  ErrorEmptyState,
  FilteredEmptyState,
  NoItemsEmptyState,
  NoSearchResultsEmptyState,
} from '../../components/ui/empty-state';

let user: ReturnType<typeof userEvent.setup>;

describe(EmptyState, () => {
  beforeEach(() => {
    user = userEvent.setup();
  });
  const defaultProps = {
    description: 'There are no items to display',
    icon: Inbox,
    title: 'No items',
  };

  it('renders with title and description', () => {
    render(<EmptyState {...defaultProps} />);
    expect(screen.getByText('No items')).toBeInTheDocument();
    expect(screen.getByText('There are no items to display')).toBeInTheDocument();
  });

  it('renders action buttons', async () => {
    const handleClick = vi.fn();

    render(
      <EmptyState {...defaultProps} actions={[{ label: 'Create Item', onClick: handleClick }]} />,
    );

    const button = screen.getByRole('button', { name: /create item/i });
    await user.click(button);
    expect(handleClick).toHaveBeenCalled();
  });

  it('renders help text', () => {
    render(<EmptyState {...defaultProps} helpText='Use keyboard shortcut Cmd+K to create' />);
    expect(screen.getByText(/keyboard shortcut/i)).toBeInTheDocument();
  });

  it('renders with different variants', () => {
    const { container } = render(<EmptyState {...defaultProps} variant='compact' />);
    expect(container.querySelector('div')).toBeInTheDocument();
  });
});

describe(NoItemsEmptyState, () => {
  it('renders with custom item type', () => {
    render(<NoItemsEmptyState itemType='requirements' />);
    expect(screen.getByText('No requirements yet')).toBeInTheDocument();
  });
});

describe(NoSearchResultsEmptyState, () => {
  it('renders with search query', () => {
    render(<NoSearchResultsEmptyState query='test' />);
    expect(screen.getByText('No results found')).toBeInTheDocument();
    expect(screen.getByText(/couldn't find any matches for "test"/i)).toBeInTheDocument();
  });
});

describe(FilteredEmptyState, () => {
  it('renders with applied filters', () => {
    render(<FilteredEmptyState filters={['Priority: High']} />);
    expect(screen.getByText('No items match your filters')).toBeInTheDocument();
  });
});

describe(ErrorEmptyState, () => {
  it('renders error message', () => {
    render(<ErrorEmptyState description='Network error' error='Network error' />);
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Network error')).toBeInTheDocument();
  });
});
