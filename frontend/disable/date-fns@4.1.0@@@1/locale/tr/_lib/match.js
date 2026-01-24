import { buildMatchFn } from "../../_lib/buildMatchFn.js";
import { buildMatchPatternFn } from "../../_lib/buildMatchPatternFn.js";

const matchOrdinalNumberPattern = /^(\d+)(\.)?/i;
const parseOrdinalNumberPattern = /\d+/i;

const matchEraPatterns = {
	narrow: /^(mö|ms)/i,
	abbreviated: /^(mö|ms)/i,
	wide: /^(milattan önce|milattan sonra)/i,
};
const parseEraPatterns = {
	any: [/(^mö|^milattan önce)/i, /(^ms|^milattan sonra)/i],
};

const matchQuarterPatterns = {
	narrow: /^[1234]/i,
	abbreviated: /^[1234]ç/i,
	wide: /^((i|İ)lk|(i|İ)kinci|üçüncü|son) çeyrek/i,
};
const parseQuarterPatterns = {
	any: [/1/i, /2/i, /3/i, /4/i],
	abbreviated: [/1ç/i, /2ç/i, /3ç/i, /4ç/i],
	wide: [
		/^(i|İ)lk çeyrek/i,
		/(i|İ)kinci çeyrek/i,
		/üçüncü çeyrek/i,
		/son çeyrek/i,
	],
};

const matchMonthPatterns = {
	narrow: /^[oşmnhtaek]/i,
	abbreviated: /^(oca|şub|mar|nis|may|haz|tem|ağu|eyl|eki|kas|ara)/i,
	wide: /^(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)/i,
};
const parseMonthPatterns = {
	narrow: [
		/^o/i,
		/^ş/i,
		/^m/i,
		/^n/i,
		/^m/i,
		/^h/i,
		/^t/i,
		/^a/i,
		/^e/i,
		/^e/i,
		/^k/i,
		/^a/i,
	],

	any: [
		/^o/i,
		/^ş/i,
		/^mar/i,
		/^n/i,
		/^may/i,
		/^h/i,
		/^t/i,
		/^ağ/i,
		/^ey/i,
		/^ek/i,
		/^k/i,
		/^ar/i,
	],
};

const matchDayPatterns = {
	narrow: /^[psçc]/i,
	short: /^(pz|pt|sa|ça|pe|cu|ct)/i,
	abbreviated: /^(paz|pzt|sal|çar|per|cum|cts)/i,
	wide: /^(pazar(?!tesi)|pazartesi|salı|çarşamba|perşembe|cuma(?!rtesi)|cumartesi)/i,
};
const parseDayPatterns = {
	narrow: [/^p/i, /^p/i, /^s/i, /^ç/i, /^p/i, /^c/i, /^c/i],
	any: [/^pz/i, /^pt/i, /^sa/i, /^ça/i, /^pe/i, /^cu/i, /^ct/i],
	wide: [
		/^pazar(?!tesi)/i,
		/^pazartesi/i,
		/^salı/i,
		/^çarşamba/i,
		/^perşembe/i,
		/^cuma(?!rtesi)/i,
		/^cumartesi/i,
	],
};

const matchDayPeriodPatterns = {
	narrow: /^(öö|ös|gy|ö|sa|ös|ak|ge)/i,
	any: /^(ö\.?\s?[ös]\.?|öğleden sonra|gece yarısı|öğle|(sabah|öğ|akşam|gece)(leyin))/i,
};
const parseDayPeriodPatterns = {
	any: {
		am: /^ö\.?ö\.?/i,
		pm: /^ö\.?s\.?/i,
		midnight: /^(gy|gece yarısı)/i,
		noon: /^öğ/i,
		morning: /^sa/i,
		afternoon: /^öğleden sonra/i,
		evening: /^ak/i,
		night: /^ge/i,
	},
};

export const match = {
	ordinalNumber: buildMatchPatternFn({
		matchPattern: matchOrdinalNumberPattern,
		parsePattern: parseOrdinalNumberPattern,
		valueCallback: (value) => parseInt(value, 10),
	}),

	era: buildMatchFn({
		matchPatterns: matchEraPatterns,
		defaultMatchWidth: "wide",
		parsePatterns: parseEraPatterns,
		defaultParseWidth: "any",
	}),

	quarter: buildMatchFn({
		matchPatterns: matchQuarterPatterns,
		defaultMatchWidth: "wide",
		parsePatterns: parseQuarterPatterns,
		defaultParseWidth: "any",
		valueCallback: (index) => index + 1,
	}),

	month: buildMatchFn({
		matchPatterns: matchMonthPatterns,
		defaultMatchWidth: "wide",
		parsePatterns: parseMonthPatterns,
		defaultParseWidth: "any",
	}),

	day: buildMatchFn({
		matchPatterns: matchDayPatterns,
		defaultMatchWidth: "wide",
		parsePatterns: parseDayPatterns,
		defaultParseWidth: "any",
	}),

	dayPeriod: buildMatchFn({
		matchPatterns: matchDayPeriodPatterns,
		defaultMatchWidth: "any",
		parsePatterns: parseDayPeriodPatterns,
		defaultParseWidth: "any",
	}),
};
