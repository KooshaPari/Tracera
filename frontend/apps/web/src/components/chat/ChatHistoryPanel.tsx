/**
 * ChatHistoryPanel - List of past conversations with search, sort, and delete.
 * Borrows ideas from agent/chat history UIs: search, sort (newest/oldest), per-item delete, click to open.
 */

import {
	Button,
	cn,
	Input,
	ScrollArea,
} from "@tracertm/ui";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui/components/Select";
import { History, Search, Trash2, X } from "lucide-react";
import { useMemo, useState } from "react";
import type { ChatConversation } from "@/lib/ai/types";

type SortOption = "newest" | "oldest";

function formatDate(iso: string) {
	const d = new Date(iso);
	const now = new Date();
	const sameDay =
		d.getDate() === now.getDate() &&
		d.getMonth() === now.getMonth() &&
		d.getFullYear() === now.getFullYear();
	if (sameDay) {
		return d.toLocaleTimeString(undefined, {
			hour: "2-digit",
			minute: "2-digit",
		});
	}
	return d.toLocaleDateString(undefined, {
		month: "short",
		day: "numeric",
		year:
			d.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
	});
}

interface ChatHistoryPanelProps {
	conversations: ChatConversation[];
	activeConversationId: string | null;
	projectId?: string | null;
	onSelectConversation: (id: string) => void;
	onDeleteConversation: (id: string) => void;
	onClose: () => void;
	className?: string;
}

export function ChatHistoryPanel({
	conversations,
	activeConversationId,
	projectId,
	onSelectConversation,
	onDeleteConversation,
	onClose,
	className,
}: ChatHistoryPanelProps) {
	const [searchQuery, setSearchQuery] = useState("");
	const [sort, setSort] = useState<SortOption>("newest");
	const [filterByProject, setFilterByProject] = useState(false);

	const filteredAndSorted = useMemo(() => {
		let list = [...conversations];

		if (filterByProject && projectId) {
			list = list.filter((c) => c.projectId === projectId);
		}

		const q = searchQuery.trim().toLowerCase();
		if (q) {
			list = list.filter(
				(c) =>
					c.title.toLowerCase().includes(q) ||
					c.messages.some(
						(m) =>
							m.content &&
							m.content.toLowerCase().includes(q),
					),
			);
		}

		list.sort((a, b) => {
			const ta = new Date(a.updatedAt).getTime();
			const tb = new Date(b.updatedAt).getTime();
			return sort === "newest" ? tb - ta : ta - tb;
		});

		return list;
	}, [conversations, searchQuery, sort, filterByProject, projectId]);

	return (
		<div
			className={cn(
				"flex flex-col bg-background h-full overflow-hidden rounded-lg",
				className,
			)}
		>
			{/* Header */}
			<div className="flex items-center justify-between px-3 py-2 border-b bg-muted/30 shrink-0">
				<div className="flex items-center gap-2 min-w-0">
					<History className="h-4 w-4 shrink-0 text-muted-foreground" />
					<h3 className="font-semibold text-sm truncate min-w-0">
						Chat history
					</h3>
				</div>
				<Button
					variant="ghost"
					size="icon"
					className="h-7 w-7 shrink-0"
					onClick={onClose}
					title="Back to chat"
				>
					<X className="h-4 w-4" />
				</Button>
			</div>

			{/* Filters */}
			<div className="px-2 py-2 border-b bg-muted/10 space-y-2 shrink-0">
				<div className="relative">
					<Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
					<Input
						placeholder="Search by title or content..."
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
						className="pl-8 h-8 text-sm"
					/>
				</div>
				<div className="flex items-center gap-2">
					<Select
						value={sort}
						onValueChange={(v) => setSort(v as SortOption)}
					>
						<SelectTrigger className="h-8 text-xs flex-1 min-w-0">
							<SelectValue />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value="newest">Newest first</SelectItem>
							<SelectItem value="oldest">Oldest first</SelectItem>
						</SelectContent>
					</Select>
					{projectId && (
						<Button
							variant={filterByProject ? "secondary" : "ghost"}
							size="sm"
							className="h-8 text-xs shrink-0"
							onClick={() => setFilterByProject(!filterByProject)}
						>
							{filterByProject ? "This project" : "All"}
						</Button>
					)}
				</div>
			</div>

			{/* List */}
			<ScrollArea className="flex-1 min-h-0 p-2">
				{filteredAndSorted.length === 0 ? (
					<div className="flex flex-col items-center justify-center py-8 text-center text-muted-foreground text-sm">
						<History className="h-10 w-10 mb-2 opacity-50" />
						{conversations.length === 0
							? "No conversations yet. Start a chat to see history here."
							: "No conversations match your search or filter."}
					</div>
				) : (
					<ul className="space-y-1">
						{filteredAndSorted.map((conv) => (
							<li key={conv.id}>
								<div
									className={cn(
										"group flex items-center gap-2 rounded-md px-2 py-2 cursor-pointer transition-colors border",
										conv.id === activeConversationId
											? "bg-primary/10 border-primary/30"
											: "hover:bg-muted/50 border-transparent",
									)}
									onClick={() => {
										onSelectConversation(conv.id);
										onClose();
									}}
								>
									<div className="flex-1 min-w-0">
										<p className="text-sm font-medium truncate">
											{conv.title || "New Chat"}
										</p>
										<p className="text-xs text-muted-foreground">
											{formatDate(conv.updatedAt)}
											{conv.messages.length > 0 && (
												<>
													{" · "}
													{conv.messages.length} message
													{conv.messages.length !== 1 ? "s" : ""}
												</>
											)}
										</p>
									</div>
									<Button
										variant="ghost"
										size="icon"
										className="h-7 w-7 opacity-50 group-hover:opacity-100 shrink-0"
										onClick={(e) => {
											e.stopPropagation();
											onDeleteConversation(conv.id);
										}}
										title="Delete conversation"
									>
										<Trash2 className="h-3.5 w-3.5" />
									</Button>
								</div>
							</li>
						))}
					</ul>
				)}
			</ScrollArea>
		</div>
	);
}
