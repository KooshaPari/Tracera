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
	GitBranch,
	Home,
	Layers,
	Settings,
	Shield,
	Zap,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { cn } from "@/lib/utils";

interface CommandItem {
	id: string;
	title: string;
	description?: string;
	icon: any;
	action: () => void;
	keywords?: string[];
	category: "NAVIGATE" | "VIEWS" | "SYSTEM" | "ACTIONS" | "SPECS";
}

export function CommandPalette() {
	const [open, setOpen] = useState(false);
	const [query, setQuery] = useState("");
	const [selected, setSelected] = useState(0);
	const navigate = useNavigate();
	const location = useLocation();

	const projectIdMatch = location.pathname.match(/\/projects\/([^/]+)/);
	const currentProjectId = projectIdMatch ? projectIdMatch[1] : null;

	const commands: CommandItem[] = useMemo(() => {
		const baseCommands: CommandItem[] = [
			{
				id: "nav-home",
				title: "Mission Control",
				description: "Main operational dashboard",
				icon: Home,
				action: () => navigate({ to: "/" }),
				category: "NAVIGATE",
				keywords: ["home", "dashboard"],
			},
			{
				id: "nav-projects",
				title: "Project Registry",
				description: "All active graph containers",
				icon: FolderOpen,
				action: () => navigate({ to: "/projects" }),
				category: "NAVIGATE",
				keywords: ["projects", "list"],
			},
			{
				id: "view-graph",
				title: "Neural Graph",
				description: "Global traceability network",
				icon: GitBranch,
				action: () => navigate({ to: "/graph" }),
				category: "NAVIGATE",
				keywords: ["graph", "trace", "link"],
			},
			{
				id: "sys-settings",
				title: "System Parameters",
				description: "Core configuration panel",
				icon: Settings,
				action: () => navigate({ to: "/settings" }),
				category: "SYSTEM",
				keywords: ["settings", "config"],
			},
		];

		if (currentProjectId) {
			const projectViews: CommandItem[] = [
				{
					id: "view-feature",
					title: "Feature Layer",
					description: "Logic & requirements",
					icon: Layers,
					action: () =>
						navigate({
							to: "/projects/$projectId/views/$viewType",
							params: { projectId: currentProjectId, viewType: "feature" },
						}),
					category: "VIEWS",
				},
				{
					id: "view-code",
					title: "Source Mapping",
					description: "Repository links",
					icon: Code,
					action: () =>
						navigate({
							to: "/projects/$projectId/views/$viewType",
							params: { projectId: currentProjectId, viewType: "code" },
						}),
					category: "VIEWS",
				},
				{
					id: "view-test",
					title: "Validation Suite",
					description: "Test coverage matrix",
					icon: Shield,
					action: () =>
						navigate({
							to: "/projects/$projectId/views/$viewType",
							params: { projectId: currentProjectId, viewType: "test" },
						}),
					category: "VIEWS",
				},
				{
					id: "view-workflows",
					title: "Workflow Runs",
					description: "Hatchet runs and schedules",
					icon: Activity,
					action: () =>
						navigate({
							to: "/projects/$projectId/views/$viewType",
							params: { projectId: currentProjectId, viewType: "workflows" },
						}),
					category: "VIEWS",
				},
			];

			const specCommands: CommandItem[] = [
				{
					id: "specs-dashboard",
					title: "Specifications Dashboard",
					description: "View all specifications",
					icon: FileCode,
					action: () =>
						navigate({
							to: "/projects/$projectId/specifications",
							params: { projectId: currentProjectId },
						}),
					category: "SPECS",
					keywords: ["specifications", "specs", "dashboard"],
				},
				{
					id: "specs-adr",
					title: "Architecture Decision Records",
					description: "ADRs for this project",
					icon: FileText,
					action: () =>
						navigate({
							to: "/projects/$projectId/specifications",
							params: { projectId: currentProjectId },
							search: { tab: "adrs" },
						}),
					category: "SPECS",
					keywords: ["adr", "architecture", "decision"],
				},
				{
					id: "specs-contracts",
					title: "Contracts",
					description: "Service and API contracts",
					icon: ClipboardCheck,
					action: () =>
						navigate({
							to: "/projects/$projectId/specifications",
							params: { projectId: currentProjectId },
							search: { tab: "contracts" },
						}),
					category: "SPECS",
					keywords: ["contract", "api", "service"],
				},
				{
					id: "specs-compliance",
					title: "Compliance",
					description: "Compliance and regulatory requirements",
					icon: Shield,
					action: () =>
						navigate({
							to: "/projects/$projectId/specifications",
							params: { projectId: currentProjectId },
							search: { tab: "compliance" },
						}),
					category: "SPECS",
					keywords: ["compliance", "regulatory", "requirements"],
				},
			];

			return [...baseCommands, ...projectViews, ...specCommands];
		}

		return baseCommands;
	}, [navigate, currentProjectId]);

	const filtered = useMemo(() => {
		if (!query) return commands;
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
			}
			if (!open) return;
			if (e.key === "Escape") {
				setOpen(false);
				setQuery("");
			}
			if (e.key === "ArrowDown") {
				e.preventDefault();
				setSelected((s) => Math.min(s + 1, filtered.length - 1));
			}
			if (e.key === "ArrowUp") {
				e.preventDefault();
				setSelected((s) => Math.max(s - 1, 0));
			}
			if (e.key === "Enter" && filtered[selected]) {
				filtered[selected].action();
				setOpen(false);
				setQuery("");
			}
		},
		[open, filtered, selected],
	);

	useEffect(() => {
		window.addEventListener("keydown", handleKeyDown);
		return () => window.removeEventListener("keydown", handleKeyDown);
	}, [handleKeyDown]);

	if (!open) return null;

	const categories = [
		"NAVIGATE",
		"VIEWS",
		"SPECS",
		"SYSTEM",
		"ACTIONS",
	] as const;

	return (
		<div
			className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] px-4 animate-in fade-in duration-300"
			onClick={() => setOpen(false)}
		>
			<div className="fixed inset-0 bg-background/80 backdrop-blur-sm" />
			<div
				className="relative w-full max-w-2xl bg-card border border-border/50 shadow-2xl rounded-[2rem] overflow-hidden animate-in zoom-in-95 slide-in-from-top-4 duration-300 ring-1 ring-primary/20"
				onClick={(e) => e.stopPropagation()}
			>
				{/* Top Command Bar */}
				<div className="flex items-center gap-4 px-6 py-5 border-b bg-muted/30">
					<Command className="h-6 w-6 text-primary animate-pulse" />
					<input
						type="text"
						placeholder="Execute command or jump to view..."
						value={query}
						onChange={(e) => setQuery(e.target.value)}
						className="flex-1 bg-transparent text-xl font-black uppercase tracking-tight outline-none placeholder:text-muted-foreground/50"
					/>
					<div className="flex items-center gap-1.5">
						<kbd className="h-6 px-2 rounded-lg border bg-background flex items-center justify-center text-[10px] font-black uppercase shadow-sm">
							ESC
						</kbd>
					</div>
				</div>

				{/* Results Surface */}
				<div className="max-h-[50vh] overflow-y-auto p-3 custom-scrollbar">
					{categories.map((cat) => {
						const items = filtered.filter((c) => c.category === cat);
						if (items.length === 0) return null;

						return (
							<div key={cat} className="space-y-1 mb-4 last:mb-0">
								<div className="px-4 py-2 text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground/60">
									{cat}
								</div>
								{items.map((cmd) => {
									const globalIndex = filtered.indexOf(cmd);
									const isSelected = globalIndex === selected;

									return (
										<button
											key={cmd.id}
											onClick={() => {
												cmd.action();
												setOpen(false);
												setQuery("");
											}}
											onMouseEnter={() => setSelected(globalIndex)}
											className={cn(
												"group flex w-full items-center gap-4 rounded-2xl px-4 py-3 text-left transition-all duration-200",
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
											>
												<cmd.icon className="h-5 w-5" />
											</div>
											<div className="flex-1 min-w-0">
												<div className="font-bold text-sm tracking-tight">
													{cmd.title}
												</div>
												{cmd.description && (
													<div
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
												<div className="flex items-center gap-2 pr-2 animate-in slide-in-from-left-2">
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
						<div className="flex flex-col items-center justify-center py-20 text-muted-foreground/40">
							<Zap className="h-12 w-12 mb-4 opacity-10" />
							<p className="text-xs font-black uppercase tracking-[0.2em]">
								Zero Command Matches
							</p>
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
