import { createRouter as createTanStackRouter } from '@tanstack/react-router';

import { routeTree } from './routeTree.gen';

type RouterInstance = ReturnType<typeof createTanStackRouter>;

let routerInstance: RouterInstance | undefined;

function createRouter(): RouterInstance {
  routerInstance ??= createTanStackRouter({
    defaultPreload: 'intent',
    routeTree: routeTree as any,
  });
  return routerInstance;
}

function getRouter(): RouterInstance {
  routerInstance ??= createRouter();
  return routerInstance;
}

type AppRouter = ReturnType<typeof createRouter>;

export { createRouter, getRouter, type AppRouter };
