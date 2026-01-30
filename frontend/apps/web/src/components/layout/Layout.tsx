import { Outlet, useLocation } from "@tanstack/react-router";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { ChatBubble } from "@/components/chat";

export function Layout() {
	const location = useLocation();
	const path = location.pathname;
	const isItemDetail =
		/\/items\/[^/]+$/.test(path) ||
		/\/projects\/[^/]+\/views\/[^/]+\/[^/]+$/.test(path);
	const handleSkipToMain = (e: React.MouseEvent) => {
		e.preventDefault();
		const mainContent = document.querySelector("main");
		if (mainContent) {
			mainContent.setAttribute("tabindex", "-1");
			mainContent.focus();
			mainContent.addEventListener(
				"blur",
				() => {
					mainContent.removeAttribute("tabindex");
				},
				{ once: true },
			);
		}
	};

	return (
		<div
			className={
				isItemDetail
					? "flex h-screen overflow-hidden selection:bg-primary/20 selection:text-primary bg-transparent"
					: "flex h-screen bg-background overflow-hidden selection:bg-primary/20 selection:text-primary"
			}
		>
			{isItemDetail && (
				<div className="pointer-events-none fixed inset-0 z-0 bg-[radial-gradient(circle_at_10%_15%,rgba(249,115,22,0.28),transparent_45%),radial-gradient(circle_at_85%_8%,rgba(14,116,144,0.3),transparent_42%),radial-gradient(circle_at_20%_75%,rgba(16,185,129,0.24),transparent_40%)]" />
			)}
			{/* Skip to main content link - visually hidden but focusable */}
			<a
				href="#main-content"
				onClick={handleSkipToMain}
				className="absolute left-[-9999px] top-0 z-[10000] bg-primary px-4 py-2 text-primary-foreground focus:left-4 focus:top-4 focus:rounded-lg"
			>
				Skip to main content
			</a>

			<Sidebar />
			<div
				className={
					isItemDetail
						? "flex flex-1 flex-col overflow-hidden relative min-w-0 bg-transparent"
						: "flex flex-1 flex-col overflow-hidden bg-muted/20 relative min-w-0"
				}
			>
				{!isItemDetail && (
					<>
						<div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:32px_32px] pointer-events-none" />
						<div className="absolute inset-0 bg-gradient-to-tr from-background via-transparent to-background pointer-events-none" />
					</>
				)}

				<Header />
				<main
					id="main-content"
					role="main"
					className="flex-1 overflow-auto relative z-10 custom-scrollbar"
				>
					<div className={isItemDetail ? "p-0" : "p-6"}>
						<Outlet />
					</div>
				</main>
			</div>
			{/* Chat Sidebar - Always visible on the right */}
			<ChatBubble />
		</div>
	);
}
