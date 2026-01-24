import { always } from "ramda";
import { Mixin } from "ts-mixer";
import MediaTypeEncodingElement from "../../../../elements/nces/MediaTypeEncoding.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class EncodingVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new MediaTypeEncodingElement();
		this.specPath = always(["document", "objects", "Encoding"]);
	}
}
export default EncodingVisitor;
