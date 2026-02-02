import { useLocation, useNavigate, useParams } from "@tanstack/react-router";
import {
	Avatar,
	AvatarFallback,
	AvatarImage,
	Button,
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
	ScrollArea,
} from "@tracertm/ui";
import {
	Activity,
	AlertTriangle,
	Bell,
	CheckCircle,
	Info,
	LogIn,
	LogOut,
	Search,
	Settings,
	Shield,
	XCircle,
} from "lucide-react";
import { useMemo } from "react";
import { MobileMenu } from "@/components/mobile";
import { useNotifications } from "@/hooks/useNotifications";
import { useProject } from "@/hooks/useProjects";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/authStore";
import { Breadcrumbs } from "./Breadcrumb";

function getNotificationIcon(type: string) {
	switch (type) {
		case "success":
			return <CheckCircle className="h-4 w-4 text-green-500" />;
		case "warning":
			return <AlertTriangle className="h-4 w-4 text-amber-500" />;
		case "error":
			return <XCircle className="h-4 w-4 text-red-500" />;
		default:
			return <Info className="h-4 w-4 text-blue-500" />;
	}
}

export function Header() {
	const location = useLocation();
	const navigate = useNavigate();
	const params = useParams({ strict: false });
	const { user, logout } = useAuthStore();
	const { notifications, unreadCount, markAsRead, markAllRead } =
		useNotifications();
	const projectId = params.projectId as string | undefined;
	const { data: project } = useProject(projectId || "");

	const handleLogout = () => {
		void logout();
		void navigate({ to: "/home" });
	};

	// Get initials for avatar
	const initials = user?.name
		? user.name
				.split(" ")
				.map((n) => n[0])
				.join("")
				.toUpperCase()
				.slice(0, 2)
		: "U";

	// Dynamic header content based on route
	const headerContext = useMemo(() => {
		const path = location.pathname;

		if (path.startsWith("/projects/") && projectId) {
			if (path.includes("/views/")) {
				const viewType = path.split("/views/")[1]?.split("/")[0];
				return {
					type: "project-view",
					project,
					viewType,
					title: project?.name || "Project",
					subtitle: viewType
						? `${viewType.charAt(0).toUpperCase() + viewType.slice(1)} View`
						: undefined,
				};
			}
			return {
				type: "project",
				project,
				title: project?.name || "Project",
				subtitle: project?.description || undefined,
			};
		}

		if (path === "/projects") {
			return {
				type: "projects-list",
				title: "Projects",
				subtitle: "",
			};
		}

		if (path === "/" || path === "/home") {
			return {
				type: "dashboard",
				title: "Dashboard",
				subtitle: undefined,
			};
		}

		return {
			type: "default",
			title: "TraceRTM",
			subtitle: undefined,
		};
	}, [location.pathname, project, projectId]);

	return (
		<header
			role="banner"
			className="sticky top-0 z-50 flex h-16 items-center justify-between border-b border-white/0 bg-[linear-gradient(90deg,rgba(2,6,23,0.65),rgba(2,6,23,0.35)_60%,rgba(15,23,42,0.25))] backdrop-blur-2xl shadow-[0_1px_0_rgba(15,23,42,0.6)] pl-4 pr-4 sm:pl-6 sm:pr-6 transition-all duration-300"
		>
			{/* Left: Mobile menu & Context & Breadcrumbs */}
			<div className="flex items-center gap-2 sm:gap-4 overflow-hidden flex-1 min-w-0">
				<MobileMenu />
				{/* Dynamic Context Info */}
				{headerContext.type === "project" ||
				headerContext.type === "project-view" ? (
					<div className="flex items-center gap-3 min-w-0">
						<div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
							<Activity className="h-4 w-4 text-primary" />
						</div>
						<div className="min-w-0">
							<h2 className="text-sm font-bold truncate">
								{headerContext.title}
							</h2>
							{headerContext.subtitle && (
								<p className="text-xs text-muted-foreground truncate">
									{headerContext.subtitle}
								</p>
							)}
						</div>
						{/* Simplified Date Display */}
						{project?.createdAt && (
							<span className="text-[10px] text-muted-foreground/50 shrink-0 hidden xl:inline-block">
								Created {new Date(project.createdAt).toLocaleDateString()}
							</span>
						)}
					</div>
				) : (
					<div className="flex items-center gap-3 min-w-0">
						<h2 className="text-sm font-bold">{headerContext.title}</h2>
						{headerContext.subtitle && (
							<p className="text-xs text-muted-foreground hidden sm:block">
								{headerContext.subtitle}
							</p>
						)}
					</div>
				)}

				<div className="hidden lg:block ml-4">
					<Breadcrumbs />
				</div>
			</div>

			{/* Actions */}
			<div className="flex items-center gap-2">
				{/* Search */}
				<div className="relative hidden md:block group mr-2">
					<Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors" />
					<input
						type="text"
						placeholder="Search... (⌘K)"
						className="h-9 w-48 lg:w-64 rounded-full border bg-muted/50 pl-9 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-primary focus:bg-background transition-all"
					/>
				</div>

				{/* Notifications Dropdown */}
				<DropdownMenu>
					<DropdownMenuTrigger asChild>
						<span>
							<Button
								variant="ghost"
								size="icon"
								className="h-9 w-9 rounded-full relative"
							>
								<Bell className="h-4 w-4" />
								{unreadCount > 0 && (
									<span className="absolute right-2 top-2 flex h-2 w-2 items-center justify-center rounded-full bg-primary ring-2 ring-background animate-pulse" />
								)}
							</Button>
						</span>
					</DropdownMenuTrigger>
					<DropdownMenuContent align="end" className="w-80">
						<div className="flex items-center justify-between px-2 py-1.5">
							<DropdownMenuLabel className="p-0">
								Notifications
							</DropdownMenuLabel>
							{unreadCount > 0 && (
								<Button
									variant="ghost"
									size="xs"
									className="h-6 text-[10px] text-primary hover:text-primary/80"
									onClick={(e) => {
										e.preventDefault();
										markAllRead.mutate();
									}}
								>
									Mark all read
								</Button>
							)}
						</div>
						<DropdownMenuSeparator />
						<ScrollArea className="h-[300px]">
							{notifications.length === 0 ? (
								<div className="text-center py-8 text-muted-foreground text-xs">
									<Bell className="h-8 w-8 mx-auto mb-2 opacity-20" />
									<p>No new notifications</p>
								</div>
							) : (
								<div className="p-1 space-y-1">
									{notifications.map((notification) => (
										<button
											key={notification.id}
											className={cn(
												"relative flex items-start gap-3 p-2 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer group w-full text-left",
												!notification.read_at && "bg-muted/30",
											)}
											onClick={() => {
												if (!notification.read_at)
													markAsRead.mutate(notification.id);
												if (notification.link)
													void navigate({ to: notification.link });
											}}
										>
											<div className="mt-1 shrink-0">
												{getNotificationIcon(notification.type)}
											</div>
											<div className="flex-1 min-w-0">
												<div className="flex items-center justify-between gap-2">
													<p
														className={cn(
															"text-xs font-medium",
															!notification.read_at && "text-foreground",
														)}
													>
														{notification.title}
													</p>
													<span className="text-[10px] text-muted-foreground whitespace-nowrap">
														{new Date(
															notification.created_at,
														).toLocaleDateString()}
													</span>
												</div>
												<p className="text-[11px] text-muted-foreground line-clamp-2 mt-0.5">
													{notification.message}
												</p>
											</div>
											{!notification.read_at && (
												<div className="absolute right-2 top-1/2 -translate-y-1/2 h-1.5 w-1.5 rounded-full bg-primary" />
											)}
										</button>
									))}
								</div>
							)}
						</ScrollArea>
						<DropdownMenuSeparator />
						<DropdownMenuItem className="cursor-pointer justify-center text-xs text-muted-foreground">
							View all notifications
						</DropdownMenuItem>
					</DropdownMenuContent>
				</DropdownMenu>

				{/* User Profile / Sign in */}
				<div className="h-8 w-px bg-border mx-1 hidden sm:block" />

				{!user ? (
					<Button
						variant="default"
						size="sm"
						className="gap-2 rounded-full font-semibold"
						onClick={() => navigate({ to: "/auth/login" })}
					>
						<LogIn className="h-4 w-4" />
						<span className="hidden sm:inline">Sign in</span>
					</Button>
				) : (
					<DropdownMenu>
						<DropdownMenuTrigger asChild>
							<Button
								variant="ghost"
								size="sm"
								className="gap-2 px-1 hover:bg-muted rounded-full ml-1"
							>
								<Avatar className="h-8 w-8 border border-border">
									<AvatarImage src={user?.avatar} alt={user?.name || "User"} />
									<AvatarFallback className="bg-primary/10 text-primary text-xs font-bold">
										{initials}
									</AvatarFallback>
								</Avatar>
								<div className="flex flex-col items-start text-left hidden md:flex mr-1">
									<span className="text-xs font-semibold leading-none max-w-[100px] truncate">
										{user?.name || "User"}
									</span>
									<span className="text-[10px] text-muted-foreground leading-none mt-0.5 max-w-[100px] truncate">
										{user?.email}
									</span>
								</div>
							</Button>
						</DropdownMenuTrigger>
						<DropdownMenuContent align="end" className="w-56">
							<DropdownMenuLabel>
								<div className="flex flex-col space-y-1">
									<p className="text-sm font-medium leading-none">
										{user?.name || "User"}
									</p>
									<p className="text-xs leading-none text-muted-foreground">
										{user?.email}
									</p>
								</div>
							</DropdownMenuLabel>
							<DropdownMenuSeparator />
							<DropdownMenuItem
								className="cursor-pointer"
								onClick={() => navigate({ to: "/settings" })}
							>
								<Settings className="mr-2 h-4 w-4" />
								<span>Settings</span>
							</DropdownMenuItem>
							{user?.role === "admin" && (
								<DropdownMenuItem
									className="cursor-pointer"
									onClick={() => navigate({ to: "/admin" })}
								>
									<Shield className="mr-2 h-4 w-4" />
									<span>Admin Panel</span>
								</DropdownMenuItem>
							)}
							<DropdownMenuSeparator />
							<DropdownMenuItem
								className="cursor-pointer text-destructive focus:text-destructive"
								onClick={handleLogout}
							>
								<LogOut className="mr-2 h-4 w-4" />
								<span>Log out</span>
							</DropdownMenuItem>
						</DropdownMenuContent>
					</DropdownMenu>
				)}
			</div>
		</header>
	);
}
