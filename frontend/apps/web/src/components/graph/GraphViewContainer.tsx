// Graph View Container - Sidebar and combo box system for separated graph views
// Provides distinct views: Traceability, Page Flow, Component Library, and Perspective views

import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@tracertm/ui/components/Select";
import { ScrollArea } from "@tracertm/ui/components/ScrollArea";
import { Separator } from "@tracertm/ui/components/Separator";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import { cn } from "@tracertm/ui";
import type { Item, Link } from "@tracertm/types";
import {
  ChevronLeft,
  ChevronRight,
  Component,
  FileStack,
  GitBranch,
  Layers,
  Lock,
  Monitor,
  Network,
  ShoppingCart,
  Workflow,
  Zap,
} from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import type { GraphPerspective } from "./types";
import { PERSPECTIVE_CONFIGS } from "./types";

// View types
export type GraphViewMode =
  | "traceability"
  | "page-flow"
  | "components"
  | "perspective-product"
  | "perspective-business"
  | "perspective-technical"
  | "perspective-ui"
  | "perspective-security"
  | "perspective-performance";

interface ViewConfig {
  id: GraphViewMode;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  category: "main" | "perspective";
  perspective?: GraphPerspective;
}

const VIEW_CONFIGS: ViewConfig[] = [
  {
    id: "traceability",
    label: "Traceability Graph",
    description: "Full node graph with all connections",
    icon: Network,
    category: "main",
  },
  {
    id: "page-flow",
    label: "Page Flow",
    description: "UI page interactions and navigation",
    icon: Workflow,
    category: "main",
  },
  {
    id: "components",
    label: "Component Library",
    description: "UI component tree and hierarchy",
    icon: Component,
    category: "main",
  },
  {
    id: "perspective-product",
    label: "Product View",
    description: "Features, epics, and user stories",
    icon: ShoppingCart,
    category: "perspective",
    perspective: "product",
  },
  {
    id: "perspective-business",
    label: "Business View",
    description: "Business rules and requirements",
    icon: FileStack,
    category: "perspective",
    perspective: "business",
  },
  {
    id: "perspective-technical",
    label: "Technical View",
    description: "Architecture and implementation",
    icon: GitBranch,
    category: "perspective",
    perspective: "technical",
  },
  {
    id: "perspective-ui",
    label: "UI/UX View",
    description: "Wireframes, mockups, and screens",
    icon: Monitor,
    category: "perspective",
    perspective: "ui",
  },
  {
    id: "perspective-security",
    label: "Security View",
    description: "Security requirements and controls",
    icon: Lock,
    category: "perspective",
    perspective: "security",
  },
  {
    id: "perspective-performance",
    label: "Performance View",
    description: "Performance requirements and metrics",
    icon: Zap,
    category: "perspective",
    perspective: "performance",
  },
];

interface GraphViewContainerProps {
  items: Item[];
  links: Link[];
  isLoading?: boolean | undefined;
  projectId?: string | undefined;
  onNavigateToItem?: ((itemId: string) => void) | undefined;
  defaultView?: GraphViewMode | undefined;
  children: (props: {
    viewMode: GraphViewMode;
    perspective: GraphPerspective | null;
    items: Item[];
    links: Link[];
    onNavigateToItem?: ((itemId: string) => void) | undefined;
  }) => React.ReactNode;
}

interface SidebarNavItemProps {
  config: ViewConfig;
  isActive: boolean;
  isCollapsed: boolean;
  itemCount?: number | undefined;
  onClick: () => void;
}

