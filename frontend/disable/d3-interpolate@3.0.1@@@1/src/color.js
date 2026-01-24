import constant from "./constant.js";

function linear(a, d) {
	return (t) => a + t * d;
}

function exponential(a, b, y) {
	return (a = a ** y), (b = b ** y - a), (y = 1 / y), (t) => (a + t * b) ** y;
}

export function hue(a, b) {
	var d = b - a;
	return d
		? linear(a, d > 180 || d < -180 ? d - 360 * Math.round(d / 360) : d)
		: constant(isNaN(a) ? b : a);
}

export function gamma(y) {
	return (y = +y) === 1
		? nogamma
		: (a, b) => (b - a ? exponential(a, b, y) : constant(isNaN(a) ? b : a));
}

export default function nogamma(a, b) {
	var d = b - a;
	return d ? linear(a, d) : constant(isNaN(a) ? b : a);
}
