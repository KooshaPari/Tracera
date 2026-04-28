// Re-export graph API from endpoints
import { graphApi } from './endpoints';

export { fetchGraph, fetchImpactAnalysis, fetchDependencyAnalysis };

const fetchGraph = graphApi.get;
const fetchImpactAnalysis = graphApi.getImpactAnalysis;
const fetchDependencyAnalysis = graphApi.getDependencyAnalysis;
