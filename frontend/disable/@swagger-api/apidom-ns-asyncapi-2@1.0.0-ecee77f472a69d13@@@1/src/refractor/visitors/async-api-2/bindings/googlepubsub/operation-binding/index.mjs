import { always } from "ramda";
import { Mixin } from "ts-mixer";
import GooglepubsubOperationBindingElement from "../../../../../../elements/bindings/googlepubsub/GooglepubsubOperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class GooglepubsubOperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new GooglepubsubOperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"googlepubsub",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default GooglepubsubOperationBindingVisitor;
