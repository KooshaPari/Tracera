import { always } from "ramda";
import { Mixin } from "ts-mixer";
import SwaggerElement from "../../../elements/Swagger.mjs";
import FallbackVisitor from "../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SwaggerVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new SwaggerElement();
		this.specPath = always(["document", "objects", "Swagger"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default SwaggerVisitor;
