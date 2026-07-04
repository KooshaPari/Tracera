/**
 * Type definitions for Figma Generator
 *
 * Comprehensive types for Figma API, component definitions, and design tokens
 */

// Figma API Types
export namespace FigmaAPI {
  export interface Color {
    r: number;
    g: number;
    b: number;
    a?: number;
  }

  export interface Paint {
    type:
      | 'SOLID'
      | 'GRADIENT_LINEAR'
      | 'GRADIENT_RADIAL'
      | 'GRADIENT_ANGULAR'
      | 'GRADIENT_DIAMOND'
      | 'IMAGE';
    visible?: boolean;
    opacity?: number;
    color?: Color;
    blendMode?: BlendMode;
    gradientHandlePositions?: Vector[];
    gradientStops?: ColorStop[];
    scaleMode?: 'FILL' | 'FIT' | 'TILE' | 'STRETCH';
    imageTransform?: Transform;
    scalingFactor?: number;
    imageRef?: string;
  }

  export interface Vector {
    x: number;
    y: number;
  }

  export interface ColorStop {
    position: number;
    color: Color;
  }

  export interface Transform {
    m00: number;
    m01: number;
    m02: number;
    m10: number;
    m11: number;
    m12: number;
  }

  export type BlendMode =
    | 'PASS_THROUGH'
    | 'NORMAL'
    | 'DARKEN'
    | 'MULTIPLY'
    | 'LINEAR_BURN'
    | 'COLOR_BURN'
    | 'LIGHTEN'
    | 'SCREEN'
    | 'LINEAR_DODGE'
    | 'COLOR_DODGE'
    | 'OVERLAY'
    | 'SOFT_LIGHT'
    | 'HARD_LIGHT'
    | 'DIFFERENCE'
    | 'EXCLUSION'
    | 'HUE'
    | 'SATURATION'
    | 'COLOR'
    | 'LUMINOSITY';

  export interface Effect {
    type: 'INNER_SHADOW' | 'DROP_SHADOW' | 'LAYER_BLUR' | 'BACKGROUND_BLUR';
    visible?: boolean;
    radius: number;
    color?: Color;
    blendMode?: BlendMode;
    offset?: Vector;
    spread?: number;
  }

  export interface Constraint {
    type: 'SCALE' | 'WIDTH' | 'HEIGHT';
    value: number;
  }

  export interface ExportSetting {
    suffix?: string;
    format: 'JPG' | 'PNG' | 'SVG' | 'PDF';
    constraint?: Constraint;
  }

  export interface Rectangle {
    x: number;
    y: number;
    width: number;
    height: number;
  }

  export interface LayoutConstraint {
    vertical: 'TOP' | 'BOTTOM' | 'CENTER' | 'TOP_BOTTOM' | 'SCALE';
    horizontal: 'LEFT' | 'RIGHT' | 'CENTER' | 'LEFT_RIGHT' | 'SCALE';
  }

  export type LayoutAlign = 'MIN' | 'CENTER' | 'MAX' | 'STRETCH';

  export type LayoutMode = 'NONE' | 'HORIZONTAL' | 'VERTICAL';

  export interface Node {
    id: string;
    name: string;
    visible?: boolean;
    type: NodeType;
    pluginData?: any;
    sharedPluginData?: any;
  }

  export type NodeType =
    | 'DOCUMENT'
    | 'CANVAS'
    | 'FRAME'
    | 'GROUP'
    | 'VECTOR'
    | 'BOOLEAN_OPERATION'
    | 'STAR'
    | 'LINE'
    | 'ELLIPSE'
    | 'REGULAR_POLYGON'
    | 'RECTANGLE'
    | 'TEXT'
    | 'SLICE'
    | 'COMPONENT'
    | 'COMPONENT_SET'
    | 'INSTANCE';

  export interface Component {
    key: string;
    name: string;
    description: string;
  }

  export interface Style {
    key: string;
    name: string;
    styleType: 'FILL' | 'TEXT' | 'EFFECT' | 'GRID';
    description?: string;
  }

