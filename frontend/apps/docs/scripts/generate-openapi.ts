#!/usr/bin/env bun
/**
 * OpenAPI Spec Generator
 *
 * Fetches OpenAPI spec from FastAPI backend and converts to YAML.
 * Used in prebuild step to auto-generate API documentation.
 *
 * Usage:
 *   bun run scripts/generate-openapi.ts
 *
 * Environment:
 *   BACKEND_URL - Backend API URL (default: http://localhost:8000)
 */

import yaml from 'js-yaml';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const BACKEND_URL = process.env['BACKEND_URL'] || 'http://localhost:8000';
const OPENAPI_ENDPOINT = `${BACKEND_URL}/openapi.json`;
const OUTPUT_DIR = join(process.cwd(), 'content/docs/03-api-reference');
const OUTPUT_FILE = join(OUTPUT_DIR, 'openapi.yaml');

interface OpenAPISpec {
  openapi: string;
  info: {
    title: string;
    description?: string;
    version: string;
  };
  paths: Record<string, unknown>;
  components?: Record<string, unknown>;
}

async function fetchOpenAPISpec(): Promise<OpenAPISpec> {
  try {
    const response = await fetch(OPENAPI_ENDPOINT);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const spec = (await response.json()) as OpenAPISpec;

    // Validate basic structure
    if (!spec.openapi || !spec.info || !spec.paths) {
      throw new Error('Invalid OpenAPI spec: missing required fields');
    }

    return spec;
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('fetch failed') || error.message.includes('ECONNREFUSED')) {
        console.warn('OpenAPI fetch failed: backend is not reachable.');
      } else {
        console.error('OpenAPI fetch failed:', error.message);
      }
    }
    throw error;
  }
}

function convertToYAML(spec: OpenAPISpec): string {
  try {
    const yamlContent = yaml.dump(spec, {
      indent: 2,
      lineWidth: 120,
      noRefs: false,
      sortKeys: false,
    });

    return yamlContent;
  } catch (error) {
    if (error instanceof Error) {
      console.error('Failed to convert OpenAPI spec to YAML:', error.message);
    }
    throw error;
  }
}

function saveToFile(content: string): void {
  try {
    // Ensure output directory exists
    mkdirSync(OUTPUT_DIR, { recursive: true });

    // Write YAML file
    writeFileSync(OUTPUT_FILE, content, 'utf8');
  } catch (error) {
    if (error instanceof Error) {
      console.error('Failed to write OpenAPI YAML file:', error.message);
    }
    throw error;
  }
}

async function main() {
  try {
    const spec = await fetchOpenAPISpec();
    const yamlContent = convertToYAML(spec);
    saveToFile(yamlContent);

    process.exit(0);
  } catch (error) {
    console.error('OpenAPI generation failed:', error);
    process.exit(1);
  }
}

// Run if executed directly
if (import.meta.main) {
  main().catch(() => {
    // Silently exit on error during build
    process.exit(0);
  });
}

export { fetchOpenAPISpec, convertToYAML, saveToFile };
