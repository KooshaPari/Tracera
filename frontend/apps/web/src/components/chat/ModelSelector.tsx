/**
 * ModelSelector - Combobox for selecting AI provider and model
 */

import { getEnabledProviders, getModel } from "@/lib/ai/modelRegistry";
import type { AIModel } from "@/lib/ai/types";
import {
	Select,
	SelectContent,
	SelectGroup,
	SelectItem,
	SelectTrigger,
	SelectValue,
	cn,
} from "@tracertm/ui";
import { Sparkles } from "lucide-react";
import { useCallback, useMemo } from "react";

interface ModelSelectorProps {
	value: AIModel;
	onChange: (model: AIModel) => void;
	disabled?: boolean;
	className?: string;
}

const ProviderGroup = ({
	models,
	name,
}: {
	models: AIModel[];
	name: string;
}) => (
	<SelectGroup>
		<div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
			{name}
		</div>
		{models.map((model) => (
			<SelectItem key={model.id} value={model.id} className="text-xs">
				<div className="flex flex-col">
					<span>{model.name}</span>
					{model.description ? (
						<span className="text-[10px] text-muted-foreground">
							{model.description}
						</span>
					) : null}
				</div>
			</SelectItem>
		))}
	</SelectGroup>
);

export const ModelSelector = ({
	value,
	onChange,
	disabled,
	className,
}: ModelSelectorProps) => {
	const providers = useMemo(() => getEnabledProviders(), []);

	const handleValueChange = useCallback(
		(modelId: string) => {
			const model = getModel(modelId);
			if (model) {
				onChange(model);
			}
		},
		[onChange],
	);

	return (
		<Select
			value={value.id}
			onValueChange={handleValueChange}
			disabled={disabled ?? false}
		>
			<SelectTrigger
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
					<ProviderGroup
						key={provider.id}
						models={provider.models}
						name={provider.name}
					/>
				))}
			</SelectContent>
		</Select>
	);
};
