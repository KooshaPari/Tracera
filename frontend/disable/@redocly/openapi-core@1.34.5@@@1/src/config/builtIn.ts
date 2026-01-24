import { decorators as arazzo1Decorators } from "../decorators/arazzo";
import { decorators as async2Decorators } from "../decorators/async2";
import { decorators as async3Decorators } from "../decorators/async3";
import { decorators as oas2Decorators } from "../decorators/oas2";
import { decorators as oas3Decorators } from "../decorators/oas3";
import { decorators as overlay1Decorators } from "../decorators/overlay1";
import {
	rules as arazzo1Rules,
	preprocessors as arazzoPreprocessors,
} from "../rules/arazzo";
import {
	preprocessors as async2Preprocessors,
	rules as async2Rules,
} from "../rules/async2";
import {
	preprocessors as async3Preprocessors,
	rules as async3Rules,
} from "../rules/async3";
import {
	preprocessors as oas2Preprocessors,
	rules as oas2Rules,
} from "../rules/oas2";
import {
	preprocessors as oas3Preprocessors,
	rules as oas3Rules,
} from "../rules/oas3";
import {
	preprocessors as overlay1Preprocessors,
	rules as overlay1Rules,
} from "../rules/overlay1";
import all from "./all";
import minimal from "./minimal";
import recommended from "./recommended";
import recommendedStrict from "./recommended-strict";
import spec from "./spec";

import type { Plugin, StyleguideRawConfig } from "./types";

export const builtInConfigs: Record<string, StyleguideRawConfig> = {
	recommended,
	"recommended-strict": recommendedStrict,
	minimal,
	all,
	spec,
	"redocly-registry": {
		decorators: { "registry-dependencies": "on" },
	},
};

export const defaultPlugin: Plugin<"built-in"> = {
	id: "", // default plugin doesn't have id
	rules: {
		oas3: oas3Rules,
		oas2: oas2Rules,
		async2: async2Rules,
		async3: async3Rules,
		arazzo1: arazzo1Rules,
		overlay1: overlay1Rules,
	},
	preprocessors: {
		oas3: oas3Preprocessors,
		oas2: oas2Preprocessors,
		async2: async2Preprocessors,
		async3: async3Preprocessors,
		arazzo1: arazzoPreprocessors,
		overlay1: overlay1Preprocessors,
	},
	decorators: {
		oas3: oas3Decorators,
		oas2: oas2Decorators,
		async2: async2Decorators,
		async3: async3Decorators,
		arazzo1: arazzo1Decorators,
		overlay1: overlay1Decorators,
	},
	configs: builtInConfigs,
};
