import { copy, transformer } from "./continuous.js";
import { initRange } from "./init.js";
import { linearish } from "./linear.js";

function transformSymlog(c) {
	return (x) => Math.sign(x) * Math.log1p(Math.abs(x / c));
}

function transformSymexp(c) {
	return (x) => Math.sign(x) * Math.expm1(Math.abs(x)) * c;
}

export function symlogish(transform) {
	var c = 1,
		scale = transform(transformSymlog(c), transformSymexp(c));

	scale.constant = function (_) {
		return arguments.length
			? transform(transformSymlog((c = +_)), transformSymexp(c))
			: c;
	};

	return linearish(scale);
}

export default function symlog() {
	var scale = symlogish(transformer());

	scale.copy = () => copy(scale, symlog()).constant(scale.constant());

	return initRange.apply(scale, arguments);
}
