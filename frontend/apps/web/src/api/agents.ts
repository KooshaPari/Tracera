// Re-export agents API from endpoints
import { agentsApi } from './endpoints'

export const fetchAgents = agentsApi.list
export const fetchAgent = agentsApi.get
export const createAgent = agentsApi.create
export const updateAgent = agentsApi.update
export const deleteAgent = agentsApi.delete
export const runAgentTask = agentsApi.runTask
export const getAgentTask = agentsApi.getTask
export const cancelAgentTask = agentsApi.cancelTask
