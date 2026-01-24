var regeneratorAsyncGen = require("./regeneratorAsyncGen.js");
function _regeneratorAsync(n, e, r, t, o) {
	var a = regeneratorAsyncGen(n, e, r, t, o);
	return a.next().then((n) => (n.done ? n.value : a.next()));
}
(module.exports = _regeneratorAsync),
	(module.exports.__esModule = true),
	(module.exports["default"] = module.exports);
