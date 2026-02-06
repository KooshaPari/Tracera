/**
 * Design Sync
 *
 * Bidirectional sync between code and Figma designs
 * - Push component changes to story.to.design
 * - Pull Figma design updates
 * - Update .trace/.meta/designs.yaml
 */

import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import * as yaml from 'yaml';

import type { ComponentDefinition } from './code-to-design';
import type { FigmaClient, Variables } from './figma-api-client';

import { createFigmaClient } from './figma-api-client';
import { FigmaGenerator } from './generate-figma';

export interface SyncConfig {
  figmaAccessToken: string;
  figmaFileKey: string;
  storyToDesignUrl?: string;
  componentPaths: string[];
  metaFilePath: string;
  outputDir: string;
}

export interface DesignMetadata {
  version: string;
  lastSync: string;
  figmaFileKey: string;
  components: ComponentMetadata[];
  tokens: Variables;
}

export interface ComponentMetadata {
  name: string;
  componentId: string;
  figmaNodeId?: string;
  filePath: string;
  lastModified: string;
  syncStatus: 'synced' | 'modified' | 'new' | 'deleted';
}

export interface SyncResult {
  pushed: number;
  pulled: number;
  conflicts: string[];
  errors: string[];
}

/**
 * Design Synchronization Manager
 */
export class DesignSync {
  private config: SyncConfig;
  private client: FigmaClient;
  private metadata: DesignMetadata | null = null;

  constructor(config: SyncConfig) {
    this.config = config;
    this.client = createFigmaClient({
      personalAccessToken: config.figmaAccessToken,
    });
  }

  /**
   * Perform full bidirectional sync
   */
  async sync(direction: 'push' | 'pull' | 'both' = 'both'): Promise<SyncResult> {
    const result: SyncResult = {
      conflicts: [],
      errors: [],
      pulled: 0,
      pushed: 0,
    };

    try {
      // Load existing metadata
      await this.loadMetadata();

      if (direction === 'push' || direction === 'both') {
        const pushResult = await this.pushToFigma();
        result.pushed = pushResult;
      }

      if (direction === 'pull' || direction === 'both') {
        const pullResult = await this.pullFromFigma();
        result.pulled = pullResult;
      }

      // Save updated metadata
      await this.saveMetadata();
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      result.errors.push(errorMsg);
    }

    return result;
  }

  /**
   * Push local component changes to Figma
   */
  private async pushToFigma(): Promise<number> {
    // Generate components
    const generator = new FigmaGenerator({
      componentPaths: this.config.componentPaths,
      figmaFileKey: this.config.figmaFileKey,
      outputDir: this.config.outputDir,
      outputFormat: 'plugin',
    });

    await generator.generate();

    // Get component definitions
    const components = await this.getLocalComponents();

    // Update metadata with component info
    for (const component of components) {
      await this.updateComponentMetadata(component);
    }

    return components.length;
  }

  /**
   * Pull design updates from Figma
   */
  private async pullFromFigma(): Promise<number> {
    // Get Figma file data
    const _file = await this.client.getFile(this.config.figmaFileKey);

    // Get design tokens/variables
    const variables = await this.client.getVariables(this.config.figmaFileKey);

    // Update metadata
    if (!this.metadata) {
      this.metadata = this.createEmptyMetadata();
    }

    this.metadata.tokens = variables;
    this.metadata.lastSync = new Date().toISOString();

    // Get components from Figma
    const figmaComponents = await this.client.getComponents(this.config.figmaFileKey);

    // Match with local components
    let pulledCount = 0;
    for (const figmaComponent of figmaComponents) {
      const localComponent = this.metadata.components.find(
        (c) => c.figmaNodeId === figmaComponent.id,
      );

      if (localComponent) {
        // Update existing component metadata
        localComponent.syncStatus = 'synced';
        pulledCount += 1;
      } else {
        // New component from Figma
        this.metadata.components.push({
          componentId: this.generateComponentId(figmaComponent.name),
          figmaNodeId: figmaComponent.id,
          filePath: '',
          lastModified: new Date().toISOString(),
          name: figmaComponent.name,
          syncStatus: 'new',
        });
        pulledCount += 1;
      }
    }

    return pulledCount;
  }

