"use strict";
exports.match = void 0;

var _index = require("../../_lib/buildMatchFn.cjs");
var _index2 = require("../../_lib/buildMatchPatternFn.cjs");

const matchOrdinalNumberPattern = /^(\d+)\.?/i;
const parseOrdinalNumberPattern = /\d+/i;

const matchEraPatterns = {
	narrow: /^(ie\.|isz\.)/i,
	abbreviated: /^(i\.\s?e\.?|b?\s?c\s?e|i\.\s?sz\.?)/i,
	wide: /^(Krisztus előtt|időszámításunk előtt|időszámításunk szerint|i\. sz\.)/i,
};
const parseEraPatterns = {
	narrow: [/ie/i, /isz/i],
	abbreviated: [/^(i\.?\s?e\.?|b\s?ce)/i, /^(i\.?\s?sz\.?|c\s?e)/i],
	any: [/előtt/i, /(szerint|i. sz.)/i],
};

const matchQuarterPatterns = {
	narrow: /^[1234]\.?/i,
	abbreviated: /^[1234]?\.?\s?n\.év/i,
	wide: /^([1234]|I|II|III|IV)?\.?\s?negyedév/i,
};
const parseQuarterPatterns = {
	any: [/1|I$/i, /2|II$/i, /3|III/i, /4|IV/i],
};

const matchMonthPatterns = {
	narrow: /^[jfmaásond]|sz/i,
	abbreviated:
		/^(jan\.?|febr\.?|márc\.?|ápr\.?|máj\.?|jún\.?|júl\.?|aug\.?|szept\.?|okt\.?|nov\.?|dec\.?)/i,
	wide: /^(január|február|március|április|május|június|július|augusztus|szeptember|október|november|december)/i,
};
const parseMonthPatterns = {
	narrow: [
		/^j/i,
		/^f/i,
		/^m/i,
		/^a|á/i,
		/^m/i,
		/^j/i,
		/^j/i,
		/^a/i,
		/^s|sz/i,
		/^o/i,
		/^n/i,
		/^d/i,
	],

	any: [
		/^ja/i,
		/^f/i,
		/^már/i,
		/^áp/i,
		/^máj/i,
		/^jún/i,
		/^júl/i,
		/^au/i,
		/^s/i,
		/^o/i,
		/^n/i,
		/^d/i,
	],
};

const matchDayPatterns = {
	narrow: /^([vhkpc]|sz|cs|sz)/i,
	short: /^([vhkp]|sze|cs|szo)/i,
	abbreviated: /^([vhkp]|sze|cs|szo)/i,
	wide: /^(vasárnap|hétfő|kedd|szerda|csütörtök|péntek|szombat)/i,
};
const parseDayPatterns = {
	narrow: [/^v/i, /^h/i, /^k/i, /^sz/i, /^c/i, /^p/i, /^sz/i],
	any: [/^v/i, /^h/i, /^k/i, /^sze/i, /^c/i, /^p/i, /^szo/i],
};

const matchDayPeriodPatterns = {
	any: /^((de|du)\.?|éjfél|délután|dél|reggel|este|éjjel)/i,
};
const parseDayPeriodPatterns = {
	any: {
		am: /^de\.?/i,
		pm: /^du\.?/i,
		midnight: /^éjf/i,
		noon: /^dé/i,
		morning: /reg/i,
		afternoon: /^délu\.?/i,
		evening: /es/i,
		night: /éjj/i,
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
