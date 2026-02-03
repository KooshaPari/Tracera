import { useLocation, useNavigate } from "@tanstack/react-router";
import {
	Activity,
	ChevronRight,
	ClipboardCheck,
	Code,
	Command,
	FileCode,
	FileText,
	FolderOpen,
	Home,
	Layers,
	Settings,
	Shield,
	Zap,
} from "lucide-react";
import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
	announceToScreenReader,
	restoreFocus,
	saveFocus,
} from "@/lib/focus-management";
import { cn } from "@/lib/utils";

interface CommandItem {
	id: string;
	title: string;
	description?: string;
	icon: React.ComponentType<{ className?: string }>;
	action: () => void;
	keywords?: string[];
	category: "NAVIGATE" | "VIEWS" | "SYSTEM" | "ACTIONS" | "SPECS";
}

function CommandPaletteComponent() {
	const [open, setOpen] = useState(false);
	const [query, setQuery] = useState("");
	const [selected, setSelected] = useState(0);
	const savedFocusRef = useRef<HTMLElement | null>(null);
	const inputRef = useRef<HTMLInputElement>(null);
	const listboxRef = useRef<HTMLDivElement>(null);
	const navigate = useNavigate();
	const location = useLocation();

	const pathname = location?.pathname ?? "";
	const projectIdMatch = pathname.match(/\/projects\/([^/]+)/);
	const currentProjectId = projectIdMatch ? projectIdMatch[1] : null;

	const commands: CommandItem[] = useMemo(() => {
		const baseCommands: CommandItem[] = [
			{
				action: () => navigate({ to: "/home" }),
				category: "NAVIGATE",
				description: "Main operational dashboard",
				icon: Home,
				id: "nav-home",
				keywords: ["home", "dashboard"],
				title: "Mission Control",
			},
			{
				action: () => navigate({ to: "/projects" }),
				category: "NAVIGATE",
				description: "All active graph containers",
				icon: FolderOpen,
				id: "nav-projects",
				keywords: ["projects", "list"],
				title: "Project Registry",
			},
			{
				action: () => navigate({ to: "/settings" }),
				category: "SYSTEM",
				description: "Core configuration panel",
				icon: Settings,
				id: "sys-settings",
				keywords: ["settings", "config"],
				title: "System Parameters",
			},
		];

		if (currentProjectId) {
			const projectViews: CommandItem[] = [
				{
					action: () =>
						navigate({
							params: { projectId: currentProjectId, viewType: "feature" },
							to: "/projects/$projectId/views/$viewType",
						}),
					category: "VIEWS",
					description: "Logic & requirements",
					icon: Layers,
					id: "view-feature",
					title: "Feature Layer",
				},
				{
					action: () =>
						navigate({
							params: { projectId: currentProjectId, viewType: "code" },
							to: "/projects/$projectId/views/$viewType",
						}),
					category: "VIEWS",
					description: "Repository links",
					icon: Code,
					id: "view-code",
					title: "Source Mapping",
				},
				{
					action: () =>
						navigate({
							params: { projectId: currentProjectId, viewType: "test" },
							to: "/projects/$projectId/views/$viewType",
						}),
					category: "VIEWS",
					description: "Test coverage matrix",
					icon: Shield,
					id: "view-test",
					title: "Validation Suite",
				},
				{
					action: () =>
						navigate({
							params: { projectId: currentProjectId, viewType: "workflows" },
							to: "/projects/$projectId/views/$viewType",
						}),
					category: "VIEWS",
					description: "Temporal runs and schedules",
					icon: Activity,
					id: "view-workflows",
					title: "Workflow Runs",
				},
			];

			const specCommands: CommandItem[] = [
				{
					action: () =>
						navigate({
							params: { projectId: currentProjectId },
							to: "/projects/$projectId/specifications",
						}),
					category: "SPECS",
					description: "View all specifications",
					icon: FileCode,
					id: "specs-dashboard",
					keywords: ["specifications", "specs", "dashboard"],
					title: "Specifications Dashboard",
				},
				{
					action: () =>
						navigate({
							params: { projectId: currentProjectId },
							search: { tab: "adrs" },
							to: "/projects/$projectId/specifications",
						}),
					category: "SPECS",
					description: "ADRs for this project",
					icon: FileText,
					id: "specs-adr",
					keywords: ["adr", "architecture", "decision"],
					title: "Architecture Decision Records",
				},
				{
					action: () =>
						navigate({
							params: { projectId: currentProjectId },
							search: { tab: "contracts" },
							to: "/projects/$projectId/specifications",
						}),
					category: "SPECS",
					description: "Service and API contracts",
					icon: ClipboardCheck,
					id: "specs-contracts",
					keywords: ["contract", "api", "service"],
					title: "Contracts",
				},
				{
					action: () =>
						navigate({
							params: { projectId: currentProjectId },
							search: { tab: "compliance" },
							to: "/projects/$projectId/specifications",
						}),
					category: "SPECS",
					description: "Compliance and regulatory requirements",
					icon: Shield,
					id: "specs-compliance",
					keywords: ["compliance", "regulatory", "requirements"],
					title: "Compliance",
				},
				{
					action: () =>
						navigate({
							params: { projectId: currentProjectId },
							to: "/projects/$projectId/scenario-activity",
						}),
					category: "SPECS",
					description: "Scenario execution and history",
					icon: Activity,
					id: "specs-scenario-activity",
					keywords: ["scenario", "activity", "history", "execution"],
					title: "Scenario Activity",
				},
			];

			return [...baseCommands, ...projectViews, ...specCommands];
		}

		return baseCommands;
	}, [navigate, currentProjectId]);

	const filtered = useMemo(() => {
		if (!query) {
			return commands;
		}
		const q = query.toLowerCase();
		return commands.filter(
			(c) =>
				c.title.toLowerCase().includes(q) ||
				c.description?.toLowerCase().includes(q) ||
				c.keywords?.some((k) => k.includes(q)),
		);
	}, [query, commands]);

	const handleKeyDown = useCallback(
		(e: globalThis.KeyboardEvent) => {
			if ((e.metaKey || e.ctrlKey) && e.key === "k") {
				e.preventDefault();
				setOpen((o) => !o);
				setQuery("");
				setSelected(0);
				return;
			}
			if (!open) {
				return;
			}

			switch (e.key) {
				case "Escape": {
					e.preventDefault();
					setOpen(false);
					setQuery("");
					break;
				}
				case "ArrowDown": {
					e.preventDefault();
					setSelected((s) => Math.min(s + 1, filtered.length - 1));
					break;
				}
				case "ArrowUp": {
					e.preventDefault();
					setSelected((s) => Math.max(s - 1, 0));
					break;
				}
				case "Home": {
					e.preventDefault();
					setSelected(0);
					break;
				}
				case "End": {
					e.preventDefault();
					setSelected(Math.max(filtered.length - 1, 0));
					break;
				}
				case "Enter": {
					e.preventDefault();
					if (filtered[selected]) {
						filtered[selected].action();
						setOpen(false);
						setQuery("");
					}
					break;
				}
				case "Tab": {
					// Allow Tab to escape palette naturally
					setOpen(false);
					setQuery("");
					break;
				}
			}
		},
		[open, filtered, selected],
	);

	// Handle focus management when opening/closing
	useEffect(() => {
		globalThis.addEventListener("keydown", handleKeyDown);

		if (open) {
			// Save focus to restore later
			savedFocusRef.current = saveFocus();
			// Focus input after palette opens
			setTimeout(() => {
				inputRef.current?.focus();
				announceToScreenReader(
					`Command palette opened. Type to search commands. ${filtered.length} result${filtered.length !== 1 ? "s" : ""} available.`,
					"polite",
				);
			}, 50);
		} else if (savedFocusRef.current) {
			// Restore focus when closing
			restoreFocus(savedFocusRef.current);
		}

		return () => globalThis.removeEventListener("keydown", handleKeyDown);
	}, [handleKeyDown, open, filtered.length]);

	// Announce when search results change
	useEffect(() => {
		if (open && query) {
			announceToScreenReader(
				`${filtered.length} result${filtered.length !== 1 ? "s" : ""} found for "${query}". Use arrow keys to navigate, Enter to select.`,
				"polite",
			);
		}
	}, [filtered, query, open]);

	if (!open) {
		return null;
	}

	const categories = [
		"NAVIGATE",
		"VIEWS",
		"SPECS",
		"SYSTEM",
		"ACTIONS",
	] as const;

	const selectedItem = filtered[selected];
	const selectedId = selectedItem ? `cmd-item-${selectedItem.id}` : "";

	return (
		<div
			className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] px-4 animate-in fade-in duration-300"
			onClick={() => setOpen(false)}
			aria-hidden="true"
		>
			<div
				className="fixed inset-0 bg-background/80 backdrop-blur-sm"
				aria-hidden="true"
			/>
			<div
				className="relative w-full max-w-2xl bg-card border border-border/50 shadow-2xl rounded-[2rem] overflow-hidden animate-in zoom-in-95 slide-in-from-top-4 duration-300 ring-1 ring-primary/20 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
				onClick={(e) => e.stopPropagation()}
				role="dialog"
				aria-modal="true"
				aria-labelledby="command-palette-title"
			>
				{/* Top Command Bar */}
				<div className="flex items-center gap-4 px-6 py-5 border-b bg-muted/30">
					<Command
						className="h-6 w-6 text-primary animate-pulse"
						aria-hidden="true"
					/>
					<div className="flex-1 flex flex-col gap-1">
						<label
							htmlFor="command-input"
							className="sr-only"
							id="command-palette-title"
						>
							Command Palette
						</label>
						<input
							ref={inputRef}
							id="command-input"
							type="text"
							placeholder="Execute command or jump to view..."
							value={query}
							onChange={(e) => setQuery(e.target.value)}
							aria-label="Search commands"
							aria-describedby="command-hint"
							aria-expanded={open}
							aria-controls="command-listbox"
							aria-activedescendant={selectedId}
							role="combobox"
							autoComplete="off"
							className="flex-1 bg-transparent text-xl font-black uppercase tracking-tight outline-none placeholder:text-muted-foreground/50 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
						/>
						<span id="command-hint" className="sr-only">
							{filtered.length > 0
								? `${filtered.length} result${filtered.length !== 1 ? "s" : ""} found. Use arrow keys to navigate, Enter to select, Home/End to jump, Escape to close.`
								: "Type to search. No results found."}
						</span>
					</div>
					<div className="flex items-center gap-1.5">
						<kbd className="h-6 px-2 rounded-lg border bg-background flex items-center justify-center text-[10px] font-black uppercase shadow-sm">
							ESC
						</kbd>
					</div>
				</div>

				{/* Results Surface */}
				<div
					ref={listboxRef}
					id="command-listbox"
					role="listbox"
					className="max-h-[50vh] overflow-y-auto p-3 custom-scrollbar"
				>
					{categories.map((cat) => {
						const items = filtered.filter((c) => c.category === cat);
						if (items.length === 0) {
							return null;
						}

						return (
							<div key={cat} className="space-y-1 mb-4 last:mb-0">
								<div className="px-4 py-2 text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground/60">
									{cat}
								</div>
								{items.map((cmd) => {
									const globalIndex = filtered.indexOf(cmd);
									const isSelected = globalIndex === selected;
									const itemId = `cmd-item-${cmd.id}`;

									return (
										<button
											key={cmd.id}
											id={itemId}
											onClick={() => {
												cmd.action();
												setOpen(false);
												setQuery("");
											}}
											onMouseEnter={() => setSelected(globalIndex)}
											role="option"
											aria-selected={isSelected}
											aria-describedby={`${itemId}-desc`}
											className={cn(
												"group flex w-full items-center gap-4 rounded-2xl px-4 py-3 text-left transition-all duration-200 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 active:scale-[0.98]",
												isSelected
													? "bg-primary text-primary-foreground shadow-lg shadow-primary/20 translate-x-1"
													: "hover:bg-muted/50",
											)}
										>
											<div
												className={cn(
													"h-10 w-10 rounded-xl flex items-center justify-center shrink-0 transition-colors",
													isSelected
														? "bg-primary-foreground/20"
														: "bg-muted text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary",
												)}
												aria-hidden="true"
											>
												<cmd.icon className="h-5 w-5" />
											</div>
											<div className="flex-1 min-w-0">
												<div className="font-bold text-sm tracking-tight">
													{cmd.title}
												</div>
												{cmd.description && (
													<div
														id={`${itemId}-desc`}
														className={cn(
															"text-[10px] font-bold uppercase tracking-widest leading-none mt-1",
															isSelected
																? "text-primary-foreground/60"
																: "text-muted-foreground",
														)}
													>
														{cmd.description}
													</div>
												)}
											</div>
											{isSelected && (
												<div
													className="flex items-center gap-2 pr-2 animate-in slide-in-from-left-2"
													aria-hidden="true"
												>
													<span className="text-[9px] font-black uppercase tracking-tighter opacity-60">
														Execute
													</span>
													<ChevronRight className="h-4 w-4" />
												</div>
											)}
										</button>
									);
								})}
							</div>
						);
					})}

					{filtered.length === 0 && (
						<div
							className="flex flex-col items-center justify-center py-20 text-muted-foreground/40"
							role="status"
							aria-live="polite"
							aria-atomic="true"
						>
							<Zap className="h-12 w-12 mb-4 opacity-10" aria-hidden="true" />
							<p className="text-xs font-black uppercase tracking-[0.2em]">
								Zero Command Matches
							</p>
							{query && (
								<p className="text-[10px] text-muted-foreground/30 mt-2">
									No results for "{query}"
								</p>
							)}
						</div>
					)}
				</div>

				{/* Global Shortcuts Hint */}
				<div className="border-t bg-muted/20 px-6 py-4 flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">
					<div className="flex items-center gap-6">
						<span className="flex items-center gap-2">
							<kbd className="h-5 px-1.5 rounded border bg-background shadow-sm">
								↑↓
							</kbd>
							NAVIGATE
						</span>
						<span className="flex items-center gap-2">
							<kbd className="h-5 px-1.5 rounded border bg-background shadow-sm">
								↵
							</kbd>
							CONFIRM
						</span>
					</div>
					<div className="flex items-center gap-2">
						<div className="h-1.5 w-1.5 rounded-full bg-green-500" />
						READY
					</div>
				</div>
			</div>
		</div>
	);
}

export const CommandPalette = memo(CommandPaletteComponent);
