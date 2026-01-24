import { buildMatchFn } from "../../_lib/buildMatchFn.js";
import { buildMatchPatternFn } from "../../_lib/buildMatchPatternFn.js";

const matchOrdinalNumberPattern = /^(\d+)(th|st|nd|rd)?/i;
const parseOrdinalNumberPattern = /\d+/i;

const matchEraPatterns = {
	narrow: /^(ق|ب)/i,
	abbreviated: /^(ق\.?\s?م\.?|ق\.?\s?م\.?\s?|a\.?\s?d\.?|c\.?\s?)/i,
	wide: /^(قبل الميلاد|قبل الميلاد|بعد الميلاد|بعد الميلاد)/i,
};
const parseEraPatterns = {
	any: [/^قبل/i, /^بعد/i],
};

const matchQuarterPatterns = {
	narrow: /^[1234]/i,
	abbreviated: /^ر[1234]/i,
	wide: /^الربع [1234]/i,
};
const parseQuarterPatterns = {
	any: [/1/i, /2/i, /3/i, /4/i],
};

const matchMonthPatterns = {
	narrow: /^[يفمأمسند]/i,
	abbreviated: /^(ين|ف|مار|أب|ماي|يون|يول|أغ|س|أك|ن|د)/i,
	wide: /^(ين|ف|مار|أب|ماي|يون|يول|أغ|س|أك|ن|د)/i,
};
const parseMonthPatterns = {
	narrow: [
		/^ي/i,
		/^ف/i,
		/^م/i,
		/^أ/i,
		/^م/i,
		/^ي/i,
		/^ي/i,
		/^أ/i,
		/^س/i,
		/^أ/i,
		/^ن/i,
		/^د/i,
	],

	any: [
		/^ين/i,
		/^ف/i,
		/^مار/i,
		/^أب/i,
		/^ماي/i,
		/^يون/i,
		/^يول/i,
		/^أغ/i,
		/^س/i,
		/^أك/i,
		/^ن/i,
		/^د/i,
	],
};

const matchDayPatterns = {
	narrow: /^[حنثرخجس]/i,
	short: /^(أحد|اثنين|ثلاثاء|أربعاء|خميس|جمعة|سبت)/i,
	abbreviated: /^(أحد|اثن|ثلا|أرب|خمي|جمعة|سبت)/i,
	wide: /^(الأحد|الاثنين|الثلاثاء|الأربعاء|الخميس|الجمعة|السبت)/i,
};
const parseDayPatterns = {
	narrow: [/^ح/i, /^ن/i, /^ث/i, /^ر/i, /^خ/i, /^ج/i, /^س/i],
	wide: [
		/^الأحد/i,
		/^الاثنين/i,
		/^الثلاثاء/i,
		/^الأربعاء/i,
		/^الخميس/i,
		/^الجمعة/i,
		/^السبت/i,
	],

	any: [/^أح/i, /^اث/i, /^ث/i, /^أر/i, /^خ/i, /^ج/i, /^س/i],
};

const matchDayPeriodPatterns = {
	narrow: /^(a|p|mi|n|(in the|at) (morning|afternoon|evening|night))/i,
	any: /^([ap]\.?\s?m\.?|midnight|noon|(in the|at) (morning|afternoon|evening|night))/i,
};
const parseDayPeriodPatterns = {
	any: {
		am: /^a/i,
		pm: /^p/i,
		midnight: /^mi/i,
		noon: /^no/i,
		morning: /morning/i,
		afternoon: /afternoon/i,
		evening: /evening/i,
		night: /night/i,
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
