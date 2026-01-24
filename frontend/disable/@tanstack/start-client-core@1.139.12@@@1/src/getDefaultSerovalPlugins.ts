import type { AnySerializationAdapter } from "@tanstack/router-core";
import {
	makeSerovalPlugin,
	defaultSerovalPlugins as routerDefaultSerovalPlugins,
} from "@tanstack/router-core";
import { getStartOptions } from "./getStartOptions";

export function getDefaultSerovalPlugins() {
	const start = getStartOptions();
	const adapters = start?.serializationAdapters as
		| Array<AnySerializationAdapter>
		| undefined;
	return [
		...(adapters?.map(makeSerovalPlugin) ?? []),
		...routerDefaultSerovalPlugins,
	];
}
