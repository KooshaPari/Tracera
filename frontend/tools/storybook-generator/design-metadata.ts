/**
 * Design Metadata Loader for TraceRTM
 * Loads Figma design URLs and component mappings from YAML
 */

import { existsSync, readFileSync } from 'node:fs';
import { parse as parseYaml } from 'yaml';

import type { ComponentDesign, DesignMetadata } from './config';

/**
 * Load design metadata from YAML file
 */
export function loadDesignMetadata(metadataPath: string): DesignMetadata | null {
  if (!existsSync(metadataPath)) {
    return null;
  }

  try {
    const content = readFileSync(metadataPath, 'utf8');
    const data = parseYaml(content);

    if (!data || typeof data !== 'object') {
      return null;
    }

    return data as DesignMetadata;
  } catch (error) {
    return null;
  }
}

/**
 * Get design information for a specific component
 */
export function getComponentDesign(
  metadata: DesignMetadata | null,
  componentName: string,
): ComponentDesign | null {
  if (!(metadata && metadata.components)) {
    return null;
  }

  return metadata.components[componentName] || null;
}

/**
 * Create example design metadata YAML file
 */
export function generateExampleDesignMetadata(): string {
  return `# TraceRTM Design Metadata
# Maps components to Figma designs and trace IDs

components:
  Button:
    figmaUrl: "https://www.figma.com/file/xxx/Design-System?node-id=123"
    componentId: "comp-button-001"
    storyId: "story-button-001"
    variants:
      - default
      - destructive
      - outline
      - secondary
      - ghost
      - link

  Input:
    figmaUrl: "https://www.figma.com/file/xxx/Design-System?node-id=456"
    componentId: "comp-input-001"
    storyId: "story-input-001"

  Card:
    figmaUrl: "https://www.figma.com/file/xxx/Design-System?node-id=789"
    componentId: "comp-card-001"
    storyId: "story-card-001"

  # Add more components here
`;
}

/**
 * Save example metadata file
 */
export function saveExampleDesignMetadata(outputPath: string): void {
  const { writeFileSync, mkdirSync } = require('node:fs');
  const { dirname } = require('node:path');

  const dir = dirname(outputPath);
  mkdirSync(dir, { recursive: true });

  const content = generateExampleDesignMetadata();
  writeFileSync(outputPath, content, 'utf8');
}
