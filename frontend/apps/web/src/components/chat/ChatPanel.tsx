/**
 * ChatPanel - Main chat interface with header, messages, and input.
 * Includes a Chat history button that opens a history panel (search, sort, delete).
 */

import { useChat } from "@/hooks/useChat";
import { logger } from "@/lib/logger";
import type { AIModel, ChatConversation, ChatMessage as ChatMessageType } from "@/lib/ai/types";
import { Button, ScrollArea, Textarea, cn } from "@tracertm/ui";
import {
	History,
	MessageSquarePlus,
	Send,
	Settings,
	Square,
	X,
} from "lucide-react";
import {
	type ChangeEvent,
	type KeyboardEvent,
	type MouseEvent,
	type RefObject,
	useCallback,
	useEffect,
	useMemo,
	useRef,
	useState,
} from "react";
import { ChatHistoryPanel } from "./ChatHistoryPanel";
import { ChatMessage } from "./ChatMessage";
import { ChatSettingsPanel } from "./ChatSettingsPanel";
import { ModelSelector } from "./ModelSelector";

const MAX_CONVERSATION_TABS = 5;

interface ChatPanelProps {
	onClose: () => void;
	onToggleMode: () => void;
	mode: "bubble" | "sidebar";
	className?: string;
}

const PanelHeader = ({
	isStreaming,
	model,
	onOpenHistory,
	onOpenSettings,
	onNewChat,
	onSelectModel,
}: {
	isStreaming: boolean;
	model: AIModel;
	onOpenHistory: () => void;
	onOpenSettings: () => void;
	onNewChat: () => void;
	onSelectModel: (model: AIModel) => void;
}) => (
	<div className="flex items-center justify-between px-3 py-2 border-b bg-muted/30 shrink-0 min-w-0">
		<div className="flex items-center gap-2 min-w-0 flex-1">
			<h3 className="font-semibold text-sm truncate min-w-0">
				TraceRTM Assistant
			</h3>
			<ModelSelector value={model} onChange={onSelectModel} disabled={isStreaming} />
		</div>
		<div className="flex items-center gap-1 shrink-0">
			<Button
				variant="ghost"
				size="icon"
				className="h-7 w-7"
				onClick={onOpenHistory}
				title="Chat history"
			>
				<History className="h-4 w-4" />
			</Button>
			<Button
				variant="ghost"
				size="icon"
				className="h-7 w-7"
				onClick={onOpenSettings}
				title="Chat settings & system prompt"
			>
				<Settings className="h-4 w-4" />
			</Button>
			<Button
				variant="ghost"
				size="icon"
				className="h-7 w-7"
				onClick={onNewChat}
				title="New chat"
			>
				<MessageSquarePlus className="h-4 w-4" />
			</Button>
		</div>
	</div>
);

const ConversationTab = ({
	conversation,
	isActive,
	onDelete,
	onSelect,
}: {
	conversation: ChatConversation;
	isActive: boolean;
	onDelete: (id: string) => void;
	onSelect: (id: string) => void;
}) => {
	const handleSelect = useCallback(() => {
		onSelect(conversation.id);
	}, [conversation.id, onSelect]);

	const handleDelete = useCallback(
		(event: MouseEvent<HTMLButtonElement>) => {
			event.stopPropagation();
			onDelete(conversation.id);
		},
		[conversation.id, onDelete],
	);

	return (
		<button
			type="button"
			onClick={handleSelect}
			className={cn(
				"flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-colors cursor-pointer shrink-0 min-w-0",
				"hover:bg-muted",
				isActive ? "bg-muted font-medium" : "text-muted-foreground",
			)}
		>
			<span className="max-w-[120px] truncate min-w-0">
				{conversation.title}
			</span>
			<button
				type="button"
				onClick={handleDelete}
				className="opacity-50 hover:opacity-100 hover:bg-muted/50 rounded p-0.5 transition-all cursor-pointer"
			>
				<X className="h-3 w-3" />
			</button>
		</button>
	);
};

const ConversationTabs = ({
	activeConversationId,
	conversations,
	onDeleteConversation,
	onSelectConversation,
}: {
	activeConversationId: string | null;
	conversations: ChatConversation[];
	onDeleteConversation: (id: string) => void;
	onSelectConversation: (id: string) => void;
}) => {
	const visibleConversations = useMemo(
		() => conversations.slice(0, MAX_CONVERSATION_TABS),
		[conversations],
	);

	return (
		<div className="flex items-center gap-1 px-2 py-1.5 border-b bg-muted/20 overflow-x-auto shrink-0 min-w-0 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
			{visibleConversations.map((conversation) => (
				<ConversationTab
					key={conversation.id}
					conversation={conversation}
					isActive={conversation.id === activeConversationId}
					onDelete={onDeleteConversation}
					onSelect={onSelectConversation}
				/>
			))}
		</div>
	);
};

