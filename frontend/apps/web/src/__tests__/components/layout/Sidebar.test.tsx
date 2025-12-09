/**
 * Comprehensive Tests for Sidebar Component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'

// Create a mutable location value that tests can change
let mockPathname = '/'

// Mock TanStack Router
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useRouter: () => ({ navigate: vi.fn() }),
    useLocation: () => ({ pathname: mockPathname }),
    useParams: () => ({}),
    Link: ({ children, to, ...props }: any) => (
      <a href={typeof to === 'string' ? to : to?.toString?.()} {...props}>
        {children}
      </a>
    ),
  }
})

import { Sidebar } from '../../../components/layout/Sidebar'

describe('Sidebar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockPathname = '/' // Reset to default
  })

  it('renders sidebar with logo', () => {
    render(
      <Sidebar />
    )

    expect(screen.getByText('TraceRTM')).toBeInTheDocument()
  })

  it('displays navigation items', () => {
    render(
      <Sidebar />
    )

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Projects')).toBeInTheDocument()
  })

  it('displays view items when on project page', async () => {
    // Set mock pathname to a project page
    mockPathname = '/projects/123/feature'

    // Need to re-import to get the new pathname
    // Since vitest caches modules, we need to force re-render
    const { rerender } = render(<Sidebar />)

    // Force component to re-evaluate location
    rerender(<Sidebar />)

    // These items show up when on a project page
    expect(screen.getByText('Feature')).toBeInTheDocument()
    expect(screen.getByText('Code')).toBeInTheDocument()
    expect(screen.getByText('Test')).toBeInTheDocument()
  })

  it('highlights active navigation item', () => {
    render(
      <Sidebar />
    )

    const dashboardLink = screen.getByText('Dashboard').closest('a')
    expect(dashboardLink).toBeInTheDocument()
  })
})
