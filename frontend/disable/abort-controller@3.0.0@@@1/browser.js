/*globals self, window */

/*eslint-disable @mysticatea/prettier */
const { AbortController, AbortSignal } =
	typeof self !== "undefined"
		? self
		: typeof window !== "undefined"
			? window
			: /* otherwise */ undefined;
/*eslint-enable @mysticatea/prettier */

module.exports = AbortController;
module.exports.AbortSignal = AbortSignal;
module.exports.default = AbortController;
