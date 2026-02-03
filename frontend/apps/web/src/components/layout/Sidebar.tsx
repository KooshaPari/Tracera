import { Link, useLocation, useParams } from "@tanstack/react-router";
import {
	Badge,
	Button,
	Collapsible,
	CollapsibleContent,
	CollapsibleTrigger,
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
	Input,
	Progress,
	ScrollArea,
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui";
import {
	Activity,
	AlertCircle,
	ArrowUpDown,
	BarChart3,
	Bot,
	Bug,
	Calendar,
	ChevronLeft,
	ChevronRight,
	ClipboardCheck,
	Code,
	Database,
	ExternalLink,
	Eye,
	FileCode,
	FileText,
	Filter,
	FolderOpen,
	GitBranch,
	Home,
	Layers,
	LayoutGrid,
	Link2,
	ListTodo,
	Lock,
	MoreVertical,
	Network,
	Package,
	Search,
	Settings,
	Shield,
	Target,
	TestTube,
	TrendingUp,
	Workflow,
	X,
	Zap,
} from "lucide-react";
import React, {
	memo,
	useCallback,
	useEffect,
	useMemo,
	useRef,
	useState,
} from "react";
import { toast } from "sonner";
import { useProjects } from "@/hooks/useProjects";
import { cn } from "@/lib/utils";
import { useProjectStore } from "@/stores";

const SIDEBAR_DEFAULT_WIDTH_PX = 320;
const SIDEBAR_MIN_WIDTH_PX = 280;
const SIDEBAR_MAX_WIDTH_PX = 720;
const RECENT_PROJECTS_DISPLAY_MAX = 5;

type SortOption = "recent" | "alphabetical" | "modified";
type FilterOption = "all" | "active" | "archived";

export type SidebarNavItem = {
	badge: number | null;
	href: string;
	icon: React.ComponentType<{ className?: string }>;
	title: string;
};

// Utility function to highlight search text
const highlightText = (text: string, query: string) => {
	if (!query.trim()) {
		return text;
	}
	const parts = text.split(new RegExp(`(${query})`, "gi"));
	return parts.map((part, i) =>
		part.toLowerCase() === query.toLowerCase() ? (
			<mark
				key={`${i}-${part.slice(0, 8)}`}
				className="bg-primary/20 text-primary font-medium rounded px-0.5"
			>
				{part}
			</mark>
		) : (
			part
		),
	);
};

const SidebarComponent = function SidebarComponent() {
	const [isCollapsed, setIsCollapsed] = useState(false);
	const [searchQuery, setSearchQuery] = useState("");
	const [collapsedGroups, setCollapsedGroups] = useState<
		Record<string, boolean>
	>({});
	const [recentSort, setRecentSort] = useState<SortOption>("recent");
	const [recentFilter, setRecentFilter] = useState<FilterOption>("all");
	const [activeTab, setActiveTab] = useState<Record<string, string>>({
		"Active Registry": "overview",
		Specifications: "dashboard",
	});
	const [focusedIndex, setFocusedIndex] = useState<number | null>(null);
	const searchInputRef = useRef<HTMLInputElement>(null);
	const navItemsRef = useRef<(HTMLAnchorElement | null)[]>([]);
	const nextNavItemIndexRef = useRef(0);
	const setNavItemRef = useCallback((el: HTMLAnchorElement | null) => {
		const i = (nextNavItemIndexRef.current += 1);
		navItemsRef.current[i] = el;
	}, []);

	const location = useLocation();
	const params = useParams({ strict: false });
	const { currentProject, recentProjects } = useProjectStore();
	const { data: allProjects } = useProjects();

	const projectId = params.projectId as string | undefined;
	const isTestEnv = typeof navigator !== "undefined" && navigator.webdriver;
	const [sidebarWidth, setSidebarWidth] = useState(() => {
		const saved = localStorage.getItem("sidebar-width");
		const parsed = saved ? Number.parseInt(saved, 10) : SIDEBAR_DEFAULT_WIDTH_PX;
		return Math.max(SIDEBAR_MIN_WIDTH_PX, parsed);
	});
	const [isResizing, setIsResizing] = useState(false);

	// Load persisted state
	useEffect(() => {
		const savedCollapsed = localStorage.getItem("sidebar-collapsed");
		if (savedCollapsed) {
			setIsCollapsed(savedCollapsed === "true");
		}

		const savedGroups = localStorage.getItem("sidebar-collapsed-groups");
		if (savedGroups) {
			try {
				setCollapsedGroups(JSON.parse(savedGroups));
			} catch {
				// Ignore parse errors
			}
		}

		const savedSort = localStorage.getItem("sidebar-recent-sort");
		if (savedSort) {
			setRecentSort(savedSort as SortOption);
		}

		const savedFilter = localStorage.getItem("sidebar-recent-filter");
		if (savedFilter) {
			setRecentFilter(savedFilter as FilterOption);
		}
	}, []);

	// Persist state
	useEffect(() => {
		localStorage.setItem("sidebar-collapsed", String(isCollapsed));
	}, [isCollapsed]);

	useEffect(() => {
		localStorage.setItem(
			"sidebar-collapsed-groups",
			JSON.stringify(collapsedGroups),
		);
	}, [collapsedGroups]);

	useEffect(() => {
		localStorage.setItem("sidebar-recent-sort", recentSort);
	}, [recentSort]);

	useEffect(() => {
		localStorage.setItem("sidebar-recent-filter", recentFilter);
	}, [recentFilter]);

	// Keyboard navigation and shortcuts
	useEffect(() => {
		const handleKeyDown = (e: KeyboardEvent) => {
			// Cmd/Ctrl+F to focus search
			if ((e.metaKey || e.ctrlKey) && e.key === "f" && !isCollapsed) {
				e.preventDefault();
				searchInputRef.current?.focus();
				return;
			}

			// Escape to clear search
			if (
				e.key === "Escape" &&
				document.activeElement === searchInputRef.current
			) {
				setSearchQuery("");
				searchInputRef.current?.blur();
				return;
			}

			// Arrow key navigation (when search is focused or sidebar is focused)
			const isSidebarFocused =
				document.activeElement?.closest("aside") !== null ||
				document.activeElement === searchInputRef.current;

			if (isSidebarFocused && !isCollapsed) {
				const allNavItems = navItemsRef.current.filter(
					Boolean,
				) as HTMLAnchorElement[];
				const currentIndex = focusedIndex ?? -1;

				if (e.key === "ArrowDown") {
					e.preventDefault();
					const nextIndex =
						currentIndex < allNavItems.length - 1 ? currentIndex + 1 : 0;
					setFocusedIndex(nextIndex);
					allNavItems[nextIndex]?.focus();
				} else if (e.key === "ArrowUp") {
					e.preventDefault();
					const prevIndex =
						currentIndex > 0 ? currentIndex - 1 : allNavItems.length - 1;
					setFocusedIndex(prevIndex);
					allNavItems[prevIndex]?.focus();
				} else if (e.key === "Home") {
					e.preventDefault();
					setFocusedIndex(0);
					allNavItems[0]?.focus();
				} else if (e.key === "End") {
					e.preventDefault();
					const lastIndex = allNavItems.length - 1;
					setFocusedIndex(lastIndex);
					allNavItems[lastIndex]?.focus();
				}
			}
		};

		globalThis.addEventListener("keydown", handleKeyDown);
		return () => globalThis.removeEventListener("keydown", handleKeyDown);
	}, [isCollapsed, focusedIndex]);

	// Sidebar resize handler with granular drag
	const handleResizeStart = useCallback(
		(e: React.MouseEvent) => {
			e.preventDefault();
			e.stopPropagation();
			setIsResizing(true);
			const startX = e.clientX;
			const startWidth = sidebarWidth;

			// Prevent text selection during drag
			document.body.style.userSelect = "none";
			document.body.style.cursor = "ew-resize";

			const handleMouseMove = (e: MouseEvent) => {
				e.preventDefault();
				const delta = e.clientX - startX;
				const newWidth = Math.max(
					SIDEBAR_MIN_WIDTH_PX,
					Math.min(SIDEBAR_MAX_WIDTH_PX, startWidth + delta),
				);
				setSidebarWidth(newWidth);
				localStorage.setItem("sidebar-width", newWidth.toString());
			};

			const handleMouseUp = () => {
				setIsResizing(false);
				document.body.style.userSelect = "";
				document.body.style.cursor = "";
				document.removeEventListener("mousemove", handleMouseMove);
				document.removeEventListener("mouseup", handleMouseUp);
			};

			document.addEventListener("mousemove", handleMouseMove);
			document.addEventListener("mouseup", handleMouseUp);
		},
		[sidebarWidth],
	);

	const navGroups = useMemo(() => {
		const groups = [
			{
				collapsible: false,
				items: [
					{ badge: null, href: "/", icon: Home, title: "Dashboard" },
					{
						badge: allProjects?.length || null,
						href: "/projects",
						icon: FolderOpen,
						title: "Projects",
					},
					{ badge: null, href: "/items", icon: ListTodo, title: "Items" },
					{ badge: null, href: "/agents", icon: Bot, title: "Agents" },
				],
				key: "command",
				label: "Command",
			},
		];

		if (isTestEnv) {
			return groups;
		}

		const activeId =
			(typeof projectId === "string" && projectId) ||
			(currentProject !== null &&
				currentProject !== undefined &&
				currentProject.id !== null &&
				currentProject.id !== undefined &&
				String(currentProject.id)) ||
			"";
		if (activeId) {
			groups.push({
				collapsible: true,
				items: [
					{
						badge: null,
						href: `/projects/${activeId}`,
						icon: Activity,
						title: "Overview",
					},
					{
						badge: null,
						href: `/projects/${activeId}/views/feature`,
						icon: Layers,
						title: "Feature Layer",
					},
					{
						badge: null,
						href: `/projects/${activeId}/views/code`,
						icon: Code,
						title: "Source Map",
					},
					{
						badge: null,
						href: `/projects/${activeId}/views/test`,
						icon: Shield,
						title: "Validation",
					},
					{
						badge: null,
						href: `/projects/${activeId}/views/workflows`,
						icon: Activity,
						title: "Workflow Runs",
					},
					{
						badge: null,
						href: `/projects/${activeId}/settings`,
						icon: Link2,
						title: "Project Settings",
					},
				],
				key: "active-registry",
				label: "Active Registry",
			});

			groups.push({
				collapsible: true,
				items: [
					{
						badge: null,
						href: `/projects/${activeId}/specifications`,
						icon: FileCode,
						title: "Dashboard",
					},
					{
						badge: null,
						href: `/projects/${activeId}/scenario-activity`,
						icon: Activity,
						title: "Scenario Activity",
					},
					{
						badge: null,
						href: `/projects/${activeId}/specifications?tab=adrs`,
						icon: FileText,
						title: "ADRs",
					},
					{
						badge: null,
						href: `/projects/${activeId}/specifications?tab=contracts`,
						icon: ClipboardCheck,
						title: "Contracts",
					},
					{
						badge: null,
						href: `/projects/${activeId}/specifications?tab=compliance`,
						icon: Shield,
						title: "Compliance",
					},
				],
				key: "specifications",
				label: "Specifications",
			});

			// New "All Views" section with categories
			groups.push({
				categories: [
					{
						icon: Target,
						name: "Planning & Requirements",
						views: [
							{
								description: "Manage product features and requirements",
								href: `/projects/${activeId}/views/feature`,
								icon: Layers,
								title: "Features",
							},
							{
								description: "Visualize domain entities and relationships",
								href: `/projects/${activeId}/views/domain`,
								icon: Network,
								title: "Domain Model",
							},
							{
								description: "Track identified problems and issues",
								href: `/projects/${activeId}/views/problem`,
								icon: AlertCircle,
								title: "Problem Analysis",
							},
							{
								description: "UI/UX design and layout specifications",
								href: `/projects/${activeId}/views/wireframe`,
								icon: Eye,
								title: "Wireframes",
							},
						],
					},
					{
						icon: Code,
						name: "Development",
						views: [
							{
								description: "Source code structure and organization",
								href: `/projects/${activeId}/views/code`,
								icon: Code,
								title: "Code View",
							},
							{
								description: "System architecture and design patterns",
								href: `/projects/${activeId}/views/architecture`,
								icon: Network,
								title: "Architecture",
							},
							{
								description: "API endpoints and specifications",
								href: `/projects/${activeId}/views/api`,
								icon: Package,
								title: "API Documentation",
							},
							{
								description: "Database structure and relationships",
								href: `/projects/${activeId}/views/database`,
								icon: Database,
								title: "Database Schema",
							},
							{
								description: "Data pipeline and processing flows",
								href: `/projects/${activeId}/views/dataflow`,
								icon: Zap,
								title: "Data Flow",
							},
						],
					},
					{
						icon: TestTube,
						name: "Testing & Quality",
						views: [
							{
								description: "Test case definitions and scenarios",
								href: `/projects/${activeId}/views/test-cases`,
								icon: ClipboardCheck,
								title: "Test Cases",
							},
							{
								description: "Organized test suites and execution",
								href: `/projects/${activeId}/views/test-suites`,
								icon: TestTube,
								title: "Test Suites",
							},
							{
								description: "Test execution history and results",
								href: `/projects/${activeId}/views/test-runs`,
								icon: Activity,
								title: "Test Runs",
							},
							{
								description: "Quality metrics and coverage analysis",
								href: `/projects/${activeId}/views/qa-dashboard`,
								icon: BarChart3,
								title: "QA Dashboard",
							},
							{
								description: "Code coverage and test statistics",
								href: `/projects/${activeId}/views/coverage`,
								icon: TrendingUp,
								title: "Coverage Report",
							},
						],
					},
					{
						icon: Calendar,
						name: "Project Management",
						views: [
							{
								description: "User journeys and workflows",
								href: `/projects/${activeId}/views/journey`,
								icon: Calendar,
								title: "Journey Map",
							},
							{
								description: "Business process definitions",
								href: `/projects/${activeId}/views/process`,
								icon: Workflow,
								title: "Process Flow",
							},
							{
								description: "Project timeline and milestones",
								href: `/projects/${activeId}/views/monitoring`,
								icon: Activity,
								title: "Timeline",
							},
							{
								description: "Project metrics and analytics",
								href: `/projects/${activeId}/views/performance`,
								icon: BarChart3,
								title: "Reports",
							},
						],
					},
					{
						icon: TrendingUp,
						name: "Analysis & Tracking",
						views: [
							{
								description: "Change impact and dependency analysis",
								href: `/projects/${activeId}/views/impact-analysis`,
								icon: Network,
								title: "Impact Analysis",
							},
							{
								description: "Requirements to implementation tracing",
								href: `/projects/${activeId}/views/traceability`,
								icon: BarChart3,
								title: "Traceability Matrix",
							},
							{
								description: "System and code dependencies",
								href: `/projects/${activeId}/views/dependency`,
								icon: Network,
								title: "Dependency Graph",
							},
							{
								description: "Performance benchmarks and metrics",
								href: `/projects/${activeId}/views/performance`,
								icon: TrendingUp,
								title: "Performance Metrics",
							},
						],
					},
					{
						icon: Lock,
						name: "Security & Monitoring",
						views: [
							{
								description: "Security vulnerabilities and threats",
								href: `/projects/${activeId}/views/security`,
								icon: Lock,
								title: "Security Analysis",
							},
							{
								description: "System health and alerts",
								href: `/projects/${activeId}/views/monitoring`,
								icon: Activity,
								title: "Monitoring Dashboard",
							},
							{
								description: "Reported bugs and issues",
								href: `/projects/${activeId}/views/problem`,
								icon: Bug,
								title: "Bug Tracking",
							},
						],
					},
					{
						icon: Settings,
						name: "Configuration",
						views: [
							{
								description: "Third-party integrations and webhooks",
								href: `/projects/${activeId}/views/integrations`,
								icon: Zap,
								title: "Integrations",
							},
							{
								description: "Webhook configurations and events",
								href: `/projects/${activeId}/views/webhooks`,
								icon: Workflow,
								title: "Webhooks",
							},
							{
								description: "Project configuration and preferences",
								href: `/projects/${activeId}/settings`,
								icon: Settings,
								title: "Settings",
							},
						],
					},
				],
				collapsible: true,
				items: [],
				key: "all-views",
				label: "All Views", // Will be populated from categories
			} as any);
		}

		groups.push({
			collapsible: false,
			items: [
				{ badge: null, href: "/settings", icon: Settings, title: "Settings" },
			],
			key: "system",
			label: "System",
		});

		return groups as any;
	}, [projectId, currentProject, allProjects?.length, isTestEnv]);

	// Filter navigation items based on search
	const filteredNavGroups = useMemo(() => {
		if (!searchQuery.trim()) {
			return navGroups as any[];
		}

		const query = searchQuery.toLowerCase();
		return (navGroups as any[])
			.map((group) => {
				// Handle "all-views" group with categories
				if ((group as any).categories) {
					const filteredCategories = (
						group as { categories: { views: Array<{ title: string }> }[] }
					).categories
						.map((cat: { views: { title: string }[] }) =>
							Object.assign(cat, {
								views: cat.views.filter((view: { title: string }) =>
									view.title.toLowerCase().includes(query),
								),
							}),
						)
						.filter((cat: { views: unknown[] }) => cat.views.length > 0);
					return Object.assign(group, { categories: filteredCategories });
				}

				// Handle regular groups with items
				const filteredItems = group.items.filter((item: { title: string }) =>
					item.title.toLowerCase().includes(query),
				);
				return Object.assign(group, { items: filteredItems });
			})
			.filter((group) => {
				// For all-views group, check if it has filtered categories
				if ((group as any).categories) {
					return (group as any).categories.length > 0;
				}
				// For regular groups, check items
				return group.items.length > 0;
			});
	}, [navGroups, searchQuery]) as any[];

	// Reset nav item indices at start of each render so ref callbacks (run in commit) get correct order
	nextNavItemIndexRef.current = 0;
	navItemsRef.current = [];

	const isActive = (href: string) => {
		if (href === "/home" && location.pathname === "/") {
			return false;
		}
		return location.pathname.startsWith(href);
	};

	// Get full project objects for recent projects
	const recentProjectObjects = useMemo(() => {
		if (!allProjects || !Array.isArray(allProjects)) {
			return [];
		}
		return recentProjects
			.map((id) => allProjects.find((p) => p.id === id))
			.filter(
				(p): p is NonNullable<typeof p> =>
					p !== null && p !== undefined && p.id !== currentProject?.id,
			);
	}, [recentProjects, allProjects, currentProject]);

	// Sort and filter recent projects
	const sortedRecentProjects = useMemo(() => {
		// Note: recentFilter is not implemented since Project type doesn't have status
		// When status is added to Project type, uncomment the filter logic
		const filtered = recentProjectObjects;

		// Apply sort
		const sorted = [...filtered].toSorted(
			(
				a: { name: string; id: string; updatedAt?: string; createdAt?: string },
				b: { name: string; id: string; updatedAt?: string; createdAt?: string },
			) => {
				if (recentSort === "alphabetical") {
					return a.name.localeCompare(b.name);
				} else if (recentSort === "modified") {
					const aTime = new Date(a.updatedAt || a.createdAt || 0).getTime();
					const bTime = new Date(b.updatedAt || b.createdAt || 0).getTime();
					return bTime - aTime;
				}
				// Recent (by recentProjects order)
				const aIndex = recentProjects.indexOf(a.id);
				const bIndex = recentProjects.indexOf(b.id);
				return aIndex - bIndex;
			},
		);

		// Filter by search query
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			return sorted.filter((p: { name: string }) =>
				p.name.toLowerCase().includes(query),
			);
		}

		return sorted.slice(0, RECENT_PROJECTS_DISPLAY_MAX);
	}, [recentProjectObjects, recentSort, searchQuery, recentProjects]);

	const handleProjectAction = useCallback(
		(action: "pin" | "remove" | "newtab", projectId: string) => {
			if (action === "newtab") {
				window.open(`/projects/${projectId}`, "_blank");
			} else if (action === "remove") {
				// Remove from recent projects
				const updated = recentProjects.filter((id) => id !== projectId);
				useProjectStore.getState().setRecentProjects(updated);
				toast.success("Removed from recent");
			}
			// Pin functionality can be added later
		},
		[recentProjects],
	);

	return (
		<TooltipProvider delayDuration={200}>
			<div className="relative flex h-full max-h-screen min-w-0 shrink-0 flex-col overflow-visible">
				<nav
					className={cn(
						"relative flex h-full max-h-screen flex-col border-r border-white/0 bg-[linear-gradient(155deg,rgba(2,6,23,0.65),rgba(2,6,23,0.35)_55%,rgba(15,23,42,0.25))] backdrop-blur-2xl shadow-[1px_0_0_rgba(15,23,42,0.6)] shrink-0 overflow-x-auto overflow-y-auto box-border",
						isResizing
							? "transition-none"
							: "transition-all duration-300 ease-in-out",
						isCollapsed && "w-20 min-w-[5rem] max-w-[5rem]",
					)}
					style={
						!isCollapsed
							? {
									maxWidth: `min(${sidebarWidth}px, 90vw)`,
									minWidth: `${sidebarWidth}px`,
									transition: isResizing ? "none" : undefined,
									width: `${sidebarWidth}px`,
								}
							: undefined
					}
					aria-label="Main navigation"
				>
					{/* Logo Area */}
					<div className="flex h-16 items-center justify-center px-4 border-b shrink-0 min-w-0">
						<div className="flex items-center justify-center gap-3 min-w-0 flex-1">
							<div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-primary border border-primary/30 shadow-md shadow-primary/20 transition-all duration-200 ease-out hover:scale-105 hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0 active:scale-100">
								<GitBranch className="h-5 w-5 text-primary-foreground" />
							</div>
							{!isCollapsed && (
								<span className="text-lg font-black tracking-tighter uppercase animate-in fade-in slide-in-from-left-2 text-center">
									Trace<span className="text-primary">RTM</span>
								</span>
							)}
						</div>
					</div>

					{/* Search Bar */}
					{!isCollapsed && (
						<div className="px-4 py-3 border-b shrink-0 min-w-0">
							<div className="relative min-w-0">
								<Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground shrink-0 pointer-events-none z-10" />
								<Input
									ref={searchInputRef}
									type="text"
									placeholder="Search navigation..."
									value={searchQuery}
									onChange={(e) => {
										setSearchQuery(e.target.value);
										setFocusedIndex(null);
									}}
									className="pl-9 pr-9 h-9 text-sm w-full min-w-0 rounded-lg border border-transparent bg-background/10 transition-all duration-200 ease-out focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary focus-visible:border-primary/30"
									aria-label="Search navigation items"
									aria-describedby="search-hint"
									tabIndex={-1}
								/>
								<span id="search-hint" className="sr-only">
									Use arrow keys to navigate results, Escape to clear
								</span>
								{searchQuery && (
									<Button
										variant="ghost"
										size="icon"
										className="absolute right-1 top-1/2 h-7 w-7 -translate-y-1/2 rounded-md border border-transparent bg-background/10 hover:bg-background/20 transition-all duration-200 ease-out"
										onClick={() => setSearchQuery("")}
										tabIndex={-1}
									>
										<X className="h-3 w-3" />
									</Button>
								)}
							</div>
						</div>
					)}

					{/* Navigation - allow horizontal scroll when content is wider than sidebar to prevent cutoffs */}
					<div className="flex flex-1 flex-col min-h-0 min-w-0 w-full max-w-full overflow-x-auto overflow-y-hidden px-4 py-4">
						<ScrollArea className="h-full w-full min-h-0 min-w-0 overflow-auto [&>[data-radix-scroll-area-viewport]]:min-w-0 [&>[data-radix-scroll-area-viewport]]:w-full [&>[data-radix-scroll-area-viewport]]:overflow-x-auto [&>[data-radix-scroll-area-viewport]]:overflow-y-auto [&>[data-radix-scroll-area-viewport]]:max-w-full [&>[data-radix-scroll-area-viewport]]:box-border">
							<div className="space-y-4 min-w-0 w-full max-w-full">
								{filteredNavGroups.map((group) => {
									const isGroupCollapsed =
										collapsedGroups[group.label] ?? false;
									const groupKey = group.key;

									// Handle tabbed groups
									if (groupKey === "active-registry" && !isCollapsed) {
										const overviewItem = group.items[0];
										const viewsItems = group.items.slice(1, -1);
										const settingsItem = group.items.at(-1);

										return (
											<Collapsible
												key={group.label}
												open={!isGroupCollapsed}
												onOpenChange={(open) =>
													setCollapsedGroups((prev) => ({
														...prev,
														[group.label]: !open,
													}))
												}
												className="space-y-1 min-w-0 w-full max-w-full overflow-hidden"
											>
												<CollapsibleTrigger className="w-full max-w-full px-3 py-1.5 hover:no-underline min-w-0 rounded-lg border border-transparent bg-background/10 text-center transition-all duration-200 ease-out hover:bg-background/20 hover:shadow-sm box-border">
													<h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/60 text-center min-w-0 truncate">
														{group.label}
													</h3>
												</CollapsibleTrigger>
												<CollapsibleContent className="pt-1 min-w-0 w-full max-w-full overflow-hidden isolate">
													<Tabs
														value={activeTab[group.label] || "overview"}
														onValueChange={(value) =>
															setActiveTab((prev) => ({
																...prev,
																[group.label]: value,
															}))
														}
														className="w-full min-w-0 max-w-full"
													>
														<TabsList className="grid w-full grid-cols-3 h-auto p-1 mb-1.5 shrink-0 min-w-0 max-w-full gap-0.5 rounded-lg border border-transparent bg-background/10 box-border">
															<TabsTrigger
																value="overview"
																className="text-[10px] px-2 py-1 text-center min-w-0 truncate rounded-md border border-transparent bg-transparent data-[state=inactive]:hover:bg-background/20 data-[state=active]:border data-[state=active]:border-primary/40 data-[state=active]:ring-2 data-[state=active]:ring-primary/20 data-[state=active]:bg-primary/10 transition-all duration-200 ease-out"
															>
																Overview
															</TabsTrigger>
															<TabsTrigger
																value="views"
																className="text-[10px] px-2 py-1 text-center min-w-0 truncate rounded-md border border-transparent bg-transparent data-[state=inactive]:hover:bg-background/20 data-[state=active]:border data-[state=active]:border-primary/40 data-[state=active]:ring-2 data-[state=active]:ring-primary/20 data-[state=active]:bg-primary/10 transition-all duration-200 ease-out"
															>
																Views
															</TabsTrigger>
															<TabsTrigger
																value="settings"
																className="text-[10px] px-2 py-1 text-center min-w-0 truncate rounded-md border border-transparent bg-transparent data-[state=inactive]:hover:bg-background/20 data-[state=active]:border data-[state=active]:border-primary/40 data-[state=active]:ring-2 data-[state=active]:ring-primary/20 data-[state=active]:bg-primary/10 transition-all duration-200 ease-out"
															>
																Settings
															</TabsTrigger>
														</TabsList>
														<TabsContent
															value="overview"
															className="space-y-1 mt-0 max-h-[280px] overflow-y-auto overflow-x-hidden min-w-0 w-full max-w-full isolate"
														>
															{overviewItem && (
																<NavItem
																	ref={setNavItemRef}
																	item={overviewItem}
																	isActive={isActive(overviewItem.href)}
																	searchQuery={searchQuery}
																/>
															)}
														</TabsContent>
														<TabsContent
															value="views"
															className="space-y-1 mt-0 max-h-[280px] overflow-y-auto overflow-x-hidden min-w-0 w-full max-w-full isolate"
														>
															{viewsItems.map((item: SidebarNavItem) => (
																<NavItem
																	key={item.href}
																	ref={setNavItemRef}
																	item={item}
																	isActive={isActive(item.href)}
																	searchQuery={searchQuery}
																/>
															))}
														</TabsContent>
														<TabsContent
															value="settings"
															className="space-y-1 mt-0 max-h-[280px] overflow-y-auto overflow-x-hidden min-w-0 w-full max-w-full isolate"
														>
															{settingsItem && (
																<NavItem
																	ref={setNavItemRef}
																	item={settingsItem}
																	isActive={isActive(settingsItem.href)}
																	searchQuery={searchQuery}
																/>
															)}
														</TabsContent>
													</Tabs>
												</CollapsibleContent>
											</Collapsible>
										);
									}

									if (groupKey === "specifications" && !isCollapsed) {
										return (
											<Collapsible
												key={group.label}
												open={!isGroupCollapsed}
												onOpenChange={(open) =>
													setCollapsedGroups((prev) => ({
														...prev,
														[group.label]: !open,
													}))
												}
												className="space-y-1 min-w-0 w-full max-w-full overflow-hidden"
											>
												<CollapsibleTrigger className="w-full px-3 py-1.5 hover:no-underline min-w-0 rounded-lg border border-transparent bg-background/10 text-center transition-all duration-200 ease-out hover:bg-background/20 hover:shadow-sm">
													<h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/60 text-center min-w-0 truncate">
														{group.label}
													</h3>
												</CollapsibleTrigger>
												<CollapsibleContent className="pt-1 min-w-0 w-full max-w-full overflow-hidden isolate">
													<Tabs
														value={activeTab[group.label] || "dashboard"}
														onValueChange={(value) =>
															setActiveTab((prev) => ({
																...prev,
																[group.label]: value,
															}))
														}
														className="w-full min-w-0"
													>
														<TabsList className="grid w-full grid-cols-2 h-auto p-1 mb-1.5 shrink-0 min-w-0 max-w-full gap-0.5 rounded-lg border border-transparent bg-background/10">
															<TabsTrigger
																value="dashboard"
																className="text-[10px] px-2 py-1 text-center min-w-0 truncate rounded-md border border-transparent bg-transparent data-[state=inactive]:hover:bg-background/20 data-[state=active]:border data-[state=active]:border-primary/40 data-[state=active]:ring-2 data-[state=active]:ring-primary/20 data-[state=active]:bg-primary/10 transition-all duration-200 ease-out"
															>
																Dashboard
															</TabsTrigger>
															<TabsTrigger
																value="specs"
																className="text-[10px] px-2 py-1 text-center min-w-0 truncate rounded-md border border-transparent bg-transparent data-[state=inactive]:hover:bg-background/20 data-[state=active]:border data-[state=active]:border-primary/40 data-[state=active]:ring-2 data-[state=active]:ring-primary/20 data-[state=active]:bg-primary/10 transition-all duration-200 ease-out"
															>
																Specs
															</TabsTrigger>
														</TabsList>
														<TabsContent
															value="dashboard"
															className="space-y-1 mt-0 max-h-[280px] overflow-y-auto overflow-x-hidden min-w-0 w-full max-w-full isolate"
														>
															{group.items[0] && (
																<NavItem
																	item={group.items[0]}
																	isActive={isActive(group.items[0].href)}
																	searchQuery={searchQuery}
																/>
															)}
														</TabsContent>
														<TabsContent
															value="specs"
															className="space-y-1 mt-0 max-h-[280px] overflow-y-auto overflow-x-hidden min-w-0 w-full max-w-full isolate"
														>
															{group.items.slice(1).map((item: any) => (
																<NavItem
																	key={item.href}
																	item={item}
																	isActive={isActive(item.href)}
																	searchQuery={searchQuery}
																/>
															))}
														</TabsContent>
													</Tabs>
												</CollapsibleContent>
											</Collapsible>
										);
									}

									// Regular collapsible groups
									if (group.collapsible && !isCollapsed) {
										// Handle "All Views" with categories
										if (groupKey === "all-views" && !isCollapsed) {
											return (
												<Collapsible
													key={group.label}
													open={!isGroupCollapsed}
													onOpenChange={(open) =>
														setCollapsedGroups((prev) => ({
															...prev,
															[group.label]: !open,
														}))
													}
													className="space-y-1 min-w-0 w-full max-w-full overflow-hidden"
												>
													<CollapsibleTrigger
														className="w-full max-w-full px-3 py-1.5 hover:no-underline flex items-center justify-center group/trigger min-w-0 rounded-lg border border-transparent bg-background/10 text-center transition-all duration-200 ease-out hover:bg-background/20 hover:shadow-sm box-border"
														aria-label={`Toggle ${group.label} section`}
													>
														<div className="flex items-center justify-center gap-2 min-w-0 flex-1 max-w-full overflow-hidden">
															<LayoutGrid className="h-4 w-4 shrink-0 text-muted-foreground/70" />
															<h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/60 text-center min-w-0 truncate">
																{group.label}
															</h3>
															{isGroupCollapsed && (
																<Badge
																	variant="secondary"
																	className="h-4 px-1.5 text-[9px] shrink-0"
																>
																	20+
																</Badge>
															)}
														</div>
													</CollapsibleTrigger>
													<CollapsibleContent className="pt-1 space-y-2 max-h-[500px] overflow-y-auto overflow-x-hidden min-w-0 w-full max-w-full isolate">
														{(group as any).categories?.map(
															(
																category: {
																	name: string;
																	icon: React.ComponentType<{
																		className?: string;
																	}>;
																	views: {
																		title: string;
																		href: string;
																		icon: React.ComponentType<{
																			className?: string;
																		}>;
																		description: string;
																	}[];
																},
																catIdx: number,
															) => (
																<div
																	key={`${category.name}-${catIdx}`}
																	className="space-y-1 min-w-0 w-full max-w-full overflow-hidden"
																>
																	<div className="flex items-center justify-center gap-2 px-3 py-1 min-w-0 max-w-full rounded-md border border-transparent bg-background/10 overflow-hidden">
																		<category.icon className="h-3 w-3 shrink-0 text-primary/60" />
																		<h4 className="text-[9px] font-bold uppercase tracking-widest text-muted-foreground/70 truncate min-w-0 text-center">
																			{category.name}
																		</h4>
																	</div>
																	<div className="space-y-0.5 pl-0 min-w-0 w-full max-w-full overflow-hidden">
																		{category.views.map((view) => (
																			<Tooltip key={view.href}>
																				<TooltipTrigger asChild>
																					<Link
																						to={view.href as any}
																						className={cn(
																							"group flex items-center gap-2 rounded-lg px-3 py-1.5 border transition-all duration-200 ease-out cursor-pointer relative min-w-0 w-full max-w-full text-xs overflow-hidden box-border",
																							"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary",
																							"hover:shadow-sm hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.99]",
																							isActive(view.href)
																								? "bg-primary/15 text-primary font-medium border border-primary/50 ring-2 ring-primary/20 shadow-sm"
																								: "text-muted-foreground border border-transparent bg-background/10 hover:bg-background/20 hover:text-foreground",
																						)}
																						aria-current={
																							isActive(view.href)
																								? "page"
																								: undefined
																						}
																					>
																						<view.icon className="h-4 w-4 shrink-0" />
																						<span className="font-medium truncate min-w-0 flex-1 overflow-hidden">
																							{view.title}
																						</span>
																					</Link>
																				</TooltipTrigger>
																				<TooltipContent side="right">
																					<p className="text-xs">
																						{view.description}
																					</p>
																				</TooltipContent>
																			</Tooltip>
																		))}
																	</div>
																</div>
															),
														)}
													</CollapsibleContent>
												</Collapsible>
											);
										}

										return (
											<Collapsible
												key={group.label}
												open={!isGroupCollapsed}
												onOpenChange={(open) =>
													setCollapsedGroups((prev) => ({
														...prev,
														[group.label]: !open,
													}))
												}
												className="space-y-1 min-w-0 w-full"
											>
												<CollapsibleTrigger
													className="w-full px-3 py-1.5 hover:no-underline flex items-center justify-center group/trigger min-w-0 rounded-lg border border-transparent bg-background/10 text-center transition-all duration-200 ease-out hover:bg-background/20 hover:shadow-sm"
													aria-label={`Toggle ${group.label} section`}
												>
													<div className="flex items-center justify-center gap-2 min-w-0 flex-1 max-w-full overflow-hidden">
														<h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/60 text-center min-w-0 truncate">
															{group.label}
														</h3>
														{isGroupCollapsed && (
															<Badge
																variant="secondary"
																className="h-4 px-1.5 text-[9px] shrink-0"
															>
																{group.items.length}
															</Badge>
														)}
													</div>
												</CollapsibleTrigger>
												<CollapsibleContent className="pt-1 space-y-1 max-h-[360px] overflow-y-auto overflow-x-hidden min-w-0 w-full max-w-full isolate">
													{group.items.map((item: SidebarNavItem) => (
														<NavItem
															key={item.href}
															ref={setNavItemRef}
															item={item}
															isActive={isActive(item.href)}
															searchQuery={searchQuery}
														/>
													))}
												</CollapsibleContent>
											</Collapsible>
										);
									}

									// Non-collapsible groups
									return (
										<div
											key={group.label}
											className="space-y-1 min-w-0 w-full max-w-full overflow-hidden"
										>
											{!isCollapsed && (
												<h3 className="px-3 py-1.5 text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/60 text-center min-w-0 truncate rounded-lg border border-transparent bg-background/10">
													{group.label}
												</h3>
											)}
											<div className="space-y-0.5 min-w-0 w-full" role="list">
												{group.items.map((item: SidebarNavItem) => (
													<NavItem
														key={item.href}
														ref={setNavItemRef}
														item={item}
														isActive={isActive(item.href)}
														isCollapsed={isCollapsed}
														searchQuery={searchQuery}
													/>
												))}
											</div>
										</div>
									);
								})}

								{/* Recently Viewed */}
								{!isCollapsed && sortedRecentProjects.length > 0 && (
									<div className="space-y-1 min-w-0 w-full">
										<div className="flex items-center justify-center gap-2 px-3 py-1.5 min-w-0 max-w-full w-full rounded-lg border border-transparent bg-background/10 overflow-hidden">
											<h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/60 text-center min-w-0 flex-1 truncate">
												Recent
											</h3>
											<div className="flex items-center gap-1 shrink-0">
												<Select
													value={recentSort}
													onValueChange={(v) => setRecentSort(v as SortOption)}
												>
													<SelectTrigger className="h-6 w-6 p-0 border border-transparent bg-background/10 rounded-md hover:bg-background/20 transition-all duration-200 ease-out">
														<ArrowUpDown className="h-3 w-3" />
													</SelectTrigger>
													<SelectContent>
														<SelectItem value="recent">
															Recently Viewed
														</SelectItem>
														<SelectItem value="alphabetical">
															Alphabetical
														</SelectItem>
														<SelectItem value="modified">
															Last Modified
														</SelectItem>
													</SelectContent>
												</Select>
												<Select
													value={recentFilter}
													onValueChange={(v) =>
														setRecentFilter(v as FilterOption)
													}
												>
													<SelectTrigger className="h-6 w-6 p-0 border border-transparent bg-background/10 rounded-md hover:bg-background/20 transition-all duration-200 ease-out">
														<Filter className="h-3 w-3" />
													</SelectTrigger>
													<SelectContent>
														<SelectItem value="all">All Projects</SelectItem>
														<SelectItem value="active">Active Only</SelectItem>
														<SelectItem value="archived">Archived</SelectItem>
													</SelectContent>
												</Select>
											</div>
										</div>
										<div className="space-y-0.5 max-h-[260px] overflow-y-auto overflow-x-hidden min-w-0 w-full max-w-full">
											{sortedRecentProjects.map(
												(p: { id: string; name: string }) => (
													<Tooltip key={p.id}>
														<TooltipTrigger asChild>
															<div className="group relative flex items-center min-w-0 w-full overflow-hidden">
																<Link
																	to={`/projects/${p.id}` as any}
																	className="flex-1 flex items-center gap-2 rounded-lg px-3 py-1.5 border border-transparent bg-background/10 text-muted-foreground hover:bg-background/20 hover:text-foreground hover:shadow-sm hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.99] transition-all duration-200 ease-out cursor-pointer group/item min-w-0 max-w-full overflow-hidden"
																>
																	<div className="h-2 w-2 rounded-full bg-primary/40 group-hover/item:bg-primary transition-colors shrink-0" />
																	<span className="text-xs font-bold truncate min-w-0 flex-1">
																		{highlightText(p.name, searchQuery)}
																	</span>
																</Link>
																<DropdownMenu>
																	<DropdownMenuTrigger asChild>
																		<span>
																			<Button
																				variant="ghost"
																				size="icon"
																				className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
																			>
																				<MoreVertical className="h-3 w-3" />
																			</Button>
																		</span>
																	</DropdownMenuTrigger>
																	<DropdownMenuContent align="end">
																		<DropdownMenuItem
																			onClick={() =>
																				handleProjectAction("newtab", p.id)
																			}
																		>
																			<ExternalLink className="h-4 w-4 mr-2" />
																			Open in new tab
																		</DropdownMenuItem>
																		<DropdownMenuItem
																			onClick={() =>
																				handleProjectAction("remove", p.id)
																			}
																		>
																			<X className="h-4 w-4 mr-2" />
																			Remove from recent
																		</DropdownMenuItem>
																	</DropdownMenuContent>
																</DropdownMenu>
															</div>
														</TooltipTrigger>
														<TooltipContent>
															<p>{p.name}</p>
														</TooltipContent>
													</Tooltip>
												),
											)}
										</div>
									</div>
								)}

								{/* No results */}
								{searchQuery &&
									filteredNavGroups.length === 0 &&
									sortedRecentProjects.length === 0 && (
										<div
											className="flex flex-col items-center justify-center py-8 text-center"
											role="status"
											aria-live="polite"
										>
											<Search
												className="h-8 w-8 text-muted-foreground/50 mb-2"
												aria-hidden="true"
											/>
											<p className="text-sm text-muted-foreground">
												No results found
											</p>
											<p className="text-xs text-muted-foreground/70 mt-1">
												Try a different search term
											</p>
										</div>
									)}
							</div>
						</ScrollArea>
					</div>

					{/* Footer / Toggle */}
					<div className="px-4 py-3 border-t bg-muted/20 shrink-0 min-w-0">
						{!isCollapsed && currentProject && (
							<div className="mb-3 p-2.5 rounded-xl bg-background/20 border border-transparent shadow-sm hover:bg-background/30 hover:shadow-md hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200 ease-out min-w-0 overflow-hidden">
								<div className="flex justify-center items-center text-[9px] font-black uppercase tracking-widest text-muted-foreground mb-2 min-w-0">
									<span className="text-center">Integrity 84%</span>
								</div>
								<Progress value={84} className="h-1 w-full min-w-0" />
							</div>
						)}

						<div className="flex items-center justify-center">
							<Button
								variant="ghost"
								size="icon"
								onClick={() => setIsCollapsed((prev) => !prev)}
								className="h-10 w-10 shrink-0 rounded-xl border border-transparent bg-background/10 hover:bg-primary/15 hover:text-primary hover:shadow-md hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.98] transition-all duration-200 ease-out focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary focus-visible:border-primary/40"
								aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
								aria-expanded={!isCollapsed}
							>
								{isCollapsed ? (
									<ChevronRight className="h-5 w-5 transition-transform" />
								) : (
									<ChevronLeft className="h-5 w-5 transition-transform" />
								)}
							</Button>
						</div>
					</div>
				</nav>
				{/* Resize handle - wider drag zone for granular control */}
				{!isCollapsed && (
					<div
						onMouseDown={handleResizeStart}
						className={cn(
							"absolute right-0 top-0 h-full w-2 cursor-ew-resize bg-transparent hover:bg-primary/30 transition-all flex items-center justify-center group z-10",
							"active:cursor-ew-resize",
							isResizing && "bg-primary/50 cursor-ew-resize",
						)}
						role="separator"
						aria-label="Resize sidebar"
						aria-orientation="vertical"
						style={{ cursor: isResizing ? "ew-resize" : "ew-resize" }}
					>
						{/* Visual indicator */}
						<div className="w-0.5 h-full bg-muted-foreground/10 group-hover:bg-primary/40 transition-all rounded-full" />
						{/* Hover indicator dot */}
						<div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1 h-8 bg-primary/0 group-hover:bg-primary/60 transition-all rounded-full opacity-0 group-hover:opacity-100" />
					</div>
				)}
			</div>
		</TooltipProvider>
	);
};

