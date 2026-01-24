import { always } from "ramda";
import { Mixin } from "ts-mixer";
import WebSocketMessageBindingElement from "../../../../../../elements/bindings/ws/WebSocketMessageBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class WebSocketMessageBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new WebSocketMessageBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"ws",
			"MessageBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default WebSocketMessageBindingVisitor;
