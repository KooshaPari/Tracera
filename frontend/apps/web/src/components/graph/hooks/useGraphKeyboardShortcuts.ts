// Keyboard Shortcuts Hook for Graph Controls
// Provides keyboard navigation and control shortcuts

import { useEffect, useCallback } from "react";
import { useReactFlow } from "@xyflow/react";

interface KeyboardShortcutsConfig {
	// View controls
	onFitView?: () => void;
	onZoomIn?: () => void;
	onZoomOut?: () => void;
	onActualSize?: () => void;
	onFullscreen?: () => void;

	// Panel controls
	onToggleDetailPanel?: () => void;
	onToggleMiniMap?: () => void;

	// Export
	onExport?: () => void;

	// Filter
	onToggleFilters?: () => void;

	// Reset
	onReset?: () => void;

	// Enable/disable
	enabled?: boolean;
}

export function useGraphKeyboardShortcuts({
	onFitView,
	onZoomIn,
	onZoomOut,
	onActualSize,
	onFullscreen,
	onToggleDetailPanel,
	onToggleMiniMap,
	onExport,
	onToggleFilters,
	onReset,
	enabled = true,
}: KeyboardShortcutsConfig) {
	const { fitView, zoomIn, zoomOut } = useReactFlow();

	const handleKeyDown = useCallback(
		(event: KeyboardEvent) => {
			if (!enabled) return;

			// Ignore if user is typing in an input
			const target = event.target as HTMLElement;
			if (
				target.tagName === "INPUT" ||
				target.tagName === "TEXTAREA" ||
				target.isContentEditable
			) {
				return;
			}

			const isMod = event.metaKey || event.ctrlKey;
			const isShift = event.shiftKey;

			// Zoom in: Cmd/Ctrl + Plus/Equal
			if (isMod && (event.key === "+" || event.key === "=")) {
				event.preventDefault();
				if (onZoomIn) onZoomIn();
				else void zoomIn({ duration: 200 });
				return;
			}

			// Zoom out: Cmd/Ctrl + Minus
			if (isMod && event.key === "-") {
				event.preventDefault();
				if (onZoomOut) onZoomOut();
				else void zoomOut({ duration: 200 });
				return;
			}

			// Fit view: Cmd/Ctrl + 0
			if (isMod && event.key === "0") {
				event.preventDefault();
				if (onFitView) onFitView();
				else void fitView({ padding: 0.2, duration: 300 });
				return;
			}

			// Actual size: Cmd/Ctrl + 1
			if (isMod && event.key === "1") {
				event.preventDefault();
				onActualSize?.();
				return;
			}

			// Export: Cmd/Ctrl + E
			if (isMod && event.key === "e") {
				event.preventDefault();
				onExport?.();
				return;
			}

			// Toggle filters: Cmd/Ctrl + F
			if (isMod && event.key === "f") {
				event.preventDefault();
				onToggleFilters?.();
				return;
			}

			// Reset: Cmd/Ctrl + R
			if (isMod && isShift && event.key === "r") {
				event.preventDefault();
				onReset?.();
				return;
			}

			// Fullscreen: F or F11
			if (event.key === "f" && !isMod) {
				event.preventDefault();
				onFullscreen?.();
				return;
			}

			// Toggle detail panel: P
			if (event.key === "p" && !isMod) {
				event.preventDefault();
				onToggleDetailPanel?.();
				return;
			}

			// Toggle mini-map: M
			if (event.key === "m" && !isMod) {
				event.preventDefault();
				onToggleMiniMap?.();
				return;
			}
		},
		[
			enabled,
			onFitView,
			onZoomIn,
			onZoomOut,
			onActualSize,
			onFullscreen,
			onToggleDetailPanel,
			onToggleMiniMap,
			onExport,
			onToggleFilters,
			onReset,
			fitView,
			zoomIn,
			zoomOut,
		],
	);

	useEffect(() => {
		if (!enabled) return;

		window.addEventListener("keydown", handleKeyDown);
		return () => window.removeEventListener("keydown", handleKeyDown);
	}, [handleKeyDown, enabled]);
}

// Keyboard shortcuts reference
export const KEYBOARD_SHORTCUTS = {
	zoom: {
		in: "Cmd/Ctrl + Plus",
		out: "Cmd/Ctrl + Minus",
		fit: "Cmd/Ctrl + 0",
		actualSize: "Cmd/Ctrl + 1",
	},
	view: {
		fullscreen: "F",
		detailPanel: "P",
		miniMap: "M",
	},
	actions: {
		export: "Cmd/Ctrl + E",
		filters: "Cmd/Ctrl + F",
		reset: "Cmd/Ctrl + Shift + R",
	},
} as const;
