import { ObjectElement } from "@swagger-api/apidom-core";
import { always } from "ramda";
import { Mixin } from "ts-mixer";
import FallbackVisitor from "../FallbackVisitor.mjs";
import MapVisitor from "../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ContentVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ObjectElement();
		this.element.classes.push("content");
		this.specPath = always(["document", "objects", "MediaType"]);
	}
}
export default ContentVisitor;
