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

import { writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import yaml from 'js-yaml';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
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
  console.log(`📡 Fetching OpenAPI spec from ${OPENAPI_ENDPOINT}...`);

  try {
    const response = await fetch(OPENAPI_ENDPOINT);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const spec = await response.json() as OpenAPISpec;

    // Validate basic structure
    if (!spec.openapi || !spec.info || !spec.paths) {
      throw new Error('Invalid OpenAPI spec: missing required fields');
    }

    console.log(`✅ Fetched OpenAPI ${spec.openapi} spec: ${spec.info.title} v${spec.info.version}`);
    console.log(`   Endpoints: ${Object.keys(spec.paths).length}`);

    return spec;
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('fetch failed') || error.message.includes('ECONNREFUSED')) {
        console.error(`\n❌ Failed to connect to backend at ${BACKEND_URL}`);
        console.error('   Make sure the backend is running:');
        console.error('   $ uvicorn tracertm.api.main:app --reload\n');
      } else {
        console.error(`\n❌ Error fetching OpenAPI spec: ${error.message}\n`);
      }
    }
    throw error;
  }
}

function convertToYAML(spec: OpenAPISpec): string {
  console.log('🔄 Converting JSON to YAML...');

  try {
    const yamlContent = yaml.dump(spec, {
      indent: 2,
      lineWidth: 120,
      noRefs: false,
      sortKeys: false,
    });

    console.log(`✅ Converted to YAML (${yamlContent.length} bytes)`);
    return yamlContent;
  } catch (error) {
    if (error instanceof Error) {
      console.error(`\n❌ Error converting to YAML: ${error.message}\n`);
    }
    throw error;
  }
}

function saveToFile(content: string): void {
  console.log(`💾 Saving to ${OUTPUT_FILE}...`);

  try {
    // Ensure output directory exists
    mkdirSync(OUTPUT_DIR, { recursive: true });

    // Write YAML file
    writeFileSync(OUTPUT_FILE, content, 'utf-8');

    console.log(`✅ OpenAPI spec saved successfully\n`);
    console.log(`📄 Output: ${OUTPUT_FILE}`);
    console.log(`📊 Size: ${(content.length / 1024).toFixed(2)} KB\n`);
  } catch (error) {
    if (error instanceof Error) {
      console.error(`\n❌ Error saving file: ${error.message}\n`);
    }
    throw error;
  }
}

async function main() {
  console.log('\n🚀 OpenAPI Spec Generator\n');

  try {
    const spec = await fetchOpenAPISpec();
    const yamlContent = convertToYAML(spec);
    saveToFile(yamlContent);

    console.log('✨ Done! API documentation is ready to build.\n');
    process.exit(0);
  } catch {
    console.error('💥 Generation failed\n');
    process.exit(1);
  }
}

// Run if executed directly
if (import.meta.main) {
  main();
}

export { fetchOpenAPISpec, convertToYAML, saveToFile };