const EmptyMessages = () => (
	<div className="flex flex-col items-center justify-center h-full py-8 text-center min-w-0 w-full">
		<div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-3 shrink-0">
			<MessageSquarePlus className="w-6 h-6 text-primary" />
		</div>
		<h4 className="font-medium mb-1 min-w-0">Welcome to TraceRTM Assistant</h4>
		<p className="text-sm text-muted-foreground max-w-[250px] min-w-0 w-full px-4">
			Ask questions about requirements traceability, project management, or get
			help navigating TraceRTM.
		</p>
	</div>
);

const MessagesList = ({
	messages,
	messagesEndRef,
}: {
	messages: ChatMessageType[];
	messagesEndRef: RefObject<HTMLDivElement | null>;
}) => {
	const lastMessageId = messages.length > 0 ? messages[messages.length - 1]?.id : null;

	return (
		<div className="space-y-2 min-w-0 w-full">
			{messages.map((message) => (
				<ChatMessage
					key={message.id}
					message={message}
					isLast={message.id === lastMessageId}
				/>
			))}
			<div ref={messagesEndRef} />
		</div>
	);
};

const ChatInput = ({
	disabled,
	inputValue,
	onChange,
	onKeyDown,
	onSend,
	onStop,
	textareaRef,
}: {
	disabled: boolean;
	inputValue: string;
	onChange: (event: ChangeEvent<HTMLTextAreaElement>) => void;
	onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void;
	onSend: () => void;
	onStop: () => void;
	textareaRef: RefObject<HTMLTextAreaElement | null>;
}) => (
	<div className="p-3 border-t bg-muted/20 shrink-0 min-w-0">
		<div className="flex gap-2 min-w-0">
			<Textarea
				ref={textareaRef}
				value={inputValue}
				onChange={onChange}
				onKeyDown={onKeyDown}
				placeholder="Ask a question..."
				className="min-h-[40px] max-h-[120px] resize-none text-sm flex-1 min-w-0"
				disabled={disabled}
				rows={1}
			/>
			{disabled ? (
				<Button
					size="icon"
					variant="destructive"
					onClick={onStop}
					title="Stop generating"
				>
					<Square className="h-4 w-4" />
				</Button>
			) : (
				<Button
					size="icon"
					onClick={onSend}
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
);

const useAutoScroll = (ref: RefObject<HTMLDivElement | null>, key: number) => {
	useEffect(() => {
		ref.current?.scrollIntoView({ behavior: "smooth" });
	}, [key, ref]);
};

const useBubbleFocus = (
	mode: "bubble" | "sidebar",
	ref: RefObject<HTMLTextAreaElement | null>,
) => {
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
		ref.current?.focus();
	}, [mode, ref]);
};

const useChatPanelState = (mode: "bubble" | "sidebar") => {
	const chat = useChat();
	const [inputValue, setInputValue] = useState("");
	const [isHistoryOpen, setIsHistoryOpen] = useState(false);
	const [isSettingsOpen, setIsSettingsOpen] = useState(false);
	const messagesEndRef = useRef<HTMLDivElement>(null);
	const textareaRef = useRef<HTMLTextAreaElement>(null);
	const messages = chat.activeConversation?.messages ?? [];

	useAutoScroll(messagesEndRef, messages.length);
	useBubbleFocus(mode, textareaRef);

	return {
		chat,
		inputValue,
		isHistoryOpen,
		isSettingsOpen,
		messages,
		messagesEndRef,
		setInputValue,
		setIsHistoryOpen,
		setIsSettingsOpen,
		textareaRef,
	};
};

