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
var DocumentImpl_1 = require("./DocumentImpl");
/**
 * Represents an XML document.
 */
var XMLDocumentImpl = /** @class */ ((_super) => {
	__extends(XMLDocumentImpl, _super);
	/**
	 * Initializes a new instance of `XMLDocument`.
	 */
	function XMLDocumentImpl() {
		return _super.call(this) || this;
	}
	return XMLDocumentImpl;
})(DocumentImpl_1.DocumentImpl);
exports.XMLDocumentImpl = XMLDocumentImpl;
//# sourceMappingURL=XMLDocumentImpl.js.map
