import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Create a mock search function and control the hook return
const mockSearch = vi.fn();
const mockUseSearchWorker = vi.fn().mockReturnValue({
  search: mockSearch,
  results: [],
  isReady: true,
  isSearching: false,
  error: null,
  performance: {},
});

vi.mock('../../lib/use-search-worker', () => ({
  useSearchWorker: () => mockUseSearchWorker(),
}));

vi.mock('../../lib/search-config', () => ({
  formatSearchPreview: (content: string, _query: string) => content.slice(0, 50),
}));

// Mock @tanstack/react-virtual
vi.mock('@tanstack/react-virtual', () => ({
  useVirtualizer: ({ count }: { count: number }) => ({
    getTotalSize: () => count * 80,
    getVirtualItems: () =>
      Array.from({ length: count }, (_, i) => ({
        index: i,
        key: `item-${i}`,
        start: i * 80,
        size: 80,
      })),
  }),
}));

import { InstantSearch } from '../instant-search';

describe('InstantSearch', () => {
  const mockOnClose = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [],
      isReady: true,
      isSearching: false,
      error: null,
      performance: {},
    });
  });

  it('returns null when isOpen is false', () => {
    const { container } = render(<InstantSearch isOpen={false} onClose={mockOnClose} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders search input when isOpen is true', () => {
    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    const input = screen.getByRole('textbox', { name: 'Search' });
    expect(input).toBeInTheDocument();
  });

  it('uses custom placeholder text', () => {
    render(<InstantSearch isOpen={true} onClose={mockOnClose} placeholder='Find something...' />);

    const input = screen.getByPlaceholderText('Find something...');
    expect(input).toBeInTheDocument();
  });

  it('uses default placeholder text', () => {
    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    const input = screen.getByPlaceholderText('Search documentation...');
    expect(input).toBeInTheDocument();
  });

  it('shows "Type at least 2 characters" message for short queries', () => {
    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    expect(screen.getByText('Type at least 2 characters to search')).toBeInTheDocument();
  });

  it('shows "Loading search index..." when not ready', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [],
      isReady: false,
      isSearching: false,
      error: null,
      performance: {},
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    expect(screen.getByText('Loading search index...')).toBeInTheDocument();
  });

  it('shows "Searching..." when search is in progress', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [],
      isReady: true,
      isSearching: true,
      error: null,
      performance: {},
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    expect(screen.getByText('Searching...')).toBeInTheDocument();
  });

  it('displays error message when there is an error', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [],
      isReady: true,
      isSearching: false,
      error: 'Failed to load index',
      performance: {},
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    expect(screen.getByText('Failed to load index')).toBeInTheDocument();
  });

  it('calls onClose when Escape key is pressed', () => {
    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.keyDown(input, { key: 'Escape' });

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('calls onClose when clicking the overlay', () => {
    const { container } = render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    // Click the outermost overlay div
    const overlay = container.firstChild as HTMLElement;
    fireEvent.click(overlay);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('does not close when clicking inside the dialog', () => {
    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.click(input);

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('renders search results when available', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [
        {
          item: {
            id: '1',
            url: '/docs/guide',
            title: 'Getting Started Guide',
            description: 'Learn how to get started',
            content: 'Full content here',
            headings: [],
            priority: 1,
          },
          score: 0.1,
          matches: [],
        },
      ],
      isReady: true,
      isSearching: false,
      error: null,
      performance: { searchDuration: 5.2 },
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    // Type a query to trigger search display
    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'getting started' } });

    expect(screen.getByText('Getting Started Guide')).toBeInTheDocument();
    expect(screen.getByText('/docs/guide')).toBeInTheDocument();
  });

  it('shows result count and search duration', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [
        {
          item: {
            id: '1',
            url: '/test',
            title: 'Test',
            description: '',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.5,
        },
        {
          item: {
            id: '2',
            url: '/test2',
            title: 'Test 2',
            description: '',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.6,
        },
      ],
      isReady: true,
      isSearching: false,
      error: null,
      performance: { searchDuration: 42 },
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    // Trigger search display by typing
    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'test' } });

    expect(screen.getByText('2 results')).toBeInTheDocument();
    expect(screen.getByText('42ms')).toBeInTheDocument();
  });

  it('renders keyboard shortcut hints in footer', () => {
    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    expect(screen.getByText('Navigate')).toBeInTheDocument();
    expect(screen.getByText('Select')).toBeInTheDocument();
    expect(screen.getByText('Close')).toBeInTheDocument();
    expect(screen.getByText('Powered by Fuse.js')).toBeInTheDocument();
  });

  it('has proper ARIA attributes for accessibility', () => {
    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    const input = screen.getByRole('textbox', { name: 'Search' });
    expect(input.getAttribute('aria-autocomplete')).toBe('list');
    expect(input.getAttribute('aria-controls')).toBe('search-results');

    const listbox = screen.getByRole('listbox');
    expect(listbox).toBeInTheDocument();
  });

  it('displays score for results that have a score', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [
        {
          item: {
            id: '1',
            url: '/test',
            title: 'Test',
            description: 'Desc',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.25,
          matches: [],
        },
      ],
      isReady: true,
      isSearching: false,
      error: null,
      performance: {},
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);

    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'test query' } });

    // Score display: 1 - 0.25 = 0.75, formatted to 3 decimal places
    expect(screen.getByText('Score: 0.750')).toBeInTheDocument();
  });

  it('highlights matched text in results with match indices', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [
        {
          item: {
            id: '1',
            url: '/test',
            title: 'Getting Started',
            description: 'A description',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.1,
          matches: [
            {
              key: 'title',
              indices: [[0, 6]] as [number, number][],
              value: 'Getting Started',
            },
          ],
        },
      ],
      isReady: true,
      isSearching: false,
      error: null,
      performance: {},
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);
    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'getting' } });

    // Should have a <mark> element for the highlighted text
    const marks = document.querySelectorAll('mark');
    expect(marks.length).toBeGreaterThan(0);
    expect(marks[0].textContent).toBe('Getting');
  });

  it('navigates selection down with ArrowDown key', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [
        {
          item: {
            id: '1',
            url: '/first',
            title: 'First',
            description: 'D1',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.1,
        },
        {
          item: {
            id: '2',
            url: '/second',
            title: 'Second',
            description: 'D2',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.2,
        },
      ],
      isReady: true,
      isSearching: false,
      error: null,
      performance: {},
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);
    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'test' } });

    // Initially first item is selected
    const firstOption = document.getElementById('result-0');
    expect(firstOption?.getAttribute('aria-selected')).toBe('true');

    // Press ArrowDown to move to second
    fireEvent.keyDown(input, { key: 'ArrowDown' });

    const secondOption = document.getElementById('result-1');
    expect(secondOption?.getAttribute('aria-selected')).toBe('true');
  });

  it('navigates selection up with ArrowUp key', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [
        {
          item: {
            id: '1',
            url: '/first',
            title: 'First',
            description: 'D1',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.1,
        },
        {
          item: {
            id: '2',
            url: '/second',
            title: 'Second',
            description: 'D2',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.2,
        },
      ],
      isReady: true,
      isSearching: false,
      error: null,
      performance: {},
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);
    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'test' } });

    // Move down, then back up
    fireEvent.keyDown(input, { key: 'ArrowDown' });
    fireEvent.keyDown(input, { key: 'ArrowUp' });

    const firstOption = document.getElementById('result-0');
    expect(firstOption?.getAttribute('aria-selected')).toBe('true');
  });

  it('does not go below last result with ArrowDown', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [
        {
          item: {
            id: '1',
            url: '/only',
            title: 'Only',
            description: 'D',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.1,
        },
      ],
      isReady: true,
      isSearching: false,
      error: null,
      performance: {},
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);
    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'test' } });

    // Try to go past the only result
    fireEvent.keyDown(input, { key: 'ArrowDown' });
    fireEvent.keyDown(input, { key: 'ArrowDown' });

    const option = document.getElementById('result-0');
    expect(option?.getAttribute('aria-selected')).toBe('true');
  });

  it('shows "No results found" when query has results but none returned', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [],
      isReady: true,
      isSearching: false,
      error: null,
      performance: {},
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);
    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'nonexistent query' } });

    expect(screen.getByText(/No results found/)).toBeInTheDocument();
  });

  it('shows singular "1 result" for a single result', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [
        {
          item: {
            id: '1',
            url: '/test',
            title: 'Test',
            description: 'Desc',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.1,
        },
      ],
      isReady: true,
      isSearching: false,
      error: null,
      performance: { searchDuration: 5 },
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);
    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'test' } });

    expect(screen.getByText('1 result')).toBeInTheDocument();
  });

  it('uses content preview when description is empty', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [
        {
          item: {
            id: '1',
            url: '/test',
            title: 'Test',
            description: '',
            content: 'This is the content preview text that should appear',
            headings: [],
            priority: 1,
          },
          score: 0.1,
          matches: [],
        },
      ],
      isReady: true,
      isSearching: false,
      error: null,
      performance: {},
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);
    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'test' } });

    // formatSearchPreview mock returns first 50 chars
    expect(
      screen.getByText('This is the content preview text that should appea'),
    ).toBeInTheDocument();
  });

  it('applies green color for search durations under 100ms', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [
        {
          item: {
            id: '1',
            url: '/t',
            title: 'T',
            description: 'D',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.1,
        },
      ],
      isReady: true,
      isSearching: false,
      error: null,
      performance: { searchDuration: 50 },
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);
    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'test' } });

    const durationSpan = screen.getByText('50ms');
    expect(durationSpan.className).toContain('text-green');
  });

  it('applies orange color for search durations at or above 100ms', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [
        {
          item: {
            id: '1',
            url: '/t',
            title: 'T',
            description: 'D',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.1,
        },
      ],
      isReady: true,
      isSearching: false,
      error: null,
      performance: { searchDuration: 150 },
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);
    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'test' } });

    const durationSpan = screen.getByText('150ms');
    expect(durationSpan.className).toContain('text-orange');
  });

  it('calls onClose when clicking a result', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [
        {
          item: {
            id: '1',
            url: '/docs/test',
            title: 'Test Doc',
            description: 'Desc',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.1,
          matches: [],
        },
      ],
      isReady: true,
      isSearching: false,
      error: null,
      performance: {},
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);
    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'test' } });

    // Click the result link
    const resultLink = screen.getByText('Test Doc').closest('a');
    fireEvent.click(resultLink!);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('highlights description matches when they exist', () => {
    mockUseSearchWorker.mockReturnValue({
      search: mockSearch,
      results: [
        {
          item: {
            id: '1',
            url: '/test',
            title: 'My Title',
            description: 'A helpful description',
            content: '',
            headings: [],
            priority: 1,
          },
          score: 0.1,
          matches: [
            {
              key: 'description',
              indices: [[2, 8]] as [number, number][],
              value: 'A helpful description',
            },
          ],
        },
      ],
      isReady: true,
      isSearching: false,
      error: null,
      performance: {},
    });

    render(<InstantSearch isOpen={true} onClose={mockOnClose} />);
    const input = screen.getByRole('textbox', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'helpful' } });

    const marks = document.querySelectorAll('mark');
    expect(marks.length).toBeGreaterThan(0);
  });
});
