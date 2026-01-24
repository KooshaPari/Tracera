import {
	FULFILLED,
	fulfill,
	getThen,
	handleMaybeThenable,
	makePromise,
	noop,
	PENDING,
	PROMISE_ID,
	REJECTED,
	reject,
	subscribe,
} from "./-internal";
import Promise from "./promise";
import originalResolve from "./promise/resolve";
import then from "./then";
import originalThen from "./then";
import { isArray, isMaybeThenable } from "./utils";

export default Enumerator;
function Enumerator(Constructor, input) {
	this._instanceConstructor = Constructor;
	this.promise = new Constructor(noop);

	if (!this.promise[PROMISE_ID]) {
		makePromise(this.promise);
	}

	if (isArray(input)) {
		this._input = input;
		this.length = input.length;
		this._remaining = input.length;

		this._result = new Array(this.length);

		if (this.length === 0) {
			fulfill(this.promise, this._result);
		} else {
			this.length = this.length || 0;
			this._enumerate();
			if (this._remaining === 0) {
				fulfill(this.promise, this._result);
			}
		}
	} else {
		reject(this.promise, validationError());
	}
}

function validationError() {
	return new Error("Array Methods must be provided an Array");
}

Enumerator.prototype._enumerate = function () {
	const { length, _input } = this;

	for (let i = 0; this._state === PENDING && i < length; i++) {
		this._eachEntry(_input[i], i);
	}
};

Enumerator.prototype._eachEntry = function (entry, i) {
	const c = this._instanceConstructor;
	const { resolve } = c;

	if (resolve === originalResolve) {
		const then = getThen(entry);

		if (then === originalThen && entry._state !== PENDING) {
			this._settledAt(entry._state, i, entry._result);
		} else if (typeof then !== "function") {
			this._remaining--;
			this._result[i] = entry;
		} else if (c === Promise) {
			const promise = new c(noop);
			handleMaybeThenable(promise, entry, then);
			this._willSettleAt(promise, i);
		} else {
			this._willSettleAt(new c((resolve) => resolve(entry)), i);
		}
	} else {
		this._willSettleAt(resolve(entry), i);
	}
};

Enumerator.prototype._settledAt = function (state, i, value) {
	const { promise } = this;

	if (promise._state === PENDING) {
		this._remaining--;

		if (state === REJECTED) {
			reject(promise, value);
		} else {
			this._result[i] = value;
		}
	}

	if (this._remaining === 0) {
		fulfill(promise, this._result);
	}
};

Enumerator.prototype._willSettleAt = function (promise, i) {
	subscribe(
		promise,
		undefined,
		(value) => this._settledAt(FULFILLED, i, value),
		(reason) => this._settledAt(REJECTED, i, reason),
	);
};
