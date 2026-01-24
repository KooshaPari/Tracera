import { JitterFactory } from "../jitter/jitter.factory";
import type { IBackOffOptions } from "../options";
import type { IDelay } from "./delay.interface";

export abstract class Delay implements IDelay {
	protected attempt = 0;
	constructor(private options: IBackOffOptions) {}

	public apply() {
		return new Promise((resolve) => setTimeout(resolve, this.jitteredDelay));
	}

	public setAttemptNumber(attempt: number) {
		this.attempt = attempt;
	}

	private get jitteredDelay() {
		const jitter = JitterFactory(this.options);
		return jitter(this.delay);
	}

	private get delay() {
		const constant = this.options.startingDelay;
		const base = this.options.timeMultiple;
		const power = this.numOfDelayedAttempts;
		const delay = constant * base ** power;

		return Math.min(delay, this.options.maxDelay);
	}

	protected get numOfDelayedAttempts() {
		return this.attempt;
	}
}
