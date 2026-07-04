/**
 * ChatPanel - Main chat interface with header, messages, and input.
 * Includes a Chat history button that opens a history panel (search, sort, delete).
 */

import type { ChangeEvent, KeyboardEvent, MouseEvent, RefObject } from 'react';

import { History, MessageSquarePlus, Send, Settings, Square, X } from 'lucide-react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import type { AIModel, ChatConversation, ChatMessage as ChatMessageType } from '@/lib/ai/types';

import { useChat } from '@/hooks/useChat';
import { logger } from '@/lib/logger';
import { Button, ScrollArea, Textarea, cn } from '@tracertm/ui';

import { ChatHistoryPanel } from './ChatHistoryPanel';
import { ChatMessage } from './ChatMessage';
import { ChatSettingsPanel } from './ChatSettingsPanel';
import { ModelSelector } from './ModelSelector';

const MAX_CONVERSATION_TABS = 5;

interface ChatPanelProps {
  onClose: () => void;
  onToggleMode: () => void;
  mode: 'bubble' | 'sidebar';
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
  <div className='bg-muted/30 flex min-w-0 shrink-0 items-center justify-between border-b px-3 py-2'>
    <div className='flex min-w-0 flex-1 items-center gap-2'>
      <h3 className='min-w-0 truncate text-sm font-semibold'>TraceRTM Assistant</h3>
      <ModelSelector value={model} onChange={onSelectModel} disabled={isStreaming} />
    </div>
    <div className='flex shrink-0 items-center gap-1'>
      <Button
        variant='ghost'
        size='icon'
        className='h-7 w-7'
        onClick={onOpenHistory}
        title='Chat history'
      >
        <History className='h-4 w-4' />
      </Button>
      <Button
        variant='ghost'
        size='icon'
        className='h-7 w-7'
        onClick={onOpenSettings}
        title='Chat settings & system prompt'
      >
        <Settings className='h-4 w-4' />
      </Button>
      <Button variant='ghost' size='icon' className='h-7 w-7' onClick={onNewChat} title='New chat'>
        <MessageSquarePlus className='h-4 w-4' />
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
      type='button'
      onClick={handleSelect}
      className={cn(
        'flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-colors cursor-pointer shrink-0 min-w-0',
        'hover:bg-muted',
        isActive ? 'bg-muted font-medium' : 'text-muted-foreground',
      )}
    >
      <span className='max-w-[120px] min-w-0 truncate'>{conversation.title}</span>
      <button
        type='button'
        onClick={handleDelete}
        className='hover:bg-muted/50 cursor-pointer rounded p-0.5 opacity-50 transition-all hover:opacity-100'
      >
        <X className='h-3 w-3' />
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
    <div className='bg-muted/20 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent flex min-w-0 shrink-0 items-center gap-1 overflow-x-auto border-b px-2 py-1.5'>
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
  <div className='flex h-full w-full min-w-0 flex-col items-center justify-center py-8 text-center'>
    <div className='bg-primary/10 mb-3 flex h-12 w-12 shrink-0 items-center justify-center rounded-full'>
      <MessageSquarePlus className='text-primary h-6 w-6' />
    </div>
    <h4 className='mb-1 min-w-0 font-medium'>Welcome to TraceRTM Assistant</h4>
    <p className='text-muted-foreground w-full max-w-[250px] min-w-0 px-4 text-sm'>
      Ask questions about requirements traceability, project management, or get help navigating
      TraceRTM.
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
  const lastMessageId = messages.length > 0 ? messages.at(-1)?.id : null;

  return (
    <div className='w-full min-w-0 space-y-2'>
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} isLast={message.id === lastMessageId} />
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
  <div className='bg-muted/20 min-w-0 shrink-0 border-t p-3'>
    <div className='flex min-w-0 gap-2'>
      <Textarea
        ref={textareaRef}
        value={inputValue}
        onChange={onChange}
        onKeyDown={onKeyDown}
        placeholder='Ask a question...'
        className='max-h-[120px] min-h-[40px] min-w-0 flex-1 resize-none text-sm'
        disabled={disabled}
        rows={1}
      />
      {disabled ? (
        <Button size='icon' variant='destructive' onClick={onStop} title='Stop generating'>
          <Square className='h-4 w-4' />
        </Button>
      ) : (
        <Button size='icon' onClick={onSend} disabled={!inputValue.trim()} title='Send message'>
          <Send className='h-4 w-4' />
        </Button>
      )}
    </div>
    <div className='text-muted-foreground mt-1.5 min-w-0 truncate text-center text-[10px]'>
      Press Enter to send, Shift+Enter for new line
    </div>
  </div>
);

const useAutoScroll = (ref: RefObject<HTMLDivElement | null>, key: number) => {
  useEffect(() => {
    ref.current?.scrollIntoView({ behavior: 'smooth' });
  }, [key, ref]);
};

const useBubbleFocus = (mode: 'bubble' | 'sidebar', ref: RefObject<HTMLTextAreaElement | null>) => {
  useEffect(() => {
    if (mode !== 'bubble') {
      return;
    }
    if (typeof document !== 'undefined' && document.activeElement !== document.body) {
      return;
    }
    ref.current?.focus();
  }, [mode, ref]);
};

const useChatPanelState = (mode: 'bubble' | 'sidebar') => {
  const chat = useChat();
  const [inputValue, setInputValue] = useState('');
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
      <div className='flex min-h-0 flex-1 flex-col overflow-hidden'>
        <ChatSettingsPanel
          context={chat.context ?? null}
          systemPromptOverride={chat.systemPromptOverride}
          onSystemPromptOverrideChange={chat.setSystemPromptOverride}
          onClose={onCloseSettings}
          className='min-h-0 flex-1'
        />
      </div>
    );
  }

  if (isHistoryOpen) {
    return (
      <div className='flex min-h-0 flex-1 flex-col overflow-hidden'>
        <ChatHistoryPanel
          conversations={chat.conversations}
          activeConversationId={chat.activeConversation?.id ?? null}
          projectId={chat.context?.project?.id ?? null}
          onSelectConversation={onSelectConversation}
          onDeleteConversation={chat.deleteConversation}
          onClose={onCloseHistory}
          className='min-h-0 flex-1'
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

      <ScrollArea className='min-w-0 flex-1 overflow-hidden p-2'>
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

    setInputValue('');
    chat.sendMessage(content).catch((error) => {
      logger.error('Failed to send chat message:', error);
    });
  }, [chat, inputValue, setInputValue]);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLTextAreaElement>) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSend();
      }
    },
    [handleSend],
  );

  const handleNewChat = useCallback(() => {
    chat.createConversation();
    setInputValue('');
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
        'flex flex-col bg-background border rounded-lg shadow-xl overflow-hidden',
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
