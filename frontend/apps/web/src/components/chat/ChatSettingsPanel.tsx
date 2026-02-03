/**
 * ChatSettingsPanel - System prompt override and chat preferences.
 * Shown when user clicks the settings (gear) button in the chat header.
 */

import type { ChatContext } from "@/lib/ai/types";
import { buildSystemPrompt } from "@/lib/ai/systemPrompt";
import { Button, ScrollArea, Textarea, cn } from "@tracertm/ui";
import { Settings, X } from "lucide-react";
import { type ChangeEvent, useCallback, useMemo } from "react";

const PROMPT_ID = "chat-settings-system-prompt";
const OVERRIDE_ID = "chat-settings-override";

interface ChatSettingsPanelProps {
	context: ChatContext | null;
	systemPromptOverride: string | null;
	onSystemPromptOverrideChange: (value: string | null) => void;
	onClose: () => void;
	className?: string;
}

const PanelHeader = ({ onClose }: { onClose: () => void }) => (
	<div className="flex items-center justify-between px-3 py-2 border-b bg-muted/30 shrink-0">
		<div className="flex items-center gap-2 min-w-0">
			<Settings className="h-4 w-4 shrink-0 text-muted-foreground" />
			<h3 className="font-semibold text-sm truncate min-w-0">Chat settings</h3>
		</div>
		<Button
			variant="ghost"
			size="icon"
			className="h-7 w-7 shrink-0"
			onClick={onClose}
			title="Close settings"
		>
			<X className="h-4 w-4" />
		</Button>
	</div>
);

const SystemPromptSection = ({ prompt }: { prompt: string }) => (
	<div className="space-y-2">
		<span
			id={`${PROMPT_ID}-label`}
			className="text-xs font-medium text-muted-foreground"
		>
			Current system prompt (with context)
		</span>
		<ScrollArea
			aria-labelledby={`${PROMPT_ID}-label`}
			className="h-32 rounded-md border bg-muted/30 p-2"
			id={PROMPT_ID}
			role="region"
		>
			<pre className="text-[11px] leading-relaxed whitespace-pre-wrap break-words font-sans">
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
	<div className="space-y-2">
		<label
			className="text-xs font-medium text-muted-foreground"
			htmlFor={OVERRIDE_ID}
		>
			Custom override (optional)
		</label>
		<p className="text-[11px] text-muted-foreground">
			If set, this replaces the prompt above for all new messages in this
			session. Leave empty to use the default TraceRTM PM Expert prompt.
		</p>
		<Textarea
			id={OVERRIDE_ID}
			placeholder="e.g. You are a strict QA reviewer. Focus only on test coverage."
			value={value}
			onChange={onChange}
			className="min-h-[80px] text-xs resize-y font-mono"
		/>
	</div>
);

const useChatSettingsPanelState = (
	context: ChatContext | null,
	onSystemPromptOverrideChange: (value: string | null) => void,
) => {
	const currentPrompt = useMemo(
		() => buildSystemPrompt(context ?? undefined),
		[context],
	);
	const handleOverrideChange = useCallback(
		(event: ChangeEvent<HTMLTextAreaElement>) => {
			onSystemPromptOverrideChange(
				event.target.value === "" ? null : event.target.value,
			);
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
	const { currentPrompt, handleOverrideChange } =
		useChatSettingsPanelState(context, onSystemPromptOverrideChange);
	return (
		<div
			className={cn(
				"flex flex-col bg-background h-full overflow-hidden rounded-lg",
				className,
			)}
		>
			<PanelHeader onClose={onClose} />
			<ScrollArea className="flex-1 min-h-0 p-3 space-y-4">
				<SystemPromptSection prompt={currentPrompt} />
				<OverrideSection
					value={systemPromptOverride ?? ""}
					onChange={handleOverrideChange}
				/>
			</ScrollArea>
		</div>
	);
};
