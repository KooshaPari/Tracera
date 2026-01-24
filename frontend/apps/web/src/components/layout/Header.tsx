import { useLocation, useParams } from "@tanstack/react-router";
import { Bell, Moon, Plus, Search, Sun, User } from "lucide-react";
import { useTheme } from "@/providers/ThemeProvider";

export function Header() {
	const location = useLocation();
	const params = useParams({ strict: false });
	const projectId = params.projectId as string | undefined;
	const { theme, toggleTheme } = useTheme();

	// Get page title based on current route
	const getTitle = () => {
		if (location.pathname === "/") return "Dashboard";
		if (location.pathname === "/projects") return "Projects";
		if (location.pathname === "/settings") return "Settings";
		if (projectId) {
			const view = location.pathname.split("/").pop();
			return view
				? `${view.charAt(0).toUpperCase() + view.slice(1)} View`
				: "Project";
		}
		return "TraceRTM";
	};

	return (
		<header className="flex h-16 items-center justify-between border-b bg-card px-6">
			{/* Title */}
			<h1 className="text-2xl font-semibold">{getTitle()}</h1>

			{/* Search & Actions */}
			<div className="flex items-center gap-4">
				{/* Search */}
				<div className="relative">
					<Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
					<input
						type="text"
						placeholder="Search items... (⌘K)"
						className="h-9 w-64 rounded-lg border bg-background pl-9 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
					/>
				</div>

				{/* Create button */}
				<button className="flex h-9 items-center gap-2 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90">
					<Plus className="h-4 w-4" />
					Create
				</button>

				{/* Theme toggle */}
				<button
					onClick={toggleTheme}
					className="flex h-9 w-9 items-center justify-center rounded-lg border hover:bg-accent"
				>
					{theme === "dark" ? (
						<Sun className="h-4 w-4" />
					) : (
						<Moon className="h-4 w-4" />
					)}
				</button>

				{/* Notifications */}
				<button className="relative flex h-9 w-9 items-center justify-center rounded-lg border hover:bg-accent">
					<Bell className="h-4 w-4" />
					<span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] font-medium text-destructive-foreground">
						3
					</span>
				</button>

				{/* User */}
				<button className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-primary-foreground">
					<User className="h-4 w-4" />
				</button>
			</div>
		</header>
	);
}