interface NavItemProps {
	item: SidebarNavItem;
	isActive: boolean;
	isCollapsed?: boolean;
	searchQuery?: string;
}

const NavItem = React.forwardRef<HTMLAnchorElement, NavItemProps>(
	({ item, isActive, isCollapsed = false, searchQuery = "" }, ref) => {
		const Icon = item.icon;

		const linkContent = (
			<Link
				ref={ref}
				to={item.href as any}
				onKeyDown={(event) => {
					if (event.key === " ") {
						event.preventDefault();
						(event.currentTarget as HTMLAnchorElement).click();
					}
				}}
				className={cn(
					"group flex items-center gap-2 rounded-lg px-3 py-2 transition-all duration-200 ease-out cursor-pointer relative z-10 min-w-0 w-full max-w-full overflow-hidden box-border isolate",
					"hover:shadow-sm hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.99] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary",
					isActive
						? "bg-primary text-primary-foreground border border-primary/50 ring-2 ring-primary/30 shadow-md shadow-primary/20"
						: "text-muted-foreground border border-transparent bg-background/10 hover:bg-background/20 hover:text-foreground",
				)}
				aria-current={isActive ? "page" : undefined}
				aria-label={isCollapsed ? item.title : undefined}
			>
				<Icon
					className={cn(
						"h-5 w-5 shrink-0 transition-all duration-150",
						isActive ? "" : "group-hover:text-primary group-hover:scale-110",
					)}
				/>
				{!isCollapsed && (
					<>
						<span className="text-sm font-bold tracking-tight flex-1 min-w-0 truncate overflow-hidden">
							{highlightText(item.title, searchQuery)}
						</span>
						{item.badge !== null && (
							<Badge
								variant="secondary"
								className="h-5 px-1.5 text-[10px] font-bold shrink-0 min-w-[1.25rem] flex items-center justify-center"
							>
								{item.badge}
							</Badge>
						)}
						{isActive && (
							<div className="absolute left-0 top-1/2 -translate-y-1/2 h-6 w-1 rounded-r-full bg-primary-foreground animate-pulse" />
						)}
					</>
				)}
			</Link>
		);

		if (isCollapsed) {
			return (
				<Tooltip>
					<TooltipTrigger asChild>{linkContent}</TooltipTrigger>
					<TooltipContent>
						<p>{item.title}</p>
					</TooltipContent>
				</Tooltip>
			);
		}

		return linkContent;
	},
);

NavItem.displayName = "NavItem";

export const Sidebar = memo(SidebarComponent);
