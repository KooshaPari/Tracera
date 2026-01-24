const Declaration = require("../declaration");
const utils = require("../utils");

class Appearance extends Declaration {
	constructor(name, prefixes, all) {
		super(name, prefixes, all);

		if (this.prefixes) {
			this.prefixes = utils.uniq(
				this.prefixes.map((i) => {
					if (i === "-ms-") {
						return "-webkit-";
					}
					return i;
				}),
			);
		}
	}
}

Appearance.names = ["appearance"];

module.exports = Appearance;
