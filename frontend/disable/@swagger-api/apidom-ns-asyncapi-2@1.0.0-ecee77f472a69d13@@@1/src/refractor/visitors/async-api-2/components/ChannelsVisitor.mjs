import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ComponentsChannelsElement from "../../../../elements/nces/ComponentsChannels.mjs";
import FallbackVisitor from "../../FallbackVisitor.mjs";
import MapVisitor from "../../generics/MapVisitor.mjs";

/**
 * @public
 */
/**
 * @public
 */
class ChannelsVisitor extends Mixin(MapVisitor, FallbackVisitor) {
	constructor(options) {
		super(options);
		this.element = new ComponentsChannelsElement();
		this.specPath = always(["document", "objects", "ChannelItem"]);
	}
}
export default ChannelsVisitor;
