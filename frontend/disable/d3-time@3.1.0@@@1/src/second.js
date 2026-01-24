import { durationSecond } from "./duration.js";
import { timeInterval } from "./interval.js";

export const second = timeInterval(
	(date) => {
		date.setTime(date - date.getMilliseconds());
	},
	(date, step) => {
		date.setTime(+date + step * durationSecond);
	},
	(start, end) => {
		return (end - start) / durationSecond;
	},
	(date) => {
		return date.getUTCSeconds();
	},
);

export const seconds = second.range;
