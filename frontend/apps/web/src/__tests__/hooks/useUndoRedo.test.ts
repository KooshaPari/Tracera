import { act, renderHook } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { useUndoRedo } from '@/hooks/useUndoRedo';

describe(useUndoRedo, () => {
  it('initializes with initial state', () => {
    const { result } = renderHook(() => useUndoRedo('initial'));

    expect(result.current.state).toBe('initial');
    expect(result.current.canUndo).toBeFalsy();
    expect(result.current.canRedo).toBeFalsy();
    expect(result.current.currentIndex).toBe(0);
  });

  it('allows setting new state', () => {
    const { result } = renderHook(() => useUndoRedo('initial'));

    act(() => {
      result.current.setState('second');
    });

    expect(result.current.state).toBe('second');
    expect(result.current.canUndo).toBeTruthy();
    expect(result.current.canRedo).toBeFalsy();
    expect(result.current.currentIndex).toBe(1);
  });

  it('allows undoing state changes', () => {
    const { result } = renderHook(() => useUndoRedo('initial'));

    act(() => {
      result.current.setState('second');
      result.current.setState('third');
    });

    expect(result.current.state).toBe('third');

    act(() => {
      result.current.undo();
    });

    expect(result.current.state).toBe('second');
    expect(result.current.canUndo).toBeTruthy();
    expect(result.current.canRedo).toBeTruthy();
  });

  it('allows redoing state changes', () => {
    const { result } = renderHook(() => useUndoRedo('initial'));

    act(() => {
      result.current.setState('second');
      result.current.setState('third');
      result.current.undo();
    });

    expect(result.current.state).toBe('second');

    act(() => {
      result.current.redo();
    });

    expect(result.current.state).toBe('third');
    expect(result.current.canRedo).toBeFalsy();
  });

  it('clears redo history when new state is set after undo', () => {
    const { result } = renderHook(() => useUndoRedo('initial'));

    act(() => {
      result.current.setState('second');
      result.current.setState('third');
      result.current.undo();
    });

    expect(result.current.canRedo).toBeTruthy();

    act(() => {
      result.current.setState('new');
    });

    expect(result.current.state).toBe('new');
    expect(result.current.canRedo).toBeFalsy();
  });

  it('maintains history with descriptions', () => {
    const { result } = renderHook(() => useUndoRedo('initial'));

    act(() => {
      result.current.setState('second', 'Changed to second');
      result.current.setState('third', 'Changed to third');
    });

    expect(result.current.history).toHaveLength(3);
    expect(result.current.history[0].description).toBe('Initial state');
    expect(result.current.history[1].description).toBe('Changed to second');
    expect(result.current.history[2].description).toBe('Changed to third');
  });

  it('prevents undo when at initial state', () => {
    const { result } = renderHook(() => useUndoRedo('initial'));

    act(() => {
      result.current.undo();
    });

    expect(result.current.state).toBe('initial');
    expect(result.current.currentIndex).toBe(0);
  });

  it('prevents redo when at latest state', () => {
    const { result } = renderHook(() => useUndoRedo('initial'));

    act(() => {
      result.current.setState('second');
      result.current.redo();
    });

    expect(result.current.state).toBe('second');
    expect(result.current.currentIndex).toBe(1);
  });

  it('clears history and resets to initial state', () => {
    const { result } = renderHook(() => useUndoRedo('initial'));

    act(() => {
      result.current.setState('second');
      result.current.setState('third');
    });

    expect(result.current.history).toHaveLength(3);

    act(() => {
      result.current.clear();
    });

    expect(result.current.state).toBe('initial');
    expect(result.current.currentIndex).toBe(0);
    expect(result.current.canUndo).toBeFalsy();
    expect(result.current.canRedo).toBeFalsy();
  });

  it('works with complex objects', () => {
    interface State {
      count: number;
      items: string[];
    }

    const initial: State = { count: 0, items: [] };
    const { result } = renderHook(() => useUndoRedo(initial));

    act(() => {
      result.current.setState({ count: 1, items: ['a'] }, 'Added item');
      result.current.setState({ count: 2, items: ['a', 'b'] }, 'Added another');
    });

    expect(result.current.state).toEqual({ count: 2, items: ['a', 'b'] });

    act(() => {
      result.current.undo();
    });

    expect(result.current.state).toEqual({ count: 1, items: ['a'] });
  });

  it('updates timestamp on state changes', () => {
    const { result } = renderHook(() => useUndoRedo('initial'));

    const initialTime = result.current.history[0].timestamp;

    act(() => {
      result.current.setState('second');
    });

    const secondTime = result.current.history[1].timestamp;

    expect(secondTime).toBeGreaterThanOrEqual(initialTime);
  });
});
