// Perspective Selector - Switch between different graph views

import { Button } from "@tracertm/ui/components/Button";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import {
	Briefcase,
	Code,
	Gauge,
	Layout,
	Network,
	Shield,
	Users,
} from "lucide-react";
import { memo } from "react";
import type { GraphPerspective } from "./types";
import { PERSPECTIVE_CONFIGS } from "./types";

interface PerspectiveSelectorProps {
	currentPerspective: GraphPerspective;
	onPerspectiveChange: (perspective: GraphPerspective) => void;
	itemCounts?: Partial<Record<GraphPerspective, number>>;
}

// Icon mapping for perspectives
const PERSPECTIVE_ICONS: Record<
	string,
	React.ComponentType<{ className?: string }>
> = {
	all: Network,
	product: Users,
	business: Briefcase,
	technical: Code,
	ui: Layout,
	security: Shield,
	performance: Gauge,
};

function PerspectiveSelectorComponent({
	currentPerspective,
	onPerspectiveChange,
	itemCounts = {},
}: PerspectiveSelectorProps) {
	return (
		<TooltipProvider>
			<div className="flex items-center gap-1 p-1 bg-muted/50 rounded-lg">
				{PERSPECTIVE_CONFIGS.map((config) => {
					const Icon = PERSPECTIVE_ICONS[config.id] || Network;
					const isActive = currentPerspective === config.id;
					const count = itemCounts[config.id] || 0;

					return (
						<Tooltip key={config.id} delayDuration={200}>
							<TooltipTrigger asChild>
								<Button
									variant={isActive ? "default" : "ghost"}
									size="sm"
									onClick={() => onPerspectiveChange(config.id)}
									className={`
                    relative h-9 px-3 gap-2
                    ${isActive ? "" : "hover:bg-muted"}
                  `}
									style={
										isActive ? { backgroundColor: config.color } : undefined
									}
								>
									<Icon className="h-4 w-4" />
									<span className="hidden sm:inline text-xs font-medium">
										{config.label.replace(" View", "")}
									</span>
									{count > 0 && (
										<span
											className={`
                        text-[10px] px-1.5 rounded-full
                        ${
													isActive
														? "bg-white/20 text-white"
														: "bg-muted-foreground/10 text-muted-foreground"
												}
                      `}
										>
											{count}
										</span>
									)}
								</Button>
							</TooltipTrigger>
							<TooltipContent side="bottom" className="max-w-xs">
								<div className="space-y-1">
									<p className="font-medium">{config.label}</p>
									<p className="text-xs text-muted-foreground">
										{config.description}
									</p>
									{config.includeTypes.length > 0 && (
										<p className="text-xs text-muted-foreground">
											Includes: {config.includeTypes.slice(0, 4).join(", ")}
											{config.includeTypes.length > 4 &&
												` +${config.includeTypes.length - 4} more`}
										</p>
									)}
								</div>
							</TooltipContent>
						</Tooltip>
					);
				})}
			</div>
		</TooltipProvider>
	);
}

export const PerspectiveSelector = memo(PerspectiveSelectorComponent);
