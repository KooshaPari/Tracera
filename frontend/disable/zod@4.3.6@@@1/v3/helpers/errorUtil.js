export var errorUtil;
((errorUtil) => {
	errorUtil.errToObj = (message) =>
		typeof message === "string" ? { message } : message || {};
	// biome-ignore lint:
	errorUtil.toString = (message) =>
		typeof message === "string" ? message : message?.message;
})(errorUtil || (errorUtil = {}));
