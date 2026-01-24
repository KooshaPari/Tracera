import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ResponsesDefinitionsElement from "../../../../elements/ResponsesDefinitions.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ResponsesDefinitionsVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ResponsesDefinitionsElement();
		this.specPath = always(["document", "objects", "Response"]);
	}
}
export default ResponsesDefinitionsVisitor;
