import { ascending, bisect, quantile } from "d3-array";
import { identity } from "./continuous.js";
import { initInterpolator } from "./init.js";

export default function sequentialQuantile() {
	var domain = [],
		interpolator = identity;

	function scale(x) {
		if (x != null && !isNaN((x = +x)))
			return interpolator((bisect(domain, x, 1) - 1) / (domain.length - 1));
	}

	scale.domain = function (_) {
		if (!arguments.length) return domain.slice();
		domain = [];
		for (let d of _) if (d != null && !isNaN((d = +d))) domain.push(d);
		domain.sort(ascending);
		return scale;
	};

	scale.interpolator = function (_) {
		return arguments.length ? ((interpolator = _), scale) : interpolator;
	};

	scale.range = () =>
		domain.map((d, i) => interpolator(i / (domain.length - 1)));

	scale.quantiles = (n) =>
		Array.from({ length: n + 1 }, (_, i) => quantile(domain, i / n));

	scale.copy = () => sequentialQuantile(interpolator).domain(domain);

	return initInterpolator.apply(scale, arguments);
}
