/**
 * OpenAPI Utilities
 * Helper functions for working with OpenAPI specifications
 */

export interface OpenAPISpec {
  openapi: string;
  info: {
    title: string;
    version: string;
    description?: string;
  };
  servers?: Array<{
    url: string;
    description?: string;
  }>;
  paths: Record<string, any>;
  components?: {
    schemas?: Record<string, any>;
    securitySchemes?: Record<string, any>;
  };
}

export interface SwaggerConfig {
  apiUrl: string;
  authType: 'bearer' | 'apiKey' | 'none';
  persistAuth: boolean;
  tryItOut: boolean;
}

/**
 * Fetch OpenAPI specification from URL
 */
export async function fetchOpenAPISpec(url: string): Promise<OpenAPISpec> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch OpenAPI spec: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Validate OpenAPI specification structure
 */
export function validateOpenAPISpec(spec: any): spec is OpenAPISpec {
  if (!spec || typeof spec !== 'object') {
    return false;
  }

  // Check required fields
  if (!spec.openapi || !spec.info || !spec.paths) {
    return false;
  }

  // Check OpenAPI version
  if (!spec.openapi.startsWith('3.')) {
    console.warn('Only OpenAPI 3.x is fully supported');
  }

  return true;
}

/**
 * Get all HTTP methods from spec
 */
export function getHttpMethods(spec: OpenAPISpec): string[] {
  const methods = new Set<string>();
  Object.values(spec.paths).forEach((path) => {
    Object.keys(path).forEach((method) => {
      if (
        ['get', 'post', 'put', 'patch', 'delete', 'options', 'head'].includes(
          method
        )
      ) {
        methods.add(method.toUpperCase());
      }
    });
  });
  return Array.from(methods);
}

/**
 * Get all tags from spec
 */
export function getTags(spec: OpenAPISpec): string[] {
  const tags = new Set<string>();
  Object.values(spec.paths).forEach((path) => {
    Object.values(path).forEach((operation: any) => {
      if (operation.tags) {
        operation.tags.forEach((tag: string) => tags.add(tag));
      }
    });
  });
  return Array.from(tags);
}

/**
 * Get security schemes from spec
 */
export function getSecuritySchemes(
  spec: OpenAPISpec
): Record<string, any> | undefined {
  return spec.components?.securitySchemes;
}

/**
 * Check if spec requires authentication
 */
export function requiresAuth(spec: OpenAPISpec): boolean {
  const securitySchemes = getSecuritySchemes(spec);
  return !!(securitySchemes && Object.keys(securitySchemes).length > 0);
}

/**
 * Get supported auth types
 */
export function getSupportedAuthTypes(
  spec: OpenAPISpec
): Array<'bearer' | 'apiKey' | 'oauth2' | 'basic'> {
  const securitySchemes = getSecuritySchemes(spec);
  if (!securitySchemes) return [];

  const authTypes: Array<'bearer' | 'apiKey' | 'oauth2' | 'basic'> = [];

  Object.values(securitySchemes).forEach((scheme: any) => {
    if (scheme.type === 'http' && scheme.scheme === 'bearer') {
      authTypes.push('bearer');
    } else if (scheme.type === 'http' && scheme.scheme === 'basic') {
      authTypes.push('basic');
    } else if (scheme.type === 'apiKey') {
      authTypes.push('apiKey');
    } else if (scheme.type === 'oauth2') {
      authTypes.push('oauth2');
    }
  });

  return authTypes;
}

/**
 * Extract server URLs
 */
export function getServerUrls(spec: OpenAPISpec): string[] {
  if (!spec.servers || spec.servers.length === 0) {
    return ['http://localhost:8000'];
  }
  return spec.servers.map((server) => server.url);
}

/**
 * Generate code examples for an endpoint
 */
export function generateCodeExamples(
  method: string,
  path: string,
  baseUrl: string,
  authToken?: string
): Record<string, string> {
  const url = `${baseUrl}${path}`;

  const examples: Record<string, string> = {
    curl: generateCurlExample(method, url, authToken),
    javascript: generateJavaScriptExample(method, url, authToken),
    python: generatePythonExample(method, url, authToken),
    typescript: generateTypeScriptExample(method, url, authToken),
  };

  return examples;
}

