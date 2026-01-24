import {
	FULFILLED,
	invokeCallback,
	makePromise,
	noop,
	PROMISE_ID,
	REJECTED,
	subscribe,
} from "./-internal";

import { asap } from "./asap";

export default function then(onFulfillment, onRejection) {
	const child = new this.constructor(noop);

	if (child[PROMISE_ID] === undefined) {
		makePromise(child);
	}

	const { _state } = this;

	if (_state) {
		const callback = arguments[_state - 1];
		asap(() => invokeCallback(_state, child, callback, this._result));
	} else {
		subscribe(this, child, onFulfillment, onRejection);
	}

	return child;
}
