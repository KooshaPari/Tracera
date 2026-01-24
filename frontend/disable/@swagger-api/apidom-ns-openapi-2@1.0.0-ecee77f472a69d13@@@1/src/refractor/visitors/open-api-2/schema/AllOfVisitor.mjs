import {
	isJSONReferenceElement,
	specificationObj as JSONSchemaDraft4Specification,
} from "@swagger-api/apidom-ns-json-schema-draft-4";
/**
 * @public
 */
export const JSONSchemaAllOfVisitor =
	JSONSchemaDraft4Specification.visitors.document.objects.JSONSchema.fixedFields
		.allOf;

/**
 * @public
 */
class AllOfVisitor extends JSONSchemaAllOfVisitor {
	ArrayElement(arrayElement) {
		const result = JSONSchemaAllOfVisitor.prototype.ArrayElement.call(
			this,
			arrayElement,
		);
		this.element
			.filter(isJSONReferenceElement)
			// @ts-expect-error
			.forEach((referenceElement) => {
				referenceElement.setMetaProperty("referenced-element", "schema");
			});
		return result;
	}
}
export default AllOfVisitor;
