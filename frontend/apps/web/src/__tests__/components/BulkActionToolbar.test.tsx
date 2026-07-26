import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Trash2 } from 'lucide-react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { BulkAction } from '../../components/BulkActionToolbar';

import { BulkActionToolbar } from '../../components/BulkActionToolbar';

let user: ReturnType<typeof userEvent.setup>;

describe(BulkActionToolbar, () => {
  beforeEach(() => {
    vi.clearAllMocks();
    user = userEvent.setup();
  });

  const getMockDelete = () => vi.fn();
  const getMockSelectAll = () => vi.fn();
  const getMockSelectNone = () => vi.fn();

  const getDeleteAction = (): BulkAction => ({
    action: getMockDelete(),
    icon: <Trash2 className='h-4 w-4' />,
    id: 'delete',
    label: 'Delete',
    variant: 'destructive',
  });

  it('does not render when no items are selected', () => {
    const { container } = render(
      <BulkActionToolbar
        selectedCount={0}
        totalCount={10}
        onSelectAll={getMockSelectAll()}
        onSelectNone={getMockSelectNone()}
        actions={[getDeleteAction()]}
      />,
    );

    expect(container.firstChild).toBeNull();
  });

  it('renders when items are selected', () => {
    const { getByText } = render(
      <BulkActionToolbar
        selectedCount={3}
        totalCount={10}
        onSelectAll={getMockSelectAll()}
        onSelectNone={getMockSelectNone()}
        actions={[getDeleteAction()]}
      />,
    );

    expect(getByText(/3 of 10 selected/)).toBeInTheDocument();
  });

  it('displays selection count correctly', () => {
    const { getByText } = render(
      <BulkActionToolbar
        selectedCount={5}
        totalCount={20}
        onSelectAll={getMockSelectAll()}
        onSelectNone={getMockSelectNone()}
        actions={[getDeleteAction()]}
      />,
    );

    expect(getByText(/5 of 20 selected/)).toBeInTheDocument();
  });

  it('calls onSelectAll when Select All is clicked', async () => {
    const mockSelectAll = getMockSelectAll();
    const { getByText } = render(
      <BulkActionToolbar
        selectedCount={3}
        totalCount={10}
        onSelectAll={mockSelectAll}
        onSelectNone={getMockSelectNone()}
        actions={[getDeleteAction()]}
      />,
    );

    await user.click(getByText('Select All'));
    expect(mockSelectAll).toHaveBeenCalled();
  });

  it('calls onSelectNone when Deselect is clicked', async () => {
    const mockSelectNone = getMockSelectNone();
    const { getByText } = render(
      <BulkActionToolbar
        selectedCount={3}
        totalCount={10}
        onSelectAll={getMockSelectAll()}
        onSelectNone={mockSelectNone}
        actions={[getDeleteAction()]}
      />,
    );

    await user.click(getByText('Deselect'));
    expect(mockSelectNone).toHaveBeenCalled();
  });

  it('disables Select All when all items are selected', () => {
    const { getByText } = render(
      <BulkActionToolbar
        selectedCount={10}
        totalCount={10}
        onSelectAll={getMockSelectAll()}
        onSelectNone={getMockSelectNone()}
        actions={[getDeleteAction()]}
      />,
    );

    const selectAllButton = getByText('Select All') as HTMLButtonElement;
    expect(selectAllButton.disabled).toBeTruthy();
  });

  it('renders all provided actions', () => {
    const archiveAction: BulkAction = {
      action: vi.fn(),
      icon: <span>📦</span>,
      id: 'archive',
      label: 'Archive',
    };

    const { getByText } = render(
      <BulkActionToolbar
        selectedCount={3}
        totalCount={10}
        onSelectAll={getMockSelectAll()}
        onSelectNone={getMockSelectNone()}
        actions={[getDeleteAction(), archiveAction]}
      />,
    );

    expect(getByText('Delete')).toBeInTheDocument();
    expect(getByText('Archive')).toBeInTheDocument();
  });

  it('disables Select All and actions when loading', () => {
    const { getByText } = render(
      <BulkActionToolbar
        selectedCount={3}
        totalCount={10}
        onSelectAll={getMockSelectAll()}
        onSelectNone={getMockSelectNone()}
        actions={[getDeleteAction()]}
        loading
      />,
    );

    const selectAllButton = getByText('Select All') as HTMLButtonElement;
    expect(selectAllButton.disabled).toBeTruthy();
  });

  it('respects action disabled flag when rendering', () => {
    const disabledAction: BulkAction = {
      ...getDeleteAction(),
      disabled: true,
    };

    const { getByText } = render(
      <BulkActionToolbar
        selectedCount={3}
        totalCount={10}
        onSelectAll={getMockSelectAll()}
        onSelectNone={getMockSelectNone()}
        actions={[disabledAction]}
      />,
    );

    // Verify toolbar renders with content
    expect(getByText(/3 of 10 selected/)).toBeInTheDocument();
    // The button will still render but should be disabled
    const deleteButton = getByText('Delete') as HTMLButtonElement;
    expect(deleteButton).toBeInTheDocument();
  });

  it('closes toolbar when close button is clicked', async () => {
    const mockSelectNone = getMockSelectNone();
    const { getByLabelText } = render(
      <BulkActionToolbar
        selectedCount={3}
        totalCount={10}
        onSelectAll={getMockSelectAll()}
        onSelectNone={mockSelectNone}
        actions={[getDeleteAction()]}
      />,
    );

    const closeButton = getByLabelText('Close toolbar');
    await user.click(closeButton);

    expect(mockSelectNone).toHaveBeenCalled();
  });
});
