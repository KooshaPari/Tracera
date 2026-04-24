/**
 * ChatMessage - Individual chat message component.
 * Shows text content and, for assistant messages, a collapsible "Tools used (MCP)" section when tool calls are present.
 */

import { Bot, ChevronDown, ChevronRight, Loader2, User, Wrench } from 'lucide-react';
import { useState } from 'react';

import type { ChatMessage as ChatMessageType, ToolCall } from '@/lib/ai/types';

import { cn } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@tracertm/ui/components/Collapsible';

const HOURS_PER_DAY = 24;
const MINUTES_PER_HOUR = 60;
const MILLIS_PER_MINUTE = 60_000;

interface ChatMessageProps {
  message: ChatMessageType;
  isLast?: boolean;
}

const resolveToolStatus = (toolCall: ToolCall): 'running' | 'ok' | 'error' | '—' => {
  if (toolCall.isExecuting) {
    return 'running';
  }
  if (!toolCall.result) {
    return '—';
  }
  return toolCall.result.success ? 'ok' : 'error';
};

const resolveBadgeVariant = (
  status: 'running' | 'ok' | 'error' | '—',
): 'secondary' | 'outline' | 'destructive' =>
  status === 'error' ? 'destructive' : status === 'running' ? 'secondary' : 'outline';

const formatMessageTime = (isoString: string): string => {
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / MILLIS_PER_MINUTE);

    if (diffMins < 1) {
      return 'Just now';
    }
    if (diffMins < MINUTES_PER_HOUR) {
      return `${diffMins}m ago`;
    }

    const diffHours = Math.floor(diffMins / MINUTES_PER_HOUR);
    if (diffHours < HOURS_PER_DAY) {
      return `${diffHours}h ago`;
    }

    return date.toLocaleDateString(undefined, {
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      month: 'short',
    });
  } catch {
    return '';
  }
};

const ToolCallRow = ({ toolCall }: { toolCall: ToolCall }) => {
  const status = resolveToolStatus(toolCall);
  const hasInput = Object.keys(toolCall.input).length > 0;
  const hasError = toolCall.result && !toolCall.result.success && toolCall.result.error;

  return (
    <li className='text-xs'>
      <div className='flex flex-wrap items-center gap-2'>
        <span className='font-medium'>{toolCall.name}</span>
        <Badge variant={resolveBadgeVariant(status)} className='px-1.5 py-0 text-[10px]'>
          {status === 'running' ? '…' : status}
        </Badge>
      </div>
      {hasInput && (
        <pre className='text-muted-foreground bg-muted/50 mt-0.5 overflow-x-auto rounded p-1 font-mono text-[10px]'>
          {JSON.stringify(toolCall.input)}
        </pre>
      )}
      {hasError && <p className='text-destructive mt-0.5 text-[10px]'>{toolCall.result?.error}</p>}
    </li>
  );
};

const AvatarBadge = ({ isUser }: { isUser: boolean }) => (
  <div
    className={cn(
      'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
      isUser ? 'bg-primary text-primary-foreground' : 'bg-muted-foreground/20',
    )}
  >
    {isUser ? <User className='h-4 w-4' /> : <Bot className='text-muted-foreground h-4 w-4' />}
  </div>
);

const ToolsSection = ({
  open,
  onOpenChange,
  toolCalls,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  toolCalls: ToolCall[];
}) => (
  <Collapsible open={open} onOpenChange={onOpenChange}>
    <CollapsibleTrigger className='text-muted-foreground hover:text-foreground mt-2 flex items-center gap-1.5 text-xs transition-colors'>
      {open ? <ChevronDown className='h-3.5 w-3.5' /> : <ChevronRight className='h-3.5 w-3.5' />}
      <Wrench className='h-3.5 w-3.5' />
      <span>Tools used ({toolCalls.length})</span>
    </CollapsibleTrigger>
    <CollapsibleContent>
      <ul className='border-muted mt-1.5 space-y-1.5 border-l-2 pl-4'>
        {toolCalls.map((toolCall) => (
          <ToolCallRow key={toolCall.id} toolCall={toolCall} />
        ))}
      </ul>
    </CollapsibleContent>
  </Collapsible>
);

export const ChatMessage = ({ message, isLast }: ChatMessageProps) => {
  const isUser = message.role === 'user';
  const isStreaming = message.isStreaming && isLast;
  const hasToolCalls = !isUser && message.toolCalls && message.toolCalls.length > 0;
  const [toolsOpen, setToolsOpen] = useState(false);

  return (
    <div className={cn('flex gap-3 p-4 rounded-lg', isUser ? 'bg-primary/5' : 'bg-muted/50')}>
      <AvatarBadge isUser={isUser} />

      <div className='min-w-0 flex-1 space-y-1'>
        <div className='text-muted-foreground text-xs font-medium'>
          {isUser ? 'You' : 'TraceRTM Assistant'}
        </div>

        <div className='text-sm leading-relaxed break-words whitespace-pre-wrap'>
          {message.content || (
            <span className='text-muted-foreground italic'>
              {isStreaming ? 'Thinking...' : 'Empty message'}
            </span>
          )}
          {isStreaming && (
            <span className='ml-1 inline-flex items-center'>
              <Loader2 className='text-primary h-3 w-3 animate-spin' />
            </span>
          )}
        </div>

        {hasToolCalls && message.toolCalls ? (
          <ToolsSection
            open={toolsOpen}
            onOpenChange={setToolsOpen}
            toolCalls={message.toolCalls}
          />
        ) : null}

        {!isStreaming && (
          <div className='text-muted-foreground/60 text-[10px]'>
            {formatMessageTime(message.createdAt)}
          </div>
        )}
      </div>
    </div>
  );
};
