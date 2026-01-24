"use strict";
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
exports.cssDiff = void 0;
exports.diffCss = diffCss;
var base_js_1 = require("./base.js");
var CssDiff = /** @class */ ((_super) => {
	__extends(CssDiff, _super);
	function CssDiff() {
		return (_super !== null && _super.apply(this, arguments)) || this;
	}
	CssDiff.prototype.tokenize = (value) => value.split(/([{}:;,]|\s+)/);
	return CssDiff;
})(base_js_1.default);
exports.cssDiff = new CssDiff();
function diffCss(oldStr, newStr, options) {
	return exports.cssDiff.diff(oldStr, newStr, options);
}
