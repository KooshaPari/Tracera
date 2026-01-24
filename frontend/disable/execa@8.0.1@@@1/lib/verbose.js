import process from "node:process";
import { debuglog } from "node:util";

export const verboseDefault = debuglog("execa").enabled;

const padField = (field, padding) => String(field).padStart(padding, "0");

const getTimestamp = () => {
	const date = new Date();
	return `${padField(date.getHours(), 2)}:${padField(date.getMinutes(), 2)}:${padField(date.getSeconds(), 2)}.${padField(date.getMilliseconds(), 3)}`;
};

export const logCommand = (escapedCommand, { verbose }) => {
	if (!verbose) {
		return;
	}

	process.stderr.write(`[${getTimestamp()}] ${escapedCommand}\n`);
};
