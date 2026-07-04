/**
 * Custom test utilities and render functions
 */

import type { RenderOptions } from '@testing-library/react';
import type React from 'react';
import type { ReactElement } from 'react';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react';
import { vi } from 'vitest';

// Mock TanStack Router
const mockNavigate = vi.fn();
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router');
  return {
    ...actual,
    Link: ({
      children,
      to,
      ...props
    }: {
      children: React.ReactNode;
      to: string;
      [key: string]: unknown;
    }) => (
      <a href={typeof to === 'string' ? to : String((to as unknown) ?? '')} {...props}>
        {children}
      </a>
    ),
    useLocation: () => ({ pathname: '/' }),
    useNavigate: () => mockNavigate,
    useParams: () => ({}),
    useRouter: () => ({
      navigate: mockNavigate,
    }),
  };
});

// Create a new QueryClient for each test
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      mutations: { retry: false },
      queries: {
        gcTime: 0,
        retry: false,
        staleTime: 0,
      },
    },
  });

interface AllProvidersProps {
  children: React.ReactNode;
}

const AllProviders = ({ children }: AllProvidersProps) => {
  const queryClient = createTestQueryClient();

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
};

/**
 * Custom render function that includes all providers
 */
const customRender = (ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) =>
  render(ui, { wrapper: AllProviders, ...options });

/**
 * Create a wrapper with providers for hooks testing
 */
export const createWrapper = () => {
  const queryClient = createTestQueryClient();

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

/**
 * Wait for queries to settle
 */
export const waitForLoadingToFinish = async () => new Promise((resolve) => setTimeout(resolve, 0));

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };
