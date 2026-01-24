var __createBinding =
	(this && this.__createBinding) ||
	(Object.create
		? (o, m, k, k2) => {
				if (k2 === undefined) k2 = k;
				var desc = Object.getOwnPropertyDescriptor(m, k);
				if (
					!desc ||
					("get" in desc ? !m.__esModule : desc.writable || desc.configurable)
				) {
					desc = {
						enumerable: true,
						get: () => m[k],
					};
				}
				Object.defineProperty(o, k2, desc);
			}
		: (o, m, k, k2) => {
				if (k2 === undefined) k2 = k;
				o[k2] = m[k];
			});
var __exportStar =
	(this && this.__exportStar) ||
	((m, exports) => {
		for (var p in m)
			if (p !== "default" && !Object.hasOwn(exports, p))
				__createBinding(exports, m, p);
	});
Object.defineProperty(exports, "__esModule", { value: true });
exports.stringify = exports.parse = exports.isTraversal = void 0;
__exportStar(require("./types"), exports);
var parse_1 = require("./parse");
Object.defineProperty(exports, "isTraversal", {
	enumerable: true,
	get: () => parse_1.isTraversal,
});
Object.defineProperty(exports, "parse", {
	enumerable: true,
	get: () => parse_1.parse,
});
var stringify_1 = require("./stringify");
Object.defineProperty(exports, "stringify", {
	enumerable: true,
	get: () => stringify_1.stringify,
});
