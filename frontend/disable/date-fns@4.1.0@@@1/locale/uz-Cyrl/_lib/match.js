import { buildMatchFn } from "../../_lib/buildMatchFn.js";
import { buildMatchPatternFn } from "../../_lib/buildMatchPatternFn.js";

const matchOrdinalNumberPattern = /^(\d+)(чи)?/i;
const parseOrdinalNumberPattern = /\d+/i;

const matchEraPatterns = {
	narrow: /^(м\.а|м\.)/i,
	abbreviated: /^(м\.а|м\.)/i,
	wide: /^(милоддан аввал|милоддан кейин)/i,
};
const parseEraPatterns = {
	any: [/^м/i, /^а/i],
};

const matchQuarterPatterns = {
	narrow: /^[1234]/i,
	abbreviated: /^[1234]-чор./i,
	wide: /^[1234]-чорак/i,
};
const parseQuarterPatterns = {
	any: [/1/i, /2/i, /3/i, /4/i],
};

const matchMonthPatterns = {
	narrow: /^[яфмамииасонд]/i,
	abbreviated: /^(янв|фев|мар|апр|май|июн|июл|авг|сен|окт|ноя|дек)/i,
	wide: /^(январ|феврал|март|апрел|май|июн|июл|август|сентабр|октабр|ноябр|декабр)/i,
};
const parseMonthPatterns = {
	narrow: [
		/^я/i,
		/^ф/i,
		/^м/i,
		/^а/i,
		/^м/i,
		/^и/i,
		/^и/i,
		/^а/i,
		/^с/i,
		/^о/i,
		/^н/i,
		/^д/i,
	],

	any: [
		/^я/i,
		/^ф/i,
		/^мар/i,
		/^ап/i,
		/^май/i,
		/^июн/i,
		/^июл/i,
		/^ав/i,
		/^с/i,
		/^о/i,
		/^н/i,
		/^д/i,
	],
};

const matchDayPatterns = {
	narrow: /^[ядсчпжш]/i,
	short: /^(як|ду|се|чо|па|жу|ша)/i,
	abbreviated: /^(якш|душ|сеш|чор|пай|жум|шан)/i,
	wide: /^(якшанба|душанба|сешанба|чоршанба|пайшанба|жума|шанба)/i,
};
const parseDayPatterns = {
	narrow: [/^я/i, /^д/i, /^с/i, /^ч/i, /^п/i, /^ж/i, /^ш/i],
	any: [/^як/i, /^ду/i, /^се/i, /^чор/i, /^пай/i, /^жу/i, /^шан/i],
};

const matchDayPeriodPatterns = {
	any: /^(п\.о\.|п\.к\.|ярим тун|пешиндан кейин|(эрталаб|пешиндан кейин|кечаси|тун))/i,
};
const parseDayPeriodPatterns = {
	any: {
		am: /^п\.о\./i,
		pm: /^п\.к\./i,
		midnight: /^ярим тун/i,
		noon: /^пешиндан кейин/i,
		morning: /эрталаб/i,
		afternoon: /пешиндан кейин/i,
		evening: /кечаси/i,
		night: /тун/i,
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
