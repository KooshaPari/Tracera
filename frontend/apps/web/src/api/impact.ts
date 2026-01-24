// Impact analysis API - re-exports from graph
import { graphApi } from "./endpoints";

export const fetchImpactAnalysis = graphApi.getImpactAnalysis;
export const fetchDependencyAnalysis = graphApi.getDependencyAnalysis;
