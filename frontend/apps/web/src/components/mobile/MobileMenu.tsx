import { useLocation, useNavigate } from "@tanstack/react-router";
import { Button } from "@tracertm/ui";
import {
	ChevronRight,
	FolderOpen,
	Home,
	LogIn,
	LogOut,
	Menu,
	Settings,
	X,
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/authStore";

interface MobileMenuProps {
	className?: string;
}

/**
 * Mobile hamburger menu with proper 44px+ touch targets
 * Compliant with WCAG accessibility guidelines
 */
export function MobileMenu({ className }: MobileMenuProps) {
	const [isOpen, setIsOpen] = useState(false);
	const navigate = useNavigate();
	const location = useLocation();
	const { user, logout } = useAuthStore();

	const handleNavigate = async (to: string) => {
		setIsOpen(false);
		await navigate({ to } as any);
	};

	const handleLogout = () => {
		void logout();
		setIsOpen(false);
		void navigate({ to: "/home" } as any);
	};

	const menuItems = [
		{
			label: "Dashboard",
			href: "/home",
			icon: Home,
		},
		{
			label: "Projects",
			href: "/projects",
			icon: FolderOpen,
		},
		{
			label: "Settings",
			href: "/settings",
			icon: Settings,
		},
	];

	const isActive = (href: string) => {
		return (
			location.pathname === href || location.pathname.startsWith(`${href}/`)
		);
	};

	return (
		<>
			{/* Hamburger button - minimum 44x44px touch target */}
			<Button
				variant="ghost"
				size="icon"
				onClick={() => setIsOpen(!isOpen)}
				className={cn(
					"h-11 w-11 rounded-lg md:hidden",
					"focus:ring-2 focus:ring-primary focus:ring-offset-0",
					"active:scale-95 transition-transform",
					className,
				)}
				aria-label={isOpen ? "Close menu" : "Open menu"}
				aria-expanded={isOpen}
				aria-controls="mobile-menu"
			>
				{isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
			</Button>

			{/* Mobile menu backdrop */}
			{isOpen && (
				<div
					className="fixed inset-0 bg-black/50 z-40 md:hidden"
					onClick={() => setIsOpen(false)}
					aria-hidden="true"
				/>
			)}

			{/* Mobile menu panel */}
			<div
				id="mobile-menu"
				className={cn(
					"fixed top-16 left-0 right-0 bottom-0 z-50 bg-background/95 backdrop-blur-sm",
					"md:hidden transform transition-all duration-300 ease-in-out",
					"flex flex-col overflow-y-auto",
					isOpen
						? "translate-x-0 opacity-100"
						: "-translate-x-full opacity-0 pointer-events-none",
				)}
			>
				{/* Header section */}
				<div className="p-4 sm:p-6 border-b border-border/30">
					<h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-widest">
						Menu
					</h2>
				</div>

				{/* Navigation items */}
				<nav className="flex-1 p-4 sm:p-6 space-y-2" role="navigation">
					{menuItems.map((item) => {
						const Icon = item.icon;
						const active = isActive(item.href);

						return (
							<button
								key={item.href}
								onClick={() => handleNavigate(item.href)}
								className={cn(
									"w-full flex items-center gap-3 px-4 py-3 rounded-lg",
									"min-h-[52px] transition-all duration-200",
									"focus:outline-none focus:ring-2 focus:ring-primary",
									"active:scale-95 transition-transform",
									active
										? "bg-primary/10 text-primary font-semibold border border-primary/30"
										: "text-foreground hover:bg-muted border border-transparent",
								)}
							>
								<Icon className="h-5 w-5 shrink-0" />
								<span className="flex-1 text-left text-sm font-medium">
									{item.label}
								</span>
								{active && <ChevronRight className="h-4 w-4 shrink-0" />}
							</button>
						);
					})}
				</nav>

				{/* User section */}
				<div className="p-4 sm:p-6 border-t border-border/30 space-y-3">
					{!user ? (
						<button
							onClick={() => handleNavigate("/auth/login")}
							className={cn(
								"w-full flex items-center gap-3 px-4 py-3 rounded-lg",
								"min-h-[52px] transition-all duration-200",
								"bg-primary text-primary-foreground hover:bg-primary/90",
								"focus:outline-none focus:ring-2 focus:ring-primary",
								"active:scale-95 transition-transform",
							)}
						>
							<LogIn className="h-5 w-5 shrink-0" />
							<span className="flex-1 text-left text-sm font-medium">
								Sign in to your account
							</span>
						</button>
					) : (
						<>
							<div className="px-4 py-3 rounded-lg bg-muted/50">
								<p className="text-xs font-semibold text-muted-foreground uppercase tracking-widest mb-1">
									Account
								</p>
								<p className="text-sm font-medium text-foreground truncate">
									{user?.name || "User"}
								</p>
								<p className="text-xs text-muted-foreground truncate mt-0.5">
									{user?.email}
								</p>
							</div>

							{/* Logout button - minimum 44x44px */}
							<button
								onClick={handleLogout}
								className={cn(
									"w-full flex items-center gap-3 px-4 py-3 rounded-lg",
									"min-h-[52px] transition-all duration-200",
									"bg-destructive/10 text-destructive hover:bg-destructive/20",
									"border border-destructive/30",
									"focus:outline-none focus:ring-2 focus:ring-destructive",
									"active:scale-95 transition-transform",
								)}
							>
								<LogOut className="h-5 w-5 shrink-0" />
								<span className="flex-1 text-left text-sm font-medium">
									Log out
								</span>
							</button>
						</>
					)}
				</div>
			</div>
		</>
	);
}
