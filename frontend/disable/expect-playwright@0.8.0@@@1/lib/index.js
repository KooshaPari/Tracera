var __importDefault =
	(this && this.__importDefault) ||
	((mod) => (mod && mod.__esModule ? mod : { default: mod }));
Object.defineProperty(exports, "__esModule", { value: true });
exports.matchers = void 0;
const matchers_1 = __importDefault(require("./matchers"));
exports.matchers = matchers_1.default;
// @ts-expect-error
if (typeof global.expect !== "undefined") {
	// @ts-expect-error
	global.expect.extend(matchers_1.default);
}
