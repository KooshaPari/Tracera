"use strict";
exports.formatRelative = void 0;

const formatRelativeLocale = {
	lastWeek: "'ថ្ងៃ'eeee'ស​ប្តា​ហ៍​មុនម៉ោង' p",
	yesterday: "'ម្សិលមិញនៅម៉ោង' p",
	today: "'ថ្ងៃនេះម៉ោង' p",
	tomorrow: "'ថ្ងៃស្អែកម៉ោង' p",
	nextWeek: "'ថ្ងៃ'eeee'ស​ប្តា​ហ៍​ក្រោយម៉ោង' p",
	other: "P",
};

const formatRelative = (token, _date, _baseDate, _options) =>
	formatRelativeLocale[token];
exports.formatRelative = formatRelative;
