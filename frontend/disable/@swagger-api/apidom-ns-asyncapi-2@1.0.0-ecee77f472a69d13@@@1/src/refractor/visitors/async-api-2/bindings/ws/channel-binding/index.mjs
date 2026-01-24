import { always } from "ramda";
import { Mixin } from "ts-mixer";
import WebSocketChannelBindingElement from "../../../../../../elements/bindings/ws/WebSocketChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class WebSocketChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new WebSocketChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"ws",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default WebSocketChannelBindingVisitor;
