import { always } from "ramda";
import { Mixin } from "ts-mixer";
import RedisOperationBindingElement from "../../../../../../elements/bindings/redis/RedisOperationBinding.mjs";
import FallbackVisitor from "../../../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class RedisOperationBindingVisitor extends Mixin(
	FixedFieldsVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new RedisOperationBindingElement();
		this.specPath = always([
			"document",
			"objects",
			"bindings",
			"redis",
			"OperationBinding",
		]);
		this.canSupportSpecificationExtensions = false;
	}
}
export default RedisOperationBindingVisitor;
