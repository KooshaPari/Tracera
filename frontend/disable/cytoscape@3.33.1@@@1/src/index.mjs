import Core from "./core/index.mjs";
import extension from "./extension.mjs";
import * as is from "./is.mjs";
import Stylesheet from "./stylesheet.mjs";
import { warnings } from "./util/index.mjs";
import version from "./version.mjs";

const cytoscape = function (options) {
	// if no options specified, use default
	if (options === undefined) {
		options = {};
	}

	// create instance
	if (is.plainObject(options)) {
		return new Core(options);
	}

	// allow for registration of extensions
	else if (is.string(options)) {
		return extension.apply(extension, arguments);
	}
};

// e.g. cytoscape.use( require('cytoscape-foo'), bar )
cytoscape.use = function (ext) {
	const args = Array.prototype.slice.call(arguments, 1); // args to pass to ext

	args.unshift(cytoscape); // cytoscape is first arg to ext

	ext.apply(null, args);

	return this;
};

cytoscape.warnings = (bool) => warnings(bool);

// replaced by build system
cytoscape.version = version;

// expose public apis (mostly for extensions)
cytoscape.stylesheet = cytoscape.Stylesheet = Stylesheet;

export default cytoscape;
