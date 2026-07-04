/**
 * ChatHistoryPanel - List of past conversations with search, sort, and delete.
 * Borrows ideas from agent/chat history UIs: search, sort (newest/oldest), per-item delete, click to open.
 */

import type { ChangeEvent, MouseEvent } from 'react';

import { History, Search, Trash2, X } from 'lucide-react';
import { useCallback, useMemo, useState } from 'react';

import type { ChatConversation } from '@/lib/ai/types';

import { Button, Input, ScrollArea, cn } from '@tracertm/ui';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';

type SortOption = 'newest' | 'oldest';

interface ConversationAction {
  onDelete: (id: string) => void;
  onSelect: (id: string) => void;
}

const formatDate = (iso: string) => {
  const date = new Date(iso);
  const now = new Date();
  const sameDay =
    date.getDate() === now.getDate() &&
    date.getMonth() === now.getMonth() &&
    date.getFullYear() === now.getFullYear();
  if (sameDay) {
    return date.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
    });
  }
  return date.toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
};

interface ChatHistoryPanelProps {
  conversations: ChatConversation[];
  activeConversationId: string | null;
  projectId?: string | null | undefined;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
  onClose: () => void;
  className?: string | undefined;
}

const HistoryHeader = ({ onClose }: { onClose: () => void }) => (
  <div className='bg-muted/30 flex shrink-0 items-center justify-between border-b px-3 py-2'>
    <div className='flex min-w-0 items-center gap-2'>
      <History className='text-muted-foreground h-4 w-4 shrink-0' />
      <h3 className='min-w-0 truncate text-sm font-semibold'>Chat history</h3>
    </div>
    <Button
      variant='ghost'
      size='icon'
      className='h-7 w-7 shrink-0'
      onClick={onClose}
      title='Back to chat'
    >
      <X className='h-4 w-4' />
    </Button>
  </div>
);

const SearchFilter = ({
  searchQuery,
  onSearchChange,
  sort,
  onSortChange,
  filterByProject,
  onToggleProject,
  projectId,
}: {
  searchQuery: string;
  onSearchChange: (event: ChangeEvent<HTMLInputElement>) => void;
  sort: SortOption;
  onSortChange: (value: SortOption) => void;
  filterByProject: boolean;
  onToggleProject: () => void;
  projectId?: string | null | undefined;
}) => (
  <div className='bg-muted/10 shrink-0 space-y-2 border-b px-2 py-2'>
    <div className='relative'>
      <Search className='text-muted-foreground absolute top-1/2 left-2.5 h-3.5 w-3.5 -translate-y-1/2' />
      <Input
        placeholder='Search by title or content...'
        value={searchQuery}
        onChange={onSearchChange}
        className='h-8 pl-8 text-sm'
      />
    </div>
    <div className='flex items-center gap-2'>
      <Select value={sort} onValueChange={onSortChange}>
        <SelectTrigger className='h-8 min-w-0 flex-1 text-xs'>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='newest'>Newest first</SelectItem>
          <SelectItem value='oldest'>Oldest first</SelectItem>
        </SelectContent>
      </Select>
      {projectId ? (
        <Button
          variant={filterByProject ? 'secondary' : 'ghost'}
          size='sm'
          className='h-8 shrink-0 text-xs'
          onClick={onToggleProject}
        >
          {filterByProject ? 'This project' : 'All'}
        </Button>
      ) : null}
    </div>
  </div>
);

const EmptyState = ({ hasConversations }: { hasConversations: boolean }) => (
  <div className='text-muted-foreground flex flex-col items-center justify-center py-8 text-center text-sm'>
    <History className='mb-2 h-10 w-10 opacity-50' />
    {hasConversations
      ? 'No conversations match your search or filter.'
      : 'No conversations yet. Start a chat to see history here.'}
  </div>
);

