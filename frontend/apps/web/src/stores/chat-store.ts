/**
 * Chat Store - Zustand state management for AI chat assistant
 */

import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { getDefaultModel } from "@/lib/ai/modelRegistry";
import type {
	AIModel,
	ChatContext,
	ChatConversation,
	ChatMessage,
	ChatUIState,
	ToolCall,
} from "@/lib/ai/types";
import { generateId } from "@/lib/ai/types";

// SSR-safe storage
const noopStorage = {
	getItem: (_key: string) => null,
	removeItem: (_key: string) => {},
	setItem: (_key: string, _value: string) => {},
};

const getStorage = () => {
	if (
		typeof globalThis.window === "undefined" ||
		typeof localStorage === "undefined" ||
		typeof localStorage.getItem !== "function"
	) {
		return noopStorage;
	}
	return localStorage;
};

interface ChatState extends ChatUIState {
	// Conversations
	conversations: ChatConversation[];
	activeConversationId: string | null;

	// Streaming state
	isStreaming: boolean;
	abortController: AbortController | null;

	// Model selection
	selectedModel: AIModel;

	// System prompt override (optional custom prompt; empty = use built-in)
	systemPromptOverride: string | null;

	// Context
	context: ChatContext | null;

	// UI Actions
	toggleOpen: () => void;
	setOpen: (open: boolean) => void;
	setMode: (mode: "bubble" | "sidebar") => void;
	setBubblePosition: (position: { x: number; y: number }) => void;
	setSidebarWidth: (width: number) => void;

	// Conversation Actions
	createConversation: (projectId?: string) => string;
	setActiveConversation: (id: string | null) => void;
	setConversationSessionId: (
		conversationId: string,
		sessionId: string | null,
	) => void;
	deleteConversation: (id: string) => void;
	clearConversations: () => void;
	updateConversationTitle: (id: string, title: string) => void;

	// Message Actions
	addMessage: (
		conversationId: string,
		role: "user" | "assistant",
		content: string,
	) => string;
	updateMessage: (
		conversationId: string,
		messageId: string,
		content: string,
	) => void;
	updateMessageToolCalls: (
		conversationId: string,
		messageId: string,
		toolCalls: ToolCall[],
	) => void;
	setMessageStreaming: (
		conversationId: string,
		messageId: string,
		isStreaming: boolean,
	) => void;

	// Streaming Actions
	setStreaming: (streaming: boolean) => void;
	setAbortController: (controller: AbortController | null) => void;
	stopStreaming: () => void;

	// Model Actions
	setSelectedModel: (model: AIModel) => void;

	// System prompt override
	setSystemPromptOverride: (value: string | null) => void;

	// Context Actions
	setContext: (context: ChatContext | null) => void;

	// Helpers
	getActiveConversation: () => ChatConversation | null;
}

