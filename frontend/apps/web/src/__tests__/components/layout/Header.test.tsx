/**
 * Comprehensive Tests for Header Component
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

// Mock the router hooks BEFORE any imports that use them
vi.mock('@tanstack/react-router', () => ({
  useLocation: () => ({ pathname: '/' }),
  useMatches: () => [],
  useNavigate: () => vi.fn(),
  useParams: () => ({}),
  useRouter: () => ({ navigate: vi.fn() }),
}));

import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { Header } from '../../../components/layout/Header';
import { ThemeProvider } from '../../../providers/theme-provider';

const renderHeader = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <Header />
      </ThemeProvider>
    </QueryClientProvider>,
  );
};

describe(Header, () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders header with title', () => {
    renderHeader();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('renders as the page banner', () => {
    renderHeader();
    expect(screen.getByRole('banner')).toBeInTheDocument();
  });

  it('displays the unauthenticated sign-in action', () => {
    renderHeader();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('displays the notification status', () => {
    renderHeader();
    expect(screen.getByText('0')).toBeInTheDocument();
  });
});
