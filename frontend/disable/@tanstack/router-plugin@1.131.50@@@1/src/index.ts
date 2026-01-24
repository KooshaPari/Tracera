export type { Config, ConfigInput, ConfigOutput } from "./core/config";
export { configSchema, getConfig } from "./core/config";
export {
	defaultCodeSplitGroupings,
	splitRouteIdentNodes,
	tsrSplit,
} from "./core/constants";
export { unpluginRouterCodeSplitterFactory } from "./core/router-code-splitter-plugin";
export { unpluginRouterGeneratorFactory } from "./core/router-generator-plugin";
