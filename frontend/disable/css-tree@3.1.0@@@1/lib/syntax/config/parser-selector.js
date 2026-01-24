import * as node from "../node/index-parse-selector.js";
import pseudo from "../pseudo/index.js";
import { Selector } from "../scope/index.js";

export default {
	parseContext: {
		default: "SelectorList",
		selectorList: "SelectorList",
		selector: "Selector",
	},
	scope: { Selector },
	atrule: {},
	pseudo,
	node,
};
