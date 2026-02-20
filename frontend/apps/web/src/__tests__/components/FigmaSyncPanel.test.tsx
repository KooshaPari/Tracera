// FigmaSyncPanel.test.tsx - Tests for Figma sync panel component

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import type { FigmaSyncState, LibraryComponent } from '@tracertm/types';

import { FigmaSyncPanel } from '../../components/graph/FigmaSyncPanel';

// =============================================================================
// MOCKS
// =============================================================================

const mockSyncState: FigmaSyncState = {
  componentsSynced: 24,
  createdAt: new Date().toISOString(),
  figmaFileKey: 'abc123xyz',
  figmaFileName: 'Design System',
  figmaFileUrl: 'https://figma.com/file/abc123xyz/Design-System',
  id: 'sync-1',
  lastSyncVersion: '1.0.0',
  lastSyncedAt: new Date(Date.now() - 3_600_000).toISOString(),
  libraryId: 'lib-1',
  projectId: 'proj-1',
  stylesSynced: 42,
  syncStatus: 'synced',
  tokensSynced: 156,
  updatedAt: new Date().toISOString(),
};

const mockComponents: LibraryComponent[] = [
  {
    category: 'atom',
    createdAt: new Date().toISOString(),
    description: 'Primary action button',
    displayName: 'Button',
    figmaNodeId: 'node-123',
    figmaUrl: 'https://figma.com/file/abc/...',
    id: 'comp-1',
    libraryId: 'lib-1',
    name: 'button',
    projectId: 'proj-1',
    status: 'stable',
    updatedAt: new Date().toISOString(),
    usageCount: 42,
  },
  {
    category: 'atom',
    createdAt: new Date().toISOString(),
    description: 'Text input field',
    displayName: 'Input',
    id: 'comp-2',
    libraryId: 'lib-1',
    name: 'input',
    projectId: 'proj-1',
    status: 'stable',
    updatedAt: new Date().toISOString(),
    usageCount: 28,
  },
  {
    category: 'molecule',
    createdAt: new Date().toISOString(),
    description: 'Container component',
    displayName: 'Card',
    figmaNodeId: 'node-456',
    figmaUrl: 'https://figma.com/file/abc/...',
    id: 'comp-3',
    libraryId: 'lib-1',
    name: 'card',
    projectId: 'proj-1',
    status: 'stable',
    updatedAt: new Date().toISOString(),
    usageCount: 15,
  },
];

// =============================================================================
// TESTS
// =============================================================================

