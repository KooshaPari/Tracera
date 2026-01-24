// Re-export graph API from endpoints
import { graphApi } from "./endpoints";

export const fetchGraph = graphApi.get;
export const fetchImpactAnalysis = graphApi.getImpactAnalysis;
export const fetchDependencyAnalysis = graphApi.getDependencyAnalysis;
