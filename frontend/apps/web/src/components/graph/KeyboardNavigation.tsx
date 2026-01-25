// Keyboard Navigation Component
// Provides keyboard shortcuts for graph navigation
// Arrow keys, Enter, Escape support

import { Card } from "@tracertm/ui/components/Card";
import { Badge } from "@tracertm/ui/components/Badge";
import { cn } from "@tracertm/ui";
import {
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  CornerDownLeft,
  HelpCircle,
} from "lucide-react";
import { memo, useEffect, useState } from "react";

/**
 * Keyboard shortcuts configuration
 */
export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  description: string;
  action: string;
}

const DEFAULT_SHORTCUTS: KeyboardShortcut[] = [
  {
    key: "ArrowUp",
    description: "Navigate to parent node",
    action: "navigate-parent",
  },
  {
    key: "ArrowDown",
    description: "Navigate to first child node",
    action: "navigate-child",
  },
  {
    key: "ArrowLeft",
    description: "Collapse node",
    action: "collapse",
  },
  {
    key: "ArrowRight",
    description: "Expand node",
    action: "expand",
  },
  {
    key: "Enter",
    description: "Toggle node expansion",
    action: "toggle-expansion",
  },
  {
    key: "Backspace",
    description: "Go back in navigation history",
    action: "navigate-back",
  },
  {
    key: "Escape",
    description: "Close current panel/deselect",
    action: "close-panel",
  },
  {
    key: "f",
    ctrl: true,
    description: "Open search",
    action: "open-search",
  },
];

interface KeyboardNavigationProps {
  onKeyPress: (action: string, event: KeyboardEvent) => void;
  shortcuts?: KeyboardShortcut[];
  showHelp?: boolean;
  className?: string;
}

/**
 * Format keyboard shortcut display
 */
function formatShortcut(shortcut: KeyboardShortcut): string {
  const parts: string[] = [];

  if (shortcut.ctrl) parts.push("Ctrl");
  if (shortcut.shift) parts.push("Shift");
  if (shortcut.alt) parts.push("Alt");

  const keyLabel =
    shortcut.key === "ArrowUp"
      ? "↑"
      : shortcut.key === "ArrowDown"
      ? "↓"
      : shortcut.key === "ArrowLeft"
      ? "←"
      : shortcut.key === "ArrowRight"
      ? "→"
      : shortcut.key === "Enter"
      ? "Return"
      : shortcut.key === "Backspace"
      ? "Backspace"
      : shortcut.key === "Escape"
      ? "Esc"
      : shortcut.key.toUpperCase();

  parts.push(keyLabel);
  return parts.join("+");
}

/**
 * Get icon for keyboard action
 */
function getActionIcon(action: string) {
  switch (action) {
    case "navigate-parent":
      return <ArrowUp className="w-4 h-4" />;
    case "navigate-child":
      return <ArrowDown className="w-4 h-4" />;
    case "collapse":
      return <ArrowLeft className="w-4 h-4" />;
    case "expand":
      return <ArrowRight className="w-4 h-4" />;
    case "toggle-expansion":
      return <CornerDownLeft className="w-4 h-4" />;
    case "navigate-back":
      return <ArrowLeft className="w-4 h-4" />;
    case "close-panel":
      return <button className="text-base leading-none">×</button>;
    default:
      return null;
  }
}

/**
 * Keyboard Navigation Controller Component
 */
function KeyboardNavigationComponent({
  onKeyPress,
  shortcuts = DEFAULT_SHORTCUTS,
  showHelp = false,
  className,
}: KeyboardNavigationProps) {
  const [showHelpPanel, setShowHelpPanel] = useState(showHelp);

  // Handle keyboard events
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Check shortcuts
      for (const shortcut of shortcuts) {
        const keyMatch =
          event.key === shortcut.key ||
          (event.key === "Enter" && shortcut.key === "Enter") ||
          (event.key === "Escape" && shortcut.key === "Escape") ||
          (event.key === "Backspace" && shortcut.key === "Backspace") ||
          (event.key === "ArrowUp" && shortcut.key === "ArrowUp") ||
          (event.key === "ArrowDown" && shortcut.key === "ArrowDown") ||
          (event.key === "ArrowLeft" && shortcut.key === "ArrowLeft") ||
          (event.key === "ArrowRight" && shortcut.key === "ArrowRight") ||
          (event.key.toLowerCase() === shortcut.key.toLowerCase());

        const ctrlMatch = shortcut.ctrl ? event.ctrlKey || event.metaKey : !event.ctrlKey && !event.metaKey;
        const shiftMatch = shortcut.shift ? event.shiftKey : !event.shiftKey;
        const altMatch = shortcut.alt ? event.altKey : !event.altKey;

        if (keyMatch && ctrlMatch && shiftMatch && altMatch) {
          // Special handling for help toggle
          if (shortcut.action === "open-search") {
            event.preventDefault();
            setShowHelpPanel(!showHelpPanel);
            return;
          }

          onKeyPress(shortcut.action, event);
          break;
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [onKeyPress, shortcuts, showHelpPanel]);

  return (
    <>
      {/* Help panel */}
      {showHelpPanel && (
        <Card className={cn("absolute bottom-4 right-4 w-80 p-4", className)}>
          <div className="space-y-3">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold flex items-center gap-2">
                <HelpCircle className="w-4 h-4" />
                Keyboard Shortcuts
              </h3>
              <button
                onClick={() => setShowHelpPanel(false)}
                className="text-muted-foreground hover:text-foreground"
                type="button"
              >
                ×
              </button>
            </div>

            <div className="space-y-2 max-h-80 overflow-y-auto">
              {shortcuts.map((shortcut) => (
                <div
                  key={`${shortcut.key}-${shortcut.ctrl}-${shortcut.shift}-${shortcut.alt}`}
                  className="flex items-center justify-between gap-2 p-2 rounded-md hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    {getActionIcon(shortcut.action) && (
                      <div className="text-muted-foreground shrink-0">
                        {getActionIcon(shortcut.action)}
                      </div>
                    )}
                    <span className="text-sm truncate">{shortcut.description}</span>
                  </div>
                  <Badge variant="outline" className="text-xs font-mono shrink-0">
                    {formatShortcut(shortcut)}
                  </Badge>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t text-xs text-muted-foreground">
              Press <Badge variant="secondary" className="text-[10px]">Ctrl+F</Badge> to toggle this help panel
            </div>
          </div>
        </Card>
      )}
    </>
  );
}

/**
 * Keyboard shortcut reference card
 */
export function KeyboardShortcutCard({
  shortcuts = DEFAULT_SHORTCUTS,
  className,
}: {
  shortcuts?: KeyboardShortcut[];
  className?: string;
}) {
  return (
    <Card className={cn("p-4", className)}>
      <h3 className="font-semibold mb-4 flex items-center gap-2">
        <HelpCircle className="w-4 h-4" />
        Keyboard Shortcuts
      </h3>

      <div className="grid grid-cols-2 gap-3">
        {shortcuts.map((shortcut) => (
          <div key={`${shortcut.key}-ref`} className="space-y-1">
            <Badge variant="outline" className="text-xs font-mono">
              {formatShortcut(shortcut)}
            </Badge>
            <p className="text-xs text-muted-foreground">{shortcut.description}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}

export const KeyboardNavigation = memo(KeyboardNavigationComponent);
