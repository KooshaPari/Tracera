/**
 * UseChat Hook - SSE streaming for AI chat with tool use support
 */

import { useCallback, useRef } from 'react';

import type { SSEEvent, ToolCall } from '@/lib/ai/types';

import { createAgentSession } from '@/api/agent';
import { client } from '@/api/client';
import { buildSystemPrompt } from '@/lib/ai/systemPrompt';
import { logger } from '@/lib/logger';
import { useChatStore } from '@/stores/chat-store';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

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
    systemPromptOverride,
    conversations,
    activeConversationId,
    toggleOpen,
    setOpen,
    setMode,
    createConversation,
    setActiveConversation,
    setConversationSessionId,
    deleteConversation,
    addMessage,
    updateMessage,
    updateMessageToolCalls,
    setMessageStreaming,
    setStreaming,
    setAbortController,
    stopStreaming,
    setSelectedModel,
    setSystemPromptOverride,
    setContext,
    getActiveConversation,
  } = useChatStore();

  const accumulatedContent = useRef<string>('');
  const toolCalls = useRef<Map<string, ToolCall>>(new Map());

  const sendMessage = useCallback(
    async (content: string, options?: SendMessageOptions) => {
      // Get or create conversation
      let conversationId = activeConversationId;
      conversationId ??= createConversation(context?.project?.id);

      // Ensure agent session for this conversation (per-session sandbox)
      let conversation = getActiveConversation();
      if (!conversation?.sessionId && context?.project?.id) {
        try {
          const session = await createAgentSession({
            project_id: context.project.id,
            session_id: conversationId,
          });
          setConversationSessionId(conversationId, session.session_id);
          conversation = { ...conversation!, sessionId: session.session_id };
        } catch {
          // Proceed without session_id; backend will run without sandbox
        }
      }
      // Re-fetch in case we just set sessionId
      conversation = getActiveConversation();

      // Add user message
      addMessage(conversationId, 'user', content);

      // Add placeholder assistant message
      const assistantMessageId = addMessage(conversationId, 'assistant', '');

      // Build messages for API (conversation already resolved above)
      const conv = getActiveConversation();
      if (!conv) {
        options?.onError?.(new Error('No active conversation'));
        return;
      }

      const messagesForApi = conv.messages
        .filter((msg: { id: string }) => msg.id !== assistantMessageId)
        .map((msg: { content: string; role: string }) => ({
          content: msg.content,
          role: msg.role,
        }));

      // Add the new user message
      messagesForApi.push({ content, role: 'user' });

      // Build system prompt: override if set, else built-in with context
      const systemPrompt =
        (systemPromptOverride?.trim() && systemPromptOverride) ??
        buildSystemPrompt(context ?? undefined);

      // Create abort controller
      const abortController = new AbortController();
      setAbortController(abortController);
      setStreaming(true);
      accumulatedContent.current = '';
      toolCalls.current = new Map();

      try {
        const response = await fetch(`${API_URL}/api/v1/chat/stream`, {
          body: JSON.stringify({
            context: context
              ? {
                  current_view: context.currentView,
                  project_id: context.project?.id,
                  project_name: context.project?.name,
                }
              : undefined,
            max_tokens: selectedModel.maxOutput ?? 4096,
            messages: messagesForApi,
            model: selectedModel.id,
            provider: selectedModel.provider,
            session_id: conv.sessionId ?? undefined,
            system_prompt: systemPrompt,
          }),
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders(),
          },
          method: 'POST',
          signal: abortController.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response['body']?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        const processSSELine = (line: string) => {
          if (!line.startsWith('data: ')) {
            return;
          }
          const data = line.slice(6).trim();
          if (data === '[DONE]') {
            updateMessageToolCalls(conversationId, assistantMessageId, [
              ...toolCalls.current.values(),
            ]);
            setMessageStreaming(conversationId, assistantMessageId, false);
            options?.onComplete?.(accumulatedContent.current);
            return;
          }
          try {
            const event: SSEEvent = JSON.parse(data);
            switch (event.type) {
              case 'text': {
                if (event.data['content']) {
                  accumulatedContent.current += event.data['content'];
                  updateMessage(
                    conversationId,
                    assistantMessageId,
                    formatMessageContent(accumulatedContent.current, toolCalls.current),
                  );
                  options?.onChunk?.(event.data['content']);
                }
                break;
              }
              case 'tool_use_start': {
                if (event.data['tool_name'] && event.data['tool_use_id']) {
                  const toolCall: ToolCall = {
                    id: event.data['tool_use_id'],
                    input: {},
                    isExecuting: true,
                    name: event.data['tool_name'],
                  };
                  toolCalls.current.set(event.data['tool_use_id'], toolCall);
                  updateMessage(
                    conversationId,
                    assistantMessageId,
                    formatMessageContent(accumulatedContent.current, toolCalls.current),
                  );
                  updateMessageToolCalls(conversationId, assistantMessageId, [
                    ...toolCalls.current.values(),
                  ]);
                  options?.onToolStart?.(event.data['tool_name'], event.data['tool_use_id']);
                }
                break;
              }
              case 'tool_use_input': {
                if (event.data['tool_use_id'] && event.data['input']) {
                  const existingCall = toolCalls.current.get(event.data['tool_use_id']);
                  if (existingCall) {
                    existingCall.input = event.data['input'];
                    toolCalls.current.set(event.data['tool_use_id'], existingCall);
                    updateMessage(
                      conversationId,
                      assistantMessageId,
                      formatMessageContent(accumulatedContent.current, toolCalls.current),
                    );
                    updateMessageToolCalls(conversationId, assistantMessageId, [
                      ...toolCalls.current.values(),
                    ]);
                  }
                }
                break;
              }
              case 'tool_result': {
                if (event.data['tool_use_id'] && event.data['result']) {
                  const existingCall = toolCalls.current.get(event.data['tool_use_id']);
                  if (existingCall) {
                    existingCall.result = event.data['result'];
                    existingCall.isExecuting = false;
                    toolCalls.current.set(event.data['tool_use_id'], existingCall);
                    updateMessage(
                      conversationId,
                      assistantMessageId,
                      formatMessageContent(accumulatedContent.current, toolCalls.current),
                    );
                    updateMessageToolCalls(conversationId, assistantMessageId, [
                      ...toolCalls.current.values(),
                    ]);
                    options?.onToolResult?.(event.data['tool_use_id'], event.data['result']);
                  }
                }
                break;
              }
              case 'error': {
                if (event.data['error']) {
                  throw new Error(event.data['error']);
                }
                break;
              }
              case 'done': {
                updateMessageToolCalls(conversationId, assistantMessageId, [
                  ...toolCalls.current.values(),
                ]);
                setMessageStreaming(conversationId, assistantMessageId, false);
                options?.onComplete?.(accumulatedContent.current);
                break;
              }
            }
          } catch {
            try {
              const legacyData = JSON.parse(data);
              if (legacyData.content) {
                accumulatedContent.current += legacyData.content;
                updateMessage(conversationId, assistantMessageId, accumulatedContent.current);
                options?.onChunk?.(legacyData.content);
              }
            } catch {
              logger.warn('Failed to parse SSE chunk:', data);
            }
          }
        };

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            // Process any remaining buffer (last SSE event may be in here)
            const lines = buffer.split('\n');
            for (const line of lines) {
              if (line.trim()) {
                processSSELine(line);
              }
            }
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() ?? '';

          for (const line of lines) {
            if (line.trim()) {
              processSSELine(line);
            }
          }
        }

        // Ensure streaming state is cleaned up and tool calls persisted
        updateMessageToolCalls(conversationId, assistantMessageId, [...toolCalls.current.values()]);
        setMessageStreaming(conversationId, assistantMessageId, false);
        // If we never got any content, show a fallback so the user knows the request finished
        if (!accumulatedContent.current) {
          updateMessage(
            conversationId,
            assistantMessageId,
            'No response received. Check that the AI provider is configured (e.g. ANTHROPIC_API_KEY for Claude) and try again.',
          );
        }
      } catch (error) {
        updateMessageToolCalls(conversationId, assistantMessageId, [...toolCalls.current.values()]);
        if ((error as Error).name === 'AbortError') {
          // Request was aborted, mark as complete
          setMessageStreaming(conversationId, assistantMessageId, false);
          if (accumulatedContent.current) {
            updateMessage(
              conversationId,
              assistantMessageId,
              `${accumulatedContent.current}\n\n*[Response stopped]*`,
            );
          }
        } else {
          // Actual error
          setMessageStreaming(conversationId, assistantMessageId, false);
          updateMessage(conversationId, assistantMessageId, `Error: ${(error as Error).message}`);
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
      systemPromptOverride,
      createConversation,
      setConversationSessionId,
      addMessage,
      updateMessage,
      updateMessageToolCalls,
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
    const { messages } = conversation;
    let lastUserMessage: (typeof messages)[number] | undefined;
    for (let i = messages.length - 1; i >= 0; i -= 1) {
      const msg = messages[i];
      if (msg?.role === 'user') {
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
    systemPromptOverride,
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

    // System prompt
    setSystemPromptOverride,

    // Chat Actions
    sendMessage,
    stopStreaming,
    regenerateLastMessage,
  };
}

/**
 * Format message content with tool calls
 */
function formatMessageContent(textContent: string, toolCalls: Map<string, ToolCall>): string {
  if (toolCalls.size === 0) {
    return textContent;
  }

  const parts: string[] = [];

  if (textContent) {
    parts.push(textContent);
  }

  for (const [, toolCall] of toolCalls) {
    parts.push('');
    parts.push(`---`);
    parts.push(`**Tool: ${toolCall.name}** ${toolCall.isExecuting ? '(executing...)' : ''}`);

    if (Object.keys(toolCall.input).length > 0) {
      parts.push('```json');
      parts.push(JSON.stringify(toolCall.input, null, 2));
      parts.push('```');
    }

    if (toolCall.result) {
      if (toolCall.result['success']) {
        parts.push('**Result:**');
        parts.push('```json');
        parts.push(JSON.stringify(toolCall.result['result'], null, 2));
        parts.push('```');
      } else {
        parts.push(`**Error:** ${toolCall.result['error']}`);
      }
    }
  }

  return parts.join('\n');
}
