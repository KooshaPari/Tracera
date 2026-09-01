type StoryArgs = Record<string, unknown>;
type Viewport = "desktop" | "laptop" | "mobile" | "tablet";
type Theme = "dark" | "light";

type VisualStory<TArgs extends StoryArgs> = {
  args: TArgs;
  parameters?: Record<string, unknown>;
  play?: () => Promise<void>;
};

const VIEWPORTS: Record<Viewport, { height: string; width: string }> = {
  desktop: { height: "900px", width: "1440px" },
  laptop: { height: "768px", width: "1024px" },
  mobile: { height: "844px", width: "390px" },
  tablet: { height: "1024px", width: "768px" },
};

const VISUAL_COMPONENTS: Record<string, { themes: Theme[]; viewports: Viewport[] }> = {
  UnifiedGraphView: {
    themes: ["light", "dark"],
    viewports: ["desktop", "laptop", "tablet", "mobile"],
  },
};

function normalizeName(value: string) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

function titleCase(value: string) {
  return `${value.slice(0, 1).toUpperCase()}${value.slice(1).toLowerCase()}`;
}

export function generateSnapshotName(
  component: string,
  variant: string,
  viewport: string,
  theme: string,
  state?: string,
) {
  return [component, variant, viewport, theme, state]
    .filter((part): part is string => Boolean(part))
    .map(normalizeName)
    .join("-");
}

export function generateVisualTestParameters(
  component: string,
  options: { delay?: number; themes?: Theme[]; viewports?: Viewport[] } = {},
) {
  const configuration = VISUAL_COMPONENTS[component];
  const themes = options.themes ?? configuration?.themes ?? ["light", "dark"];
  const viewports = options.viewports ?? configuration?.viewports ?? ["desktop"];

  return {
    chromatic: {
      delay: options.delay ?? 300,
      modes: Object.fromEntries(
        themes.map((theme) => [
          theme,
          {
            theme,
            viewports: viewports.map((viewport) => VIEWPORTS[viewport]),
          },
        ]),
      ),
    },
  };
}

export function createViewportStories<TArgs extends StoryArgs>(
  _component: string,
  args: TArgs,
  viewports: Viewport[] = ["desktop", "laptop", "tablet", "mobile"],
) {
  return Object.fromEntries(
    viewports.map((viewport) => [
      titleCase(viewport),
      {
        args,
        parameters: { viewport: { defaultViewport: viewport } },
      } satisfies VisualStory<TArgs>,
    ]),
  ) as Record<string, VisualStory<TArgs>>;
}

export function createThemeStories<TArgs extends StoryArgs>(
  args: TArgs,
  themes: Theme[] = ["light", "dark"],
) {
  return Object.fromEntries(
    themes.map((theme) => [
      titleCase(theme),
      {
        args,
        parameters: { backgrounds: { default: theme }, theme },
      } satisfies VisualStory<TArgs>,
    ]),
  ) as Record<string, VisualStory<TArgs>>;
}

export function createInteractionStories<TArgs extends StoryArgs>(
  args: TArgs,
  selector = '[data-testid="visual-subject"]',
) {
  const interactionStory = (state: string): VisualStory<TArgs> => ({
    args,
    parameters: { pseudo: { [state]: [selector] } },
  });

  return {
    Active: interactionStory("active"),
    Disabled: { args: { ...args, disabled: true } },
    Focused: interactionStory("focus"),
    Hovered: interactionStory("hover"),
  } as Record<string, VisualStory<TArgs>>;
}

export class VisualRegressionTracker {
  private readonly changes = new Map<string, string[]>();

  clear() {
    this.changes.clear();
  }

  getChanges(component?: string) {
    if (component) {
      return [...(this.changes.get(component) ?? [])];
    }
    return [...this.changes.values()].flat();
  }

  hasChanges(component?: string) {
    return this.getChanges(component).length > 0;
  }

  recordChange(component: string, snapshot: string) {
    const changes = this.changes.get(component) ?? [];
    changes.push(snapshot);
    this.changes.set(component, changes);
  }
}

export class VisualTestMetrics {
  private components = 0;
  private snapshots = 0;
  private readonly startedAt = performance.now();

  getMetrics() {
    return {
      averageSnapshotsPerComponent: this.components === 0 ? 0 : this.snapshots / this.components,
      components: this.components,
      duration: Math.max(0, performance.now() - this.startedAt),
      snapshots: this.snapshots,
    };
  }

  recordComponent(viewportCount: number, themeCount: number) {
    this.components += 1;
    this.snapshots += viewportCount * themeCount;
  }
}

export function validateComponentVisualTests(
  component: string,
  requiredViewports: string[] = [],
  requiredThemes: string[] = [],
) {
  const configuration = VISUAL_COMPONENTS[component];
  if (!configuration) {
    return false;
  }

  return (
    requiredViewports.every((viewport) => configuration.viewports.includes(viewport as Viewport)) &&
    requiredThemes.every((theme) => configuration.themes.includes(theme as Theme))
  );
}
