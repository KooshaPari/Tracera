import {
	isJSONReferenceElement,
	specificationObj as JSONSchemaDraft4Specification,
} from "@swagger-api/apidom-ns-json-schema-draft-4";
/**
 * @public
 */
export const JSONSchemaPropertiesVisitor =
	JSONSchemaDraft4Specification.visitors.document.objects.JSONSchema.fixedFields
		.properties;

/**
 * @public
 */
class PropertiesVisitor extends JSONSchemaPropertiesVisitor {
	ObjectElement(objectElement) {
		const result = JSONSchemaPropertiesVisitor.prototype.ObjectElement.call(
			this,
			objectElement,
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
export default PropertiesVisitor;
