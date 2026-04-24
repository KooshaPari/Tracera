/**
 * Configuration for TraceRTM Storybook Story Generator
 * Auto-generates CSF 3.0 stories with design system integration
 */

export interface GeneratorConfig {
  /** Root directory to scan for components */
  componentsDir: string[];
  /** Output directory for generated stories */
  storiesDir: string;
  /** File patterns to include */
  includePatterns: RegExp[];
  /** File patterns to exclude */
  excludePatterns: RegExp[];
  /** Path to Figma design metadata */
  designMetadataPath?: string;
  /** Component import path mapping */
  importPathMapping: Record<string, string>;
  /** Generate stories for variants */
  generateVariants: boolean;
  /** Generate all-variants showcase story */
  generateShowcase: boolean;
  /** Overwrite existing stories */
  overwriteExisting: boolean;
}

export const defaultConfig: GeneratorConfig = {
  componentsDir: ['packages/ui/src/components', 'apps/web/src/components'],
  designMetadataPath: '.trace/.meta/designs.yaml',
  excludePatterns: [/\.test\.tsx$/, /\.spec\.tsx$/, /\.stories\.tsx$/, /index\.tsx$/],
  generateShowcase: true,
  generateVariants: true,
  importPathMapping: {
    'apps/web/src/components': '@tracertm/web/components',
    'packages/ui/src/components': '@tracertm/ui',
  },
  includePatterns: [/\.tsx$/],
  overwriteExisting: false,
  storiesDir: 'apps/storybook/src/stories',
};

/**
 * Story template configuration
 */
export interface StoryTemplateConfig {
  /** Component name */
  componentName: string;
  /** Import path for the component */
  importPath: string;
  /** Story title (path in Storybook sidebar) */
  title: string;
  /** Component ID for tracing */
  componentId?: string;
  /** Story ID for tracing */
  storyId?: string;
  /** Figma design URL */
  figmaUrl?: string;
  /** Detected variants (for CVA components) */
  variants?: VariantInfo[];
  /** Component props information */
  props?: PropInfo[];
}

export interface VariantInfo {
  name: string;
  options: string[];
  defaultValue?: string;
}

export interface PropInfo {
  name: string;
  type: string;
  required: boolean;
  defaultValue?: string;
  description?: string;
}

/**
 * Design metadata structure
 */
export interface DesignMetadata {
  components: Record<string, ComponentDesign>;
}

export interface ComponentDesign {
  figmaUrl?: string;
  componentId?: string;
  storyId?: string;
  variants?: string[];
}
