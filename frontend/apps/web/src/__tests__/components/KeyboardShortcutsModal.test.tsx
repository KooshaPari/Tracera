import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import type { KeyboardShortcut } from '@/components/KeyboardShortcutsModal';

import { KeyboardShortcutsModal } from '@/components/KeyboardShortcutsModal';

describe(KeyboardShortcutsModal, () => {
  const mockOnClose = vi.fn();

  const shortcuts: KeyboardShortcut[] = [
    {
      category: 'system',
      description: 'Open command palette',
      key: 'k',
      meta: true,
    },
    {
      category: 'editing',
      description: 'Create new item',
      key: 'n',
      meta: true,
    },
    {
      category: 'navigation',
      description: 'Search',
      key: 'f',
      meta: true,
    },
    {
      category: 'selection',
      description: 'Bulk delete',
      key: 'Delete',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('does not render when closed', () => {
    render(<KeyboardShortcutsModal isOpen={false} onClose={mockOnClose} shortcuts={shortcuts} />);

    expect(container.firstChild).toBeNull();
  });

  it('renders when open', () => {
    render(<KeyboardShortcutsModal isOpen onClose={mockOnClose} shortcuts={shortcuts} />);

    expect(screen.getByText(/Keyboard Shortcuts/)).toBeInTheDocument();
  });

  it('displays all shortcuts', () => {
    render(<KeyboardShortcutsModal isOpen onClose={mockOnClose} shortcuts={shortcuts} />);

    expect(screen.getByText('Open command palette')).toBeInTheDocument();
    expect(screen.getByText('Create new item')).toBeInTheDocument();
    expect(screen.getByText('Search')).toBeInTheDocument();
    expect(screen.getByText('Bulk delete')).toBeInTheDocument();
  });

  it('groups shortcuts by category', () => {
    render(<KeyboardShortcutsModal isOpen onClose={mockOnClose} shortcuts={shortcuts} />);

    expect(screen.getByText('System')).toBeInTheDocument();
    expect(screen.getByText('Editing')).toBeInTheDocument();
    expect(screen.getByText('Navigation')).toBeInTheDocument();
    expect(screen.getByText('Selection')).toBeInTheDocument();
  });

  it('closes modal when close button is clicked', () => {
    render(<KeyboardShortcutsModal isOpen onClose={mockOnClose} shortcuts={shortcuts} />);

    const closeButton = screen.getByLabelText('Close shortcuts modal');
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('closes modal when clicking outside', () => {
    render(<KeyboardShortcutsModal isOpen onClose={mockOnClose} shortcuts={shortcuts} />);

    const backdrop = document.querySelector(String.raw`.fixed.inset-0.z-\[101\]`);
    if (backdrop) {
      fireEvent.click(backdrop);
      expect(mockOnClose).toHaveBeenCalled();
    }
  });

  it('does not close modal when clicking content', () => {
    render(<KeyboardShortcutsModal isOpen onClose={mockOnClose} shortcuts={shortcuts} />);

    const content = screen.getByText('Open command palette');
    fireEvent.click(content);

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('closes modal on Escape key', () => {
    render(<KeyboardShortcutsModal isOpen onClose={mockOnClose} shortcuts={shortcuts} />);

    fireEvent.keyDown(globalThis, { key: 'Escape' });

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('displays shortcut count', () => {
    render(<KeyboardShortcutsModal isOpen onClose={mockOnClose} shortcuts={shortcuts} />);

    expect(screen.getByText(/4 Shortcuts Available/)).toBeInTheDocument();
  });

  it('displays empty modal when no shortcuts provided', () => {
    render(<KeyboardShortcutsModal isOpen onClose={mockOnClose} shortcuts={[]} />);

    expect(screen.getByText(/Keyboard Shortcuts/)).toBeInTheDocument();
    expect(screen.getByText(/0 Shortcuts Available/)).toBeInTheDocument();
  });

  it('shows keyboard hint in footer', () => {
    render(<KeyboardShortcutsModal isOpen onClose={mockOnClose} shortcuts={shortcuts} />);

    expect(screen.getByText(/Press ESC or \? to close/)).toBeInTheDocument();
  });

  it('displays context when provided', () => {
    const shortcutsWithContext: KeyboardShortcut[] = [
      {
        category: 'selection',
        context: 'Items view',
        description: 'Select all items',
        key: 'a',
        meta: true,
      },
    ];

    render(
      <KeyboardShortcutsModal isOpen onClose={mockOnClose} shortcuts={shortcutsWithContext} />,
    );

    expect(screen.getByText(/Context: Items view/)).toBeInTheDocument();
  });

  it('handles shortcuts without modifiers', () => {
    const simpleShortcuts: KeyboardShortcut[] = [
      {
        category: 'navigation',
        description: 'Focus search',
        key: '/',
      },
    ];

    render(<KeyboardShortcutsModal isOpen onClose={mockOnClose} shortcuts={simpleShortcuts} />);

    expect(screen.getByText('Focus search')).toBeInTheDocument();
  });
});
