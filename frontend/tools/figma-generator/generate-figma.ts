/**
 * Figma Generator
 *
 * Main generator that reads component definitions and generates Figma-compatible output
 * Supports both Figma plugin format and story.to.design API pattern
 */

import { glob } from 'glob';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';

import type { ComponentDefinition, DesignToken } from './code-to-design';

import { ComponentParser } from './code-to-design';

export interface GeneratorConfig {
  componentPaths: string[];
  outputDir: string;
  outputFormat: 'plugin' | 'story-to-design' | 'both';
  tokens?: DesignToken;
  figmaFileKey?: string;
}

export interface FigmaPluginOutput {
  version: string;
  components: FigmaPluginComponent[];
  tokens: DesignToken;
}

export interface FigmaPluginComponent {
  id: string;
  name: string;
  description: string;
  type: 'COMPONENT';
  children: FigmaPluginNode[];
}

export interface FigmaPluginNode {
  id: string;
  name: string;
  type: string;
  properties?: Record<string, unknown>;
  styles?: Record<string, unknown>;
  children?: FigmaPluginNode[];
}

export interface StoryToDesignOutput {
  stories: StoryDefinition[];
  config: StoryToDesignConfig;
}

export interface StoryDefinition {
  id: string;
  title: string;
  component: string;
  parameters: {
    design: {
      type: 'figma';
      url?: string;
    };
  };
  args: Record<string, unknown>;
}

export interface StoryToDesignConfig {
  framework: 'react';
  stories: string;
  addons: string[];
  features: {
    design: {
      type: 'story-to-design';
      url: string;
    };
  };
}

/**
 * Main Figma Generator class
 */
export class FigmaGenerator {
  private config: GeneratorConfig;
  private parser: ComponentParser;

  constructor(config: GeneratorConfig) {
    this.config = config;
    this.parser = new ComponentParser(config.tokens);
  }

  /**
   * Generate Figma-compatible output from components
   */
  async generate(): Promise<void> {
    // Find all component files
    const componentFiles = await this.findComponentFiles();

    // Parse components
    const definitions = await this.parseComponents(componentFiles);

    // Generate output based on format
    if (this.config.outputFormat === 'plugin' || this.config.outputFormat === 'both') {
      await this.generatePluginOutput(definitions);
    }

    if (this.config.outputFormat === 'story-to-design' || this.config.outputFormat === 'both') {
      await this.generateStoryToDesignOutput(definitions);
    }
  }

  /**
   * Find all component files matching configured paths
   */
  private async findComponentFiles(): Promise<string[]> {
    const files: string[] = [];

    for (const pattern of this.config.componentPaths) {
      const matches = await glob(pattern, {
        ignore: ['**/node_modules/**', '**/*.test.tsx', '**/*.spec.tsx'],
      });
      files.push(...matches);
    }

    return files;
  }

  /**
   * Parse all component files
   */
  private async parseComponents(files: string[]): Promise<ComponentDefinition[]> {
    const definitions: ComponentDefinition[] = [];

    for (const file of files) {
      try {
        const componentDefs = await this.parser.parseFile(file);
        definitions.push(...componentDefs);
      } catch (error) {}
    }

    return definitions;
  }

  /**
   * Generate Figma plugin compatible JSON
   */
  private async generatePluginOutput(definitions: ComponentDefinition[]): Promise<void> {
    const output: FigmaPluginOutput = {
      components: definitions.map((def) => this.toPluginComponent(def)),
      tokens: this.config.tokens || this.getDefaultTokens(),
      version: '1.0.0',
    };

    const outputPath = path.join(this.config.outputDir, 'figma-plugin.json');
    await fs.mkdir(path.dirname(outputPath), { recursive: true });
    await fs.writeFile(outputPath, JSON.stringify(output, null, 2));

    // Also generate plugin manifest
    await this.generatePluginManifest(outputPath);
  }

  /**
   * Generate story.to.design compatible output
   */
  private async generateStoryToDesignOutput(definitions: ComponentDefinition[]): Promise<void> {
    const output: StoryToDesignOutput = {
      config: {
        addons: ['@storybook/addon-docs'],
        features: {
          design: {
            type: 'story-to-design',
            url: this.config.figmaFileKey
              ? `https://www.figma.com/file/${this.config.figmaFileKey}`
              : 'https://story.to.design',
          },
        },
        framework: 'react',
        stories: '../src/**/*.stories.tsx',
      },
      stories: definitions.map((def) => this.toStoryDefinition(def)),
    };

    const outputPath = path.join(this.config.outputDir, 'story-to-design.json');
    await fs.mkdir(path.dirname(outputPath), { recursive: true });
    await fs.writeFile(outputPath, JSON.stringify(output, null, 2));

    // Generate Storybook stories
    await this.generateStorybookStories(definitions);
  }