  export interface Version {
    id: string;
    created_at: string;
    label: string;
    description: string;
    user: User;
  }

  export interface User {
    id: string;
    handle: string;
    img_url: string;
  }

  export interface Comment {
    id: string;
    file_key: string;
    parent_id: string;
    user: User;
    created_at: string;
    resolved_at: string | null;
    message: string;
    client_meta: Vector | FrameOffset;
    order_id?: number;
  }

  export interface FrameOffset {
    node_id: string;
    node_offset: Vector;
  }
}

// Component Definition Types
export interface ComponentDefinition {
  id: string;
  name: string;
  filePath: string;
  sourceCode: string;
  props: PropDefinition[];
  variants?: VariantDefinition[];
  styles: StyleDefinition;
  children: ComponentDefinition[];
}

export interface PropDefinition {
  name: string;
  type: PropType;
  required: boolean;
  defaultValue?: string | number | boolean;
  description?: string;
}

export type PropType =
  | 'string'
  | 'number'
  | 'boolean'
  | 'object'
  | 'array'
  | 'function'
  | 'node'
  | 'element'
  | 'custom';

export interface VariantDefinition {
  name: string;
  values: string[];
  defaultValue?: string;
}

export interface StyleDefinition {
  layout?: LayoutStyle;
  spacing?: SpacingStyle;
  typography?: TypographyStyle;
  colors?: ColorStyle;
  borders?: BorderStyle;
  effects?: EffectStyle[];
}

export interface LayoutStyle {
  display?: 'flex' | 'grid' | 'block' | 'inline' | 'inline-block';
  flexDirection?: 'row' | 'column' | 'row-reverse' | 'column-reverse';
  justifyContent?:
    | 'flex-start'
    | 'flex-end'
    | 'center'
    | 'space-between'
    | 'space-around'
    | 'space-evenly';
  alignItems?: 'flex-start' | 'flex-end' | 'center' | 'stretch' | 'baseline';
  gap?: number;
  width?: number | 'auto' | string;
  height?: number | 'auto' | string;
}

export interface SpacingStyle {
  padding?: {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
  };
  margin?: {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
  };
}

export interface TypographyStyle {
  fontFamily?: string;
  fontSize?: number;
  fontWeight?: number;
  lineHeight?: number;
  letterSpacing?: number;
  textAlign?: 'left' | 'center' | 'right' | 'justify';
  textTransform?: 'none' | 'uppercase' | 'lowercase' | 'capitalize';
  textDecoration?: 'none' | 'underline' | 'line-through';
}

export interface ColorStyle {
  background?: string;
  color?: string;
  borderColor?: string;
}

export interface BorderStyle {
  width?: number;
  style?: 'solid' | 'dashed' | 'dotted' | 'double' | 'none';
  radius?:
    | number
    | {
        topLeft?: number;
        topRight?: number;
        bottomRight?: number;
        bottomLeft?: number;
      };
}

export interface EffectStyle {
  type: 'shadow' | 'blur' | 'gradient';
  value: string;
}

// Design Token Types
export interface DesignTokens {
  colors: ColorTokens;
  typography: TypographyTokens;
  spacing: SpacingTokens;
  borderRadius: BorderRadiusTokens;
  shadows: ShadowTokens;
  breakpoints?: BreakpointTokens;
  transitions?: TransitionTokens;
}

export type ColorTokens = Record<string, string>;

export type TypographyTokens = Record<string, TypographyToken>;

export interface TypographyToken {
  fontFamily: string;
  fontSize: number;
  fontWeight: number;
  lineHeight: number;
  letterSpacing?: number;
}

export type SpacingTokens = Record<string, number>;

export type BorderRadiusTokens = Record<string, number>;

export type ShadowTokens = Record<string, string>;

export type BreakpointTokens = Record<string, number>;

export type TransitionTokens = Record<string, string>;

