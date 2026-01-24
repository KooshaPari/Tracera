import { buildMatchFn } from "../../_lib/buildMatchFn.js";
import { buildMatchPatternFn } from "../../_lib/buildMatchPatternFn.js";

const matchOrdinalNumberPattern = /^(\d+)(-?(ші|шы))?/i;
const parseOrdinalNumberPattern = /\d+/i;

const matchEraPatterns = {
	narrow: /^((б )?з\.?\s?д\.?)/i,
	abbreviated: /^((б )?з\.?\s?д\.?)/i,
	wide: /^(біздің заманымызға дейін|біздің заманымыз|біздің заманымыздан)/i,
};
const parseEraPatterns = {
	any: [/^б/i, /^з/i],
};

const matchQuarterPatterns = {
	narrow: /^[1234]/i,
	abbreviated: /^[1234](-?ші)? тоқ.?/i,
	wide: /^[1234](-?ші)? тоқсан/i,
};
const parseQuarterPatterns = {
	any: [/1/i, /2/i, /3/i, /4/i],
};

const matchMonthPatterns = {
	narrow: /^(қ|а|н|с|м|мау|ш|т|қыр|қаз|қар|ж)/i,
	abbreviated: /^(қаң|ақп|нау|сәу|мам|мау|шіл|там|қыр|қаз|қар|жел)/i,
	wide: /^(қаңтар|ақпан|наурыз|сәуір|мамыр|маусым|шілде|тамыз|қыркүйек|қазан|қараша|желтоқсан)/i,
};
const parseMonthPatterns = {
	narrow: [
		/^қ/i,
		/^а/i,
		/^н/i,
		/^с/i,
		/^м/i,
		/^м/i,
		/^ш/i,
		/^т/i,
		/^қ/i,
		/^қ/i,
		/^қ/i,
		/^ж/i,
	],

	abbreviated: [
		/^қаң/i,
		/^ақп/i,
		/^нау/i,
		/^сәу/i,
		/^мам/i,
		/^мау/i,
		/^шіл/i,
		/^там/i,
		/^қыр/i,
		/^қаз/i,
		/^қар/i,
		/^жел/i,
	],

	any: [
		/^қ/i,
		/^а/i,
		/^н/i,
		/^с/i,
		/^м/i,
		/^м/i,
		/^ш/i,
		/^т/i,
		/^қ/i,
		/^қ/i,
		/^қ/i,
		/^ж/i,
	],
};

const matchDayPatterns = {
	narrow: /^(ж|д|с|с|б|ж|с)/i,
	short: /^(жс|дс|сс|ср|бс|жм|сб)/i,
	wide: /^(жексенбі|дүйсенбі|сейсенбі|сәрсенбі|бейсенбі|жұма|сенбі)/i,
};
const parseDayPatterns = {
	narrow: [/^ж/i, /^д/i, /^с/i, /^с/i, /^б/i, /^ж/i, /^с/i],
	short: [/^жс/i, /^дс/i, /^сс/i, /^ср/i, /^бс/i, /^жм/i, /^сб/i],
	any: [
		/^ж[ек]/i,
		/^д[үй]/i,
		/^сe[й]/i,
		/^сә[р]/i,
		/^б[ей]/i,
		/^ж[ұм]/i,
		/^се[н]/i,
	],
};

const matchDayPeriodPatterns = {
	narrow:
		/^Т\.?\s?[ДК]\.?|түн ортасында|((түсте|таңертең|таңда|таңертең|таңмен|таң|күндіз|күн|кеште|кеш|түнде|түн)\.?)/i,
	wide: /^Т\.?\s?[ДК]\.?|түн ортасында|((түсте|таңертең|таңда|таңертең|таңмен|таң|күндіз|күн|кеште|кеш|түнде|түн)\.?)/i,
	any: /^Т\.?\s?[ДК]\.?|түн ортасында|((түсте|таңертең|таңда|таңертең|таңмен|таң|күндіз|күн|кеште|кеш|түнде|түн)\.?)/i,
};
const parseDayPeriodPatterns = {
	any: {
		am: /^ТД/i,
		pm: /^ТК/i,
		midnight: /^түн орта/i,
		noon: /^күндіз/i,
		morning: /таң/i,
		afternoon: /түс/i,
		evening: /кеш/i,
		night: /түн/i,
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
		defaultMatchWidth: "wide",
		parsePatterns: parseDayPeriodPatterns,
		defaultParseWidth: "any",
	}),
};
