// Edit Affordances Component
// Shows edit capability indicators with visual feedback
// Supports instant, agent-assisted, and manual edit types

import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import { cn } from "@tracertm/ui";
import { Zap, Bot, Edit3, Check } from "lucide-react";
import { memo, useCallback, useState } from "react";

export type EditType = "instant" | "agent_required" | "manual";

interface EditAffordanceData {
  editType: EditType;
  label: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  isPending?: boolean;
}

const EDIT_TYPE_CONFIG: Record<EditType, EditAffordanceData> = {
  instant: {
    editType: "instant",
    label: "Instant Edit",
    description: "Changes apply immediately via automation",
    icon: <Zap className="w-4 h-4" />,
    color: "#3b82f6", // blue
  },
  agent_required: {
    editType: "agent_required",
    label: "Agent-Assisted Edit",
    description: "An AI agent will help implement changes",
    icon: <Bot className="w-4 h-4" />,
    color: "#8b5cf6", // violet
  },
  manual: {
    editType: "manual",
    label: "Manual Edit",
    description: "Edit manually in the full editor",
    icon: <Edit3 className="w-4 h-4" />,
    color: "#f59e0b", // amber
  },
};

interface EditAffordancesProps {
  editType: EditType;
  isEditing?: boolean;
  onEdit?: () => void;
  compact?: boolean;
  showLabel?: boolean;
  className?: string;
}

/**
 * Edit affordance badge component
 */
function EditAffordancesComponent({
  editType,
  isEditing = false,
  onEdit,
  compact = false,
  showLabel = true,
  className,
}: EditAffordancesProps) {
  const [hasInteracted, setHasInteracted] = useState(false);
  const config = EDIT_TYPE_CONFIG[editType];

  const handleClick = useCallback(() => {
    setHasInteracted(true);
    onEdit?.();
  }, [onEdit]);

  if (compact) {
    return (
      <TooltipProvider>
        <Tooltip delayDuration={200}>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className={cn("h-7 w-7 p-0", className)}
              style={{ color: config.color }}
              onClick={handleClick}
              disabled={isEditing}
            >
              {isEditing ? (
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
              ) : (
                config.icon
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">
            <div className="space-y-1">
              <p className="font-semibold text-sm">{config.label}</p>
              <p className="text-xs text-muted-foreground">{config.description}</p>
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <TooltipProvider>
      <Tooltip delayDuration={200}>
        <TooltipTrigger asChild>
          <div
            className={cn(
              "inline-flex items-center gap-2 px-3 py-2 rounded-lg border transition-all",
              hasInteracted && !isEditing && "bg-green-50 border-green-200",
              isEditing && "bg-blue-50 border-blue-200",
              !hasInteracted && !isEditing && "bg-muted/30 border-muted-foreground/20 hover:border-muted-foreground/40",
              className
            )}
            onClick={handleClick}
            style={
              !hasInteracted && !isEditing
                ? {}
                : {
                    backgroundColor: `${config.color}10`,
                    borderColor: `${config.color}30`,
                  }
            }
          >
            {/* Icon */}
            <div style={{ color: config.color }}>
              {isEditing ? (
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
              ) : (
                config.icon
              )}
            </div>

            {/* Label and description */}
            {showLabel && (
              <div className="text-sm">
                <div className="font-semibold">{config.label}</div>
                <div className="text-xs text-muted-foreground">{config.description}</div>
              </div>
            )}

            {/* Success indicator */}
            {hasInteracted && !isEditing && (
              <Check className="w-4 h-4 text-green-500 ml-auto" />
            )}
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <div className="space-y-2">
            <p className="font-semibold">{config.label}</p>
            <p className="text-sm">{config.description}</p>
            {editType === "instant" && (
              <div className="text-xs text-muted-foreground pt-2 border-t">
                Changes are applied automatically through system automation.
              </div>
            )}
            {editType === "agent_required" && (
              <div className="text-xs text-muted-foreground pt-2 border-t">
                An AI agent will analyze the request and implement changes.
              </div>
            )}
            {editType === "manual" && (
              <div className="text-xs text-muted-foreground pt-2 border-t">
                You will be taken to the full editor to make changes manually.
              </div>
            )}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

/**
 * Edit affordance badge (simple badge display)
 */
export function EditAffordanceBadge({
  editType,
  className,
}: {
  editType: EditType;
  className?: string;
}) {
  const config = EDIT_TYPE_CONFIG[editType];

  return (
    <Badge
      className={cn("text-white gap-1", className)}
      style={{ backgroundColor: config.color }}
    >
      <span className="text-sm">{config.icon}</span>
      {config.label}
    </Badge>
  );
}

/**
 * Inline edit affordance indicator
 */
export function InlineEditAffordance({
  editType,
  className,
}: {
  editType: EditType;
  className?: string;
}) {
  const config = EDIT_TYPE_CONFIG[editType];

  return (
    <div
      className={cn(
        "flex items-center gap-1 p-1.5 rounded-md",
        className
      )}
      style={{
        backgroundColor: `${config.color}15`,
        borderLeft: `3px solid ${config.color}`,
      }}
    >
      <div style={{ color: config.color }}>{config.icon}</div>
      <span className="text-xs font-medium">{config.label}</span>
    </div>
  );
}

/**
 * Edit affordance info panel
 */
export function EditAffordancePanel({
  editType,
  className,
}: {
  editType: EditType;
  className?: string;
}) {
  const config = EDIT_TYPE_CONFIG[editType];

  return (
    <div
      className={cn(
        "p-3 rounded-lg border-l-4",
        className
      )}
      style={{
        backgroundColor: `${config.color}10`,
        borderLeftColor: config.color,
      }}
    >
      <div className="flex items-start gap-3">
        <div style={{ color: config.color }} className="mt-0.5">
          {config.icon}
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-sm">{config.label}</h4>
          <p className="text-xs text-muted-foreground mt-1">{config.description}</p>
        </div>
      </div>
    </div>
  );
}

export const EditAffordances = memo(EditAffordancesComponent);
