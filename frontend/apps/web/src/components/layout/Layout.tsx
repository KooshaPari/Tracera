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
		<div className="flex h-screen overflow-hidden selection:bg-primary/20 selection:text-primary bg-transparent">
			<div className="pointer-events-none fixed inset-0 z-0 bg-[radial-gradient(circle_at_10%_15%,rgba(249,115,22,0.28),transparent_45%),radial-gradient(circle_at_85%_8%,rgba(14,116,144,0.3),transparent_42%),radial-gradient(circle_at_20%_75%,rgba(16,185,129,0.24),transparent_40%)]" />
			<div className="pointer-events-none fixed inset-0 z-0 bg-[linear-gradient(135deg,rgba(15,23,42,0.08),transparent_55%,rgba(8,47,73,0.12))]" />
			{!isItemDetail && (
				<div className="pointer-events-none fixed inset-0 z-0 bg-[radial-gradient(circle_at_30%_40%,rgba(148,163,184,0.08),transparent_55%)]" />
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
			<div className="flex flex-1 flex-col overflow-hidden relative min-w-0 bg-transparent">
				<div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:32px_32px] pointer-events-none" />

				<Header />
				<main
					id="main-content"
					role="main"
					className="flex-1 overflow-auto relative z-10 custom-scrollbar"
				>
					<div className="pointer-events-none absolute inset-x-0 top-0 h-44 bg-[radial-gradient(circle_at_20%_0%,rgba(59,130,246,0.18),transparent_65%),radial-gradient(circle_at_80%_0%,rgba(249,115,22,0.16),transparent_55%)]" />
					<div className={isItemDetail ? "p-0" : "px-4 py-6 sm:px-6 lg:px-8"}>
						<Outlet />
					</div>
				</main>
			</div>
			{/* Chat Sidebar - Always visible on the right */}
			<ChatBubble />
		</div>
	);
}
