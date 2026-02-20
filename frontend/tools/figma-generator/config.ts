/**
 * Figma Generator Configuration
 *
 * Central configuration for Figma design sync and generation
 */

export interface FigmaConfig {
  // API Configuration
  api: {
    accessToken: string;
    fileKey: string;
    rateLimit?: {
      maxRequests: number;
      perMilliseconds: number;
    };
  };

  // Component Paths
  components: {
    paths: string[];
    exclude: string[];
  };

  // Output Configuration
  output: {
    directory: string;
    format: 'plugin' | 'story-to-design' | 'both';
  };

  // Story to Design Integration
  storyToDesign?: {
    url: string;
    enabled: boolean;
  };

  // Design Tokens
  tokens: {
    colors: Record<string, string>;
    spacing: Record<string, number>;
    typography: Record<string, TypographyToken>;
    borderRadius: Record<string, number>;
    shadows: Record<string, string>;
  };

  // Sync Configuration
  sync: {
    metaFilePath: string;
    autoSync: boolean;
    conflictResolution: 'local' | 'remote' | 'manual';
  };
}

export interface TypographyToken {
  fontFamily: string;
  fontSize: number;
  fontWeight: number;
  lineHeight: number;
  letterSpacing?: number;
}

/**
 * Load configuration from environment variables and defaults
 */
export function loadFigmaConfig(): FigmaConfig {
  const accessToken = process.env.FIGMA_ACCESS_TOKEN;
  const fileKey = process.env.FIGMA_FILE_KEY;

  if (!accessToken) {
    throw new Error('FIGMA_ACCESS_TOKEN environment variable is required');
  }

  if (!fileKey) {
    throw new Error('FIGMA_FILE_KEY environment variable is required');
  }

  return {
    api: {
      accessToken,
      fileKey,
      rateLimit: {
        maxRequests: parseInt(process.env.FIGMA_RATE_LIMIT_REQUESTS || '100', 10),
        perMilliseconds: parseInt(process.env.FIGMA_RATE_LIMIT_MS || '60000', 10),
      },
    },

    components: {
      exclude: ['**/node_modules/**', '**/*.test.tsx', '**/*.spec.tsx', '**/*.stories.tsx'],
      paths: [
        'packages/ui/src/components/**/*.tsx',
        'apps/web/src/components/**/*.tsx',
        'apps/desktop/src/components/**/*.tsx',
      ],
    },

    output: {
      directory: process.env.FIGMA_OUTPUT_DIR || '.figma-output',
      format: (process.env.FIGMA_OUTPUT_FORMAT as 'plugin' | 'story-to-design' | 'both') || 'both',
    },

    storyToDesign: process.env.STORY_TO_DESIGN_URL
      ? {
          enabled: process.env.STORY_TO_DESIGN_ENABLED !== 'false',
          url: process.env.STORY_TO_DESIGN_URL,
        }
      : undefined,

    sync: {
      autoSync: process.env.FIGMA_AUTO_SYNC === 'true',
      conflictResolution:
        (process.env.FIGMA_CONFLICT_RESOLUTION as 'local' | 'remote' | 'manual') || 'manual',
      metaFilePath: '.trace/.meta/designs.yaml',
    },

    tokens: getDefaultTokens(),
  };
}

/**
 * Get default design tokens based on TracerTM design system
 */
