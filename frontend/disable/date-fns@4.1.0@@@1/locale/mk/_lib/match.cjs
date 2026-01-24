"use strict";
exports.match = void 0;

var _index = require("../../_lib/buildMatchFn.cjs");
var _index2 = require("../../_lib/buildMatchPatternFn.cjs");

const matchOrdinalNumberPattern = /^(\d+)(-?[врмт][и])?/i;
const parseOrdinalNumberPattern = /\d+/i;

const matchEraPatterns = {
	narrow: /^((пр)?н\.?\s?е\.?)/i,
	abbreviated: /^((пр)?н\.?\s?е\.?)/i,
	wide: /^(пред нашата ера|нашата ера)/i,
};
const parseEraPatterns = {
	any: [/^п/i, /^н/i],
};

const matchQuarterPatterns = {
	narrow: /^[1234]/i,
	abbreviated: /^[1234](-?[врт]?и?)? кв.?/i,
	wide: /^[1234](-?[врт]?и?)? квартал/i,
};
const parseQuarterPatterns = {
	any: [/1/i, /2/i, /3/i, /4/i],
};

const matchDayPatterns = {
	narrow: /^[нпвсч]/i,
	short: /^(не|по|вт|ср|че|пе|са)/i,
	abbreviated: /^(нед|пон|вто|сре|чет|пет|саб)/i,
	wide: /^(недела|понеделник|вторник|среда|четврток|петок|сабота)/i,
};

const parseDayPatterns = {
	narrow: [/^н/i, /^п/i, /^в/i, /^с/i, /^ч/i, /^п/i, /^с/i],
	any: [/^н[ед]/i, /^п[он]/i, /^вт/i, /^ср/i, /^ч[ет]/i, /^п[ет]/i, /^с[аб]/i],
};

const matchMonthPatterns = {
	abbreviated: /^(јан|фев|мар|апр|мај|јун|јул|авг|сеп|окт|ноем|дек)/i,
	wide: /^(јануари|февруари|март|април|мај|јуни|јули|август|септември|октомври|ноември|декември)/i,
};
const parseMonthPatterns = {
	any: [
		/^ја/i,
		/^Ф/i,
		/^мар/i,
		/^ап/i,
		/^мај/i,
		/^јун/i,
		/^јул/i,
		/^ав/i,
		/^се/i,
		/^окт/i,
		/^но/i,
		/^де/i,
	],
};

const matchDayPeriodPatterns = {
	any: /^(претп|попл|полноќ|утро|пладне|вечер|ноќ)/i,
};
const parseDayPeriodPatterns = {
	any: {
		am: /претпладне/i,
		pm: /попладне/i,
		midnight: /полноќ/i,
		noon: /напладне/i,
		morning: /наутро/i,
		afternoon: /попладне/i,
		evening: /навечер/i,
		night: /ноќе/i,
	},
};

const match = (exports.match = {
	ordinalNumber: (0, _index2.buildMatchPatternFn)({
		matchPattern: matchOrdinalNumberPattern,
		parsePattern: parseOrdinalNumberPattern,
		valueCallback: (value) => parseInt(value, 10),
	}),

	era: (0, _index.buildMatchFn)({
		matchPatterns: matchEraPatterns,
		defaultMatchWidth: "wide",
		parsePatterns: parseEraPatterns,
		defaultParseWidth: "any",
	}),

	quarter: (0, _index.buildMatchFn)({
		matchPatterns: matchQuarterPatterns,
		defaultMatchWidth: "wide",
		parsePatterns: parseQuarterPatterns,
		defaultParseWidth: "any",
		valueCallback: (index) => index + 1,
	}),

	month: (0, _index.buildMatchFn)({
		matchPatterns: matchMonthPatterns,
		defaultMatchWidth: "wide",
		parsePatterns: parseMonthPatterns,
		defaultParseWidth: "any",
	}),

	day: (0, _index.buildMatchFn)({
		matchPatterns: matchDayPatterns,
		defaultMatchWidth: "wide",
		parsePatterns: parseDayPatterns,
		defaultParseWidth: "any",
	}),

	dayPeriod: (0, _index.buildMatchFn)({
		matchPatterns: matchDayPeriodPatterns,
		defaultMatchWidth: "any",
		parsePatterns: parseDayPeriodPatterns,
		defaultParseWidth: "any",
	}),
});
