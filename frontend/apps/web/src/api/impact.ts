/* oxlint-disable oxc/no-async-await */
// Impact analysis API - re-exports from graph
import { graphApi } from "./endpoints";

const fetchImpactAnalysis = graphApi.getImpactAnalysis;
const fetchDependencyAnalysis = graphApi.getDependencyAnalysis;

const impactApi = {
	fetchDependencyAnalysis,
	fetchImpactAnalysis,
};

// eslint-disable-next-line import/no-default-export
export default impactApi;
