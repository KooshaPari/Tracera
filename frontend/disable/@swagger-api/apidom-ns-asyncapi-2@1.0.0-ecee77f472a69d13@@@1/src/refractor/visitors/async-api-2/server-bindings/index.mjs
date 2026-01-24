import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ServerBindingsElement from "../../../../elements/ServerBindings.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ServerBindingsVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ServerBindingsElement();
		this.specPath = always(["document", "objects", "ServerBindings"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default ServerBindingsVisitor;