  /**
   * Get local component definitions
   */
  private async getLocalComponents(): Promise<ComponentDefinition[]> {
    const { glob } = await import('glob');
    const files: string[] = [];

    for (const pattern of this.config.componentPaths) {
      const matches = await glob(pattern, {
        ignore: ['**/node_modules/**', '**/*.test.tsx', '**/*.spec.tsx'],
      });
      files.push(...matches);
    }

    // This would use ComponentParser in a real implementation
    // For now, return empty array
    return [];
  }

  /**
   * Update component metadata
   */
  private async updateComponentMetadata(component: ComponentDefinition): Promise<void> {
    if (!this.metadata) {
      this.metadata = this.createEmptyMetadata();
    }

    const existingIndex = this.metadata.components.findIndex(
      (c) => c.componentId === this.generateComponentId(component.name),
    );

    const stats = await fs.stat(component.filePath);
    const metadata: ComponentMetadata = {
      componentId: this.generateComponentId(component.name),
      filePath: component.filePath,
      lastModified: stats.mtime.toISOString(),
      name: component.name,
      syncStatus: 'synced',
    };

    if (existingIndex !== -1) {
      this.metadata.components[existingIndex] = metadata;
    } else {
      this.metadata.components.push(metadata);
    }
  }

  /**
   * Load metadata from YAML file
   */
  private async loadMetadata(): Promise<void> {
    try {
      const content = await fs.readFile(this.config.metaFilePath, 'utf8');
      this.metadata = yaml.parse(content) as DesignMetadata;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        this.metadata = this.createEmptyMetadata();
      } else {
        throw error;
      }
    }
  }

  /**
   * Save metadata to YAML file
   */
  private async saveMetadata(): Promise<void> {
    if (!this.metadata) {
      return;
    }

    const content = yaml.stringify(this.metadata);
    await fs.mkdir(path.dirname(this.config.metaFilePath), { recursive: true });
    await fs.writeFile(this.config.metaFilePath, content, 'utf8');
  }

  /**
   * Create empty metadata structure
   */
  private createEmptyMetadata(): DesignMetadata {
    return {
      components: [],
      figmaFileKey: this.config.figmaFileKey,
      lastSync: new Date().toISOString(),
      tokens: {
        borderRadius: {},
        colors: {},
        shadows: {},
        spacing: {},
        typography: {},
      },
      version: '1.0.0',
    };
  }

  /**
   * Generate component ID from name
   */
  private generateComponentId(name: string): string {
    return name.toLowerCase().replaceAll(/[^a-z0-9]/g, '-');
  }

  /**
   * Detect conflicts between local and Figma
   */
  async detectConflicts(): Promise<string[]> {
    const conflicts: string[] = [];

    if (!this.metadata) {
      await this.loadMetadata();
    }

    // Get Figma components
    const figmaComponents = await this.client.getComponents(this.config.figmaFileKey);

    for (const component of this.metadata?.components || []) {
      if (!component.figmaNodeId) {
        continue;
      }

      const figmaComponent = figmaComponents.find((c) => c.id === component.figmaNodeId);

      if (figmaComponent) {
        // Check if local file was modified after last sync
        try {
          const stats = await fs.stat(component.filePath);
          const lastSync = new Date(this.metadata?.lastSync || 0);

          if (stats.mtime > lastSync) {
            conflicts.push(`${component.name}: Modified locally after last sync with Figma`);
          }
        } catch {
          // File doesn't exist locally
          conflicts.push(`${component.name}: Exists in Figma but not found locally`);
        }
      } else {
        conflicts.push(`${component.name}: Deleted from Figma`);
      }
    }

    return conflicts;
  }

  /**
   * Export design tokens to code
   */
  async exportTokens(outputPath: string): Promise<void> {
    const variables = await this.client.getVariables(this.config.figmaFileKey);

    // Generate TypeScript token file
    const tokenCode = this.generateTokenCode(variables);
    await fs.writeFile(outputPath, tokenCode);
  }

  /**
   * Generate TypeScript code for design tokens
   */
  private generateTokenCode(variables: Variables): string {
    return `/**
 * Design Tokens
 * Auto-generated from Figma - Do not edit manually
 * Last updated: ${new Date().toISOString()}
 */

export const colors = ${JSON.stringify(variables.colors, null, 2)} as const;

export const typography = ${JSON.stringify(variables.typography, null, 2)} as const;

export const spacing = ${JSON.stringify(variables.spacing, null, 2)} as const;

export const borderRadius = ${JSON.stringify(variables.borderRadius, null, 2)} as const;

export const shadows = ${JSON.stringify(variables.shadows, null, 2)} as const;

export type ColorToken = keyof typeof colors;
export type TypographyToken = keyof typeof typography;
export type SpacingToken = keyof typeof spacing;
export type BorderRadiusToken = keyof typeof borderRadius;
export type ShadowToken = keyof typeof shadows;
`;
  }

  /**
   * Upload story.to.design integration
   */
  async uploadToStoryToDesign(): Promise<void> {
    if (!this.config.storyToDesignUrl) {
      return;
    }

    // Generate story.to.design output
    const generator = new FigmaGenerator({
      componentPaths: this.config.componentPaths,
      figmaFileKey: this.config.figmaFileKey,
      outputDir: this.config.outputDir,
      outputFormat: 'story-to-design',
    });

    await generator.generate();

    // Read generated output
    const outputPath = path.join(this.config.outputDir, 'story-to-design.json');
    const output = await fs.readFile(outputPath, 'utf8');

    // Upload to story.to.design API
    try {
      const response = await fetch(this.config.storyToDesignUrl, {
        body: output,
        headers: {
          'Content-Type': 'application/json',
        },
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }
    } catch (error) {
      throw error;
    }
  }
}

