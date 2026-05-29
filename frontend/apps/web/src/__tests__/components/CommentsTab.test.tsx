/**
 * CommentsTab – live API integration tests (Closes #225)
 *
 * Mocks commentsApi at the module boundary so no real HTTP requests are made.
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { CommentResponse } from '../../api/endpoints';
import { CommentsTab } from '../../views/details/tabs/CommentsTab';

// ---------------------------------------------------------------------------
// Module-level mock for commentsApi
// ---------------------------------------------------------------------------
vi.mock('../../api/endpoints', () => ({
  commentsApi: {
    list: vi.fn(),
    create: vi.fn(),
    delete: vi.fn(),
  },
}));

// Import the mock AFTER the mock declaration so vi.mock hoisting works
import { commentsApi } from '../../api/endpoints';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const mockItem = {
  id: 'item-123',
  projectId: 'proj-1',
  view: 'feature' as const,
  type: 'requirement',
  title: 'Test Item',
  status: 'todo' as const,
  priority: 'medium' as const,
  version: 1,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

const makeComment = (overrides: Partial<CommentResponse> = {}): CommentResponse => ({
  id: 'c-1',
  item_id: 'item-123',
  author_id: 'user-1',
  author: 'Alice',
  content: 'Hello world',
  edited: false,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  ...overrides,
});

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('CommentsTab', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading spinner initially', async () => {
    // list never resolves during this test
    vi.mocked(commentsApi.list).mockReturnValue(new Promise(() => {}));

    render(<CommentsTab item={mockItem} />);
    expect(screen.getByText(/loading comments/i)).toBeInTheDocument();
  });

  it('shows empty state when no comments exist', async () => {
    vi.mocked(commentsApi.list).mockResolvedValue([]);

    render(<CommentsTab item={mockItem} />);
    await waitFor(() => {
      expect(screen.getByText(/no comments yet/i)).toBeInTheDocument();
    });
  });

  it('renders fetched comments', async () => {
    vi.mocked(commentsApi.list).mockResolvedValue([makeComment({ author: 'Bob', content: 'Nice!' })]);

    render(<CommentsTab item={mockItem} />);
    await waitFor(() => {
      expect(screen.getByText('Nice!')).toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument();
    });
  });

  it('shows error state when fetch fails', async () => {
    vi.mocked(commentsApi.list).mockRejectedValue(new Error('Network error'));

    render(<CommentsTab item={mockItem} />);
    await waitFor(() => {
      expect(screen.getByText(/failed to load comments/i)).toBeInTheDocument();
    });
  });

  it('submits a new comment and appends it to the list', async () => {
    const created = makeComment({ id: 'c-new', content: 'My new comment', author: 'Alice' });

    vi.mocked(commentsApi.list).mockResolvedValue([]);
    vi.mocked(commentsApi.create).mockResolvedValue(created);

    render(<CommentsTab item={mockItem} />);
    // Wait for initial load
    await waitFor(() => expect(screen.getByText(/no comments yet/i)).toBeInTheDocument());

    const textarea = screen.getByRole('textbox', { name: /new comment/i });
    fireEvent.change(textarea, { target: { value: 'My new comment' } });

    const submitBtn = screen.getByRole('button', { name: /submit comment/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(commentsApi.create).toHaveBeenCalledWith('item-123', 'My new comment');
      expect(screen.getByText('My new comment')).toBeInTheDocument();
    });
  });

  it('disables submit button when textarea is empty', async () => {
    vi.mocked(commentsApi.list).mockResolvedValue([]);

    render(<CommentsTab item={mockItem} />);
    await waitFor(() => expect(screen.getByText(/no comments yet/i)).toBeInTheDocument());

    const submitBtn = screen.getByRole('button', { name: /submit comment/i });
    expect(submitBtn).toBeDisabled();
  });
});
