/**
 * Chat Store - Zustand state management for AI chat assistant
 */

import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

import type {
  AIModel,
  ChatContext,
  ChatConversation,
  ChatMessage,
  ChatUIState,
  ToolCall,
} from '@/lib/ai/types';

import { getDefaultModel } from '@/lib/ai/modelRegistry';
import { generateId } from '@/lib/ai/types';

const DEFAULT_BUBBLE_POSITION = { x: -1, y: -1 };
const DEFAULT_SIDEBAR_WIDTH = Number('400');
const SIDEBAR_MIN_WIDTH = Number('300');
const SIDEBAR_MAX_WIDTH = Number('800');
const TITLE_MAX_LENGTH = Number('50');

// SSR-safe storage
const noopStorage = {
  getItem: (_key: string) => null,
  removeItem: (_key: string) => {},
  setItem: (_key: string, _value: string) => {},
};

const getStorage = () => {
  if (
    typeof globalThis.window === 'undefined' ||
    typeof localStorage === 'undefined' ||
    typeof localStorage.getItem !== 'function'
  ) {
    return noopStorage;
  }
  return localStorage;
};

interface ChatState extends ChatUIState {
  // Conversations
  activeConversationId: string | null;
  conversations: ChatConversation[];

  // Streaming state
  abortController: AbortController | null;
  isStreaming: boolean;

  // Model selection
  selectedModel: AIModel;

  // System prompt override (optional custom prompt; empty = use built-in)
  systemPromptOverride: string | null;

  // Context
  context: ChatContext | null;

  // UI Actions
  setBubblePosition: (position: { x: number; y: number }) => void;
  setMode: (mode: 'bubble' | 'sidebar') => void;
  setOpen: (open: boolean) => void;
  setSidebarWidth: (width: number) => void;
  toggleOpen: () => void;

  // Conversation Actions
  addMessage: (conversationId: string, role: 'user' | 'assistant', content: string) => string;
  clearConversations: () => void;
  createConversation: (projectId?: string) => string;
  deleteConversation: (id: string) => void;
  getActiveConversation: () => ChatConversation | null;
  setActiveConversation: (id: string | null) => void;
  setConversationSessionId: (conversationId: string, sessionId: string | null) => void;
  updateConversationTitle: (id: string, title: string) => void;

  // Message Actions
  setMessageStreaming: (conversationId: string, messageId: string, isStreaming: boolean) => void;
  updateMessage: (conversationId: string, messageId: string, content: string) => void;
  updateMessageToolCalls: (
    conversationId: string,
    messageId: string,
    toolCalls: ToolCall[],
  ) => void;

  // Streaming Actions
  setAbortController: (controller: AbortController | null) => void;
  setStreaming: (streaming: boolean) => void;
  stopStreaming: () => void;

  // Model Actions
  setSelectedModel: (model: AIModel) => void;

  // System prompt override
  setSystemPromptOverride: (value: string | null) => void;

  // Context Actions
  setContext: (context: ChatContext | null) => void;
}

type StoreSetter = (
  partial: Partial<ChatState> | ((state: ChatState) => Partial<ChatState> | ChatState),
) => void;

type StoreGetter = () => ChatState;

const createInitialState = (): ChatUIState & {
  activeConversationId: string | null;
  conversations: ChatConversation[];
  abortController: AbortController | null;
  isStreaming: boolean;
  selectedModel: AIModel;
  systemPromptOverride: string | null;
  context: ChatContext | null;
} => ({
  abortController: null,
  activeConversationId: null,
  bubblePosition: DEFAULT_BUBBLE_POSITION,
  context: null,
  conversations: [],
  isOpen: false,
  isStreaming: false,
  mode: 'bubble',
  selectedModel: getDefaultModel(),
  sidebarWidth: DEFAULT_SIDEBAR_WIDTH,
  systemPromptOverride: null,
});

const clampSidebarWidth = (width: number): number =>
  Math.max(SIDEBAR_MIN_WIDTH, Math.min(SIDEBAR_MAX_WIDTH, width));

