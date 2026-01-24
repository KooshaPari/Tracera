import * as is from "../is.mjs";
import * as util from "../util/index.mjs";

const corefn = {
	layout: function (options) {
		if (options == null) {
			util.error("Layout options must be specified to make a layout");
			return;
		}

		if (options.name == null) {
			util.error("A `name` must be specified to make a layout");
			return;
		}

		const name = options.name;
		const Layout = this.extension("layout", name);

		if (Layout == null) {
			util.error(
				"No such layout `" +
					name +
					"` found.  Did you forget to import it and `cytoscape.use()` it?",
			);
			return;
		}

		let eles;
		if (is.string(options.eles)) {
			eles = this.$(options.eles);
		} else {
			eles = options.eles != null ? options.eles : this.$();
		}

		const layout = new Layout(
			util.extend({}, options, {
				cy: this,
				eles: eles,
			}),
		);

		return layout;
	},
};

corefn.createLayout = corefn.makeLayout = corefn.layout;

export default corefn;
