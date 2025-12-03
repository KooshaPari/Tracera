import { createTRPCReact } from '@trpc/react-query'
import type { AppRouter } from '@/server/trpc'
import { apiClient } from '@/api/client'

/**
 * TRPC Integration for TraceRTM
 * 
 * Replaces custom OpenAPI client with type-safe, end-to-end typed API
 * Benefits:
 * - Auto-complete for API methods
 * - Type-safe request/response
 * - Built-in error handling
 * - Optimistic updates support
 * - Real-time subscriptions
 */

export const trpc = createTRPCReact<AppRouter>()

/**
 * Enhanced API client with TRPC patterns
 * Migrates from REST/OpenAPI to type-safe procedures
 */
export const createTRPCClient = () => {
  return trpc.createClient({
    links: [
      /**
       * HTTP link for standard queries/mutations
       * Replaces openapi-fetch with type-safe procedures
       */
      {
        request: ({ op, path }) => {
          // Map TRPC procedures to existing REST endpoints
          const procedurePath = path.split('.')
          const [resource, action] = procedurePath
          
          let url, method = 'GET'
          const headers = new Headers()
          headers.set('Content-Type', 'application/json')
          
          // Add auth token
          const token = localStorage.getItem('auth_token')
          if (token) {
            headers.set('Authorization', `Bearer ${token}`)
          }

          // Map TRPC calls to REST endpoints
          switch (resource) {
            case 'projects':
              if (action === 'list') {
                url = '/api/v1/projects'
              } else if (action === 'get') {
                url = `/api/v1/projects/${op.pathVariables?.id}`
              } else if (action === 'create') {
                url = '/api/v1/projects'
                method = 'POST'
              } else if (action === 'update') {
                url = `/api/v1/projects/${op.pathVariables?.id}`
                method = 'PUT'
              } else if (action === 'delete') {
                url = `/api/v1/projects/${op.pathVariables?.id}`
                method = 'DELETE'
              }
              break
              
            case 'items':
              if (action === 'list') {
                url = `/api/v1/projects/${op.pathVariables?.projectId}/items`
              } else if (action === 'get') {
                url = `/api/v1/items/${op.pathVariables?.id}`
              } else if (action === 'create') {
                url = `/api/v1/projects/${op.pathVariables?.projectId}/items`
                method = 'POST'
              } else if (action === 'update') {
                url = `/api/v1/items/${op.pathVariables?.id}`
                method = 'PUT'
              } else if (action === 'delete') {
                url = `/api/v1/items/${op.pathVariables?.id}`
                method = 'DELETE'
              }
              break
              
            case 'links':
              if (action === 'list') {
                url = `/api/v1/projects/${op.pathVariables?.projectId}/links`
              } else if (action === 'create') {
                url = `/api/v1/projects/${op.pathVariables?.projectId}/links`
                method = 'POST'
              } else if (action === 'delete') {
                url = `/api/v1/links/${op.pathVariables?.id}`
                method = 'DELETE'
              }
              break
              
            case 'agents':
              if (action === 'list') {
                url = '/api/v1/agents'
              }
              break
          }

          return fetch(`${import.meta.env.VITE_API_URL}${url}`, {
            method,
            headers,
            body: op.type === 'mutation' ? JSON.stringify(op.input) : undefined,
          }).then(res => {
            if (!res.ok) {
              throw new Error(`HTTP ${res.status}: ${res.statusText}`)
            }
            return res.json()
          }).then(data => {
            return {
              result: {
                data,
                type: 'data' as const,
              },
            }
          })
        },
      },
      
      /**
       * WebSocket link for real-time subscriptions
       * Replaces custom WebSocket manager with TRPC subscriptions
       */
      {
        request: ({ op, path }) => {
          if (op.type !== 'subscription') return null
          
          return {
            result: {
              type: 'data' as const,
              data: new ReadableStream({
                start(controller) {
                  const wsManager = getWebSocketManager()
                  const channel = path.replace(/\./g, ':')
                  
                  const unsubscribe = wsManager.subscribe(channel, (event) => {
                    controller.enqueue(event)
                  })
                  
                  // Cleanup on stream close
                  return () => unsubscribe()
                },
              }),
            },
          }
        },
      },
    ],
  })
}

/**
 * Type-safe API Procedures
 * Replaces manual REST endpoints with typed procedures
 */