function getDefaultTokens() {
  return {
    borderRadius: {
      '2xl': 16,
      '3xl': 24,
      DEFAULT: 4,
      full: 9999,
      lg: 8,
      md: 6,
      none: 0,
      sm: 2,
      xl: 12,
    },

    colors: {
      // Primary colors
      'primary-50': '#eff6ff',
      'primary-100': '#dbeafe',
      'primary-200': '#bfdbfe',
      'primary-300': '#93c5fd',
      'primary-400': '#60a5fa',
      'primary-500': '#3b82f6',
      'primary-600': '#2563eb',
      'primary-700': '#1d4ed8',
      'primary-800': '#1e40af',
      'primary-900': '#1e3a8a',

      // Gray scale
      'gray-50': '#f9fafb',
      'gray-100': '#f3f4f6',
      'gray-200': '#e5e7eb',
      'gray-300': '#d1d5db',
      'gray-400': '#9ca3af',
      'gray-500': '#6b7280',
      'gray-600': '#4b5563',
      'gray-700': '#374151',
      'gray-800': '#1f2937',
      'gray-900': '#111827',

      // Semantic colors
      'success-500': '#10b981',
      'success-600': '#059669',
      'error-500': '#ef4444',
      'error-600': '#dc2626',
      'warning-500': '#f59e0b',
      'warning-600': '#d97706',
      'info-500': '#3b82f6',
      'info-600': '#2563eb',

      // Special colors
      white: '#ffffff',
      black: '#000000',
      transparent: 'transparent',
    },

    shadows: {
      '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
      DEFAULT: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
      inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
      lg: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
      md: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
      none: 'none',
      sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
      xl: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
      xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    },

    spacing: {
      '0': 0,
      '0.5': 2,
      '1': 4,
      '1.5': 6,
      '2': 8,
      '2.5': 10,
      '3': 12,
      '3.5': 14,
      '4': 16,
      '5': 20,
      '6': 24,
      '7': 28,
      '8': 32,
      '9': 36,
      '10': 40,
      '11': 44,
      '12': 48,
      '14': 56,
      '16': 64,
      '20': 80,
      '24': 96,
      '28': 112,
      '32': 128,
      '36': 144,
      '40': 160,
      '44': 176,
      '48': 192,
      '52': 208,
      '56': 224,
      '60': 240,
      '64': 256,
      '72': 288,
      '80': 320,
      '96': 384,
      px: 1,
    },

    typography: {
      // Display
      'display-2xl': {
        fontFamily: 'Inter',
        fontSize: 72,
        fontWeight: 700,
        letterSpacing: -2,
        lineHeight: 90,
      },
      'display-xl': {
        fontFamily: 'Inter',
        fontSize: 60,
        fontWeight: 700,
        letterSpacing: -2,
        lineHeight: 72,
      },
      'display-lg': {
        fontFamily: 'Inter',
        fontSize: 48,
        fontWeight: 700,
        letterSpacing: -2,
        lineHeight: 60,
      },
      'display-md': {
        fontFamily: 'Inter',
        fontSize: 36,
        fontWeight: 700,
        letterSpacing: -2,
        lineHeight: 44,
      },
      'display-sm': {
        fontFamily: 'Inter',
        fontSize: 30,
        fontWeight: 600,
        lineHeight: 38,
      },
      'display-xs': {
        fontFamily: 'Inter',
        fontSize: 24,
        fontWeight: 600,
        lineHeight: 32,
      },

      // Text
      'text-xl': {
        fontFamily: 'Inter',
        fontSize: 20,
        fontWeight: 400,
        lineHeight: 30,
      },
      'text-lg': {
        fontFamily: 'Inter',
        fontSize: 18,
        fontWeight: 400,
        lineHeight: 28,
      },
      'text-md': {
        fontFamily: 'Inter',
        fontSize: 16,
        fontWeight: 400,
        lineHeight: 24,
      },
      'text-sm': {
        fontFamily: 'Inter',
        fontSize: 14,
        fontWeight: 400,
        lineHeight: 20,
      },
      'text-xs': {
        fontFamily: 'Inter',
        fontSize: 12,
        fontWeight: 400,
        lineHeight: 18,
      },
    },
  };
}

/**
 * Validate configuration
 */
export function validateConfig(config: FigmaConfig): string[] {
  const errors: string[] = [];

  if (!config.api.accessToken) {
    errors.push('API access token is required');
  }

  if (!config.api.fileKey) {
    errors.push('Figma file key is required');
  }

  if (config.components.paths.length === 0) {
    errors.push('At least one component path must be specified');
  }

  if (!config.output.directory) {
    errors.push('Output directory is required');
  }

  return errors;
}

/**
 * Get environment variable template
 */
export function getEnvTemplate(): string {
  return `# Figma Integration Configuration

# Required: Your Figma personal access token
# Get it from: https://www.figma.com/developers/api#authentication
FIGMA_ACCESS_TOKEN=your_figma_access_token_here

# Required: The file key from your Figma file URL
# Example: https://www.figma.com/file/ABC123/Design-System
# File key would be: ABC123
FIGMA_FILE_KEY=your_file_key_here

# Optional: story.to.design integration
STORY_TO_DESIGN_URL=https://api.story.to.design/v1/sync
STORY_TO_DESIGN_ENABLED=true

# Optional: Rate limiting
FIGMA_RATE_LIMIT_REQUESTS=100
FIGMA_RATE_LIMIT_MS=60000

# Optional: Output configuration
FIGMA_OUTPUT_DIR=.figma-output
FIGMA_OUTPUT_FORMAT=both  # plugin | story-to-design | both

# Optional: Sync configuration
FIGMA_AUTO_SYNC=false
FIGMA_CONFLICT_RESOLUTION=manual  # local | remote | manual
`;
}
