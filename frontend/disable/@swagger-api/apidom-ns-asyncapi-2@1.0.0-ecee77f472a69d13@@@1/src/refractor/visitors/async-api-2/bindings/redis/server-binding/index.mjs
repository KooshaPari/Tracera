import { always } from "ramda";
import { Mixin } from "ts-mixer";
import RedisServerBindingElement from "../../../../../../elements/bindings/redis/RedisServerBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class RedisServerBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new RedisServerBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"redis",
			"ServerBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default RedisServerBindingVisitor;
