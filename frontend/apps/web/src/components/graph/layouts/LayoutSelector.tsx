// Layout Selector with intuitive names and descriptions
// Replaces technical layout names with user-friendly options

import { Button } from "@tracertm/ui/components/Button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@tracertm/ui/components/Select";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import { cn } from "@tracertm/ui";
import {
  ArrowDown,
  ArrowRight,
  Circle,
  CircleDot,
  GitBranch,
  LayoutGrid,
  Minimize2,
  Network,
} from "lucide-react";
import { LAYOUT_CONFIGS, type LayoutType } from "./useDAGLayout";

// Map icon names to components
const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  ArrowDown,
  ArrowRight,
  GitBranch,
  Network,
  CircleDot,
  LayoutGrid,
  Circle,
  Minimize2,
};

interface LayoutSelectorProps {
  value: LayoutType;
  onChange: (layout: LayoutType) => void;
  variant?: "select" | "buttons" | "compact";
  className?: string;
}

export function LayoutSelector({
  value,
  onChange,
  variant = "select",
  className,
}: LayoutSelectorProps) {
  const currentConfig = LAYOUT_CONFIGS.find((c) => c.id === value) ?? LAYOUT_CONFIGS[0]!;
  const CurrentIcon = ICON_MAP[currentConfig.icon] || Network;

  if (variant === "buttons") {
    return (
      <TooltipProvider>
        <div className={cn("flex flex-wrap gap-1", className)}>
          {LAYOUT_CONFIGS.map((config) => {
            const Icon = ICON_MAP[config.icon] || Network;
            const isActive = value === config.id;

            return (
              <Tooltip key={config.id}>
                <TooltipTrigger asChild>
                  <Button
                    variant={isActive ? "secondary" : "ghost"}
                    size="sm"
                    className={cn(
                      "h-8 w-8 p-0",
                      isActive && "bg-primary/10 text-primary border-primary/30"
                    )}
                    onClick={() => onChange(config.id)}
                  >
                    <Icon className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom" className="max-w-[200px]">
                  <p className="font-medium">{config.label}</p>
                  <p className="text-xs text-muted-foreground">{config.description}</p>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
      </TooltipProvider>
    );
  }

  if (variant === "compact") {
    return (
      <TooltipProvider>
        <div className={cn("flex gap-0.5 rounded-md border p-0.5", className)}>
          {LAYOUT_CONFIGS.slice(0, 4).map((config) => {
            const Icon = ICON_MAP[config.icon] || Network;
            const isActive = value === config.id;

            return (
              <Tooltip key={config.id}>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    className={cn(
                      "h-7 w-7 p-0",
                      isActive && "bg-primary/20 text-primary"
                    )}
                    onClick={() => onChange(config.id)}
                  >
                    <Icon className="h-3.5 w-3.5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                  <p>{config.label}</p>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
      </TooltipProvider>
    );
  }

  // Default: select dropdown
  return (
    <Select value={value} onValueChange={(v) => onChange(v as LayoutType)}>
      <SelectTrigger className={cn("w-[180px] h-9", className)}>
        <div className="flex items-center gap-2">
          <CurrentIcon className="h-4 w-4 text-primary" />
          <SelectValue />
        </div>
      </SelectTrigger>
      <SelectContent>
        {LAYOUT_CONFIGS.map((config) => {
          const Icon = ICON_MAP[config.icon] || Network;
          return (
            <SelectItem key={config.id} value={config.id}>
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4" />
                  <div className="flex flex-col">
                    <span>{config.label}</span>
                    <span className="text-[10px] text-muted-foreground">
                      {config.description}
                    </span>
                  </div>
                </div>
              </SelectItem>
            );
          })}
      </SelectContent>
    </Select>
  );
}

// Recommended layouts for different perspectives
export const PERSPECTIVE_RECOMMENDED_LAYOUTS: Record<string, LayoutType> = {
  traceability: "flow-chart",
  ui: "tree",
  "page-flow": "timeline",
  components: "tree",
  product: "flow-chart",
  technical: "tree",
  test: "tree",
  all: "organic-network",
};

export function getRecommendedLayout(perspective: string): LayoutType {
  return PERSPECTIVE_RECOMMENDED_LAYOUTS[perspective] || "flow-chart";
}
