import { X } from "lucide-react";
import { useEffect } from "react";

import { formatKeyboardShortcut, type KeyboardShortcut } from "@/hooks";
import { cn } from "@/lib/utils";

interface KeyboardShortcutsModalProps {
	isOpen: boolean;
	onClose: () => void;
	shortcuts: KeyboardShortcut[];
}

const categoryLabels: Record<string, string> = {
	navigation: "Navigation",
	selection: "Selection",
	editing: "Editing",
	system: "System",
};

const categoryIcons: Record<string, string> = {
	navigation: "🧭",
	selection: "☑️",
	editing: "✏️",
	system: "⚙️",
};

export function KeyboardShortcutsModal({
	isOpen,
	onClose,
	shortcuts,
}: KeyboardShortcutsModalProps) {
	useEffect(() => {
		const handler = (event: KeyboardEvent) => {
			if (event.key === "Escape" && isOpen) {
				event.preventDefault();
				onClose();
			}
		};

		if (isOpen) {
			window.addEventListener("keydown", handler);
			return () => window.removeEventListener("keydown", handler);
		}
	}, [isOpen, onClose]);

	if (!isOpen) return null;

	// Group shortcuts by category
	const grouped = shortcuts.reduce(
		(acc, shortcut) => {
			const category = shortcut.category || "system";
			if (!acc[category]) {
				acc[category] = [];
			}
			acc[category].push(shortcut);
			return acc;
		},
		{} as Record<string, KeyboardShortcut[]>,
	);

	return (
		<div
			className="fixed inset-0 z-[101] flex items-center justify-center px-4"
			onClick={onClose}
		>
			<div className="fixed inset-0 bg-background/80 backdrop-blur-sm" />

			<div
				className="relative w-full max-w-3xl bg-card border border-border/50 shadow-2xl rounded-[2rem] overflow-hidden animate-in zoom-in-95 slide-in-from-top-4 duration-300 ring-1 ring-primary/20 max-h-[85vh] flex flex-col"
				onClick={(e) => e.stopPropagation()}
			>
				{/* Header */}
				<div className="flex items-center justify-between px-8 py-6 border-b bg-muted/30">
					<div>
						<h2 className="text-2xl font-black uppercase tracking-tight">
							⌨️ Keyboard Shortcuts
						</h2>
						<p className="text-xs font-bold uppercase tracking-widest text-muted-foreground mt-1">
							Master power user commands
						</p>
					</div>
					<button
						onClick={onClose}
						className="p-2 hover:bg-muted rounded-lg transition-colors"
						aria-label="Close shortcuts modal"
					>
						<X className="h-6 w-6" />
					</button>
				</div>

				{/* Content */}
				<div className="overflow-y-auto flex-1 custom-scrollbar">
					<div className="p-8 space-y-8">
						{Object.entries(categoryLabels).map(
							([categoryKey, categoryLabel]) => {
								const categoryShortcuts = grouped[categoryKey] || [];
								if (categoryShortcuts.length === 0) return null;

								return (
									<div key={categoryKey}>
										<div className="flex items-center gap-3 mb-4">
											<span className="text-2xl">
												{categoryIcons[categoryKey] || "•"}
											</span>
											<h3 className="text-sm font-black uppercase tracking-[0.2em] text-muted-foreground">
												{categoryLabel}
											</h3>
											<div className="flex-1 h-px bg-border/50" />
										</div>

										<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
											{categoryShortcuts.map((shortcut, idx) => (
												<div
													key={idx}
													className="flex items-start justify-between gap-4 p-4 rounded-xl bg-muted/20 border border-border/30 hover:border-border/50 hover:bg-muted/40 transition-colors"
												>
													<div className="flex-1 min-w-0">
														<p className="font-bold text-sm leading-tight">
															{shortcut.description}
														</p>
														{shortcut.context && (
															<p className="text-[11px] text-muted-foreground mt-1 font-bold uppercase tracking-widest">
																Context: {shortcut.context}
															</p>
														)}
													</div>
													<div className="flex items-center gap-2 shrink-0">
														{formatKeyboardShortcut(shortcut)
															.split("+")
															.map((part, i) => (
																<div key={i}>
																	{i > 0 && (
																		<span className="text-xs text-muted-foreground mx-1">
																			+
																		</span>
																	)}
																	<kbd
																		className={cn(
																			"px-2.5 py-1.5 rounded-lg border font-bold text-[11px] uppercase tracking-widest whitespace-nowrap inline-block",
																			part === "+"
																				? "hidden"
																				: "bg-background border-border/60 shadow-sm",
																		)}
																	>
																		{part}
																	</kbd>
																</div>
															))}
													</div>
												</div>
											))}
										</div>
									</div>
								);
							},
						)}
					</div>
				</div>

				{/* Footer */}
				<div className="border-t bg-muted/20 px-8 py-4 flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">
					<span>Press ESC or ? to close</span>
					<div className="flex items-center gap-2">
						<div className="h-1.5 w-1.5 rounded-full bg-green-500" />
						<span>{shortcuts.length} Shortcuts Available</span>
					</div>
				</div>
			</div>
		</div>
	);
}
