import { BREAK } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import ServersElement from "../../../elements/nces/Servers.mjs";
import { isServerLikeElement } from "../../predicates.mjs";
import FallbackVisitor from "../FallbackVisitor.mjs";
import SpecificationVisitor from "../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ServersVisitor extends Mixin(SpecificationVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ServersElement();
	}
	ArrayElement(arrayElement) {
		arrayElement.forEach((item) => {
			const specPath = isServerLikeElement(item)
				? ["document", "objects", "Server"]
				: ["value"];
			const element = this.toRefractedElement(specPath, item);
			this.element.push(element);
		});
		this.copyMetaAndAttributes(arrayElement, this.element);
		return BREAK;
	}
}
export default ServersVisitor;
