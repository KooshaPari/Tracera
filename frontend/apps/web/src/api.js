const API_BASE_ERROR =
  'VITE_API_BASE must be an http(s) origin or a root-relative path'

const DASHBOARD_ENDPOINTS = [
  { key: 'health', path: '/health', fallback: null },
  { key: 'sprints', path: '/sdlc-pm/sprints', fallback: [] },
  { key: 'teams', path: '/org-intel/teams', fallback: [] },
]

export function normalizeApiBase(value) {
  const configuredBase = value?.trim() || ''
  if (!configuredBase) {
    return ''
  }

  const normalizedBase = configuredBase.replace(/\/+$/, '')
  if (normalizedBase.startsWith('/') && !normalizedBase.startsWith('//')) {
    return normalizedBase
  }

  try {
    const url = new URL(normalizedBase)
    if (
      (url.protocol === 'http:' || url.protocol === 'https:') &&
      url.origin === normalizedBase
    ) {
      return normalizedBase
    }
  } catch {
    // The shared diagnostic below is more useful than the URL parser error.
  }

  throw new Error(API_BASE_ERROR)
}

export function resolveApiConfiguration(value) {
  try {
    return {
      apiBase: normalizeApiBase(value),
      error: null,
    }
  } catch (error) {
    return {
      apiBase: '',
      error: error instanceof Error ? error.message : String(error),
    }
  }
}

export function buildApiUrl(apiBase, endpoint) {
  const normalizedBase = normalizeApiBase(apiBase)
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  return `${normalizedBase}${normalizedEndpoint}`
}

async function loadEndpoint(apiBase, endpoint, fetchImpl) {
  try {
    const response = await fetchImpl(buildApiUrl(apiBase, endpoint.path))
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    return {
      key: endpoint.key,
      value: await response.json(),
      failure: null,
    }
  } catch (error) {
    return {
      key: endpoint.key,
      value: endpoint.fallback,
      failure: {
        endpoint: endpoint.path,
        message: error instanceof Error ? error.message : String(error),
      },
    }
  }
}

export async function loadDashboardData(apiBase, fetchImpl = fetch) {
  const results = await Promise.all(
    DASHBOARD_ENDPOINTS.map((endpoint) => loadEndpoint(apiBase, endpoint, fetchImpl)),
  )

  return results.reduce(
    (dashboard, result) => {
      dashboard[result.key] = result.value
      if (result.failure) {
        dashboard.failures.push(result.failure)
      }
      return dashboard
    },
    { health: null, sprints: [], teams: [], failures: [] },
  )
}
