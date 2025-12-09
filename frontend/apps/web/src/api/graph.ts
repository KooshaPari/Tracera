// Re-export graph API from endpoints
import { graphApi } from './endpoints'

export const fetchGraph = graphApi.get
export const fetchImpactAnalysis = graphApi.analyzeImpact
export const fetchDependencyAnalysis = graphApi.analyzeDependencies