const updateConversationList = (
  conversations: ChatConversation[],
  conversationId: string,
  updater: (conversation: ChatConversation) => ChatConversation,
): ChatConversation[] => {
  const updated: ChatConversation[] = [];
  for (const conversation of conversations) {
    if (conversation.id === conversationId) {
      updated.push(updater(conversation));
    } else {
      updated.push(conversation);
    }
  }
  return updated;
};

const updateMessagesById = (
  messages: ChatMessage[],
  messageId: string,
  update: Partial<ChatMessage>,
): ChatMessage[] => {
  const updated: ChatMessage[] = [];
  for (const message of messages) {
    if (message.id === messageId) {
      updated.push({ ...message, ...update });
    } else {
      updated.push(message);
    }
  }
  return updated;
};

const updateConversationMessage = (
  conversations: ChatConversation[],
  conversationId: string,
  messageId: string,
  messageUpdate: Partial<ChatMessage>,
  conversationUpdate?: Partial<ChatConversation>,
): ChatConversation[] => {
  const updated: ChatConversation[] = [];
  for (const conversation of conversations) {
    if (conversation.id !== conversationId) {
      updated.push(conversation);
      continue;
    }

    const nextMessages = updateMessagesById(conversation.messages, messageId, messageUpdate);
    const nextConversation = {
      ...conversation,
      ...conversationUpdate,
      messages: nextMessages,
    };

    updated.push(nextConversation);
  }
  return updated;
};

const buildTitleFromMessage = (content: string): string =>
  content.length > TITLE_MAX_LENGTH ? `${content.slice(0, TITLE_MAX_LENGTH)}...` : content;

const createUIActions = (
  set: StoreSetter,
): Pick<
  ChatState,
  'setBubblePosition' | 'setMode' | 'setOpen' | 'setSidebarWidth' | 'toggleOpen'
> => ({
  setBubblePosition: (position) => {
    set({ bubblePosition: position });
  },
  setMode: (mode) => {
    set({ mode });
  },
  setOpen: (open) => {
    set({ isOpen: open });
  },
  setSidebarWidth: (width) => {
    set({ sidebarWidth: clampSidebarWidth(width) });
  },
  toggleOpen: () => {
    set((state) => ({ isOpen: !state.isOpen }));
  },
});

const createConversationLifecycleActions = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<ChatState, 'clearConversations' | 'createConversation' | 'deleteConversation'> => ({
  clearConversations: () => {
    set({
      activeConversationId: null,
      conversations: [],
    });
  },
  createConversation: (projectId) => {
    const id = generateId();
    const now = new Date().toISOString();
    const conversation: ChatConversation = {
      createdAt: now,
      id,
      messages: [],
      model: get().selectedModel,
      ...(projectId ? { projectId } : {}),
      title: 'New Chat',
      updatedAt: now,
    };
    set((state) => ({
      activeConversationId: id,
      conversations: [conversation, ...state.conversations],
    }));
    return id;
  },
  deleteConversation: (id) => {
    set((state) => {
      const filtered = state.conversations.filter((conversation) => conversation.id !== id);
      const newActiveId =
        state.activeConversationId === id ? (filtered[0]?.id ?? null) : state.activeConversationId;
      return {
        activeConversationId: newActiveId,
        conversations: filtered,
      };
    });
  },
});

const createConversationSelectionActions = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<
  ChatState,
  | 'getActiveConversation'
  | 'setActiveConversation'
  | 'setConversationSessionId'
  | 'updateConversationTitle'
> => ({
  getActiveConversation: () => {
    const { activeConversationId, conversations } = get();
    return conversations.find((conversation) => conversation.id === activeConversationId) ?? null;
  },
  setActiveConversation: (id) => {
    set({ activeConversationId: id });
  },
  setConversationSessionId: (conversationId, sessionId) => {
    set((state) => ({
      conversations: updateConversationList(
        state.conversations,
        conversationId,
        (conversation) => ({ ...conversation, sessionId }),
      ),
    }));
  },
  updateConversationTitle: (id, title) => {
    set((state) => ({
      conversations: updateConversationList(state.conversations, id, (conversation) => ({
        ...conversation,
        title,
        updatedAt: new Date().toISOString(),
      })),
    }));
  },
});

