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
	ArrowUpDown,
	ChevronLeft,
	ChevronRight,
	ClipboardCheck,
	Code,
	Database,
	ExternalLink,
	FileCode,
	FileText,
	Filter,
	FolderOpen,
	GitBranch,
	Home,
	Layers,
	LayoutGrid,
	Link2,
	MoreVertical,
	Search,
	Settings,
	Shield,
	TestTube,
	TrendingUp,
	Zap,
	X,
	BarChart3,
	Network,
	Workflow,
	Target,
	Calendar,
	AlertCircle,
	Bug,
	Eye,
	Lock,
	Package,
} from "lucide-react";
import React, {
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

type SortOption = "recent" | "alphabetical" | "modified";
type FilterOption = "all" | "active" | "archived";

// Utility function to highlight search text
const highlightText = (text: string, query: string) => {
	if (!query.trim()) return text;
	const parts = text.split(new RegExp(`(${query})`, "gi"));
	return parts.map((part, i) =>
		part.toLowerCase() === query.toLowerCase() ? (
			<mark
				key={i}
				className="bg-primary/20 text-primary font-medium rounded px-0.5"
			>
				{part}
			</mark>
		) : (
			part
		),
	);
};

export function Sidebar() {
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

	const location = useLocation();
	const params = useParams({ strict: false });
	const { currentProject, recentProjects } = useProjectStore();
	const { data: allProjects } = useProjects();
	// WorkOS enabled check (unused but kept for future use)
	void import.meta.env["VITE_WORKOS_CLIENT_ID"];

	const projectId = params.projectId as string | undefined;
	const [sidebarWidth, setSidebarWidth] = useState(() => {
		const saved = localStorage.getItem("sidebar-width");
		const parsed = saved ? parseInt(saved, 10) : 280;
		return Math.max(240, parsed); // Ensure minimum width
	});
	const [isResizing, setIsResizing] = useState(false);

	// Load persisted state
	useEffect(() => {
		const savedCollapsed = localStorage.getItem("sidebar-collapsed");
		if (savedCollapsed) setIsCollapsed(savedCollapsed === "true");

		const savedGroups = localStorage.getItem("sidebar-collapsed-groups");
		if (savedGroups) {
			try {
				setCollapsedGroups(JSON.parse(savedGroups));
			} catch {
				// Ignore parse errors
			}
		}

		const savedSort = localStorage.getItem("sidebar-recent-sort");
		if (savedSort) setRecentSort(savedSort as SortOption);

		const savedFilter = localStorage.getItem("sidebar-recent-filter");
		if (savedFilter) setRecentFilter(savedFilter as FilterOption);
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

		window.addEventListener("keydown", handleKeyDown);
		return () => window.removeEventListener("keydown", handleKeyDown);
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
				const delta = startX - e.clientX; // Inverted because sidebar is on left
				const newWidth = Math.max(240, Math.min(600, startWidth + delta));
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

	// Toggle group function is now inlined where used
	void setCollapsedGroups;

	const navGroups = useMemo(() => {
		const groups = [
			{
				label: "Command",
				key: "command",
				collapsible: false,
				items: [
					{ title: "Dashboard", href: "/", icon: Home, badge: null },
					{
						title: "Projects",
						href: "/projects",
						icon: FolderOpen,
						badge: allProjects?.length || null,
					},
					{
						title: "Global Graph",
						href: "/graph",
						icon: GitBranch,
						badge: null,
					},
				],
			},
		];

		if (projectId || currentProject) {
			const activeId = projectId || currentProject?.id;
			groups.push({
				label: "Active Registry",
				key: "active-registry",
				collapsible: true,
				items: [
					{
						title: "Overview",
						href: `/projects/${activeId}`,
						icon: Activity,
						badge: null,
					},
					{
						title: "Feature Layer",
						href: `/projects/${activeId}/views/feature`,
						icon: Layers,
						badge: null,
					},
					{
						title: "Source Map",
						href: `/projects/${activeId}/views/code`,
						icon: Code,
						badge: null,
					},
					{
						title: "Validation",
						href: `/projects/${activeId}/views/test`,
						icon: Shield,
						badge: null,
					},
					{
						title: "Workflow Runs",
						href: `/projects/${activeId}/views/workflows`,
						icon: Activity,
						badge: null,
					},
					{
						title: "Project Settings",
						href: `/projects/${activeId}/settings`,
						icon: Link2,
						badge: null,
					},
				],
			});

			groups.push({
				label: "Specifications",
				key: "specifications",
				collapsible: true,
				items: [
					{
						title: "Dashboard",
						href: `/projects/${activeId}/specifications`,
						icon: FileCode,
						badge: null,
					},
					{
						title: "ADRs",
						href: `/projects/${activeId}/specifications?tab=adrs`,
						icon: FileText,
						badge: null,
					},
					{
						title: "Contracts",
						href: `/projects/${activeId}/specifications?tab=contracts`,
						icon: ClipboardCheck,
						badge: null,
					},
					{
						title: "Compliance",
						href: `/projects/${activeId}/specifications?tab=compliance`,
						icon: Shield,
						badge: null,
					},
				],
			});

			// New "All Views" section with categories
			groups.push({
				label: "All Views",
				key: "all-views",
				collapsible: true,
				categories: [
					{
						name: "Planning & Requirements",
						icon: Target,
						views: [
							{
								title: "Features",
								href: `/projects/${activeId}/views/feature`,
								icon: Layers,
								description: "Manage product features and requirements",
							},
							{
								title: "Domain Model",
								href: `/projects/${activeId}/views/domain`,
								icon: Network,
								description: "Visualize domain entities and relationships",
							},
							{
								title: "Problem Analysis",
								href: `/projects/${activeId}/views/problem`,
								icon: AlertCircle,
								description: "Track identified problems and issues",
							},
							{
								title: "Wireframes",
								href: `/projects/${activeId}/views/wireframe`,
								icon: Eye,
								description: "UI/UX design and layout specifications",
							},
						],
					},
					{
						name: "Development",
						icon: Code,
						views: [
							{
								title: "Code View",
								href: `/projects/${activeId}/views/code`,
								icon: Code,
								description: "Source code structure and organization",
							},
							{
								title: "Architecture",
								href: `/projects/${activeId}/views/architecture`,
								icon: Network,
								description: "System architecture and design patterns",
							},
							{
								title: "API Documentation",
								href: `/projects/${activeId}/views/api`,
								icon: Package,
								description: "API endpoints and specifications",
							},
							{
								title: "Database Schema",
								href: `/projects/${activeId}/views/database`,
								icon: Database,
								description: "Database structure and relationships",
							},
							{
								title: "Data Flow",
								href: `/projects/${activeId}/views/dataflow`,
								icon: Zap,
								description: "Data pipeline and processing flows",
							},
						],
					},
					{
						name: "Testing & Quality",
						icon: TestTube,
						views: [
							{
								title: "Test Cases",
								href: `/projects/${activeId}/views/test-cases`,
								icon: ClipboardCheck,
								description: "Test case definitions and scenarios",
							},
							{
								title: "Test Suites",
								href: `/projects/${activeId}/views/test-suites`,
								icon: TestTube,
								description: "Organized test suites and execution",
							},
							{
								title: "Test Runs",
								href: `/projects/${activeId}/views/test-runs`,
								icon: Activity,
								description: "Test execution history and results",
							},
							{
								title: "QA Dashboard",
								href: `/projects/${activeId}/views/qa-dashboard`,
								icon: BarChart3,
								description: "Quality metrics and coverage analysis",
							},
							{
								title: "Coverage Report",
								href: `/projects/${activeId}/views/coverage`,
								icon: TrendingUp,
								description: "Code coverage and test statistics",
							},
						],
					},
					{
						name: "Project Management",
						icon: Calendar,
						views: [
							{
								title: "Journey Map",
								href: `/projects/${activeId}/views/journey`,
								icon: Calendar,
								description: "User journeys and workflows",
							},
							{
								title: "Process Flow",
								href: `/projects/${activeId}/views/process`,
								icon: Workflow,
								description: "Business process definitions",
							},
							{
								title: "Timeline",
								href: `/projects/${activeId}/views/monitoring`,
								icon: Activity,
								description: "Project timeline and milestones",
							},
							{
								title: "Reports",
								href: `/projects/${activeId}/views/performance`,
								icon: BarChart3,
								description: "Project metrics and analytics",
							},
						],
					},
					{
						name: "Analysis & Tracking",
						icon: TrendingUp,
						views: [
							{
								title: "Impact Analysis",
								href: `/projects/${activeId}/views/dependency`,
								icon: Network,
								description: "Change impact and dependency analysis",
							},
							{
								title: "Traceability Matrix",
								href: `/projects/${activeId}/views/wireframe`,
								icon: BarChart3,
								description: "Requirements to implementation tracing",
							},
							{
								title: "Dependency Graph",
								href: `/projects/${activeId}/views/dependency`,
								icon: Network,
								description: "System and code dependencies",
							},
							{
								title: "Performance Metrics",
								href: `/projects/${activeId}/views/performance`,
								icon: TrendingUp,
								description: "Performance benchmarks and metrics",
							},
						],
					},
					{
						name: "Security & Monitoring",
						icon: Lock,
						views: [
							{
								title: "Security Analysis",
								href: `/projects/${activeId}/views/security`,
								icon: Lock,
								description: "Security vulnerabilities and threats",
							},
							{
								title: "Monitoring Dashboard",
								href: `/projects/${activeId}/views/monitoring`,
								icon: Activity,
								description: "System health and alerts",
							},
							{
								title: "Bug Tracking",
								href: `/projects/${activeId}/views/problem`,
								icon: Bug,
								description: "Reported bugs and issues",
							},
						],
					},
					{
						name: "Configuration",
						icon: Settings,
						views: [
							{
								title: "Integrations",
								href: `/projects/${activeId}/views/integrations`,
								icon: Zap,
								description: "Third-party integrations and webhooks",
							},
							{
								title: "Webhooks",
								href: `/projects/${activeId}/views/webhooks`,
								icon: Workflow,
								description: "Webhook configurations and events",
							},
							{
								title: "Settings",
								href: `/projects/${activeId}/settings`,
								icon: Settings,
								description: "Project configuration and preferences",
							},
						],
					},
				],
				items: [], // Will be populated from categories
			} as any);
		}

		groups.push({
			label: "System",
			key: "system",
			collapsible: false,
			items: [
				{ title: "Settings", href: "/settings", icon: Settings, badge: null },
			],
		});

		return groups as any;
	}, [projectId, currentProject, allProjects?.length]);

	// Filter navigation items based on search
	const filteredNavGroups = useMemo(() => {
		if (!searchQuery.trim()) return navGroups as any[];

		const query = searchQuery.toLowerCase();
		return (navGroups as any[])
			.map((group) => {
				// Handle "all-views" group with categories
				if ((group as any).categories) {
					const filteredCategories = (group as any).categories
						.map((cat: any) => ({
							...cat,
							views: cat.views.filter((view: any) =>
								view.title.toLowerCase().includes(query),
							),
						}))
						.filter((cat: any) => cat.views.length > 0);
					return {
						...group,
						categories: filteredCategories,
					};
				}

				// Handle regular groups with items
				const filteredItems = group.items.filter((item: any) =>
					item.title.toLowerCase().includes(query),
				);
				return { ...group, items: filteredItems };
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

	// Reset nav items refs when search or groups change
	useEffect(() => {
		void searchQuery;
		void filteredNavGroups;
		navItemsRef.current = [];
	}, [searchQuery, filteredNavGroups]);

	const isActive = (href: string) => {
		if (href === "/" && location.pathname !== "/") return false;
		return location.pathname.startsWith(href);
	};

	// Get full project objects for recent projects
	const recentProjectObjects = useMemo(() => {
		if (!allProjects || !Array.isArray(allProjects)) return [];
		return recentProjects
			.map((id) => allProjects.find((p) => p.id === id))
			.filter(
				(p): p is NonNullable<typeof p> => !!p && p.id !== currentProject?.id,
			);
	}, [recentProjects, allProjects, currentProject]);

	// Sort and filter recent projects
	const sortedRecentProjects = useMemo(() => {
		void recentFilter;
		// Note: recentFilter is not implemented since Project type doesn't have status
		// When status is added to Project type, uncomment the filter logic
		const filtered = recentProjectObjects;

		// Apply sort
		const sorted = [...filtered].sort((a, b) => {
			if (recentSort === "alphabetical") {
				return a.name.localeCompare(b.name);
			} else if (recentSort === "modified") {
				const aTime = new Date(a.updatedAt || a.createdAt || 0).getTime();
				const bTime = new Date(b.updatedAt || b.createdAt || 0).getTime();
				return bTime - aTime;
			} else {
				// Recent (by recentProjects order)
				const aIndex = recentProjects.indexOf(a.id);
				const bIndex = recentProjects.indexOf(b.id);
				return aIndex - bIndex;
			}
		});

		// Filter by search query
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			return sorted.filter((p) => p.name.toLowerCase().includes(query));
		}

		return sorted.slice(0, 5);
	}, [
		recentProjectObjects,
		recentSort,
		recentFilter,
		searchQuery,
		recentProjects,
	]);

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
			<div className="relative flex shrink-0">
				<aside
					className={cn(
						"relative flex flex-col border-r border-white/10 bg-card/60 backdrop-blur-xl transition-all duration-300 ease-in-out shrink-0 min-w-0 overflow-hidden",
						isCollapsed && "w-20",
					)}
					style={
						!isCollapsed
							? {
									width: `${sidebarWidth}px`,
									minWidth: `${sidebarWidth}px`,
									maxWidth: `${sidebarWidth}px`,
								}
							: undefined
					}
					role="navigation"
					aria-label="Main navigation"
				>
					{/* Logo Area */}
					<div className="flex h-16 items-center justify-center px-4 border-b shrink-0 min-w-0">
						<div className="flex items-center justify-center gap-3 min-w-0 flex-1">
							<div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-primary shadow-lg shadow-primary/20 transition-transform hover:scale-105">
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
						<div className="p-4 border-b shrink-0 min-w-0">
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
									className="pl-9 pr-9 h-9 text-sm w-full min-w-0"
									aria-label="Search navigation items"
									aria-describedby="search-hint"
								/>
								<span id="search-hint" className="sr-only">
									Use arrow keys to navigate results, Escape to clear
								</span>
								{searchQuery && (
									<Button
										variant="ghost"
										size="icon"
										className="absolute right-1 top-1/2 h-7 w-7 -translate-y-1/2"
										onClick={() => setSearchQuery("")}
									>
										<X className="h-3 w-3" />
									</Button>
								)}
							</div>
						</div>
					)}

					{/* Navigation */}
					<ScrollArea className="flex-1 px-4 py-6 min-w-0 overflow-hidden">
						<div className="space-y-6 min-w-0 w-full">
							{filteredNavGroups.map((group) => {
								const isGroupCollapsed = collapsedGroups[group.label] ?? false;
								const groupKey = group.key;

								// Handle tabbed groups
								if (groupKey === "active-registry" && !isCollapsed) {
									const overviewItem = group.items[0];
									const viewsItems = group.items.slice(1, -1);
									const settingsItem = group.items[group.items.length - 1];

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
											className="space-y-2 min-w-0 w-full"
										>
											<CollapsibleTrigger className="w-full px-2 py-1 hover:no-underline min-w-0">
												<h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/50 text-center min-w-0">
													{group.label}
												</h3>
											</CollapsibleTrigger>
											<CollapsibleContent className="pt-2 min-w-0 w-full overflow-hidden">
												<Tabs
													value={activeTab[group.label] || "overview"}
													onValueChange={(value) =>
														setActiveTab((prev) => ({
															...prev,
															[group.label]: value,
														}))
													}
													className="w-full min-w-0"
												>
													<TabsList className="grid w-full grid-cols-3 h-auto p-1 mb-2 shrink-0 min-w-0 max-w-full">
														<TabsTrigger
															value="overview"
															className="text-[10px] px-2 py-1 text-center"
														>
															Overview
														</TabsTrigger>
														<TabsTrigger
															value="views"
															className="text-[10px] px-2 py-1 text-center"
														>
															Views
														</TabsTrigger>
														<TabsTrigger
															value="settings"
															className="text-[10px] px-2 py-1 text-center"
														>
															Settings
														</TabsTrigger>
													</TabsList>
													<TabsContent
														value="overview"
														className="space-y-1 mt-0 max-h-[300px] overflow-y-auto min-w-0 w-full"
													>
														{overviewItem && (
															<NavItem
																ref={(el) => {
																	const index = navItemsRef.current.length;
																	navItemsRef.current[index] = el;
																}}
																item={overviewItem}
																isActive={isActive(overviewItem.href)}
																searchQuery={searchQuery}
															/>
														)}
													</TabsContent>
													<TabsContent
														value="views"
														className="space-y-1 mt-0 max-h-[300px] overflow-y-auto min-w-0 w-full"
													>
														{viewsItems.map((item: any, _idx: number) => (
															<NavItem
																key={item.href}
																ref={(el) => {
																	const index = navItemsRef.current.length;
																	navItemsRef.current[index] = el;
																}}
																item={item}
																isActive={isActive(item.href)}
																searchQuery={searchQuery}
															/>
														))}
													</TabsContent>
													<TabsContent
														value="settings"
														className="space-y-1 mt-0 max-h-[300px] overflow-y-auto min-w-0 w-full"
													>
														{settingsItem && (
															<NavItem
																ref={(el) => {
																	const index = navItemsRef.current.length;
																	navItemsRef.current[index] = el;
																}}
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
											className="space-y-2 min-w-0 w-full"
										>
											<CollapsibleTrigger className="w-full px-2 py-1 hover:no-underline min-w-0">
												<h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/50 text-center min-w-0">
													{group.label}
												</h3>
											</CollapsibleTrigger>
											<CollapsibleContent className="pt-2 min-w-0 w-full overflow-hidden">
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
													<TabsList className="grid w-full grid-cols-2 h-auto p-1 mb-2 shrink-0 min-w-0 max-w-full">
														<TabsTrigger
															value="dashboard"
															className="text-[10px] px-2 py-1 text-center"
														>
															Dashboard
														</TabsTrigger>
														<TabsTrigger
															value="specs"
															className="text-[10px] px-2 py-1 text-center"
														>
															Specs
														</TabsTrigger>
													</TabsList>
													<TabsContent
														value="dashboard"
														className="space-y-1 mt-0 max-h-[300px] overflow-y-auto min-w-0 w-full"
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
														className="space-y-1 mt-0 max-h-[300px] overflow-y-auto min-w-0 w-full"
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
												className="space-y-2 min-w-0 w-full"
											>
												<CollapsibleTrigger
													className="w-full px-2 py-1 hover:no-underline flex items-center justify-center group/trigger min-w-0"
													aria-label={`Toggle ${group.label} section`}
												>
													<div className="flex items-center justify-center gap-2 min-w-0 flex-1 max-w-full">
														<LayoutGrid className="h-4 w-4 shrink-0 text-muted-foreground/70" />
														<h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/50 text-center min-w-0 truncate">
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
												<CollapsibleContent className="pt-2 space-y-3 max-h-[600px] overflow-y-auto min-w-0 w-full">
													{(group as any).categories?.map(
														(
															category: {
																name: string;
																icon: any;
																views: Array<{
																	title: string;
																	href: string;
																	icon: any;
																	description: string;
																}>;
															},
															catIdx: number,
														) => (
															<div
																key={`${category.name}-${catIdx}`}
																className="space-y-2"
															>
																<div className="flex items-center gap-2 px-2">
																	<category.icon className="h-3 w-3 shrink-0 text-primary/60" />
																	<h4 className="text-[9px] font-bold uppercase tracking-widest text-muted-foreground/70">
																		{category.name}
																	</h4>
																</div>
																<div className="space-y-1 pl-5">
																	{category.views.map((view) => (
																		<Tooltip key={view.href}>
																			<TooltipTrigger asChild>
																				<Link
																					to={view.href as any}
																					className={cn(
																						"group flex items-center gap-2 rounded-lg px-3 py-2 transition-all duration-150 cursor-pointer relative min-w-0 w-full max-w-full text-xs",
																						"hover:scale-[1.01] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
																						isActive(view.href)
																							? "bg-primary/10 text-primary font-medium"
																							: "text-muted-foreground hover:bg-muted/50 hover:text-foreground",
																					)}
																					aria-current={
																						isActive(view.href)
																							? "page"
																							: undefined
																					}
																				>
																					<view.icon className="h-4 w-4 shrink-0" />
																					<span className="font-medium truncate min-w-0 flex-1">
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
											className="space-y-2 min-w-0 w-full"
										>
											<CollapsibleTrigger
												className="w-full px-2 py-1 hover:no-underline flex items-center justify-center group/trigger min-w-0"
												aria-label={`Toggle ${group.label} section`}
											>
												<div className="flex items-center justify-center gap-2 min-w-0 flex-1 max-w-full">
													<h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/50 text-center min-w-0 truncate">
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
											<CollapsibleContent className="pt-2 space-y-1 max-h-[400px] overflow-y-auto min-w-0 w-full">
												{group.items.map((item: any) => (
													<NavItem
														key={item.href}
														ref={(el) => {
															const index = navItemsRef.current.length;
															navItemsRef.current[index] = el;
														}}
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
									<div key={group.label} className="space-y-2 min-w-0 w-full">
										{!isCollapsed && (
											<h3 className="px-2 text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/50 text-center min-w-0">
												{group.label}
											</h3>
										)}
										<div className="space-y-1 min-w-0 w-full" role="list">
											{group.items.map((item) => (
												<NavItem
													key={item.href}
													ref={(el) => {
														const index = navItemsRef.current.length;
														navItemsRef.current[index] = el;
													}}
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
								<div className="space-y-2 min-w-0 w-full">
									<div className="flex items-center justify-center px-2 min-w-0 w-full">
										<h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/50 text-center min-w-0 flex-1">
											Recent
										</h3>
										<div className="flex items-center gap-1 shrink-0">
											<Select
												value={recentSort}
												onValueChange={(v) => setRecentSort(v as SortOption)}
											>
												<SelectTrigger className="h-6 w-6 p-0 border-none">
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
												<SelectTrigger className="h-6 w-6 p-0 border-none">
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
									<div className="space-y-1 max-h-[300px] overflow-y-auto min-w-0 w-full">
										{sortedRecentProjects.map((p) => (
											<Tooltip key={p.id}>
												<TooltipTrigger asChild>
													<div className="group relative flex items-center min-w-0 w-full">
														<Link
															to={`/projects/${p.id}` as any}
															className="flex-1 flex items-center gap-3 rounded-xl px-3 py-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-all cursor-pointer group/item min-w-0 max-w-full"
														>
															<div className="h-2 w-2 rounded-full bg-primary/40 group-hover/item:bg-primary transition-colors shrink-0" />
															<span className="text-xs font-bold truncate min-w-0 flex-1">
																{highlightText(p.name, searchQuery)}
															</span>
														</Link>
														<DropdownMenu>
															<DropdownMenuTrigger asChild>
																<Button
																	variant="ghost"
																	size="icon"
																	className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
																>
																	<MoreVertical className="h-3 w-3" />
																</Button>
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
										))}
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

					{/* Footer / Toggle */}
					<div className="p-4 border-t bg-muted/20 shrink-0 min-w-0">
						{!isCollapsed && currentProject && (
							<div className="mb-4 p-3 rounded-2xl bg-background/50 border border-border/50 hover:bg-background/70 transition-colors min-w-0">
								<div className="flex justify-center items-center text-[9px] font-black uppercase tracking-widest text-muted-foreground mb-2 min-w-0">
									<span className="text-center">Integrity 84%</span>
								</div>
								<Progress value={84} className="h-1 w-full min-w-0" />
							</div>
						)}

						<div className="flex items-center gap-2">
							<Button
								variant="ghost"
								size="icon"
								onClick={() => setIsCollapsed((prev) => !prev)}
								className="h-10 w-10 shrink-0 rounded-xl hover:bg-primary/10 hover:text-primary transition-all duration-150 active:scale-95 focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
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
				</aside>
				{/* Resize handle - wider drag zone for granular control */}
				{!isCollapsed && (
					<div
						onMouseDown={handleResizeStart}
						className={cn(
							"w-2 cursor-ew-resize bg-transparent hover:bg-primary/30 transition-all flex items-center justify-center group shrink-0 relative",
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
}

interface NavItemProps {
	item: {
		title: string;
		href: string;
		icon: any;
		badge: number | null;
	};
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
				className={cn(
					"group flex items-center gap-3 rounded-xl px-3 py-2.5 transition-all duration-150 cursor-pointer relative min-w-0 w-full max-w-full",
					"hover:scale-[1.02] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
					isActive
						? "bg-primary text-primary-foreground shadow-md shadow-primary/10 ring-2 ring-primary/20"
						: "text-muted-foreground hover:bg-muted hover:text-foreground",
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
						<span className="text-sm font-bold tracking-tight flex-1 min-w-0 truncate">
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
