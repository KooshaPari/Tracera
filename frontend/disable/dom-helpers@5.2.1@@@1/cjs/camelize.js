exports.__esModule = true;
exports.default = camelize;
var rHyphen = /-(.)/g;

function camelize(string) {
	return string.replace(rHyphen, (_, chr) => chr.toUpperCase());
}

module.exports = exports["default"];
