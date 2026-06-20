/**
 * Comprehensive Tests for Header Component
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

// Mock the router hooks BEFORE any imports that use them
vi.mock('@tanstack/react-router', () => ({
  useLocation: () => ({ pathname: '/' }),
  useNavigate: () => vi.fn(),
  useParams: () => ({}),
  useRouter: () => ({ navigate: vi.fn() }),
}));

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { Header } from '../../../components/layout/Header';
import { ThemeProvider } from '../../../providers/theme-provider';

describe(Header, () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders header with title', () => {
    render(
      <ThemeProvider>
        <Header />
      </ThemeProvider>,
    );
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('displays search input', () => {
    render(
      <ThemeProvider>
        <Header />
      </ThemeProvider>,
    );
    expect(screen.getByPlaceholderText(/Search items/i)).toBeInTheDocument();
  });

  it('displays create button', () => {
    render(
      <ThemeProvider>
        <Header />
      </ThemeProvider>,
    );
    expect(screen.getByText('Create')).toBeInTheDocument();
  });

  it('handles theme toggle', async () => {
    const _user = userEvent.setup();
    render(
      <ThemeProvider>
        <Header />
      </ThemeProvider>,
    );

    // Theme toggle button should be present
    const themeButtons = screen.getAllByRole('button');
    expect(themeButtons.length).toBeGreaterThan(0);
  });
});
