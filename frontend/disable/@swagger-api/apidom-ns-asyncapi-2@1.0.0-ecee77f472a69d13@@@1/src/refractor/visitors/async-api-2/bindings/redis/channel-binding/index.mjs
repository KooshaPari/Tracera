import { always } from "ramda";
import { Mixin } from "ts-mixer";
import RedisChannelBindingElement from "../../../../../../elements/bindings/redis/RedisChannelBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class RedisChannelBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new RedisChannelBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"redis",
			"ChannelBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default RedisChannelBindingVisitor;
