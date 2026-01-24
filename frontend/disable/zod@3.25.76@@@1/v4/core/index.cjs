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
var __exportStar =
	(this && this.__exportStar) ||
	((m, exports) => {
		for (var p in m)
			if (p !== "default" && !Object.hasOwn(exports, p))
				__createBinding(exports, m, p);
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
exports.JSONSchema = exports.locales = exports.regexes = exports.util = void 0;
__exportStar(require("./core.cjs"), exports);
__exportStar(require("./parse.cjs"), exports);
__exportStar(require("./errors.cjs"), exports);
__exportStar(require("./schemas.cjs"), exports);
__exportStar(require("./checks.cjs"), exports);
__exportStar(require("./versions.cjs"), exports);
exports.util = __importStar(require("./util.cjs"));
exports.regexes = __importStar(require("./regexes.cjs"));
exports.locales = __importStar(require("../locales/index.cjs"));
__exportStar(require("./registries.cjs"), exports);
__exportStar(require("./doc.cjs"), exports);
__exportStar(require("./function.cjs"), exports);
__exportStar(require("./api.cjs"), exports);
__exportStar(require("./to-json-schema.cjs"), exports);
exports.JSONSchema = __importStar(require("./json-schema.cjs"));
