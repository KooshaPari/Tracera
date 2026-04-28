import { render } from '@testing-library/react';
import { memo, useCallback, useMemo } from 'react';
import { describe, expect, it, vi } from 'vitest';

interface TestItem {
  id: string;
  name?: string;
  title?: string;
  type?: string;
  status?: string;
  priority?: string;
  owner?: string;
}

describe('React Memoization Optimizations', () => {
  describe('ItemCard Memoization', () => {
    it('should only re-render when relevant props change', () => {
      const renderSpy = vi.fn();

      const TestItemCard = memo(
        ({
          item,
          onDragStart: _onDragStart,
        }: {
          item: TestItem;
          onDragStart: (item: TestItem) => void;
        }) => {
          renderSpy();
          return <div>{item.title ?? item.name}</div>;
        },
        (prev, next) =>
          prev.item.id === next.item.id &&
          prev.item.title === next.item.title &&
          prev.item.type === next.item.type &&
          prev.item.status === next.item.status &&
          prev.item.priority === next.item.priority &&
          prev.item.owner === next.item.owner,
      );

      const { rerender } = render(
        <TestItemCard
          item={{
            id: '1',
            owner: 'John',
            priority: 'medium',
            status: 'todo',
            title: 'Test',
            type: 'feature',
          }}
          onDragStart={vi.fn()}
        />,
      );

      expect(renderSpy).toHaveBeenCalledTimes(1);

      // Re-render with same props - should skip re-render
      rerender(
        <TestItemCard
          item={{
            id: '1',
            owner: 'John',
            priority: 'medium',
            status: 'todo',
            title: 'Test',
            type: 'feature',
          }}
          onDragStart={vi.fn()}
        />,
      );

      // Still 1 because memo prevented re-render
      expect(renderSpy).toHaveBeenCalledTimes(1);

      // Re-render with changed title - should re-render
      rerender(
        <TestItemCard
          item={{
            id: '1',
            owner: 'John',
            priority: 'medium',
            status: 'todo',
            title: 'Test Updated',
            type: 'feature',
          }}
          onDragStart={vi.fn()}
        />,
      );

      expect(renderSpy).toHaveBeenCalledTimes(2);
    });

    it('should use useCallback for drag handlers to maintain reference equality', async () => {
      const handleDragStartSpy = vi.fn();
      let callbackReference: ((item: TestItem) => void) | null = null;

      function TestComponent() {
        const handleDragStart = useCallback((item: TestItem) => {
          handleDragStartSpy(item);
        }, []);

        // Store reference to verify it doesn't change on re-render
        callbackReference = handleDragStart;

        return (
          <button
            onClick={() => {
              handleDragStart({ id: '1', title: 'Test' });
            }}
          >
            Drag
          </button>
        );
      }

      const { rerender } = render(<TestComponent />);
      const initialReference = callbackReference;

      rerender(<TestComponent />);
      const secondReference = callbackReference;

      // UseCallback should return same reference across renders
      expect(initialReference).toBe(secondReference);
    });
  });

  describe('TreeItem Memoization', () => {
    it('should skip re-render when only parent expandedIds Set reference changes but item stays same', () => {
      const renderSpy = vi.fn();

      const TestTreeItem = memo(
        ({
          nodeId,
          expandedIds: _expandedIds,
          onToggle: _onToggle,
        }: {
          nodeId: string;
          expandedIds: Set<string>;
          onToggle: (id: string) => void;
        }) => {
          renderSpy();
          return <div>{nodeId}</div>;
        },
        (prev, next) =>
          prev.nodeId === next.nodeId &&
          prev.expandedIds.has(prev.nodeId) === next.expandedIds.has(next.nodeId),
      );

      const expandedIds = new Set<string>(['1', '2']);

      const { rerender } = render(
        <TestTreeItem nodeId='1' expandedIds={expandedIds} onToggle={vi.fn()} />,
      );

      expect(renderSpy).toHaveBeenCalledTimes(1);

      // Re-render with same Set content but different reference
      const newExpandedIds = new Set<string>(['1', '2']);

      rerender(<TestTreeItem nodeId='1' expandedIds={newExpandedIds} onToggle={vi.fn()} />);

      // Still 1 because custom comparison checks Set content, not reference
      expect(renderSpy).toHaveBeenCalledTimes(1);

      // Re-render where item is not in expanded set - should re-render
      const changedExpandedIds = new Set<string>(['2', '3']);

      rerender(<TestTreeItem nodeId='1' expandedIds={changedExpandedIds} onToggle={vi.fn()} />);

      expect(renderSpy).toHaveBeenCalledTimes(2);
    });

    it('should use useCallback for toggle handler', async () => {
      let lastCallbackRef: ((id: string) => void) | null = null;

      function TestComponent() {
        const handleToggle = useCallback((_id: string) => {
          // Toggle logic
        }, []);

        lastCallbackRef = handleToggle;
        return (
          <button
            onClick={() => {
              handleToggle('1');
            }}
          >
            Toggle
          </button>
        );
      }

      const { rerender } = render(<TestComponent />);
      const firstRef = lastCallbackRef;

      rerender(<TestComponent />);
      const secondRef = lastCallbackRef;

      // Callback should maintain same reference
      expect(firstRef).toBe(secondRef);
    });
  });

  describe('VirtualTableRow Memoization', () => {
    it('should only re-render when item data or handlers change', () => {
      const renderSpy = vi.fn();

      const TestTableRow = memo(
        ({
          item,
          onDelete: _onDelete,
          onNavigate: _onNavigate,
        }: {
          item: TestItem;
          onDelete: (id: string) => void;
          onNavigate: (path: string) => void;
        }) => {
          renderSpy();
          return (
            <tr>
              <td>{item.title ?? item.name}</td>
            </tr>
          );
        },
        (prev, next) =>
          prev.item.id === next.item.id &&
          prev.item.title === next.item.title &&
          prev.item.type === next.item.type &&
          prev.item.status === next.item.status &&
          prev.item.priority === next.item.priority &&
          prev.item.owner === next.item.owner,
      );

      const { rerender } = render(
        <table>
          <tbody>
            <TestTableRow
              item={{
                id: '1',
                owner: 'Alice',
                priority: 'high',
                status: 'todo',
                title: 'Task 1',
                type: 'feature',
              }}
              onDelete={vi.fn()}
              onNavigate={vi.fn()}
            />
          </tbody>
        </table>,
      );

      expect(renderSpy).toHaveBeenCalledTimes(1);

      // Same item data should not trigger re-render
      rerender(
        <table>
          <tbody>
            <TestTableRow
              item={{
                id: '1',
                owner: 'Alice',
                priority: 'high',
                status: 'todo',
                title: 'Task 1',
                type: 'feature',
              }}
              onDelete={vi.fn()}
              onNavigate={vi.fn()}
            />
          </tbody>
        </table>,
      );

      expect(renderSpy).toHaveBeenCalledTimes(1);

      // Different item should trigger re-render
      rerender(
        <table>
          <tbody>
            <TestTableRow
              item={{
                id: '1',
                owner: 'Alice',
                priority: 'high',
                status: 'done',
                title: 'Task 1 Updated',
                type: 'feature',
              }}
              onDelete={vi.fn()}
              onNavigate={vi.fn()}
            />
          </tbody>
        </table>,
      );

      expect(renderSpy).toHaveBeenCalledTimes(2);
    });

    it('should use useCallback for click handlers in table row', async () => {
      let navCallbackRef: ((path: string) => void) | null = null;
      let deleteCallbackRef: ((id: string) => void) | null = null;

      function TestTableRow({
        item,
        onDelete,
        onNavigate,
      }: {
        item: TestItem;
        onDelete: (id: string) => void;
        onNavigate: (path: string) => void;
      }) {
        const handleNavigate = useCallback(() => {
          onNavigate(`/items/${item.id}`);
        }, [item.id, onNavigate]);

        const handleDelete = useCallback(() => {
          onDelete(item.id);
        }, [item.id, onDelete]);

        navCallbackRef = handleNavigate;
        deleteCallbackRef = handleDelete;

        return (
          <tr>
            <td>
              <button onClick={handleNavigate}>{item.title ?? item.name}</button>
            </td>
            <td>
              <button onClick={handleDelete}>Delete</button>
            </td>
          </tr>
        );
      }

      const { rerender } = render(
        <table>
          <tbody>
            <TestTableRow
              item={{ id: '1', title: 'Task' }}
              onDelete={vi.fn()}
              onNavigate={vi.fn()}
            />
          </tbody>
        </table>,
      );

      const navRef1 = navCallbackRef;
      const delRef1 = deleteCallbackRef;

      rerender(
        <table>
          <tbody>
            <TestTableRow
              item={{ id: '1', title: 'Task' }}
              onDelete={vi.fn()}
              onNavigate={vi.fn()}
            />
          </tbody>
        </table>,
      );

      // Callbacks should maintain same reference across renders
      expect(navCallbackRef).toBe(navRef1);
      expect(deleteCallbackRef).toBe(delRef1);
    });
  });

  describe('useMemo for Computed Values', () => {
    it('should only recompute filtered items when dependencies change', () => {
      const computeSpy = vi.fn();

      function TestComponent({ items, filter }: { items: TestItem[]; filter: string }) {
        const computed = useMemo(() => {
          computeSpy();
          return items.filter((item) =>
            (item.title ?? item.name ?? '').toLowerCase().includes(filter.toLowerCase()),
          );
        }, [items, filter]);

        return <div>{computed.length}</div>;
      }

      const items: TestItem[] = [{ id: '1', title: 'Test' }];
      const { rerender } = render(<TestComponent items={items} filter='test' />);

      expect(computeSpy).toHaveBeenCalledTimes(1);

      // Same items and filter - should not recompute
      rerender(<TestComponent items={items} filter='test' />);

      // Still 1 because items reference is same and filter is same
      expect(computeSpy).toHaveBeenCalledTimes(1);

      // Different filter - should recompute
      rerender(<TestComponent items={items} filter='other' />);

      expect(computeSpy).toHaveBeenCalledTimes(2);
    });
  });
});
