import { always } from "ramda";
import { Mixin } from "ts-mixer";
import MediaElement from "../../../../elements/Media.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class MediaVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new MediaElement();
		this.specPath = always(["document", "objects", "Media"]);
	}
}
export default MediaVisitor;
