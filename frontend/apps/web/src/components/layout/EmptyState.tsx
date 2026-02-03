import { Button } from "@tracertm/ui";
import type { ReactNode } from "react";

interface EmptyStateProps {
	icon?: ReactNode;
	title: string;
	description?: string;
	action?: {
		label: string;
		onClick: () => void;
	};
	secondaryAction?: {
		label: string;
		onClick: () => void;
	};
}

export const EmptyState = function EmptyState({
	icon,
	title,
	description,
	action,
	secondaryAction,
}: EmptyStateProps) {
	return (
		<div className="flex flex-col items-center justify-center py-12 px-4 text-center">
			{icon && (
				<div className="w-16 h-16 mb-4 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-600">
					{icon}
				</div>
			)}

			<h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
				{title}
			</h3>

			{description && (
				<p className="text-sm text-gray-600 dark:text-gray-400 max-w-md mb-6">
					{description}
				</p>
			)}

			{(action || secondaryAction) && (
				<div className="flex items-center space-x-3">
					{action && (
						<Button onClick={action.onClick} variant="default">
							{action.label}
						</Button>
					)}
					{secondaryAction && (
						<Button onClick={secondaryAction.onClick} variant="outline">
							{secondaryAction.label}
						</Button>
					)}
				</div>
			)}
		</div>
	);
};
