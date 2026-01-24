export default function (selector) {
	return function () {
		return this.matches(selector);
	};
}

export function childMatcher(selector) {
	return (node) => node.matches(selector);
}