export const useChatStore = create<ChatState>()(
	persist(
		(set, get) => ({
			// Initial UI state
			isOpen: false,
			mode: "bubble",
			bubblePosition: { x: -1, y: -1 }, // -1 means use default position
			sidebarWidth: 400,

			// Initial chat state
			conversations: [],
			activeConversationId: null,
			isStreaming: false,
			abortController: null,
			selectedModel: getDefaultModel(),
			systemPromptOverride: null,
			context: null,

			// UI Actions
			toggleOpen: () => set((state) => ({ isOpen: !state.isOpen })),
			setOpen: (open) => set({ isOpen: open }),
			setMode: (mode) => set({ mode }),
			setBubblePosition: (position) => set({ bubblePosition: position }),
			setSidebarWidth: (width) =>
				set({ sidebarWidth: Math.max(300, Math.min(800, width)) }),

			// Conversation Actions
			createConversation: (projectId) => {
				const id = generateId();
				const conversation: ChatConversation = {
					id,
					title: "New Chat",
					model: get().selectedModel,
					messages: [],
					createdAt: new Date().toISOString(),
					updatedAt: new Date().toISOString(),
					...(projectId ? { projectId } : {}),
				};
				set((state) => ({
					activeConversationId: id,
					conversations: [conversation, ...state.conversations],
				}));
				return id;
			},

			setActiveConversation: (id) => set({ activeConversationId: id }),

			setConversationSessionId: (conversationId, sessionId) =>
				set((state) => ({
					conversations: state.conversations.map((c) =>
						c.id === conversationId ? { ...c, sessionId } : c,
					),
				})),

			deleteConversation: (id) =>
				set((state) => {
					const filtered = state.conversations.filter((c) => c.id !== id);
					const newActiveId =
						state.activeConversationId === id
							? (filtered[0]?.id ?? null)
							: state.activeConversationId;
					return {
						activeConversationId: newActiveId,
						conversations: filtered,
					};
				}),

			clearConversations: () =>
				set({
					activeConversationId: null,
					conversations: [],
				}),

			updateConversationTitle: (id, title) =>
				set((state) => ({
					conversations: state.conversations.map((c) =>
						c.id === id
							? { ...c, title, updatedAt: new Date().toISOString() }
							: c,
					),
				})),

			// Message Actions
			addMessage: (conversationId, role, content) => {
				const messageId = generateId();
				const message: ChatMessage = {
					content,
					conversationId,
					createdAt: new Date().toISOString(),
					id: messageId,
					isStreaming: role === "assistant",
					role,
				};

				set((state) => ({
					conversations: state.conversations.map((c) => {
						if (c.id !== conversationId) {
							return c;
						}

						// Auto-generate title from first user message
						let newTitle = c.title;
						if (role === "user" && c.messages.length === 0) {
							newTitle =
								content.slice(0, 50) + (content.length > 50 ? "..." : "");
						}

						return {
							...c,
							title: newTitle,
							messages: [...c.messages, message],
							updatedAt: new Date().toISOString(),
						};
					}),
				}));

				return messageId;
			},

			updateMessage: (conversationId, messageId, content) =>
				set((state) => ({
					conversations: state.conversations.map((c) =>
						c.id === conversationId
							? {
									...c,
									messages: c.messages.map((m) =>
										m.id === messageId ? { ...m, content } : m,
									),
									updatedAt: new Date().toISOString(),
								}
							: c,
					),
				})),

			updateMessageToolCalls: (conversationId, messageId, toolCalls) =>
				set((state) => ({
					conversations: state.conversations.map((c) =>
						c.id === conversationId
							? {
									...c,
									messages: c.messages.map((m) =>
										m.id === messageId ? { ...m, toolCalls } : m,
									),
									updatedAt: new Date().toISOString(),
								}
							: c,
					),
				})),

			setMessageStreaming: (conversationId, messageId, isStreaming) =>
				set((state) => ({
					conversations: state.conversations.map((c) =>
						c.id === conversationId
							? {
									...c,
									messages: c.messages.map((m) =>
										m.id === messageId ? { ...m, isStreaming } : m,
									),
								}
							: c,
					),
				})),

			// Streaming Actions
			setStreaming: (streaming) => set({ isStreaming: streaming }),
			setAbortController: (controller) => set({ abortController: controller }),
			stopStreaming: () => {
				const { abortController } = get();
				if (abortController) {
					abortController.abort();
				}
				set({ abortController: null, isStreaming: false });
			},

			// Model Actions
			setSelectedModel: (model) => set({ selectedModel: model }),

			// System prompt override
			setSystemPromptOverride: (value) => set({ systemPromptOverride: value }),

			// Context Actions
			setContext: (context) => set({ context }),

			// Helpers
			getActiveConversation: () => {
				const { conversations, activeConversationId } = get();
				return conversations.find((c) => c.id === activeConversationId) ?? null;
			},
		}),
		{
			name: "tracertm-chat-store",
			partialize: (state) => ({
				// Persist UI preferences
				mode: state.mode,
				bubblePosition: state.bubblePosition,
				sidebarWidth: state.sidebarWidth,
				// Persist conversations
				conversations: state.conversations,
				activeConversationId: state.activeConversationId,
				// Persist model selection
				selectedModel: state.selectedModel,
				// Persist system prompt override
				systemPromptOverride: state.systemPromptOverride,
				// Don't persist: isOpen, isStreaming, abortController, context
			}),
			storage: createJSONStorage(() => getStorage()),
		},
	),
);
