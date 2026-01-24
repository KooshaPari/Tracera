import { createWebpackPlugin } from "unplugin";
import type { Config } from "./core/config";
import { configSchema } from "./core/config";
import { unpluginRouterCodeSplitterFactory } from "./core/router-code-splitter-plugin";
import { unpluginRouterComposedFactory } from "./core/router-composed-plugin";
import { unpluginRouterGeneratorFactory } from "./core/router-generator-plugin";

/**
 * @example
 * ```ts
 * export default {
 *   // ...
 *   plugins: [TanStackRouterGeneratorWebpack()],
 * }
 * ```
 */
const TanStackRouterGeneratorWebpack = /* #__PURE__ */ createWebpackPlugin(
	unpluginRouterGeneratorFactory,
);

/**
 * @example
 * ```ts
 * export default {
 *   // ...
 *   plugins: [TanStackRouterCodeSplitterWebpack()],
 * }
 * ```
 */
const TanStackRouterCodeSplitterWebpack = /* #__PURE__ */ createWebpackPlugin(
	unpluginRouterCodeSplitterFactory,
);

/**
 * @example
 * ```ts
 * export default {
 *   // ...
 *   plugins: [TanStackRouterWebpack()],
 * }
 * ```
 */
const TanStackRouterWebpack = /* #__PURE__ */ createWebpackPlugin(
	unpluginRouterComposedFactory,
);

export default TanStackRouterWebpack;
export {
	configSchema,
	TanStackRouterWebpack,
	TanStackRouterGeneratorWebpack,
	TanStackRouterCodeSplitterWebpack,
};
export type { Config };
