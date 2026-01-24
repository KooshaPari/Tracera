var __extends =
	(this && this.__extends) ||
	(() => {
		var extendStatics = (d, b) => {
			extendStatics =
				Object.setPrototypeOf ||
				({ __proto__: [] } instanceof Array &&
					((d, b) => {
						d.__proto__ = b;
					})) ||
				((d, b) => {
					for (var p in b) if (Object.hasOwn(b, p)) d[p] = b[p];
				});
			return extendStatics(d, b);
		};
		return (d, b) => {
			if (typeof b !== "function" && b !== null)
				throw new TypeError(
					"Class extends value " + String(b) + " is not a constructor or null",
				);
			extendStatics(d, b);
			function __() {
				this.constructor = d;
			}
			d.prototype =
				b === null
					? Object.create(b)
					: ((__.prototype = b.prototype), new __());
		};
	})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApiError = void 0;
exports.toQueryParams = toQueryParams;
function toQueryParams(x) {
	if (!x) return "";
	return Object.entries(x)
		.map((_a) => {
			var k = _a[0],
				v = _a[1];
			return k && v && "".concat(k, "=").concat(encodeURIComponent(v));
		})
		.filter(Boolean)
		.join("&");
}
var ApiError = /** @class */ ((_super) => {
	__extends(ApiError, _super);
	function ApiError(response, message) {
		var _this = _super.call(this, message) || this;
		_this.response = response;
		return _this;
	}
	return ApiError;
})(Error);
exports.ApiError = ApiError;
//# sourceMappingURL=utils.js.map
