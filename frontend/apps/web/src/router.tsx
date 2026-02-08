import { createRouter as createTanStackRouter } from '@tanstack/react-router';

import { routeTree } from './routeTree.gen';

type RouterInstance = ReturnType<typeof createTanStackRouter>;

let routerInstance: RouterInstance | undefined;

function createRouter(): RouterInstance {
  if (!routerInstance) {
    routerInstance = createTanStackRouter({
      defaultPreload: 'intent',
      routeTree: routeTree as any,
    });
  }
  return routerInstance;
}

function getRouter(): RouterInstance {
  if (!routerInstance) {
    routerInstance = createRouter();
  }
  return routerInstance;
}

type AppRouter = ReturnType<typeof createRouter>;

export { createRouter, getRouter, type AppRouter };
