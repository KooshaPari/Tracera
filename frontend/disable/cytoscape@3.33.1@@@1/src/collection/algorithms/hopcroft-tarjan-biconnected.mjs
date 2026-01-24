const hopcroftTarjanBiconnected = function () {
	const nodes = {};
	let id = 0;
	let edgeCount = 0;
	const components = [];
	const stack = [];
	const visitedEdges = {};

	const buildComponent = (x, y) => {
		let i = stack.length - 1;
		const cutset = [];
		const component = this.spawn();

		while (stack[i].x != x || stack[i].y != y) {
			cutset.push(stack.pop().edge);
			i--;
		}
		cutset.push(stack.pop().edge);

		cutset.forEach((edge) => {
			const connectedNodes = edge.connectedNodes().intersection(this);
			component.merge(edge);
			connectedNodes.forEach((node) => {
				const nodeId = node.id();
				const connectedEdges = node.connectedEdges().intersection(this);
				component.merge(node);
				if (!nodes[nodeId].cutVertex) {
					component.merge(connectedEdges);
				} else {
					component.merge(connectedEdges.filter((edge) => edge.isLoop()));
				}
			});
		});
		components.push(component);
	};

	const biconnectedSearch = (root, currentNode, parent) => {
		if (root === parent) edgeCount += 1;
		nodes[currentNode] = {
			id: id,
			low: id++,
			cutVertex: false,
		};
		const edges = this.getElementById(currentNode)
			.connectedEdges()
			.intersection(this);

		if (edges.size() === 0) {
			components.push(this.spawn(this.getElementById(currentNode)));
		} else {
			let sourceId, targetId, otherNodeId, edgeId;

			edges.forEach((edge) => {
				sourceId = edge.source().id();
				targetId = edge.target().id();
				otherNodeId = sourceId === currentNode ? targetId : sourceId;

				if (otherNodeId !== parent) {
					edgeId = edge.id();

					if (!visitedEdges[edgeId]) {
						visitedEdges[edgeId] = true;
						stack.push({
							x: currentNode,
							y: otherNodeId,
							edge,
						});
					}

					if (!(otherNodeId in nodes)) {
						biconnectedSearch(root, otherNodeId, currentNode);
						nodes[currentNode].low = Math.min(
							nodes[currentNode].low,
							nodes[otherNodeId].low,
						);

						if (nodes[currentNode].id <= nodes[otherNodeId].low) {
							nodes[currentNode].cutVertex = true;
							buildComponent(currentNode, otherNodeId);
						}
					} else {
						nodes[currentNode].low = Math.min(
							nodes[currentNode].low,
							nodes[otherNodeId].id,
						);
					}
				}
			});
		}
	};

	this.forEach((ele) => {
		if (ele.isNode()) {
			const nodeId = ele.id();

			if (!(nodeId in nodes)) {
				edgeCount = 0;
				biconnectedSearch(nodeId, nodeId);
				nodes[nodeId].cutVertex = edgeCount > 1;
			}
		}
	});

	const cutVertices = Object.keys(nodes)
		.filter((id) => nodes[id].cutVertex)
		.map((id) => this.getElementById(id));

	return {
		cut: this.spawn(cutVertices),
		components,
	};
};

export default {
	hopcroftTarjanBiconnected,
	htbc: hopcroftTarjanBiconnected,
	htb: hopcroftTarjanBiconnected,
	hopcroftTarjanBiconnectedComponents: hopcroftTarjanBiconnected,
};
