import { decorators as arazzo1Decorators } from "../decorators/arazzo/index.js";
import { decorators as async2Decorators } from "../decorators/async2/index.js";
import { decorators as async3Decorators } from "../decorators/async3/index.js";
import { decorators as oas2Decorators } from "../decorators/oas2/index.js";
import { decorators as oas3Decorators } from "../decorators/oas3/index.js";
import { decorators as overlay1Decorators } from "../decorators/overlay1/index.js";
import {
	rules as arazzo1Rules,
	preprocessors as arazzoPreprocessors,
} from "../rules/arazzo/index.js";
import {
	preprocessors as async2Preprocessors,
	rules as async2Rules,
} from "../rules/async2/index.js";
import {
	preprocessors as async3Preprocessors,
	rules as async3Rules,
} from "../rules/async3/index.js";
import {
	preprocessors as oas2Preprocessors,
	rules as oas2Rules,
} from "../rules/oas2/index.js";
import {
	preprocessors as oas3Preprocessors,
	rules as oas3Rules,
} from "../rules/oas3/index.js";
import {
	preprocessors as overlay1Preprocessors,
	rules as overlay1Rules,
} from "../rules/overlay1/index.js";
import all from "./all.js";
import minimal from "./minimal.js";
import recommended from "./recommended.js";
import recommendedStrict from "./recommended-strict.js";
import spec from "./spec.js";
export const builtInConfigs = {
	recommended,
	"recommended-strict": recommendedStrict,
	minimal,
	all,
	spec,
};
export const defaultPlugin = {
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
//# sourceMappingURL=builtIn.js.map
