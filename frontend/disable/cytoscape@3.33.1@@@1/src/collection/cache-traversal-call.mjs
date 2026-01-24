import * as is from "../is.mjs";
import * as util from "../util/index.mjs";

const cache = (fn, name) =>
	function traversalCache(arg1, arg2, arg3, arg4) {
		const selectorOrEles = arg1;
		let key;

		if (selectorOrEles == null) {
			key = "";
		} else if (
			is.elementOrCollection(selectorOrEles) &&
			selectorOrEles.length === 1
		) {
			key = selectorOrEles.id();
		}

		if (this.length === 1 && key) {
			const _p = this[0]._private;
			const tch = (_p.traversalCache = _p.traversalCache || {});
			const ch = (tch[name] = tch[name] || []);
			const hash = util.hashString(key);
			const cacheHit = ch[hash];

			if (cacheHit) {
				return cacheHit;
			} else {
				return (ch[hash] = fn.call(this, arg1, arg2, arg3, arg4));
			}
		} else {
			return fn.call(this, arg1, arg2, arg3, arg4);
		}
	};

export default cache;