const createMessageActions = (
  set: StoreSetter,
): Pick<
  ChatState,
  'addMessage' | 'setMessageStreaming' | 'updateMessage' | 'updateMessageToolCalls'
> => ({
  addMessage: (conversationId, role, content) => {
    const messageId = generateId();
    const now = new Date().toISOString();
    const message: ChatMessage = {
      content,
      conversationId,
      createdAt: now,
      id: messageId,
      isStreaming: role === 'assistant',
      role,
    };

    set((state) => ({
      conversations: updateConversationList(state.conversations, conversationId, (conversation) => {
        const shouldSetTitle = role === 'user' && conversation.messages.length === 0;
        const nextTitle = shouldSetTitle ? buildTitleFromMessage(content) : conversation.title;
        return {
          ...conversation,
          messages: [...conversation.messages, message],
          title: nextTitle,
          updatedAt: now,
        };
      }),
    }));

    return messageId;
  },
  setMessageStreaming: (conversationId, messageId, isStreaming) => {
    set((state) => ({
      conversations: updateConversationMessage(state.conversations, conversationId, messageId, {
        isStreaming,
      }),
    }));
  },
  updateMessage: (conversationId, messageId, content) => {
    set((state) => ({
      conversations: updateConversationMessage(
        state.conversations,
        conversationId,
        messageId,
        { content },
        { updatedAt: new Date().toISOString() },
      ),
    }));
  },
  updateMessageToolCalls: (conversationId, messageId, toolCalls) => {
    set((state) => ({
      conversations: updateConversationMessage(
        state.conversations,
        conversationId,
        messageId,
        { toolCalls },
        { updatedAt: new Date().toISOString() },
      ),
    }));
  },
});

const createStreamingActions = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<ChatState, 'setAbortController' | 'setStreaming' | 'stopStreaming'> => ({
  setAbortController: (controller) => {
    set({ abortController: controller });
  },
  setStreaming: (streaming) => {
    set({ isStreaming: streaming });
  },
  stopStreaming: () => {
    const { abortController } = get();
    if (abortController) {
      abortController.abort();
    }
    set({ abortController: null, isStreaming: false });
  },
});

const createModelActions = (
  set: StoreSetter,
): Pick<ChatState, 'setSelectedModel' | 'setSystemPromptOverride'> => ({
  setSelectedModel: (model) => {
    set({ selectedModel: model });
  },
  setSystemPromptOverride: (value) => {
    set({ systemPromptOverride: value });
  },
});

const createContextActions = (set: StoreSetter): Pick<ChatState, 'setContext'> => ({
  setContext: (context) => {
    set({ context });
  },
});

const buildChatStore = (set: StoreSetter, get: StoreGetter): ChatState => ({
  ...createInitialState(),
  ...createUIActions(set),
  ...createConversationLifecycleActions(set, get),
  ...createConversationSelectionActions(set, get),
  ...createMessageActions(set),
  ...createStreamingActions(set, get),
  ...createModelActions(set),
  ...createContextActions(set),
});

export const useChatStore = create<ChatState>()(
  persist<ChatState>((set, get) => buildChatStore(set, get), {
    name: 'tracertm-chat-store',
    partialize: (state: ChatState) =>
      ({
        activeConversationId: state.activeConversationId,
        bubblePosition: state.bubblePosition,
        conversations: state.conversations,
        mode: state.mode,
        selectedModel: state.selectedModel,
        sidebarWidth: state.sidebarWidth,
        systemPromptOverride: state.systemPromptOverride,
      }) as unknown as ChatState,
    storage: createJSONStorage(() => getStorage()),
  }),
);
