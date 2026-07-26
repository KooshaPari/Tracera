/**
 * Minimal GraphQL shim to resolve MSW's internal graphql dependency
 * MSW imports graphql for GraphQL handler support, but we only use HTTP handlers
 * This shim provides the minimum exports to satisfy the import without full graphql package
 */

// Minimal types that MSW might need
export interface DocumentNode {
  kind: 'Document';
  definitions: any[];
}

// Minimal parse function (MSW likely doesn't call this for HTTP-only handlers)
export function parse(source: string): DocumentNode {
  throw new Error('GraphQL parse not implemented - HTTP handlers only');
}

// Other potential exports MSW might import
export function print(ast: DocumentNode): string {
  throw new Error('GraphQL print not implemented - HTTP handlers only');
}

export function buildSchema(source: string): any {
  throw new Error('GraphQL buildSchema not implemented - HTTP handlers only');
}

export function execute(...args: any[]): any {
  throw new Error('GraphQL execute not implemented - HTTP handlers only');
}

export function subscribe(...args: any[]): any {
  throw new Error('GraphQL subscribe not implemented - HTTP handlers only');
}

// Re-export everything to satisfy "export * from 'graphql'" patterns
export default {
  parse,
  print,
  buildSchema,
  execute,
  subscribe,
};
