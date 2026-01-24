import * as util from "../util/index.mjs";

export const stateSelectors = [
	{
		selector: ":selected",
		matches: (ele) => ele.selected(),
	},
	{
		selector: ":unselected",
		matches: (ele) => !ele.selected(),
	},
	{
		selector: ":selectable",
		matches: (ele) => ele.selectable(),
	},
	{
		selector: ":unselectable",
		matches: (ele) => !ele.selectable(),
	},
	{
		selector: ":locked",
		matches: (ele) => ele.locked(),
	},
	{
		selector: ":unlocked",
		matches: (ele) => !ele.locked(),
	},
	{
		selector: ":visible",
		matches: (ele) => ele.visible(),
	},
	{
		selector: ":hidden",
		matches: (ele) => !ele.visible(),
	},
	{
		selector: ":transparent",
		matches: (ele) => ele.transparent(),
	},
	{
		selector: ":grabbed",
		matches: (ele) => ele.grabbed(),
	},
	{
		selector: ":free",
		matches: (ele) => !ele.grabbed(),
	},
	{
		selector: ":removed",
		matches: (ele) => ele.removed(),
	},
	{
		selector: ":inside",
		matches: (ele) => !ele.removed(),
	},
	{
		selector: ":grabbable",
		matches: (ele) => ele.grabbable(),
	},
	{
		selector: ":ungrabbable",
		matches: (ele) => !ele.grabbable(),
	},
	{
		selector: ":animated",
		matches: (ele) => ele.animated(),
	},
	{
		selector: ":unanimated",
		matches: (ele) => !ele.animated(),
	},
	{
		selector: ":parent",
		matches: (ele) => ele.isParent(),
	},
	{
		selector: ":childless",
		matches: (ele) => ele.isChildless(),
	},
	{
		selector: ":child",
		matches: (ele) => ele.isChild(),
	},
	{
		selector: ":orphan",
		matches: (ele) => ele.isOrphan(),
	},
	{
		selector: ":nonorphan",
		matches: (ele) => ele.isChild(),
	},
	{
		selector: ":compound",
		matches: (ele) => {
			if (ele.isNode()) {
				return ele.isParent();
			} else {
				return ele.source().isParent() || ele.target().isParent();
			}
		},
	},
	{
		selector: ":loop",
		matches: (ele) => ele.isLoop(),
	},
	{
		selector: ":simple",
		matches: (ele) => ele.isSimple(),
	},
	{
		selector: ":active",
		matches: (ele) => ele.active(),
	},
	{
		selector: ":inactive",
		matches: (ele) => !ele.active(),
	},
	{
		selector: ":backgrounding",
		matches: (ele) => ele.backgrounding(),
	},
	{
		selector: ":nonbackgrounding",
		matches: (ele) => !ele.backgrounding(),
	},
].sort((a, b) => {
	// n.b. selectors that are starting substrings of others must have the longer ones first
	return util.sort.descending(a.selector, b.selector);
});

const lookup = (() => {
	const selToFn = {};
	let s;

	for (let i = 0; i < stateSelectors.length; i++) {
		s = stateSelectors[i];

		selToFn[s.selector] = s.matches;
	}

	return selToFn;
})();

export const stateSelectorMatches = (sel, ele) => lookup[sel](ele);

export const stateSelectorRegex =
	"(" + stateSelectors.map((s) => s.selector).join("|") + ")";
