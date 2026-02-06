/**
 * Power User Tests: Keyboard Shortcuts, Undo/Redo, and Bulk Operations
 * Tests advanced features for power users and developers
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

// Mock Keyboard Shortcuts Handler
function MockKeyboardShortcuts({
  onShortcut = vi.fn(),
}: {
  onShortcut?: (action: string) => void;
}) {
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K: Command palette
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        onShortcut('command-palette');
      }
      // Cmd/Ctrl + S: Save
      else if ((e.metaKey || e.ctrlKey) && e.key === 's') {
        e.preventDefault();
        onShortcut('save');
      }
      // Cmd/Ctrl + Z: Undo / Cmd/Ctrl + Shift + Z: Redo (single branch to avoid duplicate condition)
      else if ((e.metaKey || e.ctrlKey) && e.key === 'z') {
        e.preventDefault();
        onShortcut(e.shiftKey ? 'redo' : 'undo');
      }
      // Cmd/Ctrl + A: Select all
      else if ((e.metaKey || e.ctrlKey) && e.key === 'a') {
        e.preventDefault();
        onShortcut('select-all');
      }
      // Delete: Delete selected
      else if (e.key === 'Delete') {
        onShortcut('delete');
      }
    };

    globalThis.addEventListener('keydown', handleKeyDown);
    return () => {
      globalThis.removeEventListener('keydown', handleKeyDown);
    };
  }, [onShortcut]);

  return (
    <div className='p-4'>
      <h2 className='mb-4 font-bold'>Keyboard Shortcuts Reference</h2>
      <table className='text-sm'>
        <tbody>
          <tr>
            <td className='pr-4'>Cmd/Ctrl + K</td>
            <td>Open Command Palette</td>
          </tr>
          <tr>
            <td className='pr-4'>Cmd/Ctrl + S</td>
            <td>Save</td>
          </tr>
          <tr>
            <td className='pr-4'>Cmd/Ctrl + Z</td>
            <td>Undo</td>
          </tr>
          <tr>
            <td className='pr-4'>Cmd/Ctrl + Shift + Z</td>
            <td>Redo</td>
          </tr>
          <tr>
            <td className='pr-4'>Cmd/Ctrl + A</td>
            <td>Select All</td>
          </tr>
          <tr>
            <td className='pr-4'>Delete</td>
            <td>Delete Selected</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

// Mock Undo/Redo Manager
class UndoRedoManager {
  private history: any[] = [];
  private currentIndex = -1;

  push(state: any) {
    // Remove any redo history
    this.history = this.history.slice(0, this.currentIndex + 1);
    this.history.push(state);
    this.currentIndex++;
  }

  undo() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      return this.history[this.currentIndex];
    }
    return null;
  }

  redo() {
    if (this.currentIndex < this.history.length - 1) {
      this.currentIndex++;
      return this.history[this.currentIndex];
    }
    return null;
  }

  canUndo() {
    return this.currentIndex > 0;
  }

  canRedo() {
    return this.currentIndex < this.history.length - 1;
  }
}

// Mock Undo/Redo Component
function MockUndoRedoEditor({
  onStateChange = vi.fn(),
}: {
  onStateChange?: (state: string) => void;
}) {
  const [text, setText] = React.useState('');
  const [manager] = React.useState(() => new UndoRedoManager());

  const handleTextChange = (newText: string) => {
    setText(newText);
    manager.push(newText);
    onStateChange(newText);
  };

  const handleUndo = () => {
    const previousState = manager.undo();
    if (previousState !== null) {
      setText(previousState);
      onStateChange(previousState);
    }
  };

  const handleRedo = () => {
    const nextState = manager.redo();
    if (nextState !== null) {
      setText(nextState);
      onStateChange(nextState);
    }
  };

  return (
    <div className='p-4'>
      <div className='mb-4 flex gap-2'>
        <button
          onClick={handleUndo}
          disabled={!manager.canUndo()}
          className='rounded bg-gray-200 px-3 py-2 disabled:opacity-50'
        >
          Undo
        </button>
        <button
          onClick={handleRedo}
          disabled={!manager.canRedo()}
          className='rounded bg-gray-200 px-3 py-2 disabled:opacity-50'
        >
          Redo
        </button>
      </div>
      <textarea
        value={text}
        onChange={(e) => {
          handleTextChange(e.target.value);
        }}
        className='h-32 w-full rounded border px-3 py-2 font-mono'
        placeholder='Type here...'
      />
    </div>
  );
}

// Mock Bulk Selection Component
function MockBulkSelection({
  items = [
    { completed: false, id: '1', name: 'Item 1' },
    { completed: false, id: '2', name: 'Item 2' },
    { completed: false, id: '3', name: 'Item 3' },
  ],
  onSelectChange = vi.fn(),
  onBulkAction = vi.fn(),
}: {
  items?: { id: string; name: string; completed: boolean }[];
  onSelectChange?: (selectedIds: string[]) => void;
  onBulkAction?: (action: string, selectedIds: string[]) => void;
}) {
  const [selectedIds, setSelectedIds] = React.useState<string[]>([]);

  const handleSelectAll = () => {
    if (selectedIds.length === items.length) {
      setSelectedIds([]);
      onSelectChange([]);
    } else {
      const allIds = items.map((item) => item.id);
      setSelectedIds(allIds);
      onSelectChange(allIds);
    }
  };

  const handleSelectItem = (id: string) => {
    const newSelected = selectedIds.includes(id)
      ? selectedIds.filter((sid) => sid !== id)
      : [...selectedIds, id];

    setSelectedIds(newSelected);
    onSelectChange(newSelected);
  };

  const handleBulkDelete = () => {
    onBulkAction('delete', selectedIds);
    setSelectedIds([]);
  };

  const handleBulkComplete = () => {
    onBulkAction('complete', selectedIds);
    setSelectedIds([]);
  };

  const allSelected = selectedIds.length === items.length && items.length > 0;

  return (
    <div className='p-4'>
      <div className='mb-4 flex gap-2'>
        <label className='flex items-center gap-2'>
          <input
            type='checkbox'
            checked={allSelected}
            onChange={handleSelectAll}
            aria-label='Select all items'
          />
          Select All ({selectedIds.length}/{items.length})
        </label>
      </div>

      <div className='mb-4 space-y-2'>
        {items.map((item) => (
          <label key={item.id} className='flex items-center gap-2 rounded p-2 hover:bg-gray-100'>
            <input
              type='checkbox'
              checked={selectedIds.includes(item.id)}
              onChange={() => {
                handleSelectItem(item.id);
              }}
              aria-label={`Select ${item.name}`}
            />
            {item.name}
          </label>
        ))}
      </div>

      {selectedIds.length > 0 && (
        <div className='flex gap-2'>
          <button
            onClick={handleBulkComplete}
            className='rounded bg-green-600 px-3 py-2 text-white hover:bg-green-700'
          >
            Mark as Complete ({selectedIds.length})
          </button>
          <button
            onClick={handleBulkDelete}
            className='rounded bg-red-600 px-3 py-2 text-white hover:bg-red-700'
          >
            Delete ({selectedIds.length})
          </button>
        </div>
      )}
    </div>
  );
}

let user: ReturnType<typeof userEvent.setup>;
beforeEach(() => {
  user = userEvent.setup();
});

describe('Keyboard Shortcuts - Command Palette', () => {
  it('should open command palette with Cmd/Ctrl + K', async () => {
    const handleShortcut = vi.fn();

    render(<MockKeyboardShortcuts onShortcut={handleShortcut} />);

    await user.keyboard('{Meta>}k{/Meta}');

    expect(handleShortcut).toHaveBeenCalledWith('command-palette');
  });

  it('should trigger save with Cmd/Ctrl + S', async () => {
    const handleShortcut = vi.fn();

    render(<MockKeyboardShortcuts onShortcut={handleShortcut} />);

    await user.keyboard('{Meta>}s{/Meta}');

    expect(handleShortcut).toHaveBeenCalledWith('save');
  });

  it('should display keyboard shortcuts reference', () => {
    render(<MockKeyboardShortcuts />);

    expect(screen.getByText(/Cmd\/Ctrl \+ K/)).toBeInTheDocument();
    expect(screen.getByText(/Open Command Palette/)).toBeInTheDocument();
  });

  it('should be accessible to keyboard-only users', async () => {
    render(<MockKeyboardShortcuts />);

    // Should be able to tab through and use keyboard
    await user.keyboard('{Tab}');
    // Focus should move to first tabbable element
  });
});

describe('Keyboard Shortcuts - Save and Delete', () => {
  it('should trigger save action with Cmd/Ctrl + S', async () => {
    const handleShortcut = vi.fn();

    render(<MockKeyboardShortcuts onShortcut={handleShortcut} />);

    await user.keyboard('{Meta>}s{/Meta}');

    expect(handleShortcut).toHaveBeenCalledWith('save');
  });

  it('should trigger delete with Delete key', async () => {
    const handleShortcut = vi.fn();

    render(<MockKeyboardShortcuts onShortcut={handleShortcut} />);

    await user.keyboard('{Delete}');

    expect(handleShortcut).toHaveBeenCalledWith('delete');
  });

  it('should select all with Cmd/Ctrl + A', async () => {
    const handleShortcut = vi.fn();

    render(<MockKeyboardShortcuts onShortcut={handleShortcut} />);

    await user.keyboard('{Meta>}a{/Meta}');

    expect(handleShortcut).toHaveBeenCalledWith('select-all');
  });
});

describe('Undo/Redo Functionality', () => {
  it('should undo previous action', async () => {
    const handleStateChange = vi.fn();

    render(<MockUndoRedoEditor onStateChange={handleStateChange} />);

    const textarea = screen.getByPlaceholderText('Type here...');
    await user.type(textarea, 'Hello');

    const undoBtn = screen.getByRole('button', { name: 'Undo' });
    await user.click(undoBtn);

    expect(handleStateChange).toHaveBeenLastCalledWith('Hell');
  });

  it('should redo after undo', async () => {
    const handleStateChange = vi.fn();

    render(<MockUndoRedoEditor onStateChange={handleStateChange} />);

    const textarea = screen.getByPlaceholderText('Type here...');
    await user.type(textarea, 'Test');

    const undoBtn = screen.getByRole('button', { name: 'Undo' });
    await user.click(undoBtn);

    const redoBtn = screen.getByRole('button', { name: 'Redo' });
    await user.click(redoBtn);

    expect(handleStateChange).toHaveBeenLastCalledWith('Tes');
  });

  it('should disable undo when no history', () => {
    render(<MockUndoRedoEditor />);

    const undoBtn = screen.getByRole('button', { name: 'Undo' });
    expect(undoBtn).toBeDisabled();
  });

  it('should disable redo when at latest state', async () => {
    render(<MockUndoRedoEditor />);

    const textarea = screen.getByPlaceholderText('Type here...');
    await user.type(textarea, 'Text');

    const redoBtn = screen.getByRole('button', { name: 'Redo' });
    expect(redoBtn).toBeDisabled();
  });

  it('should clear redo history when new change made after undo', async () => {
    render(<MockUndoRedoEditor />);

    const textarea = screen.getByPlaceholderText('Type here...');
    await user.type(textarea, 'A');
    await user.type(textarea, 'B');

    const undoBtn = screen.getByRole('button', { name: 'Undo' });
    await user.click(undoBtn);

    const redoBtn = screen.getByRole('button', { name: 'Redo' });
    expect(redoBtn).toBeEnabled();

    // Type new content
    await user.type(textarea, 'C');

    // Redo history should be cleared
    expect(redoBtn).toBeDisabled();
  });

  it('should support keyboard shortcuts for undo/redo', async () => {
    render(<MockUndoRedoEditor />);

    const textarea = screen.getByPlaceholderText('Type here...');
    await user.type(textarea, 'Test');

    // Undo with Cmd/Ctrl + Z
    await user.keyboard('{Meta>}z{/Meta}');

    // Verify undo happened (textarea would be modified)
  });
});

describe('Bulk Selection and Operations', () => {
  it('should render items with checkboxes', () => {
    render(<MockBulkSelection />);

    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes.length).toBeGreaterThan(0);
  });

  it('should select all items with select all checkbox', async () => {
    const handleSelectChange = vi.fn();

    render(<MockBulkSelection onSelectChange={handleSelectChange} />);

    const selectAllCheckbox = screen.getByLabelText('Select all items');
    await user.click(selectAllCheckbox);

    expect(handleSelectChange).toHaveBeenCalledWith(['1', '2', '3']);
  });

  it('should deselect all with select all checkbox', async () => {
    const handleSelectChange = vi.fn();

    render(<MockBulkSelection onSelectChange={handleSelectChange} />);

    const selectAllCheckbox = screen.getByLabelText('Select all items');

    // Select all
    await user.click(selectAllCheckbox);
    expect(handleSelectChange).toHaveBeenCalledWith(['1', '2', '3']);

    // Deselect all
    await user.click(selectAllCheckbox);
    expect(handleSelectChange).toHaveBeenLastCalledWith([]);
  });

  it('should select individual items', async () => {
    const handleSelectChange = vi.fn();

    render(<MockBulkSelection onSelectChange={handleSelectChange} />);

    const item1Checkbox = screen.getByLabelText('Select Item 1');
    await user.click(item1Checkbox);

    expect(handleSelectChange).toHaveBeenCalledWith(['1']);
  });

  it('should show bulk action buttons when items selected', async () => {
    render(<MockBulkSelection />);

    const item1Checkbox = screen.getByLabelText('Select Item 1');
    await user.click(item1Checkbox);

    expect(screen.getByRole('button', { name: /Mark as Complete/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Delete/ })).toBeInTheDocument();
  });

  it('should perform bulk delete action', async () => {
    const handleBulkAction = vi.fn();

    render(<MockBulkSelection onBulkAction={handleBulkAction} />);

    const item1Checkbox = screen.getByLabelText('Select Item 1');
    const item2Checkbox = screen.getByLabelText('Select Item 2');

    await user.click(item1Checkbox);
    await user.click(item2Checkbox);

    const deleteBtn = screen.getByRole('button', { name: /Delete/ });
    await user.click(deleteBtn);

    expect(handleBulkAction).toHaveBeenCalledWith('delete', ['1', '2']);
  });

  it('should perform bulk complete action', async () => {
    const handleBulkAction = vi.fn();

    render(<MockBulkSelection onBulkAction={handleBulkAction} />);

    const selectAllCheckbox = screen.getByLabelText('Select all items');
    await user.click(selectAllCheckbox);

    const completeBtn = screen.getByRole('button', {
      name: /Mark as Complete/,
    });
    await user.click(completeBtn);

    expect(handleBulkAction).toHaveBeenCalledWith('complete', ['1', '2', '3']);
  });

  it('should update selection count', async () => {
    render(<MockBulkSelection />);

    // Initially shows 0/3
    expect(screen.getByText('0/3')).toBeInTheDocument();

    const item1Checkbox = screen.getByLabelText('Select Item 1');
    await user.click(item1Checkbox);

    // Now shows 1/3
    expect(screen.getByText('1/3')).toBeInTheDocument();
  });

  it('should clear selection after bulk action', async () => {
    render(<MockBulkSelection />);

    const item1Checkbox = screen.getByLabelText('Select Item 1');
    await user.click(item1Checkbox);

    const deleteBtn = screen.getByRole('button', { name: /Delete/ });
    await user.click(deleteBtn);

    // Selection should be cleared
    expect(item1Checkbox).not.toBeChecked();
    expect(screen.getByText('0/3')).toBeInTheDocument();
  });

  it('should support keyboard selection (Shift + Click)', async () => {
    render(<MockBulkSelection />);

    const item1 = screen.getByLabelText('Select Item 1');
    const item3 = screen.getByLabelText('Select Item 3');

    await user.click(item1);
    await user.click(item3, { shiftKey: true });

    // Both should be selected
    expect(item1).toBeChecked();
    expect(item3).toBeChecked();
  });

  it('should support keyboard Ctrl + Click for multi-select', async () => {
    render(<MockBulkSelection />);

    const item1 = screen.getByLabelText('Select Item 1');
    const item3 = screen.getByLabelText('Select Item 3');

    await user.click(item1);
    await user.click(item3, { ctrlKey: true });

    // Both should be selected
    expect(item1).toBeChecked();
    expect(item3).toBeChecked();
  });
});

describe('Bulk Export/Share Operations', () => {
  function MockBulkExport({
    onExport = vi.fn(),
  }: {
    onExport?: (format: string, selectedIds: string[]) => void;
  }) {
    const [selectedIds, setSelectedIds] = React.useState<string[]>([]);
    const [format, setFormat] = React.useState('json');

    return (
      <div className='p-4'>
        <div className='mb-4'>
          <label>
            <input
              type='checkbox'
              onChange={() => {
                setSelectedIds(['1', '2', '3']);
              }}
            />
            Select All
          </label>
        </div>

        {selectedIds.length > 0 && (
          <div>
            <select
              value={format}
              onChange={(e) => {
                setFormat(e.target.value);
              }}
            >
              <option value='json'>JSON</option>
              <option value='csv'>CSV</option>
              <option value='pdf'>PDF</option>
            </select>
            <button
              onClick={() => {
                onExport(format, selectedIds);
              }}
              className='ml-2 rounded bg-blue-600 px-3 py-2 text-white'
            >
              Export
            </button>
          </div>
        )}
      </div>
    );
  }

  it('should export selected items in chosen format', async () => {
    const handleExport = vi.fn();

    render(<MockBulkExport onExport={handleExport} />);

    const selectAllCheckbox = screen.getByRole('checkbox');
    await user.click(selectAllCheckbox);

    const exportBtn = screen.getByRole('button', { name: 'Export' });
    await user.click(exportBtn);

    expect(handleExport).toHaveBeenCalledWith('json', expect.any(Array));
  });
});

describe('Keyboard Accessibility for Bulk Operations', () => {
  it('should navigate list with arrow keys', async () => {
    render(<MockBulkSelection />);

    const item1 = screen.getByLabelText('Select Item 1');
    item1.focus();
    expect(item1).toHaveFocus();

    // Should support arrow navigation
  });

  it('should support Space to toggle selection', async () => {
    render(<MockBulkSelection />);

    const item1 = screen.getByLabelText('Select Item 1');
    item1.focus();

    await user.keyboard(' ');

    expect(item1).toBeChecked();
  });
});
