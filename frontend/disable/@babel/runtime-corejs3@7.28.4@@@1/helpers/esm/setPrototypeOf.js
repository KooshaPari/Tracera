import _bindInstanceProperty from "core-js-pure/features/instance/bind.js";
import _Object$setPrototypeOf from "core-js-pure/features/object/set-prototype-of.js";

function _setPrototypeOf(t, e) {
	var _context;
	return (
		(_setPrototypeOf = _Object$setPrototypeOf
			? _bindInstanceProperty((_context = _Object$setPrototypeOf)).call(
					_context,
				)
			: (t, e) => ((t.__proto__ = e), t)),
		_setPrototypeOf(t, e)
	);
}
export { _setPrototypeOf as default };
