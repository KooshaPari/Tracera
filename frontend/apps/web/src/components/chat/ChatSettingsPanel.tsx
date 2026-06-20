/**
 * ChatSettingsPanel - System prompt override and chat preferences.
 * Shown when user clicks the settings (gear) button in the chat header.
 */

import type { ChangeEvent } from 'react';

import { Settings, X } from 'lucide-react';
import { useCallback, useMemo } from 'react';

import type { ChatContext } from '@/lib/ai/types';

import { buildSystemPrompt } from '@/lib/ai/systemPrompt';
import { Button, ScrollArea, Textarea, cn } from '@tracertm/ui';

const PROMPT_ID = 'chat-settings-system-prompt';
const OVERRIDE_ID = 'chat-settings-override';

interface ChatSettingsPanelProps {
  context: ChatContext | null;
  systemPromptOverride: string | null;
  onSystemPromptOverrideChange: (value: string | null) => void;
  onClose: () => void;
  className?: string;
}

const PanelHeader = ({ onClose }: { onClose: () => void }) => (
  <div className='bg-muted/30 flex shrink-0 items-center justify-between border-b px-3 py-2'>
    <div className='flex min-w-0 items-center gap-2'>
      <Settings className='text-muted-foreground h-4 w-4 shrink-0' />
      <h3 className='min-w-0 truncate text-sm font-semibold'>Chat settings</h3>
    </div>
    <Button
      variant='ghost'
      size='icon'
      className='h-7 w-7 shrink-0'
      onClick={onClose}
      title='Close settings'
    >
      <X className='h-4 w-4' />
    </Button>
  </div>
);

const SystemPromptSection = ({ prompt }: { prompt: string }) => (
  <div className='space-y-2'>
    <span id={`${PROMPT_ID}-label`} className='text-muted-foreground text-xs font-medium'>
      Current system prompt (with context)
    </span>
    <ScrollArea
      aria-labelledby={`${PROMPT_ID}-label`}
      className='bg-muted/30 h-32 rounded-md border p-2'
      id={PROMPT_ID}
      role='region'
    >
      <pre className='font-sans text-[11px] leading-relaxed break-words whitespace-pre-wrap'>
        {prompt}
      </pre>
    </ScrollArea>
  </div>
);

const OverrideSection = ({
  onChange,
  value,
}: {
  onChange: (event: ChangeEvent<HTMLTextAreaElement>) => void;
  value: string;
}) => (
  <div className='space-y-2'>
    <label className='text-muted-foreground text-xs font-medium' htmlFor={OVERRIDE_ID}>
      Custom override (optional)
    </label>
    <p className='text-muted-foreground text-[11px]'>
      If set, this replaces the prompt above for all new messages in this session. Leave empty to
      use the default TraceRTM PM Expert prompt.
    </p>
    <Textarea
      id={OVERRIDE_ID}
      placeholder='e.g. You are a strict QA reviewer. Focus only on test coverage.'
      value={value}
      onChange={onChange}
      className='min-h-[80px] resize-y font-mono text-xs'
    />
  </div>
);

const useChatSettingsPanelState = (
  context: ChatContext | null,
  onSystemPromptOverrideChange: (value: string | null) => void,
) => {
  const currentPrompt = useMemo(() => buildSystemPrompt(context ?? undefined), [context]);
  const handleOverrideChange = useCallback(
    (event: ChangeEvent<HTMLTextAreaElement>) => {
      onSystemPromptOverrideChange(event.target.value === '' ? null : event.target.value);
    },
    [onSystemPromptOverrideChange],
  );
  return { currentPrompt, handleOverrideChange };
};

export const ChatSettingsPanel = ({
  context,
  systemPromptOverride,
  onSystemPromptOverrideChange,
  onClose,
  className,
}: ChatSettingsPanelProps) => {
  const { currentPrompt, handleOverrideChange } = useChatSettingsPanelState(
    context,
    onSystemPromptOverrideChange,
  );
  return (
    <div className={cn('flex flex-col bg-background h-full overflow-hidden rounded-lg', className)}>
      <PanelHeader onClose={onClose} />
      <ScrollArea className='min-h-0 flex-1 space-y-4 p-3'>
        <SystemPromptSection prompt={currentPrompt} />
        <OverrideSection value={systemPromptOverride ?? ''} onChange={handleOverrideChange} />
      </ScrollArea>
    </div>
  );
};
