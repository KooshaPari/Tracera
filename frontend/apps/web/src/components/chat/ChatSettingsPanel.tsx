/**
 * ChatSettingsPanel - System prompt override and chat preferences.
 * Shown when user clicks the settings (gear) button in the chat header.
 */

import { Button, cn, ScrollArea, Textarea } from "@tracertm/ui";
import { Settings, X } from "lucide-react";
import { buildSystemPrompt } from "@/lib/ai/systemPrompt";
import type { ChatContext } from "@/lib/ai/types";

interface ChatSettingsPanelProps {
	context: ChatContext | null;
	systemPromptOverride: string | null;
	onSystemPromptOverrideChange: (value: string | null) => void;
	onClose: () => void;
	className?: string;
}

export function ChatSettingsPanel({
	context,
	systemPromptOverride,
	onSystemPromptOverrideChange,
	onClose,
	className,
}: ChatSettingsPanelProps) {
	const currentPrompt = buildSystemPrompt(context ?? undefined);

	return (
		<div
			className={cn(
				"flex flex-col bg-background h-full overflow-hidden rounded-lg",
				className,
			)}
		>
			{/* Header */}
			<div className="flex items-center justify-between px-3 py-2 border-b bg-muted/30 shrink-0">
				<div className="flex items-center gap-2 min-w-0">
					<Settings className="h-4 w-4 shrink-0 text-muted-foreground" />
					<h3 className="font-semibold text-sm truncate min-w-0">
						Chat settings
					</h3>
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

			<ScrollArea className="flex-1 min-h-0 p-3 space-y-4">
				{/* System prompt */}
				<div className="space-y-2">
					<label className="text-xs font-medium text-muted-foreground">
						Current system prompt (with context)
					</label>
					<ScrollArea className="h-32 rounded-md border bg-muted/30 p-2">
						<pre className="text-[11px] leading-relaxed whitespace-pre-wrap break-words font-sans">
							{currentPrompt}
						</pre>
					</ScrollArea>
				</div>

				<div className="space-y-2">
					<label className="text-xs font-medium text-muted-foreground">
						Custom override (optional)
					</label>
					<p className="text-[11px] text-muted-foreground">
						If set, this replaces the prompt above for all new messages in this
						session. Leave empty to use the default TraceRTM PM Expert prompt.
					</p>
					<Textarea
						placeholder="e.g. You are a strict QA reviewer. Focus only on test coverage."
						value={systemPromptOverride ?? ""}
						onChange={(e) =>
							onSystemPromptOverrideChange(
								e.target.value === "" ? null : e.target.value,
							)
						}
						className="min-h-[80px] text-xs resize-y font-mono"
					/>
				</div>
			</ScrollArea>
		</div>
	);
}