// Sync Metadata Types
export interface SyncMetadata {
  version: string;
  lastSync: string | null;
  figmaFileKey: string;
  components: ComponentSyncMetadata[];
  tokens: DesignTokens;
  conflicts?: ConflictMetadata[];
}

export interface ComponentSyncMetadata {
  id: string;
  name: string;
  componentId: string;
  figmaNodeId?: string;
  filePath: string;
  lastModified: string;
  syncStatus: SyncStatus;
  checksum?: string;
}

export type SyncStatus = 'synced' | 'modified' | 'new' | 'deleted' | 'conflict';

export interface ConflictMetadata {
  componentId: string;
  type: 'local_modified' | 'remote_modified' | 'both_modified' | 'deleted';
  localTimestamp: string;
  remoteTimestamp: string;
  description: string;
}

// Generator Output Types
export interface GeneratorOutput {
  plugin?: PluginOutput;
  storyToDesign?: StoryToDesignOutput;
  tokens?: TokenOutput;
  metadata?: SyncMetadata;
}

export interface PluginOutput {
  manifest: PluginManifest;
  code: string;
  ui: string;
  data: PluginData;
}

export interface PluginManifest {
  name: string;
  id: string;
  api: string;
  main: string;
  ui: string;
  capabilities: string[];
  editorType: string[];
}

export interface PluginData {
  version: string;
  components: ComponentDefinition[];
  tokens: DesignTokens;
}

export interface StoryToDesignOutput {
  stories: StoryDefinition[];
  config: StoryConfig;
}

export interface StoryDefinition {
  id: string;
  title: string;
  component: string;
  parameters: StoryParameters;
  args: Record<string, any>;
}

export interface StoryParameters {
  layout?: 'centered' | 'fullscreen' | 'padded';
  design: {
    type: 'figma';
    url?: string;
  };
  docs?: {
    description?: {
      component?: string;
      story?: string;
    };
  };
}

export interface StoryConfig {
  framework: 'react' | 'vue' | 'angular' | 'svelte';
  stories: string;
  addons: string[];
  features?: {
    design?: {
      type: 'story-to-design';
      url: string;
    };
  };
}

export interface TokenOutput {
  format: 'typescript' | 'json' | 'css' | 'scss';
  content: string;
  filePath: string;
}

// Configuration Types
export interface GeneratorConfig {
  api: APIConfig;
  components: ComponentConfig;
  output: OutputConfig;
  sync: SyncConfig;
  tokens?: DesignTokens;
}

export interface APIConfig {
  accessToken: string;
  fileKey: string;
  rateLimit?: RateLimitConfig;
}

export interface RateLimitConfig {
  maxRequests: number;
  perMilliseconds: number;
}

export interface ComponentConfig {
  paths: string[];
  exclude?: string[];
  include?: string[];
}

export interface OutputConfig {
  directory: string;
  format: 'plugin' | 'story-to-design' | 'both';
  cleanBefore?: boolean;
}

export interface SyncConfig {
  metaFilePath: string;
  autoSync: boolean;
  conflictResolution: 'local' | 'remote' | 'manual';
  backupBefore?: boolean;
}

// Error Types
export class FigmaGeneratorError extends Error {
  constructor(
    message: string,
    public code: ErrorCode,
    public cause?: unknown,
  ) {
    super(message);
    this.name = 'FigmaGeneratorError';
  }
}

export type ErrorCode =
  | 'API_ERROR'
  | 'AUTH_ERROR'
  | 'RATE_LIMIT'
  | 'PARSE_ERROR'
  | 'FILE_NOT_FOUND'
  | 'INVALID_CONFIG'
  | 'SYNC_CONFLICT'
  | 'NETWORK_ERROR'
  | 'UNKNOWN_ERROR';

// Utility Types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type RequireAtLeastOne<T, Keys extends keyof T = keyof T> = Pick<T, Exclude<keyof T, Keys>> &
  {
    [K in Keys]-?: Required<Pick<T, K>> & Partial<Pick<T, Exclude<Keys, K>>>;
  }[Keys];

export type Promisable<T> = T | Promise<T>;
