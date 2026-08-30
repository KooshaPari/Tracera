import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ProjectDetail } from '@/pages/projects/ProjectDetail';

vi.mock('@/hooks/useRealtime', () => ({ useRealtimeUpdates: vi.fn() }));
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual<typeof import('@tanstack/react-router')>('@tanstack/react-router');
  return { ...actual, useParams: () => ({ projectId: 'proj-123' }), Outlet: () => null };
});

describe('ProjectDetail page shell', () => {
  it('renders project identity and product context', () => {
    render(<ProjectDetail />);
    expect(screen.getByRole('heading', { name: /Project:/i })).toBeInTheDocument();
    expect(screen.getByText(/TraceRTM Frontend/i)).toBeInTheDocument();
  });
});
