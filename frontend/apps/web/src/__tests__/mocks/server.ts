/**
 * MSW server setup for tests
 */

import { setupServer } from 'msw/node';

import { handlers } from './handlers';

// Lazy initialization to allow localStorage mock to be set up first
let _server: ReturnType<typeof setupServer> | null = null;

export function getServer() {
  _server ??= setupServer(...handlers);
  return _server;
}

// For backward compatibility if code imports server directly
export const server = new Proxy({} as ReturnType<typeof setupServer>, {
  get: (_target, prop) => getServer()[prop as keyof ReturnType<typeof setupServer>],
});
