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
exports.readPackageJson = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function readPackageJson(dir, safe = false) {
	try {
		return await fs.readJson(path.resolve(dir, "package.json"));
	} catch (_err) {
		if (safe) {
			return {};
		} else {
			throw err;
		}
	}
}
exports.readPackageJson = readPackageJson;
//# sourceMappingURL=read-package-json.js.map
