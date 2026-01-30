import { Button } from "@tracertm/ui/components/Button";
import type { LucideIcon } from "lucide-react";

interface EmptyStateProps {
	icon?: LucideIcon;
	title: string;
	description: string;
	action?: {
		label: string;
		onClick: () => void;
		variant?: "default" | "outline" | "secondary";
	};
	testId?: string;
}

export function EmptyState({
	icon: Icon,
	title,
	description,
	action,
	testId = "empty-state",
}: EmptyStateProps) {
	return (
		<div
			className="flex flex-col items-center justify-center rounded-lg border border-dashed border-muted-foreground/25 px-8 py-16 text-center"
			data-testid={testId}
		>
			{Icon && <Icon className="mb-4 h-16 w-16 text-muted-foreground/50" />}
			<h3 className="mb-2 text-lg font-semibold text-foreground">{title}</h3>
			<p className="mb-6 text-sm text-muted-foreground">{description}</p>
			{action && (
				<Button onClick={action.onClick} variant={action.variant || "default"}>
					{action.label}
				</Button>
			)}
		</div>
	);
}
