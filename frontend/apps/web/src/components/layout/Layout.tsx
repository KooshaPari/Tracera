import { Outlet } from "@tanstack/react-router";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

export function Layout() {
	const handleSkipToMain = (e: React.MouseEvent) => {
		e.preventDefault();
		const mainContent = document.querySelector("main");
		if (mainContent) {
			mainContent.setAttribute("tabindex", "-1");
			mainContent.focus();
			mainContent.addEventListener("blur", () => {
				mainContent.removeAttribute("tabindex");
			}, { once: true });
		}
	};

	return (
		<div className="flex h-screen bg-background overflow-hidden selection:bg-primary/20 selection:text-primary">
			{/* Skip to main content link - visually hidden but focusable */}
			<a
				href="#main-content"
				onClick={handleSkipToMain}
				className="absolute left-[-9999px] top-0 z-[10000] bg-primary px-4 py-2 text-primary-foreground focus:left-4 focus:top-4 focus:rounded-lg"
			>
				Skip to main content
			</a>

			<Sidebar />
			<div className="flex flex-1 flex-col overflow-hidden bg-muted/20 relative">
				{/* Background Decoration */}
				<div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:32px_32px] pointer-events-none" />
				<div className="absolute inset-0 bg-gradient-to-tr from-background via-transparent to-background pointer-events-none" />
				
				<Header />
				<main
					id="main-content"
					role="main"
					className="flex-1 overflow-auto p-6 relative z-10 custom-scrollbar"
				>
					<Outlet />
				</main>
			</div>
		</div>
	);
}
