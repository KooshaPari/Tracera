import { cloneDeep, toValue } from "@swagger-api/apidom-core";
import { always, range, test } from "ramda";
import { Mixin } from "ts-mixer";
import ResponsesElement from "../../../../elements/Responses.mjs";
import {
	isReferenceElement,
	isResponseElement,
} from "../../../../predicates.mjs";
import { isReferenceLikeElement } from "../../../predicates.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MixedFieldsVisitor from "../../generics/MixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ResponsesVisitor extends Mixin(MixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ResponsesElement();
		this.specPathFixedFields = always(["document", "objects", "Responses"]);
		this.canSupportSpecificationExtensions = true;
		this.specPathPatternedFields = (element) => {
			return isReferenceLikeElement(element)
				? ["document", "objects", "Reference"]
				: ["document", "objects", "Response"];
		};
		// @ts-expect-error
		this.fieldPatternPredicate = test(
			new RegExp(`^(1XX|2XX|3XX|4XX|5XX|${range(100, 600).join("|")})$`),
		);
	}
	ObjectElement(objectElement) {
		const result = MixedFieldsVisitor.prototype.ObjectElement.call(
			this,
			objectElement,
		);

		// decorate every ReferenceElement with metadata about their referencing type
		// @ts-expect-error
		this.element.filter(isReferenceElement).forEach((referenceElement) => {
			referenceElement.setMetaProperty("referenced-element", "response");
		});

		// decorate every ResponseElement with metadata about their status code
		// @ts-expect-error
		this.element.filter(isResponseElement).forEach((value, key) => {
			const httpStatusCode = cloneDeep(key);
			if (!this.fieldPatternPredicate(toValue(httpStatusCode))) return;
			value.setMetaProperty("http-status-code", httpStatusCode);
		});
		return result;
	}
}
export default ResponsesVisitor;
