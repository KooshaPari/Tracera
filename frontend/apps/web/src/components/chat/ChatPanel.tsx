/**
 * ChatPanel - Main chat interface with header, messages, and input.
 * Includes a Chat history button that opens a history panel (search, sort, delete).
 */

import { Button, ScrollArea, Textarea, cn } from "@tracertm/ui";
import {
	History,
	MessageSquarePlus,
	Send,
	Settings,
	Square,
	X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import { useChat } from "@/hooks/useChat";
import { ChatHistoryPanel } from "./ChatHistoryPanel";
import { ChatMessage } from "./ChatMessage";
import { ChatSettingsPanel } from "./ChatSettingsPanel";
import { ModelSelector } from "./ModelSelector";

interface ChatPanelProps {
	onClose: () => void;
	onToggleMode: () => void;
	mode: "bubble" | "sidebar";
	className?: string;
}

export function ChatPanel({ mode, className }: ChatPanelProps) {
	const {
		isStreaming,
		selectedModel,
		activeConversation,
		conversations,
		context,
		systemPromptOverride,
		setSystemPromptOverride,
		setSelectedModel,
		sendMessage,
		stopStreaming,
		createConversation,
		setActiveConversation,
		deleteConversation,
	} = useChat();

	const [inputValue, setInputValue] = useState("");
	const [isHistoryOpen, setIsHistoryOpen] = useState(false);
	const [isSettingsOpen, setIsSettingsOpen] = useState(false);
	const messagesEndRef = useRef<HTMLDivElement>(null);
	const textareaRef = useRef<HTMLTextAreaElement>(null);

	// Auto-scroll to bottom when messages change
	useEffect(() => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	}, []);

	// Avoid stealing initial focus when the sidebar is mounted
	useEffect(() => {
		if (mode !== "bubble") {
			return;
		}
		if (
			typeof document !== "undefined" &&
			document.activeElement !== document.body
		) {
			return;
		}
		textareaRef.current?.focus();
	}, [mode]);

	const handleSend = () => {
		const content = inputValue.trim();
		if (!content || isStreaming) {
			return;
		}

		setInputValue("");
		undefined;
	};

	const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			handleSend();
		}
	};

	const handleNewChat = () => {
		createConversation();
		setInputValue("");
		textareaRef.current?.focus();
	};

	const messages = activeConversation?.messages ?? [];

	return (
		<div
			className={cn(
				"flex flex-col bg-background border rounded-lg shadow-xl overflow-hidden",
				className,
			)}
		>
			{/* Header */}
			<div className="flex items-center justify-between px-3 py-2 border-b bg-muted/30 shrink-0 min-w-0">
				<div className="flex items-center gap-2 min-w-0 flex-1">
					<h3 className="font-semibold text-sm truncate min-w-0">
						TraceRTM Assistant
					</h3>
					<ModelSelector
						value={selectedModel}
						onChange={setSelectedModel}
						disabled={isStreaming}
					/>
				</div>
				<div className="flex items-center gap-1 shrink-0">
					<Button
						variant="ghost"
						size="icon"
						className="h-7 w-7"
						onClick={() => setIsHistoryOpen(true)}
						title="Chat history"
					>
						<History className="h-4 w-4" />
					</Button>
					<Button
						variant="ghost"
						size="icon"
						className="h-7 w-7"
						onClick={() => setIsSettingsOpen(true)}
						title="Chat settings & system prompt"
					>
						<Settings className="h-4 w-4" />
					</Button>
					<Button
						variant="ghost"
						size="icon"
						className="h-7 w-7"
						onClick={handleNewChat}
						title="New chat"
					>
						<MessageSquarePlus className="h-4 w-4" />
					</Button>
				</div>
			</div>

			{/* Settings panel (replaces messages when open) */}
			{isSettingsOpen ? (
				<div className="flex-1 min-h-0 flex flex-col overflow-hidden">
					<ChatSettingsPanel
						context={context ?? null}
						systemPromptOverride={systemPromptOverride}
						onSystemPromptOverrideChange={setSystemPromptOverride}
						onClose={() => setIsSettingsOpen(false)}
						className="flex-1 min-h-0"
					/>
				</div>
			) : (isHistoryOpen ? (
				<div className="flex-1 min-h-0 flex flex-col overflow-hidden">
					<ChatHistoryPanel
						conversations={conversations}
						activeConversationId={activeConversation?.id ?? null}
						projectId={context?.project?.id ?? null}
						onSelectConversation={setActiveConversation}
						onDeleteConversation={deleteConversation}
						onClose={() => setIsHistoryOpen(false)}
						className="flex-1 min-h-0"
					/>
				</div>
			) : (
				<>
					{/* Conversation tabs (if multiple) */}
					{conversations.length > 1 && (
						<div className="flex items-center gap-1 px-2 py-1.5 border-b bg-muted/20 overflow-x-auto shrink-0 min-w-0 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
							{conversations.slice(0, 5).map((conv) => (
								<button
									key={conv.id}
									type="button"
									onClick={() => setActiveConversation(conv.id)}
									className={cn(
										"flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-colors cursor-pointer shrink-0 min-w-0",
										"hover:bg-muted",
										conv.id === activeConversation?.id
											? "bg-muted font-medium"
											: "text-muted-foreground",
									)}
								>
									<span className="max-w-[120px] truncate min-w-0">
										{conv.title}
									</span>
									<button
										type="button"
										onClick={(e) => {
											e.stopPropagation();
											deleteConversation(conv.id);
										}}
										className="opacity-50 hover:opacity-100 hover:bg-muted/50 rounded p-0.5 transition-all cursor-pointer"
									>
										<X className="h-3 w-3" />
									</button>
								</button>
							))}
						</div>
					)}

					{/* Messages */}
					<ScrollArea className="flex-1 p-2 min-w-0 overflow-hidden">
						{messages.length === 0 ? (
							<div className="flex flex-col items-center justify-center h-full py-8 text-center min-w-0 w-full">
								<div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-3 shrink-0">
									<MessageSquarePlus className="w-6 h-6 text-primary" />
								</div>
								<h4 className="font-medium mb-1 min-w-0">
									Welcome to TraceRTM Assistant
								</h4>
								<p className="text-sm text-muted-foreground max-w-[250px] min-w-0 w-full px-4">
									Ask questions about requirements traceability, project
									management, or get help navigating TraceRTM.
								</p>
							</div>
						) : (
							<div className="space-y-2 min-w-0 w-full">
								{messages.map((message, index) => (
									<ChatMessage
										key={message.id}
										message={message}
										isLast={index === messages.length - 1}
									/>
								))}
								<div ref={messagesEndRef} />
							</div>
						)}
					</ScrollArea>

					{/* Input */}
					<div className="p-3 border-t bg-muted/20 shrink-0 min-w-0">
						<div className="flex gap-2 min-w-0">
							<Textarea
								ref={textareaRef}
								value={inputValue}
								onChange={(e) => setInputValue(e.target.value)}
								onKeyDown={handleKeyDown}
								placeholder="Ask a question..."
								className="min-h-[40px] max-h-[120px] resize-none text-sm flex-1 min-w-0"
								disabled={isStreaming}
								rows={1}
							/>
							{isStreaming ? (
								<Button
									size="icon"
									variant="destructive"
									onClick={stopStreaming}
									title="Stop generating"
								>
									<Square className="h-4 w-4" />
								</Button>
							) : (
								<Button
									size="icon"
									onClick={handleSend}
									disabled={!inputValue.trim()}
									title="Send message"
								>
									<Send className="h-4 w-4" />
								</Button>
							)}
						</div>
						<div className="mt-1.5 text-[10px] text-muted-foreground text-center truncate min-w-0">
							Press Enter to send, Shift+Enter for new line
						</div>
					</div>
				</>
			))}
		</div>
	);
}