export const apiProcedures = {
  // Projects
  projects: {
    list: trpc.projects.list,
    get: trpc.projects.get,
    create: trpc.projects.create,
    update: trpc.projects.update,
    delete: trpc.projects.delete,
    
    // Enterprise features
    getMetrics: trpc.projects.getMetrics,
    exportData: trpc.projects.exportData,
    getAuditHistory: trpc.projects.getAuditHistory,
  },
  
  // Items (16 Professional Views)
  items: {
    list: trpc.items.list,
    get: trpc.items.get,
    create: trpc.items.create,
    update: trpc.items.update,
    delete: trpc.items.delete,
    search: trpc.items.search,
    
    // View-specific procedures
    getFeatures: trpc.items.getFeatures,
    getCode: trpc.items.getCode,
    getTests: trpc.items.getTests,
    getApis: trpc.items.getApis,
    getDatabases: trpc.items.getDatabases,
    getWireframes: trpc.items.getWireframes,
    
    // Advanced operations
    bulkCreate: trpc.items.bulkCreate,
    bulkUpdate: trpc.items.bulkUpdate,
    bulkDelete: trpc.items.bulkDelete,
    clone: trpc.items.clone,
    
    // Enterprise features
    getImpact: trpc.items.getImpact,
    getTraceability: trpc.items.getTraceability,
    getDependencies: trpc.items.getDependencies,
  },
  
  // Links (60+ Relationship Types)
  links: {
    list: trpc.links.list,
    create: trpc.links.create,
    delete: trpc.links.delete,
    
    // Advanced relationship operations
    getTransitive: trpc.links.getTransitive,
    getCycles: trpc.links.getCycles,
    getPaths: trpc.links.getPaths,
    
    // Enterprise features
    validateRelationships: trpc.links.validateRelationships,
    mergeDuplicateLinks: trpc.links.mergeDuplicateLinks,
  },
  
  // Agents (1-1000 Concurrent Agents)
  agents: {
    list: trpc.agents.list,
    get: trpc.agents.get,
    create: trpc.agents.create,
    update: trpc.agents.update,
    delete: trpc.agents.delete,
    
    // Agent coordination
    coordinate: trpc.agents.coordinate,
    broadcast: trpc.agents.broadcast,
    negotiate: trpc.agents.negotiate,
    
    // Monitoring
    getMetrics: trpc.agents.getMetrics,
    getWorkload: trpc.agents.getWorkload,
    getConflicts: trpc.agents.getConflicts,
  },
  
  // Search & Analytics
  search: {
    semantic: trpc.search.semantic,
    hybrid: trpc.search.hybrid,
    suggestions: trpc.search.suggestions,
    
    // Advanced search
    withContext: trpc.search.withContext,
    fuzzy: trpc.search.fuzzy,
    phonetic: trpc.search.phonetic,
  },
  
  // Graph Operations
  graph: {
    getData: trpc.graph.getData,
    getSubgraph: trpc.graph.getSubgraph,
    getNeighbors: trpc.graph.getNeighbors,
    
    // Algorithmic operations
    shortestPath: trpc.graph.shortestPath,
    centrality: trpc.graph.centrality,
    clustering: trpc.graph.clustering,
  },
  
  // Real-time Subscriptions
  subscriptions: {
    onProjectChange: trpc.subscriptions.onProjectChange,
    onItemUpdate: trpc.subscriptions.onItemUpdate,
    onLinkChange: trpc.subscriptions.onLinkChange,
    onAgentActivity: trpc.subscriptions.onAgentActivity,
  },
}

/**
 * Migration utilities
 * Gradually replace OpenAPI calls with TRPC procedures
 */
export const migrateToTRPC = {
  // Replace useProjects with type-safe equivalent
  projects: () => apiProcedures.projects.list.useQuery(),
  
  // Replace useProjectsQuery with enhanced version
  projectItems: (projectId: string, filters?: any) => 
    apiProcedures.items.list.useQuery({ ...filters, projectId }),
    
  // Replace custom WebSocket with TRPC subscriptions
  realtime: {
    subscribe: (channel: string, callback: (event: any) => void) =>
      apiProcedures.subscriptions.onItemUpdate.useSubscription(
        { channel },
        { onData: callback }
      ),
  },
}
