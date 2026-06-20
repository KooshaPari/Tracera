// Impact analysis API - re-exports from graph
import { graphApi } from './endpoints';

const fetchImpactAnalysis = graphApi.getImpactAnalysis;
const fetchDependencyAnalysis = graphApi.getDependencyAnalysis;

export { fetchDependencyAnalysis, fetchImpactAnalysis };

const impactApi = {
  fetchDependencyAnalysis,
  fetchImpactAnalysis,
};

export default impactApi;
