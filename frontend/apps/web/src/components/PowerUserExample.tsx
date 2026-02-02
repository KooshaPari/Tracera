/**
 * PowerUserExample Component
 *
 * This example demonstrates how to integrate all power user productivity features:
 * - Keyboard shortcuts (Cmd+K, Cmd+N, Cmd+F, /)
 * - Undo/Redo (Cmd+Z, Cmd+Shift+Z)
 * - Bulk selection and actions
 * - Shortcuts help modal (?)
 *
 * NOTE: This is an example/documentation component. To use these features:
 * 1. Import the hooks in your component
 * 2. Set up keyboard shortcuts with useKeyboardShortcuts
 * 3. Use useBulkSelection for item selection
 * 4. Render KeyboardShortcutsModal and BulkActionToolbar
 */

import { Plus, Trash2 } from "lucide-react";
import { useCallback, useState } from "react";
import { toast } from "sonner";
import { BulkActionToolbar, KeyboardShortcutsModal } from "@/components";
import {
	type KeyboardShortcutAction,
	useBulkSelection,
	useKeyboardShortcuts,
	useUndoRedo,
} from "@/hooks";

interface Item {
	id: string;
	title: string;
	checked: boolean;
}

interface ItemListState {
	items: Item[];
}

export function PowerUserExample() {
	const [searchQuery, setSearchQuery] = useState("");

	// Initialize undo/redo with list state
	const {
		state: listState,
		setState: setListState,
		undo,
		redo,
		canUndo,
		canRedo,
	} = useUndoRedo<ItemListState>({
		items: [
			{ id: "1", title: "Learn Keyboard Shortcuts", checked: false },
			{ id: "2", title: "Use Bulk Selection", checked: false },
			{ id: "3", title: "Master Undo/Redo", checked: false },
		],
	});

	// Bulk selection management
	const bulkSelection = useBulkSelection();

	// Define keyboard shortcuts
	const shortcuts: KeyboardShortcutAction[] = [
		{
			key: "n",
			meta: true,
			description: "Create new item",
			category: "editing",
			action: useCallback(() => {
				const newItem: Item = {
					id: Date.now().toString(),
					title: "New Item",
					checked: false,
				};
				const newState = {
					items: [...listState.items, newItem],
				};
				setListState(newState, "Created new item");
				toast.success("New item created");
			}, [listState, setListState]),
		},
		{
			key: "f",
			meta: true,
			description: "Focus search",
			category: "navigation",
			action: useCallback(() => {
				const searchInput = document.getElementById("search-input");
				searchInput?.focus();
				toast.info("Focus on search");
			}, []),
		},
		{
			key: "/",
			description: "Focus search with slash",
			category: "navigation",
			action: useCallback(() => {
				const searchInput = document.getElementById("search-input");
				searchInput?.focus();
				setSearchQuery("/");
			}, []),
		},
		{
			key: "z",
			meta: true,
			description: "Undo last action",
			category: "editing",
			action: useCallback(() => {
				if (canUndo) {
					undo();
					toast.success("Undo");
				}
			}, [canUndo, undo]),
		},
		{
			key: "z",
			meta: true,
			shift: true,
			description: "Redo last action",
			category: "editing",
			action: useCallback(() => {
				if (canRedo) {
					redo();
					toast.success("Redo");
				}
			}, [canRedo, redo]),
		},
		{
			key: "a",
			meta: true,
			description: "Select all items",
			category: "selection",
			context: "Items view",
			action: useCallback(() => {
				bulkSelection.selectAll(listState.items.map((item) => item.id));
				toast.success(`Selected ${listState.items.length} items`);
			}, [listState.items, bulkSelection]),
		},
		{
			key: "Delete",
			description: "Bulk delete selected items",
			category: "selection",
			action: useCallback(async () => {
				if (bulkSelection.selectedIds.length === 0) {
					toast.error("No items selected");
					return;
				}

				const newItems = listState.items.filter(
					(item) => !bulkSelection.selectedIds.includes(item.id),
				);
				setListState(
					{ items: newItems },
					`Deleted ${bulkSelection.selectedIds.length} items`,
				);
				bulkSelection.deselectAll();
				toast.success("Items deleted");
			}, [listState, bulkSelection, setListState]),
		},
	];

	// Setup keyboard shortcuts and modal
	const {
		isShortcutsModalOpen,
		setIsShortcutsModalOpen,
		allShortcuts,
	} = useKeyboardShortcuts(shortcuts);

	// Handle item toggle
	const toggleItem = useCallback(
		(id: string) => {
			const newItems = listState.items.map((item) =>
				item.id === id ? { ...item, checked: !item.checked } : item,
			);
			setListState({ items: newItems }, "Toggled item");
		},
		[listState, setListState],
	);

	// Handle bulk delete
	const handleBulkDelete = useCallback(async () => {
		const newItems = listState.items.filter(
			(item) => !bulkSelection.selectedIds.includes(item.id),
		);
		setListState(
			{ items: newItems },
			`Deleted ${bulkSelection.selectedIds.length} items`,
		);
		bulkSelection.deselectAll();
		toast.success(`${bulkSelection.selectedIds.length} items deleted`);
	}, [listState, bulkSelection, setListState]);

	const deleteAction = {
		id: "delete",
		label: "Delete",
		icon: <Trash2 className="h-4 w-4" />,
		action: handleBulkDelete,
		variant: "destructive" as const,
	};

	const handleSelectAll = useCallback(() => {
		bulkSelection.selectAll(listState.items.map((item) => item.id));
	}, [listState.items, bulkSelection]);

	const handleSelectNone = useCallback(() => {
		bulkSelection.deselectAll();
	}, [bulkSelection]);

	// Filter items by search
	const filteredItems = listState.items.filter((item) =>
		item.title.toLowerCase().includes(searchQuery.toLowerCase()),
	);

	return (
		<div className="w-full max-w-2xl mx-auto p-6 space-y-6">
			{/* Header */}
			<div className="space-y-2">
				<h1 className="text-2xl font-bold">Power User Features Demo</h1>
				<p className="text-sm text-muted-foreground">
					Try the keyboard shortcuts below! Press{" "}
					<kbd className="px-2 py-1 rounded border bg-muted">?</kbd> to see all
					shortcuts.
				</p>
			</div>

			{/* Undo/Redo Controls */}
			<div className="flex gap-2">
				<button
					onClick={undo}
					disabled={!canUndo}
					className="px-3 py-2 rounded bg-primary/10 text-primary disabled:opacity-50 disabled:cursor-not-allowed text-sm font-bold"
				>
					↶ Undo (Cmd+Z)
				</button>
				<button
					onClick={redo}
					disabled={!canRedo}
					className="px-3 py-2 rounded bg-primary/10 text-primary disabled:opacity-50 disabled:cursor-not-allowed text-sm font-bold"
				>
					↷ Redo (Cmd+Shift+Z)
				</button>
				<button
					onClick={() => setIsShortcutsModalOpen(true)}
					className="px-3 py-2 rounded bg-primary/10 text-primary hover:bg-primary/20 text-sm font-bold ml-auto"
				>
					⌨️ Shortcuts (?)
				</button>
			</div>

			{/* Search Input */}
			<div>
				<input
					id="search-input"
					type="text"
					placeholder="Search items... (Cmd+F)"
					value={searchQuery}
					onChange={(e) => setSearchQuery(e.target.value)}
					className="w-full px-4 py-2 rounded border bg-background"
				/>
				<p className="text-xs text-muted-foreground mt-1">
					Try pressing{" "}
					<kbd className="px-2 py-1 rounded border bg-muted">/</kbd> to focus
				</p>
			</div>

			{/* Items List with Bulk Selection */}
			<div className="space-y-2 border rounded-lg p-4 bg-muted/20">
				<div className="flex items-center justify-between mb-4">
					<h2 className="font-bold">Items ({filteredItems.length})</h2>
					<button
						onClick={() => {
							const newItem: Item = {
								id: Date.now().toString(),
								title: "New Item",
								checked: false,
							};
							const newState = {
								items: [...listState.items, newItem],
							};
							setListState(newState, "Created new item");
							toast.success("New item created");
						}}
						className="flex items-center gap-2 px-3 py-1 rounded bg-primary/10 text-primary hover:bg-primary/20 text-sm font-bold"
					>
						<Plus className="h-4 w-4" />
						New (Cmd+N)
					</button>
				</div>

				<div className="space-y-2">
					{filteredItems.map((item) => (
						<div
							key={item.id}
							className="flex items-center gap-3 p-3 rounded bg-background hover:bg-muted/30 transition-colors"
						>
							<input
								type="checkbox"
								checked={bulkSelection.isSelected(item.id)}
								onChange={() => bulkSelection.toggle(item.id)}
								className="rounded"
							/>
							<input
								type="checkbox"
								checked={item.checked}
								onChange={() => toggleItem(item.id)}
								className="rounded"
							/>
							<span
								className={
									item.checked ? "line-through text-muted-foreground" : ""
								}
							>
								{item.title}
							</span>
						</div>
					))}
				</div>
			</div>

			{/* Keyboard Shortcuts Modal */}
			<KeyboardShortcutsModal
				isOpen={isShortcutsModalOpen}
				onClose={() => setIsShortcutsModalOpen(false)}
				shortcuts={allShortcuts}
			/>

			{/* Bulk Actions Toolbar */}
			<BulkActionToolbar
				selectedCount={bulkSelection.count}
				totalCount={listState.items.length}
				onSelectAll={handleSelectAll}
				onSelectNone={handleSelectNone}
				actions={[deleteAction]}
			/>

			{/* Feature Info */}
			<div className="bg-blue-50/50 dark:bg-blue-950/20 p-4 rounded-lg space-y-2 text-sm">
				<p className="font-bold">Features Demonstrated:</p>
				<ul className="space-y-1 text-sm text-muted-foreground">
					<li>
						✓ <strong>Keyboard Shortcuts:</strong> Cmd+K, Cmd+N, Cmd+F, Cmd+A, /
					</li>
					<li>
						✓ <strong>Undo/Redo:</strong> Cmd+Z, Cmd+Shift+Z with history
						tracking
					</li>
					<li>
						✓ <strong>Bulk Selection:</strong> Checkboxes, select all/none
					</li>
					<li>
						✓ <strong>Bulk Actions:</strong> Toolbar with delete action
					</li>
					<li>
						✓ <strong>Shortcuts Modal:</strong> Press ? to view all shortcuts
					</li>
				</ul>
			</div>
		</div>
	);
}
