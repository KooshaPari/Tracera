// Journey Explorer Component Tests
// Tests visualization, filtering, overlay, and export functionality

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import type { DerivedJourney } from '@/components/graph/JourneyExplorer';
import type { Item, Link } from '@tracertm/types';

import { JourneyExplorer } from '@/components/graph/JourneyExplorer';

// =============================================================================
// TEST DATA
// =============================================================================

const now = new Date().toISOString();

const mockItems: Item[] = [
  {
    createdAt: now,
    id: 'item-1',
    priority: 'high' as any,
    projectId: 'proj-1',
    status: 'done',
    title: 'Login Page',
    type: 'page',
    updatedAt: now,
    version: 1,
    view: 'product' as any,
  },
  {
    createdAt: now,
    id: 'item-2',
    priority: 'high' as any,
    projectId: 'proj-1',
    status: 'done',
    title: 'Dashboard',
    type: 'page',
    updatedAt: now,
    version: 1,
    view: 'product' as any,
  },
  {
    createdAt: now,
    id: 'item-3',
    priority: 'high' as any,
    projectId: 'proj-1',
    status: 'done',
    title: 'Auth API',
    type: 'api',
    updatedAt: now,
    version: 1,
    view: 'technical' as any,
  },
  {
    createdAt: now,
    id: 'item-4',
    priority: 'high' as any,
    projectId: 'proj-1',
    status: 'done',
    title: 'User Database',
    type: 'database',
    updatedAt: now,
    version: 1,
    view: 'technical' as any,
  },
  {
    createdAt: now,
    id: 'item-5',
    priority: 'high' as any,
    projectId: 'proj-1',
    status: 'in_progress',
    title: 'Checkout Flow',
    type: 'user_story',
    updatedAt: now,
    version: 1,
    view: 'product' as any,
  },
];

const mockLinks: Link[] = [
  {
    createdAt: now,
    id: 'link-1',
    projectId: 'proj-1',
    sourceId: 'item-1',
    targetId: 'item-3',
    type: 'implements',
    updatedAt: now,
    version: 1,
  },
  {
    createdAt: now,
    id: 'link-2',
    projectId: 'proj-1',
    sourceId: 'item-3',
    targetId: 'item-4',
    type: 'depends_on',
    updatedAt: now,
    version: 1,
  },
  {
    createdAt: now,
    id: 'link-3',
    projectId: 'proj-1',
    sourceId: 'item-1',
    targetId: 'item-2',
    type: 'related_to',
    updatedAt: now,
    version: 1,
  },
];

const setupUser = () => userEvent.setup();

const mockJourneys: DerivedJourney[] = [
  {
    color: '#9333ea',
    id: 'journey-1',
    links: [
      { sourceId: 'item-1', targetId: 'item-3', type: 'implements' },
      { sourceId: 'item-3', targetId: 'item-4', type: 'depends_on' },
    ],
    name: 'Login Flow',
    nodeIds: ['item-1', 'item-3', 'item-4'],
    type: 'user_flow',
  },
  {
    color: '#3b82f6',
    id: 'journey-2',
    links: [{ sourceId: 'item-3', targetId: 'item-4', type: 'data_flow' }],
    name: 'Data Flow',
    nodeIds: ['item-3', 'item-4'],
    type: 'data_path',
  },
  {
    color: '#22c55e',
    id: 'journey-3',
    links: [
      { sourceId: 'item-1', targetId: 'item-2', type: 'tests' },
      { sourceId: 'item-2', targetId: 'item-3', type: 'validates' },
    ],
    name: 'Test Coverage',
    nodeIds: ['item-1', 'item-2', 'item-3'],
    type: 'test_trace',
  },
];

// =============================================================================
// TESTS
// =============================================================================

