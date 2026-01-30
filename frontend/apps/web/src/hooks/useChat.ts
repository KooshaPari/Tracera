/**
 * useChat Hook - SSE streaming for AI chat with tool use support
 */

import { useCallback, useRef } from "react";
import { useChatStore } from "@/stores/chatStore";
import { buildSystemPrompt } from "@/lib/ai/systemPrompt";
import type { SSEEvent, ToolCall } from "@/lib/ai/types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface SendMessageOptions {
	onChunk?: (chunk: string) => void;
	onToolStart?: (toolName: string, toolId: string) => void;
	onToolResult?: (toolId: string, result: unknown) => void;
	onComplete?: (fullContent: string) => void;
	onError?: (error: Error) => void;
}

export function useChat() {
	const {
		isOpen,
		mode,
		isStreaming,
		selectedModel,
		context,
		conversations,
		activeConversationId,
		toggleOpen,
		setOpen,
		setMode,
		createConversation,
		setActiveConversation,
		deleteConversation,
		addMessage,
		updateMessage,
		setMessageStreaming,
		setStreaming,
		setAbortController,
		stopStreaming,
		setSelectedModel,
		setContext,
		getActiveConversation,
	} = useChatStore();

	const accumulatedContent = useRef<string>("");
	const toolCalls = useRef<Map<string, ToolCall>>(new Map());

	const sendMessage = useCallback(
		async (content: string, options?: SendMessageOptions) => {
			// Get or create conversation
			let conversationId = activeConversationId;
			if (!conversationId) {
				conversationId = createConversation(context?.project?.id);
			}

			// Add user message
			addMessage(conversationId, "user", content);

			// Add placeholder assistant message
			const assistantMessageId = addMessage(conversationId, "assistant", "");

			// Build messages for API
			const conversation = getActiveConversation();
			if (!conversation) {
				options?.onError?.(new Error("No active conversation"));
				return;
			}

			const messagesForApi = conversation.messages
				.filter((m) => m.id !== assistantMessageId)
				.map((m) => ({
					role: m.role,
					content: m.content,
				}));

			// Add the new user message
			messagesForApi.push({ role: "user", content });

			// Build system prompt with context
			const systemPrompt = buildSystemPrompt(context ?? undefined);

			// Create abort controller
			const abortController = new AbortController();
			setAbortController(abortController);
			setStreaming(true);
			accumulatedContent.current = "";
			toolCalls.current = new Map();

			try {
				const response = await fetch(`${API_URL}/api/v1/chat/stream`, {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						messages: messagesForApi,
						model: selectedModel.id,
						provider: selectedModel.provider,
						system_prompt: systemPrompt,
						max_tokens: selectedModel.maxOutput || 4096,
						context: context
							? {
									project_id: context.project?.id,
									project_name: context.project?.name,
									current_view: context.currentView,
								}
							: undefined,
					}),
					signal: abortController.signal,
				});

				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`);
				}

				const reader = response.body?.getReader();
				if (!reader) {
					throw new Error("No response body");
				}

				const decoder = new TextDecoder();
				let buffer = "";

				while (true) {
					const { done, value } = await reader.read();

					if (done) {
						break;
					}

					buffer += decoder.decode(value, { stream: true });

					// Process SSE events in buffer
					const lines = buffer.split("\n");
					buffer = lines.pop() || ""; // Keep incomplete line in buffer

					for (const line of lines) {
						if (line.startsWith("data: ")) {
							const data = line.slice(6).trim();

							if (data === "[DONE]") {
								// Legacy done signal
								setMessageStreaming(conversationId, assistantMessageId, false);
								options?.onComplete?.(accumulatedContent.current);
								continue;
							}

							try {
								const event: SSEEvent = JSON.parse(data);

								switch (event.type) {
									case "text":
										if (event.data.content) {
											accumulatedContent.current += event.data.content;
											updateMessage(
												conversationId,
												assistantMessageId,
												formatMessageContent(
													accumulatedContent.current,
													toolCalls.current,
												),
											);
											options?.onChunk?.(event.data.content);
										}
										break;

									case "tool_use_start":
										if (event.data.tool_name && event.data.tool_use_id) {
											const toolCall: ToolCall = {
												id: event.data.tool_use_id,
												name: event.data.tool_name,
												input: {},
												isExecuting: true,
											};
											toolCalls.current.set(event.data.tool_use_id, toolCall);
											updateMessage(
												conversationId,
												assistantMessageId,
												formatMessageContent(
													accumulatedContent.current,
													toolCalls.current,
												),
											);
											options?.onToolStart?.(
												event.data.tool_name,
												event.data.tool_use_id,
											);
										}
										break;

									case "tool_use_input":
										if (event.data.tool_use_id && event.data.input) {
											const existingCall = toolCalls.current.get(
												event.data.tool_use_id,
											);
											if (existingCall) {
												existingCall.input = event.data.input;
												toolCalls.current.set(
													event.data.tool_use_id,
													existingCall,
												);
												updateMessage(
													conversationId,
													assistantMessageId,
													formatMessageContent(
														accumulatedContent.current,
														toolCalls.current,
													),
												);
											}
										}
										break;

									case "tool_result":
										if (event.data.tool_use_id && event.data.result) {
											const existingCall = toolCalls.current.get(
												event.data.tool_use_id,
											);
											if (existingCall) {
												existingCall.result = event.data.result;
												existingCall.isExecuting = false;
												toolCalls.current.set(
													event.data.tool_use_id,
													existingCall,
												);
												updateMessage(
													conversationId,
													assistantMessageId,
													formatMessageContent(
														accumulatedContent.current,
														toolCalls.current,
													),
												);
												options?.onToolResult?.(
													event.data.tool_use_id,
													event.data.result,
												);
											}
										}
										break;

									case "error":
										if (event.data.error) {
											throw new Error(event.data.error);
										}
										break;

									case "done":
										setMessageStreaming(
											conversationId,
											assistantMessageId,
											false,
										);
										options?.onComplete?.(accumulatedContent.current);
										break;
								}
							} catch (parseError) {
								// Try legacy format
								try {
									const legacyData = JSON.parse(data);
									if (legacyData.content) {
										accumulatedContent.current += legacyData.content;
										updateMessage(
											conversationId,
											assistantMessageId,
											accumulatedContent.current,
										);
										options?.onChunk?.(legacyData.content);
									}
								} catch {
									console.warn("Failed to parse SSE chunk:", data);
								}
							}
						}
					}
				}

				// Ensure streaming state is cleaned up
				setMessageStreaming(conversationId, assistantMessageId, false);
			} catch (error) {
				if ((error as Error).name === "AbortError") {
					// Request was aborted, mark as complete
					setMessageStreaming(conversationId, assistantMessageId, false);
					if (accumulatedContent.current) {
						updateMessage(
							conversationId,
							assistantMessageId,
							accumulatedContent.current + "\n\n*[Response stopped]*",
						);
					}
				} else {
					// Actual error
					setMessageStreaming(conversationId, assistantMessageId, false);
					updateMessage(
						conversationId,
						assistantMessageId,
						`Error: ${(error as Error).message}`,
					);
					options?.onError?.(error as Error);
				}
			} finally {
				setStreaming(false);
				setAbortController(null);
			}
		},
		[
			activeConversationId,
			context,
			selectedModel,
			createConversation,
			addMessage,
			updateMessage,
			setMessageStreaming,
			setStreaming,
			setAbortController,
			getActiveConversation,
		],
	);

	const regenerateLastMessage = useCallback(async () => {
		const conversation = getActiveConversation();
		if (!conversation || conversation.messages.length < 2) {
			return;
		}

		// Find last user message (search from end)
		const messages = conversation.messages;
		let lastUserMessage: (typeof messages)[number] | undefined;
		for (let i = messages.length - 1; i >= 0; i--) {
			const msg = messages[i];
			if (msg && msg.role === "user") {
				lastUserMessage = msg;
				break;
			}
		}
		if (!lastUserMessage) {
			return;
		}

		// Delete messages after last user message
		// For simplicity, we'll just send the same message again
		// The new assistant response will be appended
		await sendMessage(lastUserMessage.content);
	}, [getActiveConversation, sendMessage]);

	return {
		// State
		isOpen,
		mode,
		isStreaming,
		selectedModel,
		context,
		conversations,
		activeConversationId,
		activeConversation: getActiveConversation(),

		// UI Actions
		toggleOpen,
		setOpen,
		setMode,

		// Conversation Actions
		createConversation,
		setActiveConversation,
		deleteConversation,

		// Model Actions
		setSelectedModel,

		// Context Actions
		setContext,

		// Chat Actions
		sendMessage,
		stopStreaming,
		regenerateLastMessage,
	};
}

/**
 * Format message content with tool calls
 */
function formatMessageContent(
	textContent: string,
	toolCalls: Map<string, ToolCall>,
): string {
	if (toolCalls.size === 0) {
		return textContent;
	}

	const parts: string[] = [];

	if (textContent) {
		parts.push(textContent);
	}

	for (const [, toolCall] of toolCalls) {
		parts.push("");
		parts.push(`---`);
		parts.push(
			`**Tool: ${toolCall.name}** ${toolCall.isExecuting ? "(executing...)" : ""}`,
		);

		if (Object.keys(toolCall.input).length > 0) {
			parts.push("```json");
			parts.push(JSON.stringify(toolCall.input, null, 2));
			parts.push("```");
		}

		if (toolCall.result) {
			if (toolCall.result.success) {
				parts.push("**Result:**");
				parts.push("```json");
				parts.push(JSON.stringify(toolCall.result.result, null, 2));
				parts.push("```");
			} else {
				parts.push(`**Error:** ${toolCall.result.error}`);
			}
		}
	}

	return parts.join("\n");
}
