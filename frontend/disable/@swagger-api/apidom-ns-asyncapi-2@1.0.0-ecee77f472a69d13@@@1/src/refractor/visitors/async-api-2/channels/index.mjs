import { always } from "ramda";
import { Mixin } from "ts-mixer";
import ChannelsElement from "../../../../elements/Channels.mjs";
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
		this.element = new ChannelsElement();
		this.specPath = always(["document", "objects", "ChannelItem"]);
	}
}
export default ChannelsVisitor;
