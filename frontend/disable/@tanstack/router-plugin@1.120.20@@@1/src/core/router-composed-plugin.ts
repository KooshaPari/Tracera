import type { UnpluginFactory } from "unplugin";
import type { Config } from "./config";
import { unpluginRouterCodeSplitterFactory } from "./router-code-splitter-plugin";
import { unpluginRouterGeneratorFactory } from "./router-generator-plugin";
import { unpluginRouterHmrFactory } from "./router-hmr-plugin";

export const unpluginRouterComposedFactory: UnpluginFactory<
	Partial<Config> | undefined
> = (options = {}, meta) => {
	const getPlugin = (pluginFactory: UnpluginFactory<Partial<Config>>) => {
		const plugin = pluginFactory(options, meta);
		if (!Array.isArray(plugin)) {
			return [plugin];
		}
		return plugin;
	};

	const routerGenerator = getPlugin(unpluginRouterGeneratorFactory);
	const routerCodeSplitter = getPlugin(unpluginRouterCodeSplitterFactory);

	const result = [...routerGenerator, ...routerCodeSplitter];

	const isProduction = process.env.NODE_ENV === "production";

	if (!isProduction && !options.autoCodeSplitting) {
		const routerHmr = getPlugin(unpluginRouterHmrFactory);
		result.push(...routerHmr);
	}
	return result;
};
