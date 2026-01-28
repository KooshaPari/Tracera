import { useLocation, useParams } from "@tanstack/react-router";
import { Bell, Moon, Search, Sun, User } from "lucide-react";
import { useTheme } from "@/providers/ThemeProvider";
import { Breadcrumbs } from "./Breadcrumb";
import { Button } from "@tracertm/ui";

export function Header() {
	const location = useLocation();
	const params = useParams({ strict: false });
	const { theme, toggleTheme } = useTheme();

	return (
		<header
			role="banner"
			className="sticky top-0 z-50 flex h-16 items-center justify-between border-b bg-background/80 backdrop-blur-md px-6 transition-all duration-300"
		>
			{/* Breadcrumbs */}
			<div className="flex items-center gap-4 overflow-hidden">
				<Breadcrumbs />
			</div>

			{/* Actions */}
			<div className="flex items-center gap-3">
				{/* Search */}
				<div className="relative hidden md:block group">
					<Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors" />
					<input
						type="text"
						placeholder="Search everything... (⌘K)"
						className="h-9 w-64 rounded-full border bg-muted/50 pl-9 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-primary focus:bg-background transition-all"
					/>
				</div>

				{/* Theme toggle */}
				<Button
					variant="ghost"
					size="icon"
					onClick={toggleTheme}
					className="h-9 w-9 rounded-full"
				>
					{theme === "dark" ? (
						<Sun className="h-4 w-4" />
					) : (
						<Moon className="h-4 w-4" />
					)}
				</Button>

				{/* Notifications */}
				<Button 
					variant="ghost" 
					size="icon" 
					className="h-9 w-9 rounded-full relative"
				>
					<Bell className="h-4 w-4" />
					<span className="absolute right-2 top-2 flex h-2 w-2 items-center justify-center rounded-full bg-primary" />
				</Button>

				{/* User Profile */}
				<div className="h-8 w-px bg-border mx-1 hidden sm:block" />
				
				<Button 
					variant="ghost" 
					size="sm" 
					className="gap-2 px-2 hover:bg-muted rounded-full"
				>
					<div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10 text-primary">
						<User className="h-4 w-4" />
					</div>
					<span className="text-xs font-semibold hidden sm:inline-block">Admin</span>
				</Button>
			</div>
		</header>
	);
}
