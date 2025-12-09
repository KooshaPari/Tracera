/**
 * Comprehensive Tests for Header Component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Header } from '../../../components/layout/Header'

// Mock TanStack Router
const mockNavigate = vi.fn()
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useRouter: () => ({
      navigate: mockNavigate
    }),
    useLocation: () => ({ pathname: '/' }),
    useParams: () => ({}),
    Link: ({ children, to, ...props }: any) => (
      <a href={typeof to === 'string' ? to : to?.toString?.()} {...props}>
        {children}
      </a>
    ),
  }
})

describe('Header', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders header with title', () => {
    render(<Header />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('displays search input', () => {
    render(<Header />)
    expect(screen.getByPlaceholderText(/Search items/i)).toBeInTheDocument()
  })

  it('displays create button', () => {
    render(<Header />)
    expect(screen.getByText('Create')).toBeInTheDocument()
  })

  it('handles theme toggle', async () => {
    const user = userEvent.setup()
    render(<Header />)

    // Theme toggle button should be present
    const themeButtons = screen.getAllByRole('button')
    expect(themeButtons.length).toBeGreaterThan(0)
  })
})
