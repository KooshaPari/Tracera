import { always } from "ramda";
import { Mixin } from "ts-mixer";
import HttpChannelBindingElement from "../../../../../../elements/bindings/http/HttpChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class HttpChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new HttpChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"http",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default HttpChannelBindingVisitor;
