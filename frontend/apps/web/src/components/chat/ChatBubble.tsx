/**
 * ChatSidebar - Permanent right sidebar with resize functionality
 */

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { cn, Button } from "@tracertm/ui";
import {
	GripVertical,
	ChevronRight,
	ChevronLeft,
	MessageCircle,
} from "lucide-react";
import { useChatStore } from "@/stores/chatStore";
import { ChatPanel } from "./ChatPanel";

export function ChatBubble() {
	const { sidebarWidth, setSidebarWidth } = useChatStore();
	const [isResizing, setIsResizing] = useState(false);
	const [isCollapsed, setIsCollapsed] = useState(() => {
		const saved = localStorage.getItem("chat-sidebar-collapsed");
		return saved === "true";
	});

	// Sidebar resize handler with granular drag
	const handleSidebarResize = useCallback(
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
				const delta = e.clientX - startX; // Normal direction for right sidebar
				const newWidth = Math.max(300, Math.min(800, startWidth + delta));
				setSidebarWidth(newWidth);
				localStorage.setItem("chat-sidebar-width", newWidth.toString());
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
		[sidebarWidth, setSidebarWidth],
	);

	// Handle keyboard shortcut
	useEffect(() => {
		const handleKeyDown = (e: KeyboardEvent) => {
			// Cmd+Shift+K or Ctrl+Shift+K to toggle chat sidebar
			if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === "k") {
				e.preventDefault();
				setIsCollapsed((prev) => {
					const newValue = !prev;
					localStorage.setItem("chat-sidebar-collapsed", String(newValue));
					return newValue;
				});
			}
		};

		window.addEventListener("keydown", handleKeyDown);
		return () => window.removeEventListener("keydown", handleKeyDown);
	}, []);

	const handleToggleCollapse = () => {
		setIsCollapsed((prev) => {
			const newValue = !prev;
			localStorage.setItem("chat-sidebar-collapsed", String(newValue));
			return newValue;
		});
	};

	return (
		<>
			{/* Sidebar container - only visible when not collapsed */}
			{!isCollapsed && (
				<div className="relative flex shrink-0 h-full">
					{/* Resize handle - wider drag zone for granular control */}
					<div
						onMouseDown={handleSidebarResize}
						className={cn(
							"w-2 cursor-ew-resize bg-transparent hover:bg-primary/30 transition-all flex items-center justify-center group shrink-0 relative",
							"active:cursor-ew-resize",
							isResizing && "bg-primary/50 cursor-ew-resize",
						)}
						role="separator"
						aria-label="Resize chat sidebar"
						aria-orientation="vertical"
						style={{ cursor: isResizing ? "ew-resize" : "ew-resize" }}
					>
						{/* Visual indicator */}
						<div className="w-0.5 h-full bg-muted-foreground/10 group-hover:bg-primary/40 transition-all rounded-full" />
						{/* Hover indicator dot */}
						<div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1 h-8 bg-primary/0 group-hover:bg-primary/60 transition-all rounded-full opacity-0 group-hover:opacity-100" />
						{/* Toggle button on resize handle */}
						<Button
							size="icon"
							variant="ghost"
							onClick={(e) => {
								e.stopPropagation();
								handleToggleCollapse();
							}}
							onMouseDown={(e) => e.stopPropagation()}
							className={cn(
								"absolute top-1/2 -translate-y-1/2 -left-3 h-6 w-6 rounded-full shadow-md transition-all duration-150 z-10",
								"bg-background/70 backdrop-blur-md hover:bg-primary hover:text-primary-foreground",
								"border border-white/20 hover:border-primary",
							)}
							aria-label="Collapse chat"
						>
							<ChevronRight className="h-3 w-3" />
						</Button>
					</div>

					{/* Chat Sidebar */}
					<motion.div
						initial={false}
						animate={{
							width: `${sidebarWidth}px`,
							opacity: 1,
						}}
						transition={{ type: "spring", damping: 25, stiffness: 300 }}
						className="relative flex flex-col border-l border-white/10 bg-card/60 backdrop-blur-xl shrink-0 overflow-hidden h-full min-w-0"
						style={{
							width: `${sidebarWidth}px`,
							minWidth: `${sidebarWidth}px`,
							maxWidth: `${sidebarWidth}px`,
						}}
					>
						<ChatPanel
							onClose={() => {}}
							onToggleMode={handleToggleCollapse}
							mode="sidebar"
							className="flex-1 rounded-none border-0 h-full"
						/>
					</motion.div>
				</div>
			)}

			{/* Floating bubble button when collapsed */}
			{isCollapsed && (
				<motion.div
					initial={{ scale: 0, opacity: 0 }}
					animate={{ scale: 1, opacity: 1 }}
					exit={{ scale: 0, opacity: 0 }}
					transition={{ type: "spring", damping: 20, stiffness: 300 }}
					className="fixed bottom-6 right-6 z-50"
				>
					<Button
						size="icon"
						onClick={handleToggleCollapse}
						className={cn(
							"h-14 w-14 rounded-full shadow-2xl transition-all duration-200",
							"bg-primary hover:bg-primary/90 text-primary-foreground",
							"hover:scale-110 active:scale-95",
							"border-0",
						)}
						aria-label="Open chat"
					>
						<MessageCircle className="h-6 w-6" />
					</Button>
				</motion.div>
			)}
		</>
	);
}