/**
 * Load configuration from environment and files
 */
async function loadConfig(): Promise<SyncConfig> {
  const figmaAccessToken = process.env.FIGMA_ACCESS_TOKEN;
  const figmaFileKey = process.env.FIGMA_FILE_KEY;

  if (!(figmaAccessToken && figmaFileKey)) {
    throw new Error('FIGMA_ACCESS_TOKEN and FIGMA_FILE_KEY must be set');
  }

  return {
    componentPaths: ['packages/ui/src/components/**/*.tsx', 'apps/*/src/components/**/*.tsx'],
    figmaAccessToken,
    figmaFileKey,
    metaFilePath: '.trace/.meta/designs.yaml',
    outputDir: '.figma-output',
    storyToDesignUrl: process.env.STORY_TO_DESIGN_URL,
  };
}

/**
 * CLI entry point
 */
async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const command = args[0] || 'sync';

  const config = await loadConfig();
  const sync = new DesignSync(config);

  switch (command) {
    case 'push': {
      await sync.sync('push');
      break;
    }

    case 'pull': {
      await sync.sync('pull');
      break;
    }

    case 'sync': {
      await sync.sync('both');
      break;
    }

    case 'conflicts': {
      const conflicts = await sync.detectConflicts();
      if (conflicts.length > 0) {
        for (const conflict of conflicts) {
        }
        process.exit(1);
      } else {
      }
      break;
    }

    case 'export-tokens': {
      const outputPath = args[1] || 'src/design-tokens.ts';
      await sync.exportTokens(outputPath);
      break;
    }

    case 'upload': {
      await sync.uploadToStoryToDesign();
      break;
    }

    default: {
      console.log(`Unknown command: ${command}`);
      console.log('Available commands: push, pull, sync, conflicts, export-tokens, upload');
      process.exit(1);
    }
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    process.exit(1);
  });
}

export { DesignSync };
