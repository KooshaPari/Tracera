import { always } from "ramda";
import { Mixin } from "ts-mixer";
import HttpMessageBindingElement from "../../../../../../elements/bindings/http/HttpMessageBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class HttpMessageBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new HttpMessageBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"http",
			"MessageBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default HttpMessageBindingVisitor;
