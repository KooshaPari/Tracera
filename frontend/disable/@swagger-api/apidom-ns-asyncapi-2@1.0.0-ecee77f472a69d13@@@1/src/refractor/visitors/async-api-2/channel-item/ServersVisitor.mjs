import { BREAK, cloneDeep, isStringElement } from "@swagger-api/apidom-core";
import { Mixin } from "ts-mixer";
import ChannelItemServersElement from "../../../../elements/nces/ChannelItemsServers.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import SpecificationVisitor from "../../SpecificationVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ServersVisitor extends Mixin(SpecificationVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ChannelItemServersElement();
	}
	ArrayElement(arrayElement) {
		arrayElement.forEach((item) => {
			const element = cloneDeep(item);
			if (isStringElement(element)) {
				element.classes.push("server-name");
			}
			this.element.push(element);
		});
		this.copyMetaAndAttributes(arrayElement, this.element);
		return BREAK;
	}
}
export default ServersVisitor;
