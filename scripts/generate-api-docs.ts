#!/usr/bin/env bun
/**
 * OpenAPI Documentation Generator for TraceRTM
 *
 * This script parses the OpenAPI specification and generates MDX files
 * for each endpoint, organized by resource type.
 *
 * Output: /content/docs/api/rest-api/*.mdx
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';

interface OpenAPISpec {
  openapi: string;
  info: {
    title: string;
    version: string;
    description: string;
  };
  servers: Array<{
    url: string;
    description: string;
  }>;
  tags: Array<{
    name: string;
    description: string;
  }>;
  paths: Record<string, PathItem>;
  components: {
    securitySchemes: Record<string, SecurityScheme>;
    schemas: Record<string, Schema>;
    responses: Record<string, Response>;
  };
}

interface PathItem {
  [method: string]: Operation;
}

interface Operation {
  tags?: string[];
  summary: string;
  description: string;
  operationId: string;
  security?: Array<Record<string, string[]>>;
  parameters?: Parameter[];
  requestBody?: RequestBody;
  responses: Record<string, Response>;
}

interface Parameter {
  name: string;
  in: 'query' | 'path' | 'header';
  required?: boolean;
  description?: string;
  schema: Schema;
}

interface RequestBody {
  description?: string;
  required?: boolean;
  content: Record<string, { schema: Schema; example?: any }>;
}

interface Response {
  description: string;
  content?: Record<string, { schema: Schema; example?: any }>;
}

interface SecurityScheme {
  type: string;
  scheme?: string;
  bearerFormat?: string;
  description?: string;
  in?: string;
  name?: string;
}

interface Schema {
  type?: string;
  format?: string;
  description?: string;
  enum?: string[];
  properties?: Record<string, Schema>;
  required?: string[];
  items?: Schema;
  $ref?: string;
  nullable?: boolean;
  minimum?: number;
  maximum?: number;
  default?: any;
}

const OPENAPI_PATH = join(process.cwd(), '../frontend/apps/web/public/specs/openapi.json');
const DOCS_OUTPUT_DIR = join(process.cwd(), 'content/docs/api');

function ensureDir(dir: string) {
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

function resolveRef(ref: string, spec: OpenAPISpec): any {
  const parts = ref.replace('#/', '').split('/');
  let current: any = spec;
  for (const part of parts) {
    current = current[part];
  }
  return current;
}

function formatSchemaType(schema: Schema, spec: OpenAPISpec): string {
  if (schema.$ref) {
    const resolved = resolveRef(schema.$ref, spec);
    return `[${schema.$ref.split('/').pop()}](#schemas)`;
  }

  if (schema.type === 'array' && schema.items) {
    return `${formatSchemaType(schema.items, spec)}[]`;
  }

  if (schema.enum) {
    return `enum: ${schema.enum.map(v => `\`${v}\``).join(', ')}`;
  }

  let type = schema.type || 'any';
  if (schema.format) {
    type += ` (${schema.format})`;
  }
  return type;
}

function generateParametersTable(params: Parameter[], spec: OpenAPISpec): string {
  if (!params || params.length === 0) return '';

  let table = '\n### Parameters\n\n';
  table += '| Name | Type | Location | Required | Description |\n';
  table += '|------|------|----------|----------|-------------|\n';

  for (const param of params) {
    const type = formatSchemaType(param.schema, spec);
    const required = param.required ? '✓' : '';
    const desc = param.description || '';
    table += `| \`${param.name}\` | ${type} | ${param.in} | ${required} | ${desc} |\n`;
  }

  return table + '\n';
}

function generateRequestBodySection(requestBody: RequestBody | undefined, spec: OpenAPISpec): string {
  if (!requestBody) return '';

  let section = '\n### Request Body\n\n';
  if (requestBody.description) {
    section += `${requestBody.description}\n\n`;
  }

  for (const [contentType, content] of Object.entries(requestBody.content)) {
    section += `**Content-Type:** \`${contentType}\`\n\n`;

    if (content.schema.$ref) {
      const schemaName = content.schema.$ref.split('/').pop();
      section += `**Schema:** [${schemaName}](#${schemaName?.toLowerCase()})\n\n`;
    }

    if (content.example) {
      section += '**Example:**\n\n';
      section += '```json\n';
      section += JSON.stringify(content.example, null, 2);
      section += '\n```\n\n';
    }
  }

  return section;
}

function generateResponsesSection(responses: Record<string, Response>, spec: OpenAPISpec): string {
  let section = '\n### Responses\n\n';

  for (const [statusCode, response] of Object.entries(responses)) {
    section += `#### ${statusCode} - ${response.description}\n\n`;

    if (response.content) {
      for (const [contentType, content] of Object.entries(response.content)) {
        if (content.schema.$ref) {
          const schemaName = content.schema.$ref.split('/').pop();
          section += `**Schema:** [${schemaName}](#${schemaName?.toLowerCase()})\n\n`;
        }

        if (content.example) {
          section += '```json\n';
          section += JSON.stringify(content.example, null, 2);
          section += '\n```\n\n';
        }
      }
    }
  }

  return section;
}

function generateCodeExamples(method: string, path: string, operation: Operation): string {
  const hasAuth = operation.security && operation.security.length > 0;

  let examples = '\n### Code Examples\n\n';

  // cURL example
  examples += '<Tabs items={["cURL", "JavaScript", "Python", "Go"]}>\n\n';
  examples += '<Tab value="cURL">\n\n';
  examples += '```bash\n';
  examples += `curl -X ${method.toUpperCase()} "https://api.tracertm.com${path}" \\\n`;
  if (hasAuth) {
    examples += '  -H "Authorization: Bearer YOUR_TOKEN" \\\n';
  }
  examples += '  -H "Content-Type: application/json"\n';
  examples += '```\n\n';
  examples += '</Tab>\n\n';

  // JavaScript example
  examples += '<Tab value="JavaScript">\n\n';
  examples += '```javascript\n';
  examples += `const response = await fetch('https://api.tracertm.com${path}', {\n`;
  examples += `  method: '${method.toUpperCase()}',\n`;
  examples += '  headers: {\n';
  if (hasAuth) {
    examples += "    'Authorization': 'Bearer YOUR_TOKEN',\n";
  }
  examples += "    'Content-Type': 'application/json'\n";
  examples += '  }\n';
  examples += '});\n';
  examples += 'const data = await response.json();\n';
  examples += 'console.log(data);\n';
  examples += '```\n\n';
  examples += '</Tab>\n\n';

  // Python example
  examples += '<Tab value="Python">\n\n';
  examples += '```python\n';
  examples += 'import requests\n\n';
  examples += `response = requests.${method.toLowerCase()}(\n`;
  examples += `    "https://api.tracertm.com${path}",\n`;
  if (hasAuth) {
    examples += '    headers={"Authorization": "Bearer YOUR_TOKEN"}\n';
  }
  examples += ')\n';
  examples += 'data = response.json()\n';
  examples += 'print(data)\n';
  examples += '```\n\n';
  examples += '</Tab>\n\n';

  // Go example
  examples += '<Tab value="Go">\n\n';
  examples += '```go\n';
  examples += 'package main\n\n';
  examples += 'import (\n';
  examples += '    "fmt"\n';
  examples += '    "net/http"\n';
  examples += ')\n\n';
  examples += 'func main() {\n';
  examples += `    req, _ := http.NewRequest("${method.toUpperCase()}", "https://api.tracertm.com${path}", nil)\n`;
  if (hasAuth) {
    examples += '    req.Header.Set("Authorization", "Bearer YOUR_TOKEN")\n';
  }
  examples += '    req.Header.Set("Content-Type", "application/json")\n\n';
  examples += '    client := &http.Client{}\n';
  examples += '    resp, err := client.Do(req)\n';
  examples += '    // Handle response...\n';
  examples += '}\n';
  examples += '```\n\n';
  examples += '</Tab>\n\n';
  examples += '</Tabs>\n\n';

  return examples;
}

function generateEndpointPage(path: string, method: string, operation: Operation, spec: OpenAPISpec): string {
  const title = operation.summary;
  const description = operation.description;
  const requiresAuth = operation.security && operation.security.length > 0;

  let content = '---\n';
  content += `title: "${title}"\n`;
  content += `description: "${description}"\n`;
  content += '---\n\n';

  content += `# ${title}\n\n`;
  content += `${description}\n\n`;

  // Endpoint info
  content += '<Card>\n\n';
  content += `**\`${method.toUpperCase()} ${path}\`**\n\n`;
  if (requiresAuth) {
    content += '🔒 **Authentication Required**\n\n';
  }
  content += '</Card>\n\n';

  // Parameters
  if (operation.parameters) {
    content += generateParametersTable(operation.parameters, spec);
  }

  // Request Body
  if (operation.requestBody) {
    content += generateRequestBodySection(operation.requestBody, spec);
  }

  // Responses
  content += generateResponsesSection(operation.responses, spec);

  // Code Examples
  content += generateCodeExamples(method, path, operation);

  return content;
}

function generateOverviewPage(spec: OpenAPISpec): string {
  let content = '---\n';
  content += 'title: "REST API Overview"\n';
  content += 'description: "TraceRTM REST API documentation and quick start guide"\n';
  content += '---\n\n';

  content += '# REST API Overview\n\n';
  content += `${spec.info.description}\n\n`;

  content += '## Base URLs\n\n';
  for (const server of spec.servers) {
    content += `- **${server.description}**: \`${server.url}\`\n`;
  }
  content += '\n';

  content += '## Authentication\n\n';
  content += 'The TraceRTM API supports two authentication methods:\n\n';

  const schemes = spec.components.securitySchemes;
  for (const [name, scheme] of Object.entries(schemes)) {
    content += `### ${name}\n\n`;
    content += `${scheme.description}\n\n`;

    if (scheme.type === 'http' && scheme.scheme === 'bearer') {
      content += '```bash\n';
      content += 'curl -H "Authorization: Bearer YOUR_TOKEN" https://api.tracertm.com/api/v1/items\n';
      content += '```\n\n';
    } else if (scheme.type === 'apiKey') {
      content += '```bash\n';
      content += `curl -H "${scheme.name}: YOUR_API_KEY" https://api.tracertm.com/api/v1/items\n`;
      content += '```\n\n';
    }
  }

  content += '## Quick Start\n\n';
  content += '```javascript\n';
  content += '// Initialize the client\n';
  content += "const client = new TraceRTMClient({ token: 'YOUR_TOKEN' });\n\n";
  content += '// List items in a project\n';
  content += 'const items = await client.items.list({ project_id: "..." });\n';
  content += 'console.log(items);\n';
  content += '```\n\n';

  content += '## Rate Limiting\n\n';
  content += 'API requests are rate limited to ensure service stability:\n\n';
  content += '- **Authenticated requests**: 1000 requests/hour\n';
  content += '- **Unauthenticated requests**: 100 requests/hour\n\n';
  content += 'Rate limit information is included in response headers:\n\n';
  content += '```\n';
  content += 'X-RateLimit-Limit: 1000\n';
  content += 'X-RateLimit-Remaining: 999\n';
  content += 'X-RateLimit-Reset: 1640995200\n';
  content += '```\n\n';

  content += '## Error Codes\n\n';
  content += 'The API uses standard HTTP status codes:\n\n';
  content += '| Code | Description |\n';
  content += '|------|-------------|\n';
  content += '| 200 | Success |\n';
  content += '| 400 | Bad Request - Invalid parameters |\n';
  content += '| 401 | Unauthorized - Missing or invalid authentication |\n';
  content += '| 403 | Forbidden - Insufficient permissions |\n';
  content += '| 404 | Not Found - Resource does not exist |\n';
  content += '| 429 | Too Many Requests - Rate limit exceeded |\n';
  content += '| 500 | Internal Server Error |\n\n';

  content += '## Pagination\n\n';
  content += 'List endpoints support pagination using `skip` and `limit` parameters:\n\n';
  content += '```bash\n';
  content += 'GET /api/v1/items?project_id=xxx&skip=0&limit=100\n';
  content += '```\n\n';
  content += 'Response includes pagination metadata:\n\n';
  content += '```json\n';
  content += '{\n';
  content += '  "total": 250,\n';
  content += '  "items": [...]\n';
  content += '}\n';
  content += '```\n\n';

  return content;
}

function generateSchemaPage(schemaName: string, schema: Schema, spec: OpenAPISpec): string {
  let content = '---\n';
  content += `title: "${schemaName}"\n`;
  content += `description: "Schema definition for ${schemaName}"\n`;
  content += '---\n\n';

  content += `# ${schemaName}\n\n`;
  if (schema.description) {
    content += `${schema.description}\n\n`;
  }

  content += '## Properties\n\n';
  content += '| Property | Type | Required | Description |\n';
  content += '|----------|------|----------|-------------|\n';

  if (schema.properties) {
    for (const [propName, propSchema] of Object.entries(schema.properties)) {
      const type = formatSchemaType(propSchema, spec);
      const required = schema.required?.includes(propName) ? '✓' : '';
      const desc = propSchema.description || '';
      content += `| \`${propName}\` | ${type} | ${required} | ${desc} |\n`;
    }
  }
  content += '\n';

  content += '## Example\n\n';
  content += '```json\n';
  const example: any = {};
  if (schema.properties) {
    for (const [propName, propSchema] of Object.entries(schema.properties)) {
      if (propSchema.type === 'string') {
        example[propName] = propSchema.format === 'uuid' ? '550e8400-e29b-41d4-a716-446655440000' : 'example';
      } else if (propSchema.type === 'integer') {
        example[propName] = 0;
      } else if (propSchema.type === 'boolean') {
        example[propName] = true;
      } else if (propSchema.type === 'array') {
        example[propName] = [];
      }
    }
  }
  content += JSON.stringify(example, null, 2);
  content += '\n```\n\n';

  return content;
}

function groupEndpointsByTag(spec: OpenAPISpec): Map<string, Array<{ path: string; method: string; operation: Operation }>> {
  const groups = new Map<string, Array<{ path: string; method: string; operation: Operation }>>();

  for (const [path, pathItem] of Object.entries(spec.paths)) {
    for (const [method, operation] of Object.entries(pathItem)) {
      if (method === 'parameters') continue;

      const tag = operation.tags?.[0] || 'Other';
      if (!groups.has(tag)) {
        groups.set(tag, []);
      }
      groups.get(tag)!.push({ path, method, operation });
    }
  }

  return groups;
}

function generateResourcePage(tag: string, endpoints: Array<{ path: string; method: string; operation: Operation }>, spec: OpenAPISpec): string {
  const tagInfo = spec.tags.find(t => t.name === tag);

  let content = '---\n';
  content += `title: "${tag}"\n`;
  content += `description: "${tagInfo?.description || `${tag} API endpoints`}"\n`;
  content += '---\n\n';

  content += `# ${tag}\n\n`;
  if (tagInfo?.description) {
    content += `${tagInfo.description}\n\n`;
  }

  content += '## Endpoints\n\n';

  for (const { path, method, operation } of endpoints) {
    const methodBadge = method.toUpperCase();
    const color = {
      get: 'blue',
      post: 'green',
      put: 'yellow',
      patch: 'orange',
      delete: 'red'
    }[method.toLowerCase()] || 'gray';

    content += `### ${operation.summary}\n\n`;
    content += `<Badge variant="${color}">${methodBadge}</Badge> \`${path}\`\n\n`;
    content += `${operation.description}\n\n`;

    if (operation.parameters && operation.parameters.length > 0) {
      content += generateParametersTable(operation.parameters, spec);
    }

    content += generateCodeExamples(method, path, operation);
    content += '---\n\n';
  }

  return content;
}

async function main() {
  console.log('🚀 Generating API documentation from OpenAPI spec...\n');

  // Read OpenAPI spec
  const specContent = readFileSync(OPENAPI_PATH, 'utf-8');
  const spec: OpenAPISpec = JSON.parse(specContent);

  console.log(`📖 Loaded OpenAPI spec: ${spec.info.title} v${spec.info.version}\n`);

  // Ensure output directories exist
  const restApiDir = join(DOCS_OUTPUT_DIR, 'rest-api');
  const schemasDir = join(DOCS_OUTPUT_DIR, 'schemas');
  ensureDir(restApiDir);
  ensureDir(schemasDir);

  // Generate overview page
  console.log('📝 Generating overview page...');
  const overviewContent = generateOverviewPage(spec);
  writeFileSync(join(restApiDir, 'index.mdx'), overviewContent);

  // Generate resource pages grouped by tag
  console.log('📝 Generating resource pages...');
  const groupedEndpoints = groupEndpointsByTag(spec);

  for (const [tag, endpoints] of groupedEndpoints) {
    const filename = tag.toLowerCase().replace(/\s+/g, '-') + '.mdx';
    const content = generateResourcePage(tag, endpoints, spec);
    writeFileSync(join(restApiDir, filename), content);
    console.log(`   ✓ Generated ${filename}`);
  }

  // Generate schema documentation
  console.log('📝 Generating schema documentation...');
  for (const [schemaName, schema] of Object.entries(spec.components.schemas)) {
    const filename = schemaName.toLowerCase().replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase() + '.mdx';
    const content = generateSchemaPage(schemaName, schema, spec);
    writeFileSync(join(schemasDir, filename), content);
    console.log(`   ✓ Generated ${filename}`);
  }

  console.log('\n✅ API documentation generation complete!');
  console.log(`\n📁 Output location: ${DOCS_OUTPUT_DIR}`);
}

main().catch(console.error);
