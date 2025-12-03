// OpenAPI schema types - will be generated from backend OpenAPI spec
// For now, manually define the schema structure

import type {
  Agent,
  Item,
  ItemStatus,
  Link,
  LinkType,
  Mutation,
  PaginatedResponse,
  Priority,
  Project,
  ViewType,
} from '@tracertm/types'

export interface paths {
  '/api/v1/projects': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': PaginatedResponse<Project>
          }
        }
      }
      parameters: {
        query?: {
          page?: number
          pageSize?: number
          search?: string
        }
      }
    }
    post: {
      requestBody: {
        content: {
          'application/json': {
            name: string
            description?: string
          }
        }
      }
      responses: {
        201: {
          content: {
            'application/json': Project
          }
        }
      }
    }
  }

  '/api/v1/projects/{projectId}': {
    get: {
      parameters: {
        path: {
          projectId: string
        }
      }
      responses: {
        200: {
          content: {
            'application/json': Project
          }
        }
      }
    }
    put: {
      parameters: {
        path: {
          projectId: string
        }
      }
      requestBody: {
        content: {
          'application/json': Partial<Project>
        }
      }
      responses: {
        200: {
          content: {
            'application/json': Project
          }
        }
      }
    }
    delete: {
      parameters: {
        path: {
          projectId: string
        }
      }
      responses: {
        204: {
          content: never
        }
      }
    }
  }

  '/api/v1/projects/{projectId}/items': {
    get: {
      parameters: {
        path: {
          projectId: string
        }
        query?: {
          view?: ViewType
          status?: ItemStatus
          priority?: Priority
          page?: number
          pageSize?: number
        }
      }
      responses: {
        200: {
          content: {
            'application/json': PaginatedResponse<Item>
          }
        }
      }
    }
    post: {
      parameters: {
        path: {
          projectId: string
        }
      }
      requestBody: {
        content: {
          'application/json': {
            view: ViewType
            type: string
            title: string
            description?: string
            status?: ItemStatus
            priority?: Priority
            parentId?: string
            metadata?: Record<string, unknown>
          }
        }
      }
      responses: {
        201: {
          content: {
            'application/json': Item
          }
        }
      }
    }
  }

  '/api/v1/items/{itemId}': {
    get: {
      parameters: {
        path: {
          itemId: string
        }
      }
      responses: {
        200: {
          content: {
            'application/json': Item
          }
        }
      }
    }
    put: {
      parameters: {
        path: {
          itemId: string
        }
      }
      requestBody: {
        content: {
          'application/json': Partial<Item>
        }
      }
      responses: {
        200: {
          content: {
            'application/json': Item
          }
        }
      }
    }
    delete: {
      parameters: {
        path: {
          itemId: string
        }
      }
      responses: {
        204: {
          content: never
        }
      }
    }
  }

  '/api/v1/projects/{projectId}/links': {
    get: {
      parameters: {
        path: {
          projectId: string
        }
        query?: {
          type?: LinkType
          sourceId?: string
          targetId?: string
        }
      }
      responses: {
        200: {
          content: {
            'application/json': Link[]
          }
        }
      }
    }
    post: {
      parameters: {
        path: {
          projectId: string
        }
      }
      requestBody: {
        content: {
          'application/json': {
            sourceId: string
            targetId: string
            type: LinkType
            description?: string
            metadata?: Record<string, unknown>
          }
        }
      }
      responses: {
        201: {
          content: {
            'application/json': Link
          }
        }
      }
    }
  }

  '/api/v1/links/{linkId}': {
    delete: {
      parameters: {
        path: {
          linkId: string
        }
      }
      responses: {
        204: {
          content: never
        }
      }
    }
  }

  '/api/v1/agents': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': Agent[]
          }
        }
      }
    }
  }

  '/api/v1/mutations': {
    get: {
      parameters: {
        query?: {
          agentId?: string
          synced?: boolean
          since?: string
        }
      }
      responses: {
        200: {
          content: {
            'application/json': Mutation[]
          }
        }
      }
    }
    post: {
      requestBody: {
        content: {
          'application/json': {
            agentId: string
            itemId: string
            operation: 'create' | 'update' | 'delete'
            data: Record<string, unknown>
          }
        }
      }
      responses: {
        201: {
          content: {
            'application/json': Mutation
          }
        }
      }
    }
  }
}
