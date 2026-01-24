import { always } from "ramda";
import { Mixin } from "ts-mixer";
import IbmmqChannelBindingElement from "../../../../../../elements/bindings/ibmmq/IbmmqChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class IbmmqChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new IbmmqChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"ibmmq",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default IbmmqChannelBindingVisitor;