const ChatPanelBody = ({
	chat,
	inputValue,
	isHistoryOpen,
	isSettingsOpen,
	messages,
	messagesEndRef,
	onCloseHistory,
	onCloseSettings,
	onInputChange,
	onKeyDown,
	onSelectConversation,
	onSend,
	textareaRef,
}: {
	chat: ReturnType<typeof useChat>;
	inputValue: string;
	isHistoryOpen: boolean;
	isSettingsOpen: boolean;
	messages: ChatMessageType[];
	messagesEndRef: RefObject<HTMLDivElement | null>;
	onCloseHistory: () => void;
	onCloseSettings: () => void;
	onInputChange: (event: ChangeEvent<HTMLTextAreaElement>) => void;
	onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void;
	onSelectConversation: (id: string) => void;
	onSend: () => void;
	textareaRef: RefObject<HTMLTextAreaElement | null>;
}) => {
	if (isSettingsOpen) {
		return (
			<div className="flex-1 min-h-0 flex flex-col overflow-hidden">
				<ChatSettingsPanel
					context={chat.context ?? null}
					systemPromptOverride={chat.systemPromptOverride}
					onSystemPromptOverrideChange={chat.setSystemPromptOverride}
					onClose={onCloseSettings}
					className="flex-1 min-h-0"
				/>
			</div>
		);
	}

	if (isHistoryOpen) {
		return (
			<div className="flex-1 min-h-0 flex flex-col overflow-hidden">
				<ChatHistoryPanel
					conversations={chat.conversations}
					activeConversationId={chat.activeConversation?.id ?? null}
					projectId={chat.context?.project?.id ?? null}
					onSelectConversation={onSelectConversation}
					onDeleteConversation={chat.deleteConversation}
					onClose={onCloseHistory}
					className="flex-1 min-h-0"
				/>
			</div>
		);
	}

	return (
		<>
			{chat.conversations.length > 1 ? (
				<ConversationTabs
					activeConversationId={chat.activeConversation?.id ?? null}
					conversations={chat.conversations}
					onDeleteConversation={chat.deleteConversation}
					onSelectConversation={onSelectConversation}
				/>
			) : null}

			<ScrollArea className="flex-1 p-2 min-w-0 overflow-hidden">
				{messages.length === 0 ? (
					<EmptyMessages />
				) : (
					<MessagesList messages={messages} messagesEndRef={messagesEndRef} />
				)}
			</ScrollArea>

			<ChatInput
				disabled={chat.isStreaming}
				inputValue={inputValue}
				onChange={onInputChange}
				onKeyDown={onKeyDown}
				onSend={onSend}
				onStop={chat.stopStreaming}
				textareaRef={textareaRef}
			/>
		</>
	);
};

export const ChatPanel = ({ mode, className }: ChatPanelProps) => {
	const {
		chat,
		inputValue,
		isHistoryOpen,
		isSettingsOpen,
		messages,
		messagesEndRef,
		setInputValue,
		setIsHistoryOpen,
		setIsSettingsOpen,
		textareaRef,
	} = useChatPanelState(mode);

	const handleOpenHistory = useCallback(() => {
		setIsHistoryOpen(true);
	}, [setIsHistoryOpen]);

	const handleOpenSettings = useCallback(() => {
		setIsSettingsOpen(true);
	}, [setIsSettingsOpen]);

	const handleCloseHistory = useCallback(() => {
		setIsHistoryOpen(false);
	}, [setIsHistoryOpen]);

	const handleCloseSettings = useCallback(() => {
		setIsSettingsOpen(false);
	}, [setIsSettingsOpen]);

	const handleInputChange = useCallback(
		(event: ChangeEvent<HTMLTextAreaElement>) => {
			setInputValue(event.target.value);
		},
		[setInputValue],
	);

	const handleSend = useCallback(() => {
		const content = inputValue.trim();
		if (!content || chat.isStreaming) {
			return;
		}

		setInputValue("");
		chat
			.sendMessage(content)
			.catch((error) => logger.error("Failed to send chat message:", error));
	}, [chat, inputValue, setInputValue]);

	const handleKeyDown = useCallback(
		(event: KeyboardEvent<HTMLTextAreaElement>) => {
			if (event.key === "Enter" && !event.shiftKey) {
				event.preventDefault();
				handleSend();
			}
		},
		[handleSend],
	);

	const handleNewChat = useCallback(() => {
		chat.createConversation();
		setInputValue("");
		textareaRef.current?.focus();
	}, [chat, setInputValue, textareaRef]);

	const handleSelectConversation = useCallback(
		(id: string) => {
			chat.setActiveConversation(id);
		},
		[chat],
	);

	return (
		<div
			className={cn(
				"flex flex-col bg-background border rounded-lg shadow-xl overflow-hidden",
				className,
			)}
		>
			<PanelHeader
				isStreaming={chat.isStreaming}
				model={chat.selectedModel}
				onOpenHistory={handleOpenHistory}
				onOpenSettings={handleOpenSettings}
				onNewChat={handleNewChat}
				onSelectModel={chat.setSelectedModel}
			/>
			<ChatPanelBody
				chat={chat}
				inputValue={inputValue}
				isHistoryOpen={isHistoryOpen}
				isSettingsOpen={isSettingsOpen}
				messages={messages}
				messagesEndRef={messagesEndRef}
				onCloseHistory={handleCloseHistory}
				onCloseSettings={handleCloseSettings}
				onInputChange={handleInputChange}
				onKeyDown={handleKeyDown}
				onSelectConversation={handleSelectConversation}
				onSend={handleSend}
				textareaRef={textareaRef}
			/>
		</div>
	);
};
