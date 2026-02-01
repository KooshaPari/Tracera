/**
 * ModelSelector - Combobox for selecting AI provider and model
 */

import {
	cn,
	Select,
	SelectContent,
	SelectGroup,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui";
import { Sparkles } from "lucide-react";
import { getEnabledProviders, getModel } from "@/lib/ai/modelRegistry";
import type { AIModel } from "@/lib/ai/types";

interface ModelSelectorProps {
	value: AIModel;
	onChange: (model: AIModel) => void;
	disabled?: boolean;
	className?: string;
}

export function ModelSelector({
	value,
	onChange,
	disabled,
	className,
}: ModelSelectorProps) {
	const providers = getEnabledProviders();

	const handleValueChange = (modelId: string) => {
		const model = getModel(modelId);
		if (model) {
			onChange(model);
		}
	};

	return (
		<Select
			value={value.id}
			onValueChange={handleValueChange}
			disabled={disabled ?? false}
		>
		<SelectTrigger
			role="button"
			className={cn(
				"h-8 text-xs gap-1.5 bg-background/50 border-muted",
				className,
			)}
		>
				<Sparkles className="w-3 h-3 text-primary" />
				<SelectValue placeholder="Select model" />
			</SelectTrigger>
			<SelectContent>
				{providers.map((provider) => (
					<SelectGroup key={provider.id}>
						<div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
							{provider.name}
						</div>
						{provider.models.map((model) => (
							<SelectItem key={model.id} value={model.id} className="text-xs">
								<div className="flex flex-col">
									<span>{model.name}</span>
									{model.description && (
										<span className="text-[10px] text-muted-foreground">
											{model.description}
										</span>
									)}
								</div>
							</SelectItem>
						))}
					</SelectGroup>
				))}
			</SelectContent>
		</Select>
	);
}
