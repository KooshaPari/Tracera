import { always } from "ramda";
import { Mixin } from "ts-mixer";
import GooglepubsubChannelBindingElement from "../../../../../../elements/bindings/googlepubsub/GooglepubsubChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class GooglepubsubChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new GooglepubsubChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"googlepubsub",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default GooglepubsubChannelBindingVisitor;
