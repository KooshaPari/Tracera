import * as util from "../util/index.mjs";

const elesfn = {};

function defineDegreeFunction(callback) {
	return function (includeLoops) {
		if (includeLoops === undefined) {
			includeLoops = true;
		}

		if (this.length === 0) {
			return;
		}

		if (this.isNode() && !this.removed()) {
			let degree = 0;
			const node = this[0];
			const connectedEdges = node._private.edges;

			for (let i = 0; i < connectedEdges.length; i++) {
				const edge = connectedEdges[i];

				if (!includeLoops && edge.isLoop()) {
					continue;
				}

				degree += callback(node, edge);
			}

			return degree;
		} else {
			return;
		}
	};
}

util.extend(elesfn, {
	degree: defineDegreeFunction((node, edge) => {
		if (edge.source().same(edge.target())) {
			return 2;
		} else {
			return 1;
		}
	}),

	indegree: defineDegreeFunction((node, edge) => {
		if (edge.target().same(node)) {
			return 1;
		} else {
			return 0;
		}
	}),

	outdegree: defineDegreeFunction((node, edge) => {
		if (edge.source().same(node)) {
			return 1;
		} else {
			return 0;
		}
	}),
});

function defineDegreeBoundsFunction(degreeFn, callback) {
	return function (includeLoops) {
		let ret;
		const nodes = this.nodes();

		for (let i = 0; i < nodes.length; i++) {
			const ele = nodes[i];
			const degree = ele[degreeFn](includeLoops);
			if (
				degree !== undefined &&
				(ret === undefined || callback(degree, ret))
			) {
				ret = degree;
			}
		}

		return ret;
	};
}

util.extend(elesfn, {
	minDegree: defineDegreeBoundsFunction(
		"degree",
		(degree, min) => degree < min,
	),

	maxDegree: defineDegreeBoundsFunction(
		"degree",
		(degree, max) => degree > max,
	),

	minIndegree: defineDegreeBoundsFunction(
		"indegree",
		(degree, min) => degree < min,
	),

	maxIndegree: defineDegreeBoundsFunction(
		"indegree",
		(degree, max) => degree > max,
	),

	minOutdegree: defineDegreeBoundsFunction(
		"outdegree",
		(degree, min) => degree < min,
	),

	maxOutdegree: defineDegreeBoundsFunction(
		"outdegree",
		(degree, max) => degree > max,
	),
});

util.extend(elesfn, {
	totalDegree: function (includeLoops) {
		let total = 0;
		const nodes = this.nodes();

		for (let i = 0; i < nodes.length; i++) {
			total += nodes[i].degree(includeLoops);
		}

		return total;
	},
});

export default elesfn;
