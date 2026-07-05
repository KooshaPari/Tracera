import { logger } from '@/lib/logger';
/**
 * OpenAPI Utilities
 * Helper functions for working with OpenAPI specifications
 */

/**
 * Paths object in OpenAPI spec
 */
export interface OpenAPIPaths {
  [path: string]: {
    [method: string]: unknown;
  };
}

/**
 * Schemas components in OpenAPI spec
 */
export interface OpenAPISchemas {
  [name: string]: unknown;
}

/**
 * Security schemes components in OpenAPI spec
 */
export interface OpenAPISecuritySchemes {
  [name: string]: unknown;
}

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
  paths: OpenAPIPaths;
  components?: {
    schemas?: OpenAPISchemas;
    securitySchemes?: OpenAPISecuritySchemes;
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
export function validateOpenAPISpec(spec: unknown): spec is OpenAPISpec {
  if (!spec || typeof spec !== 'object') {
    return false;
  }

  const candidate = spec as Record<string, unknown>;

  // Check required fields
  if (!candidate['openapi'] || !candidate['info'] || !candidate['paths']) {
    return false;
  }

  // Check OpenAPI version
  if (typeof candidate['openapi'] === 'string' && !candidate['openapi'].startsWith('3.')) {
    logger.warn('Only OpenAPI 3.x is fully supported');
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
      if (['get', 'post', 'put', 'patch', 'delete', 'options', 'head'].includes(method)) {
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
    Object.values(path).forEach((operation) => {
      if (
        operation &&
        typeof operation === 'object' &&
        'tags' in operation &&
        Array.isArray(operation.tags)
      ) {
        operation.tags.forEach((tag) => {
          if (typeof tag === 'string') {
            tags.add(tag);
          }
        });
      }
    });
  });
  return Array.from(tags);
}

/**
 * Get security schemes from spec
 */
export function getSecuritySchemes(spec: OpenAPISpec): OpenAPISecuritySchemes | undefined {
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
  spec: OpenAPISpec,
): Array<'bearer' | 'apiKey' | 'oauth2' | 'basic'> {
  const securitySchemes = getSecuritySchemes(spec);
  if (!securitySchemes) return [];

  const authTypes: Array<'bearer' | 'apiKey' | 'oauth2' | 'basic'> = [];

  Object.values(securitySchemes).forEach((scheme) => {
    if (!scheme || typeof scheme !== 'object') return;

    const schemeObj = scheme as Record<string, unknown>;
    if (schemeObj['type'] === 'http' && schemeObj['scheme'] === 'bearer') {
      authTypes.push('bearer');
    } else if (schemeObj['type'] === 'http' && schemeObj['scheme'] === 'basic') {
      authTypes.push('basic');
    } else if (schemeObj['type'] === 'apiKey') {
      authTypes.push('apiKey');
    } else if (schemeObj['type'] === 'oauth2') {
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
    return ['http://localhost:4000'];
  }
  return spec.servers.map((server) => server.url);
}

/**
 * Code examples by language
 */
export interface CodeExamples {
  curl: string;
  javascript: string;
  python: string;
  typescript: string;
}

/**
 * Generate code examples for an endpoint
 */
export function generateCodeExamples(
  method: string,
  path: string,
  baseUrl: string,
  authToken?: string,
): CodeExamples {
  const url = `${baseUrl}${path}`;

  const examples: CodeExamples = {
    curl: generateCurlExample(method, url, authToken),
    javascript: generateJavaScriptExample(method, url, authToken),
    python: generatePythonExample(method, url, authToken),
    typescript: generateTypeScriptExample(method, url, authToken),
  };

  return examples;
}

function generateCurlExample(method: string, url: string, authToken?: string): string {
  let example = `curl -X ${method.toUpperCase()} "${url}"`;

  if (authToken) {
    example += ` \
  -H "Authorization: Bearer ${authToken}"`;
  }

  example += ` \
  -H "Content-Type: application/json"`;

  if (['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {
    example += ` \
  -d '{}'`;
  }

  return example;
}

function generateJavaScriptExample(method: string, url: string, authToken?: string): string {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  let example = `fetch('${url}', {
  method: '${method.toUpperCase()}',
  headers: ${JSON.stringify(headers, null, 2)}`;

  if (['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {
    example += `,
  body: JSON.stringify({})`;
  }

  example += `
})
  .then(response => response.json())
  .then(data => logger.info(data))
  .catch(error => logger.error('Error:', error));`;

  return example;
}

function generatePythonExample(method: string, url: string, authToken?: string): string {
  let example = `import requests

`;

  example += `url = "${url}"
`;
  example += `headers = {
    "Content-Type": "application/json"`;

  if (authToken) {
    example += `,
    "Authorization": "Bearer ${authToken}"`;
  }

  example += `
}

`;

  const methodLower = method.toLowerCase();

  if (['post', 'put', 'patch'].includes(methodLower)) {
    example += `data = {}

`;
    example += `response = requests.${methodLower}(url, headers=headers, json=data)`;
  } else {
    example += `response = requests.${methodLower}(url, headers=headers)`;
  }

  example += `
print(response.json())`;

  return example;
}

function generateTypeScriptExample(method: string, url: string, authToken?: string): string {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  let example = `interface ApiResponse {
  // Define your response type here
}

`;

  example += `const response = await fetch('${url}', {
  method: '${method.toUpperCase()}',
  headers: ${JSON.stringify(headers, null, 2)}`;

  if (['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {
    example += `,
  body: JSON.stringify({})`;
  }

  example += `
});

`;
  example += `const data: ApiResponse = await response.json();
logger.info(data);`;

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
  operationId: string,
): { path: string; method: string; operation: unknown } | null {
  for (const [path, pathItem] of Object.entries(spec.paths)) {
    for (const [method, operation] of Object.entries(pathItem)) {
      if (
        typeof operation === 'object' &&
        operation !== null &&
        'operationId' in operation &&
        (operation as Record<string, unknown>)['operationId'] === operationId
      ) {
        return { path, method, operation };
      }
    }
  }
  return null;
}

/**
 * Path parameters map
 */
export interface PathParams {
  [key: string]: string;
}

/**
 * Format path parameters
 */
export function formatPathWithParams(path: string, params: PathParams): string {
  let formattedPath = path;
  Object.entries(params).forEach(([key, value]) => {
    formattedPath = formattedPath.replace(`{${key}}`, value);
  });
  return formattedPath;
}

/**
 * Response examples map by status code
 */
export interface ResponseExamples {
  [statusCode: string]: unknown;
}

/**
 * Parse response examples from operation
 */
export function getResponseExamples(operation: unknown): ResponseExamples {
  const examples: ResponseExamples = {};

  if (
    !operation ||
    typeof operation !== 'object' ||
    !('responses' in operation) ||
    !operation.responses ||
    typeof operation.responses !== 'object'
  ) {
    return examples;
  }

  Object.entries(operation.responses).forEach(([status, response]) => {
    if (!response || typeof response !== 'object') return;

    const responseObj = response as Record<string, unknown>;
    const content = responseObj['content'] as Record<string, unknown> | undefined;
    if (!content) return;

    const jsonContent = content['application/json'] as Record<string, unknown> | undefined;
    if (!jsonContent) return;

    if (jsonContent['example']) {
      examples[status] = jsonContent['example'];
    } else if (jsonContent['examples'] && typeof jsonContent['examples'] === 'object') {
      const examplesObj = jsonContent['examples'] as Record<string, unknown>;
      const firstExample = Object.values(examplesObj)[0];
      if (firstExample) {
        examples[status] = firstExample;
      }
    }
  });

  return examples;
}

// SSR-safe localStorage check
const isLocalStorageAvailable = () => {
  return typeof localStorage !== 'undefined' && typeof localStorage.getItem === 'function';
};

/**
 * Storage helpers for authentication (SSR-safe)
 */
export const authStorage = {
  setToken: (token: string) => {
    if (isLocalStorageAvailable()) {
      localStorage.setItem('api_token', token);
    }
  },
  getToken: () => {
    if (!isLocalStorageAvailable()) return null;
    return localStorage.getItem('api_token');
  },
  removeToken: () => {
    if (isLocalStorageAvailable()) {
      localStorage.removeItem('api_token');
    }
  },
  setApiKey: (key: string) => {
    if (isLocalStorageAvailable()) {
      localStorage.setItem('api_key', key);
    }
  },
  getApiKey: () => {
    if (!isLocalStorageAvailable()) return null;
    return localStorage.getItem('api_key');
  },
  removeApiKey: () => {
    if (isLocalStorageAvailable()) {
      localStorage.removeItem('api_key');
    }
  },
  clearAll: () => {
    if (isLocalStorageAvailable()) {
      localStorage.removeItem('api_token');
      localStorage.removeItem('api_key');
    }
  },
};
