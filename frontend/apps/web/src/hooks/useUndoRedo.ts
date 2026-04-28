import { useCallback, useRef, useState } from 'react';

export interface HistoryEntry<T> {
  state: T;
  description?: string | undefined;
  timestamp: number;
}

export interface UseUndoRedoResult<T> {
  state: T;
  setState: (newState: T, description?: string) => void;
  undo: () => void;
  redo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  history: HistoryEntry<T>[];
  currentIndex: number;
  clear: () => void;
}

export function useUndoRedo<T>(initialState: T): UseUndoRedoResult<T> {
  const [state, setStateInternal] = useState<T>(initialState);
  const historyRef = useRef<HistoryEntry<T>[]>([
    {
      description: 'Initial state',
      state: initialState,
      timestamp: Date.now(),
    },
  ]);
  const [currentIndexState, setCurrentIndexState] = useState(0);

  const setState = useCallback((newState: T, description?: string) => {
    setCurrentIndexState((prevIndex) => {
      // Remove any redo entries if we're adding a new state
      if (prevIndex < historyRef.current.length - 1) {
        historyRef.current = historyRef.current.slice(0, prevIndex + 1);
      }

      // Add new entry
      historyRef.current.push({
        description,
        state: newState,
        timestamp: Date.now(),
      });

      const newIndex = historyRef.current.length - 1;
      setStateInternal(newState);
      return newIndex;
    });
  }, []);

  const undo = useCallback(() => {
    setCurrentIndexState((prevIndex) => {
      if (prevIndex > 0) {
        const newIndex = prevIndex - 1;
        const entry = historyRef.current[newIndex];
        if (entry) {
          setStateInternal(entry.state);
        }
        return newIndex;
      }
      return prevIndex;
    });
  }, []);

  const redo = useCallback(() => {
    setCurrentIndexState((prevIndex) => {
      if (prevIndex < historyRef.current.length - 1) {
        const newIndex = prevIndex + 1;
        const entry = historyRef.current[newIndex];
        if (entry) {
          setStateInternal(entry.state);
        }
        return newIndex;
      }
      return prevIndex;
    });
  }, []);

  const clear = useCallback(() => {
    historyRef.current = [
      {
        description: 'Initial state',
        state: initialState,
        timestamp: Date.now(),
      },
    ];
    setCurrentIndexState(0);
    setStateInternal(initialState);
  }, [initialState]);

  return {
    canRedo: currentIndexState < historyRef.current.length - 1,
    canUndo: currentIndexState > 0,
    clear,
    currentIndex: currentIndexState,
    history: historyRef.current,
    redo,
    setState,
    state,
    undo,
  };
}
