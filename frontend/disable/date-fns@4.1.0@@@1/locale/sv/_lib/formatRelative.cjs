"use strict";
exports.formatRelative = void 0;

const formatRelativeLocale = {
	lastWeek: "'i' EEEE's kl.' p",
	yesterday: "'igår kl.' p",
	today: "'idag kl.' p",
	tomorrow: "'imorgon kl.' p",
	nextWeek: "EEEE 'kl.' p",
	other: "P",
};

const formatRelative = (token, _date, _baseDate, _options) =>
	formatRelativeLocale[token];
exports.formatRelative = formatRelative;
