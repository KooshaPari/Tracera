/**
 * ChatMessage - Individual chat message component
 */

import { cn } from "@tracertm/ui";
import { Bot, User, Loader2 } from "lucide-react";
import type { ChatMessage as ChatMessageType } from "@/lib/ai/types";

interface ChatMessageProps {
	message: ChatMessageType;
	isLast?: boolean;
}

export function ChatMessage({ message, isLast }: ChatMessageProps) {
	const isUser = message.role === "user";
	const isStreaming = message.isStreaming && isLast;

	return (
		<div
			className={cn(
				"flex gap-3 p-4 rounded-lg",
				isUser ? "bg-primary/5" : "bg-muted/50",
			)}
		>
			{/* Avatar */}
			<div
				className={cn(
					"flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
					isUser
						? "bg-primary text-primary-foreground"
						: "bg-muted-foreground/20",
				)}
			>
				{isUser ? (
					<User className="w-4 h-4" />
				) : (
					<Bot className="w-4 h-4 text-muted-foreground" />
				)}
			</div>

			{/* Content */}
			<div className="flex-1 min-w-0 space-y-1">
				{/* Role label */}
				<div className="text-xs font-medium text-muted-foreground">
					{isUser ? "You" : "TraceRTM Assistant"}
				</div>

				{/* Message content */}
				<div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
					{message.content || (
						<span className="text-muted-foreground italic">
							{isStreaming ? "Thinking..." : "Empty message"}
						</span>
					)}
					{isStreaming && (
						<span className="inline-flex items-center ml-1">
							<Loader2 className="w-3 h-3 animate-spin text-primary" />
						</span>
					)}
				</div>

				{/* Timestamp */}
				{!isStreaming && (
					<div className="text-[10px] text-muted-foreground/60">
						{formatMessageTime(message.createdAt)}
					</div>
				)}
			</div>
		</div>
	);
}

function formatMessageTime(isoString: string): string {
	try {
		const date = new Date(isoString);
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffMins = Math.floor(diffMs / 60000);

		if (diffMins < 1) return "Just now";
		if (diffMins < 60) return `${diffMins}m ago`;

		const diffHours = Math.floor(diffMins / 60);
		if (diffHours < 24) return `${diffHours}h ago`;

		return date.toLocaleDateString(undefined, {
			month: "short",
			day: "numeric",
			hour: "numeric",
			minute: "2-digit",
		});
	} catch {
		return "";
	}
}
