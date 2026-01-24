import { always } from "ramda";
import { Mixin } from "ts-mixer";
import XmlElement from "../../../../elements/Xml.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import FixedFieldsVisitor from "../../generics/FixedFieldsVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class XmlVisitor extends Mixin(FixedFieldsVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new XmlElement();
		this.specPath = always(["document", "objects", "XML"]);
		this.canSupportSpecificationExtensions = true;
	}
}
export default XmlVisitor;
