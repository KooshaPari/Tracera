Object.defineProperty(exports, "__esModule", { value: true });
exports.verifyPseudoArgs = exports.pseudos = void 0;
// While filters are precompiled, pseudos get called when they are needed
exports.pseudos = {
	empty: (elem, _a) => {
		var adapter = _a.adapter;
		return !adapter.getChildren(elem).some((elem) => {
			// FIXME: `getText` call is potentially expensive.
			return adapter.isTag(elem) || adapter.getText(elem) !== "";
		});
	},
	"first-child": (elem, _a) => {
		var adapter = _a.adapter,
			equals = _a.equals;
		if (adapter.prevElementSibling) {
			return adapter.prevElementSibling(elem) == null;
		}
		var firstChild = adapter
			.getSiblings(elem)
			.find((elem) => adapter.isTag(elem));
		return firstChild != null && equals(elem, firstChild);
	},
	"last-child": (elem, _a) => {
		var adapter = _a.adapter,
			equals = _a.equals;
		var siblings = adapter.getSiblings(elem);
		for (var i = siblings.length - 1; i >= 0; i--) {
			if (equals(elem, siblings[i])) return true;
			if (adapter.isTag(siblings[i])) break;
		}
		return false;
	},
	"first-of-type": (elem, _a) => {
		var adapter = _a.adapter,
			equals = _a.equals;
		var siblings = adapter.getSiblings(elem);
		var elemName = adapter.getName(elem);
		for (var i = 0; i < siblings.length; i++) {
			var currentSibling = siblings[i];
			if (equals(elem, currentSibling)) return true;
			if (
				adapter.isTag(currentSibling) &&
				adapter.getName(currentSibling) === elemName
			) {
				break;
			}
		}
		return false;
	},
	"last-of-type": (elem, _a) => {
		var adapter = _a.adapter,
			equals = _a.equals;
		var siblings = adapter.getSiblings(elem);
		var elemName = adapter.getName(elem);
		for (var i = siblings.length - 1; i >= 0; i--) {
			var currentSibling = siblings[i];
			if (equals(elem, currentSibling)) return true;
			if (
				adapter.isTag(currentSibling) &&
				adapter.getName(currentSibling) === elemName
			) {
				break;
			}
		}
		return false;
	},
	"only-of-type": (elem, _a) => {
		var adapter = _a.adapter,
			equals = _a.equals;
		var elemName = adapter.getName(elem);
		return adapter
			.getSiblings(elem)
			.every(
				(sibling) =>
					equals(elem, sibling) ||
					!adapter.isTag(sibling) ||
					adapter.getName(sibling) !== elemName,
			);
	},
	"only-child": (elem, _a) => {
		var adapter = _a.adapter,
			equals = _a.equals;
		return adapter
			.getSiblings(elem)
			.every((sibling) => equals(elem, sibling) || !adapter.isTag(sibling));
	},
};
function verifyPseudoArgs(func, name, subselect, argIndex) {
	if (subselect === null) {
		if (func.length > argIndex) {
			throw new Error("Pseudo-class :".concat(name, " requires an argument"));
		}
	} else if (func.length === argIndex) {
		throw new Error(
			"Pseudo-class :".concat(name, " doesn't have any arguments"),
		);
	}
}
exports.verifyPseudoArgs = verifyPseudoArgs;
//# sourceMappingURL=pseudos.js.map