function SidebarNavItem({
  config,
  isActive,
  isCollapsed,
  itemCount,
  onClick,
}: SidebarNavItemProps) {
  const Icon = config.icon;

  return (
    <Button
      variant={isActive ? "secondary" : "ghost"}
      className={cn(
        "w-full justify-start gap-3 h-10 transition-all",
        isCollapsed && "justify-center px-2",
        isActive && "bg-primary/10 text-primary hover:bg-primary/15"
      )}
      onClick={onClick}
      title={isCollapsed ? config.label : undefined}
    >
      <Icon className={cn("h-4 w-4 shrink-0", isActive && "text-primary")} />
      {!isCollapsed && (
        <>
          <span className="truncate flex-1 text-left">{config.label}</span>
          {itemCount !== undefined && itemCount > 0 && (
            <Badge variant="secondary" className="text-[10px] px-1.5 h-5">
              {itemCount}
            </Badge>
          )}
        </>
      )}
    </Button>
  );
}

export function GraphViewContainer({
  items,
  links,
  isLoading = false,
  onNavigateToItem,
  defaultView = "traceability",
  children,
}: GraphViewContainerProps) {
  const [viewMode, setViewMode] = useState<GraphViewMode>(defaultView);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Get current view config
  const currentConfig = useMemo(
    () => VIEW_CONFIGS.find((c) => c.id === viewMode) || VIEW_CONFIGS[0],
    [viewMode]
  );

  // Calculate item counts per perspective
  const perspectiveCounts = useMemo(() => {
    const counts = {
      all: items.length,
      product: 0,
      business: 0,
      technical: 0,
      ui: 0,
      security: 0,
      performance: 0,
    };

    for (const item of items) {
      const itemType = (item.type || item.view || "").toLowerCase();

      // Product items
      if (
        itemType.includes("feature") ||
        itemType.includes("epic") ||
        itemType.includes("story") ||
        itemType.includes("requirement")
      ) {
        counts.product++;
      }

      // Business items
      if (
        itemType.includes("business") ||
        itemType.includes("rule") ||
        itemType.includes("process")
      ) {
        counts.business++;
      }

      // Technical items
      if (
        itemType.includes("task") ||
        itemType.includes("code") ||
        itemType.includes("api") ||
        itemType.includes("service") ||
        itemType.includes("module")
      ) {
        counts.technical++;
      }

      // UI items
      if (
        itemType.includes("ui") ||
        itemType.includes("wireframe") ||
        itemType.includes("mockup") ||
        itemType.includes("page") ||
        itemType.includes("component") ||
        itemType.includes("screen")
      ) {
        counts.ui++;
      }

      // Security items
      if (itemType.includes("security") || itemType.includes("auth")) {
        counts.security++;
      }

      // Performance items
      if (itemType.includes("performance") || itemType.includes("metric")) {
        counts.performance++;
      }
    }

    return counts;
  }, [items]);

  // Get count for a view
  const getViewCount = useCallback(
    (config: ViewConfig): number | undefined => {
      if (config.category === "main") {
        if (config.id === "traceability") return items.length;
        if (config.id === "components" || config.id === "page-flow") {
          return perspectiveCounts.ui;
        }
        return undefined;
      }
      if (config.perspective) {
        switch (config.perspective) {
          case "product":
            return perspectiveCounts.product;
          case "business":
            return perspectiveCounts.business;
          case "technical":
            return perspectiveCounts.technical;
          case "ui":
            return perspectiveCounts.ui;
          case "security":
            return perspectiveCounts.security;
          case "performance":
            return perspectiveCounts.performance;
          default:
            return perspectiveCounts.all;
        }
      }
      return undefined;
    },
    [items.length, perspectiveCounts]
  );

  // Get perspective from view mode
  const getPerspective = useCallback((mode: GraphViewMode): GraphPerspective | null => {
    const config = VIEW_CONFIGS.find((c) => c.id === mode);
    return config?.perspective || null;
  }, []);

  // Handle view change
  const handleViewChange = useCallback((mode: GraphViewMode) => {
    setViewMode(mode);
  }, []);

  // Main views
  const mainViews = VIEW_CONFIGS.filter((c) => c.category === "main");
  const perspectiveViews = VIEW_CONFIGS.filter((c) => c.category === "perspective");

  // Loading state
  if (isLoading) {
    return (
      <div className="flex h-full">
        <div className="w-56 border-r p-4 space-y-2">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
        <div className="flex-1 p-6 space-y-4">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-[calc(100vh-200px)]" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div
        className={cn(
          "border-r bg-muted/30 transition-all duration-300 flex flex-col",
          sidebarCollapsed ? "w-14" : "w-56"
        )}
      >
        {/* Sidebar header */}
        <div className="p-3 border-b flex items-center justify-between">
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-primary" />
              <span className="font-semibold text-sm">Views</span>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          >
            {sidebarCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Sidebar content */}
        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            {/* Main views */}
            {!sidebarCollapsed && (
              <div className="px-2 py-1.5 text-[11px] font-medium text-muted-foreground uppercase tracking-wide">
                Main Views
              </div>
            )}
            {mainViews.map((config) => (
              <SidebarNavItem
                key={config.id}
                config={config}
                isActive={viewMode === config.id}
                isCollapsed={sidebarCollapsed}
                itemCount={getViewCount(config)}
                onClick={() => handleViewChange(config.id)}
              />
            ))}

            {!sidebarCollapsed && <Separator className="my-3" />}

            {/* Perspective views */}
            {!sidebarCollapsed && (
              <div className="px-2 py-1.5 text-[11px] font-medium text-muted-foreground uppercase tracking-wide">
                Perspectives
              </div>
            )}
            {perspectiveViews.map((config) => (
              <SidebarNavItem
                key={config.id}
                config={config}
                isActive={viewMode === config.id}
                isCollapsed={sidebarCollapsed}
                itemCount={getViewCount(config)}
                onClick={() => handleViewChange(config.id)}
              />
            ))}
          </div>
        </ScrollArea>

        {/* Sidebar footer */}
        {!sidebarCollapsed && (
          <div className="p-3 border-t">
            <div className="text-[11px] text-muted-foreground">
              {items.length} items · {links.length} links
            </div>
          </div>
        )}
      </div>

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar with combo box */}
        <div className="border-b p-3 flex items-center justify-between gap-4 bg-background">
          <div className="flex items-center gap-3">
            {/* View selector combo box */}
            <Select value={viewMode} onValueChange={(v) => handleViewChange(v as GraphViewMode)}>
              <SelectTrigger className="w-[220px] h-9">
                <div className="flex items-center gap-2">
                  {currentConfig && <currentConfig.icon className="h-4 w-4 text-primary" />}
                  <SelectValue />
                </div>
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
                    Main Views
                  </div>
                  {mainViews.map((config) => (
                    <SelectItem key={config.id} value={config.id}>
                      <div className="flex items-center gap-2">
                        <config.icon className="h-4 w-4" />
                        <span>{config.label}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectGroup>
                <Separator className="my-1" />
                <SelectGroup>
                  <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
                    Perspectives
                  </div>
                  {perspectiveViews.map((config) => (
                    <SelectItem key={config.id} value={config.id}>
                      <div className="flex items-center gap-2">
                        <config.icon className="h-4 w-4" />
                        <span>{config.label}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>

            {/* Current view info */}
            {currentConfig && (
              <div className="hidden sm:block">
                <p className="text-sm text-muted-foreground">{currentConfig.description}</p>
              </div>
            )}
          </div>

          {/* View badge */}
          {currentConfig?.perspective && (
            <Badge
              variant="outline"
              className="px-3 py-1"
              style={{
                backgroundColor: `${
                  PERSPECTIVE_CONFIGS.find((c) => c.id === currentConfig.perspective)?.color ?? "#64748b"
                }20`,
                borderColor: PERSPECTIVE_CONFIGS.find((c) => c.id === currentConfig.perspective)
                  ?.color ?? "#64748b",
              }}
            >
              {currentConfig.label}
            </Badge>
          )}
        </div>

        {/* View content */}
        <div className="flex-1 overflow-hidden">
          {children({
            viewMode,
            perspective: getPerspective(viewMode),
            items,
            links,
            onNavigateToItem,
          })}
        </div>
      </div>
    </div>
  );
}
