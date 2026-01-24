function _objectWithoutPropertiesLoose(r, e) {
	if (null == r) return {};
	var t = {};
	for (var n in r)
		if (Object.hasOwn(r, n)) {
			if (-1 !== e.indexOf(n)) continue;
			t[n] = r[n];
		}
	return t;
}
export { _objectWithoutPropertiesLoose as default };
