const util = require("util");

const logger = new (function () {
	const _output = (type, out) => {
		const quiet =
			typeof jake != "undefined" &&
			jake.program &&
			jake.program.opts &&
			jake.program.opts.quiet;
		let msg;
		if (!quiet) {
			msg = typeof out == "string" ? out : util.inspect(out);
			console[type](msg);
		}
	};

	this.log = (out) => {
		_output("log", out);
	};

	this.error = (out) => {
		_output("error", out);
	};
})();

module.exports = logger;
