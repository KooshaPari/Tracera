import { y18n as _y18n } from "./build/lib/index.js";
import shim from "./build/lib/platform-shims/node.js";

const y18n = (opts) => {
	return _y18n(opts, shim);
};

export default y18n;
