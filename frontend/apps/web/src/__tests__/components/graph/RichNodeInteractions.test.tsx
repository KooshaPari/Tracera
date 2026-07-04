import { render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

// Import components directly to avoid layout dependencies
import { NodeActions } from '../../../components/graph/NodeActions';
import { NodeContextMenu } from '../../../components/graph/NodeContextMenu';
import { NodeHoverTooltip } from '../../../components/graph/NodeHoverTooltip';
import { NodeQuickActions } from '../../../components/graph/NodeQuickActions';

describe(NodeActions, () => {
  it('renders all action buttons', () => {
    const onExpand = vi.fn();
    const onNavigate = vi.fn();
    const onShowMenu = vi.fn();

    render(
      <NodeActions
        nodeId='test-node'
        isExpanded={false}
        onExpand={onExpand}
        onNavigate={onNavigate}
        onShowMenu={onShowMenu}
      />,
    );

    expect(screen.getByRole('button', { name: /expand/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /open details/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /more actions/i })).toBeInTheDocument();
  });

  it('calls onExpand when expand button is clicked', async () => {
    const onExpand = vi.fn();
    const onNavigate = vi.fn();
    const onShowMenu = vi.fn();

    render(
      <NodeActions
        nodeId='test-node'
        isExpanded={false}
        onExpand={onExpand}
        onNavigate={onNavigate}
        onShowMenu={onShowMenu}
      />,
    );

    const expandButton = screen.getByRole('button', { name: /expand/i });
    await user.click(expandButton);

    expect(onExpand).toHaveBeenCalledWith('test-node');
    expect(onExpand).toHaveBeenCalledOnce();
  });

  it('calls onNavigate when navigate button is clicked', async () => {
    const onExpand = vi.fn();
    const onNavigate = vi.fn();
    const onShowMenu = vi.fn();

    render(
      <NodeActions
        nodeId='test-node'
        isExpanded={false}
        onExpand={onExpand}
        onNavigate={onNavigate}
        onShowMenu={onShowMenu}
      />,
    );

    const navigateButton = screen.getByRole('button', {
      name: /open details/i,
    });
    await user.click(navigateButton);

    expect(onNavigate).toHaveBeenCalledWith('test-node');
    expect(onNavigate).toHaveBeenCalledOnce();
  });

  it('shows collapse icon when expanded', () => {
    render(
      <NodeActions
        nodeId='test-node'
        isExpanded
        onExpand={vi.fn()}
        onNavigate={vi.fn()}
        onShowMenu={vi.fn()}
      />,
    );

    expect(screen.getByRole('button', { name: /collapse/i })).toBeInTheDocument();
  });

  it('stops event propagation on button clicks', async () => {
    const onExpand = vi.fn();
    const parentClick = vi.fn();

    render(
      <div onClick={parentClick}>
        <NodeActions
          nodeId='test-node'
          isExpanded={false}
          onExpand={onExpand}
          onNavigate={vi.fn()}
          onShowMenu={vi.fn()}
        />
      </div>,
    );

    const expandButton = screen.getByRole('button', { name: /expand/i });
    await user.click(expandButton);

    expect(onExpand).toHaveBeenCalled();
    expect(parentClick).not.toHaveBeenCalled();
  });
});

describe(NodeContextMenu, () => {
  it('renders children as trigger', () => {
    render(
      <NodeContextMenu
        nodeId='test-node'
        nodeType='requirement'
        onCopyId={vi.fn()}
        onDuplicate={vi.fn()}
        onDelete={vi.fn()}
        onViewDetails={vi.fn()}
      >
        <div>Test Content</div>
      </NodeContextMenu>,
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('shows menu items on right click', async () => {
    render(
      <NodeContextMenu
        nodeId='test-node'
        nodeType='requirement'
        onCopyId={vi.fn()}
        onDuplicate={vi.fn()}
        onDelete={vi.fn()}
        onViewDetails={vi.fn()}
      >
        <div>Test Content</div>
      </NodeContextMenu>,
    );

    await user.pointer({
      keys: '[MouseRight>]',
      target: screen.getByText('Test Content'),
    });

    await waitFor(() => {
      expect(screen.getByText('View Details')).toBeInTheDocument();
      expect(screen.getByText('Copy ID')).toBeInTheDocument();
      expect(screen.getByText('Duplicate')).toBeInTheDocument();
      expect(screen.getByText('Delete')).toBeInTheDocument();
    });
  });

  it('calls onViewDetails when menu item is clicked', async () => {
    const onViewDetails = vi.fn();

    render(
      <NodeContextMenu
        nodeId='test-node'
        nodeType='requirement'
        onCopyId={vi.fn()}
        onDuplicate={vi.fn()}
        onDelete={vi.fn()}
        onViewDetails={onViewDetails}
      >
        <div>Test Content</div>
      </NodeContextMenu>,
    );

    await user.pointer({
      keys: '[MouseRight>]',
      target: screen.getByText('Test Content'),
    });

    await waitFor(() => {
      expect(screen.getByText('View Details')).toBeInTheDocument();
    });

    await user.click(screen.getByText('View Details'));

    expect(onViewDetails).toHaveBeenCalledWith('test-node');
  });

  it('calls onCopyId when Copy ID is clicked', async () => {
    const onCopyId = vi.fn();

    render(
      <NodeContextMenu
        nodeId='test-node'
        nodeType='requirement'
        onCopyId={onCopyId}
        onDuplicate={vi.fn()}
        onDelete={vi.fn()}
        onViewDetails={vi.fn()}
      >
        <div>Test Content</div>
      </NodeContextMenu>,
    );

    await user.pointer({
      keys: '[MouseRight>]',
      target: screen.getByText('Test Content'),
    });

    await waitFor(() => {
      expect(screen.getByText('Copy ID')).toBeInTheDocument();
    });

    await user.click(screen.getByText('Copy ID'));

    expect(onCopyId).toHaveBeenCalledWith('test-node');
  });
});

describe(NodeHoverTooltip, () => {
  it('renders tooltip with basic info', () => {
    render(
      <NodeHoverTooltip
        nodeId='test-node'
        nodeType='requirement'
        label='Test Requirement'
        position={{ x: 100, y: 100 }}
      />,
    );

    expect(screen.getByText('Test Requirement')).toBeInTheDocument();
    expect(screen.getByText('requirement')).toBeInTheDocument();
  });

  it('renders status when provided', () => {
    render(
      <NodeHoverTooltip
        nodeId='test-node'
        nodeType='requirement'
        label='Test Requirement'
        status='in_progress'
        position={{ x: 100, y: 100 }}
      />,
    );

    expect(screen.getByText('in_progress')).toBeInTheDocument();
  });

  it('renders metadata when provided', () => {
    const metadata = {
      assignee: 'John Doe',
      deadline: '2024-12-31',
      priority: 'high',
    };

    render(
      <NodeHoverTooltip
        nodeId='test-node'
        nodeType='requirement'
        label='Test Requirement'
        metadata={metadata}
        position={{ x: 100, y: 100 }}
      />,
    );

    expect(screen.getByText('priority:')).toBeInTheDocument();
    expect(screen.getByText('high')).toBeInTheDocument();
    expect(screen.getByText('assignee:')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('limits metadata to 3 items', () => {
    const metadata = {
      assignee: 'John Doe',
      category: 'feature',
      deadline: '2024-12-31',
      priority: 'high',
      status: 'active',
    };

    render(
      <NodeHoverTooltip
        nodeId='test-node'
        nodeType='requirement'
        label='Test Requirement'
        metadata={metadata}
        position={{ x: 100, y: 100 }}
      />,
    );

    const metadataItems = container.querySelectorAll('dl > div');
    expect(metadataItems.length).toBe(3);
  });

  it('positions tooltip based on position prop', () => {
    render(
      <NodeHoverTooltip
        nodeId='test-node'
        nodeType='requirement'
        label='Test Requirement'
        position={{ x: 150, y: 200 }}
      />,
    );

    const tooltip = container.firstChild;
    expect(tooltip).toBeInstanceOf(HTMLElement);
    if (tooltip instanceof HTMLElement) {
      expect(tooltip.style.left).toBe('160px'); // X + 10
      expect(tooltip.style.top).toBe('210px'); // Y + 10
    }
  });
});

describe(NodeQuickActions, () => {
  it('renders all quick action buttons', () => {
    render(
      <NodeQuickActions
        nodeId='test-node'
        onAddLink={vi.fn()}
        onAddTag={vi.fn()}
        onEditNote={vi.fn()}
      />,
    );

    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(3); // Link, Tag, Note buttons
  });

  it('opens link popover when link button is clicked', async () => {
    render(
      <NodeQuickActions
        nodeId='test-node'
        onAddLink={vi.fn()}
        onAddTag={vi.fn()}
        onEditNote={vi.fn()}
      />,
    );

    const buttons = screen.getAllByRole('button');
    await user.click(buttons[0]); // First button is link

    await waitFor(() => {
      expect(screen.getByText('Link to node')).toBeInTheDocument();
    });
  });

  it('calls onAddLink when link is submitted', async () => {
    const onAddLink = vi.fn();

    render(
      <NodeQuickActions
        nodeId='test-node'
        onAddLink={onAddLink}
        onAddTag={vi.fn()}
        onEditNote={vi.fn()}
      />,
    );

    const buttons = screen.getAllByRole('button');
    await user.click(buttons[0]);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Node ID')).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText('Node ID');
    await user.type(input, 'target-node-123');

    const addButton = screen.getByRole('button', { name: /add/i });
    await user.click(addButton);

    expect(onAddLink).toHaveBeenCalledWith('test-node', 'target-node-123');
  });

  it('opens tag popover when tag button is clicked', async () => {
    render(
      <NodeQuickActions
        nodeId='test-node'
        onAddLink={vi.fn()}
        onAddTag={vi.fn()}
        onEditNote={vi.fn()}
      />,
    );

    const buttons = screen.getAllByRole('button');
    await user.click(buttons[1]); // Second button is tag

    await waitFor(() => {
      expect(screen.getByText('Add tag')).toBeInTheDocument();
    });
  });

  it('calls onAddTag when tag is submitted', async () => {
    const onAddTag = vi.fn();

    render(
      <NodeQuickActions
        nodeId='test-node'
        onAddLink={vi.fn()}
        onAddTag={onAddTag}
        onEditNote={vi.fn()}
      />,
    );

    const buttons = screen.getAllByRole('button');
    await user.click(buttons[1]);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Tag name')).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText('Tag name');
    await user.type(input, 'important');

    const addButton = screen.getByRole('button', { name: /add/i });
    await user.click(addButton);

    expect(onAddTag).toHaveBeenCalledWith('test-node', 'important');
  });

  it('calls onEditNote when note is submitted', async () => {
    const onEditNote = vi.fn();

    render(
      <NodeQuickActions
        nodeId='test-node'
        onAddLink={vi.fn()}
        onAddTag={vi.fn()}
        onEditNote={onEditNote}
      />,
    );

    const buttons = screen.getAllByRole('button');
    await user.click(buttons[2]); // Third button is note

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Add note...')).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText('Add note...');
    await user.type(input, 'This is a test note');

    const saveButton = screen.getByRole('button', { name: /save/i });
    await user.click(saveButton);

    expect(onEditNote).toHaveBeenCalledWith('test-node', 'This is a test note');
  });

  it('clears input after submission', async () => {
    render(
      <NodeQuickActions
        nodeId='test-node'
        onAddLink={vi.fn()}
        onAddTag={vi.fn()}
        onEditNote={vi.fn()}
      />,
    );

    const buttons = screen.getAllByRole('button');
    await user.click(buttons[1]); // Tag button

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Tag name')).toBeInTheDocument();
    });

    const inputEl = screen.getByPlaceholderText('Tag name');
    if (inputEl instanceof HTMLInputElement) {
      await user.type(inputEl, 'test-tag');
    }

    const addButton = screen.getByRole('button', { name: /add/i });
    await user.click(addButton);

    await waitFor(() => {
      expect(inputEl instanceof HTMLInputElement ? inputEl.value : '').toBe('');
    });
  });
});
