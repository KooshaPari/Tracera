import { always } from "ramda";
import { Mixin } from "ts-mixer";
import WebSocketServerBindingElement from "../../../../../../elements/bindings/ws/WebSocketServerBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class WebSocketServerBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new WebSocketServerBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"ws",
			"ServerBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default WebSocketServerBindingVisitor;
