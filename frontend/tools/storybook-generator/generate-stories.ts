#!/usr/bin/env bun

/**
 * TraceRTM Storybook Story Generator
 * Automatically generates CSF 3.0 stories for React components
 *
 * Usage:
 *   bun run generate:stories              # Generate all stories
 *   bun run generate:stories --force      # Overwrite existing stories
 *   bun run generate:stories --component Button  # Generate for specific component
 */

import { globSync } from 'glob';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { basename, dirname, join, relative } from 'node:path';
import { parseArgs } from 'node:util';

import type { ComponentInfo } from './analyzer';
import type { GeneratorConfig, StoryTemplateConfig } from './config';

import { analyzeComponents } from './analyzer';
import { defaultConfig } from './config';
import {
  getComponentDesign,
  loadDesignMetadata,
  saveExampleDesignMetadata,
} from './design-metadata';
import { generateStoryTemplate, generateStoryTitle } from './templates/story.template';

/**
 * Main generator function
 */
async function generateStories(options: {
  force?: boolean;
  component?: string;
  verbose?: boolean;
}) {
  const { force = false, component: targetComponent, verbose = false } = options;

  const rootDir = findRootDir();
  const config = defaultConfig;

  // Load design metadata
  const designMetadataPath = join(
    rootDir,
    config.designMetadataPath || '.trace/.meta/designs.yaml',
  );
  const designMetadata = loadDesignMetadata(designMetadataPath);

  if (!designMetadata) {
    saveExampleDesignMetadata(designMetadataPath);
  }

  // Find all component files
  const componentFiles = findComponentFiles(rootDir, config, targetComponent);

  if (componentFiles.length === 0) {
    return;
  }

  // Analyze components

  const components = analyzeComponents(componentFiles);

  if (components.length === 0) {
    return;
  }

  // Generate stories
  let generated = 0;
  let skipped = 0;

  for (const componentInfo of components) {
    const result = generateStoryForComponent(
      componentInfo,
      config,
      rootDir,
      designMetadata,
      force,
      verbose,
    );

    if (result) {
      generated += 1;
    } else {
      skipped += 1;
    }
  }
}

/**
 * Find all component files matching the configuration
 */
function findComponentFiles(
  rootDir: string,
  config: GeneratorConfig,
  targetComponent?: string,
): string[] {
  const files: string[] = [];

  for (const dir of config.componentsDir) {
    const fullDir = join(rootDir, dir);

    if (!existsSync(fullDir)) {
      continue;
    }

    const pattern = join(fullDir, '**/*.tsx');
    const foundFiles = globSync(pattern, { absolute: true });

    for (const file of foundFiles) {
      // Check exclude patterns
      if (config.excludePatterns.some((pattern) => pattern.test(file))) {
        continue;
      }

      // Check include patterns
      if (!config.includePatterns.some((pattern) => pattern.test(file))) {
        continue;
      }

      // Filter by target component if specified
      if (targetComponent) {
        const fileName = basename(file, '.tsx');
        if (fileName.toLowerCase() !== targetComponent.toLowerCase()) {
          continue;
        }
      }

      files.push(file);
    }
  }

  return files;
}

/**
 * Generate story for a single component
 */
function generateStoryForComponent(
  componentInfo: ComponentInfo,
  config: GeneratorConfig,
  rootDir: string,
  designMetadata: any,
  force: boolean,
  verbose: boolean,
): boolean {
  const { name, filePath, variants, props } = componentInfo;

  // Get import path
  const importPath = getImportPath(filePath, rootDir, config);
  if (!importPath) {
    return false;
  }

  // Get design metadata
  const componentDesign = getComponentDesign(designMetadata, name);

  // Generate story title
  const title = generateStoryTitle(filePath, name);

  // Create story config
  const storyConfig: StoryTemplateConfig = {
    componentId: componentDesign?.componentId,
    componentName: name,
    figmaUrl: componentDesign?.figmaUrl,
    importPath,
    props,
    storyId: componentDesign?.storyId,
    title,
    variants,
  };

  // Generate story content
  const storyContent = generateStoryTemplate(storyConfig);

  // Determine output path
  const storiesDir = join(rootDir, config.storiesDir);
  const storyFileName = `${name}.stories.tsx`;
  const storyFilePath = join(storiesDir, storyFileName);

  // Check if story already exists
  if (existsSync(storyFilePath) && !force) {
    if (verbose) {
    }
    return false;
  }

  // Create stories directory if it doesn't exist
  mkdirSync(storiesDir, { recursive: true });

  // Write story file
  writeFileSync(storyFilePath, storyContent, 'utf8');

  const action = existsSync(storyFilePath) ? '♻️  Regenerated' : '✅ Generated';

  if (verbose) {
    if (componentDesign?.figmaUrl) {
    }
  }

  return true;
}

/**
 * Get import path for a component
 */
function getImportPath(filePath: string, rootDir: string, config: GeneratorConfig): string | null {
  const relativePath = relative(rootDir, filePath);

  for (const [dirPath, importPath] of Object.entries(config.importPathMapping)) {
    if (relativePath.startsWith(dirPath)) {
      return importPath;
    }
  }

  return null;
}

/**
 * Find project root directory
 */
function findRootDir(): string {
  let currentDir = process.cwd();

  // Go up until we find package.json with workspaces
  while (currentDir !== '/') {
    const packageJsonPath = join(currentDir, 'package.json');
    if (existsSync(packageJsonPath)) {
      const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf8'));
      if (packageJson.workspaces) {
        return currentDir;
      }
    }
    currentDir = dirname(currentDir);
  }

  // Fallback to current directory
  return process.cwd();
}

/**
 * CLI entry point
 */
async function main() {
  const { values } = parseArgs({
    options: {
      component: {
        short: 'c',
        type: 'string',
      },
      force: {
        default: false,
        short: 'f',
        type: 'boolean',
      },
      help: {
        default: false,
        short: 'h',
        type: 'boolean',
      },
      verbose: {
        default: false,
        short: 'v',
        type: 'boolean',
      },
    },
  });

  if (values.help) {
    return;
  }

  await generateStories({
    component: values.component as string | undefined,
    force: values.force as boolean,
    verbose: values.verbose as boolean,
  });
}

// Run CLI
main().catch((error) => {
  process.exit(1);
});
