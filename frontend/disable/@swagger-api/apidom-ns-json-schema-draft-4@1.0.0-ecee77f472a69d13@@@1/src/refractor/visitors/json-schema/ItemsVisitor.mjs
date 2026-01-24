import { ArrayElement, BREAK } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import { isJSONReferenceLikeElement } from "../../predicates.mjs";
import FallbackVisitor from "../FallbackVisitor.mjs";
import SpecificationVisitor from "../SpecificationVisitor.mjs";
import ParentSchemaAwareVisitor from "./ParentSchemaAwareVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ItemsVisitor extends Mixin(
	SpecificationVisitor,
	ParentSchemaAwareVisitor,
	FallbackVisitor,
) {
	ObjectElement(objectElement) {
		const specPath = isJSONReferenceLikeElement(objectElement)
			? ["document", "objects", "JSONReference"]
			: ["document", "objects", "JSONSchema"];
		this.element = this.toRefractedElement(specPath, objectElement);
		return BREAK;
	}
	ArrayElement(arrayElement) {
		this.element = new ArrayElement();
		this.element.classes.push("json-schema-items");
		arrayElement.forEach((item) => {
			const specPath = isJSONReferenceLikeElement(item)
				? ["document", "objects", "JSONReference"]
				: ["document", "objects", "JSONSchema"];
			const element = this.toRefractedElement(specPath, item);
			this.element.push(element);
		});
		this.copyMetaAndAttributes(arrayElement, this.element);
		return BREAK;
	}
}
export default ItemsVisitor;
