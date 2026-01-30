/**
 * AI Chat Types for TraceRTM
 */

/** Supported AI providers */
export type AIProvider = "claude" | "codex" | "gemini";

/** Model configuration */
export interface AIModel {
	id: string;
	name: string;
	provider: AIProvider;
	description?: string;
	contextWindow?: number;
	maxOutput?: number;
}

/** Provider configuration */
export interface AIProviderConfig {
	id: AIProvider;
	name: string;
	models: AIModel[];
	enabled: boolean;
}

/** Chat message role */
export type ChatRole = "user" | "assistant" | "system";

/** Chat message */
export interface ChatMessage {
	id: string;
	conversationId: string;
	role: ChatRole;
	content: string;
	createdAt: string;
	isStreaming?: boolean;
	toolCalls?: ToolCall[];
	metadata?: Record<string, unknown>;
}

/** Chat conversation */
export interface ChatConversation {
	id: string;
	title: string;
	projectId?: string;
	model: AIModel;
	messages: ChatMessage[];
	createdAt: string;
	updatedAt: string;
}

/** Chat context for system prompt */
export interface ChatContext {
	project?: {
		id: string;
		name: string;
		description?: string;
	};
	currentView?: string;
	selectedItems?: Array<{
		id: string;
		title: string;
		type: string;
		status?: string;
	}>;
	recentActivity?: string[];
}

/** Chat request payload */
export interface ChatRequest {
	messages: Array<{
		role: ChatRole;
		content: string;
	}>;
	model: string;
	provider: AIProvider;
	systemPrompt?: string;
	context?: ChatContext;
}

/** SSE event types from server */
export type SSEEventType =
	| "text"
	| "tool_use_start"
	| "tool_use_input"
	| "tool_result"
	| "error"
	| "done";

/** SSE event from streaming response */
export interface SSEEvent {
	type: SSEEventType;
	data: {
		content?: string;
		tool_name?: string;
		tool_use_id?: string;
		input?: Record<string, unknown>;
		result?: ToolResult;
		error?: string;
	};
}

/** Tool execution result */
export interface ToolResult {
	success: boolean;
	result?: Record<string, unknown>;
	error?: string;
}

/** Tool call in a message */
export interface ToolCall {
	id: string;
	name: string;
	input: Record<string, unknown>;
	result?: ToolResult;
	isExecuting?: boolean;
}

/** Legacy SSE chunk (for backwards compatibility) */
export interface ChatStreamChunk {
	content?: string;
	done?: boolean;
	error?: string;
}

/** Chat store UI state */
export interface ChatUIState {
	isOpen: boolean;
	mode: "bubble" | "sidebar";
	bubblePosition: { x: number; y: number };
	sidebarWidth: number;
}

/** Generate unique ID for messages/conversations */
export function generateId(): string {
	return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}
