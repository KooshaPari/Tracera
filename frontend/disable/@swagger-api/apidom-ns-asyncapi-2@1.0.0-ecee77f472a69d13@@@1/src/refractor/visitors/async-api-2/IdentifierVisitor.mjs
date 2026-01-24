import { BREAK, toValue } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import IdentifierElement from "../../../elements/Identifier.mjs";
import FallbackVisitor from "../FallbackVisitor.mjs";
import SpecificationVisitor from "../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class IdentifierVisitor extends Mixin(SpecificationVisitor, FallbackVisitor) {
	StringElement(stringElement) {
		const identifierElement = new IdentifierElement(toValue(stringElement));
		this.copyMetaAndAttributes(stringElement, identifierElement);
		this.element = identifierElement;
		return BREAK;
	}
}
export default IdentifierVisitor;
