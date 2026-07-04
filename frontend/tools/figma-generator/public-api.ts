/**
 * Figma Generator - Main Entry Point
 *
 * Exports all public APIs for Figma design sync and generation
 */

export type {
  ComponentDefinition as CodeComponentDefinition,
  ComponentProp,
  ComponentVariant,
  DesignToken,
  FigmaEffect,
  FigmaFill,
  FigmaNode,
  FigmaNodeProperties,
  FigmaNodeStyles,
  FigmaNodeType,
  FigmaStroke,
} from './code-to-design';
// Code to Design Exports
export { ComponentParser, componentsToFigma, TailwindConverter } from './code-to-design';
export type { FigmaConfig } from './config';
// Configuration Exports
export { getEnvTemplate, loadFigmaConfig, validateConfig } from './config';
export type {
  Component,
  ComponentStyles,
  FigmaClientConfig,
  FigmaFile,
  ImageMap,
  TypographyToken,
  Variables,
} from './figma-api-client';
// API Exports
export { createFigmaClient, FigmaAPIError, FigmaClient } from './figma-api-client';
export type {
  FigmaPluginComponent,
  FigmaPluginNode,
  FigmaPluginOutput,
  GeneratorConfig,
  StoryDefinition,
  StoryToDesignConfig,
  StoryToDesignOutput,
} from './generate-figma';
// Generator Exports
export { FigmaGenerator, runGenerator } from './generate-figma';
export type { ComponentMetadata, DesignMetadata, SyncConfig, SyncResult } from './sync-designs';
// Sync Exports
export { DesignSync } from './sync-designs';

// Type Exports
export type * from './types';

// Version
export const VERSION = '1.0.0';
