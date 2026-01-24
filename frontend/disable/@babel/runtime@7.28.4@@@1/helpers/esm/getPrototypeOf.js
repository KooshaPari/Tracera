function _getPrototypeOf(t) {
	return (
		(_getPrototypeOf = Object.setPrototypeOf
			? Object.getPrototypeOf.bind()
			: (t) => t.__proto__ || Object.getPrototypeOf(t)),
		_getPrototypeOf(t)
	);
}
export { _getPrototypeOf as default };
