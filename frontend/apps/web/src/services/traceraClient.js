const DEFAULT_API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8080'

async function parseJson(response) {
  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) {
    return {}
  }
  return response.json()
}

async function parseResponse(response, defaultValue) {
  if (!response.ok) {
    const body = await parseJson(response)
    throw new Error(
      `HTTP ${response.status} ${response.statusText} ${body?.error || ''}`.trim(),
    )
  }
  const payload = await parseJson(response)
  return payload ?? defaultValue
}

async function safeRequest(url, options) {
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    },
    ...options,
  })
  return response
}

export const traceraClient = {
  async getHealth() {
    const response = await safeRequest(`${DEFAULT_API_BASE}/health`)
    return parseResponse(response, { status: 'unknown' })
  },

  async getSprints() {
    const response = await safeRequest(`${DEFAULT_API_BASE}/sdlc-pm/sprints`)
    return parseResponse(response, [])
  },

  async getTeams() {
    const response = await safeRequest(`${DEFAULT_API_BASE}/org-intel/teams`)
    return parseResponse(response, [])
  },

  async getMetrics() {
    const response = await safeRequest(`${DEFAULT_API_BASE}/org-intel/metrics`)
    return parseResponse(response, {
      total_artifacts: 0,
      coverage_ratio: 0,
      open_gaps: 0,
    })
  },

  async getEvidence() {
    const response = await safeRequest(`${DEFAULT_API_BASE}/evidence`)
    const payload = await parseResponse(response, { count: 0, items: [] })
    return {
      count: payload.count ?? (Array.isArray(payload) ? payload.length : 0),
      items: Array.isArray(payload?.items) ? payload.items : [],
    }
  },
}
