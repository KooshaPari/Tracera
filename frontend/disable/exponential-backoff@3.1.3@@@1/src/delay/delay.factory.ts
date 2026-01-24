import type { IBackOffOptions } from "../options";
import { AlwaysDelay } from "./always/always.delay";
import type { IDelay } from "./delay.interface";
import { SkipFirstDelay } from "./skip-first/skip-first.delay";

export function DelayFactory(
	options: IBackOffOptions,
	attempt: number,
): IDelay {
	const delay = initDelayClass(options);
	delay.setAttemptNumber(attempt);
	return delay;
}

function initDelayClass(options: IBackOffOptions) {
	if (!options.delayFirstAttempt) {
		return new SkipFirstDelay(options);
	}

	return new AlwaysDelay(options);
}
