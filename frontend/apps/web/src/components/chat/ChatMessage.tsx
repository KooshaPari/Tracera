/**
 * ChatMessage - Individual chat message component.
 * Shows text content and, for assistant messages, a collapsible "Tools used (MCP)" section when tool calls are present.
 */

import { cn } from "@tracertm/ui";
import {
	Collapsible,
	CollapsibleContent,
	CollapsibleTrigger,
} from "@tracertm/ui/components/Collapsible";
import { Badge } from "@tracertm/ui/components/Badge";
import {
	Bot,
	ChevronDown,
	ChevronRight,
	Loader2,
	User,
	Wrench,
} from "lucide-react";
import { useState } from "react";
import type { ChatMessage as ChatMessageType, ToolCall } from "@/lib/ai/types";

interface ChatMessageProps {
	message: ChatMessageType;
	isLast?: boolean;
}

export function ChatMessage({ message, isLast }: ChatMessageProps) {
	const isUser = message.role === "user";
	const isStreaming = message.isStreaming && isLast;
	const hasToolCalls =
		!isUser && message.toolCalls && message.toolCalls.length > 0;
	const [toolsOpen, setToolsOpen] = useState(false);

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

				{/* MCP / Tools used (collapsible) */}
				{hasToolCalls && (
					<Collapsible open={toolsOpen} onOpenChange={setToolsOpen}>
						<CollapsibleTrigger className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors mt-2">
							{toolsOpen ? (
								<ChevronDown className="h-3.5 w-3.5" />
							) : (
								<ChevronRight className="h-3.5 w-3.5" />
							)}
							<Wrench className="h-3.5 w-3.5" />
							<span>Tools used ({message.toolCalls!.length})</span>
						</CollapsibleTrigger>
						<CollapsibleContent>
							<ul className="mt-1.5 space-y-1.5 pl-4 border-l-2 border-muted">
								{message.toolCalls!.map((tc) => (
									<ToolCallRow key={tc.id} toolCall={tc} />
								))}
							</ul>
						</CollapsibleContent>
					</Collapsible>
				)}

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

function ToolCallRow({ toolCall }: { toolCall: ToolCall }) {
	const status = toolCall.isExecuting
		? "running"
		: toolCall.result
			? toolCall.result.success
				? "ok"
				: "error"
			: "—";
	return (
		<li className="text-xs">
			<div className="flex items-center gap-2 flex-wrap">
				<span className="font-medium">{toolCall.name}</span>
				<Badge
					variant={
						status === "error"
							? "destructive"
							: (status === "running"
								? "secondary"
								: "outline")
					}
					className="text-[10px] px-1.5 py-0"
				>
					{status === "running" ? "…" : status}
				</Badge>
			</div>
			{Object.keys(toolCall.input).length > 0 && (
				<pre className="mt-0.5 text-[10px] text-muted-foreground overflow-x-auto rounded bg-muted/50 p-1 font-mono">
					{JSON.stringify(toolCall.input)}
				</pre>
			)}
			{toolCall.result && !toolCall.result.success && toolCall.result.error && (
				<p className="mt-0.5 text-[10px] text-destructive">
					{toolCall.result.error}
				</p>
			)}
		</li>
	);
}

function formatMessageTime(isoString: string): string {
	try {
		const date = new Date(isoString);
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffMins = Math.floor(diffMs / 60_000);

		if (diffMins < 1) {
			return "Just now";
		}
		if (diffMins < 60) {
			return `${diffMins}m ago`;
		}

		const diffHours = Math.floor(diffMins / 60);
		if (diffHours < 24) {
			return `${diffHours}h ago`;
		}

		return date.toLocaleDateString(undefined, {
			day: "numeric",
			hour: "numeric",
			minute: "2-digit",
			month: "short",
		});
	} catch {
		return "";
	}
}
