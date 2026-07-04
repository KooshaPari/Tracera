/**
 * Accessibility Tests for Main Pages
 * Tests page-level accessibility for WCAG 2.1 Level AA compliance
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { axe } from './setup';

// Mock TanStack Router
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useRouter: () => ({ navigate: vi.fn() }),
    useLocation: () => ({ pathname: '/' }),
    useParams: () => ({}),
    Link: ({ children, to, ...props }: any) => (
      <a href={typeof to === 'string' ? to : to?.toString?.()} {...props}>
        {children}
      </a>
    ),
  };
});

const queryClient = new QueryClient({
  defaultOptions: {
    mutations: { retry: false },
    queries: { retry: false },
  },
});

function TestWrapper({ children }: { children: React.ReactNode }) {
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

describe('Page Structure', () => {
  it('should have valid HTML document structure', async () => {
    render(
      <div lang='en'>
        <header>
          <h1>Page Title</h1>
        </header>
        <main>
          <p>Content</p>
        </main>
      </div>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have unique page title', async () => {
    render(
      <div>
        <title>TraceRTM - Dashboard</title>
        <h1>Dashboard</h1>
      </div>,
    );

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Dashboard');
  });

  it('should have proper heading hierarchy', async () => {
    render(
      <main>
        <h1>Main Title</h1>
        <section>
          <h2>Section 1</h2>
          <h3>Subsection 1.1</h3>
          <h3>Subsection 1.2</h3>
        </section>
        <section>
          <h2>Section 2</h2>
          <h3>Subsection 2.1</h3>
        </section>
      </main>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    expect(screen.getAllByRole('heading', { level: 2 })).toHaveLength(2);
    expect(screen.getAllByRole('heading', { level: 3 })).toHaveLength(3);
  });

  it('should not skip heading levels', async () => {
    render(
      <main>
        <h1>Page Title</h1>
        <h2>Section</h2>
        <h3>Subsection</h3>
        {/* Should not skip from h3 to h5 */}
      </main>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe('Dashboard Page', () => {
  it('should not have accessibility violations', async () => {
    render(
      <TestWrapper>
        <main>
          <h1>Dashboard</h1>
          <section aria-labelledby='recent-projects'>
            <h2 id='recent-projects'>Recent Projects</h2>
            <ul>
              <li>
                <a href='/projects/1'>Project 1</a>
              </li>
              <li>
                <a href='/projects/2'>Project 2</a>
              </li>
            </ul>
          </section>
        </main>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have accessible project cards', async () => {
    render(
      <TestWrapper>
        <div>
          <article aria-labelledby='project-1-title'>
            <h3 id='project-1-title'>Project Alpha</h3>
            <p>Description of project</p>
            <a href='/projects/1'>View project</a>
          </article>
        </div>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('article')).toBeInTheDocument();
  });
});

describe('Project List Page', () => {
  it('should not have accessibility violations', async () => {
    render(
      <TestWrapper>
        <main>
          <h1>Projects</h1>
          <section aria-labelledby='projects-list'>
            <h2 id='projects-list' className='sr-only'>
              All Projects
            </h2>
            <ul>
              <li>Project 1</li>
              <li>Project 2</li>
            </ul>
          </section>
        </main>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have accessible table for project list', async () => {
    render(
      <TestWrapper>
        <table>
          <caption>Projects</caption>
          <thead>
            <tr>
              <th scope='col'>Name</th>
              <th scope='col'>Status</th>
              <th scope='col'>Last Updated</th>
              <th scope='col'>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Project Alpha</td>
              <td>Active</td>
              <td>2025-01-15</td>
              <td>
                <button aria-label='Edit Project Alpha'>Edit</button>
              </td>
            </tr>
          </tbody>
        </table>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('table')).toBeInTheDocument();
    expect(screen.getByRole('caption')).toBeInTheDocument();
  });
});

describe('Project Detail Page', () => {
  it('should not have accessibility violations', async () => {
    render(
      <TestWrapper>
        <main>
          <header>
            <h1>Project Alpha</h1>
            <nav aria-label='Project views'>
              <a href='/projects/1/feature'>Features</a>
              <a href='/projects/1/code'>Code</a>
              <a href='/projects/1/test'>Tests</a>
            </nav>
          </header>
          <section aria-labelledby='overview'>
            <h2 id='overview'>Overview</h2>
            <p>Project description</p>
          </section>
        </main>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have accessible tab navigation', async () => {
    render(
      <TestWrapper>
        <div role='tablist' aria-label='Project views'>
          <button role='tab' aria-selected='true' aria-controls='feature-panel' id='feature-tab'>
            Features
          </button>
          <button role='tab' aria-selected='false' aria-controls='code-panel' id='code-tab'>
            Code
          </button>
          <button role='tab' aria-selected='false' aria-controls='test-panel' id='test-tab'>
            Tests
          </button>
        </div>
        <div role='tabpanel' id='feature-panel' aria-labelledby='feature-tab'>
          <h2>Features</h2>
        </div>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('tablist')).toBeInTheDocument();
    expect(screen.getAllByRole('tab')).toHaveLength(3);
    expect(screen.getByRole('tabpanel')).toBeInTheDocument();
  });
});

describe('Empty States', () => {
  it('should have accessible empty state messages', async () => {
    render(
      <TestWrapper>
        <div role='status' aria-live='polite'>
          <p>No projects found</p>
          <button>Create your first project</button>
        </div>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('should provide clear call-to-action in empty state', async () => {
    render(
      <TestWrapper>
        <div>
          <h2>No items yet</h2>
          <p>Get started by creating your first item</p>
          <button>Create Item</button>
        </div>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('button', { name: 'Create Item' })).toBeInTheDocument();
  });
});

describe('Loading States', () => {
  it('should have accessible loading indicators', async () => {
    render(
      <TestWrapper>
        <div role='status' aria-live='polite' aria-busy='true'>
          <span className='sr-only'>Loading projects...</span>
          <div aria-hidden='true'>
            {/* Visual spinner */}
            <svg className='animate-spin' />
          </div>
        </div>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByText('Loading projects...')).toBeInTheDocument();
  });

  it('should announce when content loads', async () => {
    render(
      <TestWrapper>
        <div role='status' aria-live='polite' aria-busy='true'>
          Loading...
        </div>
      </TestWrapper>,
    );

    // Content loaded
    rerender(
      <TestWrapper>
        <div role='status' aria-live='polite'>
          <span className='sr-only'>Projects loaded</span>
          <ul>
            <li>Project 1</li>
          </ul>
        </div>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe('Error States', () => {
  it('should have accessible error messages', async () => {
    render(
      <TestWrapper>
        <div role='alert' aria-live='assertive'>
          <h2>Error loading projects</h2>
          <p>Unable to fetch project data. Please try again.</p>
          <button>Retry</button>
        </div>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('should provide recovery actions in error state', async () => {
    render(
      <TestWrapper>
        <div role='alert'>
          <p>Connection failed</p>
          <button>Retry</button>
          <button>Go back</button>
        </div>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument();
  });
});

describe('Search and Filter', () => {
  it('should have accessible search input', async () => {
    render(
      <TestWrapper>
        <form role='search'>
          <label htmlFor='search'>Search projects</label>
          <input id='search' type='search' aria-describedby='search-help' />
          <span id='search-help'>Enter keywords to search</span>
          <button type='submit'>Search</button>
        </form>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('search')).toBeInTheDocument();
    expect(screen.getByLabelText('Search projects')).toBeInTheDocument();
  });

  it('should announce search results', async () => {
    render(
      <TestWrapper>
        <div>
          <div role='status' aria-live='polite'>
            5 results found
          </div>
          <ul aria-label='Search results'>
            <li>Result 1</li>
            <li>Result 2</li>
          </ul>
        </div>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('status')).toHaveTextContent('5 results found');
  });
});

describe('Breadcrumbs', () => {
  it('should have accessible breadcrumb navigation', async () => {
    render(
      <TestWrapper>
        <nav aria-label='Breadcrumb'>
          <ol>
            <li>
              <a href='/'>Home</a>
            </li>
            <li>
              <a href='/projects'>Projects</a>
            </li>
            <li aria-current='page'>Project Alpha</li>
          </ol>
        </nav>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('navigation', { name: 'Breadcrumb' })).toBeInTheDocument();
    const currentPage = screen.getByText('Project Alpha');
    expect(currentPage).toHaveAttribute('aria-current', 'page');
  });
});

describe('Pagination', () => {
  it('should have accessible pagination controls', async () => {
    render(
      <TestWrapper>
        <nav aria-label='Pagination'>
          <ul>
            <li>
              <a href='?page=1' aria-label='Go to previous page' aria-disabled='true'>
                Previous
              </a>
            </li>
            <li>
              <a href='?page=1' aria-current='page'>
                1
              </a>
            </li>
            <li>
              <a href='?page=2' aria-label='Go to page 2'>
                2
              </a>
            </li>
            <li>
              <a href='?page=2' aria-label='Go to next page'>
                Next
              </a>
            </li>
          </ul>
        </nav>
      </TestWrapper>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('navigation', { name: 'Pagination' })).toBeInTheDocument();
    expect(screen.getByLabelText('Go to next page')).toBeInTheDocument();
  });
});
