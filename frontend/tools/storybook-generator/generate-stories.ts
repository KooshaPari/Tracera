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

import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { basename, dirname, join, relative } from 'node:path'
import { parseArgs } from 'node:util'
import { globSync } from 'glob'
import { analyzeComponents, type ComponentInfo } from './analyzer'
import { defaultConfig, type GeneratorConfig, type StoryTemplateConfig } from './config'
import {
  getComponentDesign,
  loadDesignMetadata,
  saveExampleDesignMetadata,
} from './design-metadata'
import { generateStoryTemplate, generateStoryTitle } from './templates/story.template'

/**
 * Main generator function
 */
async function generateStories(options: {
  force?: boolean
  component?: string
  verbose?: boolean
}) {
  const { force = false, component: targetComponent, verbose = false } = options

  console.log('🎨 TraceRTM Storybook Story Generator')
  console.log('=====================================\n')

  const rootDir = findRootDir()
  const config = defaultConfig

  // Load design metadata
  const designMetadataPath = join(rootDir, config.designMetadataPath || '.trace/.meta/designs.yaml')
  const designMetadata = loadDesignMetadata(designMetadataPath)

  if (!designMetadata) {
    console.log('📝 No design metadata found. Creating example file...')
    saveExampleDesignMetadata(designMetadataPath)
  }

  // Find all component files
  const componentFiles = findComponentFiles(rootDir, config, targetComponent)

  if (componentFiles.length === 0) {
    console.log('❌ No components found')
    return
  }

  console.log(`📦 Found ${componentFiles.length} component(s)\n`)

  // Analyze components
  console.log('🔍 Analyzing components...')
  const components = analyzeComponents(componentFiles)

  if (components.length === 0) {
    console.log('❌ No valid components to generate stories for')
    return
  }

  console.log(`✅ Analyzed ${components.length} component(s)\n`)

  // Generate stories
  let generated = 0
  let skipped = 0

  for (const componentInfo of components) {
    const result = generateStoryForComponent(
      componentInfo,
      config,
      rootDir,
      designMetadata,
      force,
      verbose
    )

    if (result) {
      generated++
    } else {
      skipped++
    }
  }

  console.log('\n✨ Story generation complete!')
  console.log(`   Generated: ${generated}`)
  console.log(`   Skipped: ${skipped}`)
}

/**
 * Find all component files matching the configuration
 */
function findComponentFiles(
  rootDir: string,
  config: GeneratorConfig,
  targetComponent?: string
): string[] {
  const files: string[] = []

  for (const dir of config.componentsDir) {
    const fullDir = join(rootDir, dir)

    if (!existsSync(fullDir)) {
      console.warn(`⚠️  Component directory not found: ${dir}`)
      continue
    }

    const pattern = join(fullDir, '**/*.tsx')
    const foundFiles = globSync(pattern, { absolute: true })

    for (const file of foundFiles) {
      // Check exclude patterns
      if (config.excludePatterns.some((pattern) => pattern.test(file))) {
        continue
      }

      // Check include patterns
      if (!config.includePatterns.some((pattern) => pattern.test(file))) {
        continue
      }

      // Filter by target component if specified
      if (targetComponent) {
        const fileName = basename(file, '.tsx')
        if (fileName.toLowerCase() !== targetComponent.toLowerCase()) {
          continue
        }
      }

      files.push(file)
    }
  }

  return files
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
  verbose: boolean
): boolean {
  const { name, filePath, variants, props } = componentInfo

  // Get import path
  const importPath = getImportPath(filePath, rootDir, config)
  if (!importPath) {
    console.warn(`⚠️  Could not determine import path for ${name}`)
    return false
  }

  // Get design metadata
  const componentDesign = getComponentDesign(designMetadata, name)

  // Generate story title
  const title = generateStoryTitle(filePath, name)

  // Create story config
  const storyConfig: StoryTemplateConfig = {
    componentName: name,
    importPath,
    title,
    componentId: componentDesign?.componentId,
    storyId: componentDesign?.storyId,
    figmaUrl: componentDesign?.figmaUrl,
    variants,
    props,
  }

  // Generate story content
  const storyContent = generateStoryTemplate(storyConfig)

  // Determine output path
  const storiesDir = join(rootDir, config.storiesDir)
  const storyFileName = `${name}.stories.tsx`
  const storyFilePath = join(storiesDir, storyFileName)

  // Check if story already exists
  if (existsSync(storyFilePath) && !force) {
    if (verbose) {
      console.log(`⏭️  Skipping ${name} (already exists)`)
    }
    return false
  }

  // Create stories directory if it doesn't exist
  mkdirSync(storiesDir, { recursive: true })

  // Write story file
  writeFileSync(storyFilePath, storyContent, 'utf-8')

  const action = existsSync(storyFilePath) ? '♻️  Regenerated' : '✅ Generated'
  console.log(`${action} ${name}.stories.tsx`)

  if (verbose) {
    console.log(`   Import: ${importPath}`)
    console.log(`   Variants: ${variants.length}`)
    console.log(`   Props: ${props.length}`)
    if (componentDesign?.figmaUrl) {
      console.log(`   Figma: ${componentDesign.figmaUrl}`)
    }
    console.log()
  }

  return true
}

/**
 * Get import path for a component
 */
function getImportPath(filePath: string, rootDir: string, config: GeneratorConfig): string | null {
  const relativePath = relative(rootDir, filePath)

  for (const [dirPath, importPath] of Object.entries(config.importPathMapping)) {
    if (relativePath.startsWith(dirPath)) {
      return importPath
    }
  }

  return null
}

/**
 * Find project root directory
 */
function findRootDir(): string {
  let currentDir = process.cwd()

  // Go up until we find package.json with workspaces
  while (currentDir !== '/') {
    const packageJsonPath = join(currentDir, 'package.json')
    if (existsSync(packageJsonPath)) {
      const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf-8'))
      if (packageJson.workspaces) {
        return currentDir
      }
    }
    currentDir = dirname(currentDir)
  }

  // Fallback to current directory
  return process.cwd()
}

/**
 * CLI entry point
 */
async function main() {
  const { values } = parseArgs({
    options: {
      force: {
        type: 'boolean',
        short: 'f',
        default: false,
      },
      component: {
        type: 'string',
        short: 'c',
      },
      verbose: {
        type: 'boolean',
        short: 'v',
        default: false,
      },
      help: {
        type: 'boolean',
        short: 'h',
        default: false,
      },
    },
  })

  if (values.help) {
    console.log(`
TraceRTM Storybook Story Generator

Usage:
  bun run generate:stories [options]

Options:
  -f, --force          Overwrite existing story files
  -c, --component NAME Generate story for specific component only
  -v, --verbose        Show detailed output
  -h, --help           Show this help message

Examples:
  bun run generate:stories
  bun run generate:stories --force
  bun run generate:stories --component Button
  bun run generate:stories --component Input --verbose
`)
    return
  }

  await generateStories({
    force: values.force as boolean,
    component: values.component as string | undefined,
    verbose: values.verbose as boolean,
  })
}

// Run CLI
main().catch((error) => {
  console.error('❌ Error:', error)
  process.exit(1)
})
