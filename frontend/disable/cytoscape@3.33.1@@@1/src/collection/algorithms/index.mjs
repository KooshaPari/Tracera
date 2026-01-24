import * as util from "../../util/index.mjs";
import aStar from "./a-star.mjs";
import affinityPropagation from "./affinity-propagation.mjs";
import bellmanFord from "./bellman-ford.mjs";
import betweennessCentrality from "./betweenness-centrality.mjs";
import bfsDfs from "./bfs-dfs.mjs";
import closenessCentrality from "./closeness-centrality.mjs";
import degreeCentrality from "./degree-centrality.mjs";
import dijkstra from "./dijkstra.mjs";
import floydWarshall from "./floyd-warshall.mjs";
import hierarchicalClustering from "./hierarchical-clustering.mjs";
import hierholzer from "./hierholzer.mjs";
import hopcroftTarjanBiconnected from "./hopcroft-tarjan-biconnected.mjs";
import kClustering from "./k-clustering.mjs";
import kargerStein from "./karger-stein.mjs";
import kruskal from "./kruskal.mjs";
import markovClustering from "./markov-clustering.mjs";
import pageRank from "./page-rank.mjs";
import tarjanStronglyConnected from "./tarjan-strongly-connected.mjs";

var elesfn = {};

[
	bfsDfs,
	dijkstra,
	kruskal,
	aStar,
	floydWarshall,
	bellmanFord,
	kargerStein,
	pageRank,
	degreeCentrality,
	closenessCentrality,
	betweennessCentrality,
	markovClustering,
	kClustering,
	hierarchicalClustering,
	affinityPropagation,
	hierholzer,
	hopcroftTarjanBiconnected,
	tarjanStronglyConnected,
].forEach((props) => {
	util.extend(elesfn, props);
});

export default elesfn;