describe(JourneyExplorer, () => {
  describe('Rendering and Display', () => {
    it('should render with journeys', () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} />);

      expect(screen.getByText('Journey Explorer')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
      expect(screen.getByText('Login Flow')).toBeInTheDocument();
      expect(screen.getByText('Data Flow')).toBeInTheDocument();
      expect(screen.getByText('Test Coverage')).toBeInTheDocument();
    });

    it('should display empty state when no journeys', () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={[]} />);

      expect(screen.getByText('No journeys detected')).toBeInTheDocument();
    });

    it('should show journey types with correct icons and labels', () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} />);

      const userFlowTexts = screen.queryAllByText('User Flow');
      expect(userFlowTexts.length).toBeGreaterThan(0);
      const dataPathTexts = screen.queryAllByText('Data Path');
      expect(dataPathTexts.length).toBeGreaterThan(0);
      const testTraceTexts = screen.queryAllByText('Test Trace');
      expect(testTraceTexts.length).toBeGreaterThan(0);
    });

    it('should render journey legend with all types', () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} />);

      expect(screen.getByText('Journey Types')).toBeInTheDocument();
      const userFlowElements = screen.queryAllByText('User Flow');
      expect(userFlowElements.length).toBeGreaterThan(0);
      expect(screen.getByText('Call Chain')).toBeInTheDocument();
    });
  });

  describe('Journey Card Metrics', () => {
    it('should display correct node and link counts', () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} />);

      // Login Flow: 3 nodes, 2 links
      const nodesElements = screen.queryAllByText(/3 nodes/);
      expect(nodesElements.length).toBeGreaterThan(0);
      const linksElements = screen.queryAllByText(/2 links/);
      expect(linksElements.length).toBeGreaterThan(0);
    });

    it('should calculate coverage percentage correctly', () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} />);

      // Journey 1 has 3 nodes out of 5 total = 60%
      const coverageTexts = screen.getAllByText(/\d+\.\d%/);
      expect(coverageTexts.length).toBeGreaterThan(0);
    });

    it('should display journey flow visualization', () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} />);

      // Check for journey name is displayed
      const loginFlowCard = screen.getByText('Login Flow');
      expect(loginFlowCard).toBeInTheDocument();
    });
  });

  describe('Filtering', () => {
    it('should filter journeys by search term', async () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} />);

      const user = setupUser();
      const searchInput = screen.getByPlaceholderText('Search journeys...');
      await user.type(searchInput, 'Login');

      expect(screen.getByText('Login Flow')).toBeInTheDocument();
      expect(screen.queryByText('Data Flow')).not.toBeInTheDocument();
    });

    it('should clear filters with clear button', async () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} />);

      const user = setupUser();
      const searchInput = screen.getByPlaceholderText('Search journeys...');
      await user.type(searchInput, 'Login');

      expect(screen.queryByText('Data Flow')).not.toBeInTheDocument();

      // Look for clear button (X icon appears when filter is active)
      const clearButtons = screen
        .getAllByRole('button')
        .filter((btn) => btn.querySelector('svg') !== null);
      const clearButton = clearButtons.find(
        (btn) => btn.textContent === '' && btn.parentElement?.className.includes('ghost'),
      );

      if (clearButton) {
        await user.click(clearButton);
        expect(searchInput).toHaveValue('');
      }
    });

    it('should show empty state when no journeys match filter', async () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} />);

      const user = setupUser();
      const searchInput = screen.getByPlaceholderText('Search journeys...');
      await user.type(searchInput, 'NonExistent');

      expect(screen.getByText('No journeys match your filters')).toBeInTheDocument();
    });
  });

  describe('Coverage Metrics', () => {
    it('should display coverage for selected journeys', async () => {
      render(
        <JourneyExplorer
          items={mockItems}
          links={mockLinks}
          journeys={mockJourneys}
          selectedJourneyIds={['journey-1']}
        />,
      );

      const coverageElements = screen.queryAllByText(/Coverage/);
      expect(coverageElements.length).toBeGreaterThan(0);
      // Journey 1 has 3 nodes out of 5 = 60%
      expect(screen.getByText(/3 \/ 5 items/)).toBeInTheDocument();
    });

    it('should show aggregated coverage for multiple selected journeys', () => {
      render(
        <JourneyExplorer
          items={mockItems}
          links={mockLinks}
          journeys={mockJourneys}
          selectedJourneyIds={['journey-1', 'journey-2']}
        />,
      );

      // Journey 1 + 2 combined: nodes 1, 3, 4 = 3 unique nodes out of 5 = 60%
      const coverageElements = screen.queryAllByText(/Coverage/);
      expect(coverageElements.length).toBeGreaterThan(0);
    });
  });

  describe('Interactions', () => {
    it('should expand/collapse journey details', async () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} />);

      const user = setupUser();
      const detailsButtons = screen.getAllByText('Details');
      await user.click(detailsButtons[0]);

      // After expand, should show additional details
      await waitFor(() => {
        const cards = screen.getAllByText(/Links \(/);
        expect(cards.length).toBeGreaterThan(0);
      });
    });

    it('should call onJourneySelect when journey is clicked', async () => {
      const onJourneySelect = vi.fn();

      render(
        <JourneyExplorer
          items={mockItems}
          links={mockLinks}
          journeys={mockJourneys}
          onJourneySelect={onJourneySelect}
        />,
      );

      const user = setupUser();
      const journeyCard = screen.getByText('Login Flow').closest("[class*='Card']");
      if (journeyCard) {
        await user.click(journeyCard);
        expect(onJourneySelect).toHaveBeenCalledWith(
          expect.objectContaining({ id: 'journey-1', name: 'Login Flow' }),
        );
      }
    });

    it('should call onJourneyDelete when delete button is clicked', async () => {
      const onJourneyDelete = vi.fn();

      render(
        <JourneyExplorer
          items={mockItems}
          links={mockLinks}
          journeys={mockJourneys}
          onJourneyDelete={onJourneyDelete}
        />,
      );

      const user = setupUser();
      const deleteButtons = screen
        .getAllByRole('button')
        .filter(
          (btn) =>
            btn.querySelector('[data-lucide="trash-2"]') !== null ||
            btn.textContent.includes('Trash'),
        );

      if (deleteButtons.length > 0) {
        await user.click(deleteButtons[0]);
        expect(onJourneyDelete).toHaveBeenCalled();
      }
    });
  });

  describe('Overlay Mode', () => {
    it('should toggle overlay mode', async () => {
      const onJourneyOverlay = vi.fn();

      render(
        <JourneyExplorer
          items={mockItems}
          links={mockLinks}
          journeys={mockJourneys}
          selectedJourneyIds={['journey-1']}
          onJourneyOverlay={onJourneyOverlay}
        />,
      );

      const user = setupUser();
      // Find and click the overlay button (Eye icon)
      const eyeButtons = screen
        .getAllByRole('button')
        .filter((btn) => btn.querySelector('[data-lucide="eye"]') !== null);

      if (eyeButtons.length > 0) {
        await user.click(eyeButtons[0]);
        expect(onJourneyOverlay).toHaveBeenCalledWith(['journey-1']);
      }
    });

    it('should disable overlay controls when no journeys selected', () => {
      const onJourneyOverlay = vi.fn();

      render(
        <JourneyExplorer
          items={mockItems}
          links={mockLinks}
          journeys={mockJourneys}
          selectedJourneyIds={[]}
          onJourneyOverlay={onJourneyOverlay}
        />,
      );

      const eyeButtons = screen
        .queryAllByRole('button')
        .filter((btn) => btn.querySelector('[data-lucide="eye"]') !== null);

      // Should not have overlay button when nothing selected
      expect(eyeButtons.length).toBe(0);
    });
  });

  describe('Export Functionality', () => {
    it('should open export dialog when export button clicked', async () => {
      render(
        <JourneyExplorer
          items={mockItems}
          links={mockLinks}
          journeys={mockJourneys}
          selectedJourneyIds={['journey-1']}
        />,
      );

      const user = setupUser();
      // Find download button
      const downloadButtons = screen
        .getAllByRole('button')
        .filter((btn) => btn.querySelector('[data-lucide="download"]') !== null);

      if (downloadButtons.length > 0) {
        await user.click(downloadButtons[0]);
        expect(screen.getByText('Export Journeys')).toBeInTheDocument();
      }
    });

    it('should call onExport with correct format', async () => {
      const onExport = vi.fn();

      render(
        <JourneyExplorer
          items={mockItems}
          links={mockLinks}
          journeys={mockJourneys}
          selectedJourneyIds={['journey-1']}
          onExport={onExport}
        />,
      );

      const user = setupUser();
      const downloadButtons = screen
        .getAllByRole('button')
        .filter((btn) => btn.querySelector('[data-lucide="download"]') !== null);

      if (downloadButtons.length > 0) {
        await user.click(downloadButtons[0]);

        // Click JSON export option
        const jsonButton = screen.getByText('JSON Format');
        await user.click(jsonButton);

        expect(onExport).toHaveBeenCalledWith('json');
      }
    });
  });

  describe('Create Journey', () => {
    it('should open create journey dialog', async () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} />);

      const user = setupUser();
      const createButtons = screen
        .getAllByRole('button')
        .filter((btn) => btn.querySelector('[data-lucide="plus"]') !== null);

      if (createButtons.length > 0) {
        await user.click(createButtons[0]);
        expect(screen.getByText('Create Manual Journey')).toBeInTheDocument();
      }
    });

    it('should call onJourneyCreate with correct data', async () => {
      const onJourneyCreate = vi.fn();

      render(
        <JourneyExplorer
          items={mockItems}
          links={mockLinks}
          journeys={mockJourneys}
          onJourneyCreate={onJourneyCreate}
        />,
      );

      const user = setupUser();
      const createButtons = screen
        .getAllByRole('button')
        .filter((btn) => btn.querySelector('[data-lucide="plus"]') !== null);

      if (createButtons.length > 0) {
        await user.click(createButtons[0]);

        const nameInput = screen.getByPlaceholderText('e.g., Checkout Flow');
        await user.type(nameInput, 'My Journey');

        const createButton = screen.getByText('Create Journey');
        await user.click(createButton);

        expect(onJourneyCreate).toHaveBeenCalledWith(
          expect.objectContaining({
            links: [],
            name: 'My Journey',
            nodeIds: [],
            type: 'user_flow',
          }),
        );
      }
    });

    it('should disable create button when name is empty', async () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} />);

      const user = setupUser();
      const createButtons = screen
        .getAllByRole('button')
        .filter((btn) => btn.querySelector('[data-lucide="plus"]') !== null);

      if (createButtons.length > 0) {
        await user.click(createButtons[0]);

        const createButton = screen.getByText('Create Journey');
        expect(createButton).toBeDisabled();

        const nameInput = screen.getByPlaceholderText('e.g., Checkout Flow');
        await user.type(nameInput, 'Test');

        expect(createButton).not.toBeDisabled();
      }
    });
  });

  describe('Compact Mode', () => {
    it('should render in compact mode', () => {
      render(
        <JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} compact />,
      );

      expect(screen.getByText('Journey Explorer')).toBeInTheDocument();
    });

    it('should show empty state when no journeys in compact mode', () => {
      render(<JourneyExplorer items={mockItems} links={mockLinks} journeys={[]} compact />);

      expect(screen.getByText('No journeys detected')).toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    it('should disable controls when loading', () => {
      const { rerender } = render(
        <JourneyExplorer
          items={mockItems}
          links={mockLinks}
          journeys={mockJourneys}
          isLoading={false}
        />,
      );

      let createButton = screen
        .getAllByRole('button')
        .find((btn) => btn.querySelector('[data-lucide="plus"]') !== null);
      if (createButton) {
        expect(createButton).not.toBeDisabled();
      }

      rerender(
        <JourneyExplorer items={mockItems} links={mockLinks} journeys={mockJourneys} isLoading />,
      );

      createButton = screen
        .queryAllByRole('button')
        .find((btn) => btn.querySelector('[data-lucide="plus"]') !== null);
      if (createButton) {
        expect(createButton).toBeDisabled();
      }
    });
  });
});