function generateCurlExample(
  method: string,
  url: string,
  authToken?: string
): string {
  let example = `curl -X ${method.toUpperCase()} "${url}"`;

  if (authToken) {
    example += ` \\\n  -H "Authorization: Bearer ${authToken}"`;
  }

  example += ` \\\n  -H "Content-Type: application/json"`;

  if (['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {
    example += ` \\\n  -d '{}'`;
  }

  return example;
}

function generateJavaScriptExample(
  method: string,
  url: string,
  authToken?: string
): string {
  const headers: any = {
    'Content-Type': 'application/json',
  };

  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }

  let example = `fetch('${url}', {\n  method: '${method.toUpperCase()}',\n  headers: ${JSON.stringify(headers, null, 2)}`;

  if (['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {
    example += `,\n  body: JSON.stringify({})`;
  }

  example += `\n})\n  .then(response => response.json())\n  .then(data => console.log(data))\n  .catch(error => console.error('Error:', error));`;

  return example;
}

function generatePythonExample(
  method: string,
  url: string,
  authToken?: string
): string {
  let example = `import requests\n\n`;

  example += `url = "${url}"\n`;
  example += `headers = {\n    "Content-Type": "application/json"`;

  if (authToken) {
    example += `,\n    "Authorization": "Bearer ${authToken}"`;
  }

  example += `\n}\n\n`;

  const methodLower = method.toLowerCase();

  if (['post', 'put', 'patch'].includes(methodLower)) {
    example += `data = {}\n\n`;
    example += `response = requests.${methodLower}(url, headers=headers, json=data)`;
  } else {
    example += `response = requests.${methodLower}(url, headers=headers)`;
  }

  example += `\nprint(response.json())`;

  return example;
}

function generateTypeScriptExample(
  method: string,
  url: string,
  authToken?: string
): string {
  const headers: any = {
    'Content-Type': 'application/json',
  };

  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }

  let example = `interface ApiResponse {\n  // Define your response type here\n}\n\n`;

  example += `const response = await fetch('${url}', {\n  method: '${method.toUpperCase()}',\n  headers: ${JSON.stringify(headers, null, 2)}`;

  if (['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {
    example += `,\n  body: JSON.stringify({})`;
  }

  example += `\n});\n\n`;
  example += `const data: ApiResponse = await response.json();\nconsole.log(data);`;

  return example;
}

/**
 * Download OpenAPI spec as JSON file
 */
export function downloadSpec(spec: OpenAPISpec, filename = 'openapi.json') {
  const blob = new Blob([JSON.stringify(spec, null, 2)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Get endpoint by operationId
 */
export function getEndpointByOperationId(
  spec: OpenAPISpec,
  operationId: string
): { path: string; method: string; operation: any } | null {
  for (const [path, pathItem] of Object.entries(spec.paths)) {
    for (const [method, operation] of Object.entries(pathItem)) {
      if (
        typeof operation === 'object' &&
        operation.operationId === operationId
      ) {
        return { path, method, operation };
      }
    }
  }
  return null;
}

/**
 * Format path parameters
 */
export function formatPathWithParams(
  path: string,
  params: Record<string, string>
): string {
  let formattedPath = path;
  Object.entries(params).forEach(([key, value]) => {
    formattedPath = formattedPath.replace(`{${key}}`, value);
  });
  return formattedPath;
}

/**
 * Parse response examples from operation
 */
export function getResponseExamples(operation: any): Record<string, any> {
  const examples: Record<string, any> = {};

  if (operation.responses) {
    Object.entries(operation.responses).forEach(([status, response]: [string, any]) => {
      if (response.content?.['application/json']?.example) {
        examples[status] = response.content['application/json'].example;
      } else if (response.content?.['application/json']?.examples) {
        examples[status] = Object.values(
          response.content['application/json'].examples
        )[0];
      }
    });
  }

  return examples;
}

/**
 * Storage helpers for authentication
 */
export const authStorage = {
  setToken: (token: string) => localStorage.setItem('api_token', token),
  getToken: () => localStorage.getItem('api_token'),
  removeToken: () => localStorage.removeItem('api_token'),
  setApiKey: (key: string) => localStorage.setItem('api_key', key),
  getApiKey: () => localStorage.getItem('api_key'),
  removeApiKey: () => localStorage.removeItem('api_key'),
  clearAll: () => {
    localStorage.removeItem('api_token');
    localStorage.removeItem('api_key');
  },
};
