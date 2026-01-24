"use strict";
exports.match = void 0;

var _index = require("../../_lib/buildMatchFn.cjs");
var _index2 = require("../../_lib/buildMatchPatternFn.cjs");

const matchOrdinalNumberPattern = /^(\d+)(ος|η|ο)?/i;
const parseOrdinalNumberPattern = /\d+/i;

const matchEraPatterns = {
	narrow: /^(πΧ|μΧ)/i,
	abbreviated: /^(π\.?\s?χ\.?|π\.?\s?κ\.?\s?χ\.?|μ\.?\s?χ\.?|κ\.?\s?χ\.?)/i,
	wide: /^(προ Χριστο(ύ|υ)|πριν απ(ό|ο) την Κοιν(ή|η) Χρονολογ(ί|ι)α|μετ(ά|α) Χριστ(ό|ο)ν|Κοιν(ή|η) Χρονολογ(ί|ι)α)/i,
};
const parseEraPatterns = {
	any: [/^π/i, /^(μ|κ)/i],
};

const matchQuarterPatterns = {
	narrow: /^[1234]/i,
	abbreviated: /^τ[1234]/i,
	wide: /^[1234]ο? τρ(ί|ι)μηνο/i,
};
const parseQuarterPatterns = {
	any: [/1/i, /2/i, /3/i, /4/i],
};

const matchMonthPatterns = {
	narrow: /^[ιφμαμιιασονδ]/i,
	abbreviated:
		/^(ιαν|φεβ|μ[άα]ρ|απρ|μ[άα][ιΐ]|ιο[ύυ]ν|ιο[ύυ]λ|α[ύυ]γ|σεπ|οκτ|νο[έε]|δεκ)/i,
	wide: /^(μ[άα][ιΐ]|α[ύυ]γο[υύ]στ)(ος|ου)|(ιανου[άα]ρ|φεβρου[άα]ρ|μ[άα]ρτ|απρ[ίι]λ|ιο[ύυ]ν|ιο[ύυ]λ|σεπτ[έε]μβρ|οκτ[ώω]βρ|νο[έε]μβρ|δεκ[έε]μβρ)(ιος|ίου)/i,
};
const parseMonthPatterns = {
	narrow: [
		/^ι/i,
		/^φ/i,
		/^μ/i,
		/^α/i,
		/^μ/i,
		/^ι/i,
		/^ι/i,
		/^α/i,
		/^σ/i,
		/^ο/i,
		/^ν/i,
		/^δ/i,
	],

	any: [
		/^ια/i,
		/^φ/i,
		/^μ[άα]ρ/i,
		/^απ/i,
		/^μ[άα][ιΐ]/i,
		/^ιο[ύυ]ν/i,
		/^ιο[ύυ]λ/i,
		/^α[ύυ]/i,
		/^σ/i,
		/^ο/i,
		/^ν/i,
		/^δ/i,
	],
};

const matchDayPatterns = {
	narrow: /^[κδτπσ]/i,
	short: /^(κυ|δε|τρ|τε|π[εέ]|π[αά]|σ[αά])/i,
	abbreviated: /^(κυρ|δευ|τρι|τετ|πεμ|παρ|σαβ)/i,
	wide: /^(κυριακ(ή|η)|δευτ(έ|ε)ρα|τρ(ί|ι)τη|τετ(ά|α)ρτη|π(έ|ε)μπτη|παρασκευ(ή|η)|σ(ά|α)ββατο)/i,
};
const parseDayPatterns = {
	narrow: [/^κ/i, /^δ/i, /^τ/i, /^τ/i, /^π/i, /^π/i, /^σ/i],
	any: [/^κ/i, /^δ/i, /^τρ/i, /^τε/i, /^π[εέ]/i, /^π[αά]/i, /^σ/i],
};

const matchDayPeriodPatterns = {
	narrow:
		/^(πμ|μμ|μεσ(ά|α)νυχτα|μεσημ(έ|ε)ρι|πρω(ί|ι)|απ(ό|ο)γευμα|βρ(ά|α)δυ|ν(ύ|υ)χτα)/i,
	any: /^([πμ]\.?\s?μ\.?|μεσ(ά|α)νυχτα|μεσημ(έ|ε)ρι|πρω(ί|ι)|απ(ό|ο)γευμα|βρ(ά|α)δυ|ν(ύ|υ)χτα)/i,
};
const parseDayPeriodPatterns = {
	any: {
		am: /^πμ|π\.\s?μ\./i,
		pm: /^μμ|μ\.\s?μ\./i,
		midnight: /^μεσάν/i,
		noon: /^μεσημ(έ|ε)/i,
		morning: /πρω(ί|ι)/i,
		afternoon: /απ(ό|ο)γευμα/i,
		evening: /βρ(ά|α)δυ/i,
		night: /ν(ύ|υ)χτα/i,
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
