import { always } from "ramda";
import { Mixin } from "ts-mixer";
import WebSocketOperationBindingElement from "../../../../../../elements/bindings/ws/WebSocketOperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class WebSocketOperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new WebSocketOperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"ws",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default WebSocketOperationBindingVisitor;
