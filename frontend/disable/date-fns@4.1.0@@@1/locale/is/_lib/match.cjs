"use strict";
exports.match = void 0;

var _index = require("../../_lib/buildMatchFn.cjs");
var _index2 = require("../../_lib/buildMatchPatternFn.cjs");

const matchOrdinalNumberPattern = /^(\d+)(\.)?/i;
const parseOrdinalNumberPattern = /\d+(\.)?/i;

const matchEraPatterns = {
	narrow: /^(f\.Kr\.|e\.Kr\.)/i,
	abbreviated: /^(f\.Kr\.|e\.Kr\.)/i,
	wide: /^(fyrir Krist|eftir Krist)/i,
};
const parseEraPatterns = {
	any: [/^(f\.Kr\.)/i, /^(e\.Kr\.)/i],
};

const matchQuarterPatterns = {
	narrow: /^[1234]\.?/i,
	abbreviated: /^q[1234]\.?/i,
	wide: /^[1234]\.? fjórðungur/i,
};
const parseQuarterPatterns = {
	any: [/1\.?/i, /2\.?/i, /3\.?/i, /4\.?/i],
};

const matchMonthPatterns = {
	narrow: /^[jfmásónd]/i,
	abbreviated:
		/^(jan\.|feb\.|mars\.|apríl\.|maí|júní|júlí|águst|sep\.|oct\.|nov\.|dec\.)/i,
	wide: /^(januar|febrúar|mars|apríl|maí|júní|júlí|águst|september|október|nóvember|desember)/i,
};

const parseMonthPatterns = {
	narrow: [
		/^j/i,
		/^f/i,
		/^m/i,
		/^a/i,
		/^m/i,
		/^j/i,
		/^j/i,
		/^á/i,
		/^s/i,
		/^ó/i,
		/^n/i,
		/^d/i,
	],

	any: [
		/^ja/i,
		/^f/i,
		/^mar/i,
		/^ap/i,
		/^maí/i,
		/^jún/i,
		/^júl/i,
		/^áu/i,
		/^s/i,
		/^ó/i,
		/^n/i,
		/^d/i,
	],
};

const matchDayPatterns = {
	narrow: /^[smtwf]/i,
	short: /^(su|má|þr|mi|fi|fö|la)/i,
	abbreviated: /^(sun|mán|þri|mið|fim|fös|lau)\.?/i,
	wide: /^(sunnudagur|mánudagur|þriðjudagur|miðvikudagur|fimmtudagur|föstudagur|laugardagur)/i,
};
const parseDayPatterns = {
	narrow: [/^s/i, /^m/i, /^þ/i, /^m/i, /^f/i, /^f/i, /^l/i],
	any: [/^su/i, /^má/i, /^þr/i, /^mi/i, /^fi/i, /^fö/i, /^la/i],
};

const matchDayPeriodPatterns = {
	narrow: /^(f|e|síðdegis|(á|að|um) (morgni|kvöld|nótt|miðnætti))/i,
	any: /^(fyrir hádegi|eftir hádegi|[ef]\.?h\.?|síðdegis|morgunn|(á|að|um) (morgni|kvöld|nótt|miðnætti))/i,
};
const parseDayPeriodPatterns = {
	any: {
		am: /^f/i,
		pm: /^e/i,
		midnight: /^mi/i,
		noon: /^há/i,
		morning: /morgunn/i,
		afternoon: /síðdegi/i,
		evening: /kvöld/i,
		night: /nótt/i,
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
