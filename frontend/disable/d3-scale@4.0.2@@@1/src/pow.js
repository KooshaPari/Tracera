import { copy, identity, transformer } from "./continuous.js";
import { initRange } from "./init.js";
import { linearish } from "./linear.js";

function transformPow(exponent) {
	return (x) => (x < 0 ? -((-x) ** exponent) : x ** exponent);
}

function transformSqrt(x) {
	return x < 0 ? -Math.sqrt(-x) : Math.sqrt(x);
}

function transformSquare(x) {
	return x < 0 ? -x * x : x * x;
}

export function powish(transform) {
	var scale = transform(identity, identity),
		exponent = 1;

	function rescale() {
		return exponent === 1
			? transform(identity, identity)
			: exponent === 0.5
				? transform(transformSqrt, transformSquare)
				: transform(transformPow(exponent), transformPow(1 / exponent));
	}

	scale.exponent = function (_) {
		return arguments.length ? ((exponent = +_), rescale()) : exponent;
	};

	return linearish(scale);
}

export default function pow() {
	var scale = powish(transformer());

	scale.copy = () => copy(scale, pow()).exponent(scale.exponent());

	initRange.apply(scale, arguments);

	return scale;
}

export function sqrt() {
	return pow.apply(null, arguments).exponent(0.5);
}
