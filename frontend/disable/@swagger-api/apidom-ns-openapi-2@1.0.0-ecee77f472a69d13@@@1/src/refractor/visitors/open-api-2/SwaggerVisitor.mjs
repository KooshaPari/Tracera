import { BREAK, toValue } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import SwaggerVersionElement from "../../../elements/SwaggerVersion.mjs";
import FallbackVisitor from "../FallbackVisitor.mjs";
import SpecificationVisitor from "../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class SwaggerVisitor extends Mixin(SpecificationVisitor, FallbackVisitor) {
	StringElement(stringElement) {
		const swaggerVersionElement = new SwaggerVersionElement(
			toValue(stringElement),
		);
		this.copyMetaAndAttributes(stringElement, swaggerVersionElement);
		this.element = swaggerVersionElement;
		return BREAK;
	}
}
export default SwaggerVisitor;