  /**
   * Convert ComponentDefinition to Figma plugin format
   */
  private toPluginComponent(def: ComponentDefinition): FigmaPluginComponent {
    return {
      children: def.nodes.map((node) => ({
        children: node.children?.map((child) => ({
          id: child.id,
          name: child.name,
          properties: child.properties,
          styles: child.styles,
          type: child.type,
        })),
        id: node.id,
        name: node.name,
        properties: node.properties,
        styles: node.styles,
        type: node.type,
      })),
      description: `Generated from ${path.basename(def.filePath)}`,
      id: this.generateComponentId(def.name),
      name: def.name,
      type: 'COMPONENT',
    };
  }

  /**
   * Convert ComponentDefinition to Story definition
   */
  private toStoryDefinition(def: ComponentDefinition): StoryDefinition {
    return {
      args: this.extractDefaultArgs(def),
      component: def.name,
      id: this.generateComponentId(def.name),
      parameters: {
        design: {
          type: 'figma',
          url: this.config.figmaFileKey
            ? `https://www.figma.com/file/${this.config.figmaFileKey}`
            : undefined,
        },
      },
      title: `Components/${def.name}`,
    };
  }

  /**
   * Generate Figma plugin manifest.json
   */
  private async generatePluginManifest(dataPath: string): Promise<void> {
    const manifest = {
      api: '1.0.0',
      capabilities: ['read', 'write'],
      editorType: ['figma'],
      id: 'tracertm-design-sync',
      main: 'code.js',
      name: 'TracerTM Design Sync',
      networkAccess: {
        allowedDomains: ['none'],
        devAllowedDomains: ['*'],
      },
      ui: 'ui.html',
    };

    const manifestPath = path.join(this.config.outputDir, 'manifest.json');
    await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2));

    // Generate basic plugin code
    await this.generatePluginCode(dataPath);
  }

  /**
   * Generate Figma plugin code.js
   */
  private async generatePluginCode(dataPath: string): Promise<void> {
    const code = `// TracerTM Figma Plugin
// Auto-generated - Do not edit manually

figma.showUI(__html__, { width: 400, height: 600 });

figma.ui.onmessage = async (msg) => {
  if (msg.type === 'import-components') {
    try {
      const data = await fetch('${dataPath}').then(r => r.json());

      for (const component of data.components) {
        const frame = figma.createComponent();
        frame.name = component.name;

        // Apply component structure
        await importComponent(frame, component);
      }

      figma.closePlugin('Components imported successfully!');
    } catch (error) {
      figma.closePlugin('Error importing components: ' + error.message);
    }
  }
};

async function importComponent(parent, data) {
  for (const child of data.children || []) {
    let node;

    switch (child.type) {
      case 'FRAME':
        node = figma.createFrame();
        break;
      case 'TEXT':
        node = figma.createText();
        break;
      case 'RECTANGLE':
        node = figma.createRectangle();
        break;
      default:
        node = figma.createFrame();
    }

    node.name = child.name;

    // Apply styles
    if (child.styles) {
      applyStyles(node, child.styles);
    }

    parent.appendChild(node);

    // Recursively import children
    if (child.children) {
      await importComponent(node, child);
    }
  }
}

function applyStyles(node, styles) {
  if (styles.backgroundColor) {
    const color = hexToRgb(styles.backgroundColor);
    node.fills = [{ type: 'SOLID', color }];
  }

  if (styles.cornerRadius) {
    node.cornerRadius = styles.cornerRadius;
  }

  if (styles.padding) {
    node.paddingLeft = styles.padding.left || 0;
    node.paddingRight = styles.padding.right || 0;
    node.paddingTop = styles.padding.top || 0;
    node.paddingBottom = styles.padding.bottom || 0;
  }

  if (styles.layoutMode) {
    node.layoutMode = styles.layoutMode;
  }
}

function hexToRgb(hex) {
  const result = /^#?([a-f\\d]{2})([a-f\\d]{2})([a-f\\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16) / 255,
    g: parseInt(result[2], 16) / 255,
    b: parseInt(result[3], 16) / 255
  } : { r: 0, g: 0, b: 0 };
}
`;

    const codePath = path.join(this.config.outputDir, 'code.js');
    await fs.writeFile(codePath, code);

    // Generate basic UI
    await this.generatePluginUI();
  }

  /**
   * Generate Figma plugin ui.html
   */
  private async generatePluginUI(): Promise<void> {
    const html = `<!DOCTYPE html>
<html>
<head>
  <style>
    body {
      font-family: Inter, sans-serif;
      padding: 20px;
    }
    button {
      width: 100%;
      padding: 12px;
      background: #0066FF;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      cursor: pointer;
    }
    button:hover {
      background: #0052CC;
    }
    .info {
      margin-bottom: 20px;
      color: #666;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div class="info">
    <h2>TracerTM Design Sync</h2>
    <p>Import components from your codebase to Figma</p>
  </div>
  <button id="import">Import Components</button>

  <script>
    document.getElementById('import').onclick = () => {
      parent.postMessage({ pluginMessage: { type: 'import-components' } }, '*');
    };
  </script>
</body>
</html>`;

    const uiPath = path.join(this.config.outputDir, 'ui.html');
    await fs.writeFile(uiPath, html);
  }

  /**
   * Generate Storybook stories for each component
   */
  private async generateStorybookStories(definitions: ComponentDefinition[]): Promise<void> {
    const storiesDir = path.join(this.config.outputDir, 'stories');
    await fs.mkdir(storiesDir, { recursive: true });

    for (const def of definitions) {
      const story = this.generateStory(def);
      const storyPath = path.join(storiesDir, `${def.name}.stories.tsx`);
      await fs.writeFile(storyPath, story);
    }
  }

  /**
   * Generate individual Storybook story file
   */
  private generateStory(def: ComponentDefinition): string {
    const imports = `import type { Meta, StoryObj } from '@storybook/react';
import { ${def.name} } from '${def.filePath.replace(/\.(tsx|ts)$/, '')}';

`;

    const meta = `const meta: Meta<typeof ${def.name}> = {
  title: 'Components/${def.name}',
  component: ${def.name},
  parameters: {
    layout: 'centered',
    design: {
      type: 'figma',
      url: '${this.config.figmaFileKey ? `https://www.figma.com/file/${this.config.figmaFileKey}` : ''}',
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ${def.name}>;

`;

    const defaultStory = `export const Default: Story = {
  args: ${JSON.stringify(this.extractDefaultArgs(def), null, 4)},
};

`;

    return imports + meta + defaultStory;
  }

  /**
   * Extract default args from component props
   */
  private extractDefaultArgs(def: ComponentDefinition): Record<string, unknown> {
    const args: Record<string, unknown> = {};

    for (const prop of def.props) {
      if (prop.defaultValue) {
        try {
          args[prop.name] = JSON.parse(prop.defaultValue);
        } catch {
          args[prop.name] = prop.defaultValue;
        }
      } else {
        // Provide sensible defaults based on type
        switch (prop.type) {
          case 'string': {
            args[prop.name] = `Sample ${prop.name}`;
            break;
          }
          case 'number': {
            args[prop.name] = 0;
            break;
          }
          case 'boolean': {
            args[prop.name] = false;
            break;
          }
        }
      }
    }

    return args;
  }

  private generateComponentId(name: string): string {
    return name.toLowerCase().replaceAll(/[^a-z0-9]/g, '-');
  }

  private getDefaultTokens(): DesignToken {
    return {
      borderRadius: {
        lg: 16,
        md: 8,
        sm: 4,
      },
      colors: {
        error: '#EF4444',
        primary: '#0066FF',
        secondary: '#6B7280',
        success: '#10B981',
        warning: '#F59E0B',
      },
      shadows: {
        md: '0 4px 6px rgba(0, 0, 0, 0.1)',
        sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
      },
      spacing: {
        lg: 24,
        md: 16,
        sm: 8,
        xl: 32,
        xs: 4,
      },
      typography: {
        body: {
          fontFamily: 'Inter',
          fontSize: 16,
          fontWeight: 400,
          lineHeight: 24,
        },
        heading: {
          fontFamily: 'Inter',
          fontSize: 24,
          fontWeight: 600,
          lineHeight: 32,
        },
      },
    };
  }
}

/**
 * Run the generator with CLI arguments
 */
export async function runGenerator(): Promise<void> {
  const config: GeneratorConfig = {
    componentPaths: ['packages/ui/src/components/**/*.tsx', 'apps/*/src/components/**/*.tsx'],
    outputDir: '.figma-output',
    outputFormat: 'both',
  };

  const generator = new FigmaGenerator(config);
  await generator.generate();
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
}
