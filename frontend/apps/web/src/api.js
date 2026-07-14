const API_BASE_ERROR =
  'VITE_API_BASE must use HTTPS, localhost HTTP, or a root-relative path'

const DASHBOARD_ENDPOINTS = [
  { key: 'health', path: '/health', fallback: null, protected: false },
  { key: 'sprints', path: '/sdlc-pm/sprints', fallback: [], protected: true },
  { key: 'teams', path: '/org-intel/teams', fallback: [], protected: true },
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
    const isLocalDevelopmentHttp =
      url.protocol === 'http:' &&
      (url.hostname === 'localhost' || url.hostname === '127.0.0.1')
    if (
      (url.protocol === 'https:' || isLocalDevelopmentHttp) &&
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

async function loadEndpoint(apiBase, endpoint, accessToken, fetchImpl, signal) {
  try {
    const options = { signal }
    if (endpoint.protected) {
      options.headers = { Authorization: `Bearer ${accessToken}` }
    }
    const response = await fetchImpl(buildApiUrl(apiBase, endpoint.path), options)
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

export async function loadDashboardData(
  apiBase,
  getAccessToken,
  fetchImpl = fetch,
  signal,
) {
  let accessToken
  try {
    accessToken = await getAccessToken()
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    throw new Error(`Unable to authenticate API requests: ${message}`)
  }

  if (!accessToken) {
    throw new Error('Unable to authenticate API requests: WorkOS returned no access token')
  }

  const results = await Promise.all(
    DASHBOARD_ENDPOINTS.map((endpoint) =>
      loadEndpoint(apiBase, endpoint, accessToken, fetchImpl, signal),
    ),
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
