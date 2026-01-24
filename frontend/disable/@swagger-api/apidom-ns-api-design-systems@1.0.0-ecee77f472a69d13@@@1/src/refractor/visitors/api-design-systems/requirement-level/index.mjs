import { BREAK, toValue } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import RequirementLevelElement from "../../../../elements/RequirementLevel.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import SpecificationVisitor from "../../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class RequirementLevelVisitor extends Mixin(
	SpecificationVisitor,
	FallbackVisitor,
) {
	StringElement(stringElement) {
		const requirementLevelElement = new RequirementLevelElement(
			toValue(stringElement),
		);
		this.copyMetaAndAttributes(stringElement, requirementLevelElement);
		this.element = requirementLevelElement;
		return BREAK;
	}
}
export default RequirementLevelVisitor;
