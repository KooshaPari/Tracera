/**
 * Tests for CommunityControls component
 */

import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import type { CommunityResult } from '../../../lib/graph/clustering';

import { CommunityControls } from '../../../components/graph/CommunityControls';

describe(CommunityControls, () => {
  const mockResult: CommunityResult = {
    colors: new Map([
      ['0', '#3B82F6'],
      ['1', '#10B981'],
      ['2', '#F59E0B'],
    ]),
    communities: new Map([
      ['node1', '0'],
      ['node2', '0'],
      ['node3', '1'],
      ['node4', '1'],
      ['node5', '2'],
    ]),
    performance: {
      clusteringTimeMs: 15.5,
      edgeCount: 4,
      nodeCount: 5,
    },
    stats: {
      avgCommunitySize: 1.67,
      communityCount: 3,
      communitySizes: new Map([
        ['0', 2],
        ['1', 2],
        ['2', 1],
      ]),
      maxCommunitySize: 2,
      minCommunitySize: 1,
      modularity: 0.42,
    },
  };

  it('should render the component', () => {
    const onToggle = vi.fn();

    render(<CommunityControls enabled={false} onToggle={onToggle} />);

    expect(screen.getByText('Community Detection')).toBeInTheDocument();
    expect(screen.getByLabelText('Toggle community detection')).toBeInTheDocument();
  });

  it('should call onToggle when toggle button is clicked', async () => {
    const onToggle = vi.fn();

    render(<CommunityControls enabled={false} onToggle={onToggle} />);

    const toggle = screen.getByRole('switch');
    toggle.click();

    expect(onToggle).toHaveBeenCalledWith(true);
  });

  it('should show loading state', () => {
    const onToggle = vi.fn();

    render(<CommunityControls enabled onToggle={onToggle} isLoading />);

    expect(screen.getByText('Computing communities...')).toBeInTheDocument();
  });

  it('should display community results when enabled', () => {
    const onToggle = vi.fn();

    render(<CommunityControls enabled onToggle={onToggle} result={mockResult} />);

    // Should show community count
    expect(screen.getByText(/Communities:/)).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();

    // Should show modularity
    expect(screen.getByText(/Modularity:/)).toBeInTheDocument();
    expect(screen.getByText('0.420')).toBeInTheDocument();

    // Should show computation time
    expect(screen.getByText(/Computed in 16ms/)).toBeInTheDocument();
  });

  it('should display community legend', () => {
    const onToggle = vi.fn();

    render(<CommunityControls enabled onToggle={onToggle} result={mockResult} />);

    // Should show communities section
    expect(screen.getByText(/Communities/)).toBeInTheDocument();

    // Should show community items
    expect(screen.getByText('Community 0')).toBeInTheDocument();
    expect(screen.getByText('Community 1')).toBeInTheDocument();
    expect(screen.getByText('Community 2')).toBeInTheDocument();

    // Should show sizes
    const sizes = screen.getAllByText('2');
    expect(sizes.length).toBeGreaterThanOrEqual(2); // Two communities with size 2
  });

  it('should show export buttons when enabled with results', () => {
    const onToggle = vi.fn();

    render(<CommunityControls enabled onToggle={onToggle} result={mockResult} />);

    expect(screen.getByLabelText('Export communities as JSON')).toBeInTheDocument();
    expect(screen.getByLabelText('Export communities as CSV')).toBeInTheDocument();
  });

  it('should trigger JSON export when button is clicked', async () => {
    const onToggle = vi.fn();

    // Mock URL.createObjectURL and createElement
    const mockCreateObjectURL = vi.fn(() => 'blob:mock-url');
    const mockRevokeObjectURL = vi.fn();
    globalThis.URL.createObjectURL = mockCreateObjectURL;
    globalThis.URL.revokeObjectURL = mockRevokeObjectURL;

    const mockLink = {
      click: vi.fn(),
      download: '',
      href: '',
    };
    const mockAppendChild = vi.fn();
    const mockRemoveChild = vi.fn();
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
    vi.spyOn(document.body, 'appendChild').mockImplementation(mockAppendChild);
    vi.spyOn(document.body, 'removeChild').mockImplementation(mockRemoveChild);

    render(<CommunityControls enabled onToggle={onToggle} result={mockResult} />);

    const jsonButton = screen.getByLabelText('Export communities as JSON');
    jsonButton.click();

    expect(mockCreateObjectURL).toHaveBeenCalled();
    expect(mockLink.click).toHaveBeenCalled();
    expect(mockRevokeObjectURL).toHaveBeenCalled();
  });

  it('should trigger CSV export when button is clicked', async () => {
    const onToggle = vi.fn();

    // Mock URL.createObjectURL and createElement
    const mockCreateObjectURL = vi.fn(() => 'blob:mock-url');
    const mockRevokeObjectURL = vi.fn();
    globalThis.URL.createObjectURL = mockCreateObjectURL;
    globalThis.URL.revokeObjectURL = mockRevokeObjectURL;

    const mockLink = {
      click: vi.fn(),
      download: '',
      href: '',
    };
    const mockAppendChild = vi.fn();
    const mockRemoveChild = vi.fn();
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
    vi.spyOn(document.body, 'appendChild').mockImplementation(mockAppendChild);
    vi.spyOn(document.body, 'removeChild').mockImplementation(mockRemoveChild);

    render(<CommunityControls enabled onToggle={onToggle} result={mockResult} />);

    const csvButton = screen.getByLabelText('Export communities as CSV');
    csvButton.click();

    expect(mockCreateObjectURL).toHaveBeenCalled();
    expect(mockLink.click).toHaveBeenCalled();
    expect(mockRevokeObjectURL).toHaveBeenCalled();
  });

  it('should call onClose when close button is clicked', async () => {
    const onToggle = vi.fn();
    const onClose = vi.fn();

    render(<CommunityControls enabled={false} onToggle={onToggle} onClose={onClose} />);

    const closeButton = screen.getByLabelText('Close community controls');
    closeButton.click();

    expect(onClose).toHaveBeenCalled();
  });

  it('should show no results message when enabled but no data', () => {
    const onToggle = vi.fn();

    render(<CommunityControls enabled onToggle={onToggle} />);

    expect(screen.getByText('No community data available')).toBeInTheDocument();
  });

  it('should disable toggle when loading', () => {
    const onToggle = vi.fn();

    render(<CommunityControls enabled onToggle={onToggle} isLoading />);

    const toggle = screen.getByRole('switch');
    expect(toggle).toBeDisabled();
  });

  it('should have proper ARIA labels', () => {
    const onToggle = vi.fn();

    render(<CommunityControls enabled={false} onToggle={onToggle} result={mockResult} />);

    expect(
      screen.getByRole('region', { name: 'Community detection controls' }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText('Toggle community detection')).toBeInTheDocument();
  });

  it('should limit legend display to top 12 communities', () => {
    const largeCommunities = new Map<string, number>();
    const largeColors = new Map<string, string>();

    for (let i = 0; i < 20; i++) {
      largeCommunities.set(`comm${i}`, i + 1);
      largeColors.set(`comm${i}`, `#${Math.floor(Math.random() * 16_777_215).toString(16)}`);
    }

    const largeResult: CommunityResult = {
      colors: largeColors,
      communities: new Map(),
      performance: {
        clusteringTimeMs: 50,
        edgeCount: 400,
        nodeCount: 210,
      },
      stats: {
        avgCommunitySize: 10.5,
        communityCount: 20,
        communitySizes: largeCommunities,
        maxCommunitySize: 20,
        minCommunitySize: 1,
      },
    };

    const onToggle = vi.fn();

    render(<CommunityControls enabled onToggle={onToggle} result={largeResult} />);

    // Should show (top 12) label
    expect(screen.getByText('(top 12)')).toBeInTheDocument();
  });
});
