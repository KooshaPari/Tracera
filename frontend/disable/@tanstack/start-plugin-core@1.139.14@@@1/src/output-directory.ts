import { join } from "pathe";
import type * as vite from "vite";
import type { ViteEnvironmentNames } from "./constants";
import { VITE_ENVIRONMENT_NAMES } from "./constants";

export function getClientOutputDirectory(
	userConfig: vite.UserConfig | vite.ResolvedConfig,
) {
	return getOutputDirectory(
		userConfig,
		VITE_ENVIRONMENT_NAMES.client,
		"client",
	);
}

export function getServerOutputDirectory(
	userConfig: vite.UserConfig | vite.ResolvedConfig,
) {
	return getOutputDirectory(
		userConfig,
		VITE_ENVIRONMENT_NAMES.server,
		"server",
	);
}

function getOutputDirectory(
	userConfig: vite.UserConfig | vite.ResolvedConfig,
	environmentName: ViteEnvironmentNames,
	directoryName: string,
) {
	const rootOutputDirectory = userConfig.build?.outDir ?? "dist";

	return (
		userConfig.environments?.[environmentName]?.build?.outDir ??
		join(rootOutputDirectory, directoryName)
	);
}