const ConversationItem = ({
  conversation,
  activeConversationId,
  actions,
}: {
  conversation: ChatConversation;
  activeConversationId: string | null;
  actions: ConversationAction;
}) => {
  const isActive = conversation.id === activeConversationId;
  const handleSelect = useCallback(() => {
    actions.onSelect(conversation.id);
  }, [actions, conversation.id]);
  const handleDelete = useCallback(
    (event: MouseEvent<HTMLButtonElement>) => {
      event.stopPropagation();
      actions.onDelete(conversation.id);
    },
    [actions, conversation.id],
  );
  return (
    <li>
      <div
        className={cn(
          'group flex items-center gap-2 rounded-md px-2 py-2 transition-colors border',
          isActive ? 'bg-primary/10 border-primary/30' : 'hover:bg-muted/50 border-transparent',
        )}
      >
        <button type='button' className='min-w-0 flex-1 text-left' onClick={handleSelect}>
          <p className='truncate text-sm font-medium'>{conversation.title || 'New Chat'}</p>
          <p className='text-muted-foreground text-xs'>
            {formatDate(conversation.updatedAt)}
            {conversation.messages.length > 0 ? (
              <>
                {' · '}
                {conversation.messages.length} message
                {conversation.messages.length !== 1 ? 's' : ''}
              </>
            ) : null}
          </p>
        </button>
        <Button
          variant='ghost'
          size='icon'
          className='h-7 w-7 shrink-0 opacity-50 group-hover:opacity-100'
          onClick={handleDelete}
          title='Delete conversation'
        >
          <Trash2 className='h-3.5 w-3.5' />
        </Button>
      </div>
    </li>
  );
};

const ConversationList = ({
  conversations,
  activeConversationId,
  actions,
}: {
  conversations: ChatConversation[];
  activeConversationId: string | null;
  actions: ConversationAction;
}) => (
  <ul className='space-y-1'>
    {conversations.map((conversation) => (
      <ConversationItem
        key={conversation.id}
        conversation={conversation}
        activeConversationId={activeConversationId}
        actions={actions}
      />
    ))}
  </ul>
);

export const ChatHistoryPanel = ({
  conversations,
  activeConversationId,
  projectId,
  onSelectConversation,
  onDeleteConversation,
  onClose,
  className,
}: ChatHistoryPanelProps) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sort, setSort] = useState<SortOption>('newest');
  const [filterByProject, setFilterByProject] = useState(false);

  const handleSearchChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  }, []);

  const handleSortChange = useCallback((value: SortOption) => {
    setSort(value);
  }, []);

  const handleToggleProject = useCallback(() => {
    setFilterByProject((prev) => !prev);
  }, []);

  const filteredAndSorted = useMemo(() => {
    let list = [...conversations];

    if (filterByProject && projectId) {
      list = list.filter((conversation) => conversation.projectId === projectId);
    }

    const query = searchQuery.trim().toLowerCase();
    if (query) {
      list = list.filter(
        (conversation) =>
          conversation.title.toLowerCase().includes(query) ||
          conversation.messages.some(
            (message) => message.content && message.content.toLowerCase().includes(query),
          ),
      );
    }

    list.sort((a, b) => {
      const firstTime = new Date(a.updatedAt).getTime();
      const secondTime = new Date(b.updatedAt).getTime();
      return sort === 'newest' ? secondTime - firstTime : firstTime - secondTime;
    });

    return list;
  }, [conversations, searchQuery, sort, filterByProject, projectId]);

  const handleSelectConversation = useCallback(
    (id: string) => {
      onSelectConversation(id);
      onClose();
    },
    [onClose, onSelectConversation],
  );

  const actions = useMemo<ConversationAction>(
    () => ({
      onDelete: onDeleteConversation,
      onSelect: handleSelectConversation,
    }),
    [handleSelectConversation, onDeleteConversation],
  );

  return (
    <div className={cn('flex flex-col bg-background h-full overflow-hidden rounded-lg', className)}>
      <HistoryHeader onClose={onClose} />
      <SearchFilter
        searchQuery={searchQuery}
        onSearchChange={handleSearchChange}
        sort={sort}
        onSortChange={handleSortChange}
        filterByProject={filterByProject}
        onToggleProject={handleToggleProject}
        projectId={projectId}
      />
      <ScrollArea className='min-h-0 flex-1 p-2'>
        {filteredAndSorted.length === 0 ? (
          <EmptyState hasConversations={conversations.length > 0} />
        ) : (
          <ConversationList
            conversations={filteredAndSorted}
            activeConversationId={activeConversationId}
            actions={actions}
          />
        )}
      </ScrollArea>
    </div>
  );
};
