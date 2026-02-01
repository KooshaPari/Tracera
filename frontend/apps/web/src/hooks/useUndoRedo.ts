import { useCallback, useRef, useState } from "react";

export interface HistoryEntry<T> {
	state: T;
	description?: string;
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
			state: initialState,
			description: "Initial state",
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
				state: newState,
				description,
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
				setStateInternal(historyRef.current[newIndex].state);
				return newIndex;
			}
			return prevIndex;
		});
	}, []);

	const redo = useCallback(() => {
		setCurrentIndexState((prevIndex) => {
			if (prevIndex < historyRef.current.length - 1) {
				const newIndex = prevIndex + 1;
				setStateInternal(historyRef.current[newIndex].state);
				return newIndex;
			}
			return prevIndex;
		});
	}, []);

	const clear = useCallback(() => {
		historyRef.current = [
			{
				state: initialState,
				description: "Initial state",
				timestamp: Date.now(),
			},
		];
		setCurrentIndexState(0);
		setStateInternal(initialState);
	}, [initialState]);

	return {
		state,
		setState,
		undo,
		redo,
		canUndo: currentIndexState > 0,
		canRedo: currentIndexState < historyRef.current.length - 1,
		history: historyRef.current,
		currentIndex: currentIndexState,
		clear,
	};
}
