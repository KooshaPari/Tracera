// Impact analysis API - re-exports from graph
import { graphApi } from './endpoints'

export const fetchImpactAnalysis = graphApi.analyzeImpact
export const fetchDependencyAnalysis = graphApi.analyzeDependencies