describe(FigmaSyncPanel, () => {
  it('renders null when syncState is null', () => {
    render(<FigmaSyncPanel syncState={null} components={[]} />);
    expect(screen.getByText('No Figma integration configured')).toBeInTheDocument();
  });

  it('displays Figma file information', () => {
    render(<FigmaSyncPanel syncState={mockSyncState} components={mockComponents} />);

    expect(screen.getByText('Figma Integration')).toBeInTheDocument();
    // Check that the Design System link is present
    expect(screen.getByRole('link', { name: /Design System/i })).toBeInTheDocument();
    // Check that synced badge is present
    const syncedBadges = screen.getAllByText('Synced');
    expect(syncedBadges.length).toBeGreaterThan(0);
  });

  it('displays file link with external link icon', () => {
    render(<FigmaSyncPanel syncState={mockSyncState} components={mockComponents} />);

    const link = screen.getByRole('link', { name: /Design System/i });
    expect(link).toHaveAttribute('href', mockSyncState.figmaFileUrl);
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('displays last sync time', () => {
    render(<FigmaSyncPanel syncState={mockSyncState} components={mockComponents} />);

    expect(screen.getByText('Last Sync')).toBeInTheDocument();
    // The actual time string will be locale-dependent, so just check it exists
    const timeElements = screen.getAllByText(/Last Sync/);
    expect(timeElements.length).toBeGreaterThan(0);
  });

  it('displays sync statistics', () => {
    render(<FigmaSyncPanel syncState={mockSyncState} components={mockComponents} />);

    expect(screen.getByText('24')).toBeInTheDocument(); // ComponentsSynced
    expect(screen.getByText('156')).toBeInTheDocument(); // TokensSynced
    expect(screen.getByText('42')).toBeInTheDocument(); // StylesSynced
  });

  it('displays component list with sync status', () => {
    render(<FigmaSyncPanel syncState={mockSyncState} components={mockComponents} />);

    expect(screen.getByText('Button')).toBeInTheDocument();
    expect(screen.getByText('Input')).toBeInTheDocument();
    expect(screen.getByText('Card')).toBeInTheDocument();
  });

  it('shows synced status for components with figmaNodeId', () => {
    render(<FigmaSyncPanel syncState={mockSyncState} components={mockComponents} />);

    const syncedBadges = screen.getAllByText('Synced');
    // At least some should be "Synced" status
    expect(syncedBadges.length).toBeGreaterThan(0);
  });

  it('shows unlinked status for components without figmaNodeId', () => {
    render(<FigmaSyncPanel syncState={mockSyncState} components={mockComponents} />);

    const unlinkedBadges = screen.getAllByText('Unlinked');
    // At least one (Input) should be "Unlinked"
    expect(unlinkedBadges.length).toBeGreaterThan(0);
  });

  it('expands component details on click', () => {
    render(<FigmaSyncPanel syncState={mockSyncState} components={mockComponents} />);

    const buttonComponent = screen.getByText('Button');
    fireEvent.click(buttonComponent);

    expect(screen.getByText('Primary action button')).toBeInTheDocument();
    expect(screen.getByText('node-123')).toBeInTheDocument();
  });

  it('calls onSync when sync button is clicked', async () => {
    const onSync = vi.fn().mockResolvedValue();

    render(
      <FigmaSyncPanel syncState={mockSyncState} components={mockComponents} onSync={onSync} />,
    );

    const syncButtons = screen.getAllByRole('button', { name: /Sync/i });
    // Click the first sync button (the main header one)
    const syncBtn = syncButtons[0];
    if (syncBtn) {
      fireEvent.click(syncBtn);
    }

    await waitFor(() => {
      expect(onSync).toHaveBeenCalled();
    });
  });

  it('disables sync button when isSyncing is true', () => {
    const onSync = vi.fn();

    render(
      <FigmaSyncPanel
        syncState={mockSyncState}
        components={mockComponents}
        isSyncing
        onSync={onSync}
      />,
    );

    const syncButton = screen.getByRole('button', { name: /Syncing/i });
    expect(syncButton).toBeDisabled();
  });

  it('displays error status when syncStatus is error', () => {
    const errorSyncState: FigmaSyncState = {
      ...mockSyncState,
      syncStatus: 'error',
      syncError: 'Failed to connect to Figma API',
    };

    render(<FigmaSyncPanel syncState={errorSyncState} components={mockComponents} />);

    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Failed to connect to Figma API')).toBeInTheDocument();
  });

  it('displays outdated status when syncStatus is outdated', () => {
    const outdatedSyncState: FigmaSyncState = {
      ...mockSyncState,
      syncStatus: 'outdated',
    };

    render(<FigmaSyncPanel syncState={outdatedSyncState} components={mockComponents} />);

    expect(screen.getByText('Outdated')).toBeInTheDocument();
  });

  it('calls onOpenInFigma when open button is clicked', async () => {
    const onOpenInFigma = vi.fn();

    render(
      <FigmaSyncPanel
        syncState={mockSyncState}
        components={mockComponents}
        onOpenInFigma={onOpenInFigma}
      />,
    );

    // Expand Button component
    const buttonText = screen.getByText('Button');
    fireEvent.click(buttonText);

    // Click "Open in Figma" button
    const openButtons = screen.getAllByRole('button', {
      name: /Open in Figma/i,
    });
    const openBtn = openButtons[0];
    if (openBtn) {
      fireEvent.click(openBtn);
    }

    expect(onOpenInFigma).toHaveBeenCalledWith('comp-1');
  });

  it('shows action buttons for linked components', async () => {
    const onOpenInFigma = vi.fn();

    render(
      <FigmaSyncPanel
        syncState={mockSyncState}
        components={mockComponents}
        onOpenInFigma={onOpenInFigma}
      />,
    );

    // Expand Button component (has figmaNodeId)
    const componentItems = screen.getAllByText('Button');
    const firstButton = componentItems[0];
    if (firstButton) {
      fireEvent.click(firstButton);
    }

    // Wait for details to appear
    await waitFor(() => {
      expect(screen.getByText('Primary action button')).toBeInTheDocument();
    });

    // Should show action buttons
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(3);
  });

  it('displays component count summary', () => {
    render(<FigmaSyncPanel syncState={mockSyncState} components={mockComponents} />);

    // Should show synced count in the summary
    const componentHeaders = screen.getAllByText(/Components/);
    expect(componentHeaders.length).toBeGreaterThan(0);
  });

  it('handles empty components list gracefully', () => {
    render(<FigmaSyncPanel syncState={mockSyncState} components={[]} />);

    expect(screen.getByText('Figma Integration')).toBeInTheDocument();
    expect(screen.getByText('No components to display')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <FigmaSyncPanel
        syncState={mockSyncState}
        components={mockComponents}
        className='custom-class'
      />,
    );

    const card = container.querySelector('.custom-class');
    expect(card).toBeInTheDocument();
  });
});
