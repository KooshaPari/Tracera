"use strict";
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
					desc = { enumerable: true, get: () => m[k] };
				}
				Object.defineProperty(o, k2, desc);
			}
		: (o, m, k, k2) => {
				if (k2 === undefined) k2 = k;
				o[k2] = m[k];
			});
var __setModuleDefault =
	(this && this.__setModuleDefault) ||
	(Object.create
		? (o, v) => {
				Object.defineProperty(o, "default", { enumerable: true, value: v });
			}
		: (o, v) => {
				o["default"] = v;
			});
var __importStar =
	(this && this.__importStar) ||
	((mod) => {
		if (mod && mod.__esModule) return mod;
		var result = {};
		if (mod != null)
			for (var k in mod)
				if (k !== "default" && Object.hasOwn(mod, k))
					__createBinding(result, mod, k);
		__setModuleDefault(result, mod);
		return result;
	});
Object.defineProperty(exports, "__esModule", { value: true });
exports.ZodRealError = exports.ZodError = void 0;
const core = __importStar(require("../core/index.cjs"));
const index_js_1 = require("../core/index.cjs");
const util = __importStar(require("../core/util.cjs"));
const initializer = (inst, issues) => {
	index_js_1.$ZodError.init(inst, issues);
	inst.name = "ZodError";
	Object.defineProperties(inst, {
		format: {
			value: (mapper) => core.formatError(inst, mapper),
			// enumerable: false,
		},
		flatten: {
			value: (mapper) => core.flattenError(inst, mapper),
			// enumerable: false,
		},
		addIssue: {
			value: (issue) => {
				inst.issues.push(issue);
				inst.message = JSON.stringify(
					inst.issues,
					util.jsonStringifyReplacer,
					2,
				);
			},
			// enumerable: false,
		},
		addIssues: {
			value: (issues) => {
				inst.issues.push(...issues);
				inst.message = JSON.stringify(
					inst.issues,
					util.jsonStringifyReplacer,
					2,
				);
			},
			// enumerable: false,
		},
		isEmpty: {
			get() {
				return inst.issues.length === 0;
			},
			// enumerable: false,
		},
	});
	// Object.defineProperty(inst, "isEmpty", {
	//   get() {
	//     return inst.issues.length === 0;
	//   },
	// });
};
exports.ZodError = core.$constructor("ZodError", initializer);
exports.ZodRealError = core.$constructor("ZodError", initializer, {
	Parent: Error,
});
// /** @deprecated Use `z.core.$ZodErrorMapCtx` instead. */
// export type ErrorMapCtx = core.$ZodErrorMapCtx;
