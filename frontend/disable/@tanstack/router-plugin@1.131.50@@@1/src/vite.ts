import { createVitePlugin } from "unplugin";
import type { Config } from "./core/config";
import { configSchema } from "./core/config";
import { unpluginRouteAutoImportFactory } from "./core/route-autoimport-plugin";
import { unpluginRouterCodeSplitterFactory } from "./core/router-code-splitter-plugin";
import { unpluginRouterComposedFactory } from "./core/router-composed-plugin";
import { unpluginRouterGeneratorFactory } from "./core/router-generator-plugin";

const tanstackRouterAutoImport = createVitePlugin(
	unpluginRouteAutoImportFactory,
);

/**
 * @example
 * ```ts
 * export default defineConfig({
 *   plugins: [tanstackRouterGenerator()],
 *   // ...
 * })
 * ```
 */
const tanstackRouterGenerator = createVitePlugin(
	unpluginRouterGeneratorFactory,
);

/**
 * @example
 * ```ts
 * export default defineConfig({
 *   plugins: [tanStackRouterCodeSplitter()],
 *   // ...
 * })
 * ```
 */
const tanStackRouterCodeSplitter = createVitePlugin(
	unpluginRouterCodeSplitterFactory,
);

/**
 * @example
 * ```ts
 * export default defineConfig({
 *   plugins: [tanstackRouter()],
 *   // ...
 * })
 * ```
 */
const tanstackRouter = createVitePlugin(unpluginRouterComposedFactory);

/**
 * @deprecated Use `tanstackRouter` instead.
 */
const TanStackRouterVite = tanstackRouter;

export default tanstackRouter;
export {
	configSchema,
	tanstackRouterAutoImport,
	tanStackRouterCodeSplitter,
	tanstackRouterGenerator,
	TanStackRouterVite,
	tanstackRouter,
};

export type { Config };
